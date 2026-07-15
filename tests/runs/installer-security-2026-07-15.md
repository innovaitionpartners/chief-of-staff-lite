# Chief of Staff Lite installer — deterministic test run

Date: 2026-07-15
Command: `python3 -m unittest tests/test_installer.py -v`
Result: 9/9 passed

| Test surface | Result |
|---|---|
| Preview creates no target or runtime file | PASS |
| Apply rejects a stale or incorrect approval hash | PASS |
| Correct approval installs a personalized daily skill | PASS |
| Reconfiguration preserves content outside the marked block | PASS |
| Installer template matches the canonical daily skill | PASS |
| Other target folder is rejected | PASS |
| Symbolic-link target is rejected | PASS |
| Unknown keys, credential-like values, and instruction-injection text are rejected | PASS |
| Unrelated existing folder is rejected | PASS |

Both skill folders also passed Skill Creator validation. Script wiring, reference-depth, template-parity, JSON syntax, and git diff checks passed. Behavioral eval definitions are present but have not yet been run in independent model sessions.

The setup flow now includes a metadata-only tool preflight. It may inspect capability names and descriptions already exposed in the AI session, but it must not invoke connectors, read source content, test authentication, or make network requests. A fifth behavioral eval and a no-capability-inventory persona cover the distinction between “appears available” and verified access; these cases still require an independent model-session run.

Cisco AI Skill Scanner 2.0.11 reported both skills `SAFE`, with zero critical, high, medium, or low findings. Each received one informational manifest note for not declaring a license; the frontmatter intentionally follows Skill Creator's two-field contract while licensing remains undecided. Static and behavioral dataflow scans completed. LLM meta-analysis was unavailable because no scanner API key is configured.
