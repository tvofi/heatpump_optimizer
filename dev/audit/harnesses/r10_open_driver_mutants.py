#!/usr/bin/env python3
"""R10-OPENER-REUSE part 1: each rule of tools/audit/seat/open_driver.py dies alone.

Each mutant is one exact one-occurrence replacement in a COPY of
tools/audit/seat/ (never the tree); the copy's own
`open_driver.py --self-test` is then run and must FAIL. Null control: M0,
nothing mutated, must print failed=0. A pattern not found exactly once aborts.

  M-exact    drop the exact-first rule (P363 (i)): r10-roster-ops-2 resolves to
             R10-ROSTER-OPS and r10-ci-layout-p1 to nothing.
  M-body     drop the body-names-group check on a stripped match.
  M-landed   drop the ledger.py landed check: the on-main topic opens.
  M-omitlast an omitted topic sorts after every listed one (P350).
  M-crit     critical-path topics are not kept ahead of the rest.
  M-seen     mark seen on any rc, not only rc=0 (the stranded-handoff shape).
  M-starved  STARVED prints at any age.
  M-backoff  a failed open is retried every pass.
  M-live     a topic whose run is still alive launches again.
  M-launch   World.launch pastes the topic and state directory into bash -c text.
  M-bo-base  the backoff base 1800 s -> 600 s.
  M-bo-max   the backoff cap 7200 s -> 14400 s.
  M-head4    body_head reads four lines, not three.
  M-headall  body_head reads the whole body.
  M-first    parse_board lets a later line for a topic win.
  M-triageB  the R10-TRIAGE-B<M> fallback is dropped.
  M-escape   stem() no longer escapes % before /: `a%2Fb` and `a/b` share a file.
  M-maxtries the MAX_TRIES stop is dropped: a failing open is retried forever.
  M-stuckowed a stuck (topic, sha) prints OWED, not STUCK.
  M-open-stem   World.launch names the .rc by the raw topic: a slash topic's
                result file is never written (the open side).
  M-reap-stem   run_pass reads the raw topic's .rc: a slash topic's result is
                never reaped (the reap side).
  M-reap-log    run_pass reads the raw topic's log: the RESULT reason is lost.
  M-livetip     restores the SKIP moved on a board sha behind origin's live tip
                (OPENER-LIVE-TIP, P603): the line at A no longer opens at B.
  M-moved-gone  drops the SKIP moved on an absent handoff ref: the null control
                (a gone ref still prints SKIP moved) fails.

    python3 dev/audit/harnesses/r10_open_driver_mutants.py

EXPECTED RESULT mutants=24
EXPECTED RESULT survived=0
"""
from __future__ import annotations

