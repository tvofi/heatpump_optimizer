#!/usr/bin/env python3
"""R10-SEAT-SELFTESTS-CI: each seat self-test step, and the wiring check, against a mutant.

    python3 dev/audit/harnesses/r10_seat_selftests_mutants.py            # all
    python3 dev/audit/harnesses/r10_seat_selftests_mutants.py M0 S07 W1  # named

Run from a clean checkout of the branch: every mutant edits the committed
file in place and restores its bytes, and a dirty file refuses first.

M0 runs every seat step in governance.yml's `instrument-self-tests` as CI
does (its `run:` text, under `bash -e`, with RUNNER_TEMP set, a throwaway
HOME and no inherited PYTHONUNBUFFERED) and must exit 0 for each. S01..S38,
and each per-file id (<file>-<n>), plant one production-line mutant in one
file -- outside that file's self-test function -- and run only the step
that names the file: a killed mutant reddens the step, and the same step on
the unmutated file must pass first (NOT RUN otherwise). S04U is S04 run with
PYTHONUNBUFFERED=1 in the step's environment, as a Linux container sets it.
S35-S37 are #2444's three unpinned push lines in handoff_push.sh, S38 its
unpinned `gh pr merge` line in merge_pr.sh: each line is replaced by the
carry's own mutant (`true`, and `exit 0` for the merge), and the step's
offline self-test must redden.
W1..W3 drive
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

# cloud_relay.sh's handoff-arm lines the hold's ordering mutants swap
_CONTAINED = 'git merge-base --is-ancestor "$hs" "$head" && continue\n'
_HOLD = 'if grep -qxF "$pr" <<< "$held_prs"; then echo "cloud_relay: HELD #$pr $hs"; continue; fi\n'
_FAILED = 'if [ -f "$f" ] && grep -qxF "$topic $hs" "$f"; then continue; fi\n'

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
    ("S30", "selftest_wiring.py", "return 1 if unwired else 0", "return 0"),
    # r10-tick-relay-decouple: the relay runs detached under a lock, and the board never waits on it.
    ("S31", "tick_loop.sh", '  if kill -0 "$hp" 2>/dev/null; then rrc=running; return 0; fi  # mut:detach\n', ""),
    ("S32", "tick_loop.sh", "except BlockingIOError: sys.exit(75)\n", "except BlockingIOError: pass\n"),
    ("S33", "tick_loop.sh",
     '    [ "$rrc" = rc=holder-76 ] && { relay_reap "$out.relay" late; relay_start "$out.relay" "$relay"; }  # mut:reap\n',
     ""),
    # The base's serial relay step (0cc148b2f), the loop the fix replaced.
    ("S34", "tick_loop.sh",
     '    relay_start "$out.relay" "$relay"\n    # 76:',
     '    bash "$relay" pass; rrc=$?\n    [ "$rrc" = 0 ] && rrc=ok || rrc="rc=$rrc"\n    # 76:'),
    # #2444's fourth forward-carry: the push and merge lines their own
    # self-tests did not reach. Each mutant is the carry's, verbatim.
    ("S35", "handoff_push.sh", "push_app 2  # mut:push-update",
     "true  # mut:push-update"),
    ("S36", "handoff_push.sh", "out=$(push_app 2)  # mut:push-open",
     "true  # mut:push-open"),
    ("S37", "handoff_push.sh", "push_app 1  # mut:push-row", "true  # mut:push-row"),
    ("S38", "merge_pr.sh",
     "gh pr merge $PR --merge --match-head-commit $S || exit 1  # mut:merge",
     "exit 0  # mut:merge"),
    # R10-FLOW-MAIN-GATE (K15): the train's state classifier and its readers.
    ("merge_train-1", "merge_train.py", "names = [n for n in required if n not in NOT_GATING]",
     "names = list(required)"),
    ("merge_train-2", "merge_train.py", '        return "pending"\n', '        return "red"\n'),
    ("merge_train-3", "merge_train.py", 'return ("red" if red else "wait" if pending else "green")',
     'return ("wait" if pending else "red" if red else "green")'),
    ("merge_train-4", "merge_train.py", "    if required is None:\n        raise ValueError(",
     '    if required is None:\n        return "green", [], []\n        raise ValueError('),
    ("merge_train-5", "merge_train.py", '            elif state == "red":\n', '            elif state != "green":\n'),
    ("merge_train-6", "merge_train.py", 'in ("queued", "in_progress") and run_status == "completed"',
     'in ("queued", "in_progress")'),
    ("merge_train-7", "merge_train.py", "        self.unstale(h)\n", ""),
    ("merge_train-8", "merge_train.py", "        if reran:\n            red = self.wait_ci(",
     "        if False:\n            red = self.wait_ci("),
    ("merge_train-9", "merge_train.py", "if files and all(f in claim_files for f in files):",
     "if files and any(f in claim_files for f in files):"),
    ("merge_train-10", "merge_train.py", "    return lines[1:]\n", "    return lines\n"),
    ("merge_train-11", "merge_train.py", "t.required(pr_head=not a.main)", "t.required()"),
    # Round 2: GitHub's merge under a local driver, and the reviewer's R1-R4.
    ("merge_train-12", "merge_train.py",
     '    drivers = text_merge(run)\n    if drivers is None:\n        return None\n',
     '    drivers = []\n'),
    ("merge_train-13", "merge_train.py",
     'return [x for n in names for x in ("-c", f"merge.{n}.driver=git merge-file %A %O %B")]', "return []"),
    ("merge_train-14", "merge_train.py", " or (code == 1) != (len(lines) > 1):", ":"),
    ("merge_train-15", "merge_train.py", "            if m.group(1) not in reran.values():\n",
     "            if True:\n"),
    ("merge_train-16", "merge_train.py",
     '            if runs is None:\n                self.log(f"OVERLAP:',
     '            if False:\n                self.log(f"OVERLAP:'),
    ("merge_train-17", "merge_train.py", "    if code not in (0, 1):\n        return None\n    names",
     "    if False:\n        return None\n    names"),
    ("merge_train-18", "merge_train.py", "        if drivers is None:\n            raise Stop(\"build\"",
     "        if False:\n            raise Stop(\"build\""),
    ("merge_pr-1", "merge_pr.sh", 'python3 -I "$PWD/tools/audit/seat/merge_train.py" unstale', "true"),
    ("orchestrator_tick-1", "orchestrator_tick.py", "req_bad = mt.classify(latest, req)[2]", "req_bad = red"),
    ("orchestrator_tick-2", "orchestrator_tick.py", "            if req_red:\n", "            if False:\n"),
    ("orchestrator_tick-3", "orchestrator_tick.py", "mt.dirty_repair(files, CLAIM_FILES) if files else",
     '"absorb main locally with the claimnotes driver" if files else'),
    ("orchestrator_tick-4", "orchestrator_tick.py", 'getattr(self, "_req_pr", None) or required', "required"),
    # r10-flow-body-patch: retry exhaustion of the read-back never reports the body patched.
    ("body_patch-1", "body_patch.sh",
     '[ "$rbok" = 1 ] || die "#$pr could not be read back',
     '[ "$rbok" = 1 ] || : "#$pr could not be read back'),
    # R10-FLOW-TOOLKIT-MEASURE: the path walk, the per-run cache, the absorb count, the record split.
    ("ci_critpath-1", "ci_critpath.py", "n = max(live, key=lambda x: ends[x])", "n = min(live, key=lambda x: ends[x])"),
    ("ci_critpath-2", "ci_critpath.py", "        if f.exists():\n", "        if False:\n"),
    ("flow_metrics-1", "flow_metrics.py", "n += any(p in mainline for p in line.split())", "n += 0"),
    ("flow_metrics-2", "flow_metrics.py", 'fixes = [m for m in ms if not m["branch"].startswith(record)]',
     "fixes = list(ms)"),
    # R10-FLOW-RELAY-HOLD: the handoff arm's hold file, one mutant per arm
    ("cloud_relay-1", "cloud_relay.sh", 'if grep -qxF "$pr" <<< "$held_prs"; then',
     'if ! grep -qxF "$pr" <<< "$held_prs"; then'),
    ("cloud_relay-2", "cloud_relay.sh", 'held_prs=$(hold_list) || {', 'held_prs=$(hold_list || true) || {'),
    ("cloud_relay-3", "cloud_relay.sh", "*[!0-9]*|0*) echo \"cloud_relay: refused: malformed hold file $f: '$l'",
     "0*) echo \"cloud_relay: refused: malformed hold file $f: '$l'"),
    ("cloud_relay-4", "cloud_relay.sh", 'if grep -qxF "$pr" <<< "$held_prs"; then',
     'if grep -qF "$pr" <<< "$held_prs"; then'),
    ("cloud_relay-5", "cloud_relay.sh", 'while IFS= read -r l || [ -n "$l" ]; do', 'while IFS= read -r l; do'),
    ("cloud_relay-6", "cloud_relay.sh",
     'level_line handoff-hold-malformed "$(hold_file)" - >> "$state/cloud-level-hold.$$"; level_set',
     'level_set'),
    ("cloud_relay-7", "cloud_relay.sh", '  held) shift; held "$@"; exit $?;;\n', ''),
    # the two orderings the hold is a design choice of: after the contained test, before the failed ledger
    ("cloud_relay-8", "cloud_relay.sh", _HOLD + "    " + _FAILED, _FAILED + "    " + _HOLD),
    ("cloud_relay-9", "cloud_relay.sh", _CONTAINED + "    " + _HOLD, _HOLD + "    " + _CONTAINED),
    # the refusal is a level (#2547): the pre-merge event-log line, and a level never cleared
    ("cloud_relay-10", "cloud_relay.sh",
     'level_line handoff-hold-malformed "$(hold_file)" - >> "$state/cloud-level-hold.$$"; level_set',
     'logline OWED "handoff-hold-malformed $(hold_file)"; level_set'),
    ("cloud_relay-11", "cloud_relay.sh",
     'return 2; }\n  level_set handoff-hold-malformed "$state/cloud-level-hold.$$"\n',
     'return 2; }\n  rm -f "$state/cloud-level-hold.$$"\n'),
    # r10-flow-andon: ids are per file (tick_loop-N, heartbeat-N), never a new S number.
    ("tick_loop-1", "tick_loop.sh", '  timeout 60 bash "${HPO_TICK_HEARTBEAT:-$HERE/heartbeat.sh}" --once --message "TICK-PASS $now relay=$rrc tick=$trc"  # mut:heartbeat\n', ""),
    ("tick_loop-2", "tick_loop.sh", '[ $? = 0 ] || echo "HEARTBEAT NOT PUSHED: heartbeat.sh did not finish cleanly"', "true"),
    ("heartbeat-1", "heartbeat.sh", 'git -C "$HERE" push -q --no-verify -f "$remote"', 'git -C "$HERE" push -q --no-verify "$remote"'),
    ("heartbeat-2", "heartbeat.sh", '  if [ "$age" -gt "$max" ]; then', '  if [ "$age" -gt $((max * 100)) ]; then'),
    ("heartbeat-3", "heartbeat.sh", '|| { echo "HEARTBEAT NOT PUSHED: $(printf', '|| { echo "$(printf'),
    ("heartbeat-4", "heartbeat.sh", '  python3 -I "$HERE/ref_privacy.py" guard --ref "$REF" --message "$msg" >/dev/null 2>&1 \\\n',
     '  true \\\n'),
]

# Mutants run with extra step environment: (name, base mutant, env).
ENV_MUTANTS = [("S04U", "S04", {"PYTHONUNBUFFERED": "1"})]

# The wrappers' own line is the dispatch to the self-tests they delegate.
# S08's wrapper now runs both tallies (delivery_row.sh's and its own pushes):
# the mutant drops the delivery_row dispatch, so that tally is never printed.
WRAPPERS = [
    ("S08", "handoff_push.sh",
     'bash "$(dirname -- "$0")/delivery_row.sh" --self-test; r=$?',
     'r=0; :'),
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


def run_step(run: str, extra: dict | None = None) -> tuple[int, str]:
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
        env.pop("PYTHONUNBUFFERED", None)
        env.update(extra or {})
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
    by_name = {m[0]: m for m in MUTANTS + WRAPPERS}
    plan = [(*m, {}) for m in MUTANTS + WRAPPERS] + [
        (name, *by_name[base][1:], env) for name, base, env in ENV_MUTANTS]
    for name, file, old, new, extra in plan:
        if not pick(name):
            continue
        path = ROOT / SEAT / file
        if not clean(path):
            print(f"== {name}: {file} has uncommitted edits; the restore would erase them")
            return 2
        _, run = step_for(file)
        # The null control per mutant: the same step on the unmutated file
        # must pass, or a red below says nothing about the mutant.
        key = (run, tuple(sorted(extra.items())))
        if key not in baseline:
            baseline[key] = run_step(run, extra)
        base = baseline[key]
        if base[0] != 0:
            survivors += 1
            print(f"== {name} {file}: NOT RUN, the step is red unmutated | {base[1]}", flush=True)
            continue
        rc, last = mutate(path, old, new, lambda: run_step(run, extra))
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
