#!/usr/bin/env python3
"""D6-s7: every unit of dev/programme/plan-2026-09-open-issues.md rowed with an executed check.

Metric (one line): wrong_rows = units of the plan whose executed check contradicts a claim
the sentence makes about the baseline tree (verdict false or stale), EXCLUDING rows whose
only contradiction is a historical path spelling: tests/layout.json lists this file in
`historical` (tvofi's D2: it keeps the paths that were true when written), so a path that
moved or left the tree is counted apart, as `d2_path_rows`, and never in wrong_rows.

Two passes over text_ledger.py's D6 units of the file:
  * every unit: each backticked repository path is resolved against the export tree, then
    through tests/layout.py:locate (the move map), then against the baseline's git history
    (--repo); each 7-40 hex token with a digit and a letter is resolved as a commit in --repo.
  * CURATED: the sentences that state a present-tense fact about code, data or files, each
    checked by executing the production symbol that decides it (the table below names it).
A unit with no backticked token, no hex token, no `#N` and no digit is a no-claim row. A unit
with resolving references whose remaining content is dated history (issues, pull requests,
reviews, sessions -- GitHub state a D6 seat does not read) is `unverifiable`, the result
naming what resolved.

Run (from the export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D6/s7/plan_claims.py --repo GIT_DIR [--perturb ARM]
  --repo: a git repository holding the baseline commit (default $HPO_REPO), read-only.
  --perturb wave-red-guard : the web-fix-wave.js merge chain gets an in-memory red latch
        (wave_red.mjs --perturb red-guard): wrong_rows must go DOWN by 1 (9 -> 8).
  --perturb mdc-three : the .cursor/rules alwaysApply count is read over the first three
        .mdc files only (as if the set were still three): wrong_rows must go DOWN by 1 (9 -> 8;
        the loader half of the same sentence stays stale).
Writes ledger_plan.tsv beside itself.

Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (counts, exact): wrong_rows=9 (1 false, 8 stale),
d2_path_rows=29, units=2628, curated_rows=30, no_claim_rows=593, true_rows=21, unverifiable_rows=1976.
Reads the export tree only; git is read-only on --repo; writes ledger_plan.tsv beside itself. Machine: box B13 (light seat), linux x86_64.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import fnmatch
import json
import re
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest import mock

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
BASELINE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
DOC = "dev/programme/plan-2026-09-open-issues.md"
SELF = "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D6/s7/plan_claims.py --repo $HPO_REPO"
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "tools/audit"), str(ROOT / "tools/release")]
import layout  # noqa: E402  production: the move map (tests/layout.py)
import text_ledger  # noqa: E402

t_proc0, t_thr0 = time.process_time(), time.thread_time()
ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=os.environ.get("HPO_REPO", ""))
ap.add_argument("--perturb", default="", choices=["", "wave-red-guard", "mdc-three"])
a = ap.parse_args()
GIT = ["git", "-C", a.repo] if a.repo else None


def git(*args):
    if not GIT:
        return None
    r = subprocess.run(GIT + list(args), capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


# --- the tree --------------------------------------------------------------------------
files = []
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in (".git", "node_modules", "__pycache__")]
    for f in fn:
        p = os.path.relpath(os.path.join(dp, f), ROOT)
        if not p.startswith("dev/audit/rounds/round11/"):
            files.append(p)
fileset = set(files)
dirset = {str(Path(p).parent) + "/" for p in files for _ in [0]}
for p in list(dirset):
    parts = p.rstrip("/").split("/")
    for i in range(1, len(parts)):
        dirset.add("/".join(parts[:i]) + "/")
basenames = {Path(p).name for p in files}
tops = {p.split("/")[0] for p in files} | {"docs", "tools", "tests", "dev", ".claude", ".github", ".cursor", "custom_components"}

_hist = {}


def in_history(p):
    """The newest baseline-ancestor commit touching p, or None (needs --repo)."""
    if p not in _hist:
        out = git("log", "-1", "--format=%h", BASELINE, "--", p.rstrip("/"))
        _hist[p] = (out or "").strip() or None
    return _hist[p]


def resolve_path(p):
    """('now'|'moved'|'gone'|'never'|'unknown', detail)."""
    if any(ch in p for ch in "*?{"):
        rx = layout.glob_re(p)
        hits = [f for f in files if rx.match(f)]
        return ("now", f"glob matches {len(hits)}") if hits else ("unknown", "glob matches nothing now")
    if p in fileset or (p if p.endswith("/") else p + "/") in dirset:
        return "now", "exists"
    q = layout.locate(p, root=ROOT)
    if q != p and ((ROOT / q).exists()):
        return "moved", f"-> {q} (tests/layout.py:locate)"
    t = layout.target(p, layout.load(ROOT)["retired"])
    if t and t != p and (ROOT / t).exists():
        return "moved", f"-> {t} (tests/layout.py:target)"
    if not GIT:
        return "unknown", "absent; no --repo to read history"
    h = in_history(p)
    return ("gone", f"absent; last touched at {h}") if h else ("never", "absent from the tree and from the baseline's history")


_shas = {}


def resolve_sha(s):
    if s not in _shas:
        _shas[s] = None if not GIT else (git("cat-file", "-e", f"{s}^{{commit}}") is not None)
    return _shas[s]


BT = re.compile(r"`([^`]+)`")
HEX = re.compile(r"(?<![\w/.:#-])([0-9a-f]{7,40})(?![\w/-])")
EXT = re.compile(r"^[\w.-]+\.(py|md|mjs|js|json|sh|yml|yaml|txt|tsv|mdc|html|css)$")


def refs(text):
    paths, shas = set(), set()
    for tok in BT.findall(text):
        for piece in re.split(r"\s+", tok):
            piece = piece.strip("()[],;'\"")
            if not piece or "<" in piece or piece.startswith(("-", "$", "http", "~")):
                continue
            if ":" in piece and not piece.startswith("."):
                left, _, right = piece.partition(":")
                if re.fullmatch(r"[0-9a-f]{7,40}", left):
                    shas.add(left)
                    piece = right
                else:
                    piece = left
            piece = piece.split("#")[0].rstrip(".,")
            if layout.repo_path(piece, tops) or (piece.startswith(".") and "/" in piece and layout.PATH_TOKEN.fullmatch(piece.lstrip("./") or "x")):
                paths.add(piece)
            elif any(ch in piece for ch in "*") and "/" in piece and piece.split("/")[0] in tops:
                paths.add(piece)
            elif EXT.match(piece):
                paths.add("@basename:" + piece)
    for s in HEX.findall(text):
        if re.search(r"\d", s) and re.search(r"[a-f]", s):
            shas.add(s)
    return paths, shas


# --- curated present-tense checks ----------------------------------------------------------
CUR = {}   # hash prefix -> (command, result, verdict, truth)


def cur(h, cmd, result, ok, truth_if_not, stale=True):
    CUR[h] = (cmd, result, "true" if ok else ("stale" if stale else "false"), "" if ok else truth_if_not)


# 1. web-fix-wave.js and the red main (executed by wave_red.mjs)
env = dict(os.environ, HPO_PLANDATA=tempfile.mkdtemp() + "/pd")
wargs = ["node", str(HERE / "wave_red.mjs")] + (["--perturb", "red-guard"] if a.perturb == "wave-red-guard" else [])
wout = subprocess.run(wargs, cwd=ROOT, capture_output=True, text=True, env=env, timeout=300).stdout
wr = dict(re.findall(r"RESULT (\w+)=(\d+)", wout))
after, logged = int(wr.get("merges_after_red", -1)), int(wr.get("red_logged", -1))
WCMD = "node dev/audit/rounds/round11/D6/s7/wave_red.mjs"
cur("3a15803efb", WCMD, f"red_logged={logged}, merges_after_red={after} (null control: every gate green, 0)", logged == 1 and after == 0,
    "web-fix-wave.js logs `MAIN IS RED after <group> ... stop and repair` but its merge chain (mergeGroup's mergeChain.then) never reads the previous gate: "
    "the next group's merge agent runs after a red main, so the script does not stop merging. False since the sentence was written (81216e67c6 has the same chain).", stale=False)
tw, tbad = int(wr.get("tier_pairs_throwing", -1)), int(wr.get("tier_pairs_wrong", -1))
cur("3f09b9b632", WCMD + " (tier arm)", f"{tw} of 9 (fixer, reviewer) pairs throw 'a reviewer below the fixer', {tbad} disagree with haiku<sonnet<opus", tbad == 0 and tw == 3, "the ranking differs")
cur("0d64671876", WCMD + " (tier arm)", f"tierOk refuses {tw}/3 below-fixer pairs", tw == 3, "tierOk does not apply")
cur("4f8c60974f", WCMD + " (tier arm)", f"below-fixer reviewer pairs refused: {tw}/3, wrong {tbad}", tbad == 0, "a reviewer below its fixer runs")

# 2. .cursor/rules and what loads a Claude seat
mdc = sorted((ROOT / ".cursor/rules").glob("*.mdc"))
if a.perturb == "mdc-three":
    mdc = mdc[:3]
always = [p.name for p in mdc if re.search(r"^alwaysApply:\s*true\s*$", p.read_text(encoding="utf-8"), re.M)]
rules_with_paths = [p.name for p in sorted((ROOT / ".claude/rules").glob("*.md")) if re.search(r"^paths:", p.read_text(encoding="utf-8").split("\n---", 1)[0], re.M)]
claude_md_loads = bool(re.search(r"harness loads a rule when a read matches its `paths:` globs", (ROOT / "CLAUDE.md").read_text(encoding="utf-8")))
cur("89b9bdce98", "python3: count `alwaysApply: true` in .cursor/rules/*.mdc; `paths:` frontmatter in .claude/rules/*.md; CLAUDE.md's loader sentence",
    f"alwaysApply:true in {len(always)} of {len(mdc)} .mdc; {len(rules_with_paths)} .claude/rules files carry paths: globs; CLAUDE.md says the harness loads them: {claude_md_loads}",
    len(always) == 3 and not rules_with_paths,
    f".cursor/rules holds {len(always)} alwaysApply:true policies, not three, and Claude Code loads more than CLAUDE.md: {len(rules_with_paths)} .claude/rules/*.md "
    "files load on their paths: globs (CLAUDE.md, 'the harness loads a rule when a read matches its paths: globs').")
cur("2450097ed2", "python3: count `alwaysApply: true` in .cursor/rules/*.mdc", f"{len(always)} of {len(mdc)}", len(always) == 3,
    f"'all three' -- the set is {len(always)} files, generated from dev/governance/rules/ by rules_sync.mjs.")

# 3. the ratchet's cross_seam_fraction
budgets = json.loads((ROOT / "tests/structure_budgets.json").read_text())
import structure  # noqa: E402  production: tests/structure.py
band = [n for n in ("FRACTION_METRICS", "NEVER_RERECORDED") if hasattr(structure, n)]
cur("b180263d06", "python3: 'cross_seam_fraction' in tests/structure_budgets.json; hasattr(tests/structure.py, FRACTION_METRICS|NEVER_RERECORDED)",
    f"budgeted: {'cross_seam_fraction' in budgets}; band categories present: {band}", "cross_seam_fraction" in budgets and bool(band),
    "cross_seam_fraction is budgeted nowhere and tests/structure.py holds neither FRACTION_METRICS nor NEVER_RERECORDED: the metric and its band were retired on 2026-09-10 (structure.py's own record).")

# 4. the verdict grammar
vs = re.search(r"^verdict_sha\(\) \{.*?^\}", (ROOT / "tools/audit/seat/bus.sh").read_text(), re.M | re.S).group(0)


def vsha(line):
    return subprocess.run(["bash", "-c", vs + '\nverdict_sha "$1"', "_", line], capture_output=True, text=True).returncode == 0


forms = {"Fix review: merge": vsha("Fix review: merge"), "Fix review: blocked — harness gap": vsha("Fix review: blocked — harness gap"),
         "Fix review: merge <sha40>": vsha("Fix review: merge " + "a" * 40), "Fix review: blocked <sha40> harness: gap": vsha("Fix review: blocked " + "a" * 40 + " harness: gap")}
cur("de0a470338", "bash: tools/audit/seat/bus.sh's verdict_sha() over the sentence's two forms and the current grammar",
    "; ".join(f"{k!r}: {'accepted' if v else 'refused'}" for k, v in forms.items()),
    forms["Fix review: merge"] and forms["Fix review: blocked — harness gap"],
    "Both forms the sentence gives are refused by verdict_sha(): a verdict line now names the 40-hex head, and a blocked one a class (`Fix review: blocked <sha40> <class>: <why>`).")

# 5. fixer.md step 5 and the gate lock
fx = (ROOT / layout.locate("tools/audit/briefs/fixer.md", root=ROOT)).read_text()
step5 = re.search(r"^5\. .*?(?=^6\. )", fx, re.M | re.S).group(0)
locks = len(re.findall(r"gate.lock|gate_lock|lease|\block\b", step5))
cur("531c99db25", "python3: lock/lease mentions in step 5 of dev/governance/roles/fixer.md (tools/audit/briefs/fixer.md via tests/layout.py:locate)",
    f"{locks} mentions of a gate lock or lease in step 5", locks > 0,
    "fixer.md step 5 no longer mentions the gate lock at all: it measures the scope with closure.py select and runs what it names; the lease is gate-scoping.md's.")

# 6. stamp.py's flags and its REST fallback
import stamp  # noqa: E402  production: tools/release/stamp.py
src_flags = subprocess.run([sys.executable, "tools/release/stamp.py", "--help"], cwd=ROOT, capture_output=True, text=True, timeout=60).stdout
fl = {f: (f in src_flags) for f in ("--push", "--push-key", "--known-hosts", "--allow-red")}
cur("7869b20943", "python3 tools/release/stamp.py --help", f"flags listed: {fl}", all(fl[f] for f in ("--push", "--push-key", "--known-hosts")), "a flag is missing")
cur("5f2d838dcc", "python3 tools/release/stamp.py --help", f"--allow-red listed: {fl['--allow-red']}", fl["--allow-red"], "no --allow-red")
gs = (stamp.gate_source(lambda n: None), stamp.gate_source(lambda n: "/usr/bin/gh"))
cur("587d8c2ab2", "python3: tools/release/stamp.py:gate_source with and without gh on PATH", f"no gh -> {gs[0]}, gh -> {gs[1]}", gs == ("rest", "gh"), "no REST path")
cur("90f249f693", "python3: tools/release/stamp.py:gate_source with and without gh on PATH", f"no gh -> {gs[0]}, gh -> {gs[1]}", gs == ("rest", "gh"), "no REST path")

# 7. env_drift's claimed/may-drift refusal
import env_drift  # noqa: E402  production: tests/env_drift.py
md_name = sorted(getattr(env_drift, "MAY_DRIFT_ALLOWED", {"x": 1}))[0]
both = env_drift.may_drift_error({md_name: "r"}, {md_name: ["up"]})
neither = env_drift.may_drift_error({}, {})
cur("c292aa793e", "python3: tests/env_drift.py:may_drift_error with one name both claimed and may-drift (null: neither)",
    f"both -> {str(both)[:100]!r}; neither -> {neither!r}", bool(both) and neither is None, "the pair is admitted")
cur("55b0b469c0", "python3: tests/env_drift.py:may_drift_error with one name both claimed and may-drift",
    f"refused: {bool(both)}", bool(both), "the pair is admitted")

# 8. closure.py: docs/ is INERT, closure.py is a gate file, a gate file selects everything
import closure  # noqa: E402  production: tests/closure.py
inert_docs = "docs/" in closure.INERT
gf = "tests/closure.py" in closure.GATE_FILES
cur("ac6b9c13af", "python3: 'docs/' in tests/closure.py:INERT", f"{inert_docs}", inert_docs, "docs/ is not INERT")
cur("fb6b744f97", "python3: 'tests/closure.py' in tests/closure.py:GATE_FILES", f"{gf}", gf, "not a gate file")
sel = closure.select(["tests/run.sh"])
cur("09de826724", "python3: tests/closure.py:select(['tests/run.sh'])", f"mode={sel['mode']}, run={len(sel['run'])} scripts", sel["mode"] == "full",
    "a gate file is not read as run-everything")

# 9. what the documentation claims about other files
arch = (ROOT / "docs/architecture.md").read_text()
old = "65 entities / 55 sensors, 4 binary sensors, 4 buttons, 1 switch, 1 climate"
cur("af4cfd50a9", "python3: docs/architecture.md contains the quoted outputs-node text", f"occurrences: {arch.count(old)}", old in arch,
    "docs/architecture.md no longer reads that text; tests/entities.py now checks architecture.md's opening counts (#939 block).")
ent = (ROOT / "tests/entities.py").read_text()
arch_census = 'Path("docs/architecture.md").read_text()' in ent
cur("65c5554e89", "python3: tests/entities.py reads docs/architecture.md (its #939 census)", f"entities.py reads architecture.md: {arch_census}", not arch_census,
    "'no check reads it -- tests/entities.py's census covers README.md only': tests/entities.py now reads docs/architecture.md and checks its counts.")
readme = (ROOT / "README.md").read_text()
badge = re.search(r"\[!\[License: MIT\]\([^)]*\)\]\(([^)]*)\)", readme)
cur("3d35add018", "python3: the README's License badge link target", f"target: {badge.group(1) if badge else None}", bool(badge) and not badge.group(1).startswith("http"),
    "the badge's target is now absolute (https://github.com/.../LICENSE), the repair the paragraph's own control names; it is no longer 'still unfixed'.")
import ast  # noqa: E402
_pv_src = (ROOT / "tests/plan_view.py").read_text()
_pv_expr = next(n.value for n in ast.parse(_pv_src).body if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "_two_zone" for t in n.targets))
_pv_code = compile(ast.Expression(_pv_expr), "tests/plan_view.py:_two_zone", "eval")
_pv = []
for _val in (None, "1"):
    with mock.patch.dict(os.environ, {} if _val is None else {"HPO_PLAN_TWO_ZONE": _val}, clear=False):
        if _val is None:
            os.environ.pop("HPO_PLAN_TWO_ZONE", None)
        _pv.append(eval(_pv_code, {"os": os}))
cur("b72408d00e", "python3: tests/plan_view.py's `_two_zone` assignment, evaluated from its AST without and with HPO_PLAN_TWO_ZONE=1",
    f"unset -> {_pv[0]}, '1' -> {_pv[1]}", _pv == [False, True], "the switch differs")

# 10. references that are the claim
w3l = (ROOT / ".claude/workflows/wave-3l-groups.json").is_file()
cur("ab6c3b8fbe", "python3: .claude/workflows/wave-3l-groups.json exists", f"{w3l}", w3l, "absent")
rost = git("cat-file", "-e", "d5d8c4a:.claude/workflows/wave-1b-groups.json")
cur("8bb4411cc1", "git cat-file -e d5d8c4a:.claude/workflows/wave-1b-groups.json", f"resolves: {rost is not None}", rost is not None, "the roster is not at d5d8c4a")
v = (git("show", "4b6e076:VERSION") or "").strip()
cur("4b7aa3d51c", "git show 4b6e076:VERSION", f"VERSION at 4b6e076: {v!r}", v == "6.3.9", "not v6.3.9")
dec15 = sorted(p.name for p in (ROOT / "dev/governance/decisions").glob("0015-*"))
cur("fed4cc1dd5", "python3: dev/governance/decisions/0015-*; git cat-file -e 30c57744a", f"{dec15}; 30c57744a resolves: {resolve_sha('30c57744a')}",
    bool(dec15) and bool(resolve_sha("30c57744a")), "a reference does not resolve")
roles = [n for n in ("architect-planner.md", "plan-review.md") if (ROOT / "dev/governance/roles" / n).is_file()]
cur("f8a008dc60", "python3: dev/governance/roles/{architect-planner,plan-review}.md exist", f"{roles}", len(roles) == 2, "a role contract is missing")
sc = subprocess.run([sys.executable, "tools/audit/archscore/score.py", "--help"], cwd=ROOT, capture_output=True, text=True, timeout=120)
cur("12a885445c", "python3 tools/audit/archscore/score.py --help", f"--diff in usage: {'--diff' in sc.stdout + sc.stderr}", "--diff" in sc.stdout + sc.stderr, "no --diff")
gd = subprocess.run([sys.executable, "tests/golden.py", "--help"], cwd=ROOT, capture_output=True, text=True, timeout=120, env=dict(os.environ, PYTHONPATH="tests/hastub"))
gtxt = gd.stdout + gd.stderr
cur("05820d6641", "python3 tests/golden.py --help", f"--record: {'--record' in gtxt}, --only: {'--only' in gtxt}", "--record" in gtxt and "--only" in gtxt, "a flag is missing")
cur("649268d0d6", "python3: tests/structure.py exists and imports", f"imported {structure.__file__.split('/')[-1]}", True, "")

# Paths the sentence uses as an example or a name prefix, examined by hand: not a claim that the file exists.
EXAMPLES = {
    "389090c33a": "`docs/img/a.svg` is the control's hypothetical reference-link target, not a cited file",
    "5faa51088f": "`docs/arch.md` is a sample input string to the renderer's rule, not a cited file",
    "abaee7deb6": "`docs/decisions/0002` is a name prefix of decision 0002 at its pre-move directory (now dev/governance/decisions/0002-*); the standing-cost figures are dated measurements",
    "1211f3a6f0": "`docs/COMMON.md`, `docs/fixer.md`, `docs/gate-scoping.md`, `docs/Zednotes.md` are the planted probe files of a past lint escape, never meant to exist",
    "5b638c2239": "`tools/audit/round2/anything.py` is a hypothetical file the sentence uses to show the escape",
}

# --- every unit -----------------------------------------------------------------------------------
units = text_ledger.units_of(DOC, (ROOT / DOC).read_text(encoding="utf-8"), "D6")
out_rows, d2 = [], 0
stats = {"paths": 0, "now": 0, "moved": 0, "gone": 0, "never": 0, "unknown": 0, "shas": 0, "sha_ok": 0, "sha_missing": 0}
never_list, sha_missing = [], []
for uid, line, kind, t in units:
    h = uid.split("#")[1].split(".")[0]
    paths, shas = refs(t)
    res = []
    kinds = []
    for p in sorted(paths):
        stats["paths"] += 1
        if p.startswith("@basename:"):
            b = p.split(":", 1)[1]
            k, d = ("now", "basename in tree") if b in basenames else ("unknown", "basename not in the tree")
            p = b
        else:
            k, d = resolve_path(p)
        stats[k] += 1
        kinds.append(k)
        res.append(f"{p}: {k} ({d})")
        if k == "never":
            never_list.append((uid, p))
    sha_bad = []
    for s in sorted(shas):
        stats["shas"] += 1
        ok = resolve_sha(s)
        if ok:
            stats["sha_ok"] += 1
        elif ok is False:
            stats["sha_missing"] += 1
            sha_bad.append(s)
            sha_missing.append((uid, s))
        res.append(f"{s}: {'commit' if ok else 'no commit' if ok is False else 'unread'}")
    if h in CUR:
        cmd, r, verdict, truth = CUR[h]
        out_rows.append([uid, line, "claim", cmd, r + (" | refs: " + "; ".join(res) if res else ""), verdict, truth])
        continue
    has_claim = bool(paths or shas or re.search(r"#\d+|\d", t))
    if not has_claim:
        out_rows.append([uid, line, "no-claim", "", "", "-", ""])
        continue
    cmd = SELF + " (reference pass: tree, tests/layout.py:locate, git log/cat-file)"
    if h in EXAMPLES:
        out_rows.append([uid, line, "claim", cmd, "; ".join(res), "unverifiable", EXAMPLES[h]])
    elif "never" in kinds:
        bad = [p for (u, p) in never_list if u == uid]
        out_rows.append([uid, line, "claim", cmd, "; ".join(res), "false", f"never in the baseline's tree or history: {', '.join(bad)}"])
    elif sha_bad:
        out_rows.append([uid, line, "claim", cmd, "; ".join(res), "unverifiable",
                         f"{', '.join(sha_bad)} is not in the --repo clone's object store: a pull-request head or a branch commit this clone never fetched is indistinguishable from a wrong SHA without GitHub, which D6 does not read"])
    elif "gone" in kinds:
        d2 += 1
        out_rows.append([uid, line, "claim", cmd, "; ".join(res), "stale",
                         "[D2 path] a cited path has left the tree; tests/layout.json lists this file historical (tvofi's D2), so the spelling is kept as written"])
    else:
        out_rows.append([uid, line, "claim", cmd, "; ".join(res) if res else "no repository reference to resolve", "unverifiable",
                         ("references resolve; " if res else "") + "the rest is dated programme history (issues, pull requests, reviews, sessions, measurements at a past head) that the baseline tree does not decide and GitHub, which D6 does not read, holds"])

clean = lambda s: " ".join(str(s).replace("\t", " ").split())
with open(HERE / "ledger_plan.tsv", "w", encoding="utf-8") as f:
    f.write("\t".join(text_ledger.HEADER) + "\n")
    for r in out_rows:
        f.write("\t".join(clean(x) for x in r) + "\n")
wrong = [r for r in out_rows if r[5] in ("false", "stale") and not r[6].startswith("[D2 path]")]
for k, v in stats.items():
    print(f"RESULT ref_{k}={v}")
for u, p in never_list[:40]:
    print(f"NEVER {u} {p}")
for u, s in sha_missing[:40]:
    print(f"NOSHA {u} {s}")
for r in wrong:
    print(f"WRONG {r[0]} line {r[1]} {r[5]}: {r[6][:150]}")
print(f"RESULT units={len(units)} rows={len(out_rows)}")
print(f"RESULT curated_rows={sum(1 for r in out_rows if r[0].split('#')[1].split('.')[0] in CUR)}")
print(f"RESULT no_claim_rows={sum(r[2] == 'no-claim' for r in out_rows)}")
print(f"RESULT unverifiable_rows={sum(r[5] == 'unverifiable' for r in out_rows)}")
print(f"RESULT true_rows={sum(r[5] == 'true' for r in out_rows)}")
print(f"RESULT d2_path_rows={d2}")
print(f"RESULT wrong_rows={len(wrong)} rows")
tp, tt = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt}")
