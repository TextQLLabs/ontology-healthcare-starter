# Golden queries — pinned values & drift alerts

Each governed metric gets a **golden query**: a fixed call with a known-correct result,
pinned to the demo data (current date 2018-12-31). Re-run on any schema/crosswalk change;
**alert on drift**. Fill the "expected" column once verified against the live connector on
the first dry run — leave `TBD` until then (don't invent numbers).

| # | Surface | Call (params) | Expected | Status |
|---|---|---|---|---|
| 1 | `cost_pmpm` | `basis="prorated"`, all states | TBD | unverified |
| 2 | `cost_pmpm` | `basis="fullmonth"` | TBD | unverified |
| 3 | `readmission_rate` | `definition="cms"` | TBD | unverified |
| 4 | `readmission_rate` | `definition="all_cause"` (≥ #3) | TBD | unverified |
| 5 | `condition_prevalence` | `grouper="value_set"`, `concept="diabetes"` | TBD | unverified |
| 6 | `condition_prevalence` | `grouper="ccsr"`, `concept="END003"` | TBD | unverified |
| 7 | `comorbidity_profile` | `level="population"`, CY2018 | TBD | unverified |
| 8 | `utilization_per_1000` | `metric="inpatient_admits"` | TBD | unverified |
| 9 | `rx_adherence_pdc` | `drug_class="antidiabetics"`, CY2018 | TBD | unverified |
| 10 | `hedis_measure` | HbA1c testing, age 18–75, CY2018 | TBD | unverified |

## Invariants to assert (true regardless of exact value)
- `condition_prevalence.prevalence_rate` ∈ [0, 1].
- `readmission(all_cause) >= readmission(cms)` (all-cause is a superset).
- `cost_pmpm` with `prorated` ≤ `fullmonth` denominator → prorated PMPM ≥ fullmonth PMPM.
- Every count cell reported externally ≥ 11 (else suppressed) — see `governance-phi.md`.
- `member_raf >= 0` for all members.

## First dry-run checklist
1. Pull `information_schema`; confirm column names vs `databases/tuva/tables/*.md`.
2. Compile each `.tql` against the live compiler; fix dialect/column mismatches.
3. Load the terminology seeds; confirm `schema.tql` backings resolve.
4. Run surfaces 1–10; record results in "Expected"; flip Status → verified.
