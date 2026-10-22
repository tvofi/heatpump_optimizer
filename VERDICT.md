Fix review: blocked 7651b942166e994a29d4b2178ba551ac43565b73 mutation-vacuous: the real lane's 5 s py-spy cut is unpinned, LoopHeartbeat spy_timeout default set to 30.0 passes all 2394 entity checks

bus-nonce: 8e37448d9ee66b51b88aa5a9afe4b92e

Round 1 (first review) of PR #2605, group R10-NIGHTLY-PYSPY-RETRY, measured at head `7651b942166e994a29d4b2178ba551ac43565b73`. I re-read that head on the remote just before writing this verdict. The role contract under `dev/governance/roles/` is current: the diff of the merge base against origin/main there is empty.

## Block

- The body's first claim is "`py-spy dump --nonblocking` is cut at `PY_SPY_TIMEOUT_S` = 5 s instead of 30 s". The brief's second required mutant is "timeout removed must go red". The body's M2 mutates the `subprocess.run(... timeout=self.spy_timeout)` plumbing, and that mutant is killed. It is killed only because the stub tests pass `spy_timeout=0.5` explicitly, and M2 ignores that value.
- The real heartbeat boot passes no `spy_timeout`: `_async_check_hb` calls `_async_hb_control(checks)`, which calls `_async_hb_measure` and then `LoopHeartbeat(...)`. So the production cut is the constructor default at `tests/nightly_ha.py:1901`, `spy_timeout=PY_SPY_TIMEOUT_S`.
- Mutant X5 changes that default to `spy_timeout=30.0`. That puts the real lane's cut back at the base's 30 s. **The full `tests/entities.py` still prints `ALL 2394 ENTITY CHECKS PASSED`, rc=0** (`ev/entities-x5.txt`). The PR's own mutant harness, rerun with my substitution, says the same: `X5-dump-default-30 SURVIVED` (`ev/mutants-reviewer.txt`).
- With X5 in place, the body's worst-case figures are no longer true for the real lane. A hung episode would cost up to 3 × 30 s of sampling, not ≈ 22 s, and every check stays green. Mutant X2, `PY_SPY_TIMEOUT_S = 25.0`, also survives, because `entities.py` pins only `PY_SPY_TIMEOUT_S < 30`. Under X2 the whole-control bound becomes 3 × (26.25 + 1) ≈ 82 s, and nothing fails.
- Repair, small and local:
  - Pin the constructor default to the constant, for example `inspect.signature(LoopHeartbeat).parameters["spy_timeout"].default is PY_SPY_TIMEOUT_S`, or drive one stub try with no `spy_timeout` passed.
  - Pin the body's stated whole-control bound `HB_CONTROL_TRIES * (HB_CONTROL_HOLD_S + HB_CONTROL_REST_S)` under the base's 30 s, or under whatever figure the body states.
  - Then re-run the mutant harness with X2 and X5 added as named mutants.

## Findings

- Mutation-vacuous: the real lane's py-spy timeout is unpinned. X5 (the `LoopHeartbeat` default `spy_timeout=30.0`) and X2 (`PY_SPY_TIMEOUT_S = 25.0`) survive every check, as set out under Block. The fixer pins the default and the stated worst case on this PR, then re-runs steps 2 to 8. Carry: R10-NIGHTLY-PYSPY-RETRY
- Residual without a durable owner. The per-process py-spy hang still leaves the `stable` false-red rate where it was, ≈ 6.7 % per the RCA. The body measures this and discloses it (F6, F7, F10). Its Forward-carry routes it to R10-NIGHTLY-PYSPY-RETRY, the group this PR closes. `carry_audit` accepts that only because the group is open now; at merge the orchestrator would record it done and the residual would have no owner.
  - The group's resume must not go to `done` at this merge. It must be re-scoped as a design call among (a) inconclusive-on-timeout, which changes what the check asserts and so is the owner's call, (b) re-run the heartbeat container on a py-spy timeout, and (c) a longer non-blocking timeout.
  - Alternatively, the orchestrator registers a new design group and moves this carry there before the merge.
  - The red still blocks every PR through `nightly-status` and `pr-contract` (train 16).
  - Carry: R10-NIGHTLY-PYSPY-RETRY
