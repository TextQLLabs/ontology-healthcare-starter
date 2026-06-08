# reference/terminology — public grouper crosswalks

The seed tables that turn raw codes into analyzable concepts, loaded into a `terminology`
schema. The `.tql` dimensions/filters/queries join to them. **Only free / public-domain
groupers are loaded here** — certified value sets are license-gated and fetched separately
(`value-sets.md`). See `../../LICENSING.md`.

## Automated loader (do this)
```bash
pip install requests pandas
python load_terminology.py --download          # -> ./_build/*.csv + load.sql
# stage ./_build/*.csv to object storage, run ./_build/load.sql in the warehouse
```

| Table (loader output) | Grouper | Source (free) | Version | Key columns |
|---|---|---|---|---|
| `terminology.ccsr_icd10cm` | CCSR (ICD-10-CM → ~530 categories) | AHRQ HCUP | **v2026.1** | icd10cm_code, description, default_ccsr_ip, default_ccsr_op, ccsr_1..6 |
| `terminology.cmshcc_dx_hcc` | CMS-HCC dx → HCC | CMS | **V28 / PY2026** | icd10cm_code, hcc |
| `terminology.cmshcc_coefficients` | HCC RAF weights (per segment) | CMS | V28 | name, coeff, segment, term, hcc |
| `terminology.cmshcc_hierarchy` | HCC trumping rules | CMS | V28 | superior_hcc, excluded_hcc |
| `terminology.gem_icd9_icd10` | ICD-9 ↔ ICD-10 GEMs | CMS | **2018 final** | icd9_code, icd10_code, flag_* |
| `terminology.ccw_chronic` | CCW chronic (30) | CMS CCW | ICD-10 era | icd10cm_code, chronic_condition *(manual; PDF — see chronic_conditions.md)* |
| `terminology.icd10cm_chapters` | ICD-10 chapter/block ranges | CDC/CMS | annual | range_start, range_end, chapter_name, block_name *(seed CSV in repo)* |

Each table carries a `source_version` column so crosswalk versions are auditable. Codes are
stored **dot-stripped** (`E11.9` → `E119`) to match the `.tql` join expressions.

## What each spec file documents
- `ccsr_categories.md` — CCSR file layout (default vs multi-category), sample rows.
- `hcc_model.md` — the three CMS-HCC files (dx map, coefficients, **hierarchy**) + RAF nuances.
- `chronic_conditions.md` — CCW (the one PDF-parse step) + the 30 conditions.
- `gems.md` — GEMs layout + the 5 positional flags.
- `value-sets.md` / `value-sets.json` — VSAC certified value sets (fetch-with-your-key).

## Why ship the mapping logic, not 70K codes?
The full ICD-10-CM code list comes from the customer's claims data. What we provide is the
small, public, reusable **mapping logic** (chapter ranges + grouper crosswalks). The loader
fetches the authoritative files at install time so versions stay current.
