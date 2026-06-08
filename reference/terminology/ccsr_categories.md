# CCSR — Clinical Classifications Software Refined (ICD-10-CM diagnoses)

**Source (free, public domain):** AHRQ HCUP — `https://hcup-us.ahrq.gov/toolssoftware/ccsr/dxccsr.jsp`
**Provenance:** **CCSR v2026.1** (FY2026; released ~Nov 2025). Released annually on the federal
fiscal year. AHRQ requests citation. Loaded by `load_terminology.py`.
**Why:** Collapses >70K ICD-10-CM codes into ~530 clinically meaningful categories. **The
default grouper** for "what condition" questions (`dimensions/diagnosis.tql`, `condition_prevalence.tql`).

## File: `DXCCSR_v2026-1.csv` → `terminology.ccsr_icd10cm`
One CSV, **75,725 rows**, code fields wrapped in single quotes (the loader strips them).
Two mappings live in one file:
- **Default categorization** = `default_ccsr_ip` / `default_ccsr_op` — a *single* category for
  the principal/first-listed diagnosis (separate inpatient vs outpatient defaults). Use for
  mutually-exclusive ranking.
- **Multi-category** = `ccsr_1`..`ccsr_6` — *all* categories a code maps to. Explode these for
  comorbidity coverage. (Most codes use 1–2; unused slots blank.)

| Loaded column | From | Notes |
|---|---|---|
| `icd10cm_code` | ICD-10-CM CODE | dot-stripped |
| `description` | ICD-10-CM CODE DESCRIPTION | |
| `default_ccsr_ip` / `default_ccsr_op` | Default CCSR CATEGORY IP / OP | category code e.g. `END003` |
| `ccsr_1`..`ccsr_6` | CCSR CATEGORY 1..6 | multi-category |

Category codes = 3-letter body system + 3 digits (e.g. `END003` diabetes, `CIR019` heart failure).

## Sample rows (illustrative)
```
icd10cm_code,description,default_ccsr_ip,default_ccsr_op
E119,Type 2 diabetes mellitus without complications,END003,END003
I509,Heart failure unspecified,CIR019,CIR019
J449,COPD unspecified,RSP008,RSP008
N183,Chronic kidney disease stage 3,GEN003,GEN003
```
