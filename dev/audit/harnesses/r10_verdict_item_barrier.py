#!/usr/bin/env python3
"""r10-verdict-item-barrier: three merge verdicts, replayed through carry_audit.

Written by the r10-verdict-item-barrier fixer. The merge train's pre-flight
(queue_pre_flight.findings_gate) parked #2513, #2544 and #2547 because
carry_audit.items() read evidence in a `Fix review: merge` verdict -- a CI
check that "does not block", a mutation re-run "not blocking" -- as finding
items with no `Carry:`. The verdicts below are the posted comments,
verbatim (issue comments 6314156311, 6314170570, 6315224098; `--fetch`
re-reads them read-only with `gh api` and compares). Each is replayed in
four forms; the metric is the count of finding items not routed (unrouted
or a bad destination) under carry_audit.audit():

  verbatim  the comment as posted.
  evidence  the same text with `## Evidence` after its first line: every
            paragraph moved, none edited.
  reshaped  the format cloud_dispatch.py now asks for: each item that hands
            something on (LIFT below) lifted, as written, to `## Findings`
            with its own `Carry:`; the rest under `## Evidence`.
  planted   reshaped plus one Evidence bullet stating a defect and deferring
            it -- the null control: a heading smuggles nothing.

  RESULT v<pr>_<form>=<n not routed>

EXPECTED RESULT (head of r10-verdict-item-barrier):
  RESULT v2513_verbatim=1 RESULT v2544_verbatim=1 RESULT v2547_verbatim=1
  RESULT v2513_evidence=1 RESULT v2544_evidence=1 RESULT v2547_evidence=1
  RESULT v2513_reshaped=0 RESULT v2544_reshaped=0 RESULT v2547_reshaped=0
  RESULT v2513_planted=1 RESULT v2544_planted=1 RESULT v2547_planted=1
At the merge base (289426c1f) the reshaped forms read 0, 1, 0 and the planted
1, 2, 1: #2544's CI paragraph ("does not block the PR") is refused under any
heading. At the head the evidence forms still refuse #2513 and #2547 (their
own deferral: "noted for a later tightening", "advisory") and #2544 (a
post-merge check that "still has to be done", which the base never flagged):
what moves to `## Evidence` unedited is caught wherever it hands something on.

    python3 dev/audit/harnesses/r10_verdict_item_barrier.py [--fetch]
"""
from __future__ import annotations

import json
import subprocess
import sys
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
sys.path.insert(0, str(ROOT / "tools" / "audit"))
import carry_audit as ca  # noqa: E402

REPO = "tvofi/heatpump_optimizer"

