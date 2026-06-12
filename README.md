# Healthcare & Life Sciences Ontology

Your starting point for a governed, AI-ready ontology over healthcare and life-sciences data —
members, claims, encounters, diagnoses, procedures, drugs, cost, utilization, quality, and risk.

Connect it to Ana and your data warehouse, point it at your tables, and grow it from here.

> 🚀 **New here? Read [`GETTING_STARTED.md`](GETTING_STARTED.md)** — a step-by-step walkthrough:
> what this is, why it matters, how to set it up in your own Ana environment, and how to make it
> yours. **Pointing it at your own warehouse? [`MIGRATION.md`](MIGRATION.md)** is the 8-step
> re-point checklist. For a deep technical tour, see [`DEEP_DIVE.md`](DEEP_DIVE.md).

It is **just files** — Markdown + `.tql` in a git repo. Business definitions, SQL templates, and
the reasoning behind them live together, are diff-able, and render to **native warehouse SQL**.
When you connect the repo to Ana, Ana reads it and treats it as ground truth — so questions get
answered with consistent, governed SQL instead of guesswork.

> ⚠️ **Code-system scope.** Ships **free / public-domain** code systems and groupers
> (ICD-10-CM/PCS, ICD-9 + GEMs, HCPCS, NDC, RxNorm, MS-DRG/APC, CCSR, CMS-HCC, CCW chronic) —
> the full terminology layer is in the repo, so it's yours to keep and extend. Licensed systems
> (CPT, SNOMED, LOINC) are modeled **structurally**, and certified VSAC value sets are **fetched
> with your own UMLS key**. See `LICENSING.md`.

> 🔒 **No customer data.** Built entirely from publicly available standards (CMS / AHRQ / US Census).
> It contains no customer data — and connecting it never uses your data to build or improve the
> template. When connected it runs **read-only**, and each customer's adaptations live in their own
> repo, never back in this template.

---

## The six layers

| Layer | Where | What |
|---|---|---|
| **1 — Entity spine** | `ontology/schema.tql`, `ontology/relations/` | Member, Provider, Coverage, Medical/Pharmacy Claim, Encounter, Diagnosis, Procedure, Drug. |
| **2 — Metrics** | `ontology/queries/` | Governed surfaces: PMPM, readmission, prevalence, comorbidity/RAF, utilization/1000, Rx adherence, HEDIS template. |
| **3 — Terminology** | `ontology/dimensions/`, `ontology/filters/`, `reference/terminology/` | **The heart.** ICD-10 hierarchy + groupers (CCSR, CMS-HCC, CCW) as dimensions, filters & committed crosswalks. |
| **4 — Governance & PHI** | `ontology/notes/governance-phi.md`, `config/org_context.md` | HIPAA minimum-necessary, <11 suppression, 42 CFR Part 2. |
| **5 — Decision records** | `ontology/notes/` | Why each metric is defined the way it is; canonical grouper per question; glossary, claim-grain + join-verification guides. |
| **6 — Validation** | `validation/` | `validate_tql.py` (every surface checked against live `information_schema` + compiled), golden queries with pinned values, the dry-run playbook. |

`STANDARDS.md` maps the model to the industry data models it aligns with (Tuva, OMOP, FHIR, X12).

---

## Quick start (full version in `GETTING_STARTED.md`)

1. **Connect this repo to Ana** via the Git connector — Ana now knows the whole ontology.
2. **Connect your data warehouse** (Redshift, BigQuery, Snowflake, …) — read-only is enough.
3. **Validate before you trust** — run the dry-run prompt + `validation/validate_tql.py`
   against your schema, fix what they find (usually just `ontology/schema.tql`). See `MIGRATION.md`.
4. **Start asking questions** — Ana routes each through the governed definitions and shows its SQL.

The terminology crosswalks are already in the repo, so the grouper logic (CCSR, HCC/RAF, chronic)
works with **zero writes to your warehouse** — Ana joins them in its Python sandbox. See
`ontology/notes/terminology-join-pattern.md`.

## Default connector / dialect

Authored **Redshift-first** against a Tuva-shaped clinical+claims model (join key `person_id`),
with BigQuery equivalents noted inline in each `.tql`. The semantic layer (metrics, routing,
terminology) is fully separated from the physical mapping: **every physical table name lives in
`ontology/schema.tql`** and surfaces reference logical `${name}` backings — so re-pointing to
your warehouse is one file plus the `MIGRATION.md` checklist, not sixteen edits.

> **Status:** validated end-to-end on live data — all 10 governed surfaces run, with golden
> values pinned in `validation/golden-queries.md`.
