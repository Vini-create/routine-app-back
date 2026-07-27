# Alfred-only RAG migration baseline

Created on 2026-07-14 before any file was moved, renamed, merged, archived or
removed.

## Immutable checkpoint

- Snapshot: `.audit_checkpoints/rag-pre-alfred-migration-20260714T000000-0300.tar.gz`
- SHA-256: `91523448296784fbb5af7629950f4691d7a63a0438cdb2d4ad20702802650e94`
- Archive entries: 404
- Snapshot contents: 338 files and 66 directories, including the empty
  `rag/migration/` directory created immediately before the archive.

The checkpoint is outside `rag/` so it cannot be mistaken for retrievable
content or recursively included in later migration artifacts.

## File inventory

`PHASE1_FILE_INVENTORY.jsonl` contains the path, byte size, SHA-256 digest and
extension of every file present in the checkpoint. The inventory itself was
created after the snapshot and is therefore intentionally not one of its rows.

- Files: 338
- Total bytes: 2,048,579
- Markdown: 264
- JSONL: 33
- Python source: 14
- Python bytecode: 14
- JSON: 10
- `.gitkeep`: 3

## Baseline constraints

- `rag/` is not tracked by Git in the current workspace, so a Git commit could
  not serve as a trustworthy checkpoint.
- No content path was moved or removed before this baseline was completed.
- Every later relocation must be represented in `FILE_MAPPING.jsonl`.
- No migrated document may be promoted above `machine_audited` by this process.
