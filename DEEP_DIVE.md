# Deep Dive — everything in this ontology, and how it works

A technical tour for someone who wants to *really* understand what's been built: the
architecture, every layer and file, the terminology engine, the `.tql` language, how queries
actually execute, the governance model, and a full glossary of the acronyms. If `GETTING_STARTED.md`
is "how do I use it," this is "what is it, exactly, and why."

---

## 1. The core idea

An **ontology** here is a version-controlled description of *how this organization thinks about
its data*, expressed as plain files (Markdown + `.tql`) in a git repo. It has three jobs:

1. **Name the business objects** — Member, Claim, Encounter, Diagnosis, Procedure, Drug — and how
   they relate (the *entity spine*).
2. **Define the metrics** — what "cost PMPM" or "30-day readmission rate" precisely means, as one
   governed definition, so the same question always returns the same number.
3. **Encode the rules** — which ICD-10 codes mean "diabetes," who may see what, how to handle PHI.

**How Ana uses it.** When the repo is connected, Ana reads it as ground truth. A question like
"what's our readmission rate?" doesn't become a guess — Ana opens the governed surface
(`readmission_rate.tql`), renders it to warehouse SQL, runs it read-only, and shows the SQL it
used. The ontology is the difference between *probabilistic* text-to-SQL (hallucination-prone) and
*deterministic* generation from reviewed definitions.

**Why "just files."** Everything is diff-able, reviewable, and portable. Changes go through pull
requests like code: propose → diff → review → approve → audit. No proprietary store, no lock-in.

---

## 2. Repository map

```
README.md                 what this is + quick start
GETTING_STARTED.md        Ana-centric setup walkthrough (screenshots)
MIGRATION.md              re-point the starter at YOUR warehouse in 8 steps (+ field lessons)
DEEP_DIVE.md              this document
STANDARDS.md              alignment to Tuva / OMOP / FHIR / X12
LICENSING.md              which code systems are bundled vs. fetched-with-your-license
NAVIGATION.md             routing table — Ana reads this FIRST to map intent → files

config/
  org_context.md          Ana's system instructions: dialect, PHI rules, coding rules

ontology/
  schema.tql              ⭐ THE physical mapping layer — the ONLY file with real table names;
                          surfaces reference logical ${name} backings that resolve here
  relations/              one module per entity: source table + key columns + notes
    person.tql            member grain DERIVED from eligibility (no patient table exists)
    condition.tql         diagnosis fact
    procedure.tql         procedure fact
    encounter.tql         visit fact
    eligibility.tql       coverage / enrollment spans
    medical_claim.tql     medical claim lines
  dimensions/             grouping attributes, each with the join it needs
    diagnosis.tql         ⭐ the ICD-10 terminology layer (hierarchy + groupers)
    patient.tql           age band, state (sex/race/ethnicity unavailable in this data)
    procedure.tql         service-category / HCPCS / ICD-10-PCS rollups
    drug.tql              NDC / RxNorm / therapeutic class
    provider.tql          NPI / specialty / taxonomy
    time.tql              calendar rollups (month/quarter/year, rolling windows)
  filters/                reusable predicates
    compare.tql           eq/gte/lte/in/between/like, date_range
    diagnosis.tql         ⭐ 27 seed-free clinical value sets + grouper predicates
  queries/                governed query surfaces = the metrics
    cost_pmpm.tql, readmission_rate.tql, condition_prevalence.tql,
    comorbidity_profile.tql, utilization_per_1000.tql, rx_adherence_pdc.tql, hedis_measure.tql
  notes/                  decision records + rationale (the "why")
    diagnosis-coding.md, code-systems-overview.md, cost-definition.md,
    readmission-definition.md, risk-adjustment-hcc.md, governance-phi.md,
    terminology-join-pattern.md, glossary.md (override per deployment),
    claim-grain.md (header/line/event), join-key-verification.md

reference/terminology/    the grouper crosswalks (committed, public domain) + loaders
  icd10cm_chapters.csv     ICD-10 chapter/block ranges
  ccsr_icd10cm.csv         CCSR: 75,725 ICD-10-CM codes → clinical categories
  cmshcc_dx_hcc.csv        CMS-HCC: dx → HCC (8,299 rows)
  cmshcc_coefficients.csv  CMS-HCC: HCC/demographic RAF weights (1,237 rows)
  cmshcc_hierarchy.csv     CMS-HCC: trumping rules (149 rows)
  load_terminology.py      rebuilds the CSVs from AHRQ/CMS sources
  fetch_vsac.py            hydrates certified VSAC value sets with your UMLS key
  value-sets.json/.md      VSAC OID registry + the fetch-don't-bundle policy

databases/tuva/           the REFERENCE dataset's per-table docs (copy the shape for yours)
validation/               validate_tql.py (schema/compile checker), golden-queries.md
                          (pinned values), dry-run + seed-test playbooks
```

