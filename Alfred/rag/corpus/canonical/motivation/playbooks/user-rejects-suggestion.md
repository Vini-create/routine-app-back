---
id: pb-user-rejects-suggestion
topic_id: motivation
playbook_id: user-rejects-suggestion
title: User Rejects a Suggestion
document_type: playbook
language: en
related_concept_ids: [goal-autonomy, observable-behavior]
status: machine_audited
requires_human_review: true
index_in_production: true
risk_level: low
trigger_phrases:
  - that does not work for me
  - I do not want to do that
  - I already tried this
  - stop insisting
version: 3.0.0
last_machine_audited_at: '2026-07-14'
---

# User Rejects a Suggestion

## Activation criteria

The user explicitly rejects a proposed technique, explanation or direction.
The rejection is the current conversational decision, not merely a weak signal.

## Similar situations that should not activate this playbook

A request for evidence, a clarifying question or uncertainty about implementation
is not necessarily rejection.

## Possible explanations

The suggestion may conflict with cost, prior experience, values, resources or a
conversational preference. The rejection itself is useful information and does
not indicate unwillingness to cooperate.

## Missing information

Whether the user wants to explain the mismatch, choose an alternative, continue
without advice or end the exchange.

## Response objective

Stop the rejected direction, incorporate any stated constraint and return
control without disguising the same suggestion as a new one.

## Decision path

- Stop presenting the rejected strategy.
- If the user gives a reason, treat it as a constraint for future options.
- If the user requests an alternative, offer at most one materially different route.
- If the user asks to stop or end, do so without another coaching question.

## Candidate strategies

Acknowledgment, constraint update, a genuinely different option, listening or
ending the exchange.

## Conditions for selecting each strategy

Use an alternative only after the user indicates that another option is wanted.
Use listening when advice is declined but continued conversation is invited;
end when the user requests it.

## When to ask a question

Ask only when the user remains open and the answer selects among a different
option, listening or ending.

## When to respond directly

Respond directly when the reason or request to stop is explicit.

## What to avoid

Do not defend the prior suggestion, cite evidence to win the objection, relabel
the same technique or interpret rejection as a character trait.

## Suggested next step

Apply the user's stated boundary and proceed only along the option they selected.

## Related knowledge

`goal-autonomy`; `observable-behavior`.
