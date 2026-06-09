# reference/terminology — public grouper crosswalks

The seed tables that turn raw codes into analyzable concepts, loaded into a `terminology`
schema. The `.tql` dimensions/filters/queries join to them. **Only free / public-domain
groupers are loaded here** — certified value sets are license-gated and fetched separately
(`value-sets.md`). See `../../LICENSING.md`.

## Two ways to use these crosswalks

**Path 1 — Federated join in Ana (recommended; ZERO warehouse writes).** The crosswalk CSV lives
in this repo; Ana loads it into its Python sandbox and joins it to a read-only warehouse pull
in-memory. Nothing is written to the customer's database. This is the default — verified working
(212,864 conditions classified, zero writes). See `../../ontology/notes/terminology-join-pattern.md`.
To enable CCSR/CMS-HCC on this path, **commit their CSVs into this folder** (build them once with
the loader below; they're public domain — see `../../LICENSING.md`).

**Path 2 — Materialize in the warehouse (optional).** Only if the customer wants the crosswalk as
a real table (e.g. for BI tools). Requires write access.

## Build the crosswalk CSVs (loader)
```bash
pip install requests pandas
python load_terminology.py --download          # -> ./_build/*.csv (+ load.sql for Path 2)
# Path 1: commit ./_build/*.csv into reference/terminology/  (Ana federates the join)
# Path 2: stage ./_build/*.csv to object storage, run ./_build/load.sql in the warehouse
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
