# Question library — healthcare & life sciences

A library of the questions a mature healthcare data organization should be able to answer
in seconds. **It is not a checklist to implement.** Its job is to help you do two things:

1. **Run the North Star conversation.** Put these in front of stakeholders. The ones that
   make people lean in are your North Star (see [`NORTH_STAR.md`](NORTH_STAR.md)).
2. **Pick the ~20 that matter and start there.** You will not — and should not — build for
   all of them up front. Choose the handful tied to your North Star, get those answered and
   reconciled, and let the model accrete from real use.

Each question maps to a governed surface (`ontology/queries/`), a piece of terminology, or a
governance note. Where a question is a classic trap, the **⚠ watch-out** names what breaks a
naive answer — use these to sound like the expert you are.

> Convention: `[brackets]` are substitution slots — swap in your line of business, population,
> geography, or period.

---

## A. Membership, eligibility & population
1. How many members were enrolled in `[line of business]` as of `[date]`? Member-months for `[period]`?
2. What's our member mix by product, age band, and geography?
3. How many members are dual-eligible / LIS? ⚠ dual status changes month to month — point-in-time vs. ever-in-period.
4. What's our retention / disenrollment rate by cohort?
5. How many members had continuous enrollment for `[measurement year]`? ⚠ HEDIS allowable gaps — see value-set logic.
6. What share of members are attributed to a value-based / ACO arrangement?

## B. Cost & financial (PMPM / MLR)
7. What's PMPM for `[population]` over `[period]`, trended monthly? → `cost_pmpm.tql`
8. Decompose PMPM into inpatient / outpatient / professional / Rx.
9. What's our medical loss ratio by `[product / market]`? ⚠ allowed vs. paid vs. billed — `notes/cost-definition.md`.
10. Which `[CCSR category]` drives the most spend, and is it trending up?
11. What's the cost of the top 1% / 5% of members (high-cost claimant concentration)?
12. Per-member cost of `[chronic condition]` cohort vs. matched non-condition members.
13. What's our paid-claims runout / IBNR completeness by service month? ⚠ claim lag — recent months are incomplete.

## C. Utilization
14. Inpatient admits, ED visits, and bed-days per 1,000 for `[population]`. → `utilization_per_1000.tql`
15. What's our 30-day all-cause readmission rate? → `readmission_rate.tql` ⚠ index/exclusion window — `notes/readmission-definition.md`.
16. Avoidable ED visit rate and top presenting categories.
17. Ambulatory-care-sensitive (ACSC) admission rate.
18. Observation-stay rate and its trend (a classic inpatient/outpatient boundary issue).
19. Telehealth utilization share by specialty.

## D. Clinical / conditions
20. Prevalence of `[condition]` in `[population]`, by CCSR. → `condition_prevalence.tql`
21. Top comorbidities co-occurring with `[condition]`. → `comorbidity_profile.tql`
22. How many members have ≥2 / ≥3 chronic conditions (CCW multimorbidity)?
23. Incidence of newly diagnosed `[condition]` this `[period]` vs. last.
24. ⚠ Are diagnoses coded in ICD-9 anywhere in the lookback? Confirm the GEMs crosswalk — `notes/coding-tuple.md`.

## E. Quality & care gaps (HEDIS / Stars)
25. What's our `[HEDIS measure]` rate, with numerator/denominator visible? → `hedis_measure.tql`
26. Which members have an open gap for `[measure]` right now? (the care-manager work list)
27. Gap-closure rate trend over the measurement year.
28. Rate by provider / clinic — who's above and below benchmark?
29. ⚠ Are exclusions (hospice, advanced illness) applied per the official spec?
30. Projected Stars rating impact if we close `[N]` gaps in `[measure]`.

## F. Pharmacy
31. Medication adherence (PDC) for `[drug class]`, share ≥0.80. → `rx_adherence_pdc.tql`
32. Generic dispensing rate and trend.
33. Specialty-drug spend share and top molecules.
34. Members on `[drug]` without a corresponding `[indication]` diagnosis (data-quality / appropriateness).
35. ⚠ Days-supply and fill-gap logic — PDC is sensitive to overlapping fills and switches.

## G. Risk adjustment
36. Population RAF for `[MA / ACA]`, trended. → `comorbidity_profile.tql` + HCC crosswalks
37. The dx → HCC → coefficient chain for `[member]` (full auditability). ⚠ `notes/risk-adjustment-hcc.md`.
38. Suspected-but-unconfirmed HCCs (suspecting work list).
39. HCC recapture rate year over year.
40. ⚠ Are we mixing CMS-HCC model years? Pin the model year per population.

## H. Provider & network
41. Cost and utilization by attributed provider / group (efficiency profiling).
42. Network adequacy: time/distance or supply by specialty and geography.
43. In- vs. out-of-network spend share by service category.
44. Provider quality scorecard combining gaps, readmissions, and cost.

## I. Equity & access
45. Stratify `[any measure above]` by race/ethnicity, language, dual status, geography. ⚠ small-cell suppression (<11) — `governance-phi.md`.
46. Care-gap disparities across `[SDOH segment]`.

## J. Life sciences / other domains
*(If your North Star is research, trials, or genomics, the sibling kits go deeper —
`ontology-biopharma-starter`, `ontology-clinical-trials-starter`, `ontology-genomics-starter`.)*
47. Patient counts meeting `[clinical criteria]` for feasibility / cohort discovery.
48. Real-world treatment patterns and line-of-therapy for `[indication]`.
49. Time-to-treatment / time-to-diagnosis distributions.

---

## How to use this with Ana

Pick your ~20. Ask them in plain language. For the ones this repo already governs, Ana
answers from the definition and shows its SQL. For the ones it doesn't, Ana explores,
answers, and **proposes a write-back** you review in git — that's how the model grows.
Every ⚠ above is a place to ask Ana to *show its methodology* before you trust the number.

> Building from this library? Reconcile the first answer against a number someone already
> trusts (see `validation/golden-queries.md`). Trust is earned on the first matching number.
