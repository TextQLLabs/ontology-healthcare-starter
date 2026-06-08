# Golden queries — pinned values & drift alerts

Each governed metric gets a **golden query**: a fixed call with a known-correct result,
pinned to the demo data (current date 2018-12-31). Re-run on any schema/crosswalk change;
**alert on drift**. Fill the "expected" column once verified against the live connector.

> **Schema validation — DONE (2026-06-08), via Ana on live `dev.tuva`.** The `.tql` was
> realigned to the real columns. Key corrections applied:
> - **No `patient` table** → person grain derived from `eligibility` (`birth_date`,
>   `fips_state_abbreviation`); `sex`/`race`/`ethnicity` unavailable in this data.
> - **No `pharmacy_claim`** → `medication` table (columns still TBD — `rx_adherence_pdc.tql` pending).
> - **condition/procedure codes** = `normalized_code` / `normalized_code_type`;
>   rank = `condition_rank`; POA = `present_on_admit_code`.
> - `encounter_type` includes `acute inpatient` + `emergency department` (surfaces valid);
>   conditions ~100% `icd-10-cm` (GEMs dormant).
> Remaining to verify: `medication` columns, `lab_result` columns, cost-column population.

| # | Surface | Call (params) | Expected | Status |
|---|---|---|---|---|
| 1 | `cost_pmpm` | `basis="prorated"`, all states | TBD | columns OK; run |
| 2 | `cost_pmpm` | `basis="fullmonth"` | TBD | columns OK; run |
| 3 | `readmission_rate` | `definition="cms"` | TBD | columns OK; run |
| 4 | `readmission_rate` | `definition="all_cause"` (≥ #3) | TBD | columns OK; run |
| 5 | `condition_prevalence` | `grouper="value_set"`, `concept="diabetes"` | TBD | needs terminology load |
| 6 | `condition_prevalence` | `grouper="ccsr"`, `concept="END003"` | TBD | needs terminology load |
| 7 | `comorbidity_profile` | `level="population"`, CY2018 | TBD | needs CMS-HCC load |
| 8 | `utilization_per_1000` | `metric="inpatient_admits"` | TBD | columns OK; run |
| 9 | `rx_adherence_pdc` | `drug_class="antidiabetics"` | TBD | **blocked: confirm `medication` columns** |
| 10 | `hedis_measure` | HbA1c, age 18–75, CY2018 | TBD | **confirm `lab_result` columns** |

## Invariants to assert (true regardless of exact value)
- `condition_prevalence.prevalence_rate` ∈ [0, 1].
- `readmission(all_cause) >= readmission(cms)` (all-cause is a superset).
- `cost_pmpm` prorated denominator ≤ fullmonth → prorated PMPM ≥ fullmonth PMPM.
- Every externally-reported count cell ≥ 11 (else suppressed) — `governance-phi.md`.
- `member_raf >= 0` for all members.

## Remaining dry-run steps
1. Load terminology seeds (`reference/terminology/load_terminology.py`) → enables #5–#7.
2. Confirm `medication` + `lab_result` columns → unblocks #9, #10.
3. Confirm cost-column population (charge vs allowed vs total_cost) → set `cost-definition.md`.
4. Run #1–#10; record Expected; flip Status → verified; assert the invariants.
