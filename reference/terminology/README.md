# reference/terminology — public grouper crosswalks

The seed tables that turn raw codes into analyzable concepts. These are loaded into a
`terminology` schema in the warehouse (or attached as connector tables); the `.tql`
dimensions/filters join to them. **Only free / public-domain groupers live here** — see
`../../LICENSING.md`.

Each crosswalk keeps a **provenance line** (source + version/year) so we know what to
refresh. These are *starters* — for regulatory/quality reporting, load the authoritative
full file from the source below and cite it.

| File | Grouper | Source (free) | Refresh |
|---|---|---|---|
| `icd10cm_chapters.csv` | ICD-10-CM chapter & block ranges | CDC NCHS / CMS ICD-10-CM tabular | Annual (Oct 1) |
| `ccsr_categories.md` | CCSR (ICD-10-CM → ~530 categories) | AHRQ HCUP CCSR | Annual |
| `hcc_model.md` | CMS-HCC (ICD-10-CM → HCC + RAF weight) | CMS risk-adjustment model | Annual (model version) |
| `chronic_conditions.md` | CCW 27 chronic conditions | CMS Chronic Conditions Warehouse | Periodic |
| `gems.md` | ICD-9 ↔ ICD-10 GEMs | CMS General Equivalence Mappings | Frozen (2018 final) |

## Loading
1. Download the authoritative file from the source (links above / in each spec file).
2. Load into a `terminology` schema (Redshift) or dataset (BigQuery) with the column
   names the `.tql` joins expect — listed at the top of each spec file.
3. Confirm `schema.tql`'s terminology backings point at your load.

## Why ship these and not the code lists themselves?
The *full* ICD-10-CM code list comes from the customer's claims data (the `condition`
table) — we don't need to bundle 70K codes. What we bundle is the **mapping logic**
(chapter ranges, grouper crosswalks) that is small, public, and reusable. That's the
robust, redistributable core.
