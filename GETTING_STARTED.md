# Getting Started — Healthcare & Life Sciences Ontology Starter

A step-by-step guide to standing up this ontology in **your own TextQL / Ana environment**,
connecting it to **your data**, and customizing it for **your organization** — written so you
don't need to be a healthcare-data expert to follow it. Budget ~half a day for steps 1–4.

---

## 1. What this is

An **ontology** is a shared, version-controlled definition of *how your organization thinks
about its data* — the business objects (members, claims, diagnoses), the metrics (cost PMPM,
readmission rate, risk score), and the rules (which codes mean "diabetes", who can see what).
It's **just files** (Markdown + `.tql`) in a git repo. Ana (TextQL's analyst agent) reads
these files and uses them to answer questions with **consistent, governed SQL** instead of
guessing.

This starter gives you a **pre-built healthcare ontology** so you don't begin from a blank
page:
- A **data backbone** (members, coverage, claims, encounters, diagnoses, procedures, drugs).
- **Governed metrics** (cost PMPM, 30-day readmission, disease prevalence, risk/RAF,
  utilization per 1,000, medication adherence, a quality-measure template).
- A **terminology layer** that turns raw medical codes (ICD-10, etc.) into meaningful groups
  (diabetes, heart failure, chronic conditions, risk categories) — the hard part, done for you.
- **Governance built in** (PHI handling, small-cell suppression, sensitive diagnoses).

## 2. Why it matters for healthcare & life-sciences organizations

- **Codes are unusable raw.** There are ~70,000 ICD-10 diagnosis codes. "How many members
  have diabetes?" isn't one code — it's a whole branch. The ontology encodes those groupings
  (using the public AHRQ/CMS standards) so every answer is consistent and defensible.
- **Everyone gets the same number.** "Readmission rate" or "PMPM" can be computed several
  ways. The ontology pins one **governed** definition (and keeps alternates visible but
  un-swappable), so Finance and Quality stop arguing about whose number is right.
- **Risk = revenue.** The risk-adjustment (HCC/RAF) surface is wired to the official CMS
  model — the metric that drives risk-adjusted payment for payers.
- **Compliance is the default, not an afterthought.** PHI minimum-necessary, the CMS <11
  small-cell suppression rule, and 42 CFR Part 2 sensitive-diagnosis gating are baked in.
- **It's yours and portable.** Plain files in your git, no proprietary lock-in. Branch it,
  diff it, review changes like code.

## 3. Set it up in your Ana environment

> **Prerequisites:** a TextQL/Ana workspace, a data warehouse connector (Redshift, BigQuery,
> Snowflake, …), and a git host (GitHub/GitLab/enterprise). A BAA must be in place before any
> PHI flows — see `ontology/notes/governance-phi.md`.

**Step 3.1 — Put the ontology in your git.**
```bash
# create your own private repo from this starter (do NOT fork into a public space)
git clone <this-starter-repo> my-org-ontology
cd my-org-ontology
git remote set-url origin <your-enterprise-git-url>
git push -u origin main
```

**Step 3.2 — Connect your warehouse to TextQL.** In TextQL, add the connector for the
warehouse holding your claims/clinical data. Note its **connector ID** and SQL **dialect**.

**Step 3.3 — Attach the ontology as Ana's context.** Point Ana at your repo (connect the git
repo in the TextQL workspace, or attach the folder). Ana reads `NAVIGATION.md` first, then
`config/org_context.md` for its operating rules.

**Step 3.4 — Load the public terminology crosswalks** (the groupers ICD-10 codes roll up to).
These are free/public-domain (AHRQ CCSR, CMS-HCC, CMS GEMs):
```bash
cd reference/terminology
pip install requests pandas
python load_terminology.py --download     # downloads + builds load-ready CSVs in ./_build
# stage ./_build/*.csv to your object storage, then run ./_build/load.sql in your warehouse
```
This creates a `terminology` schema your `.tql` joins to. (CCW chronic conditions ship as a
PDF — see `reference/terminology/chronic_conditions.md` for the one manual step.)

**Step 3.5 — (Optional) Hydrate certified value sets** for reportable quality measures. These
are license-gated, so you fetch them with *your own free UMLS key* (we never bundle them):
```bash
export UMLS_API_KEY=...        # free at https://uts.nlm.nih.gov
python fetch_vsac.py           # expands the OIDs in value-sets.json into your warehouse
```
See `reference/terminology/value-sets.md`. Skip this if you're only doing exploratory analysis.

**Step 3.6 — Validate against your data (the dry run).** Have Ana:
1. Pull the `information_schema` of your connector.
2. Compare your real table/column names to `databases/<schema>/tables/*.md`.
3. Fix any name mismatches in `ontology/schema.tql` (this is the one place table backings live).
4. Run the 10 checks in `validation/golden-queries.md` and fill in the expected values.
Follow the **First dry-run checklist** at the bottom of that file.

## 4. Customize it for your organization

Work through these in order; each is a small, reviewable pull request.

| # | Customize | Where | How |
|---|---|---|---|
| 1 | **Point at your tables** | `ontology/schema.tql` | Change the `let <name> = sql"..."` backings to your real schema/table names. Everything downstream follows. |
| 2 | **Set dialect + rules** | `config/org_context.md` | Your warehouse dialect, connector IDs, "current date", and any org-specific SQL rules. |
| 3 | **Confirm your metric definitions** | `ontology/notes/*.md` + `ontology/queries/*.tql` | Adopt or change the governed definition of each metric (e.g. cost = allowed vs charge). Record the decision in the note. |
| 4 | **Add your value sets** | `ontology/filters/diagnosis.tql` + `value-sets.json` | Replace the starter "diabetes/CHF/…" definitions with your authoritative ones; add OIDs for measures you report. |
| 5 | **Add your own metrics** | new `ontology/queries/<metric>.tql` + a note | Copy an existing surface as a template. |
| 6 | **Tighten governance** | `ontology/notes/governance-phi.md` | Add your org's RBAC, residency, and any stricter suppression. Never loosen the defaults. |
| 7 | **Document your sources** | `databases/<schema>/tables/*.md` | One short doc per table: columns, joins, gotchas. Ana reads these. |

### How you'll actually work day-to-day
1. A question comes in → Ana reads `NAVIGATION.md` → uses the right governed surface → answers.
2. A new document/policy arrives → make a **targeted edit** to the relevant note/surface →
   open a **focused PR** → review → merge. The ontology evolves continuously; you never
   "start over."

---

## Where to look next
- **`NAVIGATION.md`** — the routing table (start here, like Ana does).
- **`ontology/notes/diagnosis-coding.md`** — how ICD-10 codes resolve to groupers (the core idea).
- **`ontology/notes/governance-phi.md`** — the PHI rules you must keep.
- **`STANDARDS.md`** — how this maps to Tuva / OMOP / FHIR if your data follows one of those.
- **`LICENSING.md`** — what code sets are safe to share vs. fetch-with-your-own-license.

**Need help?** This starter is designed so a TextQL FDE can sit with your team for a half-day
workshop and have you running governed questions against your own data by the end.
