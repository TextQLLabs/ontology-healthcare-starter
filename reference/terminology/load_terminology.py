#!/usr/bin/env python3
"""
load_terminology.py — download + normalize the authoritative, PUBLIC-DOMAIN US healthcare
terminology crosswalks this ontology depends on, and emit warehouse-ready CSVs (+ COPY SQL).

Public domain (17 U.S.C. §105) — safe to load and use. Sources & versions verified 2026-06.
NOTE: licensed value sets (VSAC / HEDIS) are NOT here — see fetch_vsac.py + value-sets.md.

What it produces (in --out, default ./_build):
  ccsr_icd10cm.csv        terminology.ccsr_icd10cm      (CCSR v2026.1)
  cmshcc_dx_hcc.csv       terminology.cmshcc_dx_hcc      (CMS-HCC V28, PY2026)
  cmshcc_coefficients.csv terminology.cmshcc_coefficients
  cmshcc_hierarchy.csv    terminology.cmshcc_hierarchy   (parsed from the SAS %SET0 macro)
  gem_icd9_icd10.csv      terminology.gem_icd9_icd10     (GEMs 2018 final)
  load.sql                Redshift COPY statements (edit the S3 path / IAM role)

Usage:
  pip install requests pandas
  python load_terminology.py --download            # fetch + build everything
  python load_terminology.py --download --only ccsr cmshcc
  # CCW chronic conditions are PDF-only (see chronic_conditions.md) — handled separately.

Codes are ALWAYS strings (leading zeros, sentinels). Every table carries a source_version.
"""
from __future__ import annotations
import argparse, io, os, re, sys, zipfile

# cms.gov rejects default UAs — present a browser UA.
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

SOURCES = {
    "ccsr": {
        "version": "ccsr_v2026.1",
        "url": "https://hcup-us.ahrq.gov/toolssoftware/ccsr/DXCCSR-v2026-1.zip",
        "member": "DXCCSR_v2026-1.csv",      # 75,725 rows; code fields wrapped in single quotes
    },
    "cmshcc_map": {
        "version": "cmshcc_v28_py2026",
        "url": "https://www.cms.gov/files/zip/2026-midyear-final-icd-10-mappings.zip",
        "member": "2026 Final ICD-10-CM Mappings.csv",   # title rows at top; per-model HCC columns
    },
    "cmshcc_software": {
        "version": "cmshcc_v28_py2026",
        "url": "https://www.cms.gov/files/zip/2026-midyear-final-model-software.zip",
        "coeff_member": "C2824T2N.csv",       # Name,Coeff,Label  (1,237 rows)
        "hier_member": "V28115H1.TXT",        # SAS %SET0(CC=..,HIER=%STR(..)) hierarchy macro
    },
    "gem": {
        "version": "gem_2018",
        "url": "https://www.cms.gov/medicare/coding/icd10/downloads/2018-icd-10-cm-general-equivalence-mappings.zip",
        "member": "2018_I9gem.txt",           # fixed/space-delimited: icd9 icd10 flags(5 digits)
    },
}


def fetch_zip(url: str) -> zipfile.ZipFile:
    import requests
    print(f"  GET {url}", file=sys.stderr)
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))


def _find(zf: zipfile.ZipFile, name: str) -> str:
    """Match a member case-insensitively, possibly inside a nested zip path."""
    for n in zf.namelist():
        if n.split("/")[-1].lower() == name.lower():
            return n
    raise KeyError(f"{name} not found in archive; members: {zf.namelist()[:20]}")


def build_ccsr(out: str):
    import pandas as pd
    s = SOURCES["ccsr"]
    zf = fetch_zip(s["url"])
    df = pd.read_csv(io.BytesIO(zf.read(_find(zf, s["member"]))), dtype=str)
    strip = lambda c: c.str.strip().str.strip("'").str.strip() if c.dtype == object else c
    df = df.apply(strip)
    col = {c.lower().strip(): c for c in df.columns}
    res = pd.DataFrame({
        "icd10cm_code": df[col["icd-10-cm code"]].str.replace(".", "", regex=False),
        "description": df[col["icd-10-cm code description"]],
        "default_ccsr_ip": df[col["default ccsr category ip"]],
        "default_ccsr_op": df[col["default ccsr category op"]],
        "ccsr_1": df.get(col.get("ccsr category 1")),
        "ccsr_2": df.get(col.get("ccsr category 2")),
        "ccsr_3": df.get(col.get("ccsr category 3")),
        "ccsr_4": df.get(col.get("ccsr category 4")),
        "ccsr_5": df.get(col.get("ccsr category 5")),
        "ccsr_6": df.get(col.get("ccsr category 6")),
    })
    res["source_version"] = s["version"]
    _write(res, out, "ccsr_icd10cm.csv")


