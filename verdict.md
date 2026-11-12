Fix review: blocked 907c15d3755fa459b6bd91333fdc2a2828d47995 mutation-vacuous: beatd floor refusal disabled; beatd launch.json never written; pulse snapshot_live never reads the train; --train-state never passed to snapshot_live

bus-nonce: d7a360748e386c9bd5ddd1b0627d7c85

## Block

Round 1. Handoff review at head 907c15d3755fa459b6bd91333fdc2a2828d47995 (refs/heads/handoff/r10-standing-contracts-p2 still points at it), body 22884c42 (refs/heads/handoff-body/r10-standing-contracts-p2), merge base 2ced371c1a.

The body says carry 21 is built: "beatd.py records its launch and refuses an interpreter below 3.12 naming it", and says carry 23's pulse "reads the train ... (--train-state, default $HPO_STATE_DIR/merge_train)". I mutated four of the lines that do this work. hooks_setup.py --self-test and pulse.py --self-test both stay green at rc 0 under each one (ev/reviewer-mutants-run1.txt):

- A: in beatd.py cmd_run, `if sys.version_info < FLOOR:` replaced with `if False:`. It survives. The only case covering this, "beatd: refuses to start under an interpreter older than the floor, naming it", greps beatd.py's source for `FLOOR = (3, 12)` and the message text. It never runs cmd_run, so the refusal is not tested. Carry 21 asks for "a planted case and a null control" per arm. This arm has neither.
- B: in beatd.py, the `launch.json` write renamed to `launch.jsonX`. It survives. The restart cases plant launch.json by hand, so nothing checks that beatd records the launch the restart arm replays.
- I: in pulse.py snapshot_live, `snap["train"] = read_train(train_state)` replaced with `pass`. It survives.
- L: in pulse.py main, `a.train_state` passed to snapshot_live replaced with `None`. It survives. With I, this means the live path (`--train-state` through snapshot_live to judge_verdict) is untested. Only judge_verdict over a fixture `train`, and read_train called directly, are covered. Carry 23's measured symptom, 13 STOPPED at 01:10Z, is a symptom of that live path.

Each needs a case that runs the behaviour, and the mutant above must fail it. Examples: run cmd_run with FLOOR set above the running interpreter and expect the Refuse message naming sys.executable. Run `beatd.py run --once` on a fixture state and read launch.json back. Drive main()/snapshot_live with `--train-state` on a planted spool, or move the train read into a seam that the snapshot test covers.

## Findings

- The body's first line says it "forward-carries 24", but `## Forward-carry` says none and the Carry 24 line says not answered here. The brief and the second commit (907c15d375) say carry 24 is deferred to a later part. The re-cut body should say one thing. Carry: dismissed: settled by the re-cut this block requires
- pulse.py `--train-state` defaults to None when HPO_STATE_DIR is unset. merge_train.py's `--state-dir` falls back to ~/.local/state/hpo/merge_train instead (merge_train.py:9284). Under an unset HPO_STATE_DIR, pulse reads no train and counts the pre-PR STOPPED set. That fails safe, but it is a second spelling of the train's default. Carry: dismissed: fails safe to the pre-PR count; the re-cut may take merge_train's default through the same seam as the block's case I/L

## Evidence

- RESULT hooks_setup.py --self-test: head 58 checks 0 failed (ev/head-hooks_setup.py.txt); merge base 39 checks 0 failed (ev/base-hooks_setup.py.txt). No instrument self-test is red at the head that was green at the base.
- RESULT pulse.py --self-test: head 64 checks 0 failed; merge base 60 checks 0 failed (ev/head-pulse.py.txt, ev/base-pulse.py.txt).
- RESULT the body's in-tree mutants: all six new hooks_setup MUTANTS are killed inside the head's self-test (rc 0). I re-derived the body's pulse figures. Answer filter replaced with `is not None` gives 2 failed. Spool read dropped gives 1 failed. Both match the body (ev/reviewer-mutants.txt).
- RESULT reviewer mutants killed: C (overlay checkouts ignored), D (restart drops HPO_* env), E (restart ignores recorded cwd), F (corpus never written on compaction), G (HELD never matches), H (dead train still holds), J (relay stale bound 15 to 100; killed through the in-tree mutant anchor), K (proof never clears the marker). Driver: ev/mut.py.
- I checked carries 21, 22, 23 and 27 against roster branch handoff/audit-r10-roster at 2eadb4e258c936e85d635899223dec0b82c840f3, group R10-STANDING-CONTRACTS-P2, carry indices 21, 22, 23 and 27. Carry 22's three constraints are met in the diff: restart is beatd only, the relay is judged by log age, and the proof line names no session path (asserted by the `"session" not in proof` case). Carry 27's HANDOVER edit is present. Carry 16: ae1971474 is an ancestor of origin/main.
- `git merge-tree --write-tree origin/main 907c15d3` exits 0 with no conflict (ev/merge-tree.txt).
- VERSION, the manifest, RELEASE_NOTES.md, claim files, golden fixtures, *_budgets.json and tests/closures.json are untouched in the three-dot diff. The diff adds no new file.
- No pull request exists yet, so there are no CI checks to read, no review packet and no red check to answer. `merge_train.py owed-reds` prints coverage-ratchet, fast (3.14), mutation, typing and validate-hacs, and none of them has run on this head.
- Head re-read before return: refs/heads/handoff/r10-standing-contracts-p2 = 907c15d3755fa459b6bd91333fdc2a2828d47995.
