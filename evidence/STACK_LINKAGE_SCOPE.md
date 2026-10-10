# Blackstone CS2 inherited provenance — claim boundary

The supplied 2024 Monitoring Plan and reconciliation evidence link Blackstone units 11/12 to the common CS2 stack. A stack measurement is not an independently measured unit NOXR value. The two-unit mass reconciliation is checked using source NOX rate × CS2 Operating Time × heat-input/time-based F-28 allocation weights.

The `verify_f28.py` checker now verifies pair identity (11,12), declared active-unit counts, F-28 weight reconstruction from unit heat-input rate and unit Operating Time, algebraic predictions and mass residuals (0.001 lb/unit-hour tolerance). Missing heat-input rate on an inactive unit is not treated as active missing data. 7,120 precompiled unit-hour rows are verified. This does not independently re-extract Monitoring Plan topology, establish legal applicability or prove physical-emissions accuracy. The explicit stack_map is an author-supplied configuration, not an automated regulatory approval.
