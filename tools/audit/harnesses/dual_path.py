#!/usr/bin/env python3
"""R9-RO-2: do the pinned graders grade a moved tree as they grade today's?

Metric, one line: for each grading command a base-restoring CI job runs, the
rc and normalised output on a planted tree whose data sits at the reorganised
location, against the same on today's tree; and whether each workflow's
restore step restores from a base that holds its graders at either location.

  graders   two shared clones of HEAD. `old` is the tree as committed. `new`
            applies every `tests/layout.json` move (`retired` and `lifted`),
            then puts back at the old path every file a restore pathspec of
            the merge base matches -- what CI holds while a move pull request
            is graded by the base's copy. Each command runs in both; the
            output is normalised (tree path, HEAD sha, durations, every moved
            path spelt old). Expected: every row `same`. At a merge base that
            predates the lookup the rows that read moved data differ.
  neither   the merge-base tree with one data file per grader deleted, run
            with the merge base's graders and then with HEAD's: the refusal
            must be unchanged. Expected: every row `same`.
  ci        THIS pull request's own CI: per base-restoring job, HEAD's tree
            with the job's restore pathspecs checked out from the merge base,
            then the job's grading commands. Expected: every rc equal to
            HEAD's graders on HEAD's tree. (#1886 round 1: the base parser and
            the base layout.py failed on the head, which `graders` cannot see.)
  shadow    an unowned copy at a new path must not grade in place of the
            file in use: COMMON.md grown past its cap with a pristine copy at
            its new path, and the rules grown with copies under dev/. Expected:
            policy_lint refuses each, as it refuses the growth alone.
  restore   (on request) each `Restore ...` step of HEAD's workflows, run in a clone whose
            PINNED holds the graders at the old location, at the new one, and
            at neither. Expected: rc 0, 0, non-zero; every file the step's
            pathspecs match in PINNED restored byte-identical.

    python3 tools/audit/harnesses/dual_path.py [--arm graders|neither|ci|shadow|restore] [--base REF] [--keep]

Baseline: the merge base with origin/main (`--base`, default `origin/main`).
Machine: any; node and python3 on PATH, no network (a grader that would reach
GitHub without a token prints its skip, identically in both trees).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                           text=True, check=True).stdout.strip())
BODY = ".claude/workflows/fixtures/policy-rot/prepr/good.md"
COMMANDS = [
    ("rules_sync --check", "node .claude/workflows/rules_sync.mjs --check"),
    ("codeowners_gap --check", "python3 -I tools/audit/round6/D11/fix/codeowners_gap.py --check"),
    ("policy_lint", "node .claude/workflows/policy_lint.mjs"),
    ("fragments_sync", "node .claude/workflows/fragments_sync.mjs"),
    ("policy_lint --report", "node .claude/workflows/policy_lint.mjs --report"),
    ("policy_lint --hooks", "node .claude/workflows/policy_lint.mjs --hooks"),
    ("field_coverage", "node .claude/workflows/field_coverage.mjs"),
    ("check-wave-script", "node .claude/workflows/check-wave-script.mjs"),
    ("agreement_py", "python3 -I .claude/workflows/agreement_py.py --out $T/agreement.json"),
    ("agreement", "node .claude/workflows/agreement.mjs --py-json $T/agreement.json"),
    ("brief_lint", "node .claude/workflows/brief_lint.mjs"),
    ("budget_raise_gate", "python3 -I .claude/workflows/budget_raise_gate.py --base HEAD~1 --head HEAD --pr 0"),
    ("policy_lint --pr-body", "node .claude/workflows/policy_lint.mjs --pr-body $T/body.md --head $HEAD"),
    ("figure_lint --pr-body", "node .claude/workflows/figure_lint.mjs --pr-body $T/body.md"),
    ("preflight", "bash tools/audit/preflight.sh < $T/body.md"),
    ("delivery_status --check", "python3 -I -S tests/delivery_status.py --check"),
]
# One data file per grader that reads one, deleted for the `neither` arm.
NEITHER = [".claude/workflows/policy_budgets.json", ".claude/workflows/fixtures/required-contexts.json",
           "tools/audit/rotation.json", "tools/audit/bugclasses.json", ".claude/rules/gate-scoping.md"]
# Rows whose text differs for a reason the arm does not measure; the rc must
# still agree. Each names why, so a reader can see what was set aside.
EXPECTED = {
    ("graders", "preflight"): "its staleness line counts the policy files the planted commit moves as authored "
                              "on the branch, which a move pull request's are",
    ("neither", "agreement"): "its grammar census counts the regexes HEAD's graders add",
}
_spec = importlib.util.spec_from_file_location("codeowners_gap", ROOT / "tools/audit/round6/D11/fix/codeowners_gap.py")
CG = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CG)  # the pin reader policy-docs runs: its restore grammar and its execution grammar
spec_hit = CG.spec_hit


def git(cwd, *args, check=True):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=check).stdout


def commit(tree: Path, msg: str) -> None:
    env = {**os.environ, "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"}
    subprocess.run(["git", "-c", "user.name=h", "-c", "user.email=h@invalid", "commit", "-q",
                    "--allow-empty", "--no-verify", "-m", msg], cwd=tree, env=env, check=True)


def clone(at: str, dest: Path) -> Path:
    subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", str(ROOT), str(dest)], check=True)
    git(dest, "checkout", "-q", "--detach", at)
    return dest


def moves(manifest: dict) -> list[tuple[str, str]]:
    return [(e["old"], e["new"]) for e in manifest.get("retired", []) + manifest.get("lifted", []) if e.get("new")]


def specs_in(text: str) -> list[str]:
    return [p for m in CG.RESTORE.finditer(text) for p in shlex.split(m.group(1).replace("\\\n", " "))]


def restore_specs(tree: Path) -> list[str]:
    """Every pathspec a restore names in `tree`'s workflows, and every file
    they execute: what CI holds at the base's path while a move is graded."""
    out: set[str] = set()
    for wf in sorted((tree / ".github/workflows").glob("*.yml")):
        text = wf.read_text()
        out.update(specs_in(text))
        out.update(m.group(1) for ln in text.splitlines() for m in CG.EXEC.finditer(ln))
    return sorted(out)


