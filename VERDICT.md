Fix review: merge 5a3c5d2395043b7ce9f82b383be350356c9d5864

bus-nonce: 8cb0599cdfd5ab2d2f2c84e292448039

This is round 2, the first re-review, of PR #2605, group R10-NIGHTLY-PYSPY-RETRY. I measured head `5a3c5d2395043b7ce9f82b383be350356c9d5864`, whose code head is `7bd9c8f3e`. Round 1 was `blocked mutation-vacuous` at `7651b942`.

I re-read the remote `refs/heads/fix/r10-nightly-pyspy-retry` just before writing, and it is still this SHA. The role contract is current: the diff of the merge base against origin/main is empty under `dev/governance/roles/`, both at `6c8903a44` and at the new main `543c8087c`.

## Findings

- **`pr-contract` stays red until the branch carries main's roster.** Roster PR #2608 merged at 11:33:58Z as `543c8087c`. Against that main, `carry_audit.py check` over the body prints `3 routed, 0 unrouted, 0 bad destination(s)`. But all three `pr-contract` runs at this head, including the one at 11:36:01Z after #2608 merged, read the roster from this head's tree. Each fails `BAD-DEST … R10-NIGHTLY-HB-RESPAWN is not a group of the roster` (`ev/ci-red.txt`). The fix is a base merge of origin/main into the branch. That merge is clean: `merge-tree` exits 0 with tree `7e5048d0…`. It is the orchestrator's resolution delta under the carry predicate, after which `pr-contract` runs again. Carry: R10-NIGHTLY-PYSPY-RETRY
- **The body's `## Red checks` section is stale.** It says "`none` at this head … no CI has run on it". In fact three `pr-contract` runs and `nightly-status` are red at this head.
  - The `pr-contract` red is answered in substance under F13. It names the BAD-DEST, its cause (the group exists only on the roster branch), the cheaper detector (local `carry_audit.py`, run before the push, about 0.1 s), and that the merge must follow the roster. So I do not return `root-cause-unanswered`.
  - The section should name the check. The orchestrator can correct that line in the body when it merges main.
  - Carry: R10-NIGHTLY-PYSPY-RETRY
- **Hand mutant H1 survives: `HB_CONTROL_REST_S = 1.0` → `0.0` passes every check.** The full `tests/entities.py` prints `ALL 2397 ENTITY CHECKS PASSED`, rc=0 (`ev/full/res-H1-rest-const-0.txt`). The rest pin drives `_async_hb_control(rest=1.0)` explicitly, so it pins the code path and not the lane's value. With a 0 rest, the production lane has no rest between tries. The body says "only that a rest happens is pinned". That is true of the code path, not of the lane. The body also states the length is free because F7 measured that no rest length rescues a hang, and that reason covers 0 too. No measured cost follows from a zero rest. Carry: dismissed: the body's stated reason (F7, no rest length rescues a real-HA hang) covers 0 s, and a zero rest moves no bound upward
- **The X1 pin's power under load is not unconditional.** The body says host load "can only lengthen a run … never pass a mutant that skips the rest". The second half does not follow: load lengthens a no-rest run too, and a run lengthened to ≥ 2.2 s would let X1 pass. I measured the margin: under 4 concurrent full suites plus my null driver, X1's two tries still took 1.61 s against the 2.2 s floor (`ev/full/res-X1-no-rest.txt`). So a 0.59 s margin held at this host's heaviest load in this session. Carry: dismissed: the margin was measured to hold at 4-way load, and a false survival would show in the mutant table, not as a false red on the head
- **The body's `## Head` section has a stale paragraph.** It names `e0725a9ede5b…`, which is not an ancestor of the head. That commit has the same tree as the head (`eccb9aed…`, `ev/head-chain.txt`), so nothing it describes differs from what I measured. Carry: dismissed: same tree as the reviewed head; the body also names the reviewed head correctly

## Evidence

- Head: `ev/HEAD.txt` = `5a3c5d2395043b7ce9f82b383be350356c9d5864`. Head chain (`ev/head-chain.txt`):
  - `a3d3c1c50` merges code head `7bd9c8f3e` into round 1's `7651b942`, and adds only the `dev/programme/delivery/2605.md` row.
  - `5a3c5d239` then merges origin/main `6c8903a44`.
- Round-1 Block, settled. X5 (the `LoopHeartbeat` default `spy_timeout=30.0`) and X2 (`PY_SPY_TIMEOUT_S = 25.0`) each go red in the **full** `tests/entities.py`, `1 of 2397 ENTITY CHECKS FAILED`, rc=1. The failing check is the one the body names, "the real lane cuts py-spy at PY_SPY_TIMEOUT_S, and the whole control, every try hung, is bounded under 22 s":
  - X5 fails it with `[default spy_timeout=30.0; whole control 21.75s]`;
  - X2 fails it with `[default spy_timeout=25.0; whole control 81.75s]`.
  - Source: `ev/full/res-X2-timeout-25.txt` and `ev/full/res-X5-default-30.txt`.
