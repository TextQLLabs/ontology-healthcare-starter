# Table: `tuva.encounter` (visits)

One row per encounter. Backing for `relations/encounter.tql`. Drives utilization,
readmission, length-of-stay, ED analysis.

| Column | Type | Notes |
|---|---|---|
| `person_id` | varchar | join key |
| `encounter_id` | varchar | PK |
| `encounter_type` | varchar | `acute inpatient` \| `outpatient` \| `emergency department` \| `office visit` |
| `encounter_start_date` | date | admit / visit date |
| `encounter_end_date` | date | discharge date (used for readmission window) |
| `length_of_stay` | int | inpatient days (bed-days metric) |
| `charge_amount` | decimal | encounter charge |
| `drg_code` | varchar | MS-DRG (inpatient payment grouper) |

## Gotchas
- Readmission = next `acute inpatient` admit for same `person_id` within `>0 and <=30` days
  of discharge (`readmission_rate.tql`).
- ~rows are large — filter by `encounter_type` early; no `SELECT *`.