def apply_moves(tree: Path, pairs: list[tuple[str, str]], keep: list[str]) -> int:
    """Move every tracked file under each `old` to its `new`, then put back
    the files `keep` matches: the base's graders, restored at the old path."""
    files = git(tree, "ls-files").split("\n")
    moved = 0
    for f in filter(None, files):
        for old, new in pairs:
            if f == old or (old.endswith("/") and f.startswith(old)):
                dst = new + f[len(old):] if old.endswith("/") else new
                (tree / dst).parent.mkdir(parents=True, exist_ok=True)
                git(tree, "mv", f, dst)
                moved += 1
                if any(spec_hit(s, f) for s in keep):
                    git(tree, "checkout", "-q", "HEAD", "--", f)
                break
    return moved


def normalise(text: str, tree: Path, tmp: Path, head: str, pairs: list[tuple[str, str]]) -> str:
    text = text.replace(str(tree.resolve()), "<TREE>").replace(str(tree), "<TREE>").replace(str(tmp), "<TMP>")
    text = re.sub(head[:7] + r"[0-9a-f]{0,33}", "<HEAD>", text)
    text = re.sub(r"\b\d+(?:\.\d+)?\s?(?:ms|s)\b|seconds=[\d.]+", "<T>", text)
    text = re.sub(r"(?m)^\s+at .*\n", "", text)  # a node stack frame: async frames vary run to run
    for old, new in sorted(pairs, key=lambda p: -len(p[1])):
        text = text.replace(new.rstrip("/"), old.rstrip("/"))
    return text


def run_all(tree: Path, tmp: Path, pairs) -> dict[str, tuple[int, str]]:
    head = git(tree, "rev-parse", "HEAD").strip()
    (tmp / "body.md").write_text(git(ROOT, "show", f"HEAD:{BODY}"))
    out = {}
    env = {**os.environ, "PYTHONPATH": "tests/hastub", "T": str(tmp), "HEAD": head}
    env.pop("GITHUB_TOKEN", None)
    env.pop("GH_TOKEN", None)
    for name, cmd in COMMANDS:
        r = subprocess.run(cmd, shell=True, cwd=tree, env=env, capture_output=True, text=True)
        out[name] = (r.returncode, normalise(r.stdout + r.stderr, tree, tmp, head, pairs))
    return out


