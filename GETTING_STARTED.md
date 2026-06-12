# Getting Started

This guide takes you from *"I have this ontology repo and nothing else"* to *"I'm asking Ana
governed questions about my own data"* — mostly without leaving the Ana chat window.

The whole idea: **you talk to Ana, Ana does the work.** You connect a few things once, then
everything else — exploring your data, validating the model, customizing metrics — happens by
asking Ana in plain English.

---

## What this is

An **ontology** is a shared definition of how your organization thinks about its data: the
business objects (members, claims, diagnoses), the metrics (cost PMPM, readmission rate, risk
score), and the rules (which codes mean "diabetes", who can see what). It's **just files**
(Markdown + `.tql`) in a git repo.

When you connect that repo to Ana, **Ana reads it and treats it as ground truth.** Ask
"what's our 30-day readmission rate?" and instead of guessing, Ana uses the governed
definition in the repo and writes the exact, consistent SQL every time.

## Why it matters for healthcare & life-sciences teams

- **Raw codes are unusable.** ~70,000 ICD-10 codes — "how many members have diabetes?" isn't
  one code, it's a whole branch. This ontology pre-maps those into meaningful groups (using
  the public AHRQ/CMS standards), so Ana answers consistently and defensibly.
- **Everyone gets the same number.** Metrics like PMPM and readmission can be computed several
  ways; the ontology pins one governed definition, so Finance and Quality stop disagreeing.
- **Risk = revenue.** The risk-adjustment (HCC/RAF) logic is wired to the official CMS model.
- **Compliance is the default.** PHI minimum-necessary, the CMS small-cell (<11) suppression
  rule, and sensitive-diagnosis gating are built in.

---

## Setup: three connections, then you're in Ana

### 1. Connect the ontology repo to Ana

This is the key step. In TextQL, add a **Git connector** (via the API connector) and point it
at this ontology repo. Because the ontology is git-backed, Ana now has the entire model —
every metric definition, every note, every coding rule — as a reference it reads on demand.

> 💡 You don't have to copy anything into Ana or maintain a second source of truth. Ana reads
> the repo live; when the repo changes, Ana sees the change.

### 2. Connect your data warehouse

Add the connector for the warehouse that holds your claims/clinical data (Redshift, BigQuery,
Snowflake, …). This is what Ana runs the governed SQL against. Read-only access is enough.

> ⚠️ A BAA must be in place before any PHI flows. Use your enterprise, BAA-covered warehouse —
> see `ontology/notes/governance-phi.md`.

### 3. (Optional) Bring in your own documents

The ontology is the structured core. Your real-world context — SOPs, metric definitions, plan
documents, policies — often lives in messy files. You have three easy ways to get them in front
of Ana, all without preprocessing:

- **Upload them directly** in the chat (PDF, Word, Excel, slides).
- **Connect Google Drive** and point Ana at a folder.
- **Connect SharePoint / OneDrive** for documents that live there.

Ana reads these alongside the ontology and can fold what it learns into the model (see
*Customizing*, below).

---

## Use it: just ask Ana

### 4. Validate the model against your data — REQUIRED before trusting any number

The ontology ships pointed at a reference dataset; your tables WILL differ (names, grain,
code values). Two complementary checks, both cheap:

**a) The validator script** — mechanically verifies every governed surface against your
warehouse: each logical name resolves, each referenced column exists, each query compiles.

```bash
python3 validation/validate_tql.py              # static checks, no warehouse needed
python3 validation/validate_tql.py --check-sql  # paste the output into Ana; rows = problems
```

**b) Ask Ana to do the discovery diff.** You don't write any SQL — just ask:

> **You:** *"Look at the ontology repo, then inspect my warehouse. Pull the information schema
> for my claims tables and tell me where the ontology's expected table and column names don't
> match what I actually have. Propose the exact changes to `ontology/schema.tql`."*

Ana will discover your schema, diff it against the ontology, and hand you a precise list of
fixes (table backings, column names). If anything's off, you just say *"make those changes and
open a pull request"* — Ana edits the files and opens a reviewable PR in your repo.

> There's a ready-made version of this check in `validation/dry-run-prompt.md` — you can paste
> it straight into Ana. The full re-point checklist (claim grain, join verification, governance
> tuning, glossary localization) is `MIGRATION.md`.

### 5. Terminology — already included, nothing to load

The terminology layer (the ICD-10 → diabetes / heart-failure / risk-category mappings, plus the
CMS-HCC risk model and CCSR clinical categories) **ships inside this repo** as public-domain
crosswalk files in `reference/terminology/`. When a question needs them, **Ana joins them in its
Python sandbox against a read-only pull of your data** — so your warehouse stays untouched: no
schema, no load, no writes.

That means grouper questions (disease prevalence by CCSR category, risk/RAF scores) just work
once the repo is connected. You only ever need a warehouse load if you specifically want the
crosswalks materialized for other BI tools — see `ontology/notes/terminology-join-pattern.md`.

### 6. Start asking questions

Now just talk to Ana. It routes every question through the governed definitions:

> *"What's our 30-day readmission rate for 2024?"*
> *"How many members have diabetes? Break it down by state."*
> *"Show me cost PMPM trend over the last 12 months."*
> *"What's our average risk (RAF) score, and which conditions drive it most?"*

Ana names which governed definition it used and shows the SQL — so every answer is traceable.

---

## Customize it for your company — by talking to Ana

You shape the ontology the same way you use it: in conversation. A few examples —

- **Adjust a metric definition:** *"We define cost using allowed amount, not charges. Update the
  cost PMPM definition and open a PR."*
- **Add a condition cohort:** *"Add a governed value set for COPD using our standard code list,"*
  then attach or point Ana at the list.
- **Fold in a new document:** upload a policy and say *"This is our updated readmission policy —
  update the readmission note and surface to match, and open a PR."*
- **Add your own metric:** *"Create a governed surface for ED visits per 1,000, like the existing
  utilization metric."*

In each case Ana makes a **targeted edit and opens a pull request** — a small, reviewable change
in your git. Nothing changes silently; you approve it like any code change.

### How it runs day-to-day
1. A question comes in → Ana reads the ontology → uses the right governed definition → answers.
2. A new document or policy arrives → you tell Ana → it makes a targeted edit → opens a PR →
   you review and merge. The ontology evolves continuously; you never start over.

---

## Where to look next
- **`MIGRATION.md`** — re-point the starter at your own warehouse in 8 steps (+ field lessons).
- **`DEEP_DIVE.md`** — a full technical tour: every file, every metric, every acronym. Read this
  if you want to *really* understand what's in here.
- **`NAVIGATION.md`** — the routing table Ana reads first.
- **`ontology/notes/diagnosis-coding.md`** — how ICD-10 codes resolve to groupers (the core idea).
- **`ontology/notes/governance-phi.md`** — the PHI rules that stay on by default.
- **`LICENSING.md`** — which code systems are bundled vs. fetched with your own license.

**Want a hand?** A TextQL FDE can sit with your team for a half-day and have you running
governed questions against your own data by the end.
