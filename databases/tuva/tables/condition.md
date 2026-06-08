# Table: `tuva.condition` (diagnoses) — VERIFIED 2026-06-08 (23 cols)

One row per diagnosis. The grain all disease/risk analysis sits on. Backing for
`relations/condition.tql`; resolved via `dimensions/diagnosis.tql`.

| Column | Type | Notes |
|---|---|---|
| `person_id` | varchar | join key |
| `encounter_id` | varchar | links dx to its visit |
| `claim_id` | varchar | |
| `normalized_code` | varchar | **the diagnosis code (ICD-10-CM)** — use this; may carry a dot |
| `normalized_code_type` | varchar | `icd-10-cm` (212,864 rows; 147 null) |
| `source_code` / `source_code_type` | varchar | original pre-normalization coding |
| `condition_rank` | int | `1` = primary/principal; `>1` = secondary |
| `present_on_admit_code` | varchar | `Y`/`N`/`U`/`W` — comorbidity vs complication |
| `recorded_date` | date | measurement-year windows |
| `onset_date`, `resolved_date`, `status`, `condition_type`, `mapping_method` | | |

## Joins
- → `terminology.ccsr_icd10cm` / `cmshcc_dx_hcc` / `ccw_chronic` on
  `REPLACE(normalized_code,'.','') = icd10cm_code`.

## Gotchas
- ~213K rows — never `SELECT *`; filter `normalized_code_type='icd-10-cm'` + a grouper.
- Use `DISTINCT person_id` for prevalence cohorts.
- **Was assumed `code`/`code_type`/`dx_rank`/`present_on_admission` — real names differ (above).**