def compare(label: str, a: dict, b: dict, tmp: Path) -> int:
    bad = 0
    for name in a:
        same = a[name] == b[name]
        why = EXPECTED.get((label, name))
        bad += not (same or (why and a[name][0] == b[name][0]))
        print(f"  {label} {name}: rc {a[name][0]}/{b[name][0]} "
              f"{'same' if same else f'differs, set aside: {why}' if why else 'DIFFERS'}")
        if not same:
            p = tmp / f"{label}-{re.sub(r'[^a-z]+', '_', name)}"
            p.with_suffix(".a").write_text(a[name][1])
            p.with_suffix(".b").write_text(b[name][1])
            print(f"    diff {p.with_suffix('.a')} {p.with_suffix('.b')}")
    return bad


def arm_graders(base: str, tmp: Path) -> int:
    pairs = moves(json.loads((ROOT / "tests/layout.json").read_text()))
    old = clone("HEAD", tmp / "old")
    commit(old, "planted: nothing moved")
    new = clone("HEAD", tmp / "new")
    keep = restore_specs(clone(base, tmp / "base"))
    n = apply_moves(new, pairs, keep)
    commit(new, "planted: every move applied, the base's graders restored")
    print(f"# graders: {n} file(s) moved, {len(keep)} restore pathspec(s) of {base} kept at the old path")
    (tmp / "o").mkdir()
    (tmp / "n").mkdir()
    a = run_all(old, tmp / "o", pairs)
    b = run_all(new, tmp / "n", pairs)
    bad = compare("graders", a, b, tmp)
    print(f"RESULT graders_differ={bad} of {len(a)}")
    return bad


def arm_neither(base: str, tmp: Path) -> int:
    tree = clone(base, tmp / "neither")
    for f in NEITHER:
        (tree / f).unlink(missing_ok=True)
    git(tree, "add", "-A")
    commit(tree, "planted: the data at neither location")
    keep = restore_specs(tree) + ["tests/layout.py", "tests/layout.json"]
    commit(tree, "planted: a placeholder, so both runs see as many commits")
    (tmp / "nb").mkdir()
    a = run_all(tree, tmp / "nb", [])
    head = git(ROOT, "rev-parse", "HEAD").strip()
    files = [f for f in git(ROOT, "ls-tree", "-r", "--name-only", head).split("\n")
             if f and any(spec_hit(s, f) for s in keep) and f not in NEITHER]
    for f in files:
        (tree / f).parent.mkdir(parents=True, exist_ok=True)
        (tree / f).write_bytes(subprocess.run(["git", "show", f"{head}:{f}"], cwd=ROOT,
                                              capture_output=True, check=True).stdout)
    git(tree, "add", "-A")
    git(tree, "commit", "-q", "--amend", "--no-edit", "--allow-empty", "--no-verify")  # as many commits as the first run saw
    (tmp / "nh").mkdir()
    b = run_all(tree, tmp / "nh", [])
    # The planted commit differs, so HEAD~1 is not the same parent: compare the
    # rows a grader of the data computes, not the budget gate's diff window.
    a.pop("budget_raise_gate"), b.pop("budget_raise_gate")
    # codeowners_gap's verdict is about the base's .github read by HEAD's
    # graders, which load tests/layout.py the base's CODEOWNERS does not own;
    # its one data read, required-contexts.json, sits in a try that returns no
    # refusal when the file is at neither path, at both ends.
    print("  neither codeowners_gap --check: not compared (its verdict reads .github, not the deleted data)")
    a.pop("codeowners_gap --check"), b.pop("codeowners_gap --check")
    bad = compare("neither", a, b, tmp)
    print(f"RESULT neither_differ={bad} of {len(a)}")
    return bad


