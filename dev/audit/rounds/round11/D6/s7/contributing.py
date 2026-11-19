#!/usr/bin/env python3
"""D6-s7: every claim of docs/CONTRIBUTING.md checked against the code that decides it.

Metric (one line): false_rows = units of docs/CONTRIBUTING.md whose executed check
contradicts the sentence; per arm, the arm's own count is printed beside it.
Count keys: `ci_skipped_switches` counts the prelude OUTPUTS (tools/ci/prelude.py:outputs)
a fork pull_request run gets that are not their full-run value (scope != full, a
LANE_GATE input "false", a CodeQL leg "skip"); `class_mismatch_*` counts tracked paths
whose class by tools/pr/outside.py:Rules.classify differs from the class the page's
table gives; `head_na_refused` is policy_lint.mjs --pr-body's exit on a body whose
`## Head` is `n/a: <reason>`.

Run (from the export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D6/s7/contributing.py [--repo GIT_DIR] [--perturb ARM]
  --repo: a git repository holding the baseline commit (default $HPO_REPO); the body arm
          clones it --shared into a temp root and runs policy_lint.mjs there. Without it
          that arm prints `unavailable` and its rows say so.
  --perturb machinery-true : tools/ci/prelude.py:machinery patched to return True
          (every machinery lane runs): ci_skipped_switches must go DOWN (21 -> 9, 4 per arm).
  --perturb fork-full : prelude.py's scope line edited in memory to `"scope": "full"`, machinery
          forced True and codeql_scope.decide forced to analyze (the sentence made true):
          ci_skipped_switches TO ZERO and false_rows DOWN by 1 (4 -> 3 with --repo).
  --perturb delivery-row-refused : outside.Rules.free patched to drop its delivery-row
          clause: class_mismatch_delivery must go TO ZERO (1788 -> 0), class_mismatch_paths 3 -> 2.
Writes ledger_contributing.tsv beside itself (the TSV rows text_ledger.py check reads).
D6S7_BUS_SELFTEST=<file> hands it a transcript of `bash tools/audit/seat/bus.sh --self-test`
run in a shared clone at the baseline (the adoption rows read its `ok` lines).

Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (all exact, counts):
false_rows=3 (4 with --repo: the `## Head` n/a row joins); ci_skipped_switches=21 over the three
fork arms (8 docs-only, 5 package-only, 8 tests-script), ci_null_push=0;
class_mismatch_paths=3, class_mismatch_delivery=1788. Machine: box B13 (light seat), linux x86_64.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
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
DOC = "docs/CONTRIBUTING.md"
sys.path[:0] = [str(ROOT / "tools/ci"), str(ROOT / "tools/pr"), str(ROOT / "tools/audit")]
import prelude  # noqa: E402  production: the umbrella's prelude
import codeql_scope  # noqa: E402
import outside  # noqa: E402  production: the outside-contributor contract
import text_ledger  # noqa: E402

t_proc0, t_thr0 = time.process_time(), time.thread_time()
ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=os.environ.get("HPO_REPO", ""))
ap.add_argument("--perturb", default="", choices=["", "machinery-true", "delivery-row-refused", "fork-full"])
a = ap.parse_args()

rows = {}  # unit hash prefix -> (command, result, verdict, truth)
SELF = "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D6/s7/contributing.py"


def row(h, arm, result, verdict, truth=""):
    rows[h] = (f"{SELF} (arm {arm})", result, verdict, truth)


# --- arm ci: what a fork pull request's run skips ---------------------------------
def fork_ctx(event="pull_request"):
    head = "f" * 40
    ev = {"action": "synchronize", "pull_request": {"number": 7, "labels": [],
          "base": {"sha": "b" * 40, "ref": "main"},
          "head": {"sha": head, "repo": {"full_name": "contributor/heatpump_optimizer"}}}}
    if event == "push":
        ev = {"before": "b" * 40}
    env = {"GITHUB_SHA": head, "GITHUB_REF": "refs/pull/7/merge" if event != "push" else "refs/heads/main",
           "GITHUB_REPOSITORY": "tvofi/heatpump_optimizer", "GITHUB_RUN_ID": "1"}
    return prelude.context(event, ev, env)


def no_api(path, params=None):
    raise AssertionError(f"a code run asked the API for {path}")


def skipped(out):
    n = int(out["scope"] != "full")
    gates = prelude.LANE_GATE
    n += sum(1 for _job, inp in gates.items() if out.get(inp) == "false")
    n += sum(1 for v in json.loads(out["legs"]).values() if v == "skip")
    return n


ARMS = {"docs-only (class F)": ["docs/setup.md"],
        "package-only (class F)": ["custom_components/heatpump_optimizer/const.py"],
        "tests script (class O)": ["tests/features.py"]}
if a.perturb == "fork-full":
    # The sentence made true in memory: tools/ci/prelude.py's scope line edited to give every
    # event `full` (one line), machinery forced on, and every CodeQL leg analyzed.
    _src = (ROOT / "tools/ci/prelude.py").read_text()
    _line = '"scope": "full" if ev == "push" else "auto",'
    assert _line in _src, "perturbation anchor moved"
    exec(compile(_src.replace(_line, '"scope": "full",'), str(ROOT / "tools/ci/prelude.py"), "exec"), prelude.__dict__)
ctxm = (mock.patch.object(prelude, "machinery", lambda *x, **k: True) if a.perturb in ("machinery-true", "fork-full")
        else mock.patch.object(prelude, "machinery", prelude.machinery))
if a.perturb == "fork-full":
    _decide = codeql_scope.decide
    codeql_scope.decide = lambda lang, ev, files, ref="", proven=None: ("analyze", "perturbed")
ci_total, ci_lines = 0, []
with ctxm:
    for name, files in ARMS.items():
        out, why = prelude.outputs(fork_ctx(), files, no_api, selftests=lambda c: "all")
        k = skipped(out)
        ci_total += k
        ci_lines.append(f"{name}: scope={out['scope']} machinery={out['machinery']} rowblind={out['machinery_rowblind']} legs={out['legs']} -> {k}")
        print(f"RESULT ci_skipped[{name}]={k} switches")
    pout, _ = prelude.outputs(fork_ctx("push"), ["docs/setup.md"], no_api, selftests=lambda c: "all")
    ci_null = skipped(pout)
print(f"RESULT ci_skipped_switches={ci_total} switches")
print(f"RESULT ci_null_push={ci_null} switches")
row("1b9b0221e7", "ci", f"ci_skipped_switches={ci_total} over 3 fork pull_request arms (" + "; ".join(ci_lines) + f"); push null control {ci_null}",
    "false" if ci_total else "true",
    "tools/ci/prelude.py:outputs gives every pull_request run, a fork's included, scope=auto (the gate runs only the scripts the diff reaches, tests/closures.json); "
    "a product-only diff sets machinery/machinery_rowblind false so the four LANE_GATE lanes stand down, and a diff with no custom_components/ or .github/ path skips "
    "every CodeQL leg (codeql_scope.decide). Only a push (to main) runs full." if ci_total else "")

# --- arm classes: the path table against Rules.classify ---------------------------
codeowners = (ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8")
rules = outside.Rules("HEAD", ROOT, codeowners=codeowners)
if a.perturb == "delivery-row-refused":
    _free = outside.Rules.free
    rules.free = lambda p, pr: (not p.startswith("dev/programme/delivery/")) and _free(rules, p, pr)
gate = set(outside.gate_files(ROOT))


def doc_class(p):
    """The page's table, read literally, first row first."""
    if (p.startswith(("custom_components/", "blueprints/")) or p == "README.md"
            or (p.startswith("docs/") and not p.startswith("docs/site/") and p.endswith((".md", ".png", ".svg")))):
        return "F"
    if (p.startswith((".github/", "tools/", ".claude/", "dev/governance/", "tests/golden/", "tests/mutation_ledger/"))
            or p.endswith("_budgets.json") or p == "tests/closures.json" or p in gate or "/" not in p):
        return "R"
    if p.startswith(("tests/", "docs/")):
        return "O"
    return "R"   # "Everything else", "any new top-level directory"


