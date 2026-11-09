Fix review: blocked 00d12cad0f12bb8eb7da1010a720f7576fd4a552 ci-red: gate red at this head because codeql / Analyze (python) was cancelled at its 45-minute timeout on both attempts; every test lane is green and the patch verifies

bus-nonce: 95a7f18af05fa01ce82707f826630026

## Block

`python3 tools/audit/seat/merge_train.py classify 00d12cad0f12bb8eb7da1010a720f7576fd4a552 --pr 3349` exited 1 at 07:04:26Z: `RED 00d12cad0f12bb8eb7da1010a720f7576fd4a552 pending: none red: gate` (ev/ci-classify.txt). The latest `gate`, job 129022507126, concluded at 07:03:50Z. Its log reads `FAIL codeql / Analyze (python): cancelled (this run)` (ev/job-129022507126.log). That analysis, job 129003558776 in run 42539673685, ran from 05:50:23Z to 06:35:30Z, which is the job's `timeout-minutes: 45`. This is its second cancellation at this head: the first was job 128913029832, which the body answers. `codeql / Analyze (python)` and `gate` are both in `merge_train.py owed-reds` (ev/owed-reds.txt), and a red CI never earns `merge`. The patch itself is not blocked on merit (see Evidence). To unblock, re-run the python analysis to completion on this head (the orchestrator's job: the head is frozen), then re-review or carry. Nothing in this repository shows whether the timeout is caused by the diff. The diff touches one production file, so a timeout caused by the diff is unlikely, but I did not measure it.

## Findings

- `codeql / Analyze (python)` has been cancelled at the 45-minute timeout on both attempts at this head (jobs 128913029832 and 129003558776). If the re-run times out again, the cause needs its own measurement: whether the analysis is near its timeout on main too, or whether this head pushes it over. Carry: R10-HOTFIX-STRESS-MEM-PEAK
- The body names the roster carries' file and stage by `origin/handoff/audit-r10-roster` but not by branch SHA, as `finding-propagation.md`'s Enforcement asks. I opened both at the branch tip b1de33a83a (commits f70dcd9d51 and ccc3286441). Both state the precondition, the base-beside-head control table and the re-measure instruction (ev/roster-carries.txt). Carry: R10-HOTFIX-STRESS-MEM-PEAK

## Evidence

- Round: the second review at this head. The first, verdict/3349 61a90cfce8, was blocked `carry-missing`. This round's body changes no code.
- Head reviewed: 00d12cad0f12bb8eb7da1010a720f7576fd4a552 (ev/HEAD.txt), base fdc8d21ada, matching the body's `## Head`. `fix-review.md` on origin/main differs from the merge base only in step 11's required-check wording; I followed main's text.
- Merge: `git merge-tree --write-tree origin/main 00d12cad...` exit 0, tree e4299609ea, origin/main 0a8033305d (ev/merge-tree.txt).
- Prior block resolved (step 10): the roster branch origin/handoff/audit-r10-roster at b1de33a83a carries item f10894a6 in R10-GENERIC-HEAT-CURVE's `carry` (resume `in-progress`, PR 3299) and item a9dfb833 in R10-PARTLOAD-RESIDUE's (resume `carries-open`). Each carries the control table, the precondition ("not, alone, evidence against a diff") and the re-measure instruction. The body also discloses that the in-window import check fires off Linux only, which settles the prior verdict's second finding.
- Mutation proof (step 1), `PYTHONPATH=tests/hastub python3 tests/features.py` in worktrees at the head:
  - head: `ALL 4979 FEATURE CHECKS PASSED`, both `_blas_pin_shared_controller` arms `ok`.
  - mutB (`_blas_threads.limit` replaced by a per-call `threadpoolctl.threadpool_limits`): `FAIL the BLAS thread pin reuses ... [constructions=4 (want 1 ...), _blas_threads=ThreadpoolController`, `1 of 4979 FEATURE CHECKS FAILED`.
  - mutC (GUARD_OFF, `if False:`): `FAIL without threadpoolctl ... AttributeError("'NoneType' object has no attribute 'limit'")`, `1 of 4979 FEATURE CHECKS FAILED`.
  - Logs and mutant diffs: ev/features-*.log, ev/mutant-*.diff. The mutA (base optimizer.py) kill is cited from verdict/3349 and not re-run.
- Replay re-record (step 14), re-derived (ev/replay-derive.txt):
  - `derive_cost_classes` gives ref47 2.7713 at the head and 3.3424 without job 128866186676's rows, so the change is earned by the new draw alone.
  - With ref47 at 3.3424, `draw_offenders` names job 128866186676 (`budget 3.342 cannot see a 2x cycle; re-record 2.193`); at the head it names none.
  - `control:cycle_cost:draws` is True, and both re-cut nulls are named.
- Class rule (step 6): `git grep -n "tracemalloc.start"` returns 9, as the body says. Production `threadpool_limits|ThreadpoolController` sites in custom_components: one construction at optimizer.py:867 plus a comment line.
- Untouched (step 5): VERSION, the manifest, RELEASE_NOTES.md and both claim files (empty three-dot diff). `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- CI at this head:
  - All test lanes are green: `tests / fast (3.14)` 129003560724, `tests / replay` 129003560388, `tests / mutation` 129003559743, `tests / closures`, `tests / typing`, arch-score, budget-raise-gate.
  - `governance / delivery-status` is red and is not required.
  - `gate` 128984122807 (04:50Z) reads `FAIL run(s) [42539673685] at this head are still being judged`, a deferral.
  - `pr-contract / pr-contract` 129017437005 (started 06:50:17Z, after the 06:35Z cancellation) passed: `record red-history ... governance / delivery-status, tests / mutation, tests / replay`, `clean no refusal`, CARRY-AUDIT 5 routed 0 unrouted. The latest `gate` concluded red after that run. I issue no root-cause ruling on this red: a cancellation at the timeout is not a test failure, and the body already answers the first one.
- Figures I could not re-derive: the body's macOS figures and its out-of-tree `$S` instruments, cited by sha1 only, and the Linux stress table, which is the prior reviewer's and is cited from verdict/3349.
