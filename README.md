# Healthcare & Life Sciences Ontology

A **document of expertise** for healthcare and life-sciences data — the entity vocabulary,
governed metric definitions, terminology crosswalks, PHI governance, and the hard-won
*known failure modes* of working with members, claims, encounters, diagnoses, procedures,
drugs, cost, utilization, quality, and risk.

> 🧭 **Read [`NORTH_STAR.md`](NORTH_STAR.md) first.** This repo is **not a schema to deploy or
> a form to fill out** — treating it that way is the fastest way to build a model nobody trusts.
> It is a warm-start *corpus* that Ana reads as context, and a head start on the model **you and
> Ana build against real questions**, committed to git as you go. `NORTH_STAR.md` shows you how:
> name what your ontology is *for*, pick the archetype that fits, and let the model accrete from
> use. Then [`QUESTION_LIBRARY.md`](QUESTION_LIBRARY.md) helps you choose the ~20 questions that
> matter.

> 🚀 **Ready to connect it?** [`GETTING_STARTED.md`](GETTING_STARTED.md) is the step-by-step
> walkthrough. **Pointing it at your own warehouse?** [`MIGRATION.md`](MIGRATION.md) is the 8-step
> re-point checklist. For a deep technical tour, see [`DEEP_DIVE.md`](DEEP_DIVE.md).

It is **just files** — Markdown + `.tql` in a git repo. Most of what matters here is *prose and
reasoning*: definitions of what terms mean, where the data gets messy, and why each metric is
shaped the way it is. The `.tql` files are the **governed metric layer you grow into** — one file
type among many, not where you start. When you connect the repo to Ana, Ana reads all of it as
context and proposes its own additions back as git commits you review — a **malleable, self-
maintaining semantic layer** (see `NORTH_STAR.md` → *Why this works*), not a static template.

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

0. **Name your North Star** — what does someone do differently on Monday when this works?
   Pick the archetype that fits (`NORTH_STAR.md`) and the ~20 questions that matter
   (`QUESTION_LIBRARY.md`). *Skip this and you'll build a model nobody trusts.*
1. **Connect this repo to Ana** via the Git connector — Ana now reads the whole corpus as context.
2. **Connect your data warehouse** (Redshift, BigQuery, Snowflake, …) — read-only is enough.
   Point Ana at any existing context you have too (dbt, LookML, a metrics wiki) — as corpus, not migration.
3. **Validate before you trust** — run the dry-run prompt + `validation/validate_tql.py`
   against your schema, fix what they find (usually just `ontology/schema.tql`). See `MIGRATION.md`.
4. **Ask your real questions** — Ana answers governed ones from the definitions (showing its SQL),
   explores the frontier for the rest, and **proposes write-backs as git commits you review**.
   The model accretes from use; you ratify it. That's the malleable loop, not a one-time deploy.

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