VERDICTS = {
    2513: (6314156311, (
        'Fix review: merge 6b46b4f8ba93ae7574312493a03fd7e0c1d2b725\n'
        '\n'
        "PR #2513, group R10-ROSTER-OPS. Fresh reviewer seat; a previous reviewer returned merge at this same head (probe/rev-2513-e19a37e0), read as one argument only -- every figure below was re-taken here. Measured head 6b46b4f8ba93ae7574312493a03fd7e0c1d2b725 (full sha in ev/HEAD.txt), still refs/pull/2513/head at verdict time (ev/head_at_verdict.txt). Merge base 6961f06637964001a2ed544e495ea0312eeefa37; dev/governance/roles/ unchanged base...main. Detached worktrees at the head (two: one for the fixer's driver, one for my own plants, so they never shared a file) and at the base.\n"
        '\n'
        'RESULT selftest head=6b46b4f8ba93ae7574312493a03fd7e0c1d2b725 "roster_edit self-test: 94 checks, 0 failed" (ev/selftest_head.txt)\n'
        'RESULT selftest base=6961f0663 "roster_edit self-test: 64 checks, 0 failed" (ev/selftest_base.txt) -- matches the body\'s df6ca4bc figure; roster_edit.py is unchanged between those bases\n'
        'RESULT mutant=null rc=0 fails=0 (ev/null.txt)\n'
        'RESULT mutants-driver plants=19 "without a FAIL line: none", rc=0, no crash tail (ev/mutants_full.txt) -- the body\'s A5/A6 crashes were host-side; all 19 killed by FAIL lines here\n'
        'RESULT mutants-harness self-test "r10_roster_ops_mutants self-test: 63 checks, 0 failed" (ev/mutants_selftest.txt)\n'
        'RESULT own-mutant=M2 (del carry[i] -> carry.pop()) rc=1 fails=4 -- killed\n'
        "RESULT own-mutant=M7 ('-' not special) rc=1 fails=2 -- killed\n"
        'RESULT own-mutant=M8 (duplicate-edge check removed) rc=1 fails=1 -- killed\n'
        'RESULT own-mutant=M1 (_cycle never marks a node finished) rc=1 -- killed by a traceback, not a FAIL line\n'
        'RESULT own-mutant=M3 (_cycle tests state 2 instead of 1) rc=1 -- killed by a traceback, not a FAIL line\n'
        'RESULT own-mutant=M4 (--match substring -> prefix) rc=0 -- SURVIVES; fail-closed (prefix hits are a subset of substring hits, so it can only refuse more or resolve an ambiguity to an entry that still contains the text)\n'
        'RESULT own-mutant=M5 (after stored sorted) rc=0 -- SURVIVES; edge order carries no dispatch meaning in the after-graph\n'
        'RESULT own-mutant=M6 (.strip() dropped from the split) rc=0 -- SURVIVES; fail-closed ("A, B" is refused as an unknown group, never written)\n'
        '   (ev/own_mutants.txt, driver ev/own_mut.py -- my own instrument, disclosed, not landed)\n'
        'RESULT live origin/main roster: 91 groups, 64 non-empty carry, 27 "carry": [], 0 key-less; dump round-trips; set-after to every group\'s own edges: 0 refused, 0 byte changes; append-carry+drop-carry on every group: 0 byte changes; a reversed real edge is refused as a cycle (ev/live_probe.txt, driver ev/live.py, in-memory, nothing written)\n'
        'RESULT live handoff/audit-r10-roster roster: 108 groups, 2 key-less (R10-HANDOFF-ARCHIVE, R10-DEPENDABOT-AIOHTTP); append+drop there adds "carry": [] to those two -- outside the body\'s claim, which is scoped to main\'s roster (default --roster-ref); non-blocking\n'
        'RESULT selftest_wiring "38 self-testing, 38 wired, 0 unwired"; tmp_paths "0 refused"; STRUCTURE RATCHET PASSED; closure select vs 6961f0663 "MODE: SCOPED -- 2 script(s) run", 5 changed files; archscore "Architecture score: dS +0.0000 NULL" (ev/cheap_checks.txt). tests/entities.py could not run locally (python3.11 SyntaxError; 3.12/3.13 lack homeassistant) -- CI fast (3.14) green is the record for it.\n'
        'RESULT merge-tree origin/main(43f79c08b) 6b46b4f8ba93ae7574312493a03fd7e0c1d2b725 rc=0 tree 91022da7f, no conflict (ev/merge_tree.txt)\n'
        'RESULT version: VERSION, manifest, RELEASE_NOTES.md, claim files, *_budgets.json, closures.json, closure.py untouched (ev/merge_tree.txt: empty diffstat)\n'
        'RESULT CI at head: 49 check runs, all concluded; every one success/skipped except nightly-status=failure (ev/check_runs.tsv)\n'
        '\n'
        'Steps:\n'
        '1. Mutation proof re-run: 19/19 plants killed by FAIL lines; 8 plants of my own, 5 killed (2 by traceback), 3 fail-closed survivors (M4, M5, M6) -- not blocking, noted for a later tightening.\n'
        '2/9. The group\'s controls ("each op\'s mutant fails its self-test arm; existing ops and the no-op path unchanged") are the finder\'s harness; the mutant driver is the fixer\'s, disclosed. I measured with the driver plus my own plants and live-roster probe (disclosed above).\n'
        '3. Null control re-run clean; base self-test 64/0, head 94/0, the 30 added checks each tied to a plant.\n'
        '4. No golden fixture or claim file touched; env_drift not applicable.\n'
        '5. Untouched.\n'
        "6. Class: the group brief carries two deliverables; this PR delivers only the ops (set-after, drop-carry) and the roster's resume.next_step dispatches the roster-sync reconciler at a new head, so the reconciler and the group's four carry items are not this PR's to disposition. For the ops it delivers, the existing ops and no-op path are pinned unchanged (no-op set-resume/set-after byte-identical arms; D1).\n"
        "7. Body's Head names 6b46b4f8ba93ae7574312493a03fd7e0c1d2b725; its figures were taken one origin/main merge earlier touching none of the five files; I re-took them at this head.\n"
        '8. Not re-derived: "121 checks, 27 failed" on the arms-without-ops tree (not rebuilt). Every other figure re-derived above.\n'
        '10. Forward-carry: none claimed, none owed by this diff.\n'
        '11. nightly-status red grades main: its log names the nightly "slow" lane failing (run 39387919507) -- this diff\'s one governance.yml hunk adds a step to instrument-self-tests, outside what nightly-status reads; not this PR\'s, and the body answers it. instrument-self-tests red at 716a34f2 is answered in the body with its cheaper detector (selftest_wiring.py --check); green at this head. pr-contract at head green, started 10:35Z after nightly-status concluded 10:04Z.\n'
        '12. Head unchanged at verdict time.\n'
        '13. merge-tree clean against current origin/main.\n'
        '14. No budget, score, ledger, closure, INERT, golden or claim movement; self-test count rise earned by the new arms.\n'
        "15. Additions stay in the existing load-modify-dump flow; no breach. Owner: .github/workflows/governance.yml is code-owned (/.github/workflows/ @tvofi, CODEOWNERS:99), so merging still needs tvofi's approving review.\n"
        'Round: first verdict from this seat at this head (second reviewer at this head overall).\n'
        '\n'
        'bus-nonce: 99034209417c54cc2ba8a44f34229a0c\n'
        '\n'
        'bus: verdict/2513 at 032c54aabb04254838743234b79e3947924fd4d8, confirmed from cloud (review/2513 at 4122f4cbe765266e2f013ca140c786d75ac10424); evidence: ~/.zcode/bus/verdicts/2513/032c54aabb04254838743234b79e3947924fd4d8/evidence\n'
        ''
    )),
    2544: (6314170570, (
        'Fix review: merge d4ab722b919b0b07917122bfe0479247bf3b989a\n'
        '\n'
        'Round 1 (there are no earlier verdicts, reviews or comments on #2544). Measured at head `d4ab722b919b0b07917122bfe0479247bf3b989a`, detached worktree. The head is unchanged at 10:42Z. Merge base `0cc148b2f`. `dev/governance/roles/` matches origin/main.\n'
        '\n'
        "**Group.** R10-PIP-BUMP is not on `handoff/audit-r10-roster`. The PR's delivery row names R10-DEPENDABOT-AIOHTTP (#2504). That group's brief supplies the finder's controls, and I ran those, not the fixer's.\n"
        '\n'
        'RESULT finder-install head rc=0 aiohttp=3.14.5   (python3.13 venv, `pip install --require-hashes --build-constraint tests/requirements-build.txt -r tests/requirements-ci.txt`)\n'
        "RESULT finder-install base rc=0 aiohttp=3.14.4   (the merge base's own lock and build constraints)\n"
        'RESULT finder-install planted-wrong-aiohttp-hashes rc=1 THESE PACKAGES DO NOT MATCH THE HASHES   (all 161 aiohttp digests altered in the full CI lock; null control: the hash list is read)\n'
        'RESULT mutation pillow-typing fixed rc=0 / mut1 (version reverted to 12.3.0, 13.0.0 hashes kept) rc=1 / mut2 (every digest altered) rc=1   (`pip download --require-hashes --no-deps`, cp314 manylinux_2_28)\n'
        "RESULT pypi-hashes: every bumped block's hash set equals PyPI's file digests: CI aiohttp 3.14.5 161/161, typing aiohttp 161/161, certifi 2/2, pillow 83/83, uv 19/19, all True\n"
        'RESULT diff: CI lock 14 pins and typing lock 112 pins, with none added or removed. Exactly five version lines move: CI aiohttp, typing aiohttp, certifi, pillow and uv. No other block changes in either version or hashes. Pillow goes from 87 to 83 hashes, matching PyPI.\n'
        'RESULT class: no other tracked requirements, lock, pyproject or manifest file pins aiohttp, pillow, certifi or uv. The class is these two locks, and both are in the diff.\n'
        'RESULT merge-tree origin/main (43f79c08b, newest at posting) rc=0. It also merges cleanly with 6961f0663.\n'
        'RESULT VERSION, manifest and RELEASE_NOTES are untouched. No golden, claim, budget or closures file changed.\n'
        'RESULT cheap checks at head: STRUCTURE RATCHET PASSED; layout self-test ok; claims hygiene ok; ALL 124 closure shrink pins PASSED; closure select gives MODE: FULL (requirements-ci.txt changes the gate itself); typing_ruler: ALL 11 source checks PASSED, including "the typing job\'s hashed lock installs the recorded pins".\n'
        '\n'
        '**CI on this head** (from the check-runs API, every run: ev/check_runs.tsv). Every gate check is green. That includes typing (the lane #2534 failed on hashes), fast (3.14), coverage, closures, mutation, env-matrix, pr-contract (twice) and budget-raise-gate. `composed-proof` is still queued, but it is not a required context and does not block the PR (tests.yml:2775).\n'
        "`nightly-status` is red, and that belongs to main, not this PR. The job reports the last scheduled run of tests.yml (the scheduled runs of 10-19 and 10-20 failed). It runs the base's pinned stdlib-only script with no pip install, so this diff cannot reach what it reads. The body names it and answers it, so step 11 is satisfied.\n"
        '\n'
        '**Figures I could not re-derive** (step 8):\n'
        '- The 27 open Dependabot alerts and their first-patched versions: the alerts API returns 403 to this seat. They are not verified.\n'
        '- "ALL 12 typing-ruler checks": I get 11 here. The twelfth is the mypy census, which runs only with HPO_TYPING_PYTHON set. CI\'s green `typing` job is that check, so I cite it rather than confirming 12 locally.\n'
        '- The "112 of 112 blocks" download sweep and the 3.13.15/3.14.7 byte-identical compile: I did not re-run them. CI\'s typing install and my PyPI digest comparison cover the same property.\n'
        '- `tests/entities.py` needs homeassistant installed, so I did not run it here. CI `fast` ran it in FULL mode and it is green.\n'
        '\n'
        "**Steps not applicable.** Step 2 (a baseline-to-head harness metric): the finder's install control is the measure, and it is run at both ends above. Step 4: there is no fixture drift and no claim files were touched. Step 10: the body says forward-carry none, and I found no later-stage finding. Step 14: no instrument number moves. Step 15: the added lines are lock data plus a header comment recording the uv/pillow overrides and when to drop them, which is sound.\n"
        '\n'
        '**Notes for the orchestrator.**\n'
        "- The roster's R10-DEPENDABOT-AIOHTTP still shows a resume at `fix/r10-dependabot-aiohttp`. This PR supersedes the brief's 3.14.4 target with 3.14.5.\n"
        '- The brief asks for a post-merge check that the GHSA alerts closed, which still has to be done.\n'
        "- The body's step-7 head chain (code head a758413a, merged with main 0cc148b2f as 1b87eb40, plus a delivery row as d4ab722b) matches `git log`.\n"
        '\n'
        'bus-nonce: 9bb2f26885d4acc59d4a6edd5dcf6555\n'
        '\n'
        'bus: verdict/2544 at 9314350826e75e9c4135c7bbd1db64d195ed87a6, confirmed from cloud (review/2544 at 83e9168e9fe41ba2f86e6615378c0b4c675b12cc); evidence: ~/.zcode/bus/verdicts/2544/9314350826e75e9c4135c7bbd1db64d195ed87a6/evidence\n'
        ''
    )),
    2547: (6315224098, (
        'Fix review: merge 90bab078d19dd6aebba140fa360576b7780a560a\n'
        '\n'
        'bus-nonce: 43ea241b40ae10814cc74e8b5440c87c\n'
        '\n'
        "Round 1 cloud review of PR #2547 (R10-TICK-OWED-LEVEL). I measured head 90bab078d19dd6aebba140fa360576b7780a560a and it was still the branch head right before I returned this (ev/HEAD.txt). I worked from detached worktrees at the head, at the code's measured base df6ca4bc6 and at the current merge base 6961f0663. `git diff <mb>...origin/main -- dev/governance/roles/` was empty, so my contract copy is current.\n"
        '\n'
        "Harness: the brief names no finder harness, and the finding (orchestrator, 2026-10-21) never committed one. That is itself a finding under step 9, and the fixer disclosed it. The only committed harness is the fixer's `dev/audit/harnesses/r10_tick_owed_level.py`. I re-ran it, and I also built an instrument of my own, disclosed here as the reviewer's (ev/probe_deleted_ref.sh): a ref deleted from origin must leave the level after one pass.\n"
        '\n'
        'RESULT lines (ev/harness.txt, ev/mine-deleted-ref.txt):\n'
        '- baseline df6ca4bc6: `passes=3 refs=5 disposed=1 log_lines=24 printed=22 distinct=7 match=no`. Merge base 6961f0663 gives the same.\n'
        '- head 90bab078d: `passes=3 refs=5 disposed=1 log_lines=5 printed=7 distinct=7 match=yes`\n'
        '- null control `--passes 1 --no-dispose`: the baseline prints `printed=8 distinct=8 match=yes` and the head prints the same. It is flat at both ends, as claimed.\n'
        '- other configuration `--passes 10 --refs 20`: the baseline prints `printed=233 distinct=23 match=no` and the head prints `printed=23 distinct=23 match=yes`.\n'
        '- my probe (deleted refs): the baseline prints `owed_after_delete=7 want=1 match=no` and the head prints `owed_after_delete=1 want=1 match=yes`.\n'
        '\n'
        'Mutation proof (ev/mutants.txt). Every mutant was killed and restored, and the tree was left clean.\n'
        '- M1 to M4 reproduce the body exactly (2, 2, 2 and 1 named FAILs; 81 and 154 checks).\n'
        '- My own mutants:\n'
        '  - M5 drops the handoff `level_set`: cloud_relay prints 8 FAIL.\n'
        '  - M6 makes the reader ignore `.level`: tick prints 1 FAIL.\n'
        '  - M7 makes a failed probe listing clear the level: 1 FAIL.\n'
        '  - M8 makes the `dispose --log` CLI ignore `--log`: 1 FAIL.\n'
        '  - M9 appends the level to the log again: 1 FAIL ("the event log carries no level line").\n'
        '\n'
        'Self-tests (ev/selftests.txt):\n'
        '- head: tick `154 checks, 0 failed`; relay `81 checks, 0 failed`\n'
        '- base: tick 150/0; relay 74/0\n'
        '\n'
        'These match the body.\n'
        '\n'
        "Class (step 6). I ran the body's two enumeration rules at the head (ev/seams-*.txt):\n"
        '- There is one writer, cloud_relay.sh. The level kinds `probe-ref` and `handoff-no-pr` both move to level_line/level_set.\n'
        '- The events are owed(), handoff-update, approve-held-runs, dispatch (x2) and reviewer-fire. Each has its PR as the first all-digit field in f[1:4].\n'
        '- There is one reader, orchestrator_tick.py. Its hermetic default is os.devnull, which makes `.level` not-found, which is harmless.\n'
        '- governance.yml only runs the self-test, and tick_loop.sh does not read the log.\n'
        '- No seam is outside the diff.\n'
        '\n'
        'Figures:\n'
        '- The figures for fixture, null, self-tests, structure (`STRUCTURE RATCHET PASSED`) and archscore (`dS +0.0000 NULL`) are re-derived (ev/cheap-checks.txt).\n'
        "- I could NOT re-derive the recorded-log figure (35214 lines -> printed=15; 34757/13/442/2 split). Its archive lives on the orchestrator's machine, so it is unverified here.\n"
        '- `harness_headers.py` could not run locally (no voluptuous). CI covers it.\n'
        '\n'
        'Other checks:\n'
        '- VERSION, the manifest and RELEASE_NOTES are untouched.\n'
        '- No claim files or golden files were touched (diff stat).\n'
        '- The `closures.json` change is one INERT read for the new harness file. The new file earns it.\n'
        '- Merge: `git merge-tree --write-tree origin/main(03b49e152) 90bab078d` exits 0 with no conflict and no claim driver involved (ev/merge-tree.txt).\n'
        '\n'
        'CI (ev/check-runs.txt, from the check-runs API at the head): 49 runs. Every run is success, skipped or neutral except `nightly-status` (failure). That check reports main\'s last scheduled run, through the pinned base copy of tests/nightly_status.py. The diff touches neither that file nor tests.yml, so the failure is not this PR\'s. `pr-contract` is green, and it ran after the last red concluded. Earlier heads in the range: b38c6431 has no red, and 12dfce128 has only nightly-status (ev/check-runs-range.txt). So the body\'s "Red checks: none" holds.\n'
        '\n'
        'Forward-carry: the body\'s "none" holds for this PR\'s own findings. The roster carries one item INTO this group (from #2545): "its grammar must agree with the ledger\'s when that lands." No such ledger is on main (03b49e152), so that agreement binds whichever lands second. The body does not mention the carry. This note is advisory and does not block.\n'
        '\n'
        'Architecture (step 15): there is one owner of the grammar (cloud_relay.sh writes, the tick reads), and writes go through temp+mv. The reader-side skip of PR-less OWED lines is a transitional compat arm, and the body says so. I found no breach.\n'
        '\n'
        'bus: verdict/2547 at e71c4303e5596dc1021a55b2a733a447453b8bb7, confirmed from cloud (review/2547 at 49c21173e62feaef4d9aadd919dc8a7e977fae04); evidence: ~/.zcode/bus/verdicts/2547/e71c4303e5596dc1021a55b2a733a447453b8bb7/evidence\n'
        ''
    )),
}

