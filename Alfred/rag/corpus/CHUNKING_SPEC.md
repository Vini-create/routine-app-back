# Canonical chunking specification

Version: 1.0.0  
Status: `machine_audited`  
Human review required: yes

## General rules

- Build records only from `document_registry.jsonl` rows marked
  `index_in_production: true`.
- Preserve `document_id`, `document_type`, `topic_id`, language, status and
  source path in sidecar metadata.
- Never chunk or embed `archive/`, `migration/`, `non_indexed/`, `sources/`,
  registries, schemas, reports or `topic.yaml` as response context.
- Normalize whitespace without rewriting scientific wording.
- Use deterministic chunk IDs so a rebuild does not silently duplicate vectors.

## Knowledge

Target 250–650 model tokens per chunk.

- Split on semantic Markdown sections, not arbitrary token windows.
- Keep one main idea per chunk.
- Preserve `topic_id`, `concept_id`, complete `source_ids`, title and section
  names.
- Keep a scientific claim with its evidence strength, caveat and limitation.
- Combine adjacent short sections from the same document only when they form one
  coherent claim unit.
- Split a long section at paragraph boundaries; repeat only the minimum heading
  and metadata needed for interpretation.
- Do not create a chunk containing only `Sources` or only an evidence citation
  without the supported statement.
- Do not mix concepts or documents in one chunk.

Recommended metadata:

```json
{
  "chunk_id": "chunk-kd-habit-formation-001",
  "document_id": "kd-habit-formation",
  "document_type": "knowledge",
  "topic_id": "habits",
  "concept_id": "habit-formation",
  "section": "Evidence summary + Evidence mapping",
  "source_ids": ["src-habit-lally-2010", "src-habit-review-2024"],
  "language": "en",
  "status": "machine_audited"
}
```

## Playbooks

Target 300–900 model tokens. Prefer one whole-document record.

All current playbooks are intentionally bounded and should be embedded as
complete documents. Preserve `playbook_id`, `related_concept_ids`, trigger
phrases and exclusions. If a future playbook exceeds the range because it
contains two different situations, split the editorial document into distinct
playbooks instead of applying blind chunking.

Recommended ID: `chunk-<document_id>-whole`.

## Quotes

Each JSONL row is one independent record. Do not create additional quote chunks.
Preserve quote, author, work, location, source, topic, concepts and verification
status. No quote vectors should be built while the canonical corpus has no
eligible quote collection.

## Token counting and validation

Use the tokenizer of the selected embedding model at build time. Word counts
are not accepted as the production token count. The build must fail when a
knowledge record falls outside 250–650 tokens unless an explicit audited
exception is stored, or when a playbook exceeds 900 tokens.

## FAISS layout

Use either separate FAISS indexes by document type or one index with a mandatory
metadata sidecar and typed over-fetch. In both designs, final selection must
enforce the limits in `RETRIEVAL_CONTRACT.md`; raw untyped top-k output is not a
valid Alfred context.
