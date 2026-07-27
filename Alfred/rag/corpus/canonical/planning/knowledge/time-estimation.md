---
id: kd-time-estimation
topic_id: planning
concept_id: time-estimation
title: Estimating Task Duration
document_type: knowledge
language: en
source_ids: [src-planning-fallacy-1994, src-planning-unpacking-2004]
supported_claims:
  - claim_id: personal-completion-estimates-were-optimistically-biased
    source_ids: [src-planning-fallacy-1994]
    evidence_strength: experimental_primary_studies
  - claim_id: unpacking-improved-some-multifaceted-task-estimates
    source_ids: [src-planning-unpacking-2004]
    evidence_strength: experimental_primary_studies
evidence_level: evidence_informed
status: machine_audited
requires_human_review: true
index_in_production: true
risk_level: low
retrieval_terms:
  - underestimate how long tasks take
  - unrealistic time estimate
  - planning fallacy
  - task takes longer than planned
  - estimate from past attempts
related_concepts: [action-planning, self-monitoring, goal-specificity, behavioral-feedback]
version: 1.0.0
last_machine_audited_at: '2026-07-14'
---

# Estimating Task Duration

## Operational definition

A task-duration estimate is a forecast from a defined start condition to a defined completion condition. Its quality depends on task boundaries, comparable observations, dependencies and uncertainty, not only confidence.

## What this concept does not mean

Every underestimate is not a planning fallacy, and a single multiplier is not a universal correction. Delays can reflect changed scope, interruptions, missing dependencies or a different definition of done.

## Main mechanisms

People can focus on a coherent future scenario while underusing the distribution of relevant past completion times. Multifaceted tasks also hide components and transitions that are absent from a single global estimate.

## Evidence summary

Buehler, Griffin and Ross found optimistic predictions for personal completion times across several studies and observed reliance on future scenarios over relevant past experience. Kruger and Evans found that prompting people to unpack multifaceted tasks produced longer estimates and reduced bias in some experiments, with stronger effects for more complex tasks. Replication and task differences preclude treating decomposition as a guaranteed correction.

## Evidence mapping

- Personal completion forecasts were often optimistic and insufficiently anchored in prior experience: `src-planning-fallacy-1994` (`experimental_primary_studies`).
- Unpacking improved estimates for some multifaceted tasks and conditions: `src-planning-unpacking-2004` (`experimental_primary_studies`).

## Relevant signals

Comparable tasks repeatedly exceed estimates, planning includes only productive steps, or the completion boundary changes during execution.

## Alternative explanations

The task may be genuinely novel, scope may be unstable, records may omit interruptions, or external dependencies may dominate duration.

## Information needed

Start and done definitions, component steps, transition and setup time, comparable actuals, dependencies, interruptions and confidence range.

## Practical implications

Use comparable recorded durations when available, unpack only meaningful components, include dependencies and state a range. Update the estimate after execution rather than moralizing the error.

## Limitations

The foundational experiments used bounded tasks and student samples. Forecasting large projects or safety-critical work requires domain-specific methods.

## Sources

`src-planning-fallacy-1994`; `src-planning-unpacking-2004`.
