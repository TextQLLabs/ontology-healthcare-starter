# Glossary — canonical claims terms (OVERRIDE PER DEPLOYMENT)

**Status:** Starter defaults · **Owner:** the deploying team — edit the *Your definition*
column to your org's reality and keep the structure.

The durable asset here is the **pattern**: one canonical business term → one governed
definition → one place it resolves in this repo. The *specific* vocabulary below is a starter
that differs across lines of business — the LOB notes flag where commercial, Medicare, and
Medicaid deployments most often diverge. When a term means something different at your org,
change it HERE (and in the linked note), not ad hoc in a thread.

| Term | Starter definition | Resolves via | LOB variance to check |
|---|---|---|---|
| **Member** | A covered individual; grain = `person_id` on `${person_grain}`. Distinct from *subscriber* (contract holder) and *patient* (clinical context). | `relations/person.tql` | Medicaid: churn makes "member" time-dependent — always pair with an enrollment window. Medicare: beneficiary ≈ subscriber. Commercial: dependents share a subscriber id + person code. |
| **Member month** | One member enrolled for one month; THE denominator for PMPM/per-1000. Prorated (days/30.44) vs full-month bases are both governed. | `relations/eligibility.tql` · `notes/cost-definition.md` | Medicaid: retroactive eligibility rewrites history — pin a snapshot date. Commercial: ASO vs fully-insured populations are often reported separately. |
| **Claim** | An adjudicated bill for services; in the reference data, line grain with header columns flattened on. Counting claims = counting headers. | `relations/medical_claim.tql` · `notes/claim-grain.md` | Transactional warehouses split header/line/event — see the grain note before any count. Medicare FFS vs MA encounter data differ in completeness. |
| **Encounter / visit** | A unit of care contact (admission, ED visit, office visit), distinct from the claim(s) that pay for it. | `relations/encounter.tql` | The claim↔encounter linkage varies wildly; verify it (`notes/join-key-verification.md`). Capitated/Medicaid MCO data may have encounters with $0 claims. |
| **Charge amount** | What was billed. Inflated relative to real cost everywhere; default cost basis ONLY because it's the most-populated column in the reference data. | `notes/cost-definition.md` | Switch the governed cost basis to **allowed** (commercial norm) or **paid** once population is confirmed (dry-run Q5). |
| **Allowed amount** | The contractually negotiated price (plan liability + member liability). The usual "cost" in commercial analytics. | `cost_pmpm.tql` `cost` param | Medicare: fee schedule ≈ allowed. Medicaid: allowed may equal paid (no member liability). Sparsely populated in some feeds — verify before defaulting. |
| **Denial** | A claim/line adjudicated not-payable. NOT modeled as a flag in the reference data — locate it before use (header status? event code? remark codes?). | `notes/claim-grain.md` | Denial semantics differ by LOB and by warehouse (soft vs hard denial, reversal vs adjustment). Document where it lives in `databases/<yourschema>/`. |
| **Prescriber** | The provider who wrote the prescription (pharmacy fact), distinct from **rendering** (performed the service, line grain) and **billing** (paid, header grain) providers. | `dimensions/provider.tql` | Which NPI lands in which column varies by feed; verify with a known provider before attribution analyses. |
| **Formulary tier** | Plan-assigned drug cost-sharing level. NOT in the reference data — a plan/benefit join the deployer supplies. | declare a backing in `schema.tql` | Medicare Part D: standardized tier model + coverage phases. Commercial: tier counts/names are plan-specific. Medicaid: often a PDL (preferred/non-preferred), not tiers. |
| **Therapeutic category** | Drug class rollup (e.g. antidiabetics). Resolve via RxNorm ATC or a licensed classification (Medi-Span/FDB) — never string-match drug names. | `dimensions/drug.tql` | Class systems differ (ATC vs USP vs proprietary); name which one a number used. USP classes are the Part D formulary-adequacy standard. |
| **Risk score (RAF)** | Sum of HCC coefficients for a member under a CMS-HCC model year + segment. | `queries/comorbidity_profile.tql` · `notes/risk-adjustment-hcc.md` | Model version matters (V24 vs V28 differ materially). Commercial uses HHS-HCC, Medicaid often CDPS — same pattern, different crosswalk. |
| **Readmission** | CMS-style: unplanned admit within 30 days of an acute inpatient discharge. All-cause exposed separately, never silently swapped. | `queries/readmission_rate.tql` · `notes/readmission-definition.md` | Planned-readmission + transfer exclusions are spec'd differently by program (HRRP vs HEDIS PCR vs state Medicaid). |

## How to override

1. Edit the row here (or add one) with your org's definition; put the long-form reasoning in
   the linked `notes/*.md`.
2. If the term is backed by data, point its backing in `schema.tql` and verify with
   `validation/validate_tql.py`.
3. Treat the change like code: PR, review, merge. Ana picks it up on the next read.
