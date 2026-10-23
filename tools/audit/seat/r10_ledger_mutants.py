#!/usr/bin/env python3
"""R10-ORCH-LEDGER: every plant must turn its owner's self-test red.

Metric, one line per plant: `RESULT mutant=<name> rc=<rc> fails=<n>`, then the
failing check names. Each plant is one exact one-occurrence replacement in one
of the files the ledger change touched; the driver applies it, runs that
file's owner's self-test (ledger.py for the ledger and open_pr.sh's attempt
lines, cloud_relay.sh, orchestrator_tick.py), and restores the file byte for
byte. It refuses to start when a target differs from HEAD, so a restore cannot
overwrite work. Expected: every plant rc=1 with fails>=1 -- a FAIL line, not a
crash (a crash is rc=1 with fails=0 and prints its tail). Each plant mutates
a predicate, never a tail.

    python3 tools/audit/seat/r10_ledger_mutants.py [plant ...]
    python3 tools/audit/seat/r10_ledger_mutants.py --null
    python3 tools/audit/seat/r10_ledger_mutants.py --self-test

Null control: `--null` runs the three self-tests with no plant, which must
print rc=0 fails=0 each. `--self-test` runs no plant and pins the sweep's
preconditions: every anchor occurs exactly once, every plant changes its text,
and every Python mutant parses.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEDGER, RELAY, TICK, OPENER = ("tools/audit/seat/ledger.py", "tools/audit/seat/cloud_relay.sh",
                               "tools/audit/seat/orchestrator_tick.py", "tools/audit/seat/open_pr.sh")
OWNER = {LEDGER: LEDGER, OPENER: LEDGER, RELAY: RELAY, TICK: TICK}
PLANTS = {
    # the ledger: event closers, the level's closers, aging, refusals, stores
    "L1_readback_no_close": (LEDGER, '                how = "read-back"', "                how = None"),
    "L2_moved_head_kept": (LEDGER, 'else "superseded" if sha != "-" and live[subj] != sha else None)', "else None)"),
    "L3_any_verdict_posts": (LEDGER, '(text in lines if kind == "verdict-unposted"',
                             '(bool(lines) if kind == "verdict-unposted"'),
    "L4_added_lines_unchecked": (LEDGER, "if not add <= have or rem & have:", "if rem & have:"),
    "L5_no_ancestry_close": (LEDGER, "carried[t] = bool(sha) and ((rc == 0 and bool(out.strip())) or covered(git, main, sha))",
                             "carried[t] = bool(sha) and covered(git, main, sha)"),
    "L6_no_content_close": (LEDGER, "carried[t] = bool(sha) and ((rc == 0 and bool(out.strip())) or covered(git, main, sha))",
                            "carried[t] = bool(sha) and (rc == 0 and bool(out.strip()))"),
    "L7_no_threshold": (LEDGER, "           if age >= aging[0]]", "           if True]"),
    "L8_future_stamp_aged": (LEDGER, "        if age < 0:\n            continue  # stamped",
                             "        if False:\n            continue  # stamped"),
    "L9_unknown_kind_taken": (LEDGER, "    if kind not in KINDS:\n        raise Refused", "    if False:\n        raise Refused"),
    "L10_first_disposition": (LEDGER, "        last.pop(f[0], None)\n        last[f[0]] = f[1]", "        last.setdefault(f[0], f[1])"),
    "L11_bad_row_read": (LEDGER, "            raise Unreadable(f\"{EVENTS}: a row '{op} {kind} {sha}' of no ledger shape\")",
                         "            pass"),
    "L12_board_owed_rc0": (LEDGER, "            return 1 if open_ else 0", "            return 0"),
    "L13_state_ref_owed": (LEDGER, "        if STATE_REF.match(t):", "        if False:"),
    "L14_disposition_ignored": (LEDGER, '        elif disp.get(ref, ("",))[0] == sha:', "        elif False:"),
    "L15_reader_persists": (LEDGER, "        if persist:\n            _write(home / EVENTS", "        if True:\n            _write(home / EVENTS"),
    "L16_moved_design_owed": (LEDGER, "if not m or designs.get(t) != m.group(1):", "if not m:"),
    "L17_dispatch_ignored": (LEDGER, " or (str(n), head) in dispatched:", ":"),
    "O1_no_attempt_on_exit": (OPENER, "pr_exit_trap 'python3 -I \"$SEAT/ledger.py\" attempt", "pr_exit_trap ': python3 -I \"$SEAT/ledger.py\" attempt"),
    # the relay writes through the ledger
    "R1_verdict_not_owed": (RELAY, '  ledger_open verdict-unposted "$pr" "$head" "$first"\n', ""),
    "R2_reviewer_not_owed": (RELAY, '      ledger_open reviewer-fire "$pr" "$nh" "nonce=$nonce"', "      :"),
    "R3_update_level_unset": (RELAY, '  level_set handoff-update "$state/cloud-level-update.$$"\n', ""),
    "R4_unreadable_clears": (RELAY, "  case $? in 0|1) level_set handoff-no-pr", "  case $? in *) level_set handoff-no-pr"),
    "R5_disposition_unread": (RELAY, 'disposed() { ledger disposed "$1" "$2"; }', "disposed() { false; }"),
    # the tick reads the ledger
    "T1_unkinded_printed": (TICK, "            if len(f) > 2 and f[2] in lg.KINDS:", "            if True:"),
    "T2_no_reads_fold": (TICK, 'lg.fold(rows, getattr(self, "_live", None), getattr(self, "_readback", None))', "lg.fold(rows)"),
    "T3_review_owed_silent": (TICK, "            for text in lg.review_owed(prs, self._readback, dispatched):\n                self.line(S, text, flag=True)",
                              "            for text in lg.review_owed(prs, self._readback, dispatched):\n                pass"),
    "T4_no_escalation": (TICK, "                                aging, group_of):\n            self.line(S, text, flag=True)",
                         "                                aging, group_of):\n            pass"),
    "T5_no_design_build": (TICK, "        self.design_builds(S, rl, roster)\n", ""),
    "T6_unreadable_silent": (TICK, '            self.unreadable(S, "obligations ledger", str(e)[:100])\n            return\n        if not rows',
                             "            return\n        if not rows"),
    "T7_readback_uncollected": (TICK, '            self._readback[str(n)] = [(c.get("body") or "").split("\\n", 1)[0].rstrip("\\r") for c in vs]',
                                "            pass"),
}


def target_self_test(owner):
    argv = ["bash", owner, "--self-test"] if owner.endswith(".sh") else [sys.executable, "-I", owner, "--self-test"]
    r = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=900)
    fails = [ln.strip() for ln in r.stdout.splitlines() if ln.strip().startswith("FAIL")]
    return r.returncode, fails, (r.stdout + r.stderr).strip().splitlines()[-3:]


def report(name, rc, fails, tail):
    print(f"RESULT mutant={name} rc={rc} fails={len(fails)}")
    for f in fails:
        print("   ", re.sub(r" \(rc=.*\)$", "", f))
    if rc and not fails:
        print("    crash tail:", *tail, sep="\n      ")


def self_test():
    passed = failed = 0

    def ck(name, ok):
        nonlocal passed, failed
        passed, failed = passed + ok, failed + (not ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")

    for name, (target, old, new) in PLANTS.items():
        text = (ROOT / target).read_text()
        ck(f"{name}: anchor occurs once in {target}", text.count(old) == 1)
        ck(f"{name}: the plant changes the text", new != old)
        if target.endswith(".py"):
            try:
                compile(text.replace(old, new), target, "exec")
                ok = True
            except SyntaxError:
                ok = False
            ck(f"{name}: the mutant parses", ok)
    ck("every plant's target has an owner self-test", all(t in OWNER for t, _, _ in PLANTS.values()))
    print(f"r10_ledger_mutants self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv):
    if argv == ["--self-test"]:
        return self_test()
    targets = sorted({t for t, _, _ in PLANTS.values()})
    if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *targets], cwd=ROOT).returncode != 0:
        print(f"refusing: a target differs from HEAD ({', '.join(targets)})", file=sys.stderr)
        return 2
    if argv == ["--null"]:
        for owner in sorted(set(OWNER.values())):
            report(f"null:{owner}", *target_self_test(owner))
        return 0
    names = argv or list(PLANTS)
    unknown = [n for n in names if n not in PLANTS]
    if unknown:
        print(f"unknown plant(s): {unknown}", file=sys.stderr)
        return 2
    survivors = []
    for name in names:
        target, old, new = PLANTS[name]
        path = ROOT / target
        original = path.read_bytes()
        try:
            text = original.decode("utf-8")
            if text.count(old) != 1:
                print(f"plant {name}: anchor occurs {text.count(old)} times", file=sys.stderr)
                return 2
            path.write_bytes(text.replace(old, new).encode("utf-8"))
            rc, fails, tail = target_self_test(OWNER[target])
        finally:
            path.write_bytes(original)
        report(name, rc, fails, tail)
        if not fails:
            survivors.append(name)
    print(f"plants: {len(names)}, without a FAIL line: {survivors or 'none'}")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
