# Identity resolution — the member key across multiple sources

**Status:** Adopted · **Applies to:** `person_grain` (schema.tql), every per-member rate ·
**Pairs with:** `join-key-verification.md`, `coding-tuple.md` · **Sources:** `SOURCES.md`

The reference dataset has one clean `person_id` per member. Real payers rarely do — a member
shows up under different IDs in eligibility, medical claims, pharmacy, and lab feeds, because
each came from a different source system. **Counting members before resolving identity
double-counts**, and every PMPM / per-1000 / prevalence rate inherits the error.

Three independent models name the same solution:

| Model | The local key | The resolved key | Mechanism |
|---|---|---|---|
| **Tuva** | source ids | `person_id` | `person_id_crosswalk` table |
| **SAP CHP** | `(Source, SourcePatientID)` | `PatientID` / **Patient Best Record** | best-record links many source IDs to one real person; `DWID` surrogate is unique across sources |
| **MDM / EMPI** (general) | source MRNs | enterprise/golden id | probabilistic + deterministic match |

The shape is always the same: a member's true key is a **`(source_system, source_id)` tuple**
resolved to a **global id** through a crosswalk or best-record. The reference dataset's single
`person_id` is the degenerate case where that resolution already happened upstream.

## What this means for re-pointing

1. **Find the resolution layer first.** During discovery, look for a crosswalk / best-record /
   EMPI table (names like `*_crosswalk`, `*_xwalk`, `member_master`, `best_record`, `empi`):
   ```sql
   SELECT table_name FROM information_schema.tables
   WHERE table_schema='<schema>'
     AND (table_name ILIKE '%crosswalk%' OR table_name ILIKE '%xwalk%'
       OR table_name ILIKE '%master%'   OR table_name ILIKE '%empi%'
       OR table_name ILIKE '%best%record%');
   ```
2. **Point `person_grain` at the RESOLVED id**, and collapse on it — not on a source id. If the
   warehouse already exposes a resolved id on every fact, use it directly. If facts only carry
   the *local* `(source, source_id)`, `person_grain` must join through the crosswalk to the
   global id before any `COUNT(DISTINCT member)`.
3. **Verify the fact tables actually carry the resolved key.** This is the
   `join-key-verification.md` overlap check with a twist: a claims table keyed on a *source*
   member id won't join to an eligibility table keyed on the *resolved* id — same concept,
   different id space, ~0% overlap. That's the signal you must route through the crosswalk, not
   that the join is broken.
4. **Pick the grain consciously.** SAP's Patient Best Record exists precisely because "consistent
   analytics is only possible when filtering on one data source" otherwise. Decide whether a
   member count means *distinct resolved persons* (almost always what's asked) or *distinct
   source records* (rarely), and state which.

## Identifier governance still applies

The resolved id and every source id are **direct identifiers** — join keys only, never output
(`governance-phi.md` §0). Resolving identity does not de-identify; a stable golden id is still
PHI. Small-cell suppression applies to the resolved-person counts.

> Record the verdict in `databases/<schema>/README.md`, e.g.:
> `member identity: facts carry source_member_id; resolve via member_master.person_id (1:1 after xwalk) — collapse person_grain through the xwalk`
