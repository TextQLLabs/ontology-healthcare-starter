# Run the golden queries (end-to-end)

Paste these into Ana against the **Tuva Redshift** connector, treat the current date as
**2018-12-31**, and paste the result rows back. Each block is the SQL the governed surface
renders with its **default params** (Redshift dialect). Then fill the Expected column in
`golden-queries.md` and assert the invariants at the bottom.

## Prerequisites
- **Q1–Q5, Q8** run on the raw `tuva` schema — **no seeds needed**.
- **Q6, Q7** need the terminology seeds loaded (`load_terminology.py` → `terminology.*`).
- **Q9, Q10** are **pending column confirmation** (`medication`, `lab_result`) — templates only.

---

## Q1 — cost_pmpm (basis=prorated)  ← FIXED formula (full span / 30.44)
```sql
SELECT
  SUM(mc.charge_amount) AS total_charge,
  (SELECT SUM((DATEDIFF('day', e.enrollment_start_date,
        COALESCE(e.enrollment_end_date, DATE '2018-12-31')) + 1) / 30.44)
   FROM tuva.eligibility e) AS member_months,
  SUM(mc.charge_amount)::DECIMAL
   / NULLIF((SELECT SUM((DATEDIFF('day', e.enrollment_start_date,
        COALESCE(e.enrollment_end_date, DATE '2018-12-31')) + 1) / 30.44)
        FROM tuva.eligibility e), 0) AS cost_pmpm
FROM tuva.medical_claim mc;
```
> The earlier formula counted only the first month of each span (member_months came back 2,368
> vs 31,184 fullmonth → PMPM 13× too high). This sums the full enrolled span. To use a real-cost
> numerator instead of billed charges, swap `mc.charge_amount` → `mc.allowed_amount` (or `paid`/`total_cost`).

## Q2 — cost_pmpm (basis=fullmonth)
```sql
SELECT
  SUM(mc.charge_amount) AS total_charge,
  (SELECT COUNT(*) FROM tuva.member_months) AS member_months,
  SUM(mc.charge_amount)::DECIMAL / NULLIF((SELECT COUNT(*) FROM tuva.member_months), 0) AS cost_pmpm
FROM tuva.medical_claim mc;
```

## Q3 — readmission_rate (definition=cms)
```sql
WITH index_adm AS (
  SELECT e.person_id, e.encounter_id, e.encounter_end_date AS discharge_date
  FROM tuva.encounter e
  WHERE e.encounter_type = 'acute inpatient'
),
flagged AS (
  SELECT i.encounter_id,
         MAX(CASE WHEN r.encounter_id IS NOT NULL THEN 1 ELSE 0 END) AS readmitted
  FROM index_adm i
  LEFT JOIN tuva.encounter r
    ON  r.person_id = i.person_id
    AND r.encounter_type = 'acute inpatient'
    AND r.encounter_start_date > i.discharge_date
    AND DATEDIFF('day', i.discharge_date, r.encounter_start_date) <= 30
  GROUP BY i.encounter_id
)
SELECT COUNT(*) AS index_admissions,
       SUM(readmitted) AS readmissions,
       SUM(readmitted)::DECIMAL / NULLIF(COUNT(*), 0) AS readmission_rate_30d
FROM flagged;
```

## Q4 — readmission_rate (definition=all_cause)
> **Currently identical to Q3.** The CMS variant's transfer exclusion is a documented
> follow-up. Now feasible: `tuva.encounter` has `discharge_disposition_code` — exclude index
> admissions/readmissions flagged as transfers to make `cms < all_cause`. Until then, Q4 = Q3.

## Q5 — condition_prevalence (grouper=value_set, concept=diabetes)  ← no seeds needed
```sql
WITH cohort AS (
  SELECT DISTINCT c.person_id
  FROM tuva.condition c
  WHERE c.normalized_code_type = 'icd-10-cm'
    AND LEFT(REPLACE(c.normalized_code, '.', ''), 3) BETWEEN 'E08' AND 'E13'
),
denom AS (SELECT COUNT(DISTINCT person_id) AS members FROM tuva.eligibility)
SELECT (SELECT COUNT(*) FROM cohort) AS members_with_condition,
       d.members AS eligible_members,
       (SELECT COUNT(*) FROM cohort)::DECIMAL / NULLIF(d.members, 0) AS prevalence_rate
FROM denom d;
```

## Q6 — condition_prevalence (grouper=ccsr, concept=END003)  ← needs CCSR seed
```sql
WITH cohort AS (
  SELECT DISTINCT c.person_id
  FROM tuva.condition c
  JOIN terminology.ccsr_icd10cm cx ON cx.icd10cm_code = REPLACE(c.normalized_code, '.', '')
  WHERE c.normalized_code_type = 'icd-10-cm'
    AND (cx.default_ccsr_ip = 'END003' OR cx.default_ccsr_op = 'END003')   -- a diabetes CCSR cat; verify exact code in the loaded file
),
denom AS (SELECT COUNT(DISTINCT person_id) AS members FROM tuva.eligibility)
SELECT (SELECT COUNT(*) FROM cohort) AS members_with_condition,
       d.members AS eligible_members,
       (SELECT COUNT(*) FROM cohort)::DECIMAL / NULLIF(d.members, 0) AS prevalence_rate
FROM denom d;
```

