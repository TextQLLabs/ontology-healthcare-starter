# The coding tuple — original value + code + system + **version**

**Status:** Adopted · **Applies to:** every coded column (`condition`, `procedure`, `medication`,
`lab_result`) and every terminology join · **Sources:** `SOURCES.md`

Every clinical concept in a warehouse is really a **tuple**, not a single column. Four
independent healthcare data models converge on the same four parts — strong evidence this is the
right shape, not a Tuva quirk:

| Part | Tuva (our default) | FHIR R4 `CodeableConcept` | OMOP CDM | SAP CHP "Codification" |
|---|---|---|---|---|
| the human/original value | `source_code` | `text` | `*_source_value` | `<attr>.OriginalValue` |
| the standardized code | `normalized_code` | `coding.code` | `concept_id` (+ `*_source_concept_id`) | `<attr>.Code` |
| which code **system** | `normalized_code_type` | `coding.system` (URI) | `vocabulary_id` | `<attr>.CodingSystem` (VocabularyID, e.g. `ots.ICD.ICD10CM`) |
| the system **version** | *(only `source_version` on the crosswalk)* | `coding.version` | `vocabulary.vocabulary_version` | `<attr>.CodingVersion` |

Read the table top-to-bottom before trusting a coded column: confirm which physical columns
carry the original vs. the normalized value, and **never group on the original** — group on the
normalized code through `dimensions/diagnosis.tql`. (This is the same "don't filter raw codes"
rule, stated structurally: the raw value is `source_code`, the safe value is `normalized_code`.)

## The gap this surfaces: code-system **version**

The starter tracks the system (`normalized_code_type = 'icd-10-cm'`) but **not its version** on
the fact row — and FHIR, OMOP, and SAP CHP all carry a version slot we don't fill. That's fine
until it isn't, and here's when it bites:

- **ICD-10-CM is re-issued every fiscal year.** Codes are added, retired, and (rarely) reused.
  A multi-year claims warehouse spans several editions; a code valid in FY2019 may not exist in
  FY2024. Grouping all years through one crosswalk silently drops the codes that edition didn't
  know about.
- **Groupers are versioned independently of the codes.** **CMS-HCC V24 vs V28** assign
  different HCCs and weights to the *same* dx — RAF is not comparable across versions (already
  flagged in `risk-adjustment-hcc.md`). **CCSR** is re-released (we pin **v2026.1**); category
  membership shifts between editions.
- **The crosswalk and the data must agree on era.** Our `reference/terminology/*.csv` each carry
  a `source_version` column (see `reference/terminology/README.md`) — that is the crosswalk's
  version. The unverified half is the **data's** version: which ICD-10-CM edition coded these
  claims?

### What to do (cheap, no schema change required)

1. **Find the data's code era** during discovery — min/max service date already bounds it; if a
   `code_system_version` / `icd_version` column exists, inventory it:
   ```sql
   SELECT normalized_code_type, COUNT(*) , MIN(recorded_date), MAX(recorded_date)
   FROM <schema>.condition GROUP BY 1 ORDER BY 2 DESC;
   ```
2. **Match the crosswalk edition to the data's span**, or accept and **document** the mismatch
   (e.g. "V28 weights applied to V24-era claims — intentional for comparability; see golden-queries").
3. **If the warehouse carries a version column, map it** — declare a backing in `schema.tql`
   and prefer it over the date heuristic. If it doesn't, say so in `databases/<schema>/` rather
   than assume one edition.
4. **Always name the grouper version** in an answer that depends on it (RAF, CCSR prevalence) —
   the same discipline as naming the metric definition. A RAF number without "V28" is unfooted.

> Rule of thumb: **system without version is a half-citation.** When a number could move between
> editions, the version is part of the answer, not metadata.
