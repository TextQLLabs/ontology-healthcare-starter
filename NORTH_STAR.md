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

## Step 1 — Decide what your ontology is *for*

Before connecting anything, answer one question with your stakeholders:

> **When this works, what does someone do differently on Monday morning?**

That answer is your North Star. It is not "model all of healthcare." It is something
narrow and real: *"the actuarial team stops waiting three days for a PMPM cut,"* or
*"care managers see open gaps for their panel every morning."* Everything in this repo is
in service of a North Star like that — and the parts that don't serve yours, you ignore.

If you can't name the North Star, you are not ready to build the ontology. You are ready
to have the North Star conversation. Do that first.

## The archetypes — pick the one that fits

Most healthcare/life-sciences engagements start from one of three North Stars. Pick the
one closest to yours; it tells you which surfaces, terminology, and governance in this
repo to lead with — and which to leave for later.

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
Same idea — name it, then lead with the surfaces that serve it.)*

## Step 2 — Feed your existing context as a corpus (don't migrate)

You already have ontology — it's just scattered. dbt models, LookML, a metrics wiki, the
spreadsheet where someone defined "active member." **Point Ana at all of it as additional
context.** You are not migrating it into a rigid schema; you are giving Ana more to read.
This repo + your existing definitions together are the starting corpus.

## Step 3 — Use it, and let the model accrete

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

**Next:** once you've named your North Star, see [`QUESTION_LIBRARY.md`](QUESTION_LIBRARY.md)
to pick the ~20 questions that matter, then [`GETTING_STARTED.md`](GETTING_STARTED.md) to
connect Ana and start.
