# GEMs — ICD-9 ↔ ICD-10 General Equivalence Mappings

**Source (free):** CMS General Equivalence Mappings (final 2018). Public.
**Why:** Claims with `service_date < 2015-10-01` use **ICD-9-CM**; everything after uses
**ICD-10-CM**. To analyze across the cutover (trends spanning 2015), translate ICD-9 → ICD-10
before applying any ICD-10 grouper. Used in `dimensions/diagnosis.tql` ICD-9 handling.

## Table: `terminology.icd9_to_icd10_gem`
| column | type | notes |
|---|---|---|
| `icd9_code` | varchar | dot-stripped |
| `icd10_code` | varchar | dot-stripped target |
| `flags` | varchar | GEM approximate/combination/scenario/choice flags |

> ⚠️ GEMs are **not 1:1**. Many ICD-9 codes map to several ICD-10 codes (and vice versa),
> and "approximate" flags mean the mapping is lossy. For trend analysis, prefer rolling up
> both eras to a **stable grouper** (CCSR/CCW) rather than code-to-code. Document the
> approach in `notes/diagnosis-coding.md`. The Tuva demo data is post-2015 (ICD-10 only),
> so GEMs is dormant there but wired for customers with historical claims.

## Sample rows
```
icd9_code,icd10_code,flags
25000,E119,approximate
4019,I10,exact
42831,I5022,approximate
49121,J449,approximate
5859,N189,approximate
```
