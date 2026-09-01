# Winperium Alfred RAG

This directory is the smallest verified retrieval layer used by Alfred in the
first Winperium version. Canonical retrieval content is English because user
input is translated and normalized before search; the final answer is produced
in the user's original language.

## Runtime boundary

```text
original multilingual input
→ normalization and deterministic topic hints
→ Security Gate
→ decision whether RAG is needed
→ dense + BM25 retrieval and deterministic reranking
→ Main LLM
→ answer in the original language
```

Only files listed with `index_in_production: true` in
`document_registry.jsonl` may become FAISS records. Feedbacker, critical safety,
migration material, source storage and archived content are never indexed.

## Canonical unit types

- `knowledge`: scientific or conceptual evidence, one concept per document.
- `playbook`: one situational decision policy for Alfred.
- `quote_collection`: optional verified editorial material; currently none pass
  the activation gate.

`topic.yaml` files provide classification and relations, not full scientific
content. Read `RETRIEVAL_CONTRACT.md` and `CHUNKING_SPEC.md` before building
records.

## Governance

The highest status assigned by this migration is `machine_audited`. Human
review remains required. Verify sources at their primary or official repository,
keep claim-level evidence mapping, and never infer efficacy from a taxonomy
alone.

Run:

```bash
python Alfred/rag/corpus/scripts/validate_rag.py
```

Historical migration snapshots and internal prompt/security candidates are
kept outside public version control. The public corpus contains the canonical
documents, registries, validation contracts, source metadata, and reproducible
runtime build artifacts.
