# perfect-handoff

Project knowledge closeout and compact handoff in one skill. It reconciles current project documents, saves a short continuation entry, and prints a ready-to-paste opener in the original conversation.

## What it does

- Checks the active project rules, current task, affected documents, and relevant workspace state.
- Updates verified project facts in their existing authoritative files.
- Preserves historical material and points to it only when a later session needs it.
- Writes a compact handoff with the goal, verified state, decisions, constraints, in-progress changes, blockers, and one next action.
- Prints both a closeout report and the complete next-session prompt in the original conversation.
- Limits proactive first-read material to 12,000 characters, while keeping required project rules in force.
- Makes a new session restore and report first; it waits for the user's next instruction before implementation.

It does not promise to prevent automatic context compression. Its character limits apply to handoff material, not the platform's required instructions or the full context window.

## Use

Invoke `$perfect-handoff` in Codex, or tell another Agent Skills-compatible agent:

> Use perfect-handoff to close out the current project and prepare a compact handoff for a new session.

The skill works in the current project directory. It reuses an existing short handoff when appropriate. After closeout, copy the prompt printed in the original conversation into a new session for that same project.

The optional `scripts/check_handoff.py` checker validates document structure, length, placeholders, and local Markdown links. It cannot prove that the summary is semantically complete or that a runtime claim is true.

## Package

- `SKILL.md` — core workflow and new-session reading contract.
- `references/closeout.md` — project knowledge reconciliation, loaded during closeout.
- `assets/handoff-template.md` — compact handoff and paste-ready prompt.
- `scripts/check_handoff.py` — read-only structural checker.
- `agents/openai.yaml` — Codex discovery metadata.

## Attribution and license

This independent integration references the knowledge-governance workflow in [neat-freak](https://github.com/KKKKhazix/khazix-skills/tree/main/neat-freak). Original copyright and MIT terms are preserved in `LICENSE`; see `NOTICE.md` for provenance.

## Release

Version 1.0.0. For the version's scope and validation limits, see the release notes in `CHANGELOG.md`.