def tracked():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in (".git", "node_modules", "__pycache__")]
        for f in fn:
            p = os.path.relpath(os.path.join(dp, f), ROOT)
            if not p.startswith("dev/audit/rounds/round11/"):   # this round's own output, not the baseline
                yield p


mism = {}
nfiles = 0
for p in tracked():
    nfiles += 1
    m = re.fullmatch(r"dev/programme/delivery/(\d+)\.md", p)
    d, c = doc_class(p), rules.classify(p, int(m.group(1)) if m else 0)
    if d != c:
        key = ("dev/programme/delivery/<its own N>.md" if m else
               "CODEOWNERS-owned path outside tests/ and docs/" if d == "R" and c == "O" else
               "policy file under tests/ (POLICY_GLOBS)" if d == "O" and c == "R" else f"{d}->{c}")
        mism.setdefault((key, d, c), []).append(p)
print(f"RESULT class_files_compared={nfiles} files")
print(f"RESULT class_mismatch_paths={len(mism)} path classes")
print(f"RESULT class_mismatch_delivery={sum(len(v) for (k, _, _), v in mism.items() if k.startswith('dev/programme/delivery'))} files")
for (k, d, c), v in sorted(mism.items()):
    print(f"RESULT class_mismatch[{k}: page {d}, code {c}]={len(v)} files  e.g. {', '.join(sorted(v)[:3])}")
