# How to apply this overlay to the starter repo

These files are the **round-2 hardening + schema-validation upgrades** for
`ontology-healthcare-starter`. They were staged here (in the writable session root) because a
sandbox file-lock blocked this session from editing the repo in place — your normal shell is
**not** affected.

## What's in this overlay
```
GETTING_STARTED.md                              NEW — payer step-by-step walkthrough
README.md                                       UPDATED — points to GETTING_STARTED + loader
LICENSING.md                                    UPDATED — VSAC "fetch, don't bundle" stance
ontology/schema.tql                             UPDATED+VERIFIED — real Tuva backings (no patient/pharmacy_claim)
ontology/relations/condition.tql                VERIFIED — normalized_code / condition_rank / present_on_admit_code
ontology/relations/procedure.tql                VERIFIED — normalized_code / normalized_code_type
ontology/relations/person.tql                   NEW — person grain derived from eligibility (no patient table)
ontology/dimensions/diagnosis.tql               VERIFIED — joins on normalized_code; rank/POA fixed
ontology/dimensions/patient.tql                 VERIFIED — birth_date/state from eligibility; sex/race/ethnicity unavailable
ontology/dimensions/procedure.tql               VERIFIED — normalized_code
ontology/queries/comorbidity_profile.tql        HARDENED+VERIFIED — HCC hierarchy + segment coeffs, real columns
ontology/queries/condition_prevalence.tql       VERIFIED — person CTE + normalized_code joins
ontology/queries/cost_pmpm.tql                  VERIFIED — person CTE for state filter
ontology/queries/utilization_per_1000.tql       VERIFIED — person CTE; encounter_type values confirmed
ontology/queries/hedis_measure.tql              UPDATED — person CTE + normalized_code (lab_result cols TBD)
ontology/queries/rx_adherence_pdc.tql           ⚠️ PENDING — retargeted to `medication`; confirm its columns
reference/terminology/load_terminology.py       NEW — downloads CCSR/CMS-HCC/GEMs -> CSV + load.sql
reference/terminology/fetch_vsac.py             NEW — hydrates VSAC value sets with a UMLS key
reference/terminology/value-sets.json           NEW — OID registry (commit OIDs, not codes)
reference/terminology/value-sets.md             NEW — VSAC fetch/licensing guide
reference/terminology/README.md                 UPDATED — loader-driven table index
reference/terminology/ccsr_categories.md        UPDATED — v2026.1 file layout
reference/terminology/hcc_model.md              UPDATED — 3 files incl. the hierarchy
reference/terminology/chronic_conditions.md     UPDATED — CCW 30 + the PDF-parse step
reference/terminology/gems.md                   UPDATED — 2018 layout + flags + table name
databases/tuva/README.md                        VERIFIED — real table list + structural facts
databases/tuva/tables/condition.md              VERIFIED — 23 real columns
databases/tuva/tables/encounter.md              VERIFIED — 43 real columns
validation/golden-queries.md                    UPDATED — schema validation done; remaining steps
validation/dry-run-prompt.md                    NEW — reusable per-customer schema-validation prompt
```
> `readmission_rate.tql` is unchanged — it uses only `encounter` columns, all confirmed valid.
> `ontology/relations/{patient,encounter,eligibility,medical_claim,pharmacy_claim}.tql` from
> round 1 are superseded by `relations/{person,condition,procedure}.tql` here; after applying,
> delete the stale `relations/patient.tql` and `relations/pharmacy_claim.tql` (renamed/removed).

## Apply (run in your normal terminal — not sandboxed)
```bash
cd "/Users/jacob/Desktop/TextQL/Cigna Workshop"
rsync -a _hcls-starter-updates/ ../ontology-healthcare-starter/
cd ../ontology-healthcare-starter
# remove the two relations superseded by the live-schema reality:
git rm -f ontology/relations/patient.tql ontology/relations/pharmacy_claim.tql 2>/dev/null
git add -A && git status            # review the diff
git commit -m "Round 2: terminology loader, hardened RAF, VSAC fetch, GETTING_STARTED + live-schema validation"
```

## Two open items (one more Ana query each)
```sql
-- (a) unblock rx_adherence_pdc.tql:
SELECT column_name, data_type FROM information_schema.columns
WHERE table_schema='tuva' AND table_name='medication' ORDER BY ordinal_position;
-- (b) confirm HEDIS numerator + cost numerator:
SELECT column_name, data_type FROM information_schema.columns
WHERE table_schema='tuva' AND table_name='lab_result' ORDER BY ordinal_position;
SELECT COUNT(*) rows, COUNT(charge_amount) chg, COUNT(paid_amount) paid,
       COUNT(allowed_amount) alwd, COUNT(total_cost_amount) tot FROM tuva.medical_claim;
```
Paste results back and the last two surfaces get finalized.
