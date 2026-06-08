# CMS-HCC — Hierarchical Condition Categories (risk adjustment)

**Source (free):** CMS — CMS-HCC risk-adjustment model (diagnosis → HCC crosswalk + coefficients).
**Provenance:** CMS-HCC model V28 (payment year 2024+). State the model version on load —
weights change by version and payment year. Public.
**Why:** The payer money grouper. Maps ICD-10-CM diagnoses to ~115 condition categories,
each with a **RAF weight**. Summing a member's HCC weights (+ demographic factors) yields
the **Risk Adjustment Factor (RAF)** that drives risk-adjusted payment.
(`dimensions/diagnosis.tql` `hcc_category`/`raf_weight`, `queries/comorbidity_profile.tql`.)

## Table: `terminology.hcc_categories`
| column | type | notes |
|---|---|---|
| `icd10cm_code` | varchar | dot-stripped |
| `hcc` | varchar | HCC id, e.g. `HCC38` |
| `hcc_description` | varchar | e.g. `Diabetes with chronic complications` |
| `raf_weight` | decimal | community-nondual aged weight (the common default) |

> ⚠️ RAF nuances to document, not hide: (1) **hierarchies** — within a disease group only
> the most severe HCC counts (don't sum both diabetes-with and diabetes-without). (2) Weights
> differ by **enrollee segment** (community/institutional, dual status, age/disability).
> The starter ships the community-nondual-aged weight; expose others as a param if needed.
> (3) HCCs require a qualifying dx in the **measurement year** — apply a date filter.

## Sample rows (illustrative — load CMS model file for production)
```
icd10cm_code,hcc,hcc_description,raf_weight
E1122,HCC37,Diabetes with chronic complications,0.166
E119,HCC38,Diabetes without complication,0.105
I509,HCC226,Heart failure,0.331
N183,HCC329,Chronic kidney disease stage 3,0.127
J449,HCC280,COPD,0.331
```
