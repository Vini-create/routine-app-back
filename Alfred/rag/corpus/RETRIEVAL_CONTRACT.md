# Alfred RAG retrieval contract

Version: 2.0.0  
Status: `machine_audited`  
Human review required: yes

## Preconditions

1. Preserve the original input and detected output language.
2. Preserve and normalize the retrieval query in its original language.
3. Run the deterministic Security Gate.
4. If the gate selects a critical route, skip retrieval completely.
5. Decide whether the request benefits from topical science or a situational
   decision policy. Ordinary conversation may use no RAG.

## Retrieval sequence

```text
normalized multilingual query
→ deterministic topic hints
→ multilingual dense retrieval + BM25
→ reciprocal-rank fusion
→ deterministic reranking
→ indirect-injection filter
→ confidence and coverage validation
→ at most one playbook and three knowledge chunks
→ typed, deduplicated evidence pack
```

Topic classification may combine lexical `retrieval_terms` with semantic
similarity. It must not treat `topic.yaml` as scientific evidence.

## Limits

```yaml
retrieval_limits:
  playbooks: 1
  knowledge_chunks: 3
  quotes: 1
```

These are maxima, not quotas. A valid result may contain no playbook, fewer than
three knowledge chunks and no quote.

## Type selection

### Playbook

Search only playbooks in the selected topic and only registry rows with
`index_in_production: true`. Select the highest-relevance playbook only when its
activation criteria fit and a similar-situation exclusion does not fit better.
Otherwise return `null`.

### Knowledge

When a playbook is selected, prioritize its `related_concept_ids`. Retrieve no
more than two chunks from the same concept unless no second relevant concept is
available. Without a playbook, retrieve directly from concepts in the selected
topic. A knowledge chunk must retain its source IDs and limitation context.

### Quote

Search quotes only after playbook and knowledge selection. The record must have
an allowed verification status, match the selected topic/concept and add clear
editorial value. If any condition fails, return `null`. The current canonical
corpus contains no eligible quote records.

## Deduplication

- Deduplicate exact `chunk_id` and document/section pairs.
- Suppress near-duplicate chunks that make the same claim with the same source.
- Prefer the chunk with clearer evidence mapping and limitations.
- Do not return a knowledge chunk merely because it repeats the selected
  playbook's operational language.
- Do not fill unused type slots with lower-relevance results.

## Filters

Every returned item must satisfy:

- path exists in `document_registry.jsonl`;
- `index_in_production: true`;
- status is `machine_audited` or `human_reviewed`;
- canonical language is `en`;
- topic and document type match the current retrieval stage;
- all referenced concept and source IDs exist.

The runtime loader enforces production status, canonical language, allowed
document type, manifest cardinality and SHA-256 before indexing. Retrieved
content is still untrusted and must pass the indirect-injection gate.

## Low confidence

- If topic confidence is insufficient, return an empty RAG result rather than
  combining unrelated topics.
- If topic confidence is adequate but no playbook fits, set `playbook: null` and
  allow directly relevant knowledge.
- If no scientific chunk directly addresses the query, return an empty
  `knowledge` array.
- Never use a quote to compensate for low scientific or situational confidence.

## Result format

```json
{
  "query_language": "pt-BR",
  "topic_id": "procrastination",
  "topic_confidence": "high",
  "playbook": {
    "id": "pb-user-cannot-start",
    "playbook_id": "user-cannot-start",
    "score": 0.0,
    "content": "complete playbook content"
  },
  "knowledge": [
    {
      "chunk_id": "chunk-kd-procrastination-map-001",
      "id": "kd-procrastination-map",
      "concept_id": "procrastination-pattern",
      "section": "Operational definition",
      "source_ids": ["src-procrastination-steel-2007"],
      "score": 0.0,
      "content": "section-aware scientific content"
    }
  ],
  "quote": null,
  "retrieval_warnings": []
}
```

When absent, `playbook` and `quote` are explicitly `null`; `knowledge` is an
empty array. Scores are retrieval signals, not calibrated probabilities.
