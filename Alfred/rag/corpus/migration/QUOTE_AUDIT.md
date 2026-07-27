# Quote migration audit

Date: 2026-07-14

The eight legacy JSONL collections contain 56 quote records. All 56 have
`verification_status: attribution_uncertain`, `status: generated`,
`requires_human_review: true` and `active: false`.

The allowed active verification states are:

- `verified_primary_source`
- `verified_official_edition`
- `verified_reliable_secondary`

No current record meets that gate. The collections will therefore be preserved
under `archive/legacy/`, and no canonical topic will receive a quote file.
`quote_file: null` is intentional and valid. The four associated Gutenberg
source records remain in the source registry but inactive and under human
review, preserving traceability without implying verification.