- The code comment at `tests/nightly_ha.py:289-291` overstates the mechanism. It says the control tries a FRESH spin because "whatever hangs py-spy outlives a retry inside it". A reader would infer that a fresh-spin retry does rescue. This PR's own F7 measured fresh-spin retries rescuing 0 of the 2 further samples in their episode, and the body says the retry "does not lower the ≈ 7 % false-red rate". The comment should state that the retry was measured not to rescue a real-HA hang, and what it is kept for (cost per red, slow-but-healthy samples). Carry: R10-NIGHTLY-PYSPY-RETRY
- Two more constants are unpinned, both surviving mutants:
  - X1: `await asyncio.sleep(rest)` replaced with `pass`, so there is no rest between tries.
  - X3: `HB_CONTROL_TRIES = 2`, because the checks compare calls to the constant and require only `>= 2`.
  - The body says "every new constant and branch is pinned by a mutant above (M1 to M10)", which is not true for these two. Pin them in the same push, or state in the body why their values are free.
  - Carry: R10-NIGHTLY-PYSPY-RETRY
- The body's "Every bound is under `HB_HANG_S` = 60 s, which `entities.py` pins" holds only for the per-spin hold: `HB_DUMP_S + PY_SPY_TIMEOUT_S <= HB_CONTROL_HOLD_S < HB_HANG_S`. The ≈ 22 s whole-control figure is not pinned. The pin in the first finding settles this; otherwise the sentence needs rewording. Carry: R10-NIGHTLY-PYSPY-RETRY

## Evidence

- Head: `ev/HEAD.txt` = `7651b942166e994a29d4b2178ba551ac43565b73`. Remote `refs/heads/fix/r10-nightly-pyspy-retry` read at that SHA just before writing.
- Merge: `git merge-tree --write-tree origin/main 7651b942166e994a29d4b2178ba551ac43565b73` exits 0 against origin/main `04c1dd77990b97ae144e48cd29655853783532f2` and again against `cd4aaed44b9000057aeff01ee3df9f80dbec8aad`. Both write tree `00639ecc…`, there are no conflicting paths, and no claim-file driver was invoked (`ev/merge-tree.txt`).
- `VERSION`, the manifest version, `RELEASE_NOTES.md` and `tests/golden/` are untouched by the three-dot diff. No claim file moved, so step 4 has nothing to compare.
- `carry_audit.py check --body` over the PR body: `CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)` (`ev/carry-audit-body.txt`). The routing is valid at this moment. Whether its destination survives the merge is the second finding.
- Mutation proof (step 1), from the PR's own harness at the head: `SUMMARY killed=10 survived=0 null=ok`, rc=0 (`ev/mutants-head.txt`). The brief's three named mutants:
  - one attempt only: M1, KILLED;
  - timeout removed: M2, KILLED at the plumbing, but X5 SURVIVED at the production default (see Block);
  - any non-empty output accepted: M3, KILLED.
- Reviewer's own mutants, run through the same harness's `block()`/`run()` (`ev/mutants-reviewer.txt`):
  - X1 no rest: SURVIVED.
  - X2 timeout 25: SURVIVED.
  - X3 tries 2: SURVIVED.
  - X4 no break: KILLED.
  - X5 default 30: SURVIVED, and confirmed against the full `entities.py`.
  - X6, the check reading only the last try: SURVIVED. X6 is equivalent, so it is not a finding: the loop breaks on the first all-true try, so in production the passing try is always the last one.
- F2, failing test first, re-derived in process with my own driver at both ends; the hang-once stub hangs on call 1 (`ev/f2.txt`):
  - base: `pass=False calls=1 elapsed=30.3s … py-spy rc=0 names it: False`;
  - head: `pass=True calls=2 elapsed=7.1s … try 2 of 2 (at most 3)`.
  - This matches the body's 30.4 s, 1 call / pass with 2 calls.
- Null control, never-answer stub at the real constants, head (`ev/never-head.txt`): `pass=False calls=3 elapsed=17.9s … try 3 of 3`. The power to fail is kept: a sampler that never answers fails after exactly `HB_CONTROL_TRIES` calls. An answer without the spin (`idle`) and an answer naming it only at rc=1 (`torn`) are pinned by the committed checks, and M3, M6 and M9 show those pins bite.
- F5, re-derived with my own runs of the PR's container harness (`dev/audit/harnesses/r10_nightly_pyspy_retry.py`). I used the RCA's image digest `sha256:33afb0659d78…` plus a `threadpoolctl` 3.6.0 layer, and the hash-verified py-spy 0.4.2 wheel (sha256 `aeb03234…`, matching `tests/requirements-nightly-ha.txt`) (`ev/container-runs.txt`):
  - base `hang-once --runs 3`: `ok=0 fail=3`, each at `timed out after 30 seconds`;
  - head: `ok=3 fail=0`, each at `try 2 of 2`.
  - This matches the body.
