# v0.2.3 typed provenance repair gate

- Both source identity fields populated: reject (no precedence rule).
- Raw source dictionary uses (facility, source-kind, source-id, clock) keys.
- Unmapped stack with coincident unit label: reject missing typed unit source, not direct.
- Explicit stack map even when labels coincide: inherited lineage.
- Referencing a unit-kind source as a stack: explicit reject.
- Noncontiguous timestamp fixture assignment avoids pandas 3 string-dtype coercion.
- New separate six-case typed reference checker: 6/6 agreement; does not prove superior performance or external portability.
- Corrected v0.2.3 wheel installed with declared dependencies in a fresh environment without system site-packages (Python 3.12.14, pandas 3.0.6, NumPy 2.5.4).
- Installed-wheel gate: 39/39 tests passed; the six-case typed reference checker agreed 6/6; prepared RI 2024 and four-unit MA 2024 regressions reproduced exact declared counts and Policy A–D masses.
- Four-unit MA 2024 raw-adapter rerun passed from the installed wheel. Blackstone shared-stack provenance remains inherited through an explicit CS2 link and must not be described as independent unit-level measurement.
- Fresh RI 2024 raw-source rerun was not possible because its unbundled raw inputs were absent. Original RI 2023 raw XML reconstruction, third-party execution, Windows v0.2.3 installation, and broader regulatory portability remain unverified.
- The source candidate originally contained a large MA raw-source working directory despite documentation stating that raw inputs were not redistributed. The corrected lightweight candidate excludes it; hashes and bounded source identities remain documented.
- No EMS manuscript Word file, public v0.2.3 tag, or provider-confirmed v0.2.3 DOI was supplied to this gate. Manuscript synchronization and rendered-page QA therefore remain on HOLD.
- All policy rules, 2023 science and reference numerical data unchanged.
