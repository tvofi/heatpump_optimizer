Fix review: blocked 1e6e79caa3b2a9f438e055cda1df52dd77eac930 harness: replay-fails-open: r10_train_raise_hold_replay.py, the body's live control, prints "0 raise(s), HOLDS" for #2368 (a real raise) when its gh/git reads fail, contradicting its docstring's "a read that fails prints the train's own Stop"

bus-nonce: 6faf46b93e2e05c4ac5f19f61ff37c1f

Round 1: no earlier `Fix review:` comment or review on #2421. Measured head 1e6e79caa3b2a9f438e055cda1df52dd77eac930 (ev/HEAD). It was still the branch head when this verdict was written (ev/heads_at_verdict.txt). Roles: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, since the merge base is 06c6f3cf2, so the contract is current.

## The blocking finding

`dev/audit/harnesses/r10_train_raise_hold_replay.py` is committed by this PR. The body cites it as the RCA's live re-derivation and as the null control ("The replay's control is a real raise that still stops at the head ... #2368 prints `2 raise(s), STOPS`"). Its `main()` checks the return code of none of these reads: `t.head(pr)` (gh), `git fetch`, `git merge-base` and `git diff`. `t.out` returns the error text as a value. When gh fails, the error text becomes `h`, `files` becomes error words, and `raise_hold` takes its cheap no-budget-file exit. Here, with gh unauthenticated (HTTP 403), the committed command prints for all three PRs (ev/replay_gh403_failopen.txt):

    #2368 head HTTP 403: Gi base fatal: Not a
      path : none (no budget path)
      gate : 0 raise(s), HOLDS: no budget file changed

That is the reverse of the truth for #2368 (ev/offline_replay.txt: 2 raises). It is also the fail-open shape this PR closes in `raise_hold` with its U1 and R1 arms: an unread budget read as a routine one. The docstring states the opposite property. A null control whose failure mode prints the passing answer controls nothing. Fix: refuse, or print a Stop, on any non-zero rc or non-40-hex head/base before reading. That is a few lines.

## Verified at this head (all PASS)

- Self-tests (ev/selftests.txt): merge_train 189/0, queue_pre_flight 36/0, budget_raise_gate 235/0, merge_pr.sh 12/0, proof_watch 34/0, agreement.mjs --self-test 27 of 27. Baselines at 176851e95 (ev/baseline_176851e9.txt): merge_train 180, pre-flight 32, gate 235. These match the body.
- Mutation proof, re-run with the PR's harness (ev/mutants.txt). M0 is clean. P1, J1, W1, H1, U1, R1, T1, B1 and Q1 are each killed by exactly the arms the body names, with the same counts per self-test (P1 2+2, J1 2+2, W1 3+0, H1 4+0, U1 1, R1 1, T1 1, B1 0+1, Q1 0+3). The tree was clean after the run.
- The agreement pair with P1 planted (ev/agreement_P1.txt): `pair budget-raise: 2 readers, 56 items, 20 divergent`, `AGREEMENT REFUSED`, rc=1. Restored: 0 divergent, `AGREEMENT ok`, merge-subject-pr 0 divergent (ev/agreement.txt). This matches the body.
- merge_pr.sh, my own D1 (draft guard → `true`): killed, "a draft refuses without --ready" FAIL, 12 checks with 1 failed (ev/merge_pr_D1.txt). I did not re-run M1, M2, D2 or B1'.
- R5, re-targeted by this PR in r10_tick_train_mutants.sh (the #2390 harness: `return raises, ok,` → `True`): still killed, with many FAIL arms (ev/tick_R5.txt).
- `gate()` behaviour: the diff is a pure extraction into `raises_between(mb, head, ls, show)` with the same loop. The gate self-test stays at 235/235.
- The replay's direction half, re-derived by my own disclosed instrument (ev/offline_replay.py: PR heads fetched over git as refs/pull/N/head, then `raises_between`). #2401 (base 176851e95) and #2373 give path RAISE with 0 raises. #2368 gives path RAISE with 2 raises (`calls_floor: None -> 6`, `floor` override added). I could not re-derive the review/mandate half ("STOPS ... no decisive review"): gh is unauthenticated in this container.
- The class rule (`git grep -n '_budgets.json' -- ...`) returns exactly the sites the body dispositions, plus one docstring at agreement_py.py:128. No undispositioned seam.
- Forward-carry: INSTRUMENTS.md documents `--mandate` and `--ready` (lines 166–168). bugclasses.json I4 `barrier` names the budget-raise pair and the PR-copy train reader, and lists `R10-RCA-TRAIN-RAISE-HOLD` under `rca`. Neither destination is a group merged this round; R10-TICK-DRIVERS/#2390 is not named as a destination. The workflow wiring is dispositioned to the orchestrator because `.github/workflows/` is code-owned.
- `VERSION`, the manifest, the RELEASE_NOTES heading and tests/golden are untouched in the three-dot diff (ev/version.txt). STRUCTURE RATCHET PASSED. `DELIVERY STATUS OK — 0 overdue`.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 against 06c6f3cf2 (ev/merge-tree.txt). It also exits 0 against fa424fd91, to which main moved during the review (#2419, #2426, #2408) (ev/merge-tree-fa424fd9.txt). The orchestrator's merge 3cd92836e has tree 6ac6784a, identical to the automatic merge-tree of 58c671693 and 06c6f3cf2: no resolution delta (the LEDGER-MERGE driver resolved tests/closures.json).
- CI on this head (check-runs API, 45 runs): no run concluded red. When read, `closures` and `Analyze (python)` were still in progress, and the rest were success, skipped or neutral. `pr-contract` was green twice. The body's `## Red checks` answers the previous head's three reds. With nothing red on this head, step 11 owes nothing yet.

## Not verified

- The replay's review/mandate readings for #2401, #2373 and #2368 (needs gh).
- merge_pr.sh mutants M1, M2, D2 and B1' (only D1 was re-run).
- The RCA's demo.out sha1 (out of tree by the body's own account).
- `closures` and `Analyze (python)` conclusions (in progress at read).
