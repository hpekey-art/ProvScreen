# ProvScreen 0.2.1 MIT-licensed candidate (not yet deposited)

- MIT license authorized by author; applies to source code, **not** EPA data or third-party inputs.
- Automated regression: 17 tests.
- Fresh local raw RI2024 and MA2024 scoped demonstrations and reference policy checks evidenced in `reports/`. The original raw ZIP/CSV is not redistributed.
- Blackstone numeric F28 ledger verification: `python verify_f28.py evidence/F28_hourly_unit_reconciliation.csv`.
- Packaging provides Python wheel to be built with `python -m build` when available or `pip wheel --no-deps --no-build-isolation .`; content identified by SHA-256 in MANIFEST_SHA256.csv.
- **Not a public release** until deposited and its actual permanent DOI/URL is checked. No DOI invented.
- Windows user operation was demonstrated previously on prepared input, not a third-party or Windows raw reconstruction.
- Mapping regulatory authorization, full record-level lossless ECMPS provenance, statewide MA, non-EPA systems, and 2023 XML parser are out of scope.
- Input error checks and safe output publishing are covered by the test suite; compatibility minimums are not exhaustively validated.
