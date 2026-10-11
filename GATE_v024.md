# v0.2.4 documentation-only repair gate

## Scope
Only release documentation, citation version, version metadata, manifest, and historical status qualifications were revised from the v0.2.3 source baseline. Engine algorithms, policy definitions, raw adapter implementations, tests, reference tables, and prepared-input data are unchanged at the byte level. The v0.2.3 public tag and archive are not modified.

All files tracked by the public v0.2.3 tag are retained, including the five historical plaintext validation logs under `reports/`. `GATE_v024.md` is the only newly added source-package file.

## Manifest identities
- `MANIFEST_SHA256.csv` inventories every file in this v0.2.4 source package except itself.
- `SHA256_CANDIDATE_MANIFEST.json` inventories the public v0.2.3 tracked tree at commit `c1afa595e2d6e24487889094272d3641e8e905dc`, excluding itself. It is a comparison baseline, not the current-package manifest.

## Historical public releases
- v0.2.2 https://doi.org/10.5281/zenodo.23287169
- v0.2.3 https://doi.org/10.5281/zenodo.23292299
- v0.2.4: new DOI only after Zenodo publication; none claimed in this candidate.

## Baseline evidence
Isolated installed v0.2.3 wheel: 39/39 tests; six bounded internal reference-linker cases; RI 2024 and MA 2024 four-unit prepared regressions. A four-unit MA raw run was recorded in the earlier gate but was not independently repeated without raw bytes; no new RI raw run. See RELEASE_STATUS.md.

## Independent clean-room result (11 Oct 2026)
The corrected source candidate passed a fresh wheel build and isolated Python 3.12.14 installation with resolved dependencies. Installed-package origin, dependency consistency, CLI operation, 39/39 automated tests, six/six bounded typed-identity cases, RI 2024 and four-unit MA 2024 prepared-input regressions, the frozen derived RI 2023 counts and Policy A–D totals, and both manifest identities passed. No raw EPA inputs were acquired or rerun in this gate.

## Publication boundary
This gate authorizes the corrected source candidate for publication as a documentation-only v0.2.4 release. Publication itself was not performed. A new GitHub tag/release must be created separately, followed by provider-assigned Zenodo DOI verification. Do not change the public v0.2.3 release and do not preassign a v0.2.4 DOI.
