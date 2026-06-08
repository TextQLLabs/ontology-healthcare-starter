# CCSR — Clinical Classifications Software Refined

**Source (free):** AHRQ HCUP — Clinical Classifications Software Refined for ICD-10-CM.
**Provenance:** AHRQ CCSR v2025-1 (refresh annually). Public domain.
**Why:** Collapses ~70K ICD-10-CM diagnosis codes into ~530 clinically meaningful
categories. **The default grouper** for "what condition" questions (`dimensions/diagnosis.tql`
`ccsr_category`, `filters/diagnosis.tql` `in_ccsr`).

## Table: `terminology.ccsr_categories`
The `.tql` joins on the dot-stripped ICD-10-CM code.

| column | type | notes |
|---|---|---|
| `icd10cm_code` | varchar | dot-stripped, e.g. `E119` |
| `ccsr_category` | varchar | category code, e.g. `END002` |
| `ccsr_description` | varchar | e.g. `Diabetes mellitus with complication` |

> Note: AHRQ's file maps each ICD-10-CM code to up to 6 CCSR categories (for non-principal
> dx) plus a default principal-dx category. For the starter, load the **default
> categorization** (one row per code). For reason-for-visit analysis, use the principal
> mapping; document the choice in `notes/diagnosis-coding.md`.

## Sample rows (illustrative — load the full AHRQ file for production)
```
icd10cm_code,ccsr_category,ccsr_description
E119,END003,Diabetes mellitus without complication
E1122,END002,Diabetes mellitus with complication
I10,CIR007,Essential hypertension
I509,CIR019,Heart failure
J449,RSP008,Chronic obstructive pulmonary disease and bronchiectasis
N183,GEN003,Chronic kidney disease
F329,MBD002,Depressive disorders
```
