#!/usr/bin/env python3
"""Build interlink-map.json + per-site WPCode snippets from interlink-scheme.csv.

Covers placements body-intro (mode=replace) and body-final-cta (mode=append).
Placements case-cta-button / related-*-block / fix-existing are template/manual
work (see interlink-scheme.md) and are excluded here.
"""
import csv, json
from urllib.parse import urlparse

CSV = "interlink-scheme.csv"
HOSTS = {
    "DP": "decorativearchitecturalproducts.com",
    "ART": "royalfoam.art",
    "DS": "decorativearchitecturalshapes.com",
}
SNIPPET_FILES = {
    "DP": "interlink-snippet-dp.php",
    "ART": "interlink-snippet-art.php",
    "DS": "interlink-snippet-ds.php",
}

rules = []
with open(CSV, encoding="utf-8") as f:
    for row in csv.DictReader(f, delimiter=";"):
        mode = {"body-intro": "replace", "body-final-cta": "append"}.get(row["placement"])
        if not mode:
            continue
        src = urlparse(row["source_url"])
        host = src.netloc.replace("www.", "")
        site = next((s for s, h in HOSTS.items() if h == host), None)
        assert site == row["site"], f"host/site mismatch: {row['id']}"
        assert row["anchor"].strip() and row["target_url"].startswith("http"), f"bad row: {row['id']}"
        rules.append({
            "id": row["id"],
            "site": site,
            "path": src.path,
            "mode": mode,
            "phrase": row["anchor"].strip(),
            "url": row["target_url"].strip(),
        })

with open("interlink-map.json", "w", encoding="utf-8") as f:
    json.dump({"version": 1, "rules": rules}, f, ensure_ascii=False, indent=1)

with open("interlink-snippet-template.php", encoding="utf-8") as f:
    tpl = f.read()

for site, fname in SNIPPET_FILES.items():
    site_rules = [r for r in rules if r["site"] == site]
    payload = json.dumps(site_rules, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("\\", "\\\\").replace("'", "\\'")
    assert "%%RULES_JSON%%" in tpl and "%%SITE_TAG%%" in tpl
    out = tpl.replace("%%SITE_TAG%%", f"{site} ({HOSTS[site]})").replace("%%RULES_JSON%%", payload)
    with open(fname, "w", encoding="utf-8") as f:
        f.write(out)
    n_rep = sum(1 for r in site_rules if r["mode"] == "replace")
    n_app = sum(1 for r in site_rules if r["mode"] == "append")
    print(f"{fname}: {len(site_rules)} rules ({n_rep} replace, {n_app} append)")
print(f"TOTAL: {len(rules)} rules -> interlink-map.json")
