# ProvScreen (v0.2.1)

ProvScreen is an MIT-licensed Python command-line tool for **provenance-aware screening of EPA Part 75 startup NOx events**. It compares four frozen data-handling policies using either a validated event-hour CSV or **locally supplied** CAMPD hourly CSV plus ECMPS Emissions Export JSON files. It does not download EPA data or perform a lossless reconstruction of all ECMPS provenance fields.

**Research scope.** The Rhode Island 2023 study is a *frozen scientific reference*; this package checks a derived 2023 event master, not the original 2023 XML processing chain. Rhode Island 2024 and the **four-unit** Massachusetts 2024 pilot supply demonstration/regression cases. Neither the entire Commonwealth of Massachusetts nor non-EPA regulatory systems have been validated.

## Install and check

Python >=3.9 is declared; the full declared version range has not been individually tested. Internet access is normally needed to obtain Python dependencies. From the repository root:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
provscreen --source data/ri_2024_event_hours.csv --classifier epa_informed_2024 --outdir run-ri-new
provscreen --source data/ma_2024_event_hours.csv --classifier epa_informed_2024 --outdir run-ma-new
python verify_f28.py evidence/F28_hourly_unit_reconciliation.csv
```

**Always use a new output directory for each run.** The CLI refuses an existing output path; this prevents stale results from being reused after unsuccessful or empty runs.

## Input and provenance semantics

Prepared CSV requires `event_id, facility, unit, onset, offset, timestamp, modc, noxr_count, mass_A, bulk_indicator`. Mass is in **lb NOx**. Policy A is reported-as-submitted; B retains only records whose bulk indicator is exactly `Measured`; C retains parameter-specific NOXR non-substitution records (MODC 01/14 under the frozen rule); D keeps the original reported masses for events whose observed hours all satisfy the C rule. Legitimate `Calculated` bulk records are excluded by B, not declared invalid. A–C filter within a fixed event universe; D applies event-level eligibility. Unknown codes are not deemed non-substitution.

`frozen_2023` and `epa_informed_2024` are separate classifier modes. The original scientific rules for Rhode Island 2023 were not changed. Source files and the meaning/coverage of the input must be evaluated independently of a program exit code.

## Local raw adapter

```bash
provscreen --raw-bulk /local/emissions-hourly-2024-ri.csv --ecmps /local/Emissions_Export.zip --year 2024 --classifier epa_informed_2024 --outdir run-raw-ri-new
```

For the four-unit Massachusetts case, users must pre-scope the bulk CSV to the documented pilot and supply an explicit Blackstone map (`evidence/stack_map.json`). The map preserves **inherited common-stack source provenance**, not independent unit measurement or general regulatory approval. See [HOW_TO_REPRODUCE_RAW.md](HOW_TO_REPRODUCE_RAW.md) and [evidence/STACK_LINKAGE_SCOPE.md](evidence/STACK_LINKAGE_SCOPE.md).

The raw adapter does not acquire EPA files, parse original 2023 XML, infer stack topology, retain every monitoring-system/component/formula field, or verify all regulatory authorization. The F-28 ledger check is a *separate internal numerical consistency* check. Raw EPA files are **not redistributed** in this repository.

## Verification and source identity

- `tests/`: 17 automated software checks in the candidate test suite.
- `reference/2023_event_master.csv`: derived frozen reference, not raw 2023 source.
- `data/`: prepared 2024 event-hour demonstration inputs; Massachusetts covers four units only.
- `reports/`: saved candidate test and real-raw regression records. These are historical run evidence; they are not new raw-source reconstructions on the GitHub host.
- `reports/RAW_SOURCE_SHA256.csv`: hashes of **unbundled** raw inputs needed to repeat the historical raw-source demonstrations.
- `MANIFEST_SHA256.csv`: checksums of this repository content at assembly time.

See [RELEASE_STATUS.md](RELEASE_STATUS.md) for unresolved boundaries. For code citation use [CITATION.cff](CITATION.cff). **No public repository release or Zenodo DOI is claimed until an actual public release is made and verified.**

## License

Source code and original documentation are licensed under the [MIT License](LICENSE), copyright 2026 Hakan Pekey. This does not change upstream EPA source terms or license third-party content.
