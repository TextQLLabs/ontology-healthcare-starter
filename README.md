# Healthcare & Life Sciences — Ontology Starter

A **general, account-agnostic TextQL ontology** for payers, providers, and life-sciences
customers. Branch this once per customer (Cigna, the next payer, …) and adapt — don't
rebuild from zero each time.

It is **just files** — Markdown + `.tql` in a git repo. Definitions, SQL templates, and
business rationale live together, are diff-able, and render to **native warehouse SQL**.
No proprietary lock-in. (See the 5 design principles in the workshop playbook.)

> ⚠️ **Redistributable scope.** This starter ships **only free / public-domain code
> systems** (ICD-10-CM/PCS, ICD-9 + GEMs, HCPCS, NDC, RxNorm, MS-DRG/APC, and the public
> groupers CCSR / HCC / CCW chronic conditions). Licensed systems (CPT, SNOMED CT, LOINC)
> are modeled **structurally** — the columns and joins are wired, but no code lists are
> bundled. See `LICENSING.md` before adding any.

---

## What's in here — the six layers

| Layer | Where | What |
|---|---|---|
| **1 — Entity spine** | `ontology/schema.tql`, `ontology/relations/` | Member, Provider, Coverage, Medical/Pharmacy Claim, Encounter, Diagnosis, Procedure, Drug. Source-agnostic backbone (Tuva grain by default). |
| **2 — Metrics** | `ontology/queries/` | Governed query surfaces: PMPM, readmission, prevalence, comorbidity/RAF, utilization/1000, Rx adherence, a HEDIS template. |
| **3 — Terminology** | `ontology/dimensions/`, `ontology/filters/`, `reference/terminology/` | **The heart.** ICD-10 hierarchy + clinical groupers (CCSR, HCC, chronic) as dimensions & reusable filter predicates. |
| **4 — Governance & PHI** | `ontology/notes/governance-phi.md`, `config/org_context.md` | HIPAA minimum-necessary, small-cell suppression (<11), 42 CFR Part 2 sensitive dx. |
| **5 — Decision records** | `ontology/notes/` | Why each metric is defined the way it is; which grouper is canonical per question. |
| **6 — Validation** | `validation/golden-queries.md` | Pinned known-correct values; drift alerts. |

`STANDARDS.md` anchors the model to the industry CDMs it stands on (Tuva, OMOP, FHIR, X12).

---

## How to use it

1. **Read `NAVIGATION.md` first** — it's the routing table. Agents (Ana) read it before anything else.
2. **Attach as context** in TextQL, or clone and point Ana at it.
3. **Branch per customer.** Adapt `ontology/schema.tql` table backings to the customer's
   real schema (discover `information_schema` first), keep the terminology layer as-is.
4. **Extend via branch + PR** — propose → diff → review → approve → audit, like code.

## Default connector / dialect

Authored **Redshift-first** against the Tuva clinical+claims model (`dev.tuva`,
join key `person_id`). Every `.tql` notes its BigQuery (`tuva_core_v2`) equivalent inline
(`DATEDIFF`→`DATE_DIFF`, `x::DECIMAL/NULLIF`→`SAFE_DIVIDE`, drop the `tuva.` qualifier).
Swap table backings in `schema.tql` to retarget; the metric logic stays put.
