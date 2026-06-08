# Table: `tuva.condition` (diagnoses)

One row per diagnosis recorded on a claim/encounter. The grain all disease/risk analysis
sits on. Backing for `relations/condition.tql`; resolved via `dimensions/diagnosis.tql`.

| Column | Type | Notes |
|---|---|---|
| `person_id` | varchar | join key → `patient`, `encounter`, `eligibility` |
| `encounter_id` | varchar | links dx to its visit (reason-for-visit) |
| `code` | varchar | diagnosis code; may carry a dot (`E11.9`) — dot-strip before matching |
| `code_type` | varchar | `icd-10-cm` (post-2015) \| `icd-9-cm` (legacy) |
| `dx_rank` | int | `1` = principal/reason-for-visit; `>1` = secondary/comorbidity |
| `present_on_admission` | char | `Y`/`N`/`U`/`W` — comorbidity vs complication (inpatient) |
| `recorded_date` | date | date dx recorded; used for measurement-year windows |

## Joins
- → `terminology.ccsr_categories` on `REPLACE(code,'.','') = icd10cm_code` (CCSR)
- → `terminology.hcc_categories` (HCC/RAF), `terminology.ccw_chronic` (chronic)
- → `terminology.icd9_to_icd10_gem` when `code_type='icd-9-cm'`

## Gotchas
- ~213K rows in the demo — never `SELECT *`; filter by `code_type='icd-10-cm'` + grouper.
- A member appears many times — use `DISTINCT person_id` for prevalence cohorts.
- Don't guess codes — go through the grouper crosswalks (`notes/diagnosis-coding.md`).
