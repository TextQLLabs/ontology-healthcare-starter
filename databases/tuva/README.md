# Database: `tuva` (clinical + claims) — VERIFIED 2026-06-08

Default connector. Real Tuva output model on **Redshift** (`dev.tuva`). Join key **`person_id`**.
Schema confirmed live; the notes below reflect what's actually there (not assumptions).

## Operating rules
- **Current date = 2018-12-31** (last date in the data).
- **Pull `information_schema` first**; no `SELECT *` on big fact tables.

## Tables present (20)
`condition`, `eligibility`, `encounter`, `medical_claim`, `member_months`, `procedure`,
`medication`, `lab_result`, `immunization`, `appointment`, `location`, `practitioner`,
`person_id_crosswalk`, + `_stg_claims_*` staging tables.

## ⚠️ Structural facts that shaped the ontology
- **No `patient` table.** Person demographics come from **`eligibility`** (`birth_date`,
  `fips_state_abbreviation`). Surfaces derive a person grain via a CTE
  (`SELECT person_id, MIN(birth_date), MAX(fips_state_abbreviation) FROM eligibility GROUP BY person_id`).
- **No `pharmacy_claim` table.** Pharmacy data is in **`medication`** (confirm its columns;
  `rx_adherence_pdc.tql` is wired to it but pending column names).
- **`sex` / `race` / `ethnicity` are NOT in the data** — health-equity dimensions are unavailable.
- **Codes are in `normalized_code` / `normalized_code_type`** (Tuva normalizes source codes;
  `source_code` keeps the original). Diagnoses are ~100% `icd-10-cm` (212,864 rows; 147 null).

## Cost columns
`medical_claim` and `encounter` both carry `charge_amount`, `paid_amount`, `allowed_amount`
(+ `total_cost_amount` on `medical_claim`). Confirm which are well-populated (dry-run Q5) and
set the cost numerator accordingly in `notes/cost-definition.md`.

## Encounter types (28 distinct)
Includes `acute inpatient`, `emergency department`, `office visit`, `urgent care`, `telehealth`,
many outpatient subtypes, and `*-orphaned` / `orphaned claim`. The readmission + utilization
surfaces key on `acute inpatient` / `emergency department` (both confirmed present). `encounter`
also has `ed_flag` and `encounter_group` for cleaner rollups.

Per-table detail: `tables/*.md`.
