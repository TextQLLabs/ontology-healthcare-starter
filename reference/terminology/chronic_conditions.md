# CCW Chronic Conditions

**Source (free):** CMS Chronic Conditions Warehouse (CCW) — 27 chronic condition algorithms.
**Provenance:** CCW condition reference. Public.
**Why:** Standard chronic-disease flags for population-health and care-management cohorts
(`dimensions/diagnosis.tql` `chronic_condition`/`is_chronic`, `filters/diagnosis.tql` `is_chronic`).

## Table: `terminology.ccw_chronic`
| column | type | notes |
|---|---|---|
| `icd10cm_code` | varchar | dot-stripped |
| `chronic_condition` | varchar | CCW condition name, e.g. `Diabetes` |

> ⚠️ CCW's *official* definitions also require a **claims/lookback rule** (e.g. ≥1
> inpatient or ≥2 outpatient claims within a window). The starter ships the **code → condition**
> map for cohorting; for the certified flag, apply the claims-count rule in the surface and
> document it in `notes/diagnosis-coding.md`.

## The 27 conditions (CCW)
Acute Myocardial Infarction · Alzheimer's & Related Dementia · Anemia · Asthma ·
Atrial Fibrillation · Benign Prostatic Hyperplasia · Cancer (Breast, Colorectal, Lung,
Prostate, Endometrial) · Chronic Kidney Disease · COPD · Depression · Diabetes ·
Heart Failure · Hip/Pelvic Fracture · Hyperlipidemia · Hypertension · Ischemic Heart
Disease · Osteoporosis · Rheumatoid Arthritis/Osteoarthritis · Stroke/TIA · Glaucoma ·
Cataract · Chronic Hepatitis · HIV/AIDS.

## Sample rows
```
icd10cm_code,chronic_condition
E119,Diabetes
E1122,Diabetes
I10,Hypertension
I509,Heart Failure
J449,COPD
N183,Chronic Kidney Disease
F329,Depression
```
