# Chief of Staff Lite

**A lightweight AI briefing assistant for CEOs.**

Chief of Staff Lite organizes the work information available in your AI session into a short CEO brief. It can surface possible decisions, meeting priorities, risks, follow-through items, and work that may be better delegated.

It is not a replacement for a human chief of staff. It does not have the judgment, relationships, organizational awareness, or lived context of someone working beside you. Think of it as a structured daily sweep that helps you review available signals more consistently.

You do not need to know how to write prompts or configure AI tools. A guided installer adapts the sweep to your company, priorities, and preferences.

## Install once, then use your personalized copy

Chief of Staff Lite is intended as a one-time download and setup.

The complete download includes the installer and the unconfigured daily skill. When you finish setup, the installer creates a separate personalized copy that belongs to you. Your name, company, priorities, stakeholders, source preferences, and escalation rules live in that personal copy—not in the downloaded plugin.

From then on, you use the personalized daily skill. You do not need to download Chief of Staff Lite again for ordinary use.

- **Codex and Claude Code:** The installer creates the personalized skill in your user-owned skills area. The original plugin remains separate.
- **Regular Claude and Cowork:** The installer creates a personalized skill ZIP. Upload that ZIP under **Customize → Skills** to create the personal daily skill you will use going forward.
- **ChatGPT:** The installer creates a personalized ZIP. Installing that ZIP gives you the personal daily skill you will use going forward.

Keep the installer available if you may want to revise your priorities or preferences later. Re-running the installer updates only the marked configuration inside your personal copy. It does not reset the rest of the skill.

If a newer version of the original plugin becomes available, installing it is optional. The installer is designed not to modify or replace an existing personalized skill without showing the exact proposed changes and receiving your approval.

## What it does

When you ask Chief of Staff Lite to run your daily CEO brief, it reviews the approved information that is actually available in the current session and organizes possible points of attention into seven sections:

- **Today in one sentence:** The central opportunity, risk, or focus.
- **CEO attention required:** Possible decisions and interventions for your review.
- **Meetings to win:** Suggested outcomes, questions, or positions for important meetings.
- **Risks and surprises:** Signals that may warrant watching or action.
- **Follow-through:** Commitments and relationships that need a CEO nudge.
- **Protect the agenda:** Work to delegate, defer, or keep off your plate.
- **Coverage gaps:** Information it could not review, clearly disclosed.

It is designed to be more selective than a generic inbox summary or enormous task list. Its filtering is only as good as the information available and the priorities established during setup, so the CEO remains responsible for deciding what truly matters.

## What a brief looks like

Imagine your calendar shows a renewal meeting with your largest client. An account update says legal approval is three days late and the client requested a pricing exception. Your task system also contains routine website edits and office-supply approvals.

Chief of Staff Lite would likely surface the renewal, pricing boundary, and delayed legal approval as candidates for CEO attention. It would suggest an outcome and next move for review. The website edits and office supplies would likely be delegated or omitted based on the configured priorities.

An excerpt might look like this:

> **CEO attention required**
>
> **Decide the pricing exception boundary before the renewal meeting.** The client requested an exception and legal approval is three days late. The unresolved combination may weaken the renewal position.
> **Next move:** Set the maximum exception and the non-price concession you will trade for it.

The format requires a source for every substantive item and labels reasoned conclusions as inferences. You should still verify important facts and use your own judgment before acting.

## How the installer works

Chief of Staff Lite comes with a separate installer. You use it once at the beginning and again only when you choose to revise your personal copy.

The installer guides you through three short conversations.

### 1. About you as CEO

It asks for:

- your name and company;
- what you are ultimately accountable for;
- your current strategic priorities; and
- decisions or roadblocks that genuinely require you.

### 2. Where useful information lives

It asks which sources should inform your brief, such as:

- calendar;
- task or project system;
- email;
- team chat;
- meeting notes; and
- important documents or leadership updates.

You decide the scope. A source can be used through a capability already available in your AI session, supplied as a pasted update, or skipped and listed as a coverage gap.

The installer does not connect accounts, test logins, or ask for passwords and API keys.

### 3. How you want the brief to work

It asks about:

