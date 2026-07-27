# Alfred-only RAG migration changelog

## 2026-07-14 — Phase 1 complete

- Created and checksum-verified an immutable pre-migration snapshot outside the
  RAG tree.
- Inventoried 338 files and 66 directories before any relocation.
- Recorded file size and SHA-256 for every baseline file.
- Confirmed that no file had been moved, renamed, merged, archived or removed.

## 2026-07-14 — Phase 2 complete

- Inspected all 338 baseline files and quantified documents, sources, quotes,
  evaluation records and quarantine material.
- Recorded the mismatch between the prior two-agent tree and the Alfred-only
  runtime architecture.
- Confirmed that the inspected tree has no English canonical layer; identified
  the 12 machine-audited Portuguese knowledge files as controlled adaptation
  sources rather than performing blind translation.

## 2026-07-14 — Phase 3 complete

- Classified every baseline file exactly once in `FILE_CLASSIFICATION.jsonl`.
- Identified 12 knowledge and seven Alfred playbooks for canonical migration.
- Separated Feedbacker, Security Gate, system-policy, unverified quote, source
  storage and legacy/control-plane material.
- Performed no relocation during classification.

## 2026-07-14 — Phase 4 complete

- Selected nine non-empty final topics.
- Merged observable behavior into `self-regulation` and capacity decisions into
  `planning`.
- Rejected four broad or unsupported topics instead of creating empty folders.
- Fixed the final active target at 12 knowledge documents, seven playbooks and
  zero quotes unless a quote later passes an allowed verification state.

## 2026-07-14 — Phase 5 complete

- Created nine `topic.yaml` files and no empty thematic topic.
- Declared all final concept and playbook relationships before document
  migration.
- Set every quote file to `null`; no quote collection was fabricated to satisfy
  the directory example.

## 2026-07-14 — Phase 6 complete

- Adapted the 12 verified knowledge documents into controlled English canonical
  documents without adding concepts.
- Preserved every source ID and claim-level evidence mapping.
- Removed Alfred/Feedbacker scripts, generic conversational questions,
  procedural trees and repeated safety instructions from scientific knowledge.
- Merged observable behavior into `self-regulation`; all other scientific
  concepts remain distinct.
- Confirmed 12 unique document IDs, 12 unique concept IDs, valid YAML and valid
  references to the source registry.

## 2026-07-14 — Phase 7 complete

- Migrated seven distinct Alfred situations into English topical playbooks.
- Renamed agent-prefixed IDs to stable situation IDs and recorded source paths
  for the later file mapping.
- Removed fixed response scripts, repeated science and repeated universal safety
  policy while retaining situation-specific decision branches.
- Excluded listening preference, evidence-request handling and safety handoff
  from topical retrieval; their useful rules are scheduled for `non_indexed/`.

## 2026-07-14 — Phase 8 complete

- Audited all 56 quote records across eight legacy collections.
- Confirmed that every record is `attribution_uncertain` and inactive.
- Selected zero active quotes and zero canonical quote files; no quote was added
  merely to fill a retrieval slot.
- Preserved the four associated source records as inactive metadata requiring
  human review.

## 2026-07-14 — Phase 9 complete

- Consolidated universal conversation and epistemic rules in
  `non_indexed/system_prompt_candidates.md` without changing the product prompt.
- Consolidated critical-route candidates in
  `non_indexed/security_gate_candidates.md` without implementing the gate.
- Generated 370 migration mapping rows: 333 physical archive movements and 37
  content consolidations into canonical or non-indexed targets.
- Moved exactly 333 baseline files to
  `archive/legacy/pre-alfred-20260714/`; all mapping targets exist and no
  archived original path remains active.

## 2026-07-14 — Phase 10 complete

- Removed literal, structural, semantic and operational duplication from the
  active target.
- Confirmed zero repeated canonical prose blocks of at least 100 normalized
  characters.
- Confirmed that no non-source directory is empty.
- Documented why related concepts and situations remain distinct in
  `DEDUPLICATION_REPORT.md`.

## 2026-07-14 — Phase 11 complete

- Rebuilt `concept_registry.jsonl` with 12 canonical concepts and their
  playbook/source relationships.
- Rebuilt `document_registry.jsonl` with only 19 canonical production inputs.
- Replaced the root README and index with the Alfred-only runtime boundary.
- Confirmed that zero archive, migration, non-indexed or source paths are marked
  for production.

## 2026-07-14 — Phase 12 complete

- Defined typed retrieval with a maximum of one playbook, three scientific
  chunks and one optional quote.
- Defined null and empty-array behavior for low confidence or missing types.
- Defined source-preserving semantic chunking and whole-playbook retrieval.
- Documented FAISS metadata-sidecar and post-filter requirements so raw untyped
  top-k results cannot become Alfred context.

## 2026-07-14 — Phase 13 complete

- Replaced the prior validator with an Alfred-only canonical validator.
- Validated JSON, JSONL, YAML, IDs, relationships, sources, registries, English
  canonical content, archive boundaries, retrieval value and duplication.
- Corrected all ten findings from the first run: one short playbook, eight
  replaced-path false positives and generated Python bytecode.
- Reached zero errors and zero warnings.

## 2026-07-14 — Phase 14 complete

- Generated `MIGRATION_REPORT.md` with inventory, movements, active counts,
  exclusions, sources, deduplication, retrieval readiness and human-review work.
- Added the final report to the required validation surface.
- Left all canonical documents at `machine_audited`; none was marked as reviewed
  by a human.
- Completed the source-storage boundary with a non-indexed `sources/original/`
  directory and documented the purpose of all four source subdirectories.