## Q7 — comorbidity_profile (level=population, segment=CNA, CY2018)  ← needs CMS-HCC seeds
```sql
WITH member_hccs AS (
  SELECT DISTINCT c.person_id, x.hcc
  FROM tuva.condition c
  JOIN terminology.cmshcc_dx_hcc x ON x.icd10cm_code = REPLACE(c.normalized_code, '.', '')
  WHERE c.normalized_code_type = 'icd-10-cm'
    AND c.recorded_date BETWEEN DATE '2018-01-01' AND DATE '2018-12-31'
),
trumped AS (
  SELECT mh.person_id, mh.hcc AS excluded_hcc
  FROM member_hccs mh
  JOIN terminology.cmshcc_hierarchy h ON h.excluded_hcc = mh.hcc
  JOIN member_hccs sup ON sup.person_id = mh.person_id AND sup.hcc = h.superior_hcc
),
surviving_hccs AS (
  SELECT mh.person_id, mh.hcc
  FROM member_hccs mh
  LEFT JOIN trumped t ON t.person_id = mh.person_id AND t.excluded_hcc = mh.hcc
  WHERE t.excluded_hcc IS NULL
),
hcc_raf AS (
  SELECT s.person_id, SUM(co.coeff::DECIMAL) AS hcc_raf
  FROM surviving_hccs s
  JOIN terminology.cmshcc_coefficients co ON co.segment = 'CNA' AND co.hcc = s.hcc
  GROUP BY s.person_id
)
SELECT AVG(hcc_raf) AS mean_raf, COUNT(*) AS members FROM hcc_raf;
```
> If `members` = 0, the HCC keys didn't join — confirm `cmshcc_dx_hcc.hcc`,
> `cmshcc_coefficients.hcc`, and `cmshcc_hierarchy` are all **bare integers** (the loader
> normalizes them; re-run it if you loaded an older build).

## Q8 — utilization_per_1000 (metric=inpatient_admits)
```sql
SELECT
  SUM(CASE WHEN e.encounter_type = 'acute inpatient' THEN 1 ELSE 0 END) AS events,
  (SELECT COUNT(*) FROM tuva.member_months) AS member_months,
  SUM(CASE WHEN e.encounter_type = 'acute inpatient' THEN 1 ELSE 0 END)::DECIMAL
    / NULLIF((SELECT COUNT(*) FROM tuva.member_months), 0) * 12000 AS per_1000_annualized
FROM tuva.encounter e;
```

## Q9 — rx_adherence_pdc (seed-free; pass RxNorm codes)  ← columns confirmed
`medication` columns: `dispensing_date` (date), `days_supply` (VARCHAR → cast), `rxnorm_code`.
Replace the example RxNorm list with your real drug set.
```sql
WITH fills AS (
  SELECT m.person_id,
         LEAST(CAST(m.days_supply AS INTEGER),
               DATEDIFF('day', m.dispensing_date, DATE '2018-12-31') + 1) AS covered_days
  FROM tuva.medication m
  WHERE m.dispensing_date BETWEEN DATE '2018-01-01' AND DATE '2018-12-31'
    AND m.rxnorm_code IN ('860975','861007','899993')          -- example antidiabetics; swap in yours
),
member_pdc AS (
  SELECT person_id,
         LEAST(SUM(covered_days)::DECIMAL / NULLIF(365, 0), 1.0) AS pdc
  FROM fills GROUP BY person_id
)
SELECT COUNT(*) AS members_measured,
       AVG(pdc) AS mean_pdc,
       SUM(CASE WHEN pdc >= 0.80 THEN 1 ELSE 0 END)::DECIMAL / NULLIF(COUNT(*),0) AS pct_adherent
FROM member_pdc;
```

## Q10 — hedis_measure (HbA1c, diabetics 18–75)  ← columns confirmed
`lab_result`: `normalized_component_code` (LOINC), `result_datetime` (timestamp).
```sql
WITH person AS (SELECT person_id, MIN(birth_date) AS birth_date FROM tuva.eligibility GROUP BY person_id),
denom AS (
  SELECT DISTINCT c.person_id
  FROM tuva.condition c JOIN person p ON p.person_id = c.person_id
  WHERE c.normalized_code_type = 'icd-10-cm'
    AND LEFT(REPLACE(c.normalized_code,'.',''),3) BETWEEN 'E08' AND 'E13'
    AND c.recorded_date BETWEEN DATE '2018-01-01' AND DATE '2018-12-31'
    AND DATEDIFF('year', p.birth_date, DATE '2018-12-31') BETWEEN 18 AND 75
),
numer AS (
  SELECT DISTINCT l.person_id
  FROM tuva.lab_result l
  WHERE l.normalized_component_code IN ('4548-4','17856-6')     -- HbA1c LOINC
    AND CAST(l.result_datetime AS DATE) BETWEEN DATE '2018-01-01' AND DATE '2018-12-31'
)
SELECT (SELECT COUNT(*) FROM denom) AS eligible,
       (SELECT COUNT(*) FROM denom d WHERE d.person_id IN (SELECT person_id FROM numer)) AS met,
       (SELECT COUNT(*) FROM denom d WHERE d.person_id IN (SELECT person_id FROM numer))::DECIMAL
         / NULLIF((SELECT COUNT(*) FROM denom),0) AS measure_rate;
```

---

## Invariants (assert after running)
- Q5/Q6 `prevalence_rate` ∈ [0, 1].
- Q4 `readmission` ≥ Q3 (equal until the transfer exclusion lands).
- Q1 `cost_pmpm` (prorated) ≥ Q2 (fullmonth)  — prorated denominator is smaller.
- Q7 `mean_raf` ≥ 0; `members` > 0.
- Every externally-reported count cell ≥ 11 (else suppress) — `notes/governance-phi.md`.

## Record back
Paste each block's result here or into `golden-queries.md`; I'll pin the Expected values and
flip Status → verified.