mdesc = "; ".join(f"{k}: page says {d}, Rules.classify says {c} ({len(v)} files, e.g. {sorted(v)[0]})" for (k, d, c), v in sorted(mism.items()))
F_rows = [x for x in mism if x[1] == "F"]
O_rows = [x for x in mism if x[1] == "O"]
R_rows = [x for x in mism if x[1] == "R"]
row("dbb1544ac0", "classes", f"{nfiles} paths compared; page-F paths classed otherwise: {sum(len(mism[x]) for x in F_rows)}", "true" if not F_rows else "false",
    "" if not F_rows else mdesc)
row("c5ba90bf74", "classes", f"page-O paths classed otherwise: {sum(len(mism[x]) for x in O_rows)} ({'; '.join(f'{x[0]} -> {x[2]}: {sorted(mism[x])}' for x in O_rows)})",
    "true" if not O_rows else "false",
    "" if not O_rows else "tests/README.md is in policy_lint.mjs's POLICY_GLOBS, which Rules.refused tests first: class R, not owner-read; the table names the policy set only as dev/governance/.")
row("513c74e002", "classes", f"page-R paths classed otherwise: {sum(len(mism[x]) for x in R_rows)} ({'; '.join(f'{x[0]} -> {x[2]}: {len(mism[x])}' for x in R_rows)})",
    "true" if not R_rows else "false",
    "" if not R_rows else "the row calls everything not listed above refused, but Rules.free admits the pull request's own dev/programme/delivery/<N>.md (class F) and "
    "Rules.classify gives the CODEOWNERS-owned paths outside tests/ and docs/ class O: "
    + ", ".join(sorted(p for x in R_rows if x[2] == "O" for p in mism[x])) + ".")
# probes for the "new top-level directory" clause and .cursor/
probes = {"newtop/x.md": "R", ".cursor/rules/x.mdc": "R", "VERSION": "R", "RELEASE_NOTES.md": "R", outside.MANIFEST: "F",
          "docs/img/card/make_card_figures.mjs": "O", "docs/site/a.css": "O", "docs/index.html": "O"}
