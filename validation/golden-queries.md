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
| 6 | `condition_prevalence` | `grouper="ccsr"`, `concept="END003"` | — | ⛔ blocked: no `terminology` schema |
| 7 | `comorbidity_profile` | `level="population"`, CY2018 | — | ⛔ blocked: no CMS-HCC seeds |
| 8 | `utilization_per_1000` | `metric="inpatient_admits"` | events 434 · member_months 31,184 · **167.01 / 1,000** | ✅ verified |
| 9 | `rx_adherence_pdc` | `rxnorm_codes=[…]` | — | ▶ ready to run (columns confirmed; surface updated) |
| 10 | `hedis_measure` | HbA1c, diabetics 18–75 | — | ▶ ready to run (columns confirmed; surface updated) |

> Cross-check ✓: Q8 inpatient `events` (434) equals Q3 `index_admissions` (434) — same population,
> two surfaces agree.

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

## ⛔ Terminology-load blocker (Q6, Q7, and class-based Q9)
The Redshift connector is **read-only for us** — we can't create the `terminology` schema, and a
new database would have to be provisioned. Until there's a writable terminology store, the
**grouper-dependent surfaces stay unavailable**: CCSR prevalence (Q6), CMS-HCC/RAF (Q7), and
class-based PDC. Options, fastest first:
1. **A writable schema on the same Redshift cluster** (even a side `terminology` DB) → cross-database
   joins work; run `load_terminology.py` → `load.sql` there. *(Recommended.)*
2. **Load the seeds into any warehouse you do control** and point those surfaces at it.
3. **Stay seed-free for now:** the value-set path (Q5) already covers common conditions via inline
   ICD-10 ranges — extend `filters/diagnosis.tql` for more conditions without any terminology tables.
The seed-free surfaces (cost, readmission, prevalence-by-value-set, utilization) need none of this.

## Remaining steps
1. Re-run **Q1** (prorated, fixed) → pin.
2. Confirm cost-column population → set `cost` default in `cost_pmpm.tql` / `notes/cost-definition.md`.
3. Run **Q9, Q10** (surfaces updated) → pin.
4. Resolve the terminology store → run **Q6, Q7** → pin.
