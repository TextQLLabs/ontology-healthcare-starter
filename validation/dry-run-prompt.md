# Dry-run validation prompt (reusable, per warehouse)

The one thing that turns this ontology from *model-accurate* into *runs-on-your-data*:
confirm the real table/column names, key code values, and join keys, then re-point
`ontology/schema.tql` to match. Run this once per connector when you first attach a
warehouse — it is Step 0 of `MIGRATION.md`.

**How to use:** paste the prompt below into a TextQL/Ana thread with the warehouse connector
set. Replace `<SCHEMA>` with the schema name and adjust the table list to what step 1 returns.
Then paste the output back to your FDE (or into `validation/golden-queries.md`).

---

## Prompt to paste into Ana

```
Run each query against the <SCHEMA> connector and paste the raw result rows as text
(no charts, no report — just the rows).

0) Data horizon (sets analysis_end_date in ontology/schema.tql):
   SELECT MAX(claim_end_date) FROM <SCHEMA>.<main_claims_table>;   -- adapt the column

1) Tables present:
   SELECT table_name FROM information_schema.tables
   WHERE table_schema='<SCHEMA>' ORDER BY 1;

2) Column inventory for the core entities (adapt names to step 1's output):
   SELECT table_name, column_name, data_type
   FROM information_schema.columns
   WHERE table_schema='<SCHEMA>'
     AND table_name IN ('patient','member','eligibility','member_months','medical_claim',
                        'claim_header','claim_line','pharmacy_claim','medication',
                        'encounter','condition','diagnosis','procedure','lab_result')
   ORDER BY table_name, ordinal_position;

3) Encounter setting values (readmission/utilization surfaces hard-code these):
   SELECT DISTINCT encounter_type FROM <SCHEMA>.encounter;

4) Diagnosis coding system + volume (confirms ICD-10 vs ICD-9 era + the type spelling):
   SELECT <code_type_column>, COUNT(*) AS n
   FROM <SCHEMA>.<diagnosis_table> GROUP BY 1 ORDER BY n DESC;

5) Cost column population (which numerator to trust):
   SELECT COUNT(*) AS rows,
          COUNT(charge_amount)  AS has_charge,
          COUNT(paid_amount)    AS has_paid,
          COUNT(allowed_amount) AS has_allowed
   FROM <SCHEMA>.<main_claims_table>;

6) Denominator grain exists (PMPM / per-member rates):
   SELECT (SELECT COUNT(*) FROM <SCHEMA>.member_months) AS member_month_rows,
          (SELECT COUNT(*) FROM <SCHEMA>.eligibility)   AS eligibility_rows;

7) Member-key reachability + overlap from the main claims table
   (see ontology/notes/join-key-verification.md):
   SELECT
     (SELECT COUNT(DISTINCT <member_key>) FROM <SCHEMA>.<main_claims_table>) AS claim_members,
     (SELECT COUNT(DISTINCT <member_key>) FROM <SCHEMA>.eligibility)         AS enrolled_members,
     (SELECT COUNT(DISTINCT mc.<member_key>)
      FROM <SCHEMA>.<main_claims_table> mc
      JOIN <SCHEMA>.eligibility e ON e.<member_key> = mc.<member_key>)       AS joined_members;

8) Record-version flags — which tables have one (filter per table, never globally):
   SELECT table_name, column_name FROM information_schema.columns
   WHERE table_schema='<SCHEMA>'
     AND column_name IN ('curr_rcd_ind','is_current','active_flag','current_flag');
```

### Reference instance (Redshift `dev.tuva`)
`<SCHEMA>` = `tuva`, horizon = `2018-12-31`. There: no `patient`/`pharmacy_claim` tables
(person grain derives from `eligibility`; pharmacy is `medication`); codes are in
`normalized_code`/`normalized_code_type`; rank is `condition_rank`; POA is
`present_on_admit_code`. Expect YOUR answers to differ — that's what this dry run is for.

---

## What each query verifies (and what to fix)

| Q | Confirms | If it differs → fix |
|---|---|---|
| 0 | the analysis horizon | set `analysis_end_date` in `ontology/schema.tql` |
| 1 | which core tables exist under this schema | re-point backings in `ontology/schema.tql`; if claims are header/line/event, read `notes/claim-grain.md` first |
| 2 | real column names on the core entities | update column refs in `relations/*.tql`, `dimensions/*.tql`, affected `queries/*.tql` |
| 3 | `encounter_type` literal values | adjust the literals in `readmission_rate.tql`, `utilization_per_1000.tql`, `relations/encounter.tql` |
| 4 | code-type spelling + ICD-10 vs ICD-9 share | if pre-2015 ICD-9 present, enable the GEMs join (`notes/diagnosis-coding.md`); fix the `'icd-10-cm'` literal |
| 5 | which cost column is populated | set the numerator default in `cost_pmpm.tql` / `notes/cost-definition.md` |
| 6 | the PMPM denominator grain exists | if `member_months` is absent, derive prorated months from `eligibility` only |
| 7 | the member key is reachable + overlap rate | if < ~95%, investigate before publishing per-member rates; if no shared key, find the bridge table (`notes/join-key-verification.md`) |
| 8 | which tables carry a current-record flag | apply the filter on exactly those tables (`notes/claim-grain.md`) |

## After the dry run
1. Apply the fixes above as a small PR (table renames → `schema.tql` only).
2. **Run the validator — required:** `python3 validation/validate_tql.py` (static), then
   `--check-sql` pasted into Ana, or `--dsn ... --explain` for a live compile test of every
   surface. Iterate until clean.
3. Re-run the governed surfaces and record results in `validation/golden-queries.md`
   (flip each row's Status from `unverified` → `verified`, fill the Expected value).
4. Assert the invariants in that file (rates ∈ [0,1]; all-cause ≥ CMS readmission; etc.).
