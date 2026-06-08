# CCW Chronic Conditions

**Source (free, public domain):** CMS Chronic Conditions Warehouse —
`https://www2.ccwdata.org/web/guest/condition-categories-chronic/`
**Provenance:** **30 CCW Chronic Conditions**, ICD-10-only algorithms for file years 2017+
(2020 expert-panel refresh; adds 3 vs. the legacy 27). Updated periodically for annual code changes.
**Why:** Standard chronic-disease flags for population-health and care-management cohorts
(`dimensions/diagnosis.tql` `chronic_condition`/`is_chronic`, `filters/diagnosis.tql` `is_chronic`).

## Table: `terminology.ccw_chronic`
| column | type | notes |
|---|---|---|
| `icd10cm_code` | varchar | dot-stripped |
| `chronic_condition` | varchar | CCW condition name, e.g. `Diabetes` |

## ⚠️ The one manual step
CMS publishes these **as a PDF only** (`chr-chronic-condition-algorithms.pdf`) — there is **no
clean CSV**. So `load_terminology.py` does **not** auto-build this table. Extract the code lists
from the PDF (e.g. `pdfplumber` / `camelot` table extraction) into
`(icd10cm_code, chronic_condition)` rows, then load. The PDF also encodes look-back periods and
qualifying-claim rules per condition — apply those in the surface if you need the *certified*
flag (e.g. ≥1 inpatient or ≥2 outpatient claims in the window); the code→condition map alone is
enough for exploratory cohorting.

## The 30 conditions
AMI · Alzheimer's & Related Dementia · Anemia · Asthma · Atrial Fibrillation/Flutter · BPH ·
Cancer (Breast, Colorectal, Lung, Prostate, Endometrial) · CKD · COPD · Depression/Bipolar ·
Diabetes · Heart Failure · Hip/Pelvic Fracture · Hyperlipidemia · Hypertension · Ischemic Heart
Disease · Osteoporosis · RA/OA · Stroke/TIA · Glaucoma · Cataract · Chronic Hepatitis ·
HIV/AIDS · Acquired Hypothyroidism · Pressure/Chronic Ulcers · (and related panel additions).

## Sample rows
```
icd10cm_code,chronic_condition
E119,Diabetes
I10,Hypertension
I509,Heart Failure
J449,COPD
N183,Chronic Kidney Disease
```
