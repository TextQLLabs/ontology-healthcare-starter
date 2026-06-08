#!/usr/bin/env python3
"""
fetch_vsac.py — hydrate CERTIFIED clinical value sets from VSAC at install time, using the
CUSTOMER's own UMLS API key. We commit OIDs (see value-sets.md), NOT codes.

WHY THIS PATTERN: VSAC value sets embed codes from licensed vocabularies (SNOMED/CPT/LOINC/
ICD-10-CM/RxNorm) and are governed by the UMLS Metathesaurus License — they may NOT be
redistributed as standalone files. Each customer holds a free UMLS license and fetches the
code lists into THEIR environment with THEIR key. This script is that fetch step.
(HEDIS value sets are NOT in VSAC — they need a separate paid NCQA license; see value-sets.md.)

Get a free UMLS API key: sign up at https://uts.nlm.nih.gov -> My Profile -> API key.

Usage:
  pip install requests
  export UMLS_API_KEY=xxxxxxxx
  python fetch_vsac.py                       # expand every OID in value-sets.json
  python fetch_vsac.py --oid 2.16.840.1.113883.3.464.1003.103.12.1001

Output: terminology.value_set_members rows -> ./_build/value_set_members.csv
  columns: value_set_oid, value_set_name, code, code_system, code_system_name, version
Respects NLM limits (<=20 req/s; cache 12-24h). Auth = HTTP Basic, user 'apikey', pass = key.
"""
from __future__ import annotations
import argparse, csv, json, os, sys, time

FHIR_EXPAND = "https://cts.nlm.nih.gov/fhir/ValueSet/{oid}/$expand"


def expand(oid: str, api_key: str) -> list[dict]:
    import requests
    url = FHIR_EXPAND.format(oid=oid)
    r = requests.get(url, auth=("apikey", api_key), timeout=60,
                     headers={"Accept": "application/fhir+json"})
    if r.status_code == 401:
        sys.exit("401 from VSAC — check UMLS_API_KEY and that your UMLS license is active.")
    r.raise_for_status()
    body = r.json()
    name = body.get("name") or body.get("title") or oid
    version = body.get("version", "")
    out = []
    for c in body.get("expansion", {}).get("contains", []):
        out.append({
            "value_set_oid": oid,
            "value_set_name": name,
            "code": c.get("code"),
            "code_system": c.get("system"),          # canonical URI
            "code_system_name": _sys_name(c.get("system", "")),
            "version": version,
        })
    return out


_SYS = {
    "http://hl7.org/fhir/sid/icd-10-cm": "ICD-10-CM",
    "http://snomed.info/sct": "SNOMED CT",
    "http://loinc.org": "LOINC",
    "http://www.ama-assn.org/go/cpt": "CPT",
    "http://www.nlm.nih.gov/research/umls/rxnorm": "RxNorm",
    "https://www.cms.gov/Medicare/Coding/HCPCSReleaseCodeSets": "HCPCS",
}
def _sys_name(uri: str) -> str:
    return _SYS.get(uri, uri.rsplit("/", 1)[-1] if uri else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default=os.path.join(os.path.dirname(__file__), "value-sets.json"))
    ap.add_argument("--oid", help="fetch a single OID instead of the registry")
    ap.add_argument("--out", default="./_build/value_set_members.csv")
    a = ap.parse_args()
    key = os.environ.get("UMLS_API_KEY")
    if not key:
        sys.exit("Set UMLS_API_KEY (free at https://uts.nlm.nih.gov).")

    if a.oid:
        oids = [a.oid]
    else:
        with open(a.registry) as fh:
            oids = [v["oid"] for v in json.load(fh)["value_sets"]]

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    rows = []
    for oid in oids:
        print(f"  expand {oid}", file=sys.stderr)
        rows += expand(oid, key)
        time.sleep(0.1)   # stay well under 20 req/s
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["value_set_oid", "value_set_name", "code",
                                           "code_system", "code_system_name", "version"])
        w.writeheader(); w.writerows(rows)
    print(f"wrote {a.out} ({len(rows):,} codes from {len(oids)} value sets)", file=sys.stderr)
    print("Load into terminology.value_set_members; join in filters/diagnosis.tql via OID.", file=sys.stderr)


if __name__ == "__main__":
    main()
