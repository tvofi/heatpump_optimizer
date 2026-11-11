"""Round-10 class sweep I5: prose (docs, comments, briefs) drifts stale against the code.

Enumerator over the whole repository, built from the five I5 findings' seam
rules plus three widened arms that the finding harnesses do not reach.

Arms (each prints SEAM rows; STALE rows are candidate instances):
  F1 ui_labels         D5-s1-01  docs UI labels vs strings.json/manifest
  F2 card_banner       D5-s2-01  doc banner version vs stamped CARD_VERSION
  F3 comment_symbols   D5-s3-01  backticked comment identifiers vs code tokens
  F4 service_counts    D5-s3-51  registry-count words in __init__/services comments
  F5 structure_refs    D11-s1-51 structure metric count / retired keys in D7.md
  W1 version_literals  every vX.Y.Z in README.md + docs/*.md; STALE when it is
                       presented as the current version (no since/until/before/
                       arrived/(vX)/or later marker) and differs from VERSION
  W2 retired_keys      cut_*/cross_seam_edges/cross_seam_fraction named in
                       dev/governance/**, CLAUDE.md, AGENTS.md, tests/README.md
                       and tests/structure.py comments/docstrings, outside the budget file
                       and outside a sentence that says the key was retired
                       or carries a history marker (#NNN, round N, AS OF ...)
  W3 scenario_counts   'N scenarios' with N >= half the live set (digits or spelled) in tests/stress.py and
                       dev/governance/** vs len(tests/stress_budgets.json),
                       STALE when no history marker sits within +-2 lines
  W4 census_refused    rows tools/audit/prose_counts_census.py REFUSES (a count
                       noun with no disposition) -- seams no arm prices

Command (repo root): PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D14/I5/sweep_i5.py
  --null     run W1-W3 over a synthetic clean fixture (expect 0 STALE)
  --perturb  in memory, re-introduce one stale line ('record all 51 scenarios'
             appended to D9.md) -> W3 STALE +1
"""
import json, os, re, subprocess, sys, tempfile

PY = sys.executable
ENV = dict(os.environ, PYTHONPATH="tests/hastub")
R10 = "dev/audit/rounds/round10"
SPELL = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen "
    "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60}


def spelled(w):
    w = w.lower()
    if w.isdigit():
        return int(w)
    if w in SPELL:
        return SPELL[w]
    m = re.fullmatch(r"(twenty|thirty|forty|fifty|sixty)-(\w+)", w)
    if m and m.group(2) in SPELL:
        return TENS[m.group(1)] + SPELL[m.group(2)]
    return TENS.get(w)


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, env=ENV)
    return p.stdout


def finding_arms():
    rows = []
    out = run([PY, f"{R10}/D5/s1/ui_labels.py"])
    rows += [("F1", l.split()[1], l) for l in out.splitlines() if l.startswith("HIT")]
    out = run([PY, f"{R10}/D5/s2/card_banner.py"])
    if "banner_mismatch=1" in out:
        rows.append(("F2", "docs/dashboard-card.md:banner", out.splitlines()[0]))
    out = run([PY, f"{R10}/D5/s3/comment_symbols.py"])
    rows += [("F3", l.split()[1], l) for l in out.splitlines() if l.startswith("MISSING")]
    out = run([PY, f"{R10}/D5/leads/service_count_comments.py"])
    rows += [("F4", l.split()[0], l) for l in out.splitlines() if l.endswith("STALE")]
    out = run(["node", f"{R10}/D11/leads/stale_structure_refs.mjs"])
    rows += [("F5", l.split()[1], l) for l in out.splitlines()
             if (l.startswith("count ") and "stale=true" in l) or (l.startswith("key ") and "budgets: false" in l)]
    return rows


def files(root, globs):
    out = []
    for g in globs:
        if g.endswith("/**"):
            base = os.path.join(root, g[:-3])
            for d, _, fs in os.walk(base):
                out += [os.path.relpath(os.path.join(d, f), root) for f in fs if f.endswith(".md")]
        elif "*" in g:
            d, pat = os.path.split(g)
            if os.path.isdir(os.path.join(root, d)):
                rx = re.compile(pat.replace(".", r"\.").replace("*", ".*") + "$")
                out += [os.path.join(d, f) for f in os.listdir(os.path.join(root, d)) if rx.match(f)]
        elif os.path.exists(os.path.join(root, g)):
            out.append(g)
    return sorted(set(out))


def read(root, f, extra):
    t = open(os.path.join(root, f), encoding="utf-8").read()
    return t + extra.get(f, "")


HIST_V = re.compile(r"(\\bin v\\d|absorbed|since|until|before|after|arrived|older than|earlier|halved|removed|gone|and later|\+|at version|onward|grammar)", re.I)


def w1(root, extra):
    ver = open(os.path.join(root, "VERSION")).read().strip()
    rows = []
    for f in files(root, ["README.md", "docs/*.md"]):
        for n, l in enumerate(read(root, f, extra).splitlines(), 1):
            for m in re.finditer(r"\bv(\d+\.\d+\.\d+)\b", l):
                hist = bool(HIST_V.search(l)) or f"(v{m.group(1)})" in l
                stale = (not hist) and m.group(1) != ver
                rows.append(("W1", f"{f}:{n}", f"v{m.group(1)} hist={hist}", stale))
    return rows


