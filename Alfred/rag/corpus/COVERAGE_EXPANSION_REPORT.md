# Controlled coverage expansion report

Date: 2026-07-14  
Architecture: Alfred-only canonical v1  
Editorial ceiling: `machine_audited`; every canonical unit still has `requires_human_review: true`.

## Outcome

The controlled expansion added 16 distinct knowledge documents and 10 recurrent-situation playbooks. The active corpus now contains:

| Asset | Before | After | Change |
|---|---:|---:|---:|
| topics | 9 | 9 | 0 |
| knowledge documents | 12 | 28 | +16 |
| playbooks | 7 | 17 | +10 |
| active documents | 19 | 45 | +26 |
| registered sources | 31 | 47 | +16 |
| sources used by production knowledge | 20 | 36 | +16 |
| active quotes | 0 | 0 | 0 |

The final size falls inside the orientation range because the coverage analysis identified that many requested items could share a scientific mechanism or an existing decision tree. No count was used as an acceptance criterion.

## Stage A diagnosis

`COVERAGE_MATRIX.md` assessed all 26 required Alfred situations and every scientific concept named in the request. `COVERAGE_GAPS.jsonl` recorded only actionable `missing` or `weak` items that met the preliminary creation criteria.

Three boundaries prevented artificial expansion:

- “User only wants to be heard” remains a system-level conversational-mode decision, not a scientific topic document.
- “User wants scientific evidence” remains an evidence/citation policy; the retrieved concept should provide its own source mapping.
- “Decision fatigue” was not promoted to a canonical construct because its boundaries and incremental decision value were insufficient; Alfred should reason from observable load, conflict, capacity and constraints.

Situations classified as `partially_covered` were routed through existing playbooks plus stronger concept relations. They did not automatically receive new files.

## Knowledge added

| Topic | New concepts | Decision value |
|---|---|---|
| habits | environmental cues and friction; graded task progression; lapse recovery | distinguish contextual barriers, feasible progression and ordinary interruption |
| procrastination | task aversiveness; temporal discounting; evaluative avoidance | discriminate unlike mechanisms behind delay instead of returning one generic explanation |
| goals | behavior versus outcome goals; specificity; difficulty; conflict | translate, calibrate and coordinate goals before action planning |
| planning | time estimation | update duration forecasts from task boundaries, components and comparable observations |
| motivation | motivation variability | treat willingness as a changing condition without ignoring endorsement, capacity or health |
| self-regulation | behavioral feedback | connect records to maintain/investigate/adjust decisions without moral judgment |
| study and learning | interleaved practice; false fluency | choose mixed practice for discrimination and test familiarity against delayed performance |
| sleep and recovery | sleep regularity | separate timing consistency from duration while preserving medical and catch-up-sleep boundaries |

Each knowledge unit contains an operational definition, exclusions, mechanisms, evidence summary, claim-level evidence mapping, alternative explanations, required information, practical implications and limitations. All bodies are canonical English and contain no agent instructions.

## Playbooks added

The new decision policies cover users who start and stop, miss several days, create too many habits, wait for motivation, hold a vague or unrealistic goal, face conflicting goals, want to compensate, are progressing sustainably, or propose increasing difficulty too quickly.

The playbooks were kept separate only where the activation and decision path differ. Examples of deliberate consolidation include:

- fear of failure and perfectionistic delay share the existing standards-block-completion playbook, supported by the new evaluative-avoidance concept;
- repeated postponement continues to use cannot-start plus mechanism-specific knowledge;
- overwhelm and inability to prioritize continue to use capacity, goal review and goal conflict rather than duplicate policies;
- environmental friction is handled by the initiation/continuation playbooks and a new concept, not by another situation file.

## Evidence research and source diversity

Sixteen sources were added only after metadata and directly relevant findings were checked against journal, PubMed/PMC or institutional repository records. The additions include longitudinal or natural-experiment habit research, experimental planning and learning studies, an intensive longitudinal motivation study, systematic reviews/meta-analyses, a formal sleep consensus and a theoretical review grounded in decades of goal-setting studies.

