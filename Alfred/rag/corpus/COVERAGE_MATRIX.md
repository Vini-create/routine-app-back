# Alfred coverage matrix

Date: 2026-07-14  
Stage: A — diagnosis and controlled expansion proposal  
Scope: active Alfred-only corpus; archived material was used only as historical context, not as evidence or a restoration source.

## Classification rules

- `well_covered`: a distinct active unit supports the relevant Alfred decision with adequate boundaries and evidence.
- `partially_covered`: active units support part of the decision, but retrieval or decision detail is incomplete. This status alone does not authorize a new document.
- `weak`: the item is mentioned or inferable, but lacks a directly evidenced, retrievable explanation or decision rule.
- `missing`: no active unit adequately supports the decision.
- `intentionally_out_of_scope`: the requirement belongs in system policy, safety routing, or another non-RAG layer, or its construct is too uncertain to justify a canonical unit.

Only `weak` and `missing` items that pass all document-creation criteria are proposed for Stage B. Related concepts are consolidated when one document can support the same decision without losing distinctions.

## Topic-level diagnosis

| Topic | Existing foundations | Important gaps | Existing playbook coverage | Cross-topic overlap | Scientific depth and mechanism variety | Intervention variety | Generic-retrieval risk |
|---|---|---|---|---|---|---|---|
| habits | automaticity, repetition, context stability, routine/habit distinction | cues and friction; graded progression; lapse recovery and streak limits | none | self-regulation, planning, motivation | `partially_covered`: strong core formation evidence, little recovery/environment detail | `weak`: repetition and context dominate | high for missed days, friction, and progression |
| goals | review under changed conditions | behavior/process versus outcome; specificity; difficulty; conflict | none | planning, motivation, self-regulation | `weak`: review is sound but only one mechanism is retrievable | `weak`: review is the only explicit operation | high for vague, unrealistic, or conflicting goals |
| motivation | autonomy and internalization | variability; competence support | questioning a goal; rejecting a suggestion | goals, procrastination, planning | `partially_covered`: one strong theoretical family, narrow operational range | `partially_covered`: autonomy support and choice | high for “waiting to feel motivated” |
| physical-activity | consistency under variable capacity | no domain-specific gap meeting the creation threshold | none | planning, habits, sleep | `well_covered` for current Alfred scope; relies appropriately on cross-topic mechanisms | `partially_covered`: planning and graded progression should be retrieved cross-topic | low if cross-topic retrieval works |
| planning | action planning; implementation intentions | time estimation; environmental planning detail | irregular schedule; insufficient capacity | goals, habits, procrastination | `partially_covered`: strong plan formation, thinner feasibility calibration | `well_covered`: action, contingency, schedule adaptation | medium for unrealistic duration and environmental constraints |
| procrastination | multi-factor pattern; initiation and standards playbooks | task aversiveness; temporal discounting; evaluative avoidance | cannot start; standards block completion | planning, motivation, goals | `weak`: broad synthesis exists, mechanisms are not separately retrievable | `partially_covered`: diagnostic split and small-start planning | high because one broad document may answer unlike mechanisms generically |
| self-regulation | observable behavior; self-monitoring | feedback interpretation | none | every behavior topic | `partially_covered`: measurement is strong, feedback-to-adjustment is implicit | `partially_covered`: observe and record | medium for progress and adjustment questions |
| sleep-and-recovery | sleep duration and tiredness triage | sleep regularity | tiredness | study, physical activity, planning | `partially_covered`: adequate duration guidance, no regularity mechanism | `partially_covered`: triage and load reduction | medium for inconsistent sleep schedules |
| study-and-learning | retrieval practice; spaced practice | interleaving; false fluency | none | planning, sleep, self-regulation | `partially_covered`: two well-supported techniques, incomplete discrimination/calibration coverage | `partially_covered`: retrieval and spacing only | high for study-method selection and misleading ease |

## Alfred situation coverage

