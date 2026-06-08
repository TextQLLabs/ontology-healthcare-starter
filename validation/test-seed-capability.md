# Test: can terminology stay in the ontology with ZERO warehouse writes?

**Goal:** join a repo CSV (e.g. `reference/terminology/icd10cm_chapters.csv`) to the customer's
warehouse tables **without creating any persistent object in their database.** Standing up the
ontology should require *read-only* access — no CREATE, no load, no schema change.

Run these four tests in Ana, best-first, against the Tuva (or customer) connector. Each says
what it proves and how to read the result. Stop at the first one that works cleanly.

---

## Test A — Native seed / virtual table (the ideal)
Does TextQL let you register a repo CSV as a queryable table that federates against the warehouse?

> **Ask Ana:** *"The ontology repo has `reference/terminology/icd10cm_chapters.csv` (columns:
> range_start, range_end, chapter_num, chapter_name, block_code, block_name). Can you register
> or attach that CSV as a queryable 'seed' table I can JOIN against `tuva.condition` — without
> writing anything to the warehouse? If yes, do it, then run: count conditions per ICD-10
> chapter by joining each diagnosis's 3-char category to the chapter ranges."*

- ✅ **Works** → this is the answer. Terminology lives in the repo; Ana federates the join. Even
  the big crosswalks (CCSR 75k) can stay in git. Document the mechanism and we're done.
- ❌ **"I can't attach a CSV as a table"** → go to Test B.

## Test B — Federated join in Python (no warehouse write; very likely works)
Ana pulls a small slice from the warehouse, loads the CSV from the repo, joins in pandas.

> **Ask Ana:** *"Without writing anything to the warehouse: (1) query `tuva.condition` for the
> count of conditions per 3-char ICD-10 category — `SELECT LEFT(REPLACE(normalized_code,'.',''),3)
> AS cat, COUNT(*) AS n FROM tuva.condition WHERE normalized_code_type='icd-10-cm' GROUP BY 1`.
> (2) Load `reference/terminology/icd10cm_chapters.csv` from the repo. (3) In Python, map each
> category to its chapter (cat BETWEEN range_start AND range_end) and return total conditions per
> chapter."*

- ✅ **Works** → the dependable fallback for ANY size crosswalk (pull only the distinct codes —
  a few thousand rows max — never raw PHI in bulk). Confirms grouper analytics with zero writes.
- This is the pattern to standardize on if Test A isn't supported.

## Test C — Session TEMP table (ephemeral, not a persistent change)
Many read-only roles still allow session-scoped temp tables (dropped at disconnect).

> **Ask Ana to run:**
```sql
CREATE TEMP TABLE _vs_probe (icd10cm_code VARCHAR, category VARCHAR);
INSERT INTO _vs_probe VALUES ('E119','END003'), ('I10','CIR007');
SELECT c.person_id, v.category
FROM tuva.condition c
JOIN _vs_probe v ON v.icd10cm_code = REPLACE(c.normalized_code,'.','')
LIMIT 5;
```
- ✅ **Succeeds** → Ana can stage small crosswalks per-session (no persistent object). Good for
  medium crosswalks. ⚠️ Confirm with the customer that **temp tables are acceptable** (they're
  ephemeral, but they are technically a write to the session temp schema).
- ❌ **"permission denied for CREATE"** → temp not allowed; rely on A or B.

## Test D — Inline VALUES / CTE (pure read; baseline, always works for small sets)
No object at all — the mapping is embedded in the query text. (This is how the value sets already
work.) Proves the zero-write path end-to-end; only limited by query size (~small crosswalks).

> **Ask Ana to run:**
```sql
WITH vs (icd10cm_code, category) AS (
  VALUES ('E119','diabetes'), ('E1122','diabetes'), ('I509','chf')
)
SELECT vs.category, COUNT(DISTINCT c.person_id) AS members
FROM tuva.condition c
JOIN vs ON vs.icd10cm_code = REPLACE(c.normalized_code,'.','')
GROUP BY vs.category;
```
- ✅ **Works** (it should — Q5 already proved inline ranges run). Good for value sets + the small
  crosswalks (HCC hierarchy ~70 rows, chronic flags). Not for full CCSR (75k → query too large).

---

## How to read the results → what we standardize on

| Outcome | Decision |
|---|---|
| Test A works | **Best.** All terminology (incl. CCSR/HCC) lives in the repo; Ana federates. Zero writes. |
| A fails, B works | **Standard fallback.** Grouper joins done in Python from repo CSVs; pull only distinct codes. Zero writes, any size. |
| A & B unavailable, C works | Stage small/medium crosswalds in session temp tables (confirm temp is OK with the customer). |
| Only D | Inline value sets + small crosswalks; big crosswalks (full CCSR/HCC) need a one-time managed load. |

**The principle either way:** the customer's warehouse stays **read-only** for setup. Terminology
is part of the ontology (git), not something we ask them to load. The only scenario that forces a
write is full-CCSR/HCC-scale grouping when neither A, B, nor C is available — and even then it's a
managed side-schema, never a change to their existing data.

Paste back which tests pass and I'll wire the surfaces to that mechanism (e.g. switch
`condition_prevalence`/`comorbidity_profile` to the Python-federated or seed-table path).
