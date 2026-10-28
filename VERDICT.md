Fix review: blocked 3fd42d9539ee90e5bf409593ff681f748db76f6e unpinned-site: the job's --window-cache wiring and two cache guards survive every check and the body dispositions none of them

bus-nonce: 5c5034eb7c7f033d16bcd621330debde

Round 1. Head 3fd42d9539ee90e5bf409593ff681f748db76f6e was measured, and it was still the branch head when this verdict was written. Worktree detached at the head. `dev/governance/roles/` has no diff between the merge base and origin/main, so the contract I followed is current.

## Block

- **The M1 wiring in the workflow is pinned by nothing, and `## Unpinned sites` does not list it** (fixer.md step 2). I dropped every `--window-cache "$RUNNER_TEMP/window.json"` from governance.yml's `record` job (mutant `M1-yaml`, ev/mutants2.txt). The policy_lint acceptance still printed `FIXTURE ok ... 251 pins` at rc=0, `tests/entities.py` passed at rc=0, and `check-wave-script.mjs` printed `202 passed`. The same happened when I dropped only the `.claude` arm of `--sunset` (mutant `Y1`, ev/mutants.txt: acceptance rc=0). The head's `record_api_calls.sh` does see both: 834 and 740. But no CI lane runs that harness, so main can lose the 834→370 saving silently. The acceptance's "wiring" arm runs `policy_lint.mjs` by hand with the flag. It never reads the job text. The body's `## Unpinned sites` covers only M0's `rate_limit` steps and M2's `concurrency:` block.
- **Two guards the body names as properties survive the acceptance and the harness, and neither is dispositioned:**
  - `pullsByShaShared`'s `if (fetched.ok)` write guard ("a failed enumeration writes nothing"). Mutant `R1b` deletes the guard and mutant `R1` caches a failed enumeration as an empty map. Under both, the acceptance stays at rc=0 with 251 pins and the harness at 370. Every acceptance arm feeds `okPulls`, and no arm feeds a failing commit-to-PR fetch. Under R1, a 403 in `--record`'s enumeration, which is the saturation case this PR exists for, reaches `--stats` and `--sunset` as an `api`-mode window with zero pull requests. Neither prints `enumSkipLine`, and `--sunset` judges rules against an empty friction map instead of `no friction data`. That is the silent-zero class #1050 closed. Under R1b, `--record` throws on `[...undefined]` instead. The per-PR half of the same claim is pinned: the `badReads` arm kills R3.
  - `readWindowCache`'s key check `cache.key === windowKey(since)` ("a file left from another window or another head is ignored rather than trusted"). Mutant `R2` makes it `cache || {}`. The acceptance stays at rc=0 and the harness at 370. No arm seeds a file with a foreign key.
- **pr-contract is red at this head, and the red is not this PR's nightly-status answer.** I read the latest run, job 120135698603, which started 22:54:12Z after the last workflow concluded at 22:53:55Z. It refuses in `carry_audit.py check --body` with `CARRY-AUDIT: 4 finding item(s): 0 routed, 4 unrouted`. The 4 unrouted items are the two `## Forward-carry` bullets and the two `## Friction` bullets. Their `Carry:` values (`` `dev/programme/rosters/...` ``, `` `dev/programme/HANDOVER.md` ``, `none`) are not destinations of the form `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`. The body's `## Red checks` answers pr-contract only for the earlier missing-row cause. A body edit fixes this without moving the head.

What clears the block:
- One acceptance arm with a failing `pulls` stand-in, followed by a re-read that must fetch again.
- One arm with a foreign-key file, which must not serve.
- Either a pin that reads the `record` job's three invocations for `--window-cache`, for example in `tests/entities.py` or the acceptance, or a written triage of that site in `## Unpinned sites`.
- Routed `Carry:` markers in the body.

## Findings

