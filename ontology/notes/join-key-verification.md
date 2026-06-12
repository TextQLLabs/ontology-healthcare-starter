# Join-key verification — prove a join before you rely on it

**Status:** Adopted · **Applies to:** every join in every surface, especially after re-pointing

This repo deliberately ships **no asserted linkage facts** ("table A joins table B at 98%
coverage"). Any such number is a property of one dataset — on yours it is fiction until
re-measured. What ships instead is the procedure. Run it once per join when you attach a new
warehouse; record the results in `databases/<yourschema>/README.md`.

## 1. Does the key exist on BOTH sides? (information_schema, free)

```sql
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = '<yourschema>'
  AND column_name IN ('person_id', 'member_id', 'claim_id', 'encounter_id')  -- your candidates
ORDER BY column_name, table_name;
```

Same name on both sides is **necessary, not sufficient** — check `data_type` too (a VARCHAR
member key on one side and BIGINT on the other "joins" with silent casts and silent misses).

⚠️ Two tables sharing a concept may share **no usable key at all.** A claim table and a
claim-event table are both "about claims," yet the event table may key on an internal
adjudication id that appears nowhere on the claim you can see. If step 1 finds no common
column, do not invent a join path — find the documented bridge table or mark the linkage
**unavailable** in the table docs (an honest gap beats a wrong join).

## 2. What's the actual overlap? (one cheap query per join)

```sql
SELECT
  (SELECT COUNT(DISTINCT person_id) FROM <yourschema>.medical_claim) AS keys_left,
  (SELECT COUNT(DISTINCT person_id) FROM <yourschema>.eligibility)   AS keys_right,
  (SELECT COUNT(DISTINCT mc.person_id)
   FROM <yourschema>.medical_claim mc
   JOIN <yourschema>.eligibility e ON e.person_id = mc.person_id)    AS keys_joined;
```

Interpret:
- `keys_joined / keys_left` < ~95% → claims for members you can't see; every per-member rate
  is silently understated. Find out why before publishing a number.
- `keys_joined` ≈ 0 with matching column names → same name, different id space (source-system
  id vs. enterprise id). Common after migrations/M&A. Look for a crosswalk table.

## 3. Is the join 1:1, 1:N, or N:N? (grain check — prevents double counting)

```sql
SELECT COUNT(*) AS rows, COUNT(DISTINCT person_id) AS keys
FROM <yourschema>.eligibility;   -- rows >> keys => span/version grain, NOT person grain
```

If the "dimension" side has multiple rows per key (enrollment spans, record versions), joining
it raw multiplies the fact side. Collapse it first (see `person_grain` in `schema.tql` for the
shipped example) or filter to the current record **where that column exists**
(`notes/claim-grain.md`).

## 4. Record the verdict

Add one line per verified join to `databases/<yourschema>/README.md`:

```
person_id: medical_claim->eligibility verified 2026-06-11, 99.4% of claim members, 1:N (spans) — collapse first
claim_event: NO usable key to medical_claim (internal adjudication id) — linkage unavailable
```

Surfaces may then rely on the join; anything not in that list is unverified by definition.
