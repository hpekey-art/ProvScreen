# ProvScreen v0.2.3 — LOCAL DEVELOPMENT CANDIDATE ONLY

This is NOT a published release. DO NOT replace the DOI for publicly archived v0.2.2 (10.5281/zenodo.23287169).
Typed unit-vs-stack identity and the pandas timestamp-fixture repair have been tested locally.

Release-gate verification on 2026-10-11:

- A v0.2.3 wheel built successfully from the corrected candidate.
- The wheel and all declared dependencies installed into a new environment that did not expose system site-packages (Python 3.12.14, pandas 3.0.6, NumPy 2.5.4).
- Package metadata, `provscreen.__version__`, installed module origin, dependency checks, and CLI entry point agreed with v0.2.3.
- All 39 tests passed against the installed wheel, including negative typed-lineage cases.
- Prepared-input RI 2024 and four-unit MA 2024 CLI runs exactly reproduced the declared counts and Policy A–D masses.
- A local MA 2024 four-unit raw-adapter rerun from the installed wheel reproduced 829 events, 1,997 event-hours, and all four declared masses. Its source files are verification inputs and are not redistributed in the lightweight release candidate.

Still NOT VERIFIED: a fresh RI 2024 raw-source rerun (required raw inputs were not supplied to this gate); original RI 2023 raw EPA XML reconstruction; independent external-user execution of v0.2.3; Windows installation of v0.2.3; comprehensive support for other EPA schemas or regulatory systems; physical-emissions accuracy; and independent unit-level measurement at Blackstone.

The frozen RI 2023 science and derived reference results remain unchanged. Public release remains on HOLD until an immutable GitHub v0.2.3 tag and a provider-confirmed, version-specific Zenodo DOI exist. Manuscript synchronization must follow, not precede, that evidence.