---

## 3. The six layers

### Layer 1 — Entity spine
The source-agnostic backbone. Default grain follows the **Tuva** healthcare data model; join key
is **`person_id`** everywhere. Entities: Member/Patient, Coverage/Enrollment, Medical Claim,
Pharmacy/Medication, Encounter/Visit, Diagnosis (Condition), Procedure, Lab/Observation, Provider.

Two realities this repo was validated against (live schema, 2026-06):
- **There is no `patient` table.** Person demographics live on `eligibility`
  (`birth_date`, `fips_state_abbreviation`); `sex`/`race`/`ethnicity` are absent. So the "person"
  entity is *derived* from eligibility (`relations/person.tql`) via
  `SELECT person_id, MIN(birth_date), MAX(fips_state_abbreviation) … GROUP BY person_id`.
- **Codes live in `normalized_code` / `normalized_code_type`** (Tuva normalizes the raw
  `source_code`), diagnosis rank is `condition_rank`, present-on-admission is `present_on_admit_code`.

### Layer 2 — Metrics (governed query surfaces)
Each `.tql` in `queries/` is one metric with a pinned definition. Detailed in §5.

### Layer 3 — Terminology
The heart of the system: turning ~70,000 ICD-10 codes into analyzable concepts via hierarchy and
groupers. Detailed in §6.

### Layer 4 — Governance & PHI
Fail-closed defaults baked into `config/org_context.md` and `notes/governance-phi.md`: small-cell
suppression (<11), HIPAA minimum-necessary, 42 CFR Part 2 sensitive-diagnosis gating. Detailed in §8.

### Layer 5 — Decision records
Every non-obvious choice is written down in `notes/` (e.g. *why* the CMS readmission definition is
the governed one, *which* grouper is canonical per question). These are what make the ontology
auditable rather than a black box.

### Layer 6 — Validation
`validation/golden-queries.md` pins known-correct values for each surface and lists invariants
(rates ∈ [0,1], all-cause ≥ CMS readmission, etc.). All 10 surfaces are verified on live data.

---

## 4. The entity spine in detail

| Entity | Backing (Tuva) | Grain | Key columns |
|---|---|---|---|
| Person/Member | derived from `eligibility` | 1 / person | person_id, birth_date, state |
| Coverage | `eligibility` | enrollment span | person_id, enrollment_start/end_date, payer, plan, dual_status_code |
| Member-months | `member_months` | 1 / person / month | person_id, year_month |
| Medical claim | `medical_claim` | claim line | person_id, charge/paid/allowed/total_cost_amount, claim_start/end_date |
| Encounter | `encounter` | visit | person_id, encounter_type, start/end_date, length_of_stay, drg_code, ed_flag |
| Diagnosis | `condition` | 1 / dx | person_id, normalized_code, normalized_code_type, condition_rank, present_on_admit_code, recorded_date |
| Procedure | `procedure` | 1 / proc | person_id, normalized_code, normalized_code_type, procedure_date |
| Pharmacy | `medication` | 1 / fill | person_id, dispensing_date, days_supply, rxnorm_code |
| Lab | `lab_result` | 1 / result | person_id, normalized_order_code (LOINC), result_datetime |