def restore_steps(tree: Path) -> list[tuple[str, str]]:
    import yaml  # the workflows are YAML; PyYAML is in every seat venv

    out = []
    for wf in sorted((tree / ".github/workflows").glob("*.yml")):
        for job, j in (yaml.safe_load(wf.read_text()).get("jobs") or {}).items():
            for s in j.get("steps") or []:
                if str(s.get("name", "")).startswith("Restore") and specs_in(str(s.get("run", ""))):
                    out.append((f"{wf.name}:{job}", str(s["run"])))
    return out


def arm_restore(base: str, tmp: Path) -> int:
    pairs = moves(json.loads((ROOT / "tests/layout.json").read_text()))
    repo = clone("HEAD", tmp / "restore")
    pinned = {"old": git(repo, "rev-parse", "HEAD").strip()}
    git(repo, "checkout", "-q", "--detach", "HEAD")
    apply_moves(repo, pairs, [])
    commit(repo, "planted: graders at the new location only")
    pinned["new"] = git(repo, "rev-parse", "HEAD").strip()
    git(repo, "checkout", "-q", "--detach", pinned["old"])
    specs = restore_specs(repo)
    for f in filter(None, git(repo, "ls-files").split("\n")):
        if any(spec_hit(s, f) for s in specs):
            git(repo, "rm", "-q", "--cached", f)
    commit(repo, "planted: graders at neither location")
    pinned["neither"] = git(repo, "rev-parse", "HEAD").strip()
    bad = total = 0
    for label, script in restore_steps(ROOT):
        for arm, want in (("old", 0), ("new", 0), ("neither", 1)):
            total += 1
            git(repo, "checkout", "-q", "-f", "--detach", pinned["old"])
            git(repo, "clean", "-qfdx")
            rt = tmp / "rt"
            shutil.rmtree(rt, ignore_errors=True)
            rt.mkdir()
            r = subprocess.run(["bash", "-eo", "pipefail", "-c", script], cwd=repo, capture_output=True, text=True,
                               env={**os.environ, "PINNED": pinned[arm], "RUNNER_TEMP": str(rt)})
            ok = (r.returncode == 0) == (want == 0)
            exact = True
            if r.returncode == 0:
                for f in filter(None, git(repo, "ls-tree", "-r", "--name-only", pinned[arm]).split("\n")):
                    if any(spec_hit(s, f) for s in specs_in(script)):
                        blob = git(repo, "rev-parse", f"{pinned[arm]}:{f}").strip()
                        exact &= git(repo, "hash-object", f).strip() == blob
            bad += not (ok and exact)
            print(f"  restore {label} PINNED={arm}: rc {r.returncode} "
                  f"{'ok' if ok and exact else 'WRONG' + ('' if exact else ' (a file differs from PINNED)')}")
            if not ok:
                print("    " + (r.stderr.strip().splitlines() or [""])[-1][:200])
    print(f"RESULT restore_wrong={bad} of {total}")
    return bad


# The grading commands each base-restoring job runs (COMMANDS' names).
JOBS = {
    "governance.yml:policy-docs": ["rules_sync --check", "codeowners_gap --check", "policy_lint", "fragments_sync",
                                   "policy_lint --report", "policy_lint --hooks", "field_coverage"],
    "governance.yml:wave-script": ["check-wave-script", "agreement_py", "agreement"],
    "tests.yml:briefs": ["brief_lint"],
    "budget-raise-gate.yml:budget-raise-gate": ["budget_raise_gate"],
    "pr-contract.yml:pr-contract": ["policy_lint --pr-body", "figure_lint --pr-body", "preflight"],
    "governance.yml:delivery-status": ["delivery_status --check"],
}