pbad = [p for p, want in probes.items() if rules.classify(p, 0) != want]
print(f"RESULT class_probe_mismatch={len(pbad)} probes")
row("1a87df45d6", "classes", f"probes {sorted(probes)}: {len(pbad)} classed otherwise", "true" if not pbad else "false", ", ".join(pbad))

# --- arm shape: branch name, base ------------------------------------------------------
def facts(ref="fix/issue-12", base_ref="main", head_repo="contributor/heatpump_optimizer"):
    return {"author": {}, "state": "open", "head_repo": head_repo, "head_ref": ref, "head_owner": "contributor",
            "head": "f" * 40, "base_repo": "tvofi/heatpump_optimizer", "base_ref": base_ref}


REPO = "tvofi/heatpump_optimizer"
names = {"fix/issue-12": True, "a" * 100: True, "a" * 101: False, "main": False, "-x": False, "_x": False,
         ".x": False, "9.x_y-z/w": True, "x y": False, "x+y": False, "x$(id)": False, "x~1": False}
nbad = [n for n, ok in names.items() if (not outside.shape(facts(n), REPO)) != ok]
print(f"RESULT branch_name_disagree={len(nbad)} of {len(names)} names")
row("6a50b0b548", "shape", f"{len(names)} names through outside.shape: {len(nbad)} disagree with the sentence", "true" if not nbad else "false", ", ".join(nbad))
row("3cd947c1ed", "shape", f"refused names among the probes refused by outside.shape: {sum(1 for n, ok in names.items() if not ok and outside.shape(facts(n), REPO))}/{sum(1 for ok in names.values() if not ok)}", "true")
bad_base = outside.shape(facts(base_ref="dev"), REPO)
print(f"RESULT base_not_main_refused={int(bool(bad_base))}")
row("6011328e21", "shape", f"base dev refused: {bool(bad_base)}", "true" if bad_base else "false", "" if bad_base else "outside.shape admits a base other than main")

# --- arm check: one pull request per head, the version files, the allowlist -------------
gate_mod = outside.load_gate(ROOT)
ALLOW = {"contributors": [{"login": "contributor", "id": 4242, "since": "2026-11-12", "decision": "0017"}]}
AUTHOR = {"login": "contributor", "id": 4242, "type": "User"}


def run_check(paths, others=(), versions=("1.0.0", "1.0.0"), author=AUTHOR):
    f = facts(); f["author"] = author
    with mock.patch.object(outside, "pull_facts", lambda r, n, p=None: f), \
         mock.patch.object(outside, "read_allowlist", lambda ref: ALLOW), \
         mock.patch.object(outside, "other_pulls", lambda r, n, ff: list(others)), \
         mock.patch.object(outside, "changed", lambda ref, head: ("b" * 40, list(paths))), \
         mock.patch.object(outside, "manifest_version", lambda ref: (True, versions[0] if ref == "b" * 40 else versions[1])), \
         mock.patch.object(outside, "show", lambda ref, p: codeowners if p == outside.CODEOWNERS else None):
        return outside.check(REPO, 7, "origin/main", gate=gate_mod, fetch=False)