Across the 36 production sources, the source-role distribution is:

| Source role | Count |
|---|---:|
| primary journal studies | 12 |
| secondary journal reviews/meta-analyses | 18 |
| consensus statements | 3 |
| book-chapter meta-analysis | 1 |
| institutional guideline | 1 |
| institutional guidance | 1 |

Production source years span 1994–2025. The most reused source is the BCT Taxonomy in 7 of 28 knowledge documents; it supplies standardized technique definitions, not isolated efficacy claims. The next most reused sources appear in four documents. Mechanism claims use directly related primary studies or syntheses, and every reused source retains a scope limitation in `source_registry.jsonl`.

Important evidence boundaries preserved during writing include:

- contextual stability is predictive and context-sensitive, not environmental determinism;
- graded-task evidence is domain-limited and cannot prescribe clinical or exercise progression;
- one missed opportunity does not establish that every interruption is harmless;
- perfectionistic concerns and perfectionistic strivings have different average associations;
- a correlation between discounting and a trajectory measure does not establish individual causality;
- goal-setting effects depend on commitment, ability, feedback, complexity and setting;
- interleaving effects change with material and similarity structure;
- fluency can mislead, but subjective ease is not always false;
- sleep-regularity evidence is largely observational and supplies no universal variability threshold.

## Relationship and registry updates

All nine `topic.yaml` files remain the authoritative topic layer. Their concept and playbook lists, descriptions and retrieval terms now reflect the expansion. `concept_registry.jsonl` has 28 exact concept rows and bidirectional playbook relationships where a decision policy uses a concept. `document_registry.jsonl` has 45 exact production paths. Source usage lists were recalculated against all knowledge frontmatter.

`INDEX.md` now reports the new per-topic totals. Historical counts in `migration/MIGRATION_REPORT.md` were intentionally left unchanged because they describe the completed migration baseline, not the current expansion.

## Validation and duplication analysis

The canonical validator completed with `status: ok`, zero errors and zero warnings. It checked topic relationships, IDs, frontmatter, active source references, evidence mappings, English bodies, required sections, playbook length, registries, production exclusions, source usage and repeated normalized prose blocks.

Additional duplication checks produced:

- 45 unique canonical filenames, document IDs and unit IDs;
- 990 pairwise full-body comparisons;
- zero pairs at or above a conservative normalized-text similarity ratio of 0.45;
- zero repeated canonical prose blocks of at least 100 normalized characters;
- all 17 playbooks within the 300–900-word safety proxy (315–440 words).

Conceptual overlap was retained only when it supports cross-topic routing. For example, goal difficulty and graded progression are linked but answer different questions: one evaluates a target relative to conditions; the other defines how task demand changes over attempts.

## Archive and scope controls

No file under `Alfred/rag/corpus/archive/legacy/pre-alfred-20260714/` was moved, copied or reactivated. Archived texts were not treated as evidence and no prior boilerplate was restored. Feedbacker material, critical safety handling, cases, evaluation fixtures, unverified quotations and system prompt candidates remain outside the production registry.

## Remaining work and limitations

This expansion is machine-audited, not human-approved. Before commercial indexing, a qualified human reviewer should check scientific interpretation, product voice, trigger collisions and the medical/safety boundary in medium-risk units. Retrieval evaluation should then test the 26 named situations plus adversarial near-neighbors, especially:

- ordinary tiredness versus a health or safety signal;
- ambitious goals versus infeasible goals;
- careful revision versus evaluative avoidance;
- a short lapse versus a changed context or capacity;
- useful interleaving versus unrelated task switching;
- sleep regularity guidance versus insufficient duration or a sleep disorder.

The corpus is now broad enough for this defined Alfred scope, but production quality still depends on the Security Gate running before ordinary retrieval and on using registries rather than directory-wide indexing.
