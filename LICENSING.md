# Code-System Licensing — what's safe to ship

This starter is meant to be **branched across customers and shared**. That is only safe if we
are careful about which standardized vocabularies we **bundle code lists for** vs. only **model
structurally** vs. **fetch with the customer's own license**. "Model structurally" = the
relation/dimension/column and joins exist, but no proprietary code list is committed.

| Code system | Domain | License | In this starter |
|---|---|---|---|
| **ICD-10-CM** | Diagnoses (~70K, hierarchical) | Public domain | ✅ Chapter ranges shipped; full list via customer data |
| **ICD-10-PCS** | Inpatient procedures | Public domain | ✅ Structure |
| **ICD-9-CM + GEMs** | Legacy + crosswalk | Public domain | ✅ GEMs 2018 loaded by `load_terminology.py` |
| **HCPCS Level II** | Drugs/supplies/DME | Public domain | ✅ |
| **NDC** | Drug products | Public (FDA) | ✅ |
| **RxNorm / RxCUI** | Normalized drugs | Public (NLM) | ✅ |
| **MS-DRG / APC** | Payment groups | Public (CMS) | ✅ |
| **CCSR** | ICD-10 → ~530 categories | Public (AHRQ) | ✅ Loaded (v2026.1) |
| **CMS-HCC** | Risk/RAF + hierarchy | Public (CMS) | ✅ Loaded (V28, dx map + coeffs + hierarchy) |
| **CCW Chronic** | 30 chronic flags | Public (CMS) | ✅ Loaded (one PDF-parse step) |
| **CPT / CPT-4** | Professional procedures | ❌ **AMA-licensed** | ⚙️ Structure only — never commit CPT lists |
| **SNOMED CT** | Clinical terminology | ⚠️ Free via UMLS license | ⚙️ Structure only |
| **LOINC** | Labs/observations | ⚠️ Free w/ Regenstrief license | ⚙️ Structure only |
| **VSAC value sets** | Certified measure code lists | ⚠️ **UMLS Metathesaurus License** | 🔑 **Fetch, don't bundle** (see below) |
| **HEDIS value sets** | NCQA quality measures | ❌ **Paid NCQA license** | ⚙️ Customer-imported only |

## The three rules

1. **Public-domain groupers (CCSR, CMS-HCC, CCW, GEMs)** — safe to load and use. The
   `load_terminology.py` script fetches the authoritative files; keep a `source_version` on each.

2. **VSAC certified value sets — fetch with the customer's own UMLS key, never commit codes.**
   VSAC value sets embed SNOMED/CPT/LOINC/ICD-10-CM/RxNorm and are governed by the UMLS
   Metathesaurus License, which prohibits redistributing subsets. So we commit **OIDs + version
   pins only** (`reference/terminology/value-sets.json`) and each customer hydrates the codes in
   their own environment with their own free UMLS API key via `fetch_vsac.py`. This is the
   clearly-compliant vendor pattern. (Confirm the boundary with NLM/UMLS for any commercial
   redistribution scenario; CPT carries separate AMA terms.)

3. **HEDIS (NCQA) — never bundle.** Requires a paid NCQA license; the customer loads their own
   Value Set Directory. Prefer free **CMS eCQM** value sets (in VSAC) where a measure has both,
   so the baseline ontology has no NCQA dependency.

## When a customer branch adds a licensed system
Note the license + effective date in `ontology/notes/code-systems-overview.md`, keep the data
in **their** warehouse, and join by code only. Never commit CPT/SNOMED/LOINC or NCQA content here.
