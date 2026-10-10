# R2 reproducibility — local sources (not redistributed)

From package root with `pip install -e .` and local archives, use **fresh** output paths. Each command fails rather than overwriting a previous run.

```bash
provscreen --raw-bulk /path/emissions-hourly-2024-ri.csv --ecmps /path/Emissions_Export.zip --year 2024 --classifier epa_informed_2024 --outdir /path/run-ri-unique
```

MA requires a CSV scoped **in advance** to ORIS 1594 units 11/12 and ORIS 60903 units 1/2. The broad MA state input is NOT directly passed through as though four-unit sources covered all statewide units.

```bash
provscreen --raw-bulk /path/ma_2024_four_unit_bulk.csv --ecmps /path/MA_2024_pilot_ECMPS.zip --stack-map /path/stack_map.json --year 2024 --classifier epa_informed_2024 --outdir /path/run-ma-unique
```

The stack map is `{"1594|11":"CS2","1594|12":"CS2"}`. This map records inherited stack provenance and is NOT itself an independently validated regulatory allocation engine. See companion Blackstone F28 audit for supplied separate reconciliation.

Expected counts and exact masses are in `reports/R2_REAL_RAW_CHECKS.json`. SHA-256 of source archives and scoped prepared file is in `reports/RAW_SOURCE_SHA256.csv`. Obtain original inputs from official data access sources or researcher source archives; archive contents must be verified against hashes. This lightweight code ZIP does not include EPA raw data.

**Caution**: `--source` is prepared event-hour input; it is not equivalent to raw acquisition. Old 2023 XML/lossless reconstruction is not implemented in this package.