def build_cmshcc(out: str):
    import pandas as pd
    # (1) dx -> HCC (V28 column)
    sm = SOURCES["cmshcc_map"]
    zf = fetch_zip(sm["url"])
    raw = pd.read_csv(io.BytesIO(zf.read(_find(zf, sm["member"]))), dtype=str,
                      skiprows=3, engine="python")  # skip title/legend rows
    raw.columns = [c.strip() for c in raw.columns]
    dxcol = next(c for c in raw.columns if "diagnosis" in c.lower() and "code" in c.lower())
    v28col = next(c for c in raw.columns if "v28" in c.lower())
    dxmap = pd.DataFrame({
        "icd10cm_code": raw[dxcol].str.replace(".", "", regex=False).str.strip(),
        # normalize to a bare integer HCC ("HCC19"/"19" -> "19") so it joins to the
        # coefficients (term HCC<n> -> n) and hierarchy (CC=<n>) tables. All three are bare ints.
        "hcc": raw[v28col].str.extract(r"(\d+)")[0],
    }).dropna(subset=["hcc"])
    dxmap["source_version"] = sm["version"]
    _write(dxmap, out, "cmshcc_dx_hcc.csv")

    # (2) coefficients + (3) hierarchy (both inside the model-software zip)
    ss = SOURCES["cmshcc_software"]
    zf2 = fetch_zip(ss["url"])
    inner = next((n for n in zf2.namelist() if n.lower().endswith(".zip") and "v28" in n.lower()), None)
    pkg = zipfile.ZipFile(io.BytesIO(zf2.read(inner))) if inner else zf2

    coeff = pd.read_csv(io.BytesIO(pkg.read(_find(pkg, ss["coeff_member"]))), dtype=str)
    coeff.columns = [c.strip().lower() for c in coeff.columns]   # name, coeff, label
    parts = coeff["name"].str.extract(r"^(?P<segment>[A-Z]+)_(?P<term>.+)$")
    coeff["segment"] = parts["segment"]
    coeff["term"] = parts["term"]
    coeff["hcc"] = coeff["term"].str.extract(r"^HCC(\d+)$")[0]    # null for demographic/interaction terms
    coeff["source_version"] = ss["version"]
    _write(coeff, out, "cmshcc_coefficients.csv")

    # hierarchy: parse %SET0(CC=35, HIER=%STR(36, 37, 38)) -> (superior, excluded) rows
    macro = pkg.read(_find(pkg, ss["hier_member"])).decode("latin-1")
    rows = []
    for m in re.finditer(r"CC\s*=\s*(\d+)\D+HIER\s*=\s*%STR\(([^)]*)\)", macro):
        sup = m.group(1)
        for exc in re.findall(r"\d+", m.group(2)):
            rows.append((sup, exc))
    hier = pd.DataFrame(rows, columns=["superior_hcc", "excluded_hcc"])
    hier["source_version"] = ss["version"]
    _write(hier, out, "cmshcc_hierarchy.csv")


def build_gem(out: str):
    import pandas as pd
    s = SOURCES["gem"]
    zf = fetch_zip(s["url"])
    txt = zf.read(_find(zf, s["member"])).decode("latin-1")
    rows = []
    for line in txt.splitlines():
        p = line.split()
        if len(p) >= 3:
            rows.append((p[0], p[1], p[2]))
    df = pd.DataFrame(rows, columns=["icd9_code", "icd10_code", "flags"])
    f = df["flags"].str.zfill(5)   # 5 positional flags
    df["flag_approximate"] = f.str[0]
    df["flag_nomap"] = f.str[1]
    df["flag_combination"] = f.str[2]
    df["flag_scenario"] = f.str[3]
    df["flag_choice"] = f.str[4]
    df["source_version"] = s["version"]
    _write(df, out, "gem_icd9_icd10.csv")


def _write(df, out: str, name: str):
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, name)
    df.to_csv(path, index=False)
    print(f"  wrote {path}  ({len(df):,} rows)", file=sys.stderr)


COPY_TEMPLATE = """-- load.sql — stage the CSVs to S3, then COPY into the `terminology` schema (Redshift).
-- Replace s3://YOUR-BUCKET/terminology/ and the IAM role ARN. BigQuery: use `bq load` instead.
CREATE SCHEMA IF NOT EXISTS terminology;
{copies}
"""
COPY_ONE = """COPY terminology.{table} FROM 's3://YOUR-BUCKET/terminology/{file}'
  IAM_ROLE 'arn:aws:iam::ACCOUNT:role/REDSHIFT_COPY' CSV IGNOREHEADER 1 REGION 'us-west-2';"""


def write_load_sql(out: str):
    tables = {
        "ccsr_icd10cm": "ccsr_icd10cm.csv",
        "cmshcc_dx_hcc": "cmshcc_dx_hcc.csv",
        "cmshcc_coefficients": "cmshcc_coefficients.csv",
        "cmshcc_hierarchy": "cmshcc_hierarchy.csv",
        "gem_icd9_icd10": "gem_icd9_icd10.csv",
    }
    copies = "\n".join(COPY_ONE.format(table=t, file=f) for t, f in tables.items())
    with open(os.path.join(out, "load.sql"), "w") as fh:
        fh.write(COPY_TEMPLATE.format(copies=copies))
    print(f"  wrote {os.path.join(out, 'load.sql')}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="./_build")
    ap.add_argument("--download", action="store_true", help="actually fetch + build (else dry list)")
    ap.add_argument("--only", nargs="*", choices=["ccsr", "cmshcc", "gem"], help="subset")
    a = ap.parse_args()
    targets = a.only or ["ccsr", "cmshcc", "gem"]
    if not a.download:
        print("Would build:", ", ".join(targets), "-> ", a.out)
        print("Re-run with --download (needs: pip install requests pandas).")
        return
    builders = {"ccsr": build_ccsr, "cmshcc": build_cmshcc, "gem": build_gem}
    for t in targets:
        print(f"[{t}]", file=sys.stderr)
        builders[t](a.out)
    write_load_sql(a.out)
    print("Done. Stage ./_build/*.csv to object storage, then run load.sql.", file=sys.stderr)


if __name__ == "__main__":
    main()
