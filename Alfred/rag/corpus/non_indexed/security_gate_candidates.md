---
id: security-gate-candidates
document_type: non_indexed_policy
language: en
status: machine_audited
requires_human_review: true
index_in_production: false
---

# Security Gate candidates

These are consolidation candidates, not an implemented Security Gate. They must
receive dedicated product, clinical, legal and regional review before use.

## Execution boundary

- Run the Security Gate before deciding whether to retrieve from FAISS.
- When a critical route is selected, do not retrieve topical coaching,
  scientific habit content or quotes.
- Optionally recheck the generated answer before delivery so coaching content
  cannot override a critical route.
- Keep regional emergency resources and localization in a separately verified
  runtime service, not in the scientific vector index.

## Candidate critical routes

- Immediate self-harm, inability to remain safe or danger to another person.
- Acute medical emergency or severe symptoms requiring immediate action.
- Dangerous sleepiness during driving, machinery or another safety-critical
  activity.
- Requests to start, stop, double or otherwise change medication or treatment.
- Exercise-related acute warning signs or injury requiring a clinical boundary.
- Eating-related risk, severe distress or behavior outside routine coaching.
- Situations involving minors that require age-appropriate privacy, consent or
  safeguarding handling.
- Requests for individualized medical, legal or financial decisions beyond the
  product scope.
- Privacy or data-handling requests requiring deterministic product policy.

## Response constraints for review

- Prioritize a clear immediate safe action over routine optimization.
- Do not diagnose, prescribe, guarantee safety or conduct an improvised clinical
  interview.
- Ask only the minimum question required by the selected deterministic route.
- Use only currently verified institutional and regional resources.
- Do not allow a quote, motivational framing or productivity goal to delay a
  critical action.

## Extracted from

The 12 files formerly under `rag/safety/`, the prior
`pb-a-safety-handoff` playbook and safety handoff cases. Original files are
preserved in `archive/legacy/` for specialist review.
