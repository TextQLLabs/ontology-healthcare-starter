# NAVIGATION — read this first

Routing table for Ana. **Start here before answering any question.** Find the user's
intent in the left column; open the files in the right column; never guess code sets or
metric definitions — they are defined here.

## Operating rules (always)
1. **Discovery first.** On a new connector, pull `information_schema` before writing SQL.
   Confirm column names against `databases/tuva/tables/*.md`.
2. **Dialect.** Default **Redshift** (`dev.tuva`, `tuva.`-qualified, `DATEDIFF`/`NULLIF`).
   BigQuery `tuva_core_v2` equivalents are noted inline in each `.tql`.
3. **Never analyze raw ICD codes directly.** Resolve clinical concepts through the
   groupers in `ontology/dimensions/diagnosis.tql` + `ontology/filters/diagnosis.tql`.
   The canonical grouper per question is in `ontology/notes/diagnosis-coding.md`.
4. **Governance.** Apply small-cell suppression (counts < 11) and PHI rules from
   `ontology/notes/governance-phi.md`. Sensitive diagnoses (42 CFR Part 2) are gated.
5. **Prefer a governed `.tql` surface over raw SQL.** Render → inspect → execute.

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
| **Members / enrollment / demographics** | `relations/patient.tql` · `relations/eligibility.tql` · `dimensions/patient.tql` |
| **Providers / specialty** | `dimensions/provider.tql` |
| **Which code systems exist / licensing** | `notes/code-systems-overview.md` · `LICENSING.md` |

## Repo map
```
config/org_context.md       agent system instructions, dialect + PHI rules, connector routing
ontology/
  schema.tql                central table backings (rename once, everywhere follows)
  relations/                per-source modules: source table + key columns + metric keys
  dimensions/               grouping expressions, each with the join it needs
  filters/                  reusable filter predicates (eq/gte/in/… + clinical value-sets)
  queries/                  public governed query surfaces (the metrics)
  notes/                    decision records + coding/governance rationale
reference/terminology/      public grouper crosswalks (CCSR, HCC, chronic, ICD chapters)
databases/tuva/             schema overview + per-table docs (columns, joins, gotchas)
validation/                 golden-query fixtures
```
