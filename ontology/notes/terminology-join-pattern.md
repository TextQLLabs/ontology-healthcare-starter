# Pattern: terminology joins with ZERO warehouse writes (federated in Python)

**Status:** Adopted (verified 2026-06-09) · **Applies to:** every grouper-dependent surface
(`condition_prevalence` CCSR/HCC, `comorbidity_profile`, chapter/block rollups).

## The rule
Standing up this ontology must keep the customer's warehouse **read-only**. Terminology
crosswalks (ICD-10 chapters, CCSR, CMS-HCC, CCW chronic, GEMs) **live in the ontology repo**
(`reference/terminology/*.csv`) — not in their database. When a surface needs to group codes,
Ana **joins the CSV to the warehouse data in its Python sandbox**, not via an in-warehouse SQL
join. No `CREATE`, no load, no schema change.

## How it works (verified)
1. The crosswalk CSV is in the **context library / connected repo** (e.g. `icd10cm_chapters.csv`).
2. Ana loads it into a pandas DataFrame in the Python sandbox.
3. Ana pulls **only what's needed** from the warehouse with read-only SQL — typically the
   distinct codes + counts (a few thousand rows), never bulk member-level PHI.
4. Ana joins in memory and aggregates.

**Proof (2026-06-09):** chapter rollup of `tuva.condition` — all **212,864** ICD-10-CM rows
mapped to a chapter across **21 chapters**, **zero unclassified**, zero warehouse writes.

## Two join shapes
- **Alphabetic range** (chapters/blocks): the 3-char category `LEFT(REPLACE(code,'.',''),3)` is
  compared against `range_start`/`range_end` (e.g. `A00`–`B99`). Done in pandas with a range
  lookup, not `=`.
- **Equality** (CCSR, CMS-HCC, CCW): dot-stripped `normalized_code` == `icd10cm_code`. A direct
  pandas merge.

## Volume discipline (keep it read-only AND cheap)
- Prefer pulling **distinct codes with counts** (`GROUP BY` the code) and joining those to the
  crosswalk, then weighting by count — instead of pulling every claim row.
- When member-level cohorts are needed (prevalence, RAF), pull `person_id` + code only, join,
  then aggregate. Still no PHI beyond the necessary keys; still zero writes.

## Enabling CCSR / CMS-HCC on this path
These need their public-domain CSVs **in the repo** so Ana can load them:
1. Run `reference/terminology/load_terminology.py --download` once (it fetches + normalizes).
2. Commit the resulting CSVs into `reference/terminology/` (CCSR/CMS-HCC/GEMs are public domain —
   safe to commit; see `../../LICENSING.md`). For CMS-HCC, commit `cmshcc_dx_hcc.csv`,
   `cmshcc_coefficients.csv`, `cmshcc_hierarchy.csv`.
3. Ana then runs `comorbidity_profile` / CCSR prevalence via the same federated join — no
   terminology DB, no warehouse write.

## When to use an in-warehouse table instead
Only if the customer *wants* the crosswalk materialized (e.g. for BI tools hitting the warehouse
directly, or very large repeated joins). Then `load_terminology.py` + `load.sql` apply. The
`.tql` surfaces are written as in-warehouse SQL joins to `terminology.*` for that case; when the
tables aren't present, Ana satisfies the same logical join via this federated pattern. Either way
the **governed definition is identical** — only the execution venue differs.
