#!/usr/bin/env python3
"""validate_tql.py — validate the ontology's .tql surfaces BEFORE trusting them on a warehouse.

What it catches (each of these is a real, observed migration-bug class):
  * a ${ref} that resolves to nothing (typo'd logical name, missing schema.tql backing)
  * a column referenced on the wrong alias/table (the header-vs-line grain trap)
  * a table or column that simply doesn't exist on the target warehouse
  * a query that no longer compiles after re-pointing (via EXPLAIN / LIMIT-0)

Modes (composable):
  python validation/validate_tql.py                       # static checks only (no warehouse needed)
  python validation/validate_tql.py --render              # + print each query rendered with default params
  python validation/validate_tql.py --manifest            # + print the table->column requirements (JSON)
  python validation/validate_tql.py --check-sql           # + emit ONE information_schema SQL check
                                                          #   (paste it into Ana; FAILs come back as rows)
  python validation/validate_tql.py --columns-csv f.csv   # offline check against a column dump
                                                          #   (CSV: table_schema,table_name,column_name)
  python validation/validate_tql.py --dsn DSN [--driver psycopg2] [--explain]
                                                          # live check + compile test per query

Exit code 0 = all checks passed; 1 = failures (suitable for CI).

Conventions this validator enforces (see ontology/schema.tql header):
  * physical names live ONLY in schema.tql; every surface uses ${logical} refs
  * ${ref} resolution order: file-local let > params > lambda args > schema.tql backing
  * federated terminology backings (default schema `terminology`) are satisfied by repo CSVs
    in reference/terminology/ when not materialized in the warehouse
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCHEMA_TQL = REPO / "ontology" / "schema.tql"
TERMINOLOGY_DIR = REPO / "reference" / "terminology"
FEDERATED_SCHEMAS = {"terminology"}  # backings here may live as repo CSVs, not warehouse tables

SQL_KEYWORDS = {
    "select", "from", "join", "left", "right", "inner", "outer", "cross", "on", "where",
    "and", "or", "not", "in", "as", "with", "group", "order", "by", "having", "limit",
    "case", "when", "then", "else", "end", "between", "like", "is", "null", "distinct",
    "union", "all", "exists", "date", "interval", "cast",
}


# ── parsing ──────────────────────────────────────────────────────────────────

def strip_comments(text: str) -> str:
    return re.sub(r"--[^\n]*", "", text)


def parse_lets(text: str) -> dict:
    """All `name = <expr>` bindings in a .tql (top-level `let x =` and let-block entries)."""
    out = {}
    clean = strip_comments(text)
    # multi-line aware: capture from `name =` to the start of the next binding / `in sql` / EOF
    pattern = re.compile(
        r"(?:^|\n)\s*(?:let\s+)?([a-z_][a-z0-9_]*)\s*=\s*(.+?)(?=\n\s*(?:let\s+)?[a-z_][a-z0-9_]*\s*=|\nin\s|\Z)",
        re.S,
    )
    for m in pattern.finditer(clean):
        name, expr = m.group(1), m.group(2).strip()
        if name in ("params",):
            continue
        out[name] = expr
    return out


def parse_params(text: str) -> dict:
    """params { name: Type = default } -> {name: {"type":..., "default": python value}}."""
    m = re.search(r"params\s*\{(.*?)\}", strip_comments(text), re.S)
    if not m:
        return {}
    out = {}
    # a param line: name: Type [= default]   (Type may contain <...> incl. multi-line Sets)
    for pm in re.finditer(
        r"([a-z_][a-z0-9_]*)\s*:\s*((?:Set<[^>]*>|List<[^>]*>|String\??|Int|Bool|Float))\s*(?:=\s*([^\n]+))?",
        m.group(1), re.S,
    ):
        name, ptype, default = pm.group(1), " ".join(pm.group(2).split()), pm.group(3)
        value = None
        if default is not None:
            d = default.strip()
            if d.startswith("["):  # Set/List default — take the literal list
                value = re.findall(r'"([^"]*)"', d)
                if ptype.startswith("Set"):
                    value = value[0] if value else None  # default arm of a matchSet
            elif d.startswith('"'):
                value = d.strip('"')
            elif d in ("true", "false"):
                value = d == "true"
            else:
                try:
                    value = int(d)
                except ValueError:
                    value = d
        out[name] = {"type": ptype, "default": value}
    return out


def parse_lambda_args(text: str) -> set:
    """Names bound by lambda heads:  (a: String, b: Int) ->"""
    args = set()
    for m in re.finditer(r"\(([^()]*?)\)\s*->", strip_comments(text)):
        for part in m.group(1).split(","):
            part = part.strip()
            am = re.match(r"([a-z_][a-z0-9_]*)\s*:", part)
            if am:
                args.add(am.group(1))
    return args


def parse_schema_backings() -> dict:
    text = SCHEMA_TQL.read_text()
    out = {}
    for m in re.finditer(r'^\s*let\s+([a-z_][a-z0-9_]*)\s*=\s*sql"(.+)"\s*$',
                         strip_comments(text), re.M):
        out[m.group(1)] = m.group(2)
    return out


# ── rendering (queries only) ─────────────────────────────────────────────────

def sql_literal(value, ptype: str) -> str:
    if isinstance(value, list):
        return ", ".join("'%s'" % v for v in value)
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    return "'%s'" % value


def eval_let(expr: str, params: dict):
    """Evaluate one let expression to its sql"" body (string) using default params.
    Handles the three idioms used in this repo: plain sql, if/else, matchSet."""
    expr = expr.strip()
    m = re.match(r'^sql"(.*)"$', expr, re.S) or re.match(r"^sql'''?(.*?)'''?$", expr, re.S)
    if m:
        return m.group(1)
    m = re.match(r'^sql"""(.*)"""$', expr, re.S)
    if m:
        return m.group(1)
    # if <param> == null then A else B   |   if <param> then A else B
    m = re.match(r"^if\s+([a-z_][a-z0-9_]*)\s*(==\s*null)?\s*then\s+(sql\"[^\"]*\")\s+else\s+(sql\"[^\"]*\")",
                 expr, re.S)
    if m:
        name, isnull, then_e, else_e = m.groups()
        p = params.get(name, {})
        cond = (p.get("default") is None) if isnull else bool(p.get("default"))
        return eval_let(then_e if cond else else_e, params)
    # matchSet <param> { "k" -> sql"..." ... }
    m = re.match(r"^matchSet\s+([a-z_][a-z0-9_]*)\s*\{(.*)\}\s*$", expr, re.S)
    if m:
        name, body = m.groups()
        key = params.get(name, {}).get("default")
        arms = dict(re.findall(r'"([^"]+)"\s*->\s*sql"((?:[^"\\]|\\.)*)"', body))
        if key in arms:
            return arms[key]
        if arms:
            return next(iter(arms.values()))
    return None  # unsupported shape -> caller flags it


def substitute(sql: str, lets: dict, params: dict, backings: dict, errors: list, fname: str,
               depth: int = 0) -> str:
    if depth > 8:
        errors.append(f"{fname}: ${{...}} substitution exceeded depth 8 (cycle?)")
        return sql

    def repl(m):
        name = m.group(1)
        if name in lets and lets[name] is not None:
            return lets[name]
        if name in params:
            return sql_literal(params[name]["default"], params[name]["type"])
        if name in backings:
            return backings[name]
        errors.append(f"{fname}: unresolved reference ${{{name}}}")
        return m.group(0)

    new = re.sub(r"\$\{([a-z_][a-z0-9_]*)\}", repl, sql)
    if new != sql and "${" in new:
        return substitute(new, lets, params, backings, errors, fname, depth + 1)
    return new


def render_query(path: Path, backings: dict, errors: list):
    text = path.read_text()
    m = re.search(r"\bin\s+sql''(.*)''", strip_comments(text), re.S)
    if not m:
        return None  # not a full query surface (relation/dimension/filter)
    params = parse_params(text)
    raw_lets = parse_lets(text)
    lets = {}
    for name, expr in raw_lets.items():
        body = eval_let(expr, params)
        if body is not None:
            # lets may themselves contain ${param}/${backing}/${other-let} refs
            lets[name] = body
    rendered = substitute(m.group(1), lets, params, backings, errors, path.name)
    if "${" in rendered:
        for ref in sorted(set(re.findall(r"\$\{([a-z_][a-z0-9_]*)\}", rendered))):
            errors.append(f"{path.name}: could not render ${{{ref}}} (unsupported let shape?)")
    return rendered.strip()


# ── static reference check (all .tql) ────────────────────────────────────────

def static_check(path: Path, backings: dict) -> list:
    text = path.read_text()
    errors = []
    local = set(parse_lets(text)) | set(parse_params(text)) | parse_lambda_args(text)
    # comments may sketch optional join recipes (${rxnorm_atc} etc.) — only check live code
    for ref in set(re.findall(r"\$\{([a-z_][a-z0-9_]*)\}", strip_comments(text))):
        if ref not in local and ref not in backings:
            errors.append(f"{path.relative_to(REPO)}: ${{{ref}}} resolves to no let/param/backing")
    return errors


# ── manifest: table -> columns actually referenced ───────────────────────────

def build_manifest(rendered: str, fname: str, warnings: list) -> dict:
    """Map physical table -> set(columns) from a rendered query. CTE/subquery aliases are
    resolved to their projection when parseable, else skipped with a warning."""
    cte_names = set(re.findall(r"(?:WITH|,)\s*([a-z_][a-z0-9_]*)\s+AS\s*\(", rendered, re.I))
    alias_to_table = {}
    cte_aliases = set(cte_names)
    # FROM/JOIN <schema.table> <alias>
    for m in re.finditer(
        r"\b(?:FROM|JOIN)\s+([a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*)\s+(?:AS\s+)?([a-z_][a-z0-9_]*)\b",
        rendered, re.I,
    ):
        table, alias = m.group(1).lower(), m.group(2).lower()
        if alias not in SQL_KEYWORDS:
            alias_to_table[alias] = table
    # FROM/JOIN <cte_name> <alias> — alias of a CTE, nothing physical to check
    for m in re.finditer(
        r"\b(?:FROM|JOIN)\s+([a-z_][a-z0-9_]*)\s+(?:AS\s+)?([a-z_][a-z0-9_]*)\b", rendered, re.I,
    ):
        if m.group(1).lower() in cte_names and m.group(2).lower() not in SQL_KEYWORDS:
            cte_aliases.add(m.group(2).lower())
    # FROM/JOIN (subquery) alias — e.g. ${person_grain}; paren-balanced scan for the alias
    for m in re.finditer(r"\b(?:FROM|JOIN)\s+\(", rendered, re.I):
        depth, i = 1, m.end()
        while i < len(rendered) and depth:
            depth += {"(": 1, ")": -1}.get(rendered[i], 0)
            i += 1
        am = re.match(r"\s+(?:AS\s+)?([a-z_][a-z0-9_]*)\b", rendered[i:], re.I)
        if am and am.group(1).lower() not in SQL_KEYWORDS:
            alias_to_table[am.group(1).lower()] = f"<subquery:{fname}>"

    manifest = {}
    for m in re.finditer(r"\b([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\b", rendered):
        alias, col = m.group(1).lower(), m.group(2).lower()
        if alias in cte_aliases or alias in SQL_KEYWORDS:
            continue
        table = alias_to_table.get(alias)
        if table is None:
            # qualified schema.table tokens themselves match this regex — ignore those
            if f"{alias}.{col}" in alias_to_table.values() or alias in {
                t.split(".")[0] for t in alias_to_table.values() if "." in t
            }:
                continue
            warnings.append(f"{fname}: alias `{alias}` not bound to a table (CTE? lateral?) — skipped")
            continue
        if table.startswith("<subquery"):
            continue
        manifest.setdefault(table, set()).add(col)
    return manifest


# ── checks against information_schema ────────────────────────────────────────

def emit_check_sql(manifest: dict) -> str:
    """One portable SQL statement: returns a row per MISSING table/column. Zero rows = pass."""
    selects = []
    for table, cols in sorted(manifest.items()):
        schema, tname = table.split(".", 1)
        for col in sorted(cols):
            selects.append(
                f"SELECT '{table}' AS expected_table, '{col}' AS expected_column\n"
                f"WHERE NOT EXISTS (SELECT 1 FROM information_schema.columns\n"
                f"  WHERE table_schema = '{schema}' AND table_name = '{tname}' AND column_name = '{col}')"
            )
    return "\nUNION ALL\n".join(selects) + ";"


def load_columns_csv(path: Path) -> set:
    have = set()
    with open(path, newline="") as f:
        for row in csv.reader(f):
            row = [c.strip().lower() for c in row if c.strip()]
            if len(row) >= 3:
                have.add((f"{row[0]}.{row[1]}", row[2]))
            elif len(row) == 2:
                have.add((row[0], row[1]))
    return have


def check_federated_csv(table: str, cols: set) -> list:
    """Terminology backings: check the repo CSV header instead of the warehouse."""
    errors = []
    tname = table.split(".", 1)[1]
    csv_path = TERMINOLOGY_DIR / f"{tname}.csv"
    if not csv_path.exists():
        return [f"  note: {table} — no warehouse table required (federated), but no repo CSV "
                f"`reference/terminology/{tname}.csv` either; hydrate or load before using it"]
    with open(csv_path, newline="") as f:
        header = {c.strip().lower() for c in next(csv.reader(f))}
    for col in sorted(cols):
        if col not in header:
            errors.append(f"  FAIL: {csv_path.name} lacks column `{col}`")
    return errors


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--render", action="store_true", help="print rendered SQL per query")
    ap.add_argument("--manifest", action="store_true", help="print table->column manifest (JSON)")
    ap.add_argument("--check-sql", action="store_true", help="emit information_schema check SQL (paste into Ana)")
    ap.add_argument("--columns-csv", help="offline check against a column dump CSV")
    ap.add_argument("--dsn", help="live DB-API DSN/connection string")
    ap.add_argument("--driver", default="psycopg2", help="DB-API module for --dsn (default psycopg2)")
    ap.add_argument("--explain", action="store_true", help="with --dsn: EXPLAIN-compile each rendered query")
    args = ap.parse_args()

    backings = parse_schema_backings()
    errors, warnings = [], []

    # 1. static ${ref} resolution across every .tql
    tql_files = sorted((REPO / "ontology").rglob("*.tql"))
    for path in tql_files:
        if path == SCHEMA_TQL:
            continue
        errors.extend(static_check(path, backings))

    # 2. render query surfaces + build the column manifest
    manifest, rendered_queries = {}, {}
    for path in sorted((REPO / "ontology" / "queries").glob("*.tql")):
        rendered = render_query(path, backings, errors)
        if rendered is None:
            warnings.append(f"{path.name}: no `in sql''` block — skipped render")
            continue
        rendered_queries[path.name] = rendered
        for table, cols in build_manifest(rendered, path.name, warnings).items():
            manifest.setdefault(table, set()).update(cols)

    if args.render:
        for name, sql in rendered_queries.items():
            print(f"\n──── {name} (defaults) ────\n{sql}")

    if args.manifest:
        print(json.dumps({t: sorted(c) for t, c in sorted(manifest.items())}, indent=2))

    warehouse_manifest = {t: c for t, c in manifest.items()
                          if t.split(".")[0] not in FEDERATED_SCHEMAS}
    federated_manifest = {t: c for t, c in manifest.items()
                          if t.split(".")[0] in FEDERATED_SCHEMAS}

    # 3. federated terminology — verify against repo CSVs
    for table, cols in sorted(federated_manifest.items()):
        for line in check_federated_csv(table, cols):
            (errors if line.strip().startswith("FAIL") else warnings).append(line.strip())

    # 4. information_schema checks
    if args.check_sql:
        print("\n-- Paste into Ana / your SQL client. Every returned row is a MISSING column.")
        print(emit_check_sql(warehouse_manifest))

    if args.columns_csv:
        have = load_columns_csv(Path(args.columns_csv))
        bare = {t.split(".", 1)[1] for t, _ in have if "." in t} | {t for t, _ in have}
        for table, cols in sorted(warehouse_manifest.items()):
            for col in sorted(cols):
                if (table, col) not in have and (table.split(".", 1)[1], col) not in have:
                    errors.append(f"missing on warehouse: {table}.{col}")

    if args.dsn:
        import importlib
        driver = importlib.import_module(args.driver)
        conn = driver.connect(args.dsn) if args.driver != "psycopg2" else driver.connect(args.dsn)
        cur = conn.cursor()
        for table, cols in sorted(warehouse_manifest.items()):
            schema, tname = table.split(".", 1)
            cur.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = %s AND table_name = %s", (schema, tname))
            have = {r[0].lower() for r in cur.fetchall()}
            if not have:
                errors.append(f"missing table: {table}")
                continue
            for col in sorted(cols - have):
                errors.append(f"missing column: {table}.{col}")
        if args.explain:
            for name, sql in rendered_queries.items():
                try:
                    cur.execute(f"EXPLAIN {sql}")
                    print(f"compile OK: {name}")
                except Exception as e:  # noqa: BLE001 — report and continue
                    conn.rollback()
                    errors.append(f"compile FAIL: {name}: {e}")
        conn.close()

    # ── report ──
    warnings = list(dict.fromkeys(warnings))
    errors = list(dict.fromkeys(errors))
    for w in warnings:
        print(f"⚠️  {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"❌ {e}", file=sys.stderr)
        print(f"\n{len(errors)} failure(s).", file=sys.stderr)
        sys.exit(1)
    print(f"✅ {len(tql_files) - 1} .tql files checked; "
          f"{len(rendered_queries)} queries rendered; "
          f"{sum(len(c) for c in manifest.values())} column refs across {len(manifest)} tables.")


if __name__ == "__main__":
    main()
