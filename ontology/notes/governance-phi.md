# Governance & PHI — fail-closed rules for healthcare data

**Status:** Adopted · **Owner:** Privacy/Compliance + Data Governance · **Enforced via:** `config/org_context.md`

These are **non-negotiable defaults**. A customer branch can tighten them, never loosen them
without a reviewed, attributable decision.

## 1. Small-cell suppression (the one that bites most)
Never report a cell whose member/patient count is **< 11**. Show `<11` or suppress the row.
This is the CMS cell-suppression standard and applies to **every** count/rate output,
including subgroup breakdowns (age × state × condition can re-identify). Suppress
complementary cells too if a total + one subgroup lets you back out a suppressed cell.

## 2. Minimum necessary (HIPAA)
Return only the fields needed to answer. Default to **aggregates**; member-level detail
requires an explicit, authorized reason. Never emit direct identifiers (name, MRN, full DOB,
full address, phone, email, SSN, member ID) in outputs, charts, or logs.

## 3. Sensitive diagnoses — extra gating
- **42 CFR Part 2** — substance use disorder records have heightened federal protection.
- Also gate: **HIV/AIDS, behavioral/mental health, reproductive/sexual health, genetic.**
Do not surface member-level detail for these categories without explicit authorization; in
aggregate, apply suppression strictly (these subgroups are small and re-identifiable).

## 4. De-identification reference (HIPAA Safe Harbor)
The 18 identifiers that must be removed for a data set to be "de-identified": names; geographic
subdivisions smaller than state (incl. ZIP, except first 3 digits per rules); all date elements
finer than year (except year) for dates related to an individual, and ages > 89; phone/fax;
email; SSN; MRN; health-plan beneficiary #; account #; certificate/license #; vehicle/device
IDs; URLs; IPs; biometric IDs; full-face photos; any other unique identifier.

## 5. Operating constraints (payers)
- **BAA required** before any PHI flows. No consumer cloud drives (Google/personal). Use the
  customer's enterprise, BAA-covered storage.
- **Data residency** — keep data in the contracted region; don't move PHI across boundaries.
- **Audit** — every governed change is proposed → reviewed → approved → audited (like code).

## 6. Health-equity reporting
Race/ethnicity dimensions exist (`dimensions/patient.tql`) for disparity analysis — surface
**only in aggregate**, with suppression, per an approved health-equity reporting standard.