- Round-1 finding X1/X3, settled. X1 (`await asyncio.sleep(rest)` → `pass`) fails only "the control rests between tries…" with `[two tries took 1.61s against a 1.0s rest]`. X3 (`HB_CONTROL_TRIES = 2`) fails only "the control survives two hung samples…" with `pass=False calls=2`. Both are full-suite runs, rc=1.
- In those runs, the indented `FAIL a3:…`, `hb:changed_save` and `hb:positive_control` lines are the suite's own negative-control output. The same lines print on the unmutated head (`ev/entities-head.txt`).
- The PR's mutant harness at this head: `SUMMARY killed=14 survived=0 null=ok`, rc=0, `M0-null all checks pass` (`ev/mutants-head.txt`). This matches the body's table.
- My own hand mutants, outside the PR's list, each run against the full `tests/entities.py` in its own worktree at this head (`ev/reviewer_mutants_driver.py`, `ev/mutants-summary.txt`):
  - H2: `_async_hb_control` default `tries: int = 1`. KILLED, 5 checks.
  - H3: `if all(hb_control_reading(...))` → `any`. KILLED, 5 checks.
  - H4: the boot calls `_async_hb_control(checks, tries=1)`. KILLED by "the real heartbeat boot runs the retried control".
  - H1: rest constant 0.0. SURVIVED, see Findings.
- The whole-control bound matches the body: 3 × (0.25 + 5 + 1 + 1) = 21.75 s < 22, as printed by X5's detail at the real constants.
  - The tighter figure 3 × 6.25 + 2 × 1 = 20.75 s is re-derived.
  - Under the pin, PY_SPY_TIMEOUT_S ≤ 5.08 s: 3 × (t + 2.25) < 22 gives t < 5.083.
  - 4 tries would be 4 × 7.25 = 29 s, which the pin refuses.
- Comment (F7), settled. `tests/nightly_ha.py:289-295` at this head reads "On real HA this was measured NOT to rescue a hang … across retries inside one held spin and across fresh spins 1 s apart (R10-NIGHTLY-PYSPY-RETRY, F6 and F7)". It names R10-NIGHTLY-HB-RESPAWN for the respawn, and says what the retry is kept for.
- The whole-control comment now states 21.75 s and names the pin.
- F11 re-derived: `AST IDENTICAL` for blob `91164340…` against `de2bcb89…`. Round 2 changed only comments in `nightly_ha.py`, so the container figures F5 to F9 carry over (`ev/blobs-ast-version.txt`).
- Power is kept. My own driver runs the real `_async_hb_control` at its production defaults, passing no `spy_timeout` and no `rest`, against stub py-spys (`ev/null_ctrl_driver.py`, `ev/null-control-head.txt`):
  - never answers: `pass=False calls=3 elapsed=17.9s`, with the 5 s cut visible as a 5320 ms gap;
  - answers rc=0 without naming the spin: `pass=False calls=3`;
  - names it only at rc=1: `pass=False calls=3`;
  - hang, hang, spin: `pass=True calls=3`.
  - The committed null-control check is also green at the head and red under H2 and H3.
- Full suite at this head: `ALL 2397 ENTITY CHECKS PASSED`, rc=0 (`ev/entities-head.txt`). That is 2394 + 3 added checks, as the body says.
- Merge: `git merge-tree --write-tree` exits 0 against origin/main `6c8903a44` (tree `eccb9aed…`, equal to the head's tree) and against the newer main `543c8087c` (tree `7e5048d0…`). No conflicting paths, and no claim driver invoked (`ev/merge-tree.txt`). The 15 commits main gained touch only `dev/programme/rosters/wave-r10-groups.json` among this PR's surroundings.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/` are untouched three-dot. CI's `pr-contract` prints "no version edit". No claim file moved.
- Carry (`ev/carry-audit-body.txt`, `ev/roster-2608.txt`):
  - `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body` (`aa38bdd5f`) prints `3 routed, 0 unrouted, 0 bad destination(s)`.
  - The same holds against #2608's head `63ca4f33`, which contains `aa38bdd5f`, and against main `543c8087c` now that #2608 has merged.
  - Against the old main it prints `2 routed, 0 unrouted, 1 bad destination(s)`, as F13 states.
  - R10-NIGHTLY-HB-RESPAWN is on main's roster as queued and `after` R10-NIGHTLY-PYSPY-RETRY. Its brief states the control as a precondition: "a stub that never answers, or answers without naming the spin, still fails hb:positive_control after the respawn".
  - The Forward-carry line names the roster path and #2608.
- CI on this head (`ev/check-runs.tsv`, 42 runs, read 11:48Z): 39 success or skipped, and every workflow has concluded. These are green: `arch-score`, `closures`, `closure-scope`, `mutation`, `nightly-ha (stable)`, `nightly-ha (2025.2.0)` and `budget-raise-gate`.
  - The three `pr-contract` reds are the BAD-DEST in the first finding.
  - `nightly-status` is red, `NIGHTLY ABSENT: no scheduled run of the workflow was found at all`. Per its own log it is not a required context and does not block. It grades main's schedule, not this diff (`ev/ci-red.txt`).
  - I did not re-run the heavy gate or the mutation table. I cite CI.
- Figures re-derived here:
  - 14/0 mutants, 2397 checks, 21.75 s, 20.75 s, 5.08 s, 29 s;
  - blob identities and the AST;
  - F13's two carry lines;
  - F2's and F10's arithmetic (round 1);
  - X1's margin: 1.61 s here against the body's 1.603 s.
- Figures I could not re-derive: the body's unmutated `late=2.604` s (F12). The suite prints no detail on an `ok` line, so I verified the floor only by the head passing it.
- Figures not re-taken this round: F5 to F9, container runs at round 1's blob, which has an AST identical to this head's. Round 1 reproduced F5 at both ends, and the real-py-spy counts F6, F7, F8 and F9 are the fixer's.
- Load disclosure: the eight full-suite mutant runs ran four at a time on a 4-core host. My null driver ran alongside the first four.
- Environment: this seat's `python3` resolved to `/usr/local/bin/python3` without numpy. I prefixed `/opt/hpo/venv-ci/bin`, as the fixer reported.