`schema.tql` is the **single place** these table names live — repoint a backing there and every
relation/dimension/query that imports it follows.

---

## 5. The metrics library

Every surface is a `params{} → let → sql''` definition. The pinned golden values below were
verified on the 1,000-member Tuva demo (current date 2018-12-31).

| Surface | What it computes | Key decision | Golden value |
|---|---|---|---|
| `cost_pmpm` | medical cost ÷ member-months | numerator: charge/allowed/paid/total (param); denominator: prorated (days/30.44) vs fullmonth | $13,277 fullmonth / $13,275 prorated (charge basis) |
| `readmission_rate` | unplanned inpatient readmit ≤30 days of discharge | governed = CMS-style; all-cause exposed separately, never silently swapped | 0.1221 (cms) |
| `condition_prevalence` | distinct members with a condition ÷ eligible | grouper = value_set / CCSR / chronic / HCC / prefix | diabetes value-set 0.446; CCSR END003 0.297 |
| `comorbidity_profile` | population/member RAF from HCCs | applies HCC **hierarchy trumping** + segment coefficients | mean RAF 0.680 (CNA, dx-portion) |
| `utilization_per_1000` | events ÷ member-months × 12000 | inpatient admits / ED visits / bed days | 167.0 inpatient admits/1000 |
| `rx_adherence_pdc` | proportion of days covered, % ≥0.80 | drug set via explicit RxNorm codes (seed-free) | n/a — `medication` empty in demo |
| `hedis_measure` | HbA1c testing in diabetics 18–75 (template) | eCQM/VSAC value sets preferred over HEDIS | 0.437 |

Notes that matter:
- **Cost magnitude.** $13k PMPM reflects *billed charges* (inflated). `paid`/`allowed`/`total_cost`
  exist; switch the `cost` param once population is confirmed. The denominator *bug* (prorated
  once counted only the first month → 13× undercount) is fixed; prorated now converges with
  fullmonth (31,188 vs 31,184 member-months).
- **RAF is the dx-driven HCC portion only.** The full CMS RAF adds demographic/age-sex and disease-
  interaction terms (present in the same coefficient file) — a documented hook, not yet summed.
  Hierarchy trumping *is* applied (287 HCC pairs removed in the demo run).

---

## 6. The terminology layer (the engine)

### Why it exists
No one analyzes raw ICD codes — there are ~70,000 of them. Analysts think in **hierarchy** (codes
roll up) and **groupers** (clinically/financially meaningful buckets). This layer encodes both so
Ana resolves "diabetes prevalence" deterministically to the right set of codes.

### The ICD-10-CM hierarchy
```
E11.9   Type 2 DM without complications      full code (most specific)
 └ E11   Type 2 diabetes mellitus             category   (3-char — the rollup unit)
    └ E08–E13  Diabetes block                 block      (alphabetic range)
       └ Chapter 4: Endocrine/metabolic       chapter    (E00–E89)
```
The 3-char category is a pure string op (`LEFT(REPLACE(code,'.',''),3)`); chapter/block come from
`icd10cm_chapters.csv` (a *range* lookup, since chapters are alphabetic spans like `A00`–`B99`).

### The groupers (all public domain, committed in `reference/terminology/`)
| Grouper | Maps | Used for | File |
|---|---|---|---|
| **CCSR** (AHRQ) | ICD-10-CM → ~530 clinical categories | "what condition" (the default) | `ccsr_icd10cm.csv` (75,725 rows) |
| **CMS-HCC** (CMS) | ICD-10-CM → HCC + RAF weight | risk / payment | `cmshcc_dx_hcc.csv`, `cmshcc_coefficients.csv`, `cmshcc_hierarchy.csv` |
| **CCW chronic** (CMS) | ICD-10-CM → 1 of 30 chronic flags | chronic cohorts | (build via loader) |
| **GEMs** (CMS) | ICD-9 ↔ ICD-10 | cross-cutover trends | (dormant; data is ICD-10-only) |

