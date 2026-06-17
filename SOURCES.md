# Sources — citation index

Every external standard, crosswalk, and data model this ontology stands on, with a stable URL,
the version we built against, and when we last checked it. **`LICENSING.md`** governs what may
be redistributed; this file is about *provenance* — where each fact came from, so any number is
traceable to an authority. Cite from here (not from memory) whenever a definition is questioned.

> Access dates reflect the last verification pass (**2026-06-17**). Versioned artifacts
> (CCSR v2026.1, CMS-HCC V28, GEMs 2018) are pinned; re-check the others on each refresh.

## Code systems (vocabularies)

| System | Authority | Source URL | Version pinned |
|---|---|---|---|
| ICD-10-CM | CDC NCHS / CMS | https://www.cms.gov/medicare/coding-billing/icd-10-codes | annual (FY) |
| ICD-10-PCS | CMS | https://www.cms.gov/medicare/coding-billing/icd-10-codes/icd-10-pcs | annual (FY) |
| ICD-9-CM + GEMs | CMS | https://www.cms.gov/medicare/coding-billing/icd-10-codes/icd-10-cm-pcs-gem | 2018 final (frozen) |
| HCPCS Level II | CMS | https://www.cms.gov/medicare/coding-billing/healthcare-common-procedure-system | quarterly |
| NDC | FDA | https://www.fda.gov/drugs/drug-approvals-and-databases/national-drug-code-directory | rolling |
| RxNorm / RxCUI | NLM | https://www.nlm.nih.gov/research/umls/rxnorm/ | monthly |
| LOINC | Regenstrief | https://loinc.org/ | semiannual *(license — structural only)* |
| SNOMED CT | SNOMED Intl / NLM (US ed.) | https://www.nlm.nih.gov/healthit/snomedct/ | semiannual *(UMLS license — structural only)* |
| CPT | AMA | https://www.ama-assn.org/practice-management/cpt | annual *(licensed — structural only)* |
| NUCC provider taxonomy | NUCC | https://nucc.org/index.php/code-sets-mainmenu-41/provider-taxonomy-mainmenu-40 | semiannual |
| MS-DRG | CMS | https://www.cms.gov/medicare/payment/prospective-payment-systems/acute-inpatient-pps/ms-drg-classifications-and-software | annual (FY) |
| FIPS (geography) | US Census / NIST | https://www.census.gov/library/reference/code-lists/ansi.html | rolling |

## Groupers / crosswalks (the analytic layer we ship)

| Grouper | Authority | Source URL | Version pinned |
|---|---|---|---|
| CCSR (ICD-10-CM → clinical categories) | AHRQ HCUP | https://hcup-us.ahrq.gov/toolssoftware/ccsr/dxccsr.jsp | **v2026.1** |
| CMS-HCC (dx→HCC, coefficients, hierarchy) | CMS | https://www.cms.gov/medicare/health-plans/medicareadvtgspecratestats/risk-adjustors | **V28 / PY2026** |
| CCW chronic conditions (30) | CMS Chronic Conditions Warehouse | https://www2.ccwdata.org/web/guest/condition-categories-chronic | ICD-10 era |
| VSAC certified value sets (HEDIS/eCQM) | NLM VSAC | https://vsac.nlm.nih.gov/ | fetch-with-your-UMLS-key |

## Data models (what the spine is portable across)

| Model | Steward | Source URL | Role here |
|---|---|---|---|
| Tuva Project | Tuva Health (open source) | https://thetuvaproject.com/ · https://github.com/tuva-health/tuva | **Default grain.** `normalized_code`/`source_code` convention + shipped terminology seeds. |
| OMOP CDM | OHDSI | https://ohdsi.github.io/CommonDataModel/ | Research/RWE mapping target; Athena vocabularies. |
| HL7 FHIR R4 | HL7 | https://hl7.org/fhir/R4/ | Interoperability/API mapping target; `CodeableConcept`. |
| X12 837 / 835 | ASC X12 | https://x12.org/codes | The EDI transactions claims arrive in (header/line grain origin). |
| SAP Connected Health Platform — Clinical Data Modeling Guide | SAP SE | https://help.sap.com/docs/SAP_CONNECTED_HEALTH_PLATFORM (data-modeling guide PDF: https://help.sap.com/doc/f68fbeeec12d439ca35367e8ed8eebef/1.0.3/en-US/SAP_Connected_Health_Data_Modeling_Guide.pdf) | Enterprise clinical-warehouse mapping target; codification tuple, EAV interactions, Patient Best Record, bi-temporal validity. |

## Are we hitting the same sources? (the cross-reference)

**Yes — by design, not coincidence.** The independent data models above don't supply *rival*
terminology; they all sit on the **same public authorities** we cite directly:

- **Tuva's** terminology seeds (CCSR, CMS-HCC, CCW, RxNorm) are repackaged **AHRQ / CMS / NLM**
  files — the exact rows in our `reference/terminology/*.csv`. We reuse Tuva's *packaging*, but
  the origin is the authority, so our crosswalks and a Tuva-native warehouse agree by construction.
- **OMOP** standardizes through Athena, which **ingests** ICD-10-CM (CDC/CMS), RxNorm (NLM),
  SNOMED (NLM US edition) — same files, re-keyed to `concept_id`.
- **FHIR** `CodeableConcept.coding.system` URIs (e.g. `http://hl7.org/fhir/sid/icd-10-cm`,
  `http://www.nlm.nih.gov/research/umls/rxnorm`) are **pointers to** these same authorities.
- **SAP CHP** "ontology services" resolve a `VocabularyID` such as `ots.ICD.ICD10CM` — i.e.
  the **same ICD-10-CM** from CMS/CDC, wrapped in SAP's vocabulary registry.

So a code grouped by our CCSR crosswalk, by Tuva's seed, by an OMOP `concept_ancestor`, or by
SAP's ontology service traces to **one** authoritative definition. The convergence is the point:
it's what lets the spine be portable and lets us defend a number to a customer's data team. Where
two models could legitimately differ (e.g. **CMS-HCC V24 vs V28**, **CCSR annual editions**),
that difference is a *version*, not a *source* — which is exactly why version is pinned in the
tables above and discussed in `ontology/notes/coding-tuple.md`.
