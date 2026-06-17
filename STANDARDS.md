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
- **SAP Connected Health Platform (CHP)** — an enterprise clinical data warehouse model
  (SAP HANA). Map: Patient→person, Practitioner→practitioner, Organization→org/authorization,
  Observation→lab_result/observation, Condition→condition, **Interaction**→encounter (and any
  clinically-relevant event — diagnosis, therapy, contact). CHP stores interaction attributes
  **EAV-style** rather than as fixed columns (`notes/claim-grain.md`), every coded attribute as
  a **codification tuple** (`notes/coding-tuple.md`), member identity via a **Patient Best
  Record** (`notes/identity-resolution.md`), and **bi-temporal** validity. Use when a customer's
  warehouse is SAP/HANA-based or otherwise EAV-shaped.

## Why this matters
A payer's analysts think in **groupers and measures** (CCSR, HCC, HEDIS), not raw codes or
raw tables. Anchoring to these models lets us say "this maps to OMOP/FHIR/Tuva/SAP" and reuse
their public terminology — which is what makes the terminology layer (Layer 3) robust
instead of hand-rolled.

## Convergence — the same shape, four times over
These models were designed independently, yet agree on three structural choices. That agreement
is *why* the spine is portable, and each has a working note:

1. **A code is a tuple, not a column** — original value + standardized code + code system +
   version. Tuva `source/normalized`, FHIR `CodeableConcept`, OMOP `*_source_value`/`concept_id`,
   SAP `Codification`. → `notes/coding-tuple.md`.
2. **Member identity is resolved, not assumed** — many source ids collapse to one real person.
   Tuva `person_id_crosswalk`, SAP `Patient Best Record`, MDM/EMPI golden record. →
   `notes/identity-resolution.md`.
3. **Terminology is externalized** — codes resolve through a separate vocabulary/grouper layer
   (Athena, FHIR `system` URIs, SAP "ontology services", our `reference/terminology/`), not
   hard-coded in queries. → `notes/terminology-join-pattern.md`.

## Sources & citations
Full provenance — every standard and crosswalk above with a stable URL, pinned version, and
access date, plus the cross-reference showing our crosswalks share the **same** CMS / AHRQ / NLM
origins these models all sit on — is in **`SOURCES.md`**. Cite from there, not from memory.