| # | Situation | Classification | Active support | Decision and Stage B disposition |
|---:|---|---|---|---|
| 1 | user cannot start | `well_covered` | `pb-user-cannot-start`, `concept-procrastination-pattern`, `concept-action-planning` | Existing playbook separates ambiguity, capacity, aversiveness, and first action. |
| 2 | user starts and abandons | `missing` | no dedicated decision policy | Create `pb-user-stops-after-starting`; distinguish early friction, excessive progression, and a repeated lapse pattern. |
| 3 | user missed multiple days | `missing` | habit formation and self-monitoring only | Create `pb-user-missed-several-days` after adding lapse-recovery evidence. |
| 4 | user is overwhelmed | `partially_covered` | `pb-user-reports-insufficient-capacity`, `pb-user-reports-tiredness` | Broaden retrieval terms and relations; do not duplicate the same capacity decision tree. |
| 5 | user created too many habits | `missing` | goal review is too general | Create `pb-user-created-too-many-habits`; route through conflict, load, and sequencing. |
| 6 | user lacks time | `well_covered` | `pb-user-reports-insufficient-capacity`, `pb-user-has-irregular-schedule` | Existing split covers low capacity versus unstable opportunity. |
| 7 | user has low energy | `well_covered` | `pb-user-reports-tiredness` plus security gate | Existing playbook first separates safety/health signals from routine adjustment. |
| 8 | user is waiting for motivation | `missing` | autonomy does not explain day-to-day variability | Create `pb-user-waits-for-motivation` after adding motivation-variability evidence. |
| 9 | user is perfectionistic | `well_covered` | `pb-standards-block-completion` | Keep playbook; strengthen its scientific relation with evaluative avoidance. |
| 10 | user fears failure | `partially_covered` | standards and cannot-start playbooks | Same core decision tree as evaluative standards; add knowledge, not a duplicate playbook. |
| 11 | user has a vague goal | `missing` | action planning starts too late in the chain | Create `pb-user-has-vague-goal`; distinguish outcome clarification from observable action specification. |
| 12 | user has an unrealistic goal | `missing` | goal review and capacity are indirect | Create `pb-user-set-unrealistic-goal`; calibrate difficulty and constraints without moral judgment. |
| 13 | user has conflicting goals | `missing` | no conflict decision support | Create `pb-user-has-conflicting-goals`; identify resource, time, and value conflict before reprioritizing. |
| 14 | user cannot prioritize | `partially_covered` | capacity and goal review | Use the existing capacity/review route; priority depends on constraints and goal conflict, not a separate technique. |
| 15 | user wants to compensate for missed work | `missing` | no escalation/recovery policy | Create `pb-user-wants-to-compensate`; prevent load spikes and choose resume, redistribute, or deliberately drop. |
| 16 | user repeatedly postpones | `partially_covered` | cannot-start plus procrastination pattern | Existing tree applies; new mechanism documents will improve retrieval without a new playbook. |
| 17 | user rejects suggestions | `well_covered` | `pb-user-rejects-suggestion` | Existing policy protects autonomy and stops suggestion loops. |
| 18 | user only wants to be heard | `intentionally_out_of_scope` | system behavior, not a corpus document | Conversational-mode detection is system behavior, not evidence-bearing topical content. |
| 19 | user is making sustainable progress | `missing` | self-monitoring records but does not guide reinforcement/adjustment | Create `pb-user-is-progressing-sustainably`; preserve what works and avoid needless escalation. |
| 20 | user wants to increase difficulty too quickly | `missing` | no progression policy | Create `pb-user-increases-difficulty-too-quickly`; assess stability, cost, and one-variable progression. |
| 21 | user's environment creates friction | `partially_covered` | cannot-start and habit context | Add a directly retrievable environment concept; reuse current initiation playbook. |
| 22 | user's schedule conflicts with the habit | `well_covered` | `pb-user-has-irregular-schedule`, action planning | Day-type and anchor adaptation are explicit. |
| 23 | user lacks the required skill or clarity | `well_covered` | cannot-start and action planning | Existing decision tree separates undefined action from capacity and teaches specification. |
| 24 | user has inconsistent weekdays and weekends | `well_covered` | irregular-schedule playbook | Existing day-type planning covers this case; add retrieval phrases only if evaluation shows misses. |
| 25 | user wants scientific evidence | `intentionally_out_of_scope` | evidence and citation rules belong in system/retrieval policy | A generic “science” playbook would compete with the actual concept and its source mapping. |
| 26 | user asks how long habit formation takes | `well_covered` | `concept-habit-formation` | Active document gives observed range, uncertainty, and rejects a universal day count. |

