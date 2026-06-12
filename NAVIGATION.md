# NAVIGATION — read this first

Routing table for Ana. **Start here before answering any question.** Find the user's
intent in the left column; open the files in the right column; never guess code sets or
metric definitions — they are defined here.

## Operating rules (always)
1. **Discovery first.** On a new connector, pull `information_schema` before writing SQL.
   Confirm column names against `databases/<schema>/tables/*.md`; verify joins per
   `ontology/notes/join-key-verification.md`.
2. **Physical names live ONLY in `ontology/schema.tql`.** Surfaces reference `${logical}`
   backings. Default dialect **Redshift**; BigQuery equivalents noted inline in each `.tql`.
3. **Never analyze raw ICD codes directly.** Resolve clinical concepts through the
   groupers in `ontology/dimensions/diagnosis.tql` + `ontology/filters/diagnosis.tql`.
   The canonical grouper per question is in `ontology/notes/diagnosis-coding.md`.
4. **Governance.** Apply small-cell suppression (< `min_cell_size`, see `config/org_context.md`)
   and PHI rules from `ontology/notes/governance-phi.md`. Sensitive diagnoses (42 CFR Part 2)
   are gated; direct identifiers are join-keys only, never output.
5. **Prefer a governed `.tql` surface over raw SQL.** Render → inspect → execute.
6. **Know the claim grain** before counting claims/cost on a new warehouse —
   `ontology/notes/claim-grain.md`.

## Intent → files

| If the user asks about… | Open |
|---|---|
| **Cost / spend / PMPM / trend** | `queries/cost_pmpm.tql` · `notes/cost-definition.md` |
| **Readmissions** | `queries/readmission_rate.tql` · `notes/readmission-definition.md` |
| **Disease prevalence / "how many patients with X"** | `queries/condition_prevalence.tql` · `dimensions/diagnosis.tql` · `filters/diagnosis.tql` |
| **Comorbidity / risk / RAF / HCC** | `queries/comorbidity_profile.tql` · `notes/risk-adjustment-hcc.md` |
| **Utilization (admits/ED per 1000)** | `queries/utilization_per_1000.tql` |
| **Medication adherence / PDC** | `queries/rx_adherence_pdc.tql` · `dimensions/drug.tql` |
| **Quality measures / HEDIS / Stars** | `queries/hedis_measure.tql` (template) |
| **"What does ICD code X mean / roll up to"** | `dimensions/diagnosis.tql` · `reference/terminology/` · `notes/code-systems-overview.md` |
| **Members / enrollment / demographics** | `relations/person.tql` · `relations/eligibility.tql` · `dimensions/patient.tql` |
| **Providers / specialty** | `dimensions/provider.tql` |
| **What a business term means (claim vs line, allowed vs paid, tier…)** | `notes/glossary.md` |
| **Claim header vs line vs event / why a count looks doubled** | `notes/claim-grain.md` |
| **Whether two tables join / how to verify a key** | `notes/join-key-verification.md` |
| **Setting up against a new warehouse / renaming tables** | `MIGRATION.md` · `ontology/schema.tql` · `validation/validate_tql.py` |
| **Which code systems exist / licensing** | `notes/code-systems-overview.md` · `LICENSING.md` |

## Repo map
```
config/org_context.md       agent system instructions, per-deployment CONFIG, PHI rules
MIGRATION.md                re-point the starter at a new warehouse in 8 steps (+ field lessons)
ontology/
  schema.tql                THE physical mapping layer — the only file naming real tables
  relations/                per-source modules: logical backing + key columns + metric keys
  dimensions/               grouping expressions, each with the join it needs
  filters/                  reusable filter predicates (eq/gte/in/… + clinical value-sets)
  queries/                  public governed query surfaces (the metrics)
  notes/                    decision records, glossary, grain/join/PHI guidance
reference/terminology/      public grouper crosswalks (CCSR, HCC, chronic, ICD chapters)
databases/tuva/             the REFERENCE dataset's docs — copy the folder shape for yours
validation/                 validate_tql.py · dry-run prompt · golden-query fixtures
```
