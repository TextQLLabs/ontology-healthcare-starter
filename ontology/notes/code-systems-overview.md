# Code systems — what's used where

A map of the standardized vocabularies this ontology touches, which fact they live on, and
their licensing. Licensing detail + shipping rules: `../../LICENSING.md`.

| System | Lives on | Used for | License |
|---|---|---|---|
| **ICD-10-CM** | `condition` | diagnoses, prevalence, HCC/CCSR/chronic groupers | Public |
| **ICD-9-CM** | `condition` (pre-2015-10-01) | legacy dx; GEMs to ICD-10 | Public |
| **ICD-10-PCS** | `procedure` | inpatient procedures | Public |
| **HCPCS Level II** | `procedure` | drugs/supplies/DME; J-codes = Part B drugs | Public |
| **CPT** | `procedure` | professional procedures, HEDIS numerators | ❌ AMA-licensed — structural only |
| **NDC** | `pharmacy_claim` | dispensed drug product | Public (FDA) |
| **RxNorm / RxCUI** | `pharmacy_claim` | normalized drug → therapeutic class | Public (NLM) |
| **LOINC** | `lab_result` / `observation` | lab tests, HEDIS lab numerators | ⚠️ free w/ license — structural |
| **SNOMED CT** | clinical (EHR-sourced) | clinical findings/problems | ⚠️ UMLS license — structural |
| **MS-DRG** | `encounter.drg_code` | inpatient payment grouping | Public |
| **APC / HCPCS** | outpatient claims | outpatient payment grouping | Public |
| **NUCC taxonomy** | `practitioner` | provider specialty rollup | Public |
| **FIPS** | geography | state/county joins, socioeconomic | Public |

## Groupers (derived, public) — the analytic layer
| Grouper | From | For | File |
|---|---|---|---|
| **CCSR** | ICD-10-CM | ~530 clinical categories (default) | `reference/terminology/ccsr_categories.md` |
| **CMS-HCC** | ICD-10-CM | risk / RAF | `reference/terminology/hcc_model.md` |
| **CCW chronic (27)** | ICD-10-CM | chronic cohorts | `reference/terminology/chronic_conditions.md` |
| **GEMs** | ICD-9↔10 | cutover bridging | `reference/terminology/gems.md` |

## Per-customer additions
When a customer brings a licensed system (CPT/SNOMED/LOINC) or a proprietary class system
(Medi-Span, First Databank, ATC), note it here with **license + effective date**, keep the
data in **their** warehouse, and join by code only.
