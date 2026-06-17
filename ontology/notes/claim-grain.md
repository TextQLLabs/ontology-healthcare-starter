# Claim grain — header vs. line vs. event (read BEFORE re-pointing the claims backings)

**Status:** Adopted · **Applies to:** `schema.tql` claims backings, every query touching `${medical_claim}`

The reference dataset stores claims as **one wide row per claim line with the member key on
the row**. That shape is common in pre-aggregated/analytic models (CMS research files, Tuva
output) — and rare in transactional warehouses. Most payer/adjudication systems normalize:

| Table | Grain | What lives here (and ONLY here) |
|---|---|---|
| **Claim header** | 1 row / claim | claim status, received/adjudicated dates, billing provider, claim type, total amounts, the link toward the member |
| **Claim line** | 1 row / service line | procedure/drug codes, units, line amounts (allowed/paid), rendering provider, place of service, revenue code |
| **Claim event** | 1 row / adjudication event | denial/adjustment/reversal codes, event timestamps, remit detail |

A given column lives on **exactly one** of these. Denial flags are usually header or event,
never line. Drug codes are line. The member key is often **not on any of them directly** —
it's reached through a bridge (header → enrollment span → member, or header → subscriber +
person code).

### A fourth shape: EAV / generic "interaction" models

Some enterprise clinical warehouses (e.g. SAP Connected Health Platform — `SOURCES.md`) don't
use fixed claim columns at all. They model every clinical event as a generic **interaction**
with a few common columns (member, period start/end, type) and push the *specific* attributes
into **entity-attribute-value (EAV)** side tables — one row per (interaction, attribute, value),
split by value kind (codes/"details", numeric "measures", free "text"). A diagnosis code, a lab
value, and a note all live as rows in those EAV tables, distinguished by an `attribute` column,
not as named columns you can `SELECT`.

Re-pointing onto an EAV source means a surface can't read `c.normalized_code` directly — it must
**pivot** the EAV rows (`WHERE attribute_code = '<dx attribute>'`) up to the grain it needs
first. Treat the pivot like the header→line join: do it in a CTE, name the grain it produces,
and verify which `attribute_code` carries each concept before trusting it. The coding tuple
(`notes/coding-tuple.md`) still applies — EAV just stores the tuple as rows instead of columns.

## The #1 migration bug: "select everything off one alias"

A surface written against the wide model says `mc.normalized_code`, `mc.paid_amount`,
`mc.person_id` — all off one alias. Re-pointed at a normalized warehouse, **each of those
column refs now belongs to a different table**, and the query either fails to compile (lucky)
or silently joins/filters the wrong grain and double-counts lines as claims (unlucky).
`validation/validate_tql.py` catches the compile-level cases; the grain-level cases need the
pattern below.

## The worked pattern: anchor on the header

```sql
-- Counting CLAIMS (or members): anchor on the header; line columns come via a join.
SELECT mb.person_id,
       h.claim_id,
       SUM(l.paid_amount)  AS claim_paid          -- cost columns: LINE grain, aggregated up
FROM   yourschema.claim_header h
JOIN   yourschema.claim_line   l  ON l.claim_id = h.claim_id      -- header -> line
JOIN   yourschema.member_bridge mb ON mb.subscriber_id = h.subscriber_id
                                   AND mb.person_code = h.person_code   -- header -> member
WHERE  h.claim_status = 'PAID'                    -- status: HEADER grain
GROUP  BY mb.person_id, h.claim_id
```

Rules of thumb:
1. **Pick the anchor by what you're counting.** Claims/members → header. Services/units/cost
   detail → line (then be explicit that the count is lines, not claims).
2. **Never aggregate a header column after joining lines** without `DISTINCT`/pre-aggregation —
   a 10-line claim repeats its header amount 10×.
3. **Reach the member key via the documented bridge**, not the shortest-looking join. Two
   tables sharing a *concept* (claim and event both being "about a claim") may share **no
   usable key** — verify per `notes/join-key-verification.md` before writing the join.
4. When you map a normalized warehouse, fill the `claim_header`/`claim_line`/`claim_event`
   backings in `schema.tql` and record which columns you sourced from which grain in
   `databases/<yourschema>/tables/*.md`.

## Two kinds of time: business validity vs. technical validity

A versioned warehouse usually tracks **two** time spans, and conflating them corrupts both
point-in-time and trend queries. SAP CHP names the distinction cleanly (`SOURCES.md`), and it
generalizes:

- **Business validity** — *when the fact was true in the real world.* SAP: `ValidFrom`/`ValidTo`;
  here: eligibility `enrollment_start_date`/`enrollment_end_date`, a diagnosis `onset`/`resolved`
  date. Filter on this to ask "what was true **as of** date X."
- **Technical validity** — *when the record was the live version in the warehouse,* for history
  preservation. SAP: `DWDateFrom`/`DWDateTo` (+ the current-record flags below). Filter on this
  to ask "what did the warehouse **believe** as of load X" — almost always "the current version."

When both exist, a correct as-of-date query filters business validity for the date **and**
technical validity to the current record. Most analytics wants current-record + a business-date
range; mixing them up (e.g. filtering a business date against a technical column) silently
returns superseded rows or none.

## Record-version / current-record flags are NOT universal

Current-record indicators (`curr_rcd_ind`, `is_current`, `active_flag`, or `DWDateTo IS NULL`)
implement *technical* validity above — and the rule "always filter to the current record" is
correct **only on tables that have the column**. Some tables in the same warehouse won't (e.g. an
admissions or event table that's already point-in-time). Treat it as **verify per table**:

```sql
SELECT table_name FROM information_schema.columns
WHERE table_schema = '<yourschema>'
  AND column_name IN ('curr_rcd_ind', 'is_current', 'active_flag', 'current_flag');
```

Document the per-table answer in `databases/<yourschema>/tables/*.md`, apply the filter where
the column exists, and never assume it where it doesn't — a blanket rule fails to compile on
tables that lack it, and silently dropping the filter where it *does* exist double-counts
versioned rows.
