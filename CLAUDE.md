---
type: project-claude-md
commercial_status: external
artifact_type: skill
status: active
---

# Chief of Staff Lite — standalone repository

## Who I Am

A free, Codex-compatible AI chief-of-staff template that creates a tool-aware daily brief for a CEO.

## What Exists

- `SKILL.md` — canonical runtime skill source
- `agents/` and `assets/` — runtime metadata and profile template
- `evals/evals.json` — canonical behavioral cases
- `tests/` and `docs/` — maintenance notes and recorded test results

## Recent Activity

- 2026-07-15 — Moved out of the shared personal-skills repository into this standalone local repository. The previous runtime worktree is clean and no runtime optimization changes were merged or pushed there.
- 2026-07-15 — Optimized CEO-specific setup, active-profile enforcement, source-instruction boundary, prioritization rubric, brief evidence labels, portability fallback, and behavioral eval coverage. Independent forward-test review passed all four eval cases after fixture calibration.
- 2026-07-14 — Registered in `CATALOG.md` and `_skills-index.md`; runtime commit `01ff94f` passed Skill Creator structural validation.
- 2026-07-14 — Scaffolded v1 runtime skill and its maintenance sidecar.

## My Guidelines

- Keep the skill CEO-specific, tool-agnostic, read-only by default, and free of client-specific examples.
- Keep `SKILL.md`, `agents/`, and `assets/` self-contained so the runtime portion can be installed for local testing without the maintenance material.

## Current State

- active: standalone local repository ready for testing; no remote has been created.
- done when: the repository is committed and a publication choice is made.

## Compound Knowledge

- Before changing setup or runtime behavior, read `../docs/solutions/best-practices/initialize-mode-phase-ab-pattern-2026-04-17.md` and `../docs/solutions/best-practices/cross-reference-skill-files-for-scaffold-runtime-parity-2026-04-21.md`.
