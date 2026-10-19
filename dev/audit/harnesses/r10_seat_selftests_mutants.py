#!/usr/bin/env python3
"""R10-SEAT-SELFTESTS-CI: each seat self-test step, and the wiring check, against a mutant.

    python3 dev/audit/harnesses/r10_seat_selftests_mutants.py            # all
    python3 dev/audit/harnesses/r10_seat_selftests_mutants.py M0 S07 W1  # named

Run from a clean checkout of the branch: every mutant edits the committed
file in place and restores its bytes, and a dirty file refuses first.

M0 runs every seat step in governance.yml's `instrument-self-tests` as CI
does (its `run:` text, under `bash -e`, with RUNNER_TEMP set and a throwaway
HOME) and must exit 0 for each. S01..S29 each plant one production-line
mutant in one file -- outside that file's self-test function -- and run only
the step that names the file: a killed mutant reddens the step, and the same
step on the unmutated file must pass first (NOT RUN otherwise). W1..W3 drive
the wiring step: an unwired self-testing file, a step reduced to a comment
naming its file, and a trailing comment, each of which must redden it.
Prints one line per mutant, `KILLED` or `SURVIVED`, with the step's last
line, and `RESULT survivors=<n>`; exit 1 when any survived or M0 failed.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
WF = ROOT / ".github" / "workflows" / "governance.yml"
SEAT = "tools/audit/seat"

# name, file, old (exactly once in the file), new
MUTANTS = [
    ("S01", "ci-watch.sh", '[ -n "$RS" ] && REQ=$(gh api', '[ -n "$RS" ] || REQ=$(gh api'),
    ("S02", "cloud_dispatch.py", "return len(head) == 40 and set(head) <= LOWER_HEX",
     "return len(head) != 40 and set(head) <= LOWER_HEX"),
    ("S03", "cloud_relay.sh", 'if [ -f "$led" ] && grep -qxF "$ref $sha" "$led"; then',
     'if [ -f "$led" ] && ! grep -qxF "$ref $sha" "$led"; then'),
    ("S04", "daemonize.py", '"-u" not in run_argv[1:2]:', '"-u" in run_argv[1:2]:'),
    ("S05", "delivery_row.sh", 'if [ -n "${4:-}" ]; then', 'if [ -z "${4:-}" ]; then'),
    ("S06", "failure_logs.sh", 'if [ -z "$jid" ]; then', 'if [ -n "$jid" ]; then'),
    ("S07", "features_block.py", 'i = source.rindex("\\n", 0, source.index(start)) + 1',
     'i = source.rindex("\\n", 0, source.index(start)) + 0'),
    ("S09", "handover_prompt.py",
     "if stage not in roster_lib.DONE_STAGES and stage != NOT_STARTED:",
     "if stage not in roster_lib.DONE_STAGES and stage == NOT_STARTED:"),
    ("S10", "merge_pr.sh", '[ "$4" = 1 ] || { echo "DRAFT:', 'true || { echo "DRAFT:'),
    ("S11", "moved_paths.py", 'e["new"] or "(retired)"', 'e["new"] and "(retired)"'),
    ("S13", "plan_table.py",
     '        ids[g] = _task_id(g, ids)\n    lanes = sorted({open_[g].get("lane") or "?"',
     '        ids[g] = _task_id(g, ids)\n    lanes = sorted({open_[g].get("lane") and "?"'),
    ("S14", "pr_args.sh", '"$*" >&2; exit 1; }', '"$*" >&2; exit 0; }'),
    ("S15", "pr_cap.py", 'a = pr.get("author") or {}', 'a = pr.get("author") and {}'),
    ("S16", "proof_watch.py", 'and last[n].get("conclusion") not in GREEN)',
     'and last[n].get("conclusion") in GREEN)'),
    ("S17", "prune_refs.py", "    if sha in main_reachable:\n        return DELETE_MERGED",
     "    if sha not in main_reachable:\n        return DELETE_MERGED"),
    ("S18", "queue_pre_flight.py", "if not mt.is_sha(v):", "if mt.is_sha(v):"),
    ("S19", "record_row.py", 'if n in required and r.get("conclusion") in bad)',
     'if n in required and r.get("conclusion") not in bad)'),
    ("S20", "resume_doc.py", "done = {k for k in G if k not in open_}",
     "done = {k for k in G if k in open_}"),
    ("S21", "roster_edit.py", "    if r.returncode != 0:\n        raise Refuse(",
     "    if r.returncode == 0:\n        raise Refuse("),
    ("S22", "roster_lib.py", '    m = _ROSTER_NAME.match(path.rsplit("/", 1)[-1])\n    if not m:',
     '    m = _ROSTER_NAME.match(path.rsplit("/", 1)[-1])\n    if m:'),
    ("S23", "run_twins.py", '    pr = [r for r in runs if r.get("event") == "pull_request"]\n    ts = {',
     '    pr = [r for r in runs if r.get("event") != "pull_request"]\n    ts = {'),
    ("S24", "seat_venv.sh", '|| die "$VENV_HA is missing a pinned homeassistant',
     '|| true "$VENV_HA is missing a pinned homeassistant'),
    ("S25", "state_docs.py", "        if a.roster_file:\n            return roster_lib.roster_round(a.roster_file)",
     "        if not a.roster_file:\n            return roster_lib.roster_round(a.roster_file)"),
    ("S26", "tick_loop.sh", '[ "$rrc" = 0 ] && rrc=ok', '[ "$rrc" != 0 ] && rrc=ok'),
    ("S28", "offline_spy.py", "and bool(URL_RE.search(parts[2])))", "and False)"),
    ("S29", "selftest_wiring.py", 'return [COMMENT_RE.sub("", x) for x in out]', "return out"),
]

# The wrappers' own line is the dispatch to the self-tests they delegate.
WRAPPERS = [
    ("S08", "handoff_push.sh",
     '[ "${1:-}" = --self-test ] && exec bash "$(dirname -- "$0")/delivery_row.sh" --self-test',
     '[ "${1:-}" = --self-test ] && exit 0'),
    ("S12", "open_pr.sh",
     'bash "$(dirname -- "$0")/pr_args.sh" --self-test || exit 1; exit $r; }',
     'exit $r; }'),
    ("S27", "update_pr.sh",
     '[ "${1:-}" = --self-test ] && { bash "$(dirname -- "$0")/delivery_row.sh" --self-test; r=$?',
     '[ "${1:-}" = --self-test ] && { r=0'),
]


def steps() -> list[tuple[str, str]]:
    """(name, run text) of each step in instrument-self-tests."""
    text = WF.read_text()
    job = text[text.index("\n  instrument-self-tests:\n"):]
    job = job[:re.search(r"\n  [a-z][\w-]*:\n", job[1:]).start() + 1]
    out = []
    for blk in job.split("\n      - name: ")[1:]:
        name = blk.split("\n", 1)[0]
        m = re.search(r"\n        run: \|\n((?:          .*\n|\s*\n)+)", blk + "\n")
        if m:
            out.append((name, "\n".join(x[10:] for x in m.group(1).splitlines())))
        else:
            m = re.search(r"\n        run: (.*)", blk)
            if m:
                out.append((name, m.group(1)))
    return out


def step_for(file: str) -> tuple[str, str]:
    pat = re.compile(re.escape(f"{SEAT}/{file}") + r" --self-test")
    hits = [s for s in steps() if pat.search(s[1])]
    assert len(hits) == 1, f"{file}: {len(hits)} steps"
    return hits[0]


def run_step(run: str) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp, "step.sh")
        script.write_text(run + "\n")
        # A throwaway HOME, as on a runner, and python3 the interpreter running
        # this harness: a seat shim on PATH finds its venv under the real HOME,
        # and without it every step exits 127.
        pybin = Path(tmp, "pybin")
        pybin.mkdir()
        for name in ("python3", "python"):
            (pybin / name).symlink_to(sys.executable)
        env = dict(os.environ, RUNNER_TEMP=tmp, HOME=tmp, PYTHONDONTWRITEBYTECODE="1",
                   PATH=f"{pybin}{os.pathsep}{os.environ.get('PATH', '')}")
        p = subprocess.run(["bash", "-e", str(script)], cwd=ROOT, env=env,
                           capture_output=True, text=True, timeout=900)
    lines = (p.stdout + p.stderr).strip().splitlines()
    return p.returncode, lines[-1] if lines else ""


def clean(path: Path) -> bool:
    return subprocess.run(["git", "diff", "--quiet", "--", str(path)], cwd=ROOT).returncode == 0


def mutate(path: Path, old: str, new: str, fn) -> tuple[int, str]:
    orig = path.read_bytes()
    text = orig.decode()
    if text.count(old) != 1:
        return -1, f"PATTERN FOUND {text.count(old)} TIMES"
    path.write_text(text.replace(old, new))
    try:
        return fn()
    finally:
        path.write_bytes(orig)


def main(want: list[str]) -> int:
    pick = lambda n: not want or n in want  # noqa: E731
    survivors = 0
    baseline: dict = {}
    if pick("M0"):
        bad = 0
        for name, run in steps():
            if SEAT not in run:
                continue
            rc, last = run_step(run)
            bad += rc != 0
            print(f"== M0 rc={rc} {name} | {last}", flush=True)
        print(f"== M0: {bad} seat step(s) red")
        survivors += bad
    for name, file, old, new in MUTANTS + WRAPPERS:
        if not pick(name):
            continue
        path = ROOT / SEAT / file
        if not clean(path):
            print(f"== {name}: {file} has uncommitted edits; the restore would erase them")
            return 2
        _, run = step_for(file)
        # The null control per mutant: the same step on the unmutated file
        # must pass, or a red below says nothing about the mutant.
        base = baseline.setdefault(run, run_step(run))
        if base[0] != 0:
            survivors += 1
            print(f"== {name} {file}: NOT RUN, the step is red unmutated | {base[1]}", flush=True)
            continue
        rc, last = mutate(path, old, new, lambda: run_step(run))
        verdict = "NOT RUN" if rc == -1 else ("KILLED" if rc else "SURVIVED")
        survivors += rc <= 0
        print(f"== {name} {file}: {verdict} rc={rc} | {last}", flush=True)
    _, wiring = [s for s in steps() if "selftest_wiring.py --check" in s[1]][0]
    if any(pick(w) for w in ("W1", "W2", "W3")) and run_step(wiring)[0] != 0:
        print("== W: NOT RUN, the wiring step is red unmutated")
        return 1
    if pick("W1"):
        extra = ROOT / SEAT / "zz_unwired_probe.py"
        extra.write_text("import sys\nif sys.argv[1:] == ['--self-test']:\n    print('ok')\n")
        try:
            rc, last = run_step(wiring)
        finally:
            extra.unlink()
        survivors += rc == 0
        print(f"== W1 an unwired self-testing file: {'KILLED' if rc else 'SURVIVED'} rc={rc} | {last}")
    for name, old, new, what in (
        ("W2", "          bash tools/audit/seat/tick_loop.sh --self-test",
         "          # bash tools/audit/seat/tick_loop.sh --self-test", "a step reduced to a comment"),
        ("W3", "          bash tools/audit/seat/tick_loop.sh --self-test",
         "          true  # bash tools/audit/seat/tick_loop.sh --self-test", "a trailing comment"),
    ):
        if not pick(name):
            continue
        rc, last = mutate(WF, old, new, lambda: run_step(wiring))
        survivors += rc <= 0
        print(f"== {name} {what}: {'KILLED' if rc > 0 else 'SURVIVED'} rc={rc} | {last}")
    print(f"RESULT survivors={survivors}")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