CCSR ships two mappings in one file: a **default** category (for principal-dx ranking, columns
`default_ccsr_ip`/`default_ccsr_op`) and a **multi-category** set (`ccsr_1`…`ccsr_6`, for
comorbidity coverage). HCC carries three files because RAF requires all three: the dx→HCC map, the
per-segment **coefficients** (e.g. `CNA_HCC92` = 0.479), and the **hierarchy** that *trumps* a
lower HCC when a more-severe one in the same family is present.

### The federated join — how terminology runs with ZERO warehouse writes
The crosswalks live in the repo, not the warehouse. When a surface needs a grouper, **Ana loads
the CSV into its Python sandbox and joins it to a read-only pull of the warehouse data in memory.**
No `CREATE`, no load, no schema change — the customer's warehouse stays strictly read-only.
Verified: all 212,864 conditions classified to a chapter, the full 75k-row CCSR join, and the HCC
hierarchy/coefficient pipeline all ran this way. See `notes/terminology-join-pattern.md`. (An
in-warehouse materialization via `load_terminology.py` + `load.sql` remains optional, for BI tools.)

### Value sets — the seed-free entry point
`filters/diagnosis.tql` defines **27 named clinical value sets** (diabetes, CHF, COPD, CKD,
hypertension, the CCW chronic conditions, four cancers, etc.) as **inline ICD-10 ranges** — so they
need no crosswalk at all and run on any connector. `value_set("diabetes")` → `LEFT(code,3) BETWEEN
'E08' AND 'E13'`. Sensitive sets (HIV, substance-use) are flagged for 42 CFR Part 2 gating. These
are *starter* definitions; for regulatory reporting, hydrate the certified **VSAC** set instead.

### Licensed terminology — fetch, don't bundle
CPT (AMA), SNOMED CT, LOINC, and certified VSAC value sets are license-gated. They are **modeled
structurally** (columns/joins exist) but never bundled. `fetch_vsac.py` hydrates VSAC value sets
into your environment using *your own* free UMLS API key (we commit only the OIDs). See `LICENSING.md`.

---

## 7. The `.tql` language

A `.tql` surface is a typed template that renders to native warehouse SQL. Four constructs:

- **`params { }`** — typed inputs with defaults and closed enums, e.g.
  `basis: Set<"prorated" | "fullmonth"> = ["prorated"]`. Closed enums prevent invalid calls.
- **`let`** — named bindings, including conditionals (`if x == null then … else …`).
- **`matchSet x { "k" -> sql"…" }`** — pattern-matches a param to a SQL fragment (how a metric
  switches between definitions, e.g. cms vs all_cause readmission).
- **`sql'' … ''`** — the rendered SQL body, with `${…}` interpolation of the bindings/params.

Dialect: authored **Redshift-first** (`DATEDIFF`, `NULLIF`, `x::DECIMAL`, `LEAST`, `LAST_DAY`), with
BigQuery equivalents noted inline (`DATE_DIFF`, `SAFE_DIVIDE`). A subtlety learned the hard way:
Redshift has **no `FILTER (WHERE …)`** on aggregates — use `SUM(CASE WHEN … THEN 1 ELSE 0 END)`.

---

## 8. Governance & PHI

Fail-closed defaults (in `config/org_context.md` + `notes/governance-phi.md`):
- **Small-cell suppression** — never report a cell with a member count < 11 (CMS standard);
  applies to subgroup breakdowns too (age × state × condition can re-identify).
- **Minimum necessary** — return only the fields needed; aggregates by default; never emit direct
  identifiers (name, MRN, full DOB, address) in outputs/charts/logs.