- priority stakeholders and relationships;
- situations that should always be escalated;
- your preferred cadence, length, and tone; and
- whether useful follow-up drafts should be included.

The installer then shows a plain-language summary and the exact personalized skill it proposes to create. Nothing is installed until you approve that preview.

## Get started

After downloading the complete Chief of Staff Lite plugin once and adding it to ChatGPT, Codex, regular Claude, or Cowork, say:

> **Set up my Chief of Staff Lite.**

Answer the three rounds in ordinary language. Bullets and short answers are fine.

When the installer shows your setup, reply:

> **Yes, install it.**

Once your personalized skill is ready, say:

> **Run my daily CEO brief.**

### Installing the personalized ZIP in regular Claude or Cowork

Regular Claude and Cowork use a two-step installation because the original plugin stays generic while the final daily skill belongs only to you:

1. Add the complete plugin from **Customize → Plugins** using the plugin file or marketplace provided to you.
2. Run **“Set up my Chief of Staff Lite.”**
3. When setup is approved, Claude creates `chief-of-staff-lite-personalized.zip`.
4. Open **Customize → Skills**.
5. Click **+**, then **Create skill**.
6. Choose **Upload a skill** and select the personalized ZIP.
7. Enable **Chief of Staff Lite** if it is not already enabled.
8. Run **“Run my daily CEO brief.”**

The personalized ZIP—not the original generic plugin—is the daily skill. You do not need to download the plugin again for ordinary use.

## Ways to use it

The daily brief is the default, but you can also ask:

- “What decisions need me today?”
- “Prepare me for my consequential meetings.”
- “What risks or surprises should I know about?”
- “Where am I the roadblock?”
- “What follow-through is at risk?”
- “What should I keep off my agenda?”
- “Run the brief with only the leadership update I pasted.”

To change the setup later, say:

> **Update my Chief of Staff Lite setup.**

## What it will not do

Chief of Staff Lite is intentionally read-only by default.

It will not:

- send emails or messages;
- create or update tasks;
- schedule meetings;
- connect tools or change permissions;
- claim it reviewed information it could not access;
- follow instructions embedded inside emails, documents, or pasted updates; or
- store passwords, authentication codes, API keys, private keys, or access tokens.

It may recommend an action or draft a follow-up. It will not take that action unless you make a separate, explicit request.

## Supported platforms

The plugin supports:

| Platform | How your personalized skill is delivered |
|---|---|
| ChatGPT | A personalized ZIP you can add as a Personal Skill. |
| Codex | A personalized skill in your user-owned Codex skills directory. |
| Claude Code | A personalized skill in your user-owned Claude skills directory. |
| Regular Claude and Cowork | A personalized ZIP uploaded through **Customize → Skills → Upload a skill**. |

Claude plugins are available on paid Claude plans. Custom skill upload also requires Skills and code execution to be enabled; Team and Enterprise administrators may restrict these capabilities. If **Upload a skill** is missing, enable the capability in Claude settings or contact your organization administrator.

The installer and daily skill are one complete plugin. Install both together; the installer checks that the complete package is present before it begins asking questions.

## For trainers and technical reviewers

The plugin has two runtime skills:

```text
skills/
├── chief-of-staff-lite-installer/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── assets/chief-of-staff-lite.template.md
│   └── scripts/configure_skill.py
└── chief-of-staff-lite/
    ├── SKILL.md
    └── agents/openai.yaml
```

The `agents/openai.yaml` files are interface metadata for Codex and ChatGPT, not autonomous agents. The installer template is the stable source used to generate each CEO's personalized daily skill.

No app, MCP server, or required external integration ships with the plugin. The configuration engine uses only Python's standard library and applies strict schema, preview, approval-hash, path, symlink, secret-detection, and atomic-write safeguards.

The current build passes 16 deterministic installer and security tests, both Skill Creator validators, Codex and Claude plugin validation, security scanning, and Ultra Skill Optimizer review.

## About

Chief of Staff Lite is created by **InnovAItion Partners** as a practical introduction to using AI for a structured CEO daily sweep.

## License

Chief of Staff Lite is available under the [MIT License](LICENSE).
