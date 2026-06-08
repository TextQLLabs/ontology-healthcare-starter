# Definition: Cost PMPM (per member per month)

**Status:** Adopted · **Surface:** `queries/cost_pmpm.tql` · **Owner:** Analytics CoE + Finance/Actuarial

## Metric
```
cost_pmpm = SUM(medical_claim.charge_amount) / member_months
```

## Decisions
- **Numerator = `charge_amount`.** In the Tuva model, `paid_amount` / `allowed_amount` are
  **sparsely populated** — use `charge_amount` for cost. (When a customer has reliable
  `paid`/`allowed`, prefer `allowed` for true cost and expose `paid` separately.)
- **Denominator = member months** from the authoritative enrollment grain:
  - **`member_months`** = one row per person per enrolled month → the **full-month** count.
  - **`eligibility`** spans → **prorated** member-months by days enrolled.
  - Governed default = **prorated** (actuarial); full-month via `basis = "fullmonth"`.

## Guardrails
- Never derive member-months from claims — use `member_months` / `eligibility`.
- Confirm `eligibility` column names on the dry run.

## Validation
Golden-query test: pin `cost_pmpm` for a known month once the basis is fixed; alert on drift.
