# Governance & PHI — fail-closed rules for healthcare data

**Status:** Adopted (TEMPLATE — tune §0 and the thresholds to YOUR compliance regime) ·
**Owner:** Privacy/Compliance + Data Governance · **Enforced via:** `config/org_context.md`

These are **non-negotiable defaults**. A deployment branch can tighten them, never loosen them
without a reviewed, attributable decision. The starter ships conservative settings because any
real claims warehouse is member-grain PHI; your compliance team sets the final values for
HIPAA Safe Harbor / Expert Determination, state rules, and internal policy.

## 0. Direct-identifier inventory (fill in per warehouse)

Inventory every direct identifier in the connected schema on day one (dry-run step), then
classify each into exactly one role:

| Identifier (typical columns) | Role | Rule |
|---|---|---|
| member/patient/subscriber/beneficiary IDs (`member_id`, `subscriber_id`, `mbi`, `mrn`) | **JOIN KEY ONLY** | May appear in `ON`/`WHERE`/`GROUP BY` internals; **never in an output column, chart, label, or log** |
| names (member, subscriber, dependent, guarantor) | **NEVER OUTPUT** | Not needed for analytics; exclude from any SELECT list |
| SSN, full DOB, phone, email, full address | **NEVER OUTPUT** | DOB may be used *internally* for age math; only age/age-band leaves |
| ZIP code | **AGGREGATE ONLY** | First 3 digits max (Safe Harbor), and only when the 3-digit area > 20,000 people |
| internal surrogate keys (`person_id` in the reference data) | join key; output only in authorized member-level work | Surrogate ≠ safe: stable pseudonyms are still identifiers under re-identification risk |

**Using an identifier as a join key is not the same as outputting it.** The surfaces in this
repo join on `person_id` everywhere and output it nowhere except the explicitly member-level
views (`comorbidity_profile level="member"`), which require authorization per §2.

## 1. Small-cell suppression (the one that bites most)

Never report a cell whose member/patient count is **< `min_cell_size`**. Show `<{n}` or
suppress the row.

> **`min_cell_size` = 11** (starter default — the CMS cell-suppression standard).
> Configure in `config/org_context.md`; common alternatives: 10 (several state agencies),
> 30 (some internal policies). Tighten freely; loosening below 11 needs Compliance sign-off.

Applies to **every** count/rate output, including subgroup breakdowns (age × state ×
condition can re-identify). Suppress complementary cells too if a total + one subgroup lets
you back out a suppressed cell.

## 2. Minimum necessary (HIPAA) — default to aggregate

Return only the fields needed to answer. **Default to aggregates**; member-level detail
requires an explicit, authorized reason recorded in the thread. Never emit direct identifiers
(§0) in outputs, charts, or logs.

## 3. Sensitive diagnoses — extra gating

- **42 CFR Part 2** — substance use disorder records have heightened federal protection.
- Also gate: **HIV/AIDS, behavioral/mental health, reproductive/sexual health, genetic.**
Do not surface member-level detail for these categories without explicit authorization; in
aggregate, apply suppression strictly (these subgroups are small and re-identifiable).

## 4. Re-identification risk — socioeconomic & geographic joins

Member-level joins to socioeconomic/SDOH data (income, housing, census tract, race/ethnicity
imputation) can **re-identify small groups even in aggregate output**: a rare condition × a
small geography × an income band may describe one person. Before adding any such join:
- require an approved purpose (e.g. a health-equity reporting standard),
- aggregate the socioeconomic attribute to the coarsest level that answers the question,
- apply `min_cell_size` on the **cross-product** of every grouping dimension, and
- prefer area-level (census tract and coarser) attributes over person-level ones.

## 5. De-identification reference (HIPAA Safe Harbor)

The 18 identifiers that must be removed for a data set to be "de-identified": names; geographic
subdivisions smaller than state (incl. ZIP, except first 3 digits per rules); all date elements
finer than year (except year) for dates related to an individual, and ages > 89; phone/fax;
email; SSN; MRN; health-plan beneficiary #; account #; certificate/license #; vehicle/device
IDs; URLs; IPs; biometric IDs; full-face photos; any other unique identifier.

## 6. Operating constraints (payers)

- **BAA required** before any PHI flows. No consumer cloud drives (Google/personal). Use the
  customer's enterprise, BAA-covered storage.
- **Data residency** — keep data in the contracted region; don't move PHI across boundaries.
- **Audit** — every governed change is proposed → reviewed → approved → audited (like code).

## 7. Health-equity reporting

Race/ethnicity dimensions, where available (`dimensions/patient.tql`), exist for disparity
analysis — surface **only in aggregate**, with suppression and the §4 safeguards, per an
approved health-equity reporting standard.
