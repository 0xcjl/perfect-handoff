#!/usr/bin/env python3
"""Read-only structural checks; no semantic, authorization or runtime proof."""

import argparse
import json
import re
from pathlib import Path

SECTIONS = (
    "目标与验收", "当前状态与证据", "工作现场与改动归属", "决策与边界",
    "下一步与验证", "按需定位", "覆盖与缺口", "新会话提示词",
)
PLACEHOLDERS = re.compile(
    r"<(?:项目根目录|精简交接文件|root|project-root|handoff-path|skill-dir)>"
    r"|\{\{[^\n{}]+\}\}|\[TODO:[^\n\]]*\]"
)


def without_fences(text: str) -> str:
    """Skip fenced examples when extracting headings and document links."""
    lines = []
    marker = None
    length = 0
    for line in text.splitlines(keepends=True):
        fence = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if fence:
            run, suffix = fence.groups()
            if marker is None:
                marker, length = run[0], len(run)
            elif run[0] == marker and len(run) >= length and not suffix.strip():
                marker = None
            lines.append(re.sub(r"[^\r\n]", " ", line))
            continue
        lines.append(line if marker is None else re.sub(r"[^\r\n]", " ", line))
    return "".join(lines)


def decode_path(path: str) -> str:
    """Decode percent-encoded UTF-8 path bytes without URL/network libraries."""
    def decode_match(match: re.Match) -> str:
        raw = bytes.fromhex(match.group(0).replace("%", ""))
        return raw.decode("utf-8", errors="replace")

    return re.sub(r"(?:%[0-9a-fA-F]{2})+", decode_match, path)


def check_handoff(path: Path, project_root: Path) -> dict:
    errors = []
    result = {"status": "fail", "characters": None, "opener_characters": None,
              "local_links_checked": 0, "errors": errors,
              "limitations": ["结构通过不证明语义完整、运行状态或授权",
                              "字符数不是 token 数；只检查显式 Markdown 本地链接的存在性",
                              "不校验链接章节锚点，也不读取链接内容"]}
    if not project_root.is_dir():
        errors.append("项目根不存在或不是目录")
        return result
    if not path.is_file():
        errors.append("交接文件不存在或不是文件")
        return result
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"读取失败：{type(exc).__name__}")
        return result
    result["characters"] = len(content)
    if len(content) > 6000:
        errors.append("交接超过 6000 字符；必须人工保留关键内容后重新整理")
    if PLACEHOLDERS.search(content):
        errors.append("存在已知未填占位符；请人工核查")
    # Parse actual sections, including opener content, without matching code headings.
    visible = without_fences(content)
    headings = list(re.finditer(r"^##[ \t]+([^\n]+)$", visible, re.MULTILINE))
    sections = {}
    for index, match in enumerate(headings):
        title = match.group(1).strip()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(content)
        if title in sections:
            errors.append(f"重复章节：{title}")
        sections[title] = content[match.end():end].strip()
    actual_headings = set(sections)
    for title in SECTIONS:
        if title not in actual_headings or not sections.get(title):
            errors.append(f"缺少或空章节：{title}")
    opener = sections.get("新会话提示词", "")
    result["opener_characters"] = len(opener)
    if len(opener) > 1000:
        errors.append("新会话提示词超过 1000 字符")
    if str(project_root) not in opener or str(path) not in opener:
        errors.append("提示词须包含本次项目根与交接文件的实际绝对路径")
    # Markdown relative links resolve from the handoff's directory.
    for target in re.findall(r"\[[^\]\n]*\]\((<[^>\n]+>|[^\s)]+)\)", visible):
        target = target.strip("<>")
        link_path = target.split("#", 1)[0].split("?", 1)[0]
        if not link_path or link_path.startswith("//") or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", link_path):
            continue
        link = Path(decode_path(link_path))
        if not link.is_absolute():
            link = path.parent / link
        result["local_links_checked"] += 1
        if not link.exists():
            errors.append(f"本地链接不存在：{target}")
    result["status"] = "structural-pass" if not errors else "fail"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff", type=Path)
    parser.add_argument("--project-root", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = check_handoff(args.handoff.expanduser().resolve(),
                               args.project_root.expanduser().resolve())
    except (OSError, ValueError) as exc:
        result = {"status": "fail", "errors": [f"路径检查失败：{type(exc).__name__}"]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "structural-pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
