# Decision: One Governed 30-Day Readmission Rate

**Status:** Adopted · **Owner:** Clinical Quality + Finance/Actuarial · **Surface:** `queries/readmission_rate.tql`

## Context
"30-day readmission rate" gets computed two ways and the numbers diverge:
- **Quality:** **all-cause**, any inpatient readmit within 30 days; no planned exclusion.
- **Finance/Actuarial:** **unplanned**, excludes transfers/same-day rebills; CMS-HRRP-style.

## Decision
Adopt the **CMS-style** measure as the governed `readmission_rate_30d` (`definition="cms"`):
unplanned inpatient readmission within 30 days of an index acute-inpatient discharge,
excluding transfers. Aligns with external/quality reporting; the defensible definition.

## Rejected alternative (kept, renamed)
The **all-cause** rate stays useful for operations/outreach and is exposed via the same
surface under `definition="all_cause"` so it can never be silently substituted.

## Guardrails
- Index = `encounter_type='acute inpatient'` discharge; join next acute-inpatient admit for
  the same `person_id`; window strictly `>0 and <=30` days.
- Planned-readmission exclusion needs a planned/elective flag or DRG mapping — follow-up if
  not directly available in the data.
- Confirm `encounter_type` values + encounter date columns on the dry run.

## Validation
Golden-query test: pin `readmission_rate_30d` (cms) for CY2018; alert on drift.
