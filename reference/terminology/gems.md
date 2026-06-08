# GEMs — ICD-9 ↔ ICD-10 General Equivalence Mappings

**Source (free, public domain):** CMS GEM archive —
`https://www.cms.gov/medicare/coding-billing/icd-10-codes/icd-10-cm-icd-10-pcs-gem-archive`
Diagnosis zip: `https://www.cms.gov/medicare/coding/icd10/downloads/2018-icd-10-cm-general-equivalence-mappings.zip`
**Provenance:** **2018 is the final, frozen version** — GEMs were not updated after FY2018, by design.
**Why:** Claims with `service_date < 2015-10-01` use **ICD-9-CM**; later use **ICD-10-CM**. To
analyze across the cutover, translate before applying any ICD-10 grouper. Loaded by `load_terminology.py`.

## Table: `terminology.gem_icd9_icd10`
From `2018_I9gem.txt` (space-delimited). Columns:
| column | notes |
|---|---|
| `icd9_code` | dot-stripped source |
| `icd10_code` | dot-stripped target (`NoDx` sentinel when no map) |
| `flags` | 5 positional digits |
| `flag_approximate` / `flag_nomap` / `flag_combination` / `flag_scenario` / `flag_choice` | split from `flags` |

The 5 flags: **approximate** (mapping is not exact), **no-map** (no valid target), **combination**
(source needs multiple targets together), **scenario** (combination grouping), **choice list**
(alternatives within a scenario).

## ⚠️ Use carefully
GEMs are **not 1:1** — many-to-many and lossy ("approximate"). For trend analysis spanning the
cutover, **don't map code-to-code**; roll both eras up to a **stable grouper** (CCSR/CCW) and
compare there. The Tuva demo data is post-2015 (ICD-10 only), so this is dormant there but wired
for customers with historical claims. See `notes/diagnosis-coding.md`.

## Sample rows
```
icd9_code,icd10_code,flag_approximate
25000,E119,1
4019,I10,0
49121,J449,1
5859,N189,1
```