rc_ok, out_ok = run_check(["custom_components/heatpump_optimizer/const.py"])
rc_two, out_two = run_check(["custom_components/heatpump_optimizer/const.py"], others=(8,))
rc_ver, out_ver = run_check([outside.MANIFEST], versions=("1.0.0", "1.0.1"))
rc_vf, _ = run_check(["VERSION"])
rc_rn, _ = run_check(["RELEASE_NOTES.md"])
rc_na, out_na = run_check(["custom_components/heatpump_optimizer/const.py"], author={"login": "stranger", "id": 1, "type": "User"})
print(f"RESULT check_null_admitted_rc={rc_ok}")
print(f"RESULT second_pull_refused_rc={rc_two}")
print(f"RESULT manifest_version_refused_rc={rc_ver} VERSION_rc={rc_vf} RELEASE_NOTES_rc={rc_rn}")
print(f"RESULT not_allowlisted_rc={rc_na}")
row("f423048b38", "check", f"outside.check rc {rc_two} with another pull request at the head (null rc {rc_ok}): {out_two[-1][:120]}", "true" if rc_two == 1 and rc_ok == 0 else "false", "" if rc_two == 1 else "not refused")
row("2379c0c7f8", "check", f"manifest version change rc {rc_ver}; VERSION rc {rc_vf}; RELEASE_NOTES.md rc {rc_rn} (null rc {rc_ok})",
    "true" if (rc_ver, rc_vf, rc_rn) == (1, 1, 1) else "false", "" if (rc_ver, rc_vf, rc_rn) == (1, 1, 1) else "one of the three is admitted")
row("fe3f041d2b", "check", f"manifest version change refused: {out_ver[-1][:140]}", "true" if rc_ver == 1 else "false", "" if rc_ver == 1 else "admitted")
row("3dfe18ee54", "check", f"allowlisted author on a class-F diff: rc {rc_ok} ({out_ok[-1][:100]}); allowlist {outside.ALLOWLIST} owned by CODEOWNERS: {rules.is_owned(outside.ALLOWLIST)}",
    "true" if rc_ok == 0 else "false", "" if rc_ok == 0 else "an allowlisted class-F pull request is refused")

# --- arm review: the class-O approval words -----------------------------------------
H = "c" * 40


def rv(state, body, cid=H):
    return {"id": 1, "user": {"login": gate_mod.OWNER_LOGIN, "id": gate_mod.OWNER_ID, "type": "User"},
            "state": state, "body": body, "commit_id": cid}


plain = outside.owner_read([rv("APPROVED", f"Outside read: {H}")], H, gate_mod, REPO, lambda x, y: False)[0]
words = {w: outside.owner_read([rv("APPROVED", f"Outside read: {H}\nread by the {w}")], H, gate_mod, REPO, lambda x, y: False)[0]
         for w in ("seat", "mandate", "orchestrator")}
later_cr = outside.owner_read([rv("APPROVED", f"Outside read: {H}"), rv("CHANGES_REQUESTED", "no")], H, gate_mod, REPO, lambda x, y: False)[0]
dismissed = outside.owner_read([rv("DISMISSED", f"Outside read: {H}")], H, gate_mod, REPO, lambda x, y: False)[0]
other_head = outside.owner_read([rv("APPROVED", f"Outside read: {'d' * 40}", "d" * 40)], H, gate_mod, REPO, lambda x, y: False)[0]
print(f"RESULT owner_plain_admitted={int(plain)}")
print(f"RESULT agent_words_refused={sum(not v for v in words.values())} of 3")
print(f"RESULT later_changes_or_dismissal_refused={int(not later_cr) + int(not dismissed)} of 2")
row("1955f7faa1", "review", f"owner_read admits `Outside read: <head40>`: {plain}; a read of another head with no carry: {other_head}", "true" if plain and not other_head else "false", "" if plain else "refused")
row("ea3a802bb1", "review", f"owner_read admits the one-line body at the head: {plain}", "true" if plain else "false", "" if plain else "refused")
row("489588f4aa", "review", f"owner_read with each word added: {words} (False = refused)", "true" if not any(words.values()) else "false", "" if not any(words.values()) else "a word is admitted")
row("9be1c6c86c", "review", f"APPROVED then CHANGES_REQUESTED admitted: {later_cr}; DISMISSED admitted: {dismissed}", "true" if not later_cr and not dismissed else "false", "" if not (later_cr or dismissed) else "admitted")
row("caf0a5018e", "review", f"plain body admitted {plain}; the agent words refuse ({sum(not v for v in words.values())}/3)", "true")
row("51d48d1f8f", "review", f"class O admitted by the owner's own review: {plain}", "true" if plain else "false", "" if plain else "refused")

