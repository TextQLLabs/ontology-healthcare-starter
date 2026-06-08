# Table: `tuva.encounter` (visits) — VERIFIED 2026-06-08 (43 cols)

One row per encounter. Backing for `relations/encounter.tql`. Drives utilization, readmission,
length-of-stay, ED. All assumed columns confirmed present.

| Column | Type | Notes |
|---|---|---|
| `person_id` | varchar | join key |
| `encounter_id` | varchar | PK |
| `encounter_type` | varchar | 28 values; `acute inpatient` / `emergency department` confirmed |
| `encounter_group` | varchar | coarser rollup of encounter_type |
| `encounter_start_date` / `encounter_end_date` | date | admit / discharge (readmission window) |
| `length_of_stay` | int | inpatient bed-days |
| `drg_code` / `drg_code_type` / `drg_description` | varchar | MS-DRG |
| `charge_amount` / `paid_amount` / `allowed_amount` | numeric | cost (all present) |
| `ed_flag` | int | cleaner ED indicator than encounter_type alone |
| `primary_diagnosis_code` / `_type` | varchar | encounter principal dx |
| `discharge_disposition_code` / `admit_source_code` | varchar | (transfer detection for CMS readmission) |
| `claim_count` / `inst_claim_count` / `prof_claim_count` | int | |

## Gotchas
- Readmission = next `acute inpatient` admit, same `person_id`, `>0 and <=30` days after
  discharge (`readmission_rate.tql`). `discharge_disposition_code` enables the transfer
  exclusion for the CMS variant (a noted follow-up).
- Large table — filter by `encounter_type` early; no `SELECT *`.
