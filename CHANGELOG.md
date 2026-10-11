# Changelog

## 0.2.4 — documentation and release-identity synchronization
- Correct inconsistent public-release status and citation guidance left in the archived v0.2.3 documentation; the historical v0.2.3 archive itself remains unchanged.
- Synchronize current package version identifiers to 0.2.4 without changing the policy engine, raw adapters, test logic, prepared inputs, or frozen Rhode Island 2023 analysis.
- Replace incomplete source checksums with a complete, reproducible manifest covering tracked package files (excluding self-referential manifest files).
- Retain the five historical plaintext validation logs present in the public v0.2.3 tracked tree and enumerate them in the v0.2.4 source manifest.
- Replace the stale development JSON inventory with an exact, non-self-referential public-v0.2.3 baseline manifest tied to Git commit `c1afa595e2d6e24487889094272d3641e8e905dc`.
- Clarify validation evidence levels: installed-wheel 39-test gate, prepared RI/MA regressions, recorded four-unit MA raw-adapter gate, and the absence of a fresh v0.2.3 RI raw rerun.
- This entry does not assert a v0.2.4 Zenodo DOI before provider publication and verification.


## 0.2.3 — published 2026-10-11 (historical release)
- Introduce typed identifiers that distinguish EPA unit IDs from stack/pipe IDs in source matching.
- Reject ambiguous unit/stack keys and unmapped stack lineage rather than treating matching text labels as equivalent identities.
- Require an explicit map before inheriting provenance from a shared-stack source to a unit.
- Repair a pandas 3-sensitive noncontiguous-event test fixture assignment.
- Preserve the frozen Rhode Island 2023 definitions, event population, calculations, and reference results unchanged.
- Add six synthetic typed-identity reference cases and extend the automated suite to 39 tests.

Historical public version: https://github.com/hpekey-art/ProvScreen/releases/tag/v0.2.3 ; version DOI: https://doi.org/10.5281/zenodo.23292299 . The v0.2.3 archive remains unchanged; its historical release-state documents were inconsistent.

## 0.2.1 — 2026-10-10 (historical entry)
- MIT licensing and publication-candidate packaging.
- Fail-closed output directories and zero-event protections; additional input validation and tests.
- Saved RI2024 and scoped MA2024 real-raw regression evidence and separate Blackstone F-28 ledger check.
- No changes to frozen 2023 scientific definitions or results.

Historical note: this text originated in a local candidate. Public v0.2.1 was subsequently released; see its archived tag.

## 0.2.2 — published 2026-10-10 (historical release)
- Repair S01: reject within-roster CAMPD timestamp gaps instead of silently shortening startup windows.
- Repair S02: validate integer hour and finite source Operating Time for direct/shared-stack ECMPS records.
- Add source-kind check on mapped stack targets.
- 27 automated tests; independently rerun RI2024 and four-unit MA2024 local raw regression.
- Add bounded naive flat-table contract demonstration; no change to 2023 frozen science.
