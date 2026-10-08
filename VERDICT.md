Fix review: blocked 245468e28908863ee1a12df6176a2b1943e9a705 carry-missing: not carried to R9-RO-9 (its roster carry holds /private/tmp file paths, not the follow-up text)

bus-nonce: 343a62f6ed49a69cfa6632e643e2bf8d

PR #2049 (R9-CI-1), round 2. Measured head 245468e28908863ee1a12df6176a2b1943e9a705, which merges fixer commit cf0bba2b into 04b8b4bd. It was still the live head at 04:59Z. Merge base e2a4f7c6 = origin/main; dev/governance/roles/ is unchanged. I worked from a fresh detached worktree, /Users/timmalmstrom/hpo-seats/review-2049/wt2.
Evidence: /Users/timmalmstrom/hpo-seats/review-2049/ev2

## The one block, and its repair (orchestrator-side, a minute's work)

The body's Forward-carry names its destination: "the R9-RO-9 roster entry on the `handoff/audit-r9-fixplan` branch (commit `4d7aa048`, corrected in `c716b8f8`)". I opened `.claude/workflows/wave-r9-groups.json` at that branch's tip, c716b8f8, `groups[100].carry`. The two R9-CI-1 entries there are the literal strings `/private/tmp/claude-501/.../scratchpad/orch/cCI1.txt` and `.../cCI1b.txt`. The follow-up text itself (the ~2000 s per site pin cost; boost_drift_replay.py timing out as a driver; the stamp.py --self-test cleanup race and the misattribution in the null-control message) exists only in those scratch files. A later seat reading the roster gets a path into another session's /tmp, and the text disappears when that directory is cleaned up. Content and file paths: carry-destination.txt.

The cause: `roster_edit.py append-carry` reads a file only when the argument starts with `@` (`_text()`, line 190). These were passed without the `@`. Five earlier entries on the same group have the same defect (c2014, c2027, c2029, c2030, c2044). Repair: re-append each carry with `@<file>` (or the text inline) and drop the path entries. Nothing in this PR's diff has to change, so a round 3 needs only that ref re-checked.

## Everything else asked for in round 2 holds

- **M7 is now killed.** The new entities check "a failed recording of a driven child refuses its driver's repair; the same pair recorded cleanly repairs" fails under M7 with `failed child=('changed', False)`. Its null control (the same pair, child recorded cleanly) gives `changed` at the head and under the mutant, so the check discriminates on the failed child alone.
- **tests/closures.json adds only the entry described.** A semantic diff 04b8b4bd to head shows `inert_reads["tests/harness_headers.py"]` gains `dev/audit/harnesses/r9_ro12_batch_mutants.sh` and nothing else; nothing is removed and there are no duplicates. `recorded["tests/harness_headers.py"].seconds` goes from 228.4 to 167.0. The other textual moves are reorderings within the same list (boost_replay_fork_parity.py, ci_script_seconds.py, eg_b7_seam_hubs.py). No `closures` entry changed. The gap is main's: d95e0383 (#2044) added the harness, main's tests/closures.json has 0 mentions of it, and main's own `closures` at e2a4f7c6 is red (check-run 113092114325).
- **Red checks are answered.** At round 1 they were `closures`, `closures-autofix`, `delivery-status` and `pr-contract`. Each is named with a check-run id and a cause, and the cheaper-detector question is answered. `pr-contract` is green at this head (113149098933, 113149187257).
- **Body corrections are in.** #2048 is cited as run 37711053129. Shard 2's refusal is attributed to stamp.py's --self-test (OSError ENOTEMPTY), with the a3:roster misattribution explained. #2047 is cited as run 37710478042.
- **ci-autofix.md** names INERT READS in its description and its table, and the third green-unrepaired bullet now covers `changed`. policy_lint reports `TOTAL: 0 error(s) across 40 policy file(s)`; RULES-SYNC is ok. The coordinator states the file is at its cap of 1469/1469; I did not re-measure that, but the lint passing means the cap holds.
- **autofix_statuses.sh** is now paced: `api()` sleeps 1 s before every call, each run's job list is cached under jobs/ and read with jq, and a non-numeric pages argument is refused. `bash -n` is clean. It now needs a `jq` binary; noted, not blocking.

## RESULT lines (ev2/mutants/run.sh, tests/entities.py, PYTHONPATH=tests/hastub, venv-ci)

- RESULT M0 baseline head: ALL 2210 ENTITY CHECKS PASSED (rc 0)
- RESULT M1 pin_shard overlap: KILLED
- RESULT M2 merge_pin_shards one head on mixed heads: SURVIVED (unreachable within one run, as in round 1; observation)
- RESULT M3 merged status = last shard's: KILLED
- RESULT M4 pin_shard_count floor: KILLED
- RESULT M5 survivor remedy whenever left: KILLED
- RESULT M6 stale_scripts ignores INERT READS: KILLED
- RESULT M7 driven-child mapping emptied: KILLED (new check; round-1 block cleared)
- RESULT M8 tail-deadline check off: KILLED

Local at the head: STRUCTURE RATCHET PASSED; `closure.py selftest` ALL 39 closure shrink pins PASSED.

## CI at the head (check-runs API, three reads at ≥5-minute spacing, last at 04:59Z)

- **Green:** 20 checks, including `closures` (113149079722, success at 04:58Z, so the inert_reads repair holds on CI's Linux recording), `mutation`, `pr-contract`, policy-docs, instrument-self-tests, briefs, typing, closure-scope, hassfest and validate-hacs.
- **Red:** `delivery-status` (113149021242). It is main's, answered in the body, and I reproduced the cause in round 1.
- **Other:** one budget-raise-gate twin cancelled.
- **Still in progress:** `fast (3.14)` and `coverage`.
- **Skipped:** `mutation-pin-plan`, `mutation-pins`, `mutation-autofix` and `closures-autofix`, because `mutation` and `closures` passed. The sharded path is still evidenced only by the proof runs.
