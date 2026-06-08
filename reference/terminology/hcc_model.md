# CMS-HCC — Hierarchical Condition Categories (risk adjustment)

**Source (free, public domain):** CMS — CMS-HCC risk-adjustment model.
**Provenance:** **Model V28, Payment Year 2026** (Midyear/Final). V28 is 100% phased in for
PY2026; the V24 blend is gone. State the model version on every load — weights and the
dx→HCC map change by version and payment year.
**Why:** The payer money grouper. Maps ICD-10-CM diagnoses to ~115 condition categories,
each with a RAF weight. A member's RAF (HCC weights + demographic + interaction factors)
drives risk-adjusted payment. Used by `queries/comorbidity_profile.tql`.

## Download (handled by load_terminology.py)
- ICD-10 mappings zip: `https://www.cms.gov/files/zip/2026-midyear-final-icd-10-mappings.zip`
- Model software zip (coefficients + hierarchy): `https://www.cms.gov/files/zip/2026-midyear-final-model-software.zip`
- Landing: cms.gov → Risk Adjustment → "2026 Model Software/ICD-10 Mappings" (needs a browser UA).

## The THREE files (all loaded; this is what makes the RAF surface production-grade)

**(i) `terminology.cmshcc_dx_hcc`** — dx → HCC. From `2026 Final ICD-10-CM Mappings.csv`
(filter to the V28 column) or the SAS-package `F2826T1N.TXT` (tab-delimited code→CC).
Columns: `icd10cm_code`, `hcc`.

**(ii) `terminology.cmshcc_coefficients`** — RAF weights. From `C2824T2N.csv` (`Name,Coeff,Label`,
~1,237 rows). The loader splits the segment prefix: `CNA_HCC68` → `segment=CNA`, `term=HCC68`,
`hcc=68`. Segments: CNA/CND/CFA/CFD/CPA/CPD (community combos of dual/aged/disabled) + INS
(institutional). Demographic and disease-interaction terms are in the same file (null `hcc`).

**(iii) `terminology.cmshcc_hierarchy`** — the **trumping** logic. Parsed from the SAS macro
`V28115H1.TXT` (`%SET0(CC=35, HIER=%STR(36,37,38))` → rows `(superior_hcc=35, excluded_hcc=36/37/38)`).
Within a disease group, the most severe HCC zeroes out the lower ones. **This is applied in
`comorbidity_profile.tql`** — the #1 thing that separates a real RAF from an over-count.

## RAF nuances (documented, not hidden)
- **Hierarchies** — applied via the hierarchy table (e.g. diabetes-with-complication trumps without).
- **Segment** — weights differ by community/institutional + dual + aged/disabled; the surface
  exposes a `segment` param (default `CNA`).
- **Measurement year** — HCCs require a qualifying dx in the year; the surface filters on `recorded_date`.
- **Demographic + interaction factors** — part of the official RAF; the starter surface computes
  the **dx-driven HCC portion**, with a documented hook to add demographic terms from the same
  coefficient table. Note this when reporting an absolute RAF.

## Sample (illustrative — loader fetches the real files)
```
cmshcc_dx_hcc:     E1122 -> 37   ;  I509 -> 226   ;  N183 -> 329
cmshcc_coeff:      CNA_HCC37, 0.318, "Diabetes with chronic complications"
cmshcc_hierarchy:  superior 35 -> excluded 36,37,38
```
