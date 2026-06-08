# Healthcare & Life Sciences — Ontology Starter

A **general, account-agnostic TextQL ontology** for payers, providers, and life-sciences
customers. Branch this once per customer (Cigna, the next payer, …) and adapt — don't rebuild
from zero each time.

> 🚀 **New here? Read [`GETTING_STARTED.md`](GETTING_STARTED.md)** — a step-by-step,
> non-expert walkthrough: what this is, why it matters, how to set it up in your own Ana
> environment, and how to customize it for your company.

It is **just files** — Markdown + `.tql` in a git repo. Definitions, SQL templates, and
business rationale live together, are diff-able, and render to **native warehouse SQL**.
No proprietary lock-in.

> ⚠️ **Redistributable scope.** Ships **only free / public-domain code systems** (ICD-10-CM/PCS,
> ICD-9 + GEMs, HCPCS, NDC, RxNorm, MS-DRG/APC, and the public groupers CCSR / CMS-HCC / CCW
> chronic). Licensed systems (CPT, SNOMED, LOINC) are modeled **structurally**; certified VSAC
> value sets are **fetched with the customer's own UMLS key, never bundled**. See `LICENSING.md`.

---

## The six layers

| Layer | Where | What |
|---|---|---|
| **1 — Entity spine** | `ontology/schema.tql`, `ontology/relations/` | Member, Provider, Coverage, Medical/Pharmacy Claim, Encounter, Diagnosis, Procedure, Drug (Tuva grain). |
| **2 — Metrics** | `ontology/queries/` | Governed surfaces: PMPM, readmission, prevalence, comorbidity/RAF, utilization/1000, Rx adherence, HEDIS template. |
| **3 — Terminology** | `ontology/dimensions/`, `ontology/filters/`, `reference/terminology/` | **The heart.** ICD-10 hierarchy + groupers (CCSR, CMS-HCC, CCW) as dimensions & filters, loaded by `load_terminology.py`. |
| **4 — Governance & PHI** | `ontology/notes/governance-phi.md`, `config/org_context.md` | HIPAA minimum-necessary, <11 suppression, 42 CFR Part 2. |
| **5 — Decision records** | `ontology/notes/` | Why each metric is defined the way it is; canonical grouper per question. |
| **6 — Validation** | `validation/golden-queries.md` | Pinned known-correct values; drift alerts. |

`STANDARDS.md` anchors the model to the industry CDMs it stands on (Tuva, OMOP, FHIR, X12).

---

## Quick start (summary — full version in GETTING_STARTED.md)

1. **Read `NAVIGATION.md`** — the routing table agents read first.
2. **Clone into your own private git**, point your warehouse connector + Ana at it.
3. **Load terminology:** `cd reference/terminology && python load_terminology.py --download`
   → stage `_build/*.csv` → run `_build/load.sql` (creates the `terminology` schema).
4. **(Optional) Hydrate certified value sets:** `export UMLS_API_KEY=… && python fetch_vsac.py`.
5. **Dry run:** point `ontology/schema.tql` backings at your real tables; run
   `validation/golden-queries.md`.

## Default connector / dialect

Authored **Redshift-first** against the Tuva clinical+claims model (`dev.tuva`, join key
`person_id`). Each `.tql` notes its BigQuery (`tuva_core_v2`) equivalent inline. Swap the table
backings in `schema.tql` to retarget; the metric logic stays put.
