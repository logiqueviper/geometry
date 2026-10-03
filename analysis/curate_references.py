"""Sanitize manually reviewed bibliographic candidates into public fact records.

The private retrieval cache is intentionally excluded from Git and the archive.
DOI/title/author/year matching verifies existence, not a full-paper review.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Deliberately reject deceptive fuzzy matches, duplicate venue versions, books
# with missing authors, and unrelated search results. Preserve deposited titles.
ACCEPTED_LEADS = [0,2,3,4,5,7,8,9,10,11,12,13,14,15,16,18,19,20,
                  25,26,29,30,33,35,37,39,41,43,44,45]
RECENT = {
    "10.1145/3633331": "cost-aware stealing; shared-memory boundary",
    "10.1016/j.jpdc.2021.03.010": "latency-aware work-stealing analysis",
    "10.1016/j.jpdc.2023.104816": "work-queue correctness; multiplicity differs from our invariant",
    "10.1016/j.jpdc.2022.07.002": "load-balancing criteria",
    "10.1016/j.parco.2023.103020": "lifeline balancing in distributed task runtimes",
    "10.1016/j.jpdc.2021.06.003": "autotuning; heterogeneous systems boundary",
    "10.1109/mc.2022.3152681": "benchmarking and statistical interpretation",
    "10.1504/ijwgs.2019.103233": "shared-memory stealing and cache effects boundary",
    "10.1109/empdp.2019.8671619": "MPI dynamic loop scheduling",
    "10.1109/ipdpsw.2019.00117": "hierarchical distributed loop scheduling",
    "10.1002/cpe.6750": "adaptive self-scheduling",
    "10.1145/3337821.3337878": "accelerated work stealing",
    "10.1145/3774934.3786452": "work-stealing overhead; published January 2026",
    "10.1145/3295500.3356161": "deterministic distributed stealing",
    "10.1145/3558481.3591099": "synchronization overhead of stealing",
    "10.1145/3635035.3635041": "portable work-stealing implementations",
    "10.1145/3293883.3295735": "futures/dependencies; model boundary",
    "10.2197/ipsjjip.29.478": "amount and hierarchy in stealing strategies",
    "10.1109/cluster48925.2021.00040": "distributed stealing via matchmaking",
    "10.1145/3526063.3535352": "simulation performance methodology",
    "10.5220/0009875302330239": "distributed simulator verification",
    "10.1016/j.tcs.2021.09.026": "constrained client-server topology theory",
}
CLOSEST = ["10.1016/0743-7315(89)90021-x", "10.1002/cpe.4330020403",
           "10.1006/jcss.1996.0075", "10.1016/s0167-8191(99)00002-2",
           "10.1109/88.532137", "10.1145/1654059.1654113",
           "10.1145/2038037.1941582", "10.1016/j.jpdc.2021.03.010",
           "10.1016/j.parco.2023.103020", "10.1016/j.tcs.2021.09.026"]

def facts(record, source, scope):
    dates = record.get("published", record.get("issued", {}))["date-parts"][0]
    year = dates[0]
    assert isinstance(year, int) and year <= 2026
    assert record.get("author") and record.get("title") and record.get("DOI")
    return {"doi": record["DOI"].lower(), "title": " ".join(record["title"]),
            "subtitle": " ".join(record.get("subtitle", [])),
            "authors": [{k: a[k] for k in ("given", "family", "name") if k in a}
                        for a in record["author"]],
            "year": year, "publication_date_parts": dates,
            "venue": " ".join(record.get("container-title", [])),
            "type": record["type"], "volume": record.get("volume"),
            "issue": record.get("issue"), "pages": record.get("page"),
            "source_url": "https://api.crossref.org/works/" + record["DOI"],
            "source_cache_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "verification": "Crossref bibliographic existence; author/title/date reviewed",
            "full_paper_read": False, "claim_verification": "pending full text",
            "relevance_scope": scope, "retrieval_date": "2026-10-03"}

def main():
    cache = ROOT / "docs/source-records"
    lead_path = cache / "crossref-candidates.json"
    candidates = json.loads(lead_path.read_text())["candidates"]
    selected = [facts(candidates[i]["record"], lead_path,
                      "historical scheduling, graph theory, runtime, or methodology background")
                for i in ACCEPTED_LEADS]
    correction_path = cache / "crossref-canonical-corrections.json"
    for item in json.loads(correction_path.read_text()):
        selected.append(facts(item["record"], correction_path,
                              "canonical replacement of a misleading title-only match"))
    found = {}
    for filename in ("crossref-recent-candidates.json", "crossref-targeted-recent.json"):
        path = cache / filename
        for query in json.loads(path.read_text()):
            for record in query.get("records", []):
                if record.get("DOI", "").lower() in RECENT:
                    found[record["DOI"].lower()] = facts(record, path, RECENT[record["DOI"].lower()])
    assert set(found) == set(RECENT)
    selected.extend(found.values())
    selected.sort(key=lambda r: (r["year"], r["doi"]))
    assert len({r["doi"] for r in selected}) == len(selected)
    for r in selected:
        r["key"] = "ref" + str(selected.index(r) + 1)
        r["closest_ten_reading_priority"] = r["doi"] in CLOSEST
    output = {"status": "bibliographic verification only; literature gate remains open",
              "records": selected, "verified_count": len(selected),
              "since_2019_count": sum(r["year"] >= 2019 for r in selected),
              "full_paper_read_count": 0,
              "excluded_examples": ["Spectral Graph Theory: wrong 2019 chapter",
                "Regular Polytopes: wrong Johnson chapter", "MapReduce: wrong authors",
                "Ray: unrelated 1992 paper", "Borg Next Generation: unrelated poem",
                "Holm: wrong Shaffer paper", "UTS: deposited publication year missing"]}
    (ROOT / "docs/reference_records.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    lines = ["% Verified bibliographic facts; full-text reading/claims remain pending."]
    def escape(text):
        return str(text).replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
    for r in selected:
        authors = " and ".join(a.get("family", a.get("name", "")) +
                              (", " + a["given"] if a.get("given") else "") for a in r["authors"])
        kind = "article" if r["type"] == "journal-article" else "misc"
        fields = {"author": authors, "title": "{" + r["title"] + "}", "year": r["year"],
                  "doi": r["doi"], "url": "https://doi.org/" + r["doi"]}
        if r["venue"]: fields["journal" if kind == "article" else "howpublished"] = r["venue"]
        for key, source_key in (("volume","volume"),("number","issue"),("pages","pages")):
            if r[source_key]: fields[key] = r[source_key]
        lines.append("@" + kind + "{" + r["key"] + ",\n" + ",\n".join(
            "  " + k + " = {" + escape(v) + "}" for k, v in fields.items()) + "\n}")
    (ROOT / "refs.bib").write_text("\n\n".join(lines) + "\n")
    table = ["# Bibliographic verification and reading queue", "",
             f"{len(selected)} DOI records verified; {output['since_2019_count']} published since 2019. "
             "These are existence checks, not completed full-paper reviews.", "",
             "The ten marked papers are the provisional closest reading queue. "
             "Full text, methods, assumptions, and claims must be reviewed before the literature gate closes.", "",
             "| Year | DOI and deposited title | Scope | Full text read |", "|---|---|---|---|"]
    for r in selected:
        mark = " **[closest 10]**" if r["closest_ten_reading_priority"] else ""
        table.append(f"| {r['year']} | [{r['title']}](https://doi.org/{r['doi']}){mark} | "
                     f"{r['relevance_scope']} | Pending |")
    (ROOT / "docs/LITERATURE_MATRIX.md").write_text("\n".join(table) + "\n")
    print(f"Curated {len(selected)} metadata-verified records; {output['since_2019_count']} since 2019; full-text gate pending.")

if __name__ == "__main__": main()