- Real py-spy, my reduced sample: head `--runs 10` gave `ok=10 fail=0`, all `try 1 of 1`; base `--runs 10` gave `ok=10 fail=0`. This is not a re-derivation of F6 (20 runs), F7 (60), F8 (20) or F9 (80). I did not repeat those counts, and F6 and F9 measure code that is not at this head. At a ≈ 2 % local hang rate, 10 runs separates nothing; the body says the same of its own runs.
- Blobs: the base and the body's before-base share `tests/nightly_ha.py` blob `30f8263e…`, and the head blob is `91164340…`, matching the body (`ev/blobs.txt`).
- Worst-case bounds, from the head's constants (`HB_DUMP_S` 0.25, `PY_SPY_TIMEOUT_S` 5, so `HB_CONTROL_HOLD_S` 6.25):
  - The formula 3 × (6.25 + 1) = 21.75 s gives the body's "≈ 22 s". The control rests only between tries, so the tighter bound is 3 × 6.25 + 2 × 1 = 20.75 s. The never-answer run measured 17.9 s.
  - "3 × 5 s" is `HB_MAX_DUMPS` × `PY_SPY_TIMEOUT_S`, derived and not measured.
  - Both figures hold only while the default is wired, which is the Block.
- F10 arithmetic re-derived: 0.07² = 0.0049, so P ≈ 0.005 per episode; 0.07⁴ = 2.4e-5; 0.93²⁰ = 0.234, so P ≈ 0.23; and 3/140 = 2.1 %. All match the body. The rule (an episode is a run whose first sample timed out) is stated, and I applied it to the body's own counts. I could not re-observe the episodes.
- 710/710 and ≤ 0.15 s are the RCA's figures (`dev/audit/rca/nightly-ha-pyspy-timeout.md`, the synthetic self-dump in the image), quoted correctly. They come from a small synthetic process, not real HA. Real-HA first samples under 5 s: the body's 59 green F7 runs, my 10, and CI's stable lane at this head all returned within the cut.
- Harness: the group brief names no finder harness. The RCA's "Reproduce" section is a prose recipe. The fixer turned it into `r10_nightly_pyspy_retry.py`, disclosed it as their own reconstruction, and it lands in the tree. I used it for F5 and the real runs, and my own in-process driver for F2 and the null control.
- Class (step 6): `LoopHeartbeat.dump` is the only py-spy call site in the lane (grep over `*.py`, `*.yml`, `*.sh` outside `dev/audit` and `entities.py`), so the class is one seam.
- CI at this head (`ev/check-runs.tsv`, 40 runs): every concluded run passed, was skipped or neutral, except `nightly-status`, and `closures` was still in progress when read.
  - `nightly-status` is red with `NIGHTLY ABSENT: no scheduled run of the workflow was found at all` (`ev/ci-nightly-status.txt`). That check is not a required context and does not block. It grades main's nightly, not this PR's diff.
  - `nightly-ha (stable)` at this head ran the new control: `ok hb:positive_control [… try 1 of 1 (at most 3)]`, `ALL 64 checks PASSED` (`ev/ci-nightly-stable-control.txt`).
  - `mutation` is green, but the diff writes no production line, so that lane evaluated no mutant here.
  - I did not re-run the heavy gate. I cite the scope reported by CI's `closure-scope` run, which is green.
- Architecture score: CI's `arch-score` is green and the body states dS +0.0000. No budget file moved.
- Judgement on soundness, given for the re-review:
  - Merging a change that cannot clear the red does not mask it. The check keeps its power (null controls above), the body discloses the per-process hang in full, and the CI lane still fails on a per-process hang exactly as before.
  - The change is sound to merge once the Block is repaired and the second finding is settled.
- Load disclosure: the PR's mutant harness, F2 and the never-answer run ran alongside the container runs on one host.
