# Changelog

## Unreleased — alpha package reconstruction

- Reconstructed the importable `velisara_agent` layout from the historical
  flat upload and added the previously missing daemon worker base.
- Separated live runtime data from uploaded archival files; no automatic
  migration or changes to historical state.
- Made JSON boot validation fail closed on malformed persistent records and
  maintained JSONL journals (including interrupted final lines), with staged
  replacement for JSON writes. The journal is not automatically repaired.
- Replaced nonexclusive PID locking with exclusive creation and owner-only
  removal; cooperative stop during launcher shutdown.
- Added isolated startup, JSON/JSONL corruption-preservation and lock tests
  plus a two-version Python CI workflow.

Original uploaded Python files and archived data/logs remain in Git history
(and at top level, except the maintained root launcher). This entry records
the new reconstruction, not an inferred historical release.