# The text each verdict hands on, as written, and the Carry: a reviewer
# following the new prompt would give it (illustrative destinations: a
# dismissal needs no roster, so the replay reads none).
LIFT = {
    2513: (" -- not blocking, noted for a later tightening.",
           "- Mutation proof: three fail-closed survivors (M4, M5, M6), not blocking, noted for a later "
           "tightening. Carry: dismissed: fail-closed survivors only refuse more"),
    2544: ("- The brief asks for a post-merge check that the GHSA alerts closed, which still has to be done.\n",
           "- The brief asks for a post-merge check that the GHSA alerts closed, which still has to be done. "
           "Carry: dismissed: the orchestrator's post-merge step, recorded in the row"),
    2547: (" The roster carries one item INTO this group (from #2545): \"its grammar must agree with the "
           "ledger's when that lands.\" No such ledger is on main (03b49e152), so that agreement binds "
           "whichever lands second. The body does not mention the carry. This note is advisory and does "
           "not block.",
           "- The roster carries one item INTO this group (from #2545): \"its grammar must agree with the "
           "ledger's when that lands.\" No such ledger is on main (03b49e152), so that agreement binds "
           "whichever lands second. The body does not mention the carry. This note is advisory and does "
           "not block. Carry: dismissed: binds whichever lands second"),
}
PLANT = "- The stale-head guard misses a deleted ref; deferred to a later round.\n"


