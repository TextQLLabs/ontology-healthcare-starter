# Golden queries — pinned values & drift alerts

Each governed metric gets a **golden query**: a fixed call with a known-correct result,
pinned to the demo data (current date 2018-12-31). Re-run on any schema/crosswalk change;
**alert on drift**.

> **Status (2026-06-08).** Schema validated on live `dev.tuva`; `.tql` realigned to real columns.
> Golden run executed for the seed-free surfaces (values pinned below). Two findings from the run:
> 1. **Prorated PMPM was buggy** (counted only the first month of each span → 13× undercount).
>    Fixed in `cost_pmpm.tql`; **Q1 must be re-run.**
> 2. **`charge_amount` is inflated** (fullmonth PMPM ≈ $13.3k). `cost_pmpm` now takes a `cost`
>    param (charge/allowed/paid/total) — confirm which is populated and set the default.
> **Q6/Q7 are blocked** because the `terminology` schema can't be loaded on this connector
> (no write access — see note at bottom).

| # | Surface | Call (params) | Expected | Status |
|---|---|---|---|---|
| 1 | `cost_pmpm` | `basis="prorated"`, `cost="charge"` | **re-run** (was $174,824 under the buggy formula) | ⚠️ re-run after fix |
| 2 | `cost_pmpm` | `basis="fullmonth"`, `cost="charge"` | total $414,031,139.38 · member_months 31,184 · **PMPM $13,277.04** | ✅ verified (charge basis) |
| 3 | `readmission_rate` | `definition="cms"` | index 434 · readmits 53 · **rate 0.1221** | ✅ verified |
| 4 | `readmission_rate` | `definition="all_cause"` | **= Q3 (0.1221)** until transfer exclusion lands | ✅ verified (= Q3 by design) |
| 5 | `condition_prevalence` | `grouper="value_set"`, `concept="diabetes"` | 446 / 1,000 · **prevalence 0.4460** | ✅ verified |
| 6 | `condition_prevalence` | `grouper="ccsr"`, `concept="END003"` | default-CCSR **297 / 1,000 = 0.2970** (any-position 302 = 0.302) | ✅ verified (federated join) |
| 7 | `comorbidity_profile` | `level="population"`, segment CNA, CY2018 | **mean RAF 0.680** (all 1,000 enrolled); 0.757 dx'd; 1.030 HCC-positive. 287 pairs trumped | ✅ verified (federated join) |
| 8 | `utilization_per_1000` | `metric="inpatient_admits"` | events 434 · member_months 31,184 · **167.01 / 1,000** | ✅ verified |
| 9 | `rx_adherence_pdc` | `rxnorm_codes=[…]` | — | ▶ ready to run (columns confirmed; surface updated) |
| 10 | `hedis_measure` | HbA1c, diabetics 18–75 | — | ▶ ready to run (columns confirmed; surface updated) |

> Cross-check ✓: Q8 inpatient `events` (434) equals Q3 `index_admissions` (434) — same population,
> two surfaces agree.
>
> **Q5 vs Q6 are not contradictory** — they measure different scopes of "diabetes":
> Q5 `value_set("diabetes")` = ALL diabetes (ICD-10 E08–E13) → **446 members (0.446)**;
> Q6 CCSR `END003` = the diabetes-with-complication CCSR category → **297 members (0.297)**.
> The value-set is the broad cohort; the CCSR category is a clinical subset. Confirm `END003`'s
> exact label in `ccsr_icd10cm.csv` (description col) when reporting, and name the scope used.
>
> **Q7 caveats confirmed against `notes/risk-adjustment-hcc.md`:** the 0.680 is the **dx-driven HCC
> portion only** (demographic/age-sex terms excluded — a documented hook); V28 weights applied to
> 2018 (V24-era) claims is intentional for the demo; hierarchy trumping IS applied (287 pairs removed).

## Invariants (re-assert after the prorated fix)
- `condition_prevalence.prevalence_rate` ∈ [0, 1] — 0.446 ✅
- `readmission_rate` ∈ [0, 1] — 0.1221 ✅
- `readmission(all_cause) >= readmission(cms)` — equal (✅, transfer exclusion pending)
- `cost_pmpm` prorated ≥ fullmonth (prorated denominator is smaller) — **re-check after the fix**
  (the old buggy prorated denom 2,368 made PMPM 13× too high; corrected denom should land just
  below 31,184, so prorated PMPM should be slightly *above* fullmonth — modestly, not 13×).
- `member_raf >= 0` — pending Q7.

## Confirmed column mappings (from the run)
- `medication`: `dispensing_date` (date), `days_supply` (**VARCHAR → CAST**), `rxnorm_code` (no rxcui/ndc).
- `lab_result`: `normalized_component_code` (LOINC), `result_datetime` (timestamp), `result` (VARCHAR).
- `medical_claim`: `charge/paid/allowed/total_cost_amount` all present (confirm population for the cost default).

## ✅ Terminology "blocker" — SOLVED (federated join, zero warehouse writes)
The Redshift connector is read-only and we can't create a `terminology` schema — and we no
longer need to. **Test B confirmed** (2026-06-09) Ana joins the repo crosswalk CSVs to the
warehouse data **in its Python sandbox**, keeping the warehouse strictly read-only. See
`ontology/notes/terminology-join-pattern.md`. To run Q6/Q7 this way:
1. `python reference/terminology/load_terminology.py --download` (fetches CCSR/CMS-HCC public files).
2. **Commit the resulting CSVs** into `reference/terminology/` (public domain — see `LICENSING.md`):
   `ccsr_icd10cm.csv` for Q6; `cmshcc_dx_hcc.csv` + `cmshcc_coefficients.csv` + `cmshcc_hierarchy.csv` for Q7.
3. Ask Ana to run the grouper surface — it loads the CSV + joins in Python.
An in-warehouse table (`load.sql`) is now **optional** — only if the customer wants the crosswalk
materialized for BI tools. The seed-free value-set path (Q5, 27 conditions) needs none of this.

## Remaining steps
**7 of 10 verified** (Q2–Q8). Q6/Q7 done via the federated join (terminology CSVs in repo). Left:
1. Re-run **Q1** (prorated, fixed formula) → pin.
2. Confirm cost-column population → set the `cost` default in `cost_pmpm.tql` / `notes/cost-definition.md`.
3. Run **Q9, Q10** (surfaces updated; columns confirmed) → pin.
