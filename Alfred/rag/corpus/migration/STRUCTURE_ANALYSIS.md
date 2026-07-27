# Current RAG structure analysis

Date: 2026-07-14

## Scope inspected

The analysis covers all 338 baseline files. `FILE_CLASSIFICATION.jsonl` has one
classification row for every baseline path and no duplicate paths.

## Current runtime-relevant inventory

- 12 machine-audited knowledge documents, all in Portuguese.
- 10 machine-audited Alfred playbooks, all in Portuguese.
- 10 machine-audited Feedbacker playbook files, including its evidence guide.
- 30 machine-audited cases: 11 Alfred, nine Feedbacker, five ambiguity cases
  and five safety handoff cases.
- 12 generated safety documents.
- 12 machine-audited but inactive technique records.
- 56 inactive quotes; every quote is `attribution_uncertain`.
- 31 source records; 27 are active and verified, four remain under human review.
- 120 generated and inactive evaluation records.
- 210 prior items represented in quarantine records.
- Zero documents currently marked for production indexing.

## Architectural mismatch

The current tree models Alfred, Feedbacker, shared routing, cases, safety,
techniques and evaluation as neighboring collections. The product now needs a
single topical RAG for Alfred. Feedbacker analysis, critical safety, routing,
cases and generators therefore create false retrieval candidates even while
they are marked inactive.

The brief mentions an existing English canonical layer, but the inspected tree
does not contain one. The best scientific material is the 12 Portuguese
machine-audited knowledge documents reconstructed in Phase 5. The migration
will preserve their claims, evidence mapping, source IDs and limitations while
performing a controlled English editorial adaptation. It will not claim that a
pre-existing English document was found or perform bulk blind translation.

## Content decisions

### Canonical candidates

- All 12 active knowledge documents: retain one concept per document, remove
  agent scripts, conversation questions, universal rules and repeated safety
  instructions.
- Seven Alfred playbooks: retain distinct situations for inability to start,
  questioned/imposed goals, irregular schedules, insufficient capacity,
  standards blocking completion, rejected suggestions and tiredness.

### Extract outside FAISS

- Explicit listening preference and requests for evidence are universal
  conversation policies, not topical science.
- Safety handoff and all 12 safety documents belong to the Security Gate.
- Shared coaching, uncertainty and agent-contract rules belong to system prompt
  candidates.

### Archive

- All Feedbacker playbooks and cases.
- All cases and evaluation datasets from the prior architecture.
- All 56 quotes because none meets an allowed verification state.
- Inactive techniques, old generators, reports, audits and quarantine trees.
- Superseded schemas, registries, root documentation and validator.

## Deduplication findings

- The 48 legacy knowledge files use recurring generic questions and boilerplate;
  they remain historical evidence only.
- The active knowledge set has no literal repeated paragraphs, but it mixes
  scientific explanation with Alfred/Feedbacker application. That structural
  duplication will be removed from canonical knowledge.
- `pb-a-listen` duplicates a universal preference-following rule;
  `pb-a-science` duplicates evidence-use policy; `pb-a-safety-handoff`
  duplicates the Security Gate boundary. None belongs in topical retrieval.
- The 12 technique records overlap the mechanisms and strategies already linked
  by knowledge and playbooks. Keeping a fourth runtime document type would make
  balanced retrieval harder without adding a distinct response unit.

## Classification totals

- 19 canonical migration candidates: 12 knowledge and seven playbooks.
- 18 direct non-indexed extraction candidates: 12 safety, three Alfred/shared
  conversation files and three shared policy files.
- 19 current Feedbacker files explicitly classified for archive.
- Eight quote collections classified for archive.
- Five source-control files preserved outside retrieval.
- All remaining baseline files classified as legacy/control-plane archive.

No path was moved during Phases 2–4.
