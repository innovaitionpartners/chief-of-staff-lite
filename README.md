# Chief of Staff Lite

A lightweight, personalized daily briefing skill for CEOs, created by **InnovAItion Partners**.

Install one **chief-of-staff-lite** skill. It starts unconfigured and helps you clarify your mandate, priorities, CEO-only decisions, stakeholders, sources, and briefing preferences. Setup authors a daily procedure around those answers: source investigation, evidence cross-checks, useful preparation, judgment, and the structure of your brief. After you approve the setup, that procedure becomes part of the installed skill. Say **“Update my setup”** whenever those details change.

## Get started

1. Upload the standalone skill ZIP under **Customize > Skills > Upload a skill** in Cowork or regular Claude, or your host's Skills upload screen in ChatGPT. Enable Chief of Staff Lite.
2. Say **“Set up my Chief of Staff Lite.”** Answer a short conversation in ordinary language. You can select each source independently and choose to use it, paste updates, or skip it.
3. Review the complete setup posted in chat and approve the stated action.
4. In Cowork, regular Claude, or ChatGPT, download the personalized ZIP and replace the existing **Chief of Staff Lite** under **Customize > Skills** (or the host's Skills screen). Keep only one enabled copy. Creating the ZIP does not install it.
5. After replacement, say **“Run my daily CEO brief.”**

The personalized ZIP contains the same complete skill, including customization instructions and its configuration script. Later **“Update my setup”** requests generate a replacement ZIP from your current configuration; no separate installer is required. The ZIP contains private business context: keep it in your own account.

For Codex or Claude Code, install the complete `skills/chief-of-staff-lite/` folder in your user-owned skill directory. After approval, customization updates its marked configuration block directly. If no local copy exists, the script can create the complete skill. Repository and plugin-cache copies are never personalized in place.

Customization requires access to the bundled files and Python code execution. If a host cannot execute the script or upload a skill, use a supported environment; the assistant must not claim installation or generate a partial replacement.

## What the brief does

The brief follows the procedure authored for your work. For example, a CEO overwhelmed by client follow-ups may get a reconciled queue and ready-to-use asks; a CEO weighing investment may get the evidence and tradeoffs for a small set of capital decisions. There is no mandatory seven-section template. It ranks signals by strategic impact, urgency, reversibility, and unique CEO leverage, using your priorities as ordered guidance. Substantive items identify sources and distinguish facts from inferences.

The skill uses only approved source scopes available in the current session. Setup can see which capability names appear available but does not test account access, connect tools, or read business content. The daily brief checks actual access and reports missing coverage. It can prepare useful follow-up drafts but does not send them.

Scheduling is separate. After installation, use the host’s native scheduled-task flow for recurrence, time, and timezone. Skill customization neither creates a schedule nor stores timing in your briefing preferences.

## Upgrade a previously personalized standalone skill

Save its marked `CSL-CONFIG` block or setup summary, replace the complete skill with this release, and ask “Update my setup using this saved context.” Setup preserves your answers and authors the missing daily procedure. You do not need to repeat the interview or read the original prompt. Review the normal assistance summary, approve, and replace the skill with the returned personalized ZIP. The old version’s “Update my setup” command cannot upgrade its own bundled runtime.

## Migrate from the earlier plugin

1. Save the marked `CSL-CONFIG` block from your current personalized skill, or copy your configuration summary, before removing anything. Keep it private.
2. Disable the old **Chief of Staff Lite** plugin and its installer. If it created a separate personal daily skill, preserve that configuration and remove/replace the old skill as well, leaving no duplicate enabled.
3. Install the standalone ZIP through **Customize > Skills**. Say **“Set up Chief of Staff Lite using this previous configuration”** and provide the saved block or summary. Confirm the interpreted values, review the generated preview, and approve.
4. Upload the resulting personalized ZIP to replace that same standalone skill. Run a brief to check source coverage. The personalized skill now handles future setup changes itself.

For local Codex/Claude Code migration, replace the old runtime folder with the complete standalone folder after saving your context, then personalize it from that context. The configuration command refuses to treat an old daily-only folder as a complete standalone installation; it will not silently rewrite workflow files during a configuration update.

Existing scheduled tasks are separate host resources. Review any task that still calls the old installer or plugin and retarget it through the host's native editing flow. Migrating this skill does not change or duplicate scheduled tasks.

## Runtime and validation

The primary distribution is a standalone skill ZIP. Plugin manifests have been removed; there is no marketplace wrapper or second discoverable daily skill.

```text
skills/chief-of-staff-lite/
├── SKILL.md                         # Mode routing and embedded configuration
├── references/customization.md      # Setup, reconfiguration, preview, delivery
├── references/daily-brief.md         # Daily judgment, examples, output contract
└── scripts/configure_skill.py       # Deterministic validation and packaging
```

`SKILL.md` loads customization only when unconfigured or explicitly asked to change setup. An active brief loads only the daily reference.

Run `python3 skills/chief-of-staff-lite/scripts/configure_skill.py --check-bundle` to validate the bundle. Preview and apply consume JSON through `--config-stdin`. Preview writes nothing, and the approval hash binds the destination, current state, proposed skill, and bundled resources. Existing local skills change only inside the marked configuration block. Hosted packages use a fixed allowlist of the four runtime files and atomic ZIP replacement.

The maintenance sidecar in the Skills repository holds requirements, behavioral evals, regression tests, and audit evidence. Run its suite against a candidate checkout by setting `CHIEF_OF_STAFF_LITE_RUNTIME_ROOT` to this repository and running `python3 -m unittest discover -s <sidecar>/tests -v`.

## License

[MIT License](LICENSE). This repository's visibility is managed separately from distribution of the skill.
