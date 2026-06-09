# A/B test — plain-vanilla Ana vs. the ontology

A side-by-side that shows, concretely, what connecting this ontology changes. Doubles as a GTM
demo ("let me test it") and the source of a **measured** improvement number.

## How to run it
Two threads against the **same** connector (the Tuva healthcare demo; current date **2018-12-31**):
- **A — Vanilla:** Ana with the warehouse connector only. **No ontology repo connected.**
- **B — Ontology:** the same connector **plus** this ontology repo connected (Git connector).

Ask each question below in both threads. For the consistency check, ask 3× (or 3 phrasings). Score
with the rubric and fill the results table. (The "Correct answer" column is pre-filled from the
validated golden values in `golden-queries.md`.)

> Honesty note: the lift is large on **coded / multi-definition / risk** questions and **small on
> trivial ones** (Q7 is the control). Showing the control builds trust — it's not magic, it's
> governance where governance matters.

## The questions

| # | Ask Ana (both threads) | Correct answer (governed) | Why vanilla struggles |
|---|---|---|---|
| 1 | "How many members have diabetes? What's the prevalence?" | **0.446** (value-set E08–E13) / 0.297 (CCSR END003) | Vanilla guesses one code (e.g. `E11`) or a text `LIKE '%diabetes%'` on descriptions → partial/wrong; doesn't know the ICD-10 branch or CCSR. |
| 2 | "What's our 30-day readmission rate?" | **0.1221** (governed CMS definition) | Vanilla picks an arbitrary definition, often miscounts the index/30-day window, and varies run to run. |
| 3 | "What's our average member risk (RAF) score, and which conditions drive it?" | **0.680** mean RAF; HF & diabetes-w/-complication lead | Vanilla can't map dx→HCC, can't apply the CMS hierarchy (trumping) → fabricates or fails. |
| 4 | "What's our cost PMPM?" | **$13,277** (fullmonth, charge basis) — and it flags the basis | Vanilla divides charges by member count (no member-month concept) → wrong magnitude, no denominator definition. |
| 5 | "How many inpatient admissions per 1,000 members?" | **167** /1,000 (annualized, member-month denom) | Vanilla returns a raw count or uses the wrong denominator/annualization. |
| 6 | (Consistency) Ask Q1 three ways: "diabetic members %", "prevalence of diabetes", "how many have DM" | **0.446 every time** | Vanilla drifts across phrasings/runs. |
| 7 | (Control) "How many members are there total?" | **1,000** | Both should get this — simple single-table count. Establishes it's not magic. |

> Bonus the demo surfaces for free: the live schema has **no `patient` table** and codes live in
> `normalized_code`. Vanilla typically mis-joins or errors; the ontology already knows — so even
> "does it run at all" often favors B.

## Scoring rubric (per question)
- **Correct?** matches the governed answer — Yes / Partial / No.
- **Consistent?** same answer across the 3 runs/phrasings — Yes / No.
- **Traceable?** shows the definition used + the SQL — Yes / No.

## Results (fill in after running)

| # | Vanilla: correct / consistent / traceable | Ontology: correct / consistent / traceable |
|---|---|---|
| 1 | TBD | ✅ correct · ✅ consistent · ✅ traceable |
| 2 | TBD | ✅ · ✅ · ✅ |
| 3 | TBD | ✅ · ✅ · ✅ |
| 4 | TBD | ✅ · ✅ · ✅ (flags charge-vs-allowed) |
| 5 | TBD | ✅ · ✅ · ✅ |
| 6 | TBD | ✅ · ✅ · ✅ |
| 7 | TBD (likely ✅) | ✅ · ✅ · ✅ |

**Headline metric to report:** "Ontology correct on N/7, consistent 7/7, traceable 7/7; vanilla
correct on M/7, consistent _/7, traceable 0/7." Fill M and N from the run — that's the number for GTM.

## What to take away
- The **consistency** column is usually the most striking for enterprise buyers: the ontology
  returns the same trustable number every time; vanilla doesn't.
- The ontology answers are pre-validated (see `golden-queries.md`), so B's column is known-correct.
- Keep the control (Q7) in the deck — candor that simple questions are equivalent makes the wins
  on Q1–Q5 credible.
