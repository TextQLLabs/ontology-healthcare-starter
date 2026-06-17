# ana.md — context routing for the healthcare ontology

This file tells Ana **how context is organized in this workspace and where to read or write each
kind.** It is the substrate every other context file hangs off of. Read it before answering;
it sits above `NAVIGATION.md` (which routes *questions → governed surfaces*), while this routes
*context → the layer it belongs in*.

## The three layers

1. **ORG (shared, governed)** — applies to *everyone* in the organization. Enterprise
   definitions, the governed metric/grouper logic, coding rules, and PHI policy.
   - Location: `config/org_context.md` (agent instructions + CONFIG) · `ontology/` (the model
     itself) · `ontology/notes/` (decision records, `glossary.md`, grain/identity/coding guides).
   - Change process: **reviewed PR** — an admin approves. Never edited casually. This is the
     same discipline as code (`governance-phi.md` §6: propose → review → approve → audit).
2. **PERSONA / ROLE (shared within a function, governed)** — applies to everyone in a role:
   the lens, default rollups, and which surfaces/definitions that function leans on.
   - Location: `behaviors/<role>/org_context.md` (create per deployment).
   - Examples for a payer: `actuarial`, `care_management`, `quality_hedis`, `network`,
     `business_analyst`, `admin`. Two roles may share identical connector scope and differ only
     in behavior — that's expected; behavior binds 1:1 to the RBAC role.
   - Change process: **reviewed PR**.
3. **PERSONAL (individual, immediate)** — applies only to one user: their preferences and tweaks.
   - Location: `users/<email-local-part>.context.md` (create per deployment).
   - Change process: **immediate, private**. Promote to a persona or ORG via PR once it turns
     out to be shared.

## Routing rules (where does a new piece of context belong?)

- An enterprise definition (PMPM basis, the governed readmission definition, a value set, the
  canonical grouper for a question) → **ORG**. One governed copy; personas never fork it.
- A whole function's lens or standard rollups (e.g. "actuarial always trends PMPM on allowed,
  by segment") → **that role's persona**.
- One person's preference or shortcut → **their personal file**.
- **Decision rule:** *Everyone? → ORG. A whole function? → persona. Just me? → personal.*

## Data & definition routing

- **A governed surface exists for the question → use it** (`NAVIGATION.md` → `ontology/queries/`).
  Render the SQL, name the surface/grouper/definition, then the result.
- **No surface yet → discover** (`information_schema`), confirm against `databases/<schema>/`,
  draft, and propose adding a surface via PR. Never free-hand a metric that ORG already defines.
- **Terminology** resolves through `ontology/dimensions/diagnosis.tql` + `reference/terminology/`
  — never hand-guessed codes. Name the grouper **and its version** (`notes/coding-tuple.md`).
- When two definitions exist (CMS vs all-cause readmission; charge vs allowed cost), name the
  governed one and flag that the other exists — never silently swap.

## Personal-context write target

- When a user says "remember this for me" / "save my preference," write to
  `users/<email-local-part>.context.md` and confirm the exact path. Do **not** write personal
  preferences into ORG or persona files.

## Governance note (PHI-aware)

- Users without context-update rights can still propose changes: tell Ana "update this in
  context," and Ana opens a **PR** for a workspace admin to review. Few people hold direct ORG
  update rights, to avoid conflicts and uphold the audit trail.
- Context files are **definitions and policy, never PHI.** No member-level data, identifiers, or
  query outputs go in any layer here (`ontology/notes/governance-phi.md` §0/§2). Personal files
  hold preferences, not patient data.

## Map

```
ana.md                       ← this file: the three layers + routing (read first)
config/org_context.md        ← ORG: agent instructions, CONFIG (min_cell_size…), PHI rules
ontology/                    ← ORG: the governed model (schema, relations, queries, dimensions)
  notes/                       ← ORG: glossary, coding-tuple, identity-resolution, claim-grain, PHI
behaviors/<role>/org_context.md  ← PERSONA: one folder per role (create per deployment)
users/<user>.context.md          ← PERSONAL: individual prefs (Ana writes here)
NAVIGATION.md                ← question → governed surface routing (complements this file)
```