- **Sensitive diagnoses** — 42 CFR Part 2 (substance use) + HIV + behavioral health are gated;
  no member-level detail without explicit authorization.
- **De-identification** — the HIPAA Safe Harbor 18 identifiers are documented for reference.
- **Operating constraints** — BAA required before PHI flows; data residency; every change audited.
- **Read-only setup** — standing up the ontology requires no writes to the warehouse (terminology
  is joined in Python). This is both a security property and a deployment convenience.

---

## 9. How a question flows, end to end

1. **Question in** → Ana reads `NAVIGATION.md`, maps intent to a surface.
2. **Render** → the `.tql` compiles to warehouse SQL with the chosen params.
3. **Terminology** → if a grouper is needed, Ana joins the repo CSV in Python against a read-only pull.
4. **Execute** → read-only SQL against the warehouse.
5. **Govern** → small-cell suppression + minimum-necessary applied to the result.
6. **Answer** → result + the SQL used + which governed definition/grouper, so it's traceable.

To change something, you tell Ana in plain English; it makes a targeted edit and opens a PR you review.

---

## 10. Standards alignment (see `STANDARDS.md`)

- **Tuva** — the open-source claims+clinical data model this repo's grain follows; also the source
  of the terminology seed concepts.
- **OMOP CDM** (OHDSI) — research-grade common data model; Person→person, Visit→encounter,
  Condition→condition, Drug→medication, Procedure→procedure.
- **FHIR R4** — interoperability standard; Patient/Coverage/Claim/Encounter/Condition/MedicationRequest/Observation.
- **X12 837/835** — the EDI transactions claims arrive in; origin of POA, revenue/bill-type codes.

---

## 11. Acronym & term glossary

**Coding systems**
- **ICD-10-CM** — International Classification of Diseases, 10th rev., Clinical Modification. US
  diagnosis codes (~70K). Hierarchical: chapter → block → 3-char category → full code.
- **ICD-10-PCS** — Procedure Coding System; inpatient procedures (~78K).
- **ICD-9-CM** — the pre-2015-10-01 diagnosis/procedure code set (legacy).
- **GEMs** — General Equivalence Mappings; CMS crosswalk between ICD-9 and ICD-10 (frozen 2018).
- **HCPCS** — Healthcare Common Procedure Coding System (Level II); drugs/supplies/DME. "J-codes"
  (HCPCS starting with J) = physician-administered drugs.
- **CPT** — Current Procedural Terminology; AMA-licensed professional procedure codes.
- **NDC** — National Drug Code; FDA identifier for a specific drug product.
- **RxNorm / RxCUI** — NLM normalized drug naming; RxCUI is the concept id (this data uses `rxnorm_code`).
- **LOINC** — Logical Observation Identifiers Names and Codes; lab tests and observations.
- **SNOMED CT** — Systematized Nomenclature of Medicine, Clinical Terms; clinical findings/problems.
- **DRG / MS-DRG** — (Medicare Severity) Diagnosis-Related Group; inpatient payment grouping.
- **APC** — Ambulatory Payment Classification; outpatient payment grouping.
- **NPI** — National Provider Identifier. **NUCC taxonomy** — provider specialty code set.
- **FIPS** — Federal Information Processing Standards geographic codes (state/county).
- **POA** — Present On Admission; distinguishes a comorbidity from a complication (inpatient).

**Groupers & risk**
- **CCSR** — Clinical Classifications Software Refined (AHRQ); ICD-10-CM → ~530 clinical categories.
- **HCC** — Hierarchical Condition Category; the condition groups in CMS risk adjustment.
- **CMS-HCC** — CMS's HCC risk-adjustment model. **V28** is the current model version; **PY** = payment year.
- **RAF** — Risk Adjustment Factor; a member's relative expected cost (sum of HCC + demographic
  coefficients). Drives risk-adjusted payment.
