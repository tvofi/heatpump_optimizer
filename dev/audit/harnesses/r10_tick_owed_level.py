#!/usr/bin/env python3
"""Round-10 R10-TICK-OWED-LEVEL: does the tick print each owed item once?

Written by the R10-TICK-OWED-LEVEL fixer; there was no committed harness for
the finding (2026-10-21: the board printed `DISPATCH LIST: 35317 finding(s)`
from a cloud-relay log of 35214 lines naming ~281 distinct items, because
`cloud_relay.sh pass` re-appends a level line per undisposed ref per pass and
`orchestrator_tick.py` replayed every one).

It drives a TREE's own writer and reader end to end, offline: a throwaway bare
origin holding --refs handoff refs with no open pull request and one non-rev
probe ref; `cloud_relay.sh pass` run --passes times (an empty PR lister stub);
then, unless --no-dispose, `cloud_relay.sh dispose` on one ref at its sha and
one more pass; then four event lines in the log's documented grammar (an OWED
healed by a later POSTED, an unposted OWED, an unposted `handoff-update`, an
unposted `reviewer-fire`). The tree's `Tick.relay_owed` reads the result.

  printed   flagged `OWED:` lines the tree's reader prints
  distinct  what is owed now, from the fixture itself: refs on the origin less
            the disposed one, plus the three unposted events

RESULT match=yes means printed == distinct. The null control is --passes 1
--no-dispose: a single pass has no repeated level line, so printed is the same
at the baseline and at the head.

    python3 dev/audit/harnesses/r10_tick_owed_level.py --tree <checkout> [--passes N] [--refs N] [--no-dispose]

--read-log FILE skips the fixture and runs the tree's reader over a recorded
log (and FILE.level, if present), read-only: RESULT printed=<flagged OWED
lines> and the reader's unflagged notes. Distinct items in a recorded log are
not derivable from the log alone, so that mode prints no match.
"""
from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
from throwaway_git import throwaway_git_init  # noqa: E402


def git(*argv: str, cwd: Path, env: "dict | None" = None) -> str:
    return subprocess.run(["git", *argv], cwd=cwd, env=env, check=True,
                          capture_output=True, text=True).stdout.strip()


def reader(tree: Path, log: Path) -> list[dict]:
    sys.path.insert(0, str(tree / "tools/audit/seat"))
    spec = importlib.util.spec_from_file_location("tick_under_test",
                                                  tree / "tools/audit/seat/orchestrator_tick.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    t = mod.Tick("o/r", str(tree), relay_log=str(log))
    t.relay_owed("PRS")
    return t.sections.get("PRS", [])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--refs", type=int, default=4)
    ap.add_argument("--no-dispose", action="store_true")
    ap.add_argument("--read-log")
    a = ap.parse_args()
    tree = Path(a.tree).resolve()
    if a.read_log:
        rows = reader(tree, Path(a.read_log))
        for x in rows:
            if not x["flag"]:
                print(f"  note: {x['text']}")
        print(f"RESULT tree={git('rev-parse', '--short=9', 'HEAD', cwd=tree)} read-log "
              f"log_lines={sum(1 for _ in open(a.read_log))} "
              f"printed={sum(1 for x in rows if x['flag'] and x['text'].startswith('OWED:'))}")
        return 0
    relay = tree / "tools/audit/seat/cloud_relay.sh"
    tmp = Path(tempfile.mkdtemp(prefix="hpo_tick_owed_"))
    try:
        origin, work, state = tmp / "o.git", tmp / "w", tmp / "state"
        throwaway_git_init(origin, "-q", "--bare")
        env = {**throwaway_git_init(work, "-q"), "HPO_STATE_DIR": str(state),
               "HPO_BUS_STATE": str(tmp / "bus")}
        lister = tmp / "lister.sh"
        lister.write_text("#!/bin/sh\nexit 0\n")
        lister.chmod(0o755)
        env["HPO_RELAY_PRS"] = str(lister)
        git("remote", "add", "origin", str(origin), cwd=work, env=env)
        refs = [f"refs/heads/handoff/t{i}" for i in range(a.refs)] + ["refs/heads/probe/scan-x"]
        shas = {}
        for r in refs:
            git("commit", "-q", "--allow-empty", "-m", r, cwd=work, env=env)
            shas[r] = git("rev-parse", "HEAD", cwd=work, env=env)
            git("push", "-q", "origin", f"HEAD:{r}", cwd=work, env=env)

        def run(*argv: str) -> None:
            subprocess.run(["bash", str(relay), *argv], cwd=work, env=env, check=True,
                           capture_output=True, text=True)

        for _ in range(a.passes):
            run("pass")
        disposed = set()
        if not a.no_dispose:
            run("dispose", refs[0], shas[refs[0]])
            disposed.add(refs[0])
            run("pass")
        log = state / "cloud-relay.log"
        z = "2026-10-21T08:00:00Z"
        events = [f"OWED {z} 7 {'a' * 40} confirm failed",
                  f"POSTED {z} 7 {'a' * 40}",
                  f"OWED {z} 8 - push-verdict printed no 40-hex review commit",
                  f"OWED {z} handoff-update 9 topic-9 {'b' * 40}",
                  f"OWED reviewer-fire 10 {'c' * 40} {'0' * 32} {z}"]
        with open(log, "a") as fh:
            fh.write("\n".join(events) + "\n")
        printed = [x["text"] for x in reader(tree, log)
                   if x["flag"] and x["text"].startswith("OWED:")]
        distinct = len([r for r in refs if r not in disposed]) + 3
        lines = sum(1 for _ in open(log))
        for p in printed:
            print(f"  {p}")
        print(f"RESULT tree={git('rev-parse', '--short=9', 'HEAD', cwd=tree)} passes={a.passes} "
              f"refs={len(refs)} disposed={len(disposed)} log_lines={lines} printed={len(printed)} "
              f"distinct={distinct} match={'yes' if len(printed) == distinct else 'no'}")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
