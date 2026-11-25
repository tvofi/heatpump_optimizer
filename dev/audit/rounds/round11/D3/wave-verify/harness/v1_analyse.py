#!/usr/bin/env python3
"""V1 comparator: every name=value pair the probe's EXPECTED header (else the record's baseline/mutant values)
states, found again in the re-run's RESULT lines; plus the null-control lines and whether the arms differ."""
import json, re, pathlib, math
D = pathlib.Path("<seat-dir>")
SKIP = re.compile(r"^(thread_factor|load1|swapins|wall|cpu|elapsed|rss|t_|time)", re.I)
PAIR = re.compile(r"([A-Za-z_][\w.\-]*)\s*[=:]\s*(-?[\w.+\-]+|\([^)]*\)|\[[^\]]*\])")


def num(s):
    try:
        return float(s)
    except Exception:
        return None


UNIT = re.compile(r"\s+(count|ratio|bool|kWh|kW|K|C|degC|Hz|s|h|displace)$")


def same(a, b):
    a, b = UNIT.sub("", str(a).strip()), UNIT.sub("", str(b).strip())
    x, y = num(a), num(b)
    if x is not None and y is not None:
        return x == y or math.isclose(x, y, rel_tol=1e-6, abs_tol=1e-9)
    return a.strip(",;") == b.strip(",;")


def pairs(text):
    return [(k, v) for k, v in PAIR.findall(text) if not SKIP.match(k)]


ARM = re.compile(r"^(?P<pre>.*?)(?:_|\b)(?P<arm>baseline|base|mutant|mut)(?P<post>(?:_[\w.\-]+)?)\s*=\s*(?P<val>.+?)\s*$")


def arm_pairs(res_lines):
    """name -> [baseline value, mutant value], from `X_baseline=V` / `X_mutant=W` lines and
    `X baseline=V mutant=W` lines."""
    out = {}
    for l in res_lines:
        l = re.sub(r"\s+\(.*$", "", l)  # trailing prose in parentheses
        m = re.match(r"^(\S+?)(?:[_ :]+)baseline\w*\s*[=:]\s*(.+?)\s+mutant\w*\s*[=:]\s*(\([^)]*\)|\[[^\]]*\]|\S+)(?:\s+\w+=.*)?\s*$", l) or \
            re.match(r"^(\S+)\s+base\w*=\s*(.+?)\s+mut\w*=\s*(.+?)\s*$", l)
        if m:
            out[m.group(1)] = [m.group(2), m.group(3)]
            continue
        toks = re.findall(r"(\S+?)_(baseline|mutant)=(\S+)", l)
        if len(toks) >= 2:
            for pre, arm, val in toks:
                out.setdefault(pre, [None, None])[0 if arm == "baseline" else 1] = val
            continue
        m = re.match(r"^(\S+?)_(baseline|mutant):\s*(.+)$", l)
        if m:
            out.setdefault(m.group(1), [None, None])[0 if m.group(2) == "baseline" else 1] = m.group(3)
            continue
        m = re.match(r"^(\S+?)=\s*(.+?)\s*$", l)
        if not m:
            continue
        name, val = m.group(1), m.group(2)
        a = ARM.match(name + "=" + val)
        if not a:
            continue
        key = (a.group("pre") or "") + (a.group("post") or "")
        slot = 0 if a.group("arm").startswith("base") else 1
        out.setdefault(key, [None, None])[slot] = re.sub(r"\s+(count|ratio|bool|kWh|kW|K|C|degC|Hz)$", "", val)
    return out


def analyse(c, vdir="v1"):
    r = json.load(open(D / vdir / f"{c['key']}.json"))
    out = r["stdout"]
    res_lines = [l[len("RESULT "):] for l in out.splitlines() if l.startswith("RESULT ")]
    got = {}
    for l in res_lines:
        for k, v in pairs(l):
            got.setdefault(k, []).append(v)
    src = open(D / "base" / c["probe_path"]).read().splitlines()[:80]
    exp = [l.split("EXPECTED", 1)[1] if "EXPECTED" in l else l.split("Expected:", 1)[1]
           for l in src if "EXPECTED RESULT" in l or "# Expected:" in l]
    basis = "header"
    want = []
    for l in exp:
        want += pairs(re.sub(r"\(.*?\)\s*$", "", l.replace("RESULT", "")))
    if not want:
        basis = "record"
        want = pairs(f"{c.get('baseline_value') or ''} ; {c.get('mutant_value') or ''}")
    hit = [(k, v) for k, v in want if any(same(v, g) for g in got.get(k, []))]
    loose = [(k, v) for k, v in want if (k, v) not in hit and any(
        k in l and re.search(r"(?<![\w.])" + re.escape(v.strip(",;")) + r"(?!\w)", l) for l in res_lines)]
    arms = arm_pairs(res_lines)
    moved = {k: v for k, v in arms.items() if "null" not in k.lower() and v[0] is not None and v[1] is not None and not same(v[0], v[1])}
    null_pairs = {k: v for k, v in arms.items() if "null" in k.lower() and v[0] is not None and v[1] is not None}
    null_moved = {k: v for k, v in null_pairs.items() if not same(v[0], v[1])}
    moved_counts = [l for l in res_lines if re.search(r"(^|_)moved\w*=\s*[1-9]", l) and "null" not in l.lower()]
    nulls = [l for l in res_lines if "null" in l.lower()]
    null_ok = (all(re.search(r"=\s*(0(\.0+)?|False|0/\d+)\b|moved=0|delta=0|same|equal|True", l) for l in nulls)
               if nulls else None)
    return {"key": c["key"], "box": c["box"], "rc": r["rc"], "wall_s": r["wall_s"], "load1": round(r["load1"], 1),
            "basis": basis, "pairs": len(want), "matched": len(hit) + len(loose),
            "unmatched": [f"{k}={v}" for k, v in want if (k, v) not in hit and (k, v) not in loose][:6],
            "arm_pairs": len([k for k in arms if "null" not in k.lower()]), "moved_pairs": len(moved),
            "moved_lines": len(moved_counts), "null_pairs": len(null_pairs), "null_moved": len(null_moved),
            "moved_example": next(iter(moved.items()), None),
            "n_result": len(res_lines), "null_lines": nulls[:4], "null_ok": null_ok, "result_head": res_lines[:8],
            "stderr_tail": r["stderr"][-300:] if r["rc"] != 0 else ""}


if __name__ == "__main__":
    from collections import Counter
    cands = json.load(open(D / "candidates.json"))
    rows = [analyse(c) for c in cands if (D / "v1" / f"{c['key']}.json").exists()]
    json.dump(rows, open(D / "v1_analysis.json", "w"), indent=1)
    st = Counter((("rc0" if r["rc"] == 0 else f"rc{r['rc']}"),
                  ("full" if r["pairs"] and r["matched"] == r["pairs"] else ("nopairs" if not r["pairs"] else "partial")),
                  r["null_ok"]) for r in rows)
    print(len(rows), st.most_common())
