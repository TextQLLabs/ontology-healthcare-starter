# Dry-run validation prompt (reusable, per customer)

The one thing that turns this ontology from *model-accurate* into *runs-on-your-data*:
confirm the real table/column names and key code values, then fix `ontology/schema.tql`
backings to match. Run this once per connector when you first attach a customer's warehouse.

**How to use:** paste the prompt below into a TextQL/Ana thread with the customer's connector
set. Replace `tuva` with the customer's schema and adjust the table list to theirs. Treat the
analysis "current date" as the last date in their data. Then paste the output back to your FDE
(or into `validation/golden-queries.md`).

---

## Prompt to paste into Ana

```
Run each query against the <SCHEMA> connector and paste the raw result rows as text
(no charts, no report — just the rows). Treat the current date as <LAST_DATE_IN_DATA>.

1) Tables present:
   SELECT table_name FROM information_schema.tables
   WHERE table_schema='<SCHEMA>' ORDER BY 1;

2) Column inventory for the core entities:
   SELECT table_name, column_name, data_type
   FROM information_schema.columns
   WHERE table_schema='<SCHEMA>'
     AND table_name IN ('patient','eligibility','member_months','medical_claim',
                        'pharmacy_claim','encounter','condition','procedure')
   ORDER BY table_name, ordinal_position;

3) Encounter setting values (readmission/utilization surfaces hard-code these):
   SELECT DISTINCT encounter_type FROM <SCHEMA>.encounter;

4) Diagnosis coding system + volume (confirms ICD-10 vs ICD-9 era):
   SELECT code_type, COUNT(*) AS n FROM <SCHEMA>.condition GROUP BY code_type ORDER BY n DESC;

5) Cost column population (which numerator to trust):
   SELECT
     COUNT(*) AS rows,
     COUNT(charge_amount)  AS has_charge,
     COUNT(paid_amount)    AS has_paid,
     COUNT(allowed_amount) AS has_allowed
   FROM <SCHEMA>.medical_claim;

6) Denominator grain exists (PMPM / per-member rates):
   SELECT (SELECT COUNT(*) FROM <SCHEMA>.member_months) AS member_month_rows,
          (SELECT COUNT(*) FROM <SCHEMA>.eligibility)   AS eligibility_rows;
```

### Tuva demo instance (Redshift `dev.tuva`)
`<SCHEMA>` = `tuva`, `<LAST_DATE_IN_DATA>` = `2018-12-31`.

---

## What each query verifies (and what to fix)

| Q | Confirms | If it differs → fix |
|---|---|---|
| 1 | the 8 core tables exist under this schema | rename/repoint backings in `ontology/schema.tql` |
| 2 | real column names — esp. `condition`: `code`, `code_type`, `dx_rank`, `present_on_admission`, `recorded_date`; `encounter`: `encounter_type`, `encounter_start_date`/`encounter_end_date`, `length_of_stay`, `drg_code` | update the column refs in `relations/*.tql`, `dimensions/diagnosis.tql`, and the affected `queries/*.tql` |
| 3 | `encounter_type` literal values | adjust the hard-coded `'acute inpatient'` / `'emergency department'` in `readmission_rate.tql`, `utilization_per_1000.tql`, `dimensions/diagnosis.tql` |
| 4 | `code_type` spelling + ICD-10 vs ICD-9 share | if pre-2015 ICD-9 present, enable the GEMs join (`notes/diagnosis-coding.md`); fix the `'icd-10-cm'` literal |
| 5 | which cost column is populated | set the numerator in `cost_pmpm.tql` / `notes/cost-definition.md` (charge vs allowed vs paid) |
| 6 | the PMPM denominator grain exists | if `member_months` is absent, derive prorated months from `eligibility` only |

## After the dry run
1. Apply the column/name fixes above as a small PR.
2. Re-run the governed surfaces and record results in `validation/golden-queries.md`
   (flip each row's Status from `unverified` → `verified`, fill the Expected value).
3. Assert the invariants in that file (rates ∈ [0,1]; all-cause ≥ CMS readmission; etc.).
