# Code-System Licensing — what's safe to ship

This starter is meant to be **branched across customers and shared**. That is only safe if
we are careful about which standardized vocabularies we **bundle code lists for** vs. only
**model structurally**. "Model structurally" = the relation/dimension/column and the joins
exist, but no proprietary code list is committed; the customer's own licensed copy populates
it at their warehouse.

| Code system | Domain | License | In this starter |
|---|---|---|---|
| **ICD-10-CM** | Diagnoses (~70K, hierarchical) | Public domain (CMS/CDC/WHO-US) | ✅ Chapter/block ranges shipped; full code list via customer data |
| **ICD-10-PCS** | Inpatient procedures (~78K) | Public domain (CMS) | ✅ Structure + section map |
| **ICD-9-CM + GEMs** | Legacy dx/proc + crosswalk | Public domain (CMS) | ✅ GEMs crosswalk modeled |
| **HCPCS Level II** | Drugs/supplies/DME (J-codes) | Public domain (CMS) | ✅ |
| **NDC** | Drug products | Public (FDA) | ✅ |
| **RxNorm / RxCUI** | Normalized drug names | Public (NLM) | ✅ (already in Part D data) |
| **MS-DRG / APC** | Inpatient/outpatient payment groups | Public (CMS) | ✅ |
| **CCSR** | ICD-10 → ~530 clinical categories | Public (AHRQ) | ✅ Grouper modeled; AHRQ file referenced |
| **HCC** | Risk-adjustment categories (RAF) | Public (CMS) | ✅ Model spec + crosswalk |
| **CCW Chronic Conditions** | 27 chronic flags | Public (CMS/CCW) | ✅ |
| **Elixhauser / Charlson** | Comorbidity indices | Public (AHRQ / academic) | ⚙️ Structure only (add if needed) |
| **CPT / CPT-4** | Professional procedures | ❌ **AMA-licensed** | ⚙️ Structure only — **never commit CPT code lists** |
| **SNOMED CT** | Clinical terminology | ⚠️ Free in US via NLM/UMLS license | ⚙️ Structure only — gate behind customer's UMLS license |
| **LOINC** | Labs/observations | ⚠️ Free with Regenstrief license | ⚙️ Structure only |

## Rules
- **Do not commit CPT, SNOMED, or LOINC code/description lists to this repo.** Reference them
  by code in joins to the customer's licensed tables only.
- Public groupers (CCSR, HCC, CCW chronic, GEMs) **may** be committed as seed crosswalks —
  see `reference/terminology/`. Keep the provenance line (source + version/year) on each.
- When a customer branch adds a licensed system, note the license + effective date in
  `ontology/notes/code-systems-overview.md` and keep the data in **their** warehouse.