## Scientific concept coverage

### Habits

| Concept | Classification | Coverage and disposition |
|---|---|---|
| automaticity | `well_covered` | Central construct in `concept-habit-formation`. |
| stable context | `well_covered` | Direct evidence and practical boundary in habit formation. |
| repetition | `well_covered` | Directly described as repeated action, not a guaranteed schedule. |
| cues | `partially_covered` | Context is present, but cue selection is not independently retrievable; consolidate with friction. |
| friction | `weak` | Mentioned indirectly; create `concept-environmental-cues-and-friction`. |
| graded tasks | `missing` | Create `concept-graded-task-progression`. |
| self-monitoring | `well_covered` | Dedicated cross-topic concept. |
| habit recovery | `missing` | Create `concept-lapse-recovery`. |
| streak limitations | `weak` | Cover as a bounded section of lapse recovery, not a standalone document. |
| routine versus habit | `well_covered` | Explicit distinction in habit formation. |

### Procrastination

| Concept | Classification | Coverage and disposition |
|---|---|---|
| task initiation | `partially_covered` | Operationally strong in playbook/action planning; scientific mechanism remains broad but does not require a standalone unit. |
| task aversiveness | `weak` | Create `concept-task-aversiveness`. |
| temporal discounting | `weak` | Create `concept-temporal-discounting`. |
| perfectionism | `weak` | Consolidate with fear of failure in `concept-evaluative-avoidance`. |
| fear of failure | `weak` | Same decision mechanism as evaluative avoidance; no duplicate concept. |
| task ambiguity | `partially_covered` | Action planning and cannot-start provide an adequate decision route. |
| avoidance | `partially_covered` | Broad procrastination map identifies it; mechanism-specific documents improve discrimination. |
| immediate rewards | `weak` | Treat as the near-term side of temporal discounting. |

### Goals

| Concept | Classification | Coverage and disposition |
|---|---|---|
| behavioral versus outcome goals | `weak` | Create `concept-behavior-vs-outcome-goals`. |
| goal specificity | `missing` | Create `concept-goal-specificity`. |
| goal difficulty | `weak` | Create `concept-goal-difficulty`. |
| goal review | `well_covered` | Dedicated concept. |
| goal conflict | `missing` | Create `concept-goal-conflict`. |
| goal disengagement | `partially_covered` | Goal review and autonomy support revision; add relations, not a standalone document. |
| process goals | `partially_covered` | Cover within behavior-versus-outcome goals. |
| unrealistic goals | `weak` | Cover within goal difficulty and the dedicated playbook. |

### Planning

| Concept | Classification | Coverage and disposition |
|---|---|---|
| action planning | `well_covered` | Dedicated concept. |
| implementation intentions | `well_covered` | Dedicated concept with limitations. |
| contingency planning | `partially_covered` | If-then planning and irregular-schedule playbook cover the decision. |
| prioritization | `partially_covered` | Goal review/capacity/conflict route is sufficient; no isolated technique document. |
| time estimation | `weak` | Create `concept-time-estimation`. |
| schedule compatibility | `well_covered` | Action planning and irregular-schedule playbook. |
| environmental planning | `weak` | Cover in environmental cues and friction. |

### Motivation and self-regulation

