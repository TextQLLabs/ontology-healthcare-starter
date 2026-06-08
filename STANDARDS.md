# Standards this ontology stands on

This starter is deliberately aligned to the established healthcare data models so it's
credible to a customer's data team and portable across sources. The entity spine is a
least-common-denominator of these — you can map any of them onto it.

## Data models

- **Tuva Project** (open-source) — the default grain here. A claims+clinical data model
  with shipped **terminology** and **value-set** seeds (chronic conditions, CCSR, service
  categories, CMS-HCC). We reuse Tuva's seeds rather than rebuild crosswalks.
  → entity spine maps 1:1 to `patient`, `medical_claim`, `pharmacy_claim`, `encounter`,
  `condition`, `procedure`, `eligibility`, `member_months`.
- **OMOP CDM** (OHDSI) — research-grade common data model + standardized vocabularies
  (Athena). Map: Person→patient, Visit_occurrence→encounter, Condition_occurrence→condition,
  Drug_exposure→pharmacy_claim/drug, Procedure_occurrence→procedure. Concept_id ≈ our code
  dimensions. Use when the customer is research/RWE oriented.
- **FHIR R4** — interoperability/API standard. Map: Patient→patient, Coverage→eligibility,
  Claim/ExplanationOfBenefit→medical_claim, Encounter→encounter, Condition→condition,
  MedicationRequest/Dispense→pharmacy_claim, Observation→lab/observation.
- **X12 837 / 835** — the EDI transactions claims actually arrive in (837 = claim submission,
  835 = remittance). Header vs. line grain, dx pointers, POA, revenue/bill-type codes all
  originate here. Useful when modeling raw claims feeds.

## Why this matters
A payer's analysts think in **groupers and measures** (CCSR, HCC, HEDIS), not raw codes or
raw tables. Anchoring to these models lets us say "this maps to OMOP/FHIR/Tuva" and reuse
their public terminology — which is what makes the terminology layer (Layer 3) robust
instead of hand-rolled.

## Authoritative external references (free)
- ICD-10-CM/PCS files — CMS.gov / CDC NCHS
- CCSR — AHRQ HCUP
- HCC model — CMS (CMS-HCC risk adjustment model)
- CCW chronic conditions — CMS Chronic Conditions Warehouse
- RxNorm / UMLS — NLM
- Value sets for quality measures — VSAC (NLM)
