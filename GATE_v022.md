# Historical v0.2.2 pre-release gate (archival record)

The original gate below predates public v0.2.2 publication. Its candidate-status and pending-DOI statements are historical, not the current repository status. v0.2.2 version DOI: https://doi.org/10.5281/zenodo.23287169 .


**Historical gate status at the time:** local candidate. Public v0.2.2 was subsequently published with DOI https://doi.org/10.5281/zenodo.23287169 ; v0.2.1 also remains immutable.

## S01 — missing CAMPD clock hour
`raw.build` refuses an internal gap in the supplied clock-hour series for each selected facility/unit. It does not infer an operating stop from absence of a row. Explicit 0 remains an observed stop. Missing hours before the first or after the last supplied timestamp are a separate boundary/roster-completeness limitation.

## S02 — invalid ECMPS hour and operating-time
ECMPS/CAMPD clocks must be exact integral hours 0–23, and ECMPS operatingTime must be finite in [0,1] even for shared-stack mappings (where source and unit operation time need not equal). Arbitrary unit targets cannot masquerade as common stacks.

## Tests and unchanged scientific results
- `PYTHONPATH=src python -m unittest discover -s tests -v`: 27/27 PASS.
- Local *real raw* RI 2024: 1,233 events, 3,568 hours; A/B/C/D = 152527.348 / 145905.497 / 146435.058 / 140385.959 lb.
- Local *real raw* Massachusetts 2024 selected four units: 829 events, 1,997 hours; A/B/C/D = 18035.757 / 17305.222 / 17939.975 / 17897.087 lb.
- 2023 frozen reference and scientific policies are not rewritten. The original 2023 raw XML was not reprocessed here.

## Same-science comparator
`compare_flat_workflow.py` is an explicitly **naive** flat-key join, **not** the strongest validated alternative. Synthetic three-hour valid input: both accept 9 lb. Remove the middle CAMPD hour: flat join silently reports 2 lb while v0.2.2 rejects. Set ECMPS hour 1.9: naive integer coercion accepts 9 lb while v0.2.2 rejects. These show practical input-contract behavior, **not** novelty firstness, superior environmental accuracy, or measurable adoption/performance improvements. See `reports/flat_workflow_comparison.json`.

## Remaining pre-submission issues
Figure 3B scientific-value geometry, final EMS references and software-centric manuscript, source/decision manifest, independent broad boundary conditions and publication-ready DOI for a corrected version remain to be reviewed. Do not claim a zero-critical/no-open-issues release or re-label Zenodo v0.2.1.

## Additional pre-release security/lineage iteration

- Verified continuity of observed CAMPD unit-hour ranges; full-year coverage reported **per unit**, never assumed from arbitrary endpoints.
- Raw adapter emits `coverage_manifest.csv` and `stack_map_used.json` (when applicable), in addition to original reports.
- Strict CLI uses an isolated staging directory and `run_manifest.json` with hashes of its analytic outputs and declared input identities.
- Engine rejects existing nonempty outputs and incomplete raw-adapter ledgers; hour-level policy decisions carry source fields when provided.
- F28 checker additionally verifies distinct unit identities and recomputed heat-input/time allocation weights.
- The supported public use path remains CLI; direct programmatic handling of hand-curated event-hour inputs cannot certify their upstream completeness.
- No full-year endpoint guarantee for partial-roster sources, independent human usability study, full ECMPS provenance reconstruction or external source-system portability claim.