| Concept | Classification | Coverage and disposition |
|---|---|---|
| intrinsic and extrinsic motivation | `partially_covered` | Autonomy/internalization document gives the decision-relevant distinction. |
| autonomy | `well_covered` | Dedicated concept and related playbooks. |
| competence | `weak` | Decision need is supported by graded-task progression; avoid a second abstract theory document. |
| ambivalence | `partially_covered` | Goal questioning, autonomy, and goal review provide a sufficient conversational route. |
| motivation variability | `missing` | Create `concept-motivation-variability`. |
| self-monitoring | `well_covered` | Dedicated concept. |
| feedback | `weak` | Create `concept-behavioral-feedback`. |
| recovery after failure | `missing` | Cover in lapse recovery; “failure” is not treated as a user trait. |

### Study and learning

| Concept | Classification | Coverage and disposition |
|---|---|---|
| retrieval practice | `well_covered` | Dedicated concept. |
| spaced practice | `well_covered` | Dedicated concept. |
| interleaving | `missing` | Create `concept-interleaved-practice`. |
| planning study sessions | `partially_covered` | Cross-topic action and spaced planning suffice. |
| false fluency | `weak` | Create `concept-false-fluency`. |
| sleep and learning | `partially_covered` | Sleep duration plus learning concepts support cautious cross-topic retrieval; no extra unit yet. |
| active versus passive study | `well_covered` | Retrieval-practice document explicitly supports the decision. |

### Energy and overload

| Concept | Classification | Coverage and disposition |
|---|---|---|
| sleep consistency | `weak` | Create `concept-sleep-regularity`. |
| overload | `partially_covered` | Insufficient-capacity and tiredness playbooks already split practical and safety decisions. |
| decision fatigue | `intentionally_out_of_scope` | Construct boundaries and incremental Alfred value are insufficient for a canonical unit; use observable load and constraints instead. |
| recovery | `weak` | Support through lapse recovery and sleep regularity rather than an underspecified “recovery” document. |
| task load | `weak` | Support through graded-task progression and capacity playbook. |
| sustainable progression | `missing` | Support through graded-task progression, behavioral feedback, and a dedicated situation playbook. |

## Stage B proposals passing the creation criteria

### Knowledge documents

| Proposed concept ID | Classification | Alfred decision supported | Expected evidence | Required relations |
|---|---|---|---|---|
| `concept-environmental-cues-and-friction` | `weak` | Change an opportunity or response cost when context, not intent, blocks action | habit/context primary studies or systematic review; behavior-change taxonomy for technique definition | habit formation, action planning, cannot start |
| `concept-graded-task-progression` | `missing` | Select a feasible starting dose and increase one dimension only after evidence of tolerability | behavior-change taxonomy; intervention review or guideline addressing graded progression | capacity, feedback, physical-activity consistency |
| `concept-lapse-recovery` | `missing` | Resume after missed repetitions without overcompensation or diagnostic labeling | prospective lapse/maintenance evidence; systematic review of maintenance or relapse processes | habit formation, self-monitoring, goal review |
| `concept-task-aversiveness` | `weak` | Distinguish unpleasant task experience from ambiguity or low capacity | procrastination meta-analysis/review plus directly relevant primary evidence | procrastination pattern, cannot start, action planning |
| `concept-temporal-discounting` | `weak` | Address preference for immediate relief/reward when outcomes are delayed | temporal motivation/procrastination meta-analysis or primary study | procrastination pattern, implementation intentions |
| `concept-evaluative-avoidance` | `weak` | Respond when standards or anticipated evaluation block initiation/completion | perfectionism–procrastination meta-analysis/systematic review and primary evidence | standards playbook, task aversiveness, goal difficulty |
| `concept-behavior-vs-outcome-goals` | `weak` | Translate a desired result into controllable behavior without denying the result | behavior-change taxonomy; goal-setting review/meta-analysis | observable behavior, action planning, goal review |
| `concept-goal-specificity` | `missing` | Determine whether a goal is specific enough to act on and observe | goal-setting review/meta-analysis and primary goal research | action planning, behavior-vs-outcome goals |
| `concept-goal-difficulty` | `weak` | Calibrate challenge against skill, resources, and feedback | goal-setting review/meta-analysis and primary goal-difficulty research | graded progression, goal review, capacity |
| `concept-goal-conflict` | `missing` | Identify whether goals compete for time, resources, or direction before prioritizing | systematic review/meta-analysis or prospective goal-conflict research | goal review, autonomy, capacity |
| `concept-time-estimation` | `weak` | Treat duration estimates as uncertain and update them from records | planning-fallacy primary research plus review/meta-analysis where available | action planning, self-monitoring, capacity |
| `concept-motivation-variability` | `missing` | Plan action without assuming motivation will remain constant | longitudinal/within-person motivation evidence plus motivational theory review | goal autonomy, action planning, self-monitoring |
| `concept-behavioral-feedback` | `weak` | Interpret records as feedback for adjustment rather than judgment | feedback intervention meta-analysis/review plus self-regulation evidence | self-monitoring, goal review, graded progression |
| `concept-interleaved-practice` | `missing` | Choose mixed versus blocked practice when discrimination is the learning target | interleaving meta-analysis/systematic review and direct learning experiments | retrieval practice, spaced practice |
| `concept-false-fluency` | `weak` | Detect when ease/familiarity is mistaken for durable learning | metacognition review and direct learning/judgment experiments | retrieval practice, spaced practice, self-monitoring |
| `concept-sleep-regularity` | `weak` | Consider timing regularity separately from duration while preserving medical boundaries | consensus/guideline or systematic review plus prospective sleep evidence | sleep duration, tiredness playbook, irregular schedule |

