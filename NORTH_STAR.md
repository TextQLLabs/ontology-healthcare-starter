# Start here: your North Star

> **Read this before you read anything else in this repo.** It is the most important
> file here — more important than `schema.tql`, more important than any `.tql` metric.

## This is not a form to fill out

The biggest mistake you can make with this repo is to treat it as a schema to deploy —
to skim it, decide it's "close enough" to healthcare, point it at your warehouse, and
ship. That is the same mistake as building a rigid semantic layer in a BI tool, just
faster to make: you bake in decisions before you know which questions actually matter,
and you end up with a model that is 10% useful and 90% noise that nobody trusts.

**A domain starter is a document of expertise, not a destination.** Everything in this
repo — the entity vocabulary, the governed metric *definitions and the reasoning behind
them*, the PHI governance, the [known failure modes](#known-failure-modes), the glossary,
the terminology crosswalks — exists so that **Ana can read it as context** and so that
*you* start a conversation already knowing where this domain gets hard. It is a warm
start, not a finished model.

The model you actually ship is the one **you and Ana build against real questions**, in
your warehouse, committed to git as you go. This repo is the corpus you start from.

**And you won't fill anything out.** There's no questionnaire, no menu to pick from, no
homework. Ana does the work: it scans the data you've connected, proposes your North Star
and the use case that fits, and you confirm or redirect. Start there.

## Let Ana tailor this to you (the actual first step)

Connect your data and any context you have (dbt models, dashboards, docs) to a thread,
then paste this to Ana:

```
Look at the data connected to this thread and any context I've attached (dbt models, dashboards, docs). Based on what you actually see — not assumptions:
1. Summarize in 3-4 lines what we have: the key tables, the grain, and the domains it covers.
2. Ask me 5-7 sharp scoping questions to pin down what we're really doing — who will use this, what decision it changes on Monday morning, which use case fits, what "working" looks like in 30 days, and where our data is messiest. A few at a time, not all at once.
3. From my answers plus the data, recommend the use case that fits and draft our North Star: one short paragraph on what this ontology is for, plus the 6-8 questions it must answer in 30 days.
4. Save it as north_star.md in the ontology and propose it as a reviewed change, so every later step builds toward it.
```

That's the whole flow: **Ana scans → proposes a North Star → asks only what it can't infer
from the data → you confirm or redirect.** It takes minutes, not a survey, and it produces a
North Star grounded in *your* tables rather than a generic template. Everything else in this
repo exists to make that proposal sharper and to give you the vocabulary to refine it.

## What a North Star looks like (examples to spark yours)

Most healthcare/life-sciences teams land on a North Star adjacent to one of the three below.
These are **common examples, not a menu to pick from** — yours might be one of these, a blend,
or something next to them. Ana drafts yours from your data; the value of reading these is the
"lead with" hints, which tell you which surfaces, terminology, and governance in this repo
become relevant once your North Star is set.

### A. BI parity — "match the dashboards we already trust"
**For:** analytics teams who already have a warehouse and reports, and want Ana to
answer in natural language *and reconcile to the numbers they know.*
**Lead with:** `queries/cost_pmpm.tql`, `utilization_per_1000.tql`, `condition_prevalence.tql`;
`validation/golden-queries.md` (reconcile against a number someone already trusts).
**The win:** the first time Ana hits the exact PMPM the actuary expected, you have trust.
**Failure mode to avoid:** redefining a metric a hair differently than their existing
report and eroding trust on day one. Reconcile *first*, govern *second*.

### B. Care-gap / quality — "close gaps and move quality measures"
**For:** care management, quality, and pop-health teams working HEDIS / Stars / gaps.
**Lead with:** `queries/hedis_measure.tql`, `rx_adherence_pdc.tql`; the value-set
terminology (`reference/terminology/value-sets.md`) and `dimensions/diagnosis.tql`.
**The win:** an open-gap list a care manager can act on, with the numerator/denominator
logic visible and defensible.
**Failure mode to avoid:** measure logic that doesn't match the official spec
(continuous-enrollment, anchor dates, exclusions). Govern the *spec*, not a guess.

### C. Risk adjustment — "capture the risk we're actually carrying"
**For:** MA / ACA / value-based teams managing RAF accuracy and suspecting.
**Lead with:** `queries/comorbidity_profile.tql`; `reference/terminology/hcc_model.md`,
the CMS-HCC crosswalks, `notes/risk-adjustment-hcc.md`.
**The win:** a defensible RAF with the dx→HCC→coefficient chain fully auditable.
**Failure mode to avoid:** mixing model years or counting unconfirmed diagnoses. The
governance here exists precisely because regulators ask you to show your work.

*(Other common ones: cost/MLR management, utilization & readmissions, network adequacy.
Same idea — Ana drafts this from your data; you refine it, then lead with the surfaces
that serve it.)*

## A few things this starter is great at

Flavor to spark ideas — **not homework, and not a list to work through.** When Ana proposes
your North Star, it'll pull from the kind of questions this repo already knows how to govern:

- PMPM for a population over a period, trended monthly and decomposed into inpatient /
  outpatient / professional / Rx. → `cost_pmpm.tql`
- 30-day all-cause readmission rate, with the index/exclusion window done correctly. →
  `readmission_rate.tql`
- The open-gap work list for a HEDIS measure right now, with numerator/denominator visible. →
  `hedis_measure.tql`
- Population RAF trended, with the dx → HCC → coefficient chain fully auditable. →
  `comorbidity_profile.tql` + HCC crosswalks
- Medication adherence (PDC) for a drug class, share ≥ 0.80. → `rx_adherence_pdc.tql`
- Prevalence of a condition by CCSR, and the top comorbidities co-occurring with it. →
  `condition_prevalence.tql`, `comorbidity_profile.tql`
- High-cost claimant concentration — the cost of the top 1% / 5% of members.
- Any measure above, stratified by race/ethnicity, language, dual status, or geography
  (with <11 small-cell suppression). → `governance-phi.md`

## Feed your existing context as a corpus (don't migrate)

You already have ontology — it's just scattered. dbt models, LookML, a metrics wiki, the
spreadsheet where someone defined "active member." **Point Ana at all of it as additional
context.** You are not migrating it into a rigid schema; you are giving Ana more to read.
This repo + your existing definitions together are the starting corpus.

## Use it, and let the model accrete

This is the part the rigid-tool playbook gets wrong. **You do not finish the ontology and
then start asking questions. You ask questions, and the ontology grows from the answers.**

When you ask Ana something this repo doesn't cover, Ana explores the frontier, answers,
and **proposes a write-back** — a new metric, a discovered join, a corrected filter — as a
git commit you review. Over time the model gets more complete and exploration shrinks
toward a "novelty floor" instead of being re-paid on every question. (This is the
[*malleable semantic layer*](#why-this-works) idea — discovery paid once, amortized across
every future question, with git provenance on every change.)

Your job is not to author the whole model up front. Your job is to **establish the North
Star, seed it with this corpus, start asking real questions, and ratify what Ana proposes**
via normal git review. High-stakes definitions (anything in `governance-phi.md` scope, or
core metrics) go through human review before merge — see `STANDARDS.md`.

## Known failure modes (where naive implementations break)

This is the expertise that makes the repo worth more than a blank slate. Each has a note:

| Trap | Where it bites | Note |
|---|---|---|
| Claim header vs. line grain | Double-counting cost/utilization | `notes/claim-grain.md` |
| Identity resolution | One member counted as many | `notes/identity-resolution.md` |
| The coding tuple (code + system + version) | ICD-9/10 mismatches, wrong groupers | `notes/coding-tuple.md` |
| Unverified join keys | Silent fan-out, inflated counts | `notes/join-key-verification.md` |
| HCC model-year mixing | Indefensible RAF | `notes/risk-adjustment-hcc.md` |
| Readmission window/exclusion logic | Wrong rate, failed audit | `notes/readmission-definition.md` |
| Cost: allowed vs. paid vs. billed | Metrics that don't reconcile | `notes/cost-definition.md` |

Lead a stakeholder conversation with these and you are immediately the most credible
person in the room. That is what this repo is *for*.

## Why this works

The approach behind this repo is documented in TextQL's research:
**"Malleability Is All You Need: A Self-Maintaining Semantic Layer for Data Agents"**
(Baumstark, Tomitsuka, Ma — VLDB 2026). The short version: agents that re-discover a
warehouse on every question pay an "amnesia tax" — most of their tokens go to rediscovery,
results aren't reproducible, and nothing carries across engines. A version-controlled,
agent-writable semantic layer inverts that: read what's known → explore only the frontier
→ answer → commit. The measured result is a ~30% token reduction and a model that gets
*cheaper and more reliable* the more it's used.

This repo is a head start on that layer for healthcare — not a substitute for building it.

---

**Next:** let Ana propose your North Star from your data (the prompt above), then head to
[`GETTING_STARTED.md`](GETTING_STARTED.md) to connect Ana and start building toward it.