- M0 survives every check: I deleted both `GITHUB_TOKEN rate limit` steps, and the acceptance, entities.py and check-wave-script all stayed green (ev/mutants2.txt). The dispatch asks for each of M0, M1 and M2 to be caught by a check. The body dispositions M0 by a written triage, a form fixer.md step 2 allows: it is a log line, never a gate. Whether that triage satisfies O-1's need to read the limit is the orchestrator's call. Carry: R10-RECORD-API-BUDGET
- M2 survives every check: I deleted the `concurrency:` block, and the acceptance, entities.py and check-wave-script all stayed green (ev/mutants2.txt). The body's written triage says a pin would fix a spelling and not GitHub's queueing, and the replay measures the effect offline. Same dispatch bar as M0, same disposition. Carry: R10-RECORD-API-BUDGET
- The finder's harness at the base (`record_api_calls.sh` as of fd9914851) passes no flags to the modes, so it reads 834 at both ends and cannot see M1. The fixer extended it to read the job's flags. I disclose my own instrument here: `ev/finder_harness_cache.sh` is the base harness plus `--window-cache` on all three modes. It reads 370 at the head and 0 on the empty window. `record_burst_replay.py` is the fixer's own new instrument, not the finder's. Carry: dismissed: disclosed instrument provenance, no defect

## Evidence

- RESULT harness-base-at-base (finder's harness, origin/main pinned to 04c1dd779, `v7.0.2`): `--record 94`, `--stats 370`, `--sunset 370`, TOTAL 834, rc=0 (ev/harness.txt).
- RESULT harness-head-at-head (head harness): 94 + 276 + 0, TOTAL 370, rc=0. The base harness at the head also reads 834, because it passes no flags. My cache variant at the head reads 94 + 276 + 0 = 370, and 0 on `origin/main..origin/main` (ev/harness_cache.txt).
- W + 3P versus 3W + 6P, measured: W = 94 and P = 92. 94 + 3×92 = 370, and 3×94 + 6×92 = 834. Both match the body.
- The PR's named mutants under the acceptance (`node tools/policy/policy_lint.mjs`) and the head harness (ev/mutants.txt). Each one reproduced the body's figure and was killed at rc=1:

  | mutant | harness TOTAL |
  |---|---|
  | M-A (per-mode fetch restored) | 834 |
  | M-B | 370 |
  | M-C | 464 |
  | M-D | 646 |
  | M-E | 558 |

  My R3 (a failed per-PR fetch written as empty reads) and R4 (`--record` not given the cache, harness 464) were also killed.
- RESULT replay (`record_burst_replay.py v7.0.2`, at the head, ev/replay.txt). Every row matches the body:

  | hour | before | M1 | M1+M2, 30 to 120 s | M1+M2, 240 s |
  |---|---|---|---|---|
  | 08Z | 6 runs, 4599 calls | 2040 calls | 4 runs, 1364 to 1368 calls | 3 runs, 1026 calls |
  | 06Z | 4305 calls | 1911 calls | 4 runs, 1277 to 1281 calls | 3 runs, 960 calls |
  | 09Z | 5 runs, 1810 calls in every M1 row | | | |

  The 09Z hour is the null control.
- Concurrency (item 3): the `record` job sets `concurrency: {group: governance-record, cancel-in-progress: false}` (parsed with PyYAML). With `cancel-in-progress: false`, GitHub never cancels a running job. It only replaces a pending one, before any step runs, so a run cannot be cut off mid-write by the group. No other workflow uses the group name. The `timeout-minutes: 10` is unchanged. `record` is in merge_train.py's `NOT_GATING`, so a superseded pending run that shows `cancelled` on a main commit gates nothing. No step between the modes fetches, so the cache key (`since..origin/main` SHAs) is stable within a job, and `$RUNNER_TEMP` is per job.
- Acceptance at the head: `FIXTURE ok: 92 error(s) hold 251 pins`, rc=0 (ev/accept_head.txt). `tests/entities.py` at the head under Python 3.13 printed `ALL 2397 ENTITY CHECKS PASSED` (ev/entities_head.txt).
- Merge: `git merge-tree --write-tree origin/main(fef4a1351) 3fd42d953` exits 0. Stderr shows `LEDGER-MERGE: resolved tests/closures.json` and no MERGE-CLAIM refusal (ev/merge-tree.txt).
- VERSION, the manifest version, RELEASE_NOTES and both claim files are untouched three-dot, and pr-contract's version step confirms it.
- CI at the head: all 41 runs have concluded (ev/ci.txt). Every gate except pr-contract is green. nightly-status is red. That red is main's false ABSENT, answered in the body as R10-NIGHTLY-ABSENT / #2627. The diff does not touch `tests/nightly_status.py` or nightly.yml, so the red is not treated as this PR's.
- Figures I did not re-derive: the gate-scope, policy-lane and agreement-lane lines in the body's `## Figures`, which CI's heavy runs at this head cover. The ≈3,000 calls of run 39745228063.
