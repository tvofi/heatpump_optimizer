Fix review: blocked aef46436e67c917821a6126aa882d2a4f2468a28 root-cause-detectable: pr-contract went red at first-parent head 0adc19241 (run 117608332257, 06:40Z, "## Head" named f4df860) and the Red checks table does not name it; every other red on the 27 first-parent heads is answered, and the code is mergeable

bus-nonce: 30ab759ca08b55ba0aaf8b25ae4cd4b6
This is a re-review after my round-1 block on dec7b91ea, judged at head aef46436e67c917821a6126aa882d2a4f2468a28. The PR as a whole is in round 4 or later.

## Head and carry
aef46436e = 0adc19241 + main 2b06786c2. `git merge-tree --write-tree 0adc19241 2b06786c2` gives tree ed82c4ad5, which is the head's own tree, so the merge resolved nothing.
Main brought no change to custom_components/, tests/*.py or log_flood/. It touched only records, ledger rows, other dimensions' round-10 artefacts and seven tools/ files outside the closure that matters here. So my 0adc19241 figures carry. I re-ran the probe, my recurrence harness and the census at aef46436e anyway.
merge-tree against current origin/main: rc=0, no conflict; the head is 8 commits behind.
The body's ## Head names aef46436e (on the 0adc19241 base), which matches.

## Round-1 block: resolved
Every site now passes its condition as `active` and clears on recovery. `async_shutdown` calls `forget_held(hass)`. The failed solve starts as ERROR with exc_info.
Finder's probe at the head (it now carries the recur_* arms):
RESULT recur_future_stamp.hold=2 clear=0 recur=2
RESULT recur_solve_failure.hold=1 clear=0 recur=1
RESULT recur_space_target.hold=1 clear=0 recur=1
RESULT recur_valve_write.hold=1 clear=0 recur=1
RESULT recur_reload.hold=2 clear=0 recur=2
Every one of the 13 flood arms reads floods=0, rc=0.
My own harness from round 1 at the head: future_stamp 2/0/2, solve_failure 1/0/1, space_target 1/0/1. Round 1 read recur=0 on all three.
My after_reload arm reads 0. That is a defect in my harness, not in the code: it builds a second coordinator without calling async_shutdown. The real reload path does call it (async_unload_entry -> coordinator.async_shutdown, __init__.py:424), and the probe's recur_reload, which does shut down, reads 2.
Census: RESULT sites=71 latched=6 seams=65. The extra seam is the latch's own ERROR branch, and it is on the barrier list.

## The two survivors, re-run at 0adc19241 (production tree identical at aef46436e)
RESULT survivor_valve_GUARD_OFF (coordinator.py, "if log_held(self, \"valve_write\" ...)" -> "if False:"): features.py rc=1 killed, by the "#2351: a write the valve refused is not remembered as commanded" check. The probe also kills it: recur_valve_write hold=0, rc=1.
RESULT survivor_space_CMP_BOUND (pump_arbiter.py, ">" -> ">="): features.py rc=1 killed, by the "#2351: ... exactly the tolerance above the room target is written" check. The probe does not kill it (rc=0), which is expected because no arm sits at the bound.
Both pins name the right killer. Restored clean.

## My own mutants
RESULT own_forget_held_DEL (delete `forget_held(self.hass)` in async_shutdown): features.py rc=0, so it SURVIVES there. probe.py kills it: rc=1, recur_reload recur=0.
The body's mutation proof 2 names the probe for this line, so it is answered as claimed. features.py tests `forget_held` directly, not its call site. That is a gap for the gate, not for this PR's claims.
RESULT own_flowunit_clear_DEL (delete the flow-unit path's `log_held(..., False)` in _space_target): features.py rc=0 and probe.py rc=0, so it SURVIVES both. Changing the unit to Flow is an options change. `async_update_options` reloads the entry on any real change (__init__.py:398), and the reload's `forget_held(hass)` already drops the key. So in practice this clear is redundant with the reload path: an equivalent mutant, not a lost signal. I note it and do not block on it.
Not blocking either: `forget_held(hass)` is keyed on the shared `hass`. On a multi-entry install, one entry's unload re-arms the other entries' reader and arbiter latches, so each warns once more. That is one extra WARNING, not a flood.

## The block: step 11 against every first-parent head
I read check-runs on all 27 first-parent heads in origin/main..aef46436e67c917821a6126aa882d2a4f2468a28 (evidence/r3.allruns.tsv) and matched each failure against the body's Red checks table (evidence/r3.reds.tsv):
- 15 failures in total.
- 14 are named with an answer: 83bf0770c (arch-score, fast, mutation, pr-contract), fc9d9186d, 7ef037831 and 225bff1cf (delivery-status), 7ef037831 (pr-contract), 225bff1cf (fast), 72a6844ae (pr-contract), f4df86098 (mutation, pr-contract), and 75a788a87 (mutation, two runs).
- UNNAMED: 0adc19241 pr-contract, failure, run 117608332257 at 06:40:06Z. The "Check the body against the contract" step failed with "PR-BODY: 1 error(s)" because the body still named f4df860.
That head's only pr-contract run is the red one, and the push to aef46436e superseded it.
The answer is one line in the shape of the table's existing f4df86098 and 72a6844ae pr-contract rows, whose own cheaper detector is tools/pr/prepr.sh step 7. Hence root-cause-detectable. I check that the trigger is answered, not the answer itself.
Cancelled runs on superseded heads are not counted.

## Other steps
CI at aef46436e67c917821a6126aa882d2a4f2468a28, latest run per name (evidence/r3.check-runs.head.tsv): 27 success, 15 skipped, 0 red. Every workflow has concluded, and the head's pr-contract runs (06:51Z, two) started after the 06:40Z red. The mutation lane log reads "scope changed: 5 production file(s)" and "MUTATION TABLE PASSED". Not re-run: the gate and the mutation table.
Steps 5, 10 and 14 are unchanged from round 1. VERSION, the manifest and the notes heading are untouched, and so are both claim files. Forward-carry is none. For private_cross_module, the body cites 17 (budget 17) and dS +0.0011 IMPROVES; I did not re-take archscore, and the arch-score check is green at the head.
Evidence: /Users/timmalmstrom/hpo-seats/r10s3/review-n-log-flood/evidence
