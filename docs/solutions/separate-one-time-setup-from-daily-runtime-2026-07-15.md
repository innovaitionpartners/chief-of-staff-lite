---
title: Keep one-time CEO profile setup out of the recurring daily skill
date: 2026-07-15
module: chief-of-staff-lite
problem_type: architecture
component: onboarding
resolution_type: skill_split
severity: high
---

# Separate one-time setup from the daily runtime

## Decision

Chief of Staff Lite's recurring daily skill must not carry the one-time CEO configuration workflow. A separately installable companion creates or revises the CEO configuration block in a local daily `SKILL.md`; the daily skill consumes that active embedded context and produces the CEO brief.

## Why

Mixing setup with the daily workflow makes a one-time onboarding task look like part of the recurring operating cadence, obscures the daily skill's trigger, and adds instructions that most runs do not need.

## Implemented design

`chief-of-staff-lite-installer` is independently installable. It asks three plain-language question rounds, previews an exact personalized daily skill, and requires a matching approval hash before a bounded script writes. `chief-of-staff-lite` contains no setup interview and refuses to run while unconfigured.

The installer edits only the marked configuration block on later runs. It does not manually rewrite workflow or safety instructions.

## Tool-integration boundary

Setup inspects only the names and descriptions of capabilities already exposed by the current AI session. It does not invoke connectors, test authentication, install integrations, or request credentials. Clear matches are presented to the CEO as “appears available here,” followed by a permission-and-scope question. Missing or ambiguous sources get a paste-or-skip choice.

This preflight is deliberately provisional. The installed daily skill rechecks actual availability at run time and reports a coverage gap instead of claiming access when a configured tool is unavailable.
