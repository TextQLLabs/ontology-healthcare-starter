# Database: `tuva` (clinical + claims)

The default connector this starter is authored against. Tuva clinical+claims model on
**Redshift** (`dev.tuva`). Join key **`person_id`** across all tables.

## Operating rules (data-owner)
- **Treat the current date as 2018-12-31** (last date in the demo data).
- **Pull `information_schema` first** on a new thread before writing SQL.
- **No `SELECT *`** on big fact tables (`encounter`, `condition`, `procedure`).

## Core tables
| Table | Grain | Key columns |
|---|---|---|
| `patient` | 1 / person | person_id, birth_date, sex, race, ethnicity, state |
| `eligibility` | enrollment span | person_id, enrollment_start_date, enrollment_end_date |
| `member_months` | 1 / person / month | person_id, year_month |
| `medical_claim` | claim line | person_id, claim_id, charge_amount, service_date |
| `pharmacy_claim` | fill | person_id, ndc, rxcui, days_supply, fill_date, paid_amount |
| `encounter` | visit | person_id, encounter_id, encounter_type, start/end, length_of_stay, charge_amount, drg_code |
| `condition` | diagnosis | person_id, encounter_id, code, code_type, dx_rank, present_on_admission, recorded_date |
| `procedure` | procedure | person_id, encounter_id, code, code_type, procedure_date |
| `lab_result` | lab | person_id, loinc_code, result, result_date |
| `observation`, `immunization`, `practitioner`, `location`, `appointment` | — | see per-table docs |

## Gotchas
- Use `charge_amount` for cost — `paid_amount`/`allowed_amount` are sparse.
- `encounter_type` ∈ {`acute inpatient`, `outpatient`, `emergency department`, `office visit`}.
- Demo data is **ICD-10 only** (post-2015 cutover); GEMs path is dormant but wired.

> Per-table detail lives in `tables/*.md`. Confirm exact column names on first discovery —
> the starter's `.tql` is written to the Tuva model but column spellings vary by load.