def arm_ci(base: str, tmp: Path) -> int:
    import yaml

    tree = clone("HEAD", tmp / "ci")
    commit(tree, "planted: nothing")
    (tmp / "ch").mkdir()
    want = run_all(tree, tmp / "ch", [])
    bad = 0
    for job, names in JOBS.items():
        wf, jid = job.split(":")
        j = yaml.safe_load((tree / ".github/workflows" / wf).read_text())["jobs"][jid]
        specs = [p for st in j.get("steps") or [] for p in specs_in(str(st.get("run", "")))]
        git(tree, "checkout", "-q", "-f", "HEAD")
        files = [f for f in git(tree, "ls-tree", "-r", "--name-only", base).split("\n")
                 if f and any(spec_hit(sp, f) for sp in specs)]
        if files:
            git(tree, "checkout", "-q", base, "--", *files)
        d = tmp / f"cb-{jid}"
        d.mkdir()
        saved = COMMANDS[:]
        COMMANDS[:] = [(n, c) for n, c in saved if n in names]
        got = run_all(tree, d, [])
        COMMANDS[:] = saved
        for n in names:
            ok = got[n][0] == want[n][0]
            bad += not ok
            print(f"  ci {job} {n}: base graders rc {got[n][0]}, HEAD's rc {want[n][0]} {'same' if ok else 'DIFFERS'}")
            if not ok:
                (tmp / f"ci-{re.sub(r'[^a-z]+', '_', n)}.txt").write_text(got[n][1])
                print("    " + (got[n][1].strip().splitlines() or [""])[-1][:200])
    git(tree, "checkout", "-q", "-f", "HEAD")
    print(f"RESULT ci_differ={bad} of {sum(len(v) for v in JOBS.values())}")
    return bad


def arm_shadow(base: str, tmp: Path) -> int:
    """The #1886 round-1 plants: a pristine copy at an unowned new path beside
    a grown file in use. policy_lint must refuse, as it refuses the growth alone."""
    pairs = moves(json.loads((ROOT / "tests/layout.json").read_text()))
    plants = {
        "COMMON.md grown, its copy at the new path": (["tools/audit/briefs/COMMON.md"], 150, True),
        "COMMON.md grown alone (null control)": (["tools/audit/briefs/COMMON.md"], 150, False),
        "the rules copied under dev/, claim-files.md grown": (
            [f for f in git(ROOT, "ls-files", ".claude/rules").split("\n") if f], 120, True),
    }
    bad = 0
    for name, (files, grow, copy) in plants.items():
        tree = clone("HEAD", tmp / "shadow")
        for f in files:
            src = tree / f
            if copy:
                rule = next(((o, n) for o, n in pairs if f == o or (o.endswith("/") and f.startswith(o))), None)
                dst = tree / ((rule[1] + f[len(rule[0]):]) if rule[0].endswith("/") else rule[1])
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src, dst)
        grown = tree / ("tools/audit/briefs/COMMON.md" if "COMMON" in name else ".claude/rules/claim-files.md")
        grown.write_text(grown.read_text() + "".join(f"Planted line {i} of prose that grows the file.\n" for i in range(grow)))
        git(tree, "add", "-A")
        commit(tree, f"planted: {name}")
        r = subprocess.run(["node", ".claude/workflows/policy_lint.mjs"], cwd=tree, capture_output=True, text=True)
        ok = r.returncode == 1 and "exceeds its cap" in r.stdout
        bad += not ok
        print(f"  shadow {name}: policy_lint rc {r.returncode} {'refused' if ok else 'NOT REFUSED'}")
        shutil.rmtree(tree)
    print(f"RESULT shadow_unrefused={bad} of {len(plants)}")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["graders", "neither", "ci", "shadow", "restore"], action="append")
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    base = git(ROOT, "merge-base", a.base, "HEAD").strip()
    tmp = Path(tempfile.mkdtemp(prefix="dual_path."))
    print(f"# HEAD {git(ROOT, 'rev-parse', 'HEAD').strip()}, merge base {base}, scratch {tmp}")
    bad = 0
    arms = {"graders": arm_graders, "neither": arm_neither, "ci": arm_ci, "shadow": arm_shadow,
            "restore": arm_restore}
    for arm in a.arm or ["graders", "neither", "ci", "shadow"]:
        bad += arms[arm](base, tmp)
    # The clones are large; the diff files beside them are what a reader needs.
    for d in tmp.iterdir():
        if d.is_dir() and not a.keep:
            shutil.rmtree(d, ignore_errors=True)
    if not a.keep and not bad:
        shutil.rmtree(tmp, ignore_errors=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