# --- arm files: references that must resolve ------------------------------------------
dec = sorted(p.name for p in (ROOT / "dev/governance/decisions").glob("0017-*"))
row("79e8f750c5", "files", f"dev/governance/decisions/0017-*: {dec}", "true" if dec else "false", "" if dec else "no decision 0017")
tmpl = (ROOT / ".github/PULL_REQUEST_TEMPLATE.md").is_file()
row("a80b006db9", "files", f".github/PULL_REQUEST_TEMPLATE.md exists: {tmpl}", "true" if tmpl else "false", "" if tmpl else "missing")
fr = (ROOT / "dev/governance/roles/fix-review.md").is_file()
row("9d7358c7b6", "files", f"dev/governance/roles/fix-review.md exists: {fr}", "true" if fr else "false", "" if fr else "missing")

# --- arm body: policy_lint.mjs --pr-body in a shared clone of the baseline ---------------
body_res = None
if a.repo and Path(a.repo).exists():
    T = Path(tempfile.mkdtemp())
    env = dict(os.environ, HPO_PLANDATA=str(T / "plandata"))
    w = T / "w"
    subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", a.repo, str(w)], check=True)
    subprocess.run(["git", "-C", str(w), "checkout", "-q", "--detach", BASELINE], check=True)

    def body(head_text):
        heads = ["Mutation proof", "Null control", "Figures", "Red checks", "Forward-carry", "Friction"]
        return "Why.\n\n## Head\n\n" + head_text + "\n" + "".join(f"\n## {h}\n\nn/a: not applicable to this change\n" for h in heads)

    def lint(text, *author):
        f = T / "body.md"; f.write_text(text)
        r = subprocess.run(["node", "tools/policy/policy_lint.mjs", "--pr-body", str(f), "--head", BASELINE, *author],
                           cwd=w, env=env, capture_output=True, text=True, timeout=600)
        return r.returncode, [l.strip() for l in (r.stdout + r.stderr).splitlines() if "ERROR" in l]

    rc_named, e_named = lint(body(BASELINE), "--author", "contributor", "--outside-author", "contributor")
    rc_na_head, e_na = lint(body("n/a: no measurement in a documentation change"), "--author", "contributor", "--outside-author", "contributor")
    rc_stranger, e_str = lint(body(BASELINE), "--author", "stranger")
    body_res = (rc_named, rc_na_head, rc_stranger)
    print(f"RESULT body_all_na_but_head_rc={rc_named}")
    print(f"RESULT head_na_refused={int(rc_na_head != 0)}")
    print(f"RESULT stranger_author_refused={int(rc_stranger != 0)}")
    row("4328f74596", "body", f"policy_lint --pr-body: every heading `n/a: <reason>` but `## Head` naming the head rc {rc_named}; `## Head` as `n/a: <reason>` rc {rc_na_head} ({(e_na or [''])[0][:160]})",
        "false" if rc_na_head else "true",
        "`## Head` cannot be `n/a: <reason>`: checkPrBody requires it to name the head commit, so one of the template's seven headings is not 'content or n/a'." if rc_na_head else "")
    row("b69925e785", "body", f"policy_lint --pr-body --author stranger (no allowlist admission) rc {rc_stranger}: {(e_str or [''])[0][:160]}", "true" if rc_stranger else "false", "" if rc_stranger else "admitted")
    row("c34315780e", "body", f"author arm: only the hpo-author App or an admitted outside author passes (stranger rc {rc_stranger}, admitted outside author rc {rc_named})", "true" if rc_stranger and not rc_named else "false",
        "" if rc_stranger and not rc_named else "author arm differs")
else:
    print("RESULT body_arm=unavailable (no --repo)")
    for h in ("4328f74596", "b69925e785", "c34315780e"):
        row(h, "body", "body arm not run: no git repository holding the baseline was given (--repo)", "unverifiable", "policy_lint.mjs needs a git checkout; re-run with --repo")