def forms(pr: int) -> dict[str, str]:
    body = "".join(VERDICTS[pr][1])
    first, rest = body.split("\n", 1)
    cut, finding = LIFT[pr]
    if rest.count(cut) != 1:
        raise SystemExit(f"LIFT for #{pr} not found once")
    kept = rest.replace(cut, "." if cut.startswith(" --") else "")
    reshaped = f"{first}\n\n## Findings\n\n{finding}\n\n## Evidence\n{kept}"
    return {"verbatim": body, "evidence": f"{first}\n\n## Evidence\n{rest}",
            "reshaped": reshaped, "planted": reshaped.rstrip("\n") + "\n\n" + PLANT}


def not_routed(text: str) -> int:
    dests = ca.Dests({"groups": []}, set(), None)
    rows = ca.audit("", [{"id": 0, "body": text}], dests)["rows"]
    return sum(r["status"] != "routed" for r in rows)


def main(argv: list[str]) -> int:
    if "--fetch" in argv:
        for pr, (cid, parts) in VERDICTS.items():
            r = subprocess.run(["gh", "api", f"repos/{REPO}/issues/comments/{cid}"],
                               capture_output=True, text=True)
            live = json.loads(r.stdout).get("body") if not r.returncode else None
            print(f"RESULT fetch_{pr}={'identical' if live == ''.join(parts) else 'DIFFERS'}")
    for pr in VERDICTS:
        for name, text in forms(pr).items():
            print(f"RESULT v{pr}_{name}={not_routed(text)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
