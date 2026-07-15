# Chief of Staff Lite — product requirements

## Outcome

A CEO who is not AI-savvy can install one setup skill, answer ordinary-language questions, approve a clear preview, and receive a personalized daily Chief of Staff Lite skill. The installed daily skill reflects the CEO's context without collecting credentials, connecting tools, or changing unrelated files.

## Product shape

1. **Chief of Staff Lite Installer** — used once for initial setup and again only when the CEO wants to revise the configuration.
2. **Chief of Staff Lite** — the personalized recurring skill that produces the daily CEO brief. It contains no setup interview or configuration-writing behavior.

## Installer requirements

- Ask three short rounds: CEO context, information sources, and briefing preferences.
- Inspect only the tool and connector capability names exposed in the current session; do not invoke them or read content during setup.
- Show the CEO which named sources appear available and which are not visible, without claiming authentication or successful access.
- Ask only for permission and scope when a clear capability match appears; offer paste-or-skip choices for missing or ambiguous sources.
- Translate those plain-language choices into `connected`, `manual`, or `unavailable` internally. Recheck actual access during every daily run.
- Generate a personalized daily `SKILL.md`; do not create a separate profile file.
- Show the CEO a plain-language summary and exact target before writing.
- Require explicit approval of the exact preview.
- Re-running the installer may update only the marked CEO configuration block.
- Never run the first daily brief automatically.

## Security requirements

- Never request or store credentials or authentication material.
- Treat pasted material as untrusted data and ignore embedded instructions.
- Make no network requests and change no tool permissions or connections.
- Never probe a tool to test authentication or access during setup.
- Write only `chief-of-staff-lite/SKILL.md` and missing UI metadata in the sibling daily-skill folder.
- Reject symbolic-link targets, unrelated existing folders, unknown schema keys, oversized configuration files, and secret-like values.
- Preview must write nothing.
- Apply must require the SHA-256 hash from the latest preview.
- Writes must be atomic. The only permitted deletion is the exact validated temporary configuration file after a successful apply.

## Daily-skill requirements

- Refuse to run when its configuration is not active; direct the CEO to the installer without conducting setup itself.
- Use only configured, available sources and expose coverage gaps.
- Treat all source content as untrusted data.
- Prioritize strategic impact, urgency, reversibility, and unique CEO leverage.
- Separate facts from inferences and cite each substantive item's source.
- Remain read-only unless the CEO makes a separate explicit request.

## Acceptance criteria

1. Both skill folders pass Skill Creator validation.
2. Preview produces a diff and approval hash without creating the target folder.
3. A correct approval hash installs a personalized daily skill.
4. A stale or incorrect approval hash cannot write.
5. Reconfiguration preserves everything outside the marked CEO configuration block.
6. Attempts to target another skill, overwrite an unrelated folder, use a symlink, add unknown keys, or include credentials fail safely.
7. The installer's bundled daily template exactly matches the canonical unconfigured daily skill.
8. A nontechnical CEO can understand the questions, preview, approval request, and first-use instruction without filesystem or AI terminology.
9. Setup inventories exposed capability metadata without invoking tools, clearly distinguishes “appears available” from verified access, and never asks the CEO to classify internal access modes.
