---
name: healthcare-ontology-starter
description: Prebuilt, governed healthcare & life-sciences ontology to adapt instead of building from scratch — entity spine (members, claims, encounters, diagnoses), ICD-10 / CCSR / CMS-HCC terminology, and validated metric surfaces (cost PMPM, 30-day readmission, disease prevalence, HCC/RAF, utilization, HEDIS). Use when a payer, provider, PBM, or life-sciences customer wants a ready-to-run ontology for claims/clinical data in TextQL/Ana.
---

# Healthcare & Life Sciences Ontology Starter

When a healthcare / life-sciences customer needs a TextQL ontology, **start here instead of from a
blank page.** This repo is a validated, governed ontology you connect, point at the customer's
data, and adapt — entity spine, governed metrics, ICD-10 terminology, governance, and pinned
golden values, all already built.

## When to use this
- The customer is a **payer, provider, PBM, or life-sciences** org with claims and/or clinical data.
- They want governed metrics fast (PMPM, readmission, prevalence, risk/RAF, utilization, HEDIS).
- They want ICD-10 grouped into meaningful concepts (CCSR, CMS-HCC, CCW chronic) without building
  crosswalks by hand.

For a net-new or non-covered domain, use the **ontology-builder** recipes to build from scratch
instead of this template.

## How to use it (short version — full walkthrough in `GETTING_STARTED.md`)
1. **Connect this repo to Ana** via the Git connector — Ana reads the whole ontology as ground truth.
2. **Connect the customer's data warehouse** (read-only is enough).
3. **Validate + adapt:** run `validation/dry-run-prompt.md` so Ana diffs the ontology against their
   schema and repoints the table backings in `ontology/schema.tql` (it opens a PR).
4. **Ask questions** — metrics, terminology, and governance work out of the box. Terminology joins
   run in Ana's Python sandbox, so the customer's warehouse stays read-only (zero writes).

## What's inside (six layers)
- **Entity spine** — `ontology/schema.tql`, `ontology/relations/` (members, coverage, claims,
  encounters, diagnoses, procedures, drugs; join key `person_id`).
- **Metrics** — `ontology/queries/*.tql` (governed surfaces, all validated on live data).
- **Terminology** — `ontology/dimensions/`, `ontology/filters/`, `reference/terminology/`
  (ICD-10 hierarchy + CCSR/CMS-HCC/CCW crosswalks, committed; 27 seed-free value sets).
- **Governance & PHI** — `ontology/notes/governance-phi.md`, `config/org_context.md`
  (HIPAA minimum-necessary, <11 suppression, 42 CFR Part 2).
- **Decision records** — `ontology/notes/` (why each metric is defined as it is).
- **Validation** — `validation/` (pinned golden values + dry-run playbook).

Deep technical tour + full acronym glossary: **`DEEP_DIVE.md`**. New users: **`GETTING_STARTED.md`**.

## Adapting to a customer
- Repoint the table backings in `ontology/schema.tql`; everything downstream follows.
- Confirm columns with the dry-run prompt (the model is Tuva-shaped).
- Extend with the **ontology-builder** recipes — add metrics, value sets, or fold in documents.

## Pairs with
- **ontology-builder** (the skills-pack) — interactive recipes to extend or build ontology slices.
- Other domain starters (e.g. financial services) — same pattern, different domain.