### Playbooks

| Proposed playbook ID | Classification | Distinct decision policy | Required concept relations |
|---|---|---|---|
| `pb-user-stops-after-starting` | `missing` | Locate the drop-off point and distinguish friction, dose, and repetition before changing the plan | observable behavior, self-monitoring, task aversiveness, graded progression |
| `pb-user-missed-several-days` | `missing` | Separate an ordinary lapse from changed capacity/context and resume without compensation | lapse recovery, habit formation, self-monitoring |
| `pb-user-created-too-many-habits` | `missing` | Map competition, choose a protected minimum, and sequence remaining habits | goal conflict, graded progression, goal review |
| `pb-user-waits-for-motivation` | `missing` | Validate low motivation, check whether the goal remains chosen, then plan a low-dependence action | motivation variability, goal autonomy, action planning |
| `pb-user-has-vague-goal` | `missing` | Clarify desired outcome, specify observable behavior, then define context | goal specificity, behavior-vs-outcome goals, action planning |
| `pb-user-set-unrealistic-goal` | `missing` | Identify which constraint makes the target implausible and adjust scope, pace, or deadline | goal difficulty, goal review, graded progression |
| `pb-user-has-conflicting-goals` | `missing` | Identify the type of conflict before choosing coexistence, sequencing, or deliberate deprioritization | goal conflict, goal autonomy, goal review |
| `pb-user-wants-to-compensate` | `missing` | Choose resume, redistribute, or drop; avoid untested workload spikes | lapse recovery, graded progression, goal review |
| `pb-user-is-progressing-sustainably` | `missing` | Reinforce the stable mechanism, verify cost, and change only with a reason | behavioral feedback, self-monitoring, graded progression |
| `pb-user-increases-difficulty-too-quickly` | `missing` | Check stability and cost, then increase one variable with a review point | graded progression, behavioral feedback, physical-activity consistency |

## Stage A decision

The proposed controlled expansion is 16 knowledge documents and 10 playbooks, yielding 28 knowledge units, 17 playbooks, and 45 active documents if every evidence check succeeds. This is a consequence of the decision inventory, not a target count. Stage B may reject or merge a proposal if direct evidence, distinctness, or retrieval value is not confirmed during source verification.

## Stage B resolution

All 26 proposals passed the distinctness, decision-value, direct-evidence and retrieval-value checks and were implemented as `machine_audited` units on 2026-07-14. No archived document was restored. The final evidence, relationship, validation and duplication results are recorded in `COVERAGE_EXPANSION_REPORT.md`; each row in `COVERAGE_GAPS.jsonl` records `stage_b_outcome: created` and remains subject to human editorial review.
