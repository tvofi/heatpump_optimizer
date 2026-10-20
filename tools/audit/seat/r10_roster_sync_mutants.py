#!/usr/bin/env python3
"""R10-ROSTER-OPS' roster-sync mutants: each plant must turn its own arm red.

    python3 tools/audit/seat/r10_roster_sync_mutants.py [plant ...]
    python3 tools/audit/seat/r10_roster_sync_mutants.py --null

One line per plant: `RESULT mutant=<name> rc=<rc> fails=<n>`, then the failing
check names the self-test printed. Each plant is an exact one-occurrence
replacement in `roster_sync.py`; the driver applies one, runs the reconciler's
own self-test (`run_self_test`, offline), restores the file byte for byte, and
refuses to start on a dirty tree. Expected: every plant rc=1 with fails>=1 --
a named FAIL, never a crash. The null run applies nothing and must read
rc=0, fails=0, so a plant's red is attributable to its replacement.

Plants:
  M1_deferred_overwritten     every stage is treated as derivable, so a
                              `deferred` stage is overwritten by its PR.
  M2_open_not_in_progress     an OPEN pull request makes no change, so the
                              stage a queued group derives from is never set.
  M3_merged_without_commit    a MERGED pull request sets `done` but not
                              `resume.commit` at the merge commit.
  M4_carry_to_done_appended   the done-destination guard is dropped, so a
                              `Carry: <done group>` lands instead of refusing.
  M5_second_parser            carry_audit's parser is replaced by a line
                              regex, which also reads a quoted marker in a
                              code span.
  M6_dry_run_writes           the `--apply` gate is dropped, so a dry run
                              writes the roster.
"""
import subprocess
import sys

SRC = "tools/audit/seat/roster_sync.py"
RUN = ("import sys; sys.path.insert(0, 'tools/audit/seat'); "
       "import roster_sync; sys.exit(roster_sync.run_self_test())")


PLANTS = {
    "M1_deferred_overwritten": [
        (SRC, "        if stage not in DERIVABLE_STAGES:",
              "        if False:  # M1")],
    "M2_open_not_in_progress": [
        (SRC, "        if pr.state == OPEN:\n"
              "            if stage != \"in-progress\" or resume.get(\"pr\") != pr.number:",
              "        if pr.state == OPEN:\n"
              "            if False:  # M2")],
    "M3_merged_without_commit": [
        (SRC, "            changes.append(Change(gid, \"done\", pr.number, pr.merge_commit,\n"
              "                                  stage, pr.state))",
              "            changes.append(Change(gid, \"done\", pr.number, None,\n"
              "                                  stage, pr.state))  # M3")],
    "M4_carry_to_done_appended": [
        (SRC, "                elif not roster_lib.is_open(g):",
              "                elif False:  # M4")],
    "M5_second_parser": [
        (SRC, "        result = carry_audit.audit(pr_body(pr, repo, pr_state), [],\n"
              "                                   carry_audit.Dests(roster, set()))",
              "        result = {\"rows\": [\n"
              "            {\"text\": line, \"dests\": re.findall(\n"
              "                r\"Carry:\\s*([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)\", line)}\n"
              "            for line in pr_body(pr, repo, pr_state).splitlines()\n"
              "            if \"Carry:\" in line]}  # M5")],
    "M6_dry_run_writes": [
        (SRC, "        if not a.apply:",
              "        if False:  # M6")],
}


def run(name, edits):
    orig = {f: open(f).read() for f in {e[0] for e in edits}}
    try:
        for f, old, new in edits:
            s = open(f).read()
            if s.count(old) != 1:
                print(f"RESULT mutant={name} rc=ERR fails=0\n"
                      f"    anchor not unique in {f}: {old[:70]!r} ({s.count(old)})")
                return
            open(f, "w").write(s.replace(old, new))
        r = subprocess.run([sys.executable, "-c", RUN], capture_output=True,
                           text=True, timeout=900)
        lines = (r.stdout + r.stderr).splitlines()
        fails = [ln for ln in lines if ln.startswith("FAIL")]
        print(f"RESULT mutant={name} rc={r.returncode} fails={len(fails)}")
        for ln in fails:
            print("    " + ln.strip()[:200])
        if r.returncode and not fails:
            for ln in lines[-4:]:
                print("    tail: " + ln[:200])
    finally:
        for f, s in orig.items():
            open(f, "w").write(s)
    sys.stdout.flush()


def main():
    left = subprocess.run(["git", "status", "--short", "--", SRC],
                          capture_output=True, text=True).stdout
    if left.strip():
        sys.exit(f"refusing: {SRC} is modified")
    args = sys.argv[1:]
    if args == ["--null"]:
        run("NULL_no_plant", [])
        return
    for name in args or list(PLANTS):
        run(name, PLANTS[name])
    left = subprocess.run(["git", "status", "--short", "--", SRC],
                          capture_output=True, text=True).stdout
    print("restored" if not left.strip() else "NOT RESTORED:\n" + left)


if __name__ == "__main__":
    main()
