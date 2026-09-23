#!/usr/bin/env python3
"""Drive the `record` job's report step's own shell, and the two windows it reads.

METRIC (one line). The headline the `record` job's run summary would carry, for
each of four states of the world, read off the production shell the workflow
runs -- plus the two `--record` captures that shell reads, taken with a stub
`curl` so nothing touches the network.

COMMAND.  python3 tools/audit/round7-fix/governance/report_step_driver.py
          (needs `node` and the window tag in the tree; no network, no token.)
          `--mutate <marker|not-run|did-not-run-list>` deletes one production arm
          from the extracted shell in memory and re-runs every case.
          `--ref <git-ref>` drives the step as it stands at that ref instead of
          the working tree.

BASELINE. origin/main 6e2a0f2a (round-6 fix wave stamped); D13-03/#1473.

WHY IT EXISTS. `.github/workflows/governance.yml`'s report step is inline shell,
so a pin on its text says nothing about what it prints, and the workflow-side
perturbation cannot be executed without a push to `main`. This cuts the step out
of the YAML and runs it -- the same shell GitHub runs -- with the two captures
as its input and the step outcomes as its environment, so the fix and its
absence are read off RESULT lines rather than argued. Two of the four cases are
what D13-03 found: at the baseline the unenumerable window reads `clean`, and so
does a run whose refusal step never ran at all.

WHAT IT DOES NOT DO. It does not re-implement one branch of the step: the
extraction is `step_script`, and the mutations are asserted to find their arm in
the extracted text (`--mutate` refuses rather than no-oping). The captures are
this file's own stub; the finding's own numbers (exit code 0, the UNCHECKED
marker present) are re-run separately with the round-7 harness
`tools/audit/round7/D13/window_api_ledger.mjs`, which is not in this tree.

EXPECTED at the fixed head: `outage-reads-clean_headline=UNCHECKED -- the
window's merged pull requests could not be enumerated`,
`refusal-never-ran_headline=UNCHECKED -- the disposition check did not run
(skipped)`, `refusal-clean_headline=clean -- ...`,
`refusal-red_headline=REFUSED -- ...`, `arms_in_step=4 count`.
At origin/main: the first two read `clean`, `arms_in_step=2 count`.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

STEP = "Report the refusal on the run summary"
REL = ".github/workflows/governance.yml"
ROOT = Path(__file__).resolve().parents[4]  # <root>/tools/audit/round7-fix/governance/
# label, refusal outcome, which capture, (self-test outcome, filer outcome)
CASES = [
    ("refusal-clean", "success", "healthy", ("success", "success")),
    ("outage-reads-clean", "success", "api-500", ("success", "success")),
    ("refusal-red", "failure", "healthy", ("success", "success")),
    ("refusal-never-ran", "skipped", "healthy", ("skipped", "skipped")),
]
STUB = """#!/bin/sh
url=""
for a in "$@"; do url="$a"; done
cat >/dev/null 2>&1
case "$url" in
  */commits/*/pulls)
    if [ "$HPO_STUB_500" = "1" ]; then printf '{"message":"stub outage"}\\n500'; exit 0; fi
    n=$(cat "$HPO_STUB_CTR"); n=$((n + 1)); printf '%s' "$n" > "$HPO_STUB_CTR"
    printf '[{"number": %s}]\\n200' "$n" ;;
  */issues/*/comments*) printf '[]\\n200' ;;
  */pulls/*) printf '{"body": ""}\\n200' ;;
  *) printf '[]\\n200' ;;
esac
"""


def window_tag(tree: Path) -> str:
    """The newest release tag whose window to HEAD holds a MERGE.

    Not simply `git describe --tags`: at a release stamp the newest tag IS
    HEAD, so its window is empty, `--record` enumerates no commit, the stub's
    outage is never asked for anything, and the capture that is meant to model
    an unenumerable window carries no marker at all -- a vacuous arm that reads
    exactly like a fix. `--merges` and not bare `git log`: a branch's own
    commits are in the first-parent line too, and they are not merges. The tag
    is derived, so the driver follows the stamps.
    """
    tags = subprocess.run(["git", "tag", "--sort=-creatordate", "--list", "v*"],
                          cwd=tree, capture_output=True, text=True).stdout.split()
    for tag in tags:
        rng = subprocess.run(["git", "log", "--first-parent", "--merges",
                              "--format=%H", f"{tag}..HEAD"],
                             cwd=tree, capture_output=True, text=True).stdout.split()
        if rng:
            return tag
    raise SystemExit("no release tag has a merge in its window to HEAD")


def capture(tree: Path, outdir: Path, since: str | None) -> str:
    """The two `--record` windows: one the API answers, one it refuses."""
    tag = since or window_tag(tree)
    tmp = Path(tempfile.mkdtemp(prefix="r7-report-capture-"))
    (tmp / "bin").mkdir()
    (tmp / "ctr").write_text("9000")
    stub = tmp / "bin" / "curl"
    stub.write_text(STUB)
    stub.chmod(0o755)
    for name, status500 in (("healthy", "0"), ("api-500", "1")):
        env = dict(os.environ, PATH=f"{tmp / 'bin'}:{os.environ['PATH']}",
                   GITHUB_TOKEN="r7-report-driver-stub-not-a-credential",
                   HPO_STUB_CTR=str(tmp / "ctr"), HPO_STUB_500=status500)
        p = subprocess.run(["node", ".claude/workflows/policy_lint.mjs", "--record",
                            "--since", tag], cwd=tree, env=env,
                           capture_output=True, text=True)
        (outdir / f"record-{name}.txt").write_text(p.stdout)
        print(f"RESULT capture_{name}_rc={p.returncode} count"
              f"   # --record over {tag}..origin/main, stub transport")
        print(f"RESULT capture_{name}_marker_lines="
              f"{sum('merge-enumeration' in l for l in p.stdout.splitlines())} count")
        print(f"RESULT capture_{name}_enum_mode="
              f"{(p.stdout.splitlines() or [''])[0].removeprefix('RECORD_ENUM: ')}")
    return tag


def step_script(text: str, name: str) -> str:
    """The step's `run:` block, dedented -- the production shell, whole."""
    lines = text.split("\n")
    i = next(k for k, l in enumerate(lines) if l.strip() == f"- name: {name}")
    j = next(k for k in range(i, len(lines)) if lines[k].strip() == "run: |")
    indent = len(lines[j]) - len(lines[j].lstrip())
    body = []
    for l in lines[j + 1:]:
        if l.strip() and (len(l) - len(l.lstrip())) <= indent:
            break
        body.append(l[indent + 2:] if l.strip() else "")
    return "\n".join(body).rstrip() + "\n"


MUTATIONS = {
    "marker": ('elif grep -q \'merge-enumeration\' "$RECORD_TXT"; then\n'
               '  VERDICT="UNCHECKED -- the window\'s merged pull requests could'
               ' not be enumerated"\n'),
    "not-run": ('elif [ "$REFUSAL_OUTCOME" != "success" ]; then\n'
                '  VERDICT="UNCHECKED -- the disposition check did not run'
                ' (${REFUSAL_OUTCOME:-no outcome})"\n'),
}


def mutate(script: str, name: str) -> str:
    """Delete one production arm from the EXTRACTED shell. The anchor is the
    arm's own text, so a rewrite that moves it makes this refuse rather than
    report a vacuous mutation."""
    if name in MUTATIONS:
        arm = MUTATIONS[name]
        assert arm in script, f"{name}: arm not found in the extracted step"
        return script.replace(arm, "")
    head = 'DID_NOT_RUN=""\nfor s in \\\n'
    assert head in script, "did-not-run-list: the enumeration is not there"
    i = script.index(head)
    return script[:i] + script[script.index("done\n", i) + len("done\n"):]


def run_case(script, label, refusal, capture_name, tails, capture_dir):
    tmp = Path(tempfile.mkdtemp(prefix="r7-report-"))
    (tmp / "record.txt").write_text((capture_dir / f"record-{capture_name}.txt").read_text())
    summary = tmp / "summary.md"
    env = dict(os.environ, RUNNER_TEMP=str(tmp), GITHUB_STEP_SUMMARY=str(summary),
               REFUSAL_OUTCOME=refusal, WINDOW_OUTCOME="success",
               HISTOGRAM_OUTCOME="success", SELFTEST_OUTCOME=tails[0],
               FILER_OUTCOME=tails[1], SUNSET_OUTCOME="success")
    p = subprocess.run(["bash", "-c", script], capture_output=True, text=True, env=env)
    body = summary.read_text() if summary.exists() else ""
    head = next((l for l in body.split("\n") if l.startswith("### record: ")), "?")
    not_run = next((l for l in body.split("\n")
                    if l.startswith("steps this job did not run: ")), "?")
    print(f"RESULT {label}_rc={p.returncode} count")
    print(f"RESULT {label}_headline={head.removeprefix('### record: ')}")
    print(f"RESULT {label}_did_not_run="
          f"{not_run.split(': ', 1)[1] if not_run != '?' else 'absent'}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", default=str(ROOT))
    ap.add_argument("--ref", default=None)
    ap.add_argument("--since", default=None,
                    help="the window tag; default: the newest tag whose window "
                         "to HEAD holds a merge (see `window_tag`)")
    ap.add_argument("--mutate", default=None)
    ap.add_argument("--capture-dir", default=None)
    a = ap.parse_args()
    tree = Path(a.tree).resolve()
    capture_dir = Path(a.capture_dir).resolve() if a.capture_dir else \
        Path(tempfile.mkdtemp(prefix="r7-report-fixtures-"))
    tag = capture(tree, capture_dir, a.since)
    if a.ref:
        text = subprocess.run(["git", "show", f"{a.ref}:{REL}"], cwd=tree,
                              capture_output=True, text=True, check=True).stdout
        where = f"{a.ref}:{REL}"
    else:
        text = (tree / REL).read_text()
        where = str(tree / REL)
    script = step_script(text, STEP)
    print(f"# {where} -- step `{STEP}` over {tag}..origin/main, "
          f"{len(script.splitlines())} shell line(s)"
          + (f", mutation `{a.mutate}`" if a.mutate else ""))
    if a.mutate:
        script = mutate(script, a.mutate)
    for label, refusal, cap, tails in CASES:
        run_case(script, label, refusal, cap, tails, capture_dir)
    print("RESULT arms_in_step=%d count" % script.count("VERDICT="))
    print("RESULT cases=%d count" % len(CASES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
