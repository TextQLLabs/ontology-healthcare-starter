# Decision: how we resolve diagnoses (the canonical grouper per question)

**Status:** Adopted · **Owner:** Clinical Analytics + Actuarial · **Surfaces:** `queries/condition_prevalence.tql`, `comorbidity_profile.tql` · **Dimensions:** `dimensions/diagnosis.tql` · **Filters:** `filters/diagnosis.tql`

## Principle
**Never analyze raw ICD codes.** ~70K ICD-10-CM codes are meaningless as a filter. Every
clinical-concept question resolves through one of three groupers. Which one is **not** a
free choice — it depends on the question:

| Question is about… | Canonical grouper | Why |
|---|---|---|
| "What condition / disease category" (general analytics) | **CCSR** (AHRQ) | ~530 clinically coherent buckets; the analytics default |
| "Risk / RAF / expected cost" | **CMS-HCC** | payment-relevant; carries RAF weights |
| "Chronic-disease cohort / care management" | **CCW chronic (27)** | standard chronic flags |
| "A specific reportable measure" (HEDIS/Stars) | **the measure's VSAC value set** | regulatory; nothing else is defensible |
| Ad-hoc exploration ("just E11") | **ICD-10 prefix** (`filters` `has_icd10_prefix`) | fast, but label it exploratory |

Default when unspecified = **CCSR**.

## ICD-10-CM hierarchy (the rollup)
`E11.9 → E11 (category) → E08–E13 (block) → Chapter 4 (E00–E89)`. The 3-char category is a
pure string op (`LEFT(REPLACE(code,'.',''),3)`); chapter/block come from
`reference/terminology/icd10cm_chapters.csv`. The shipped chapter map is **chapter-level**
(one representative block per chapter) — load AHRQ/CMS block detail for finer rollups.

## Primary vs. secondary diagnosis
`dx_rank = 1` = principal/reason-for-visit; `> 1` = comorbidity. Use **primary-only** for
"why did members present"; **any-position** for disease burden/risk. `comorbidity_profile`
uses any-position (HCCs accrue from any qualifying dx). State the choice in every answer.

## Present on admission (POA)
For inpatient, POA distinguishes a **comorbidity** (present at admit) from a **complication**
(developed during stay). Matters for quality/safety measures — don't count complications as
pre-existing burden.

## ICD-9 → ICD-10 cutover (2015-10-01)
Claims before the cutover are **ICD-9-CM** (`code_type='icd-9-cm'`). For cross-cutover trends,
**don't map code-to-code** (GEMs are lossy/many-to-many) — roll both eras up to a stable
grouper (CCSR/CCW) and compare at that level. Tuva demo data is post-2015 (ICD-10 only).

## Value sets are governed
The named value sets in `filters/diagnosis.tql` (`diabetes`, `chf`, …) are **starter**
definitions for demo/exploration. For any reported number, replace with the authoritative
VSAC/HEDIS value set and cite version + date here. A value-set change is a reviewed PR, not
a silent edit.