# --- arm adopt: bus.sh's adoption rules, from its own self-test transcript ------------------
selftest = os.environ.get("D6S7_BUS_SELFTEST", "")
adopt_cases = {"0d41899ffd": ["a review commit holding a file beside VERDICT.md and ev/", "an evidence path with a space"],
               "83666ee36d": ["a comment whose first line is outside the grammar", "a verdict naming a commit that is not the live head"],
               "125db03a2b": ["a VERDICT.md whose first line is not the comment's"],
               "48c58bfcc1": ["a verdict naming a commit that is not the live head"],
               "49d1217605": ["a comment by an account that is not the allowlist entry"]}
if selftest and Path(selftest).is_file():
    txt = Path(selftest).read_text(errors="replace")
    for h, cases in adopt_cases.items():
        got = {c: bool(re.search(r"^\s*ok\b.*" + re.escape(c), txt, re.M)) for c in cases}
        rows[h] = (f"bash tools/audit/seat/bus.sh --self-test (in a shared clone at {BASELINE[:12]}), transcript {selftest}",
                   "; ".join(f"{'ok' if v else 'NOT ok'}: {c}" for c, v in got.items()), "true" if all(got.values()) else "unverifiable",
                   "" if all(got.values()) else "a case did not print ok in the transcript")
else:
    for h in adopt_cases:
        rows[h] = ("bash tools/audit/seat/bus.sh --self-test", "transcript not given (D6S7_BUS_SELFTEST)", "unverifiable", "re-run with D6S7_BUS_SELFTEST=<transcript>")

# --- the units: every one rowed -------------------------------------------------------------
NOCLAIM = {"41e81beb93", "0832010ebe", "dd3e7c13dd", "67f8f561a6", "4b4d2a931a", "82719a3847", "e0208e0241", "e8dcd70c45"}
UNVERIFIABLE = {
    "6c51756d8a": "a habit of fixes ('normally'), not a property of the code",
    "449bddf757": "needs tests/entities.py's classification check run on a planted new file; not executed by this seat",
    "9f218033b0": "a GitHub operation the project performs (merging main into a fork branch, merging the pull request); D6 reads no GitHub",
}
units = text_ledger.units_of(DOC, (ROOT / DOC).read_text(encoding="utf-8"), "D6")
out_rows = []
for uid, line, kind, t in units:
    h = uid.split("#")[1].split(".")[0]
    if h in rows:
        cmd, res, v, truth = rows[h]
        out_rows.append([uid, str(line), "claim", cmd, res, v, truth])
    elif h in UNVERIFIABLE:
        out_rows.append([uid, str(line), "claim", f"{SELF} (read: no arm)", "no executed check decides it", "unverifiable", UNVERIFIABLE[h]])
    elif h in NOCLAIM:
        out_rows.append([uid, str(line), "no-claim", "", "", "-", ""])
    else:
        out_rows.append([uid, str(line), "claim", SELF, "UNMAPPED", "unverifiable", "harness maps no check to this unit"])
clean = lambda s: " ".join(str(s).replace("\t", " ").split())
with open(HERE / "ledger_contributing.tsv", "w", encoding="utf-8") as f:
    f.write("\t".join(text_ledger.HEADER) + "\n")
    for r in out_rows:
        f.write("\t".join(clean(x) for x in r) + "\n")
false_rows = sum(r[5] == "false" for r in out_rows)
print(f"RESULT units={len(units)} rows={len(out_rows)} unmapped={sum(r[4] == 'UNMAPPED' for r in out_rows)}")
print(f"RESULT false_rows={false_rows} rows")
print(f"RESULT unverifiable_rows={sum(r[5] == 'unverifiable' for r in out_rows)} rows")
tp, tt = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt}")
