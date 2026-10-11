# Changelog

## 0.2.3 — release candidate (not published)
- Introduce typed identifiers that distinguish EPA unit IDs from stack/pipe IDs in source matching.
- Reject ambiguous unit/stack keys and unmapped stack lineage rather than treating matching text labels as equivalent identities.
- Require an explicit map before inheriting provenance from a shared-stack source to a unit.
- Repair a pandas 3-sensitive noncontiguous-event test fixture assignment.
- Preserve the frozen Rhode Island 2023 definitions, event population, calculations, and reference results unchanged.
- Add six synthetic typed-identity reference cases and extend the automated suite to 39 tests.

This entry does not assert a public v0.2.3 tag, archive, or DOI. Release-gate evidence and remaining limitations are recorded in `RELEASE_STATUS.md` and `GATE_v023.md`.

## 0.2.1 — 2026-10-10 (candidate)
- MIT licensing and publication-candidate packaging.
- Fail-closed output directories and zero-event protections; additional input validation and tests.
- Saved RI2024 and scoped MA2024 real-raw regression evidence and separate Blackstone F-28 ledger check.
- No changes to frozen 2023 scientific definitions or results.

This is a GitHub upload candidate, not a verified public release/DOI.

## 0.2.2 (local candidate, not a public release)
- Repair S01: reject within-roster CAMPD timestamp gaps instead of silently shortening startup windows.
- Repair S02: validate integer hour and finite source Operating Time for direct/shared-stack ECMPS records.
- Add source-kind check on mapped stack targets.
- 27 automated tests; independently rerun RI2024 and four-unit MA2024 local raw regression.
- Add bounded naive flat-table contract demonstration; no change to 2023 frozen science.