- **CNA / CND / CFA / CFD / CPA / CPD / INS** — CMS-HCC rate *segments* (Community vs Institutional ×
  Non-dual/Full-dual/Partial-dual × Aged/Disabled). `CNA` = Community Non-dual Aged (the common default).
- **CCW** — Chronic Conditions Warehouse (CMS); publishes the 30 standard chronic-condition algorithms.
- **Elixhauser / Charlson** — comorbidity indices (academic/AHRQ).

**Measures & metrics**
- **PMPM / PMPY** — Per Member Per Month / Per Year; the standard cost-normalization unit.
- **Member-month** — one member enrolled for one month; the denominator for "per member" rates.
- **per 1,000** — utilization rate normalized to 1,000 members, annualized (events ÷ member-months × 12000).
- **Readmission (30-day)** — an inpatient admission within 30 days of a prior discharge.
- **PDC / MPR** — Proportion of Days Covered / Medication Possession Ratio; adherence (adherent ≥ 0.80).
- **HEDIS** — Healthcare Effectiveness Data and Information Set (NCQA); quality measures.
- **Star Ratings** — CMS quality/performance ratings for Medicare Advantage/Part D plans.
- **eCQM** — electronic Clinical Quality Measure (CMS); specs on the eCQI Resource Center.
- **VSAC** — Value Set Authority Center (NLM); the authoritative repository of measure value sets.
- **OID** — Object Identifier; the dotted id that names a VSAC value set (e.g. 2.16.840.1.113883…).
- **UMLS** — Unified Medical Language System (NLM); the license/key gating VSAC downloads.

**Data models & standards**
- **Tuva** — open-source healthcare claims+clinical data model (this repo's default grain).
- **OMOP CDM** — Observational Medical Outcomes Partnership Common Data Model (OHDSI).
- **FHIR** — Fast Healthcare Interoperability Resources (HL7); the API/interop standard.
- **X12 837 / 835** — EDI claim submission (837) and remittance (835) transactions.

**Privacy & governance**
- **PHI** — Protected Health Information (HIPAA).
- **HIPAA** — Health Insurance Portability and Accountability Act; "minimum necessary" + Safe Harbor.
- **BAA** — Business Associate Agreement; required before PHI may flow to a vendor.
- **42 CFR Part 2** — federal rule giving substance-use-disorder records heightened protection.
- **Small-cell suppression** — never reporting counts < 11 (CMS), to prevent re-identification.

**Platform / format**
- **Ana** — TextQL's analyst agent; reads this ontology, renders SQL, executes, answers.
- **`.tql`** — TextQL's typed, SQL-rendering query-surface language (params/let/matchSet/sql).
- **Governed surface** — a public, reviewed `.tql` metric definition (vs. ad-hoc SQL).
- **Federated join** — joining a repo CSV to warehouse data in Ana's Python sandbox (zero writes).

---

## 12. Validation status

All 10 governed surfaces verified on the live Tuva demo (1,000 members, CY2018), zero warehouse
writes. Pinned values and invariants are in `validation/golden-queries.md`. Headlines: readmission
0.1221, diabetes prevalence 0.446 (value-set) / 0.297 (CCSR END003), population mean RAF 0.680,
inpatient utilization 167/1,000, HbA1c testing 0.437, cost PMPM ~$13.3k (charge basis — switch to
allowed/paid for true cost). The `medication` table is empty in the demo, so the Rx-adherence
surface is logic-verified but unexercised.

---

## 13. Extending it

- **New metric** → copy a `queries/*.tql` as a template; add a `notes/*.md` decision record; PR it.
- **New condition cohort** → add a value set in `filters/diagnosis.tql` (seed-free) or a VSAC OID.
- **New data source** → add table backings in `schema.tql`, a relation module, and `databases/*` docs.
- **Tighten governance** → edit `notes/governance-phi.md`; never loosen the defaults without a
  reviewed, attributable decision.

Everything is a small, reviewable pull request. The ontology is meant to grow continuously — you
never start over.
