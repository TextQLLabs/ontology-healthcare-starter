# MIGRATION — re-point this starter at YOUR warehouse in 8 steps

This repo is built on one asymmetry, observed across real deployments: **teams keep ~100% of
the structure and replace ~100% of the data model.** The skeleton (taxonomy, routing, governed
surfaces, terminology pattern, governance) is the asset; any hardcoded schema is a liability.
So the physical model is quarantined in **one file** — `ontology/schema.tql` — and this guide
is the checklist for swapping it.

Works the same for commercial, Medicare, or Medicaid warehouses on Redshift, BigQuery,
Snowflake, or Databricks. Budget: a half-day with warehouse access; most of it is verification,
not editing.

## Step 0 — Discover (nothing trusted yet)
Attach the warehouse connector (read-only is enough) and run the prompt in
`validation/dry-run-prompt.md`. It inventories tables/columns, encounter-type literals, code
systems, cost-column population, denominator grain, and the data horizon (last date present).

## Step 1 — Determine your claim grain (before editing anything)
Wide one-row-per-line model, or normalized header/line/event? Read
`ontology/notes/claim-grain.md`. If normalized, decide now which table anchors claims, where
cost columns live, and how the member key is reached. This decision shapes every other step.

## Step 2 — Re-point `ontology/schema.tql` (the ONLY file with physical names)
- Repoint each backing (`eligibility`, `medical_claim`, `encounter`, `condition`, …).
- If you have a real member/patient table, point `person_grain` at it (one line).
- Fill `claim_header` / `claim_line` / `claim_event` if normalized.
- Set `analysis_end_date` to your data horizon (from step 0).

## Step 3 — Verify joins you intend to rely on
Per `ontology/notes/join-key-verification.md`: key exists on both sides, overlap rate, grain
(1:1 vs 1:N). Record verdicts in `databases/<yourschema>/README.md` (copy the `databases/tuva/`
folder as the template and rewrite it for your warehouse — that folder documents the
*reference* dataset, not yours).

## Step 4 — Validate before you trust (required, not optional)
```bash
python3 validation/validate_tql.py                # static: every ${ref} resolves
python3 validation/validate_tql.py --check-sql    # paste output into Ana: rows = missing columns
# or, with direct access:
python3 validation/validate_tql.py --dsn "<dsn>" --explain   # live column check + compile test
```
Fix what it finds: column renames go in the affected `relations/*.tql` / `queries/*.tql`;
table renames go in `schema.tql` only. Re-run until clean. This single gate catches the
typo'd-backing, wrong-alias, and missing-column bug classes that otherwise surface as wrong
numbers in front of stakeholders.

## Step 5 — Fix the dataset-specific literals
The validator can't know your enumerations. Grep targets, all flagged inline:
- `encounter_type` literals (`'acute inpatient'`, `'emergency department'`) — from dry-run Q3.
- `normalized_code_type` spelling (`'icd-10-cm'`) — from dry-run Q4.
- Cost basis default (`charge` vs `allowed` vs `paid`) — from dry-run Q5; set it in
  `cost_pmpm.tql` + `notes/cost-definition.md`.
- Record-version flags: apply per table where verified (`notes/claim-grain.md`).

## Step 6 — Tune governance to your regime
`config/org_context.md` CONFIG block (`min_cell_size`) + `ontology/notes/governance-phi.md`
§0 identifier inventory, filled in for your schema. Compliance signs off here.

## Step 7 — Localize the vocabulary
`ontology/notes/glossary.md`: walk the LOB-variance column for your line of business and
override what differs (cost basis, denial semantics, formulary model, risk model —
HHS-HCC/CDPS instead of CMS-HCC, etc.). Keep the term → definition → source pattern.

## Step 8 — Pin golden values
Run each governed surface once, confirm the numbers with a business owner, and pin them in
`validation/golden-queries.md` (Status `unverified` → `verified`). Re-run on every schema or
crosswalk change; alert on drift. Done — the ontology is now *yours*.

---

# Appendix — field lessons (why this guide looks the way it does)

Hard-won, deployment-agnostic, and each now has a structural countermeasure in the repo:

**1. The header/line/event grain trap.** Surfaces written against a wide one-row-per-claim
model selected member key, clinical codes, and amounts off a single alias. On a normalized
warehouse those columns live on three different tables with different keys; the queries
either failed to compile or — worse — double-counted lines as claims. *Countermeasure:*
`notes/claim-grain.md` + explicit `claim_header`/`claim_line`/`claim_event` slots in
`schema.tql` + the anchor-on-the-header worked example.

**2. The unreachable member key.** A fact table everyone assumed joined to members turned out
to share no usable key with the member spine — the only path was a bridge table found by
reading `information_schema`, and one "obvious" linkage didn't exist at all. Asserted coverage
stats from the source dataset ("98% of X joins Y") were fiction on the new one.
*Countermeasure:* no linkage facts ship in this repo; `notes/join-key-verification.md` ships
instead, and verified joins are recorded per-warehouse in `databases/<yourschema>/`.

**3. The non-universal record-version flag.** A blanket "always filter the current-record
indicator" rule broke on tables that lack the column, and the failure mode flipped by table:
compile error where it was missing, double-counted history where it existed but was skipped.
*Countermeasure:* verify-per-table procedure in `notes/claim-grain.md`.

**4. Validation by stakeholder is too late.** Every one of the bugs above is mechanically
detectable from `information_schema` + a compile test — none required domain knowledge to
catch. *Countermeasure:* `validation/validate_tql.py` exists, and Step 4 is mandatory.
