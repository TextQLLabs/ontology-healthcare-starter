# Definition: Risk adjustment (CMS-HCC / RAF)

**Status:** Adopted · **Surface:** `queries/comorbidity_profile.tql` · **Crosswalk:** `reference/terminology/hcc_model.md` · **Owner:** Actuarial + Risk Adjustment

## Metric
```
member_raf = sum(raf_weight of the member's qualifying HCCs)  [+ demographic factors]
```
A higher RAF = higher expected cost = higher risk-adjusted payment. The payer-critical metric.

## Decisions
- **Model version matters.** Weights and the dx→HCC map change by CMS model version (e.g.
  V24 vs V28) and payment year. Record the version loaded in `hcc_model.md`. Don't mix versions.
- **HCC hierarchies.** Within a disease group only the **most severe** HCC counts (e.g. count
  diabetes-with-complication *or* without, never both). The starter surface approximates by
  summing distinct HCCs; a production impl applies CMS's HCC-to-HCC exclusion table. **This
  is the #1 thing to harden before reporting RAF.**
- **Qualifying window.** HCCs require a qualifying diagnosis in the **measurement year** —
  the surface filters `recorded_date` to the year params.
- **Enrollee segment.** RAF weights differ by community/institutional, dual status, and
  age/disability. Starter ships community-nondual-aged; expose a segment param if the
  customer needs the others.

## Guardrails
- Demographic factors (age/sex, originally-disabled, etc.) are part of the official RAF —
  the starter computes the **dx-driven HCC portion** only. Note this when reporting.
- Member-level RAF is PHI-adjacent — suppress small cells, aggregate by default.

## Validation
Pin population mean RAF for a known cohort/year; alert on drift after any model-version or
crosswalk refresh.