RETIRED = re.compile(r"\b(cut_[a-z_]+|cross_seam_edges|cross_seam_fraction)\b")
RETIRE_WORD = re.compile(r"retir|was retired|replaced|folded into|seam_cut_total", re.I)


def w2(root, extra):
    budgets = set(json.load(open(os.path.join(root, "tests/structure_budgets.json"))))
    rows = []
    for f in files(root, ["dev/governance/**", "CLAUDE.md", "AGENTS.md", "tests/README.md", "tests/structure.py"]):
        lines = read(root, f, extra).splitlines()
        in_doc = False
        for n, l in enumerate(lines, 1):
            prose = True
            if f.endswith(".py"):
                q = l.count('"""')
                prose = in_doc or q > 0 or l.lstrip().startswith("#")
                if q % 2:
                    in_doc = not in_doc
            if not prose:
                continue  # a live code identifier (cut_costs table, evidence-only ratio) is not a claim
            for m in RETIRED.finditer(l):
                if m.group(1) in budgets or m.group(1) in ("cut_at",):
                    continue
                win = " ".join(lines[max(0, n - 3):n + 2])
                stale = not (RETIRE_WORD.search(win) or HIST_S.search(win))
                rows.append(("W2", f"{f}:{n}", m.group(1), stale))
    return rows


NUM = r"(\d+|(?:twenty|thirty|forty|fifty|sixty)(?:-[a-z]+)?|[a-z]+teen|ten|eleven|twelve)"
SCEN = re.compile(NUM + r" (?:stress )?scenarios\b", re.I)
HIST_S = re.compile(r"#\d+|round[- ]\d|\bR\d|re-planned|the old rule|passed|let a|blinded|synthetic|range\(|AS OF|snapshot", re.I)


def w3(root, extra):
    live = len(json.load(open(os.path.join(root, "tests/stress_budgets.json"))))
    rows = []
    for f in files(root, ["tests/stress.py", "dev/governance/**"]):
        lines = read(root, f, extra).splitlines()
        for n, l in enumerate(lines, 1):
            for m in SCEN.finditer(l):
                v = spelled(m.group(1))
                if v is None or v < live // 2:  # a claim about the whole set, not a subset or a slack
                    continue
                win = " ".join(lines[max(0, n - 3):n + 2])
                hist = bool(HIST_S.search(win))
                stale = (not hist) and v != live
                rows.append(("W3", f"{f}:{n}", f"{m.group(0)} live={live} hist={hist}", stale))
    return rows


def w4():
    out = run([PY, "tools/audit/prose_counts_census.py"])
    return [("W4", l.split()[1].rstrip(":") + ":" + l.split()[1].split(":")[1] if False else l.split()[1], l.strip())
            for l in out.splitlines() if l.strip().startswith("REFUSED") and ".md:" in l]


def fixture():
    d = tempfile.mkdtemp(prefix="i5null")
    os.makedirs(f"{d}/docs"); os.makedirs(f"{d}/tests"); os.makedirs(f"{d}/dev/governance/dimensions")
    open(f"{d}/VERSION", "w").write("7.0.0\n")
    open(f"{d}/README.md", "w").write("Since v5.0.0 names are translated.\n")
    open(f"{d}/docs/a.md", "w").write("```\n heatpump-optimizer-card  v7.0.0\n```\n")
    json.dump({"recorded_at": "x", "seam_cut_total": 1}, open(f"{d}/tests/structure_budgets.json", "w"))
    json.dump({f"s{i}": {} for i in range(54)}, open(f"{d}/tests/stress_budgets.json", "w"))
    open(f"{d}/tests/structure.py", "w").write("# cross_seam_edges was retired into seam_cut_total\n")
    open(f"{d}/tests/stress.py", "w").write("# the merge base solves the same fifty-four scenarios\n")
    open(f"{d}/dev/governance/dimensions/D9.md", "w").write("record all 54 scenarios\n")
    return d


def main():
    if "--null" in sys.argv:
        root = fixture()
        rows = [r for r in w1(root, {}) + w2(root, {}) + w3(root, {}) if r[3]]
        for r in rows:
            print("STALE", *r[:3])
        print(f"RESULT null_stale={len(rows)} count")
        return
    extra = {"dev/governance/dimensions/D9.md": "\nThe stress harness records all 51 scenarios.\n"} if "--perturb" in sys.argv else {}
    fr = finding_arms()
    for a, s, l in fr:
        print("STALE", a, s, "|", l)
    wide = w1(".", extra) + w2(".", extra) + w3(".", extra)
    for a, s, l, st in wide:
        print("STALE" if st else "SEAM ", a, s, "|", l)
    w4r = w4()
    for a, s, l in w4r:
        print("SEAM ", a, s, "|", l)
    per = {}
    for a, *_ in fr:
        per[a] = per.get(a, 0) + 1
    for a, s, l, st in wide:
        per.setdefault(a, 0); per[a] += int(st)
    for k in sorted(per):
        print(f"RESULT stale_{k}={per[k]} count")
    print(f"RESULT seams_wide={len(wide)} seams_census_refused={len(w4r)} count")
    print(f"RESULT stale_total={sum(per.values())} count")


main()
