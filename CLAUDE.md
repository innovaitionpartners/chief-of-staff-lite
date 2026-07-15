---
type: project-claude-md
commercial_status: external
artifact_type: skill
status: active
---

# Chief of Staff Lite — private product repository

## Who I Am

A two-skill product for nontechnical CEOs: a one-time installer safely generates a personalized daily Chief of Staff Lite skill.

## What Exists

- `skills/chief-of-staff-lite-installer/` — one-time install and personalization skill
- `skills/chief-of-staff-lite/` — canonical unconfigured daily-skill template
- `evals/` — canonical behavioral cases for discovery and orchestration
- `tests/` — deterministic security tests and forward-test cases
- `docs/solutions/` — maintainer decisions and lessons

## Recent Activity

- 2026-07-15 — Added a metadata-only tool preflight to setup. It reports capabilities that appear available, asks the CEO only for permission and scope or paste-or-skip choices, and never invokes connectors or claims authentication.
- 2026-07-15 — Split the product into an installable one-time configurator and a recurring daily skill. The installer previews an exact diff, requires a matching approval hash, and writes only a sibling `chief-of-staff-lite` folder.
- 2026-07-15 — Repository visibility corrected to private. Public release requires separate explicit approval.
- 2026-07-15 — Moved out of the shared personal-skills repository into this standalone repository.
- 2026-07-15 — Optimized CEO-specific setup, active-profile enforcement, source-instruction boundary, prioritization rubric, brief evidence labels, portability fallback, and behavioral eval coverage. Independent forward-test review passed all four eval cases after fixture calibration.
- 2026-07-14 — Registered in `CATALOG.md` and `_skills-index.md`; runtime commit `01ff94f` passed Skill Creator structural validation.
- 2026-07-14 — Scaffolded v1 runtime skill and its maintenance sidecar.

## My Guidelines

- Keep both skills CEO-specific, tool-agnostic, and free of client-specific examples.
- Keep one-time setup out of the daily skill.
- Treat installer writes as a security boundary: preview, exact approval hash, bounded target, strict schema, atomic write.
- Never infer public repository visibility from giveaway or external status.

## Current State

- active: private repository; installer/daily split is under test on `codex/installer-and-daily-split`.
- done when: both skills pass structural, deterministic, and beginner-usability validation; changes are reviewed before any push.

## Compound Knowledge

- Before changing setup or runtime behavior, read `../docs/solutions/best-practices/initialize-mode-phase-ab-pattern-2026-04-17.md` and `../docs/solutions/best-practices/cross-reference-skill-files-for-scaffold-runtime-parity-2026-04-21.md`.
