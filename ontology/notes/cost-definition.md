# Definition: Cost PMPM (per member per month)

**Status:** Adopted · **Surface:** `queries/cost_pmpm.tql` · **Owner:** Analytics CoE + Finance/Actuarial

## Metric
```
cost_pmpm = SUM(medical_claim.<cost_col>) / member_months
```

## Decisions
- **Numerator (`cost` param): default `charge` — REVISIT.** The golden run showed `charge_amount`
  gives ~$13.3k PMPM (billed charges are inflated; not real cost). `paid_amount`,
  `allowed_amount`, and `total_cost_amount` **all exist** on `medical_claim` here. Confirm which
  is well-populated and switch the default to **`allowed`** (true cost) — exposing `paid`/`charge`
  via the param. (Population check: `SELECT COUNT(charge_amount), COUNT(paid_amount),
  COUNT(allowed_amount), COUNT(total_cost_amount) FROM tuva.medical_claim;`)
- **Denominator = member months** from the authoritative enrollment grain:
  - **`member_months`** = one row per person per enrolled month → the **full-month** count.
  - **`eligibility`** spans → **prorated** member-months (enrolled days / 30.44).
  - Governed default = **prorated** (actuarial); full-month via `basis = "fullmonth"`.

## Guardrails
- Never derive member-months from claims — use `member_months` / `eligibility`.
- ⚠️ **Prorated formula fixed (2026-06-08):** the original counted only the first month of each
  enrollment span (member_months 2,368 vs 31,184 fullmonth → PMPM 13× too high). Now sums the
  full span. Re-pin the prorated golden value.

## Validation
Golden-query test: `cost_pmpm` fullmonth/charge pinned at **$13,277.04** (member_months 31,184) on
the 2018 demo — see `validation/golden-queries.md`. Re-pin prorated after the fix and once the
numerator default is decided; alert on drift.
