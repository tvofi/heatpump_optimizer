Fix review: merge df3dbd867c142d727d11c8eb9681ff67ea4a6d9e

bus-nonce: 7db88b8564635821883b8344f30ba335
pending-ci: gate

## Scope

Round 1 (first review; no reviewed head), full review at head df3dbd867c142d727d11c8eb9681ff67ea4a6d9e from a detached worktree. The three-dot diff (ev/three-dot.diff) touches tools/ci/ghapi.py, tools/ci/prelude.py and dev/programme/delivery/3944.md only; nothing under custom_components/.

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main df3dbd86` rc 0; origin/main is a59a1b0d9a, the PR's merge base, so the head is level with main (ev/merge-tree.txt).
- RESULT role contract current: `git diff <merge-base>...origin/main -- dev/governance/roles/` empty.
- RESULT self-tests at the head: `ghapi self-test: 36 checks, 0 failed`, `prelude self-test: 168 checks, 0 failed`; both match the body (ev/selftests.txt).
- RESULT structure: `STRUCTURE RATCHET PASSED`; no `*_budgets.json` in the diff.
- RESULT claims: `env_drift.py --claims-only` prints `claims hygiene: origin/main ok`, rc 0; no golden fixture, claim file, VERSION, manifest or RELEASE_NOTES path in the diff (step 4, step 5).
- RESULT closure select vs the merge base: `MODE: FULL`, reason `tools/ci/ghapi.py changes the gate itself`, matching the body.
- RESULT mutation proof (step 1): my own driver (ev/mut.py, the reviewer's instrument, not the finder's) applied each of the body's nine hand mutants alone to the head and ran both self-tests; all nine were KILLED, each failing the check the body names. I added five mutants of my own: `self.calls += 1` deleted, the sleep-start `t0` deleted, `local_s := wall_s`, `attempt := 1`, and `report(...)` short-circuited. All five were KILLED (ev/mutants.txt). One survived: `naps` keeping the query string (`path.split("?")[0]` -> `path`). It is equivalent at this head; see Findings.
- RESULT null controls (step 3): `Meter: an answer at once sleeps nothing (null control)` and `L3 null: a prelude deferring to nothing names no run` both pass at the head. The `meter.api_s` mutant flips the first, and the `outcome := ok` and `defer := []` mutants flip the defer pair, so each control moves under its own perturbation.
- RESULT decision invariance: `main` hands `outputs` a `Meter` whose `__call__(path, params=None, headers=None)` forwards to `ghapi.get(path, params, headers)`, so the client's behaviour is unchanged. The timing line goes to stderr only. ci.yml:161 (`prelude.py ... >> "$GITHUB_OUTPUT"`) and main-cancel.yml:44 (`prelude.py | sed -n 's/^scope=//p'`) read stdout only. The `rate limit fails closed` check still reads `RATE-LIMITED` as stderr's first token, because the timing line prints after it in `finally`.
- RESULT class (step 6): #3885's ask for this part is one seam: "Could prelude report API work and sleeping time separately, including which source runs delayed it?". The body names no enumeration rule, and none is owed for a one-seam class. I am not reading that absence as compliance. Other pollers (gate.py's POLL_S) are outside L3's stated ask.
- RESULT finder's harness (step 2): the packet reports `Finder's harness: none named`. L3 is a measurement feature. Its judge is the self-tests the fixer wrote, which are disclosed as the fixer's. On this PR the live prelude job 141049537192 ran main's pinned programs (`programs restored from a59a1b0d9a`), so no live `PRELUDE-TIMING` line exists at this head. That is by the pinning design, not a defect of the diff; see Findings.
- RESULT figures: `score.py --diff a59a1b0d9a HEAD` re-run at this head prints `Architecture score: dS +0.0000 NULL`, matching the body's figure at 59c100b6 (ev/figures.txt). I could not re-derive `ALL 2794 ENTITY CHECKS PASSED` (quoted at 59c100b6): my local `entities.py` hit its 220 s cap before printing a total, and only `ok` lines were seen. It is cited from CI's full-suite run at this head, not verified by me.
- RESULT owed reds: the set is in ev/owed-reds.txt. `tests / nightly-status` reads failure and is outside the set, so no answer is owed. `gate` is decided by classify (ev/classify-log.txt, final line quoted under CI).
- RESULT step 12: the head was re-read before return (see CI).

## Findings

- Residual: `Meter.slept` strips a query string from a nap's path (`path.split("?")[0]`), and no check pins that. The mutant keeping the full path SURVIVED. It is equivalent at this head: no `get(...)` call in tools/ci/prelude.py, tools/ci/shards.py or tools/pr/codeql_scope.py puts `?` in its path, because params travel separately, and the field decides nothing. Carry: dismissed: equivalent mutant at this head, on a decides-nothing log field with no caller passing a query
- Follow-up: the first real `PRELUDE-TIMING` line exists only after merge, because PR runs restore tools/ci/*.py from the pinned base. #3885's suggested experiment ("instrument one review event, measure waiting occupancy") is read off main's first review-event prelude log, not this PR. Carry: #3885

## CI

- RESULT classify: `merge_train.py classify df3dbd86 --pr 3944` was polled at 60 s intervals from 17:10 to 17:40 UTC. Every run printed `WAIT df3dbd867c142d727d11c8eb9681ff67ea4a6d9e pending: gate red: none` (rc 3; ev/classify-log.txt). No red was read. The review is otherwise complete, so I return the verdict with `pending-ci: gate`; the relay posts it once CI is green at this head.
- RESULT head re-read at 17:40 UTC: `refs/heads/fix/r11-outside-ci-3885-l3-timing` = df3dbd867c142d727d11c8eb9681ff67ea4a6d9e, unchanged.
