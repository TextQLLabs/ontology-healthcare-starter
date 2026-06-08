# Certified value sets (VSAC) — fetch, don't bundle

For **reportable** measures (HEDIS/Stars/eCQM) the cohort must be defined by the
**authoritative, certified value set**, not the starter ICD-10 prefix definitions in
`../../ontology/filters/diagnosis.tql`. Those certified sets live in **VSAC** (NLM's Value
Set Authority Center).

## The licensing reality (why we fetch instead of commit)
VSAC value sets embed codes from licensed vocabularies (SNOMED CT, CPT, LOINC, ICD-10-CM,
RxNorm) and are governed by the **UMLS Metathesaurus License**. They **may not be
redistributed** as standalone files. So:

- ✅ **We commit OIDs + version pins** (`value-sets.json`). Identifiers are not the restricted asset.
- ✅ **Each customer hydrates the codes** in their own environment with their own **free UMLS
  API key** via `fetch_vsac.py` (VSAC FHIR `$expand`).
- ❌ We never commit the expanded code lists.

This is the standard vendor pattern (mirrors `cqframework/cql-exec-vsac`). Bonus: fetching
auto-picks-up the annual value-set updates.

## HEDIS is separate (and paid)
HEDIS value sets are **not in VSAC** — NCQA distributes them as the **Value Set Directory
(VSD)** under a **paid HEDIS license**. Do not bundle NCQA content. Where a measure has both
a free **CMS eCQM** version and a HEDIS version, prefer the eCQM value sets so the baseline
ontology carries **no NCQA-license dependency** (e.g. use eCQM `CMS122` HbA1c-poor-control
rather than the HEDIS GSD product). If the customer holds a HEDIS license, import their VSD
Excel through a parallel step.

## How to hydrate
```bash
pip install requests
export UMLS_API_KEY=...            # free: https://uts.nlm.nih.gov -> My Profile -> API key
python fetch_vsac.py               # expands every OID in value-sets.json
# -> _build/value_set_members.csv  -> load into terminology.value_set_members
```
Then a governed surface can resolve a measure cohort by OID:
```sql
JOIN terminology.value_set_members vsm
  ON vsm.value_set_oid = '2.16.840.1.113883.3.464.1003.103.12.1001'   -- Diabetes dx
 AND vsm.code_system_name = 'ICD-10-CM'
 AND vsm.code = REPLACE(c.code, '.', '')
```

## Registry
See `value-sets.json`. Verify each OID + version at <https://vsac.nlm.nih.gov> before relying
on it — value sets are versioned annually and some concepts (notably diabetes ICD-10-CM) have
**multiple overlapping value sets**, so pin the OID *and* the version your numbers depend on.

| Concept | OID | Code systems |
|---|---|---|
| Diabetes (diagnosis) | `2.16.840.1.113883.3.464.1003.103.12.1001` | ICD-10-CM, SNOMED |
| HbA1c Laboratory Test | `2.16.840.1.113883.3.464.1003.198.12.1013` | LOINC |

## Sources
- VSAC FHIR API — https://www.nlm.nih.gov/vsac/support/usingvsac/vsacfhirapi.html
- UMLS Metathesaurus License — https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/license_agreement.html
- eCQM value-set downloads — https://vsac.nlm.nih.gov/download/ecqm
- eCQI Resource Center (measure specs) — https://ecqi.healthit.gov
