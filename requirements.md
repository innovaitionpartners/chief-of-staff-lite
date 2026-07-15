# Chief of Staff Lite — v1 build brief

## Goal

Give a CEO a reusable, light AI chief-of-staff cadence. The skill captures the CEO's name, company, mandate, actual sources, and briefing preferences, then produces a concise daily CEO brief without requiring a particular platform, integration, or automatic action.

## User promise

Set up a CEO operating profile once. On a daily run, receive a brief that identifies what needs the CEO's attention, which meetings need to be won, what could become a surprise, and what follow-through matters.

## In scope

- A guided setup that creates an approved `chief-of-staff-profile.md` using the user's actual tools and source availability.
- Three source states: `connected`, `manual`, and `unavailable`.
- A read-only daily brief covering executive attention, meetings, risks, follow-through, agenda protection, and coverage gaps.
- A no-profile Quick Start mode for a one-time brief using pasted context.

## Out of scope

- Tool-specific integrations, task writes, email or chat sends, calendar changes, automation scheduling, and persistent cross-system sync.
- Replacing a full human chief of staff or task-management system.

## Required behavior

- Never claim access to a configured source unless it is available in the current session.
- Never silently omit a configured source; name it as a coverage gap and request the smallest useful paste when appropriate.
- Never manufacture urgency, a risk, or a CEO-only responsibility from ordinary task noise.
- Never write the profile during setup until the user has explicitly approved the draft and named a save location.

## Acceptance criteria

1. The setup template records leadership mandate, source status and scope, operating preferences, and a read-only safety boundary.
2. A daily brief includes every required section, including coverage gaps.
3. The skill works credibly with no integrations, partial integrations, and full connected context.
4. The deployed files contain no customer names, InnovAItion Partners-specific context, dev-workspace paths, or runtime references to the maintenance sidecar.