import shutil
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
SEAT = "tools/audit/seat"
TARGET = "open_driver.py"
GRAMMAR = "topic_grammar.py"  # resolve() moved here (a7fd743e5): its plants name this file
#: A plant is (old, new) in TARGET, or (old, new, file) in another module of SEAT.
PLANTS = {
    "M-livetip": ("            log(f\"RETIP {topic} {sha[:8]} -> {live_tip[:8]}\")\n            sha = live_tip\n",
                  "            live_tip = None\n"),
    "M-moved-gone": ("        elif live_tip is None:\n            skip(\"moved\")", "        elif False:\n            skip(\"moved\")"),
    "M-exact": ("    if up in groups:  # exact match always wins\n", "    if False:\n", GRAMMAR),
    "M-body": (" and names_group(body_head, m.group(1).upper())", "", GRAMMAR),
    "M-landed": ("        elif main and world.landed(main, sha):\n", "        elif False:\n"),
    "M-omitlast": ("        return max(above, default=-1) + 0.5\n", "        return 1e9\n"),
    "M-crit": ("(min(cls[x[0]], FENCED + 1), pos(x[0])", "(False, pos(x[0])"),
    "M-seen": ("        if rc == 0:\n            seen.add(key)", "        if True:\n            seen.add(key)"),
    "M-starved": ("ct and now - ct > STARVE_S", "ct"),
    "M-backoff": ('fails.get(f"{topic} {sha}", {}).get("next", 0) > now', "False"),
    "M-live": ("        elif topic in runs:\n", "        elif False:\n"),
    "M-launch": (
        """        cmd = 'o=$0; l=$1; r=$2; shift 2; bash "$o" "$@" > "$l" 2>&1; echo $? > "$r"'
        argv = ["bash", "-c", cmd, str(self.opener), str(d / f"t-{stem(topic)}.log"), str(rc), topic, sha, title, group]
""",
        """        cmd = f'bash {self.opener} "$@" > {d}/t-{topic}.log 2>&1; echo $? > {d}/t-{topic}.rc'
        argv = ["bash", "-c", cmd, "_", topic, sha, title, group]
"""),
    "M-bo-base": ("BACKOFF_S, BACKOFF_MAX_S, MAX_TRIES = 1800, 7200, 3", "BACKOFF_S, BACKOFF_MAX_S, MAX_TRIES = 600, 7200, 3"),
    "M-bo-max": ("BACKOFF_S, BACKOFF_MAX_S, MAX_TRIES = 1800, 7200, 3", "BACKOFF_S, BACKOFF_MAX_S, MAX_TRIES = 1800, 14400, 3"),
    "M-head4": ("splitlines()[:3]", "splitlines()[:4]"),
    "M-headall": ('"\\n".join(r.stdout.splitlines()[:3])', "r.stdout"),
    "M-first": ("        if m and m.group(1) not in seen:\n", "        if m:\n"),
    "M-triageB": ('for g in (f"R10-TRIAGE-S{m.group(1)}", f"R10-TRIAGE-B{m.group(2)}"):', 'for g in (f"R10-TRIAGE-S{m.group(1)}",):', GRAMMAR),
    "M-open-stem": ('        rc = d / f"t-{stem(topic)}.rc"\n', '        rc = d / f"t-{topic}.rc"\n'),
    "M-reap-stem": ('        rcf = d / f"t-{stem(t)}.rc"\n', '        rcf = d / f"t-{t}.rc"\n'),
    "M-reap-log": ('{reason(d / f"t-{stem(t)}.log")}', '{reason(d / f"t-{t}.log")}'),
    "M-escape": ('topic.replace("%", "%25").replace("/", "%2F")', 'topic.replace("/", "%2F")'),
    "M-maxtries": ('        elif fails.get(f"{topic} {sha}", {}).get("n", 0) >= MAX_TRIES:\n', "        elif False:\n"),
    "M-stuckowed": ('f"STUCK {t} {sha[:8]} rc=', 'f"OWED {stamp} open-refused {t} {sha[:8]} rc='),
}


def selftest(tree: Path) -> tuple:
    r = subprocess.run([sys.executable, "-I", str(tree / SEAT / TARGET), "--self-test"], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def main() -> int:
    survived = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name in ["M0", *PLANTS]:
            tree = Path(tmp) / name
            shutil.copytree(ROOT / SEAT, tree / SEAT)
            (tree / "tests").mkdir()
            shutil.copy(ROOT / "tests/throwaway_git.py", tree / "tests/throwaway_git.py")
            if name != "M0":
                old, new, *where = PLANTS[name]
                p = tree / SEAT / (where[0] if where else TARGET)
                s = p.read_text()
                if s.count(old) != 1:
                    print(f"ABORT {name}: pattern occurs {s.count(old)} times")
                    return 2
                p.write_text(s.replace(old, new))
            rc, out = selftest(tree)
            failed = sum(1 for l in out.splitlines() if l.startswith("FAIL "))
            if name == "M0":
                print(f"RESULT mutant=M0 failed={failed} verdict={'null-ok' if rc == 0 and not failed else 'NULL-RED'}")
                if rc:
                    return 2
                continue
            dead = rc != 0 and failed > 0
            survived += not dead
            print(f"RESULT mutant={name} failed={failed} verdict={'killed' if dead else 'SURVIVED'}")
    print(f"RESULT mutants={len(PLANTS)}")
    print(f"RESULT survived={survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
