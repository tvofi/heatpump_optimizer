Fix review: merge c99d73f3b39220dc09441b430ea2d85bd48e653e

bus-nonce: 60658fe67249521e7fc283f382670ec5
bus-nonce-note: the dispatch this carry started under, `d452d47f143d63d5746d0454cb2e5fa0`, was minted at `a0c4431df`; `push-verdict` refuses a nonce whose record names a different head than the verdict does, which is the cross-head guard working, so a fresh dispatch was minted at `c99d73f3` naming the same reviewer token (`rev-2336`) before this verdict was pushed.
head-measured: c99d73f3b39220dc09441b430ea2d85bd48e653e (re-read at post time: `refs/pull/2336/head` and `refs/heads/fix/r10-feeds` both this sha)
carried-from: `a0c4431df91e75b3c7ed4976586c0da86e292214` (`review/2336` `aa45c3af5`, round 2). This is `fix-review.md` step 12: my `merge` verdict carried to the head the merge train produced.
round: 3

## What moved, and that it is a carry rather than a re-cut

`c99d73f3` is the merge train's clean automatic merge of my measured head into `origin/main`. Two parents, `a0c4431df91e75b3c7ed4976586c0da86e292214` and `81ae048e8bbdf2335fe2016e987ec2739481f293`, and its tree is **identical** to the tree `git merge-tree --write-tree a0c4431df 81ae048e8` writes:

    merge-tree tree  08f9aa73620f48e6026f388e12227a0d8cf681a5   (rc 0, no conflicting path, no driver verdict line)
    c99d73f3 tree    08f9aa73620f48e6026f388e12227a0d8cf681a5

so there is no hand resolution and nothing authored to judge in the merge itself. `origin/main` is still `81ae048e8`, so the merge base of this head and main is exactly the ref the round-2 review compared against.

The resolution delta is main's own change, ten paths: `early_cutoff.py` (13 insertions, 2 deletions), `tests/features.py` (+33), `tests/closures.json` (+1), one `early_cutoff.py` ledger pin, a new `dev/audit/harnesses/r10_registry_leak.py`, `.claude/hooks/pre-edit.sh`, and four delivery rows. Inside `custom_components/` it reaches **only** `early_cutoff.py` — none of the four production files this pull request authors. And the authored diff over production plus the pull request's own test files is byte-for-byte the one round 1 and 2 measured:

    git diff 81ae048e8...c99d73f3 -- custom_components/ tests/entities.py tests/solar_alignment.py tests/seam_map.json tests/structure_budgets.json | git hash-object --stdin
      57aafb48e9e333bc12bfcb8d12f552bad1b885a8
    git diff 8f174c4ce...a0c4431df -- (the same paths)  | git hash-object --stdin
      57aafb48e9e333bc12bfcb8d12f552bad1b885a8

`tests/features.py`'s only change is main's three early-cutoff checks at `63539`; the R10-FEEDS block at `63944` is untouched. The body's `## Head` still names `a0c4431df`, the pre-merge head, which is the carry rather than a stale figure.

## Re-measured at the new head (nothing regressed; the numbers below are this head's)

Everything the delta could reach was re-taken rather than assumed:

    barrier arms            N-no-expiry allowed 6 keys / 6 sites, found 6/6, verdict {}; modules read 77
                            N-log-flood allowed 63 keys / 74 sites, found 63/74, verdict {}
                            both CHECK ok -- main's early_cutoff change moved its seam line 249 -> 260,
                            and the arms key on (module, function) so the exact counts are unmoved
    PR 16-check block       R10-FEEDS BLOCK: 16 ok, 0 failed
    mutants re-run          M1 -> 13 ok 3 FAIL (covering arm, stale price list, forecast/plan siblings)
                            M4 -> 14 ok 2 FAIL (latch transitions, four-cycle flood)
    finder harnesses        stale_price uncovered 0/0, control_covered_published 2
                            tibber_ingress empty_ok_wipes 0, startless_rows 0, misplaced_steps 0
                            weather_warn no_entity 1, control_48_rows 0
                            probe_n_no_expiry probe_failures 0, CONTROL covered forecast=-2.0 plan=49.5
                            weather_probe empty_ok_wipes 0 | probe_spot_head spot_wrong 0
                            log_flood/probe control.floods 0 and all seven arms 0
    enumerators             sweep_n_no_expiry seams 6 / unbounded 4 | sweep-N-silent-zero unguarded 1
                            p1_ts_seams seams_flagged 3 | log_flood sites=80 latched=6 seams=74
    instruments             STRUCTURE RATCHET PASSED
                            Architecture score dS +0.0158 IMPROVES, coord_footprint 2575 -> 2547
    ledger / claims         completeness(head ledger) 0 | completeness(base ledger 81ae048e8) 7
                            claims hygiene: 81ae048e8... ok
                            git merge-tree --write-tree origin/main c99d73f3 -> rc 0, no conflicting path

**CI is green at this head, and it is cited rather than re-run**: 45 check-runs, **zero failures** — `mutation`, `pr-contract` (twice, the later `18:41:32Z`), `closures`, `arch-score`, `typing`, `env-matrix`, `delivery-status`, `nightly-status`, `budget-raise-gate`, `instrument-self-tests`, `policy-docs`, `briefs`, `closure-scope`, `wave-script`, `fast (3.14)`, `CodeQL` and the three `Analyze` jobs all `success`; the rest `skipped`. That is the gate's own run of `tests/entities.py`, `tests/features.py`, `env_drift.py --all` and `structure.py` at `c99d73f3`. Its `pr-contract` prints `PR-BODY: 0 error(s)` and `record red-history 12 commit(s) between origin/main and this head, every failure conclusion across them: mutation` — the range's red is checked, not skipped, and the body answers it (round 1 verified that answer).

## Two numbers main moved, neither the body's error

- `tests/mutation_table.py`'s `inventory()` at this head reads **6134** candidate sites where the body and the round-1 review both read 6133 at `a0c4431df`. The extra site is main's `if held.wiring is None:` in `early_cutoff.py` — a new GUARD_OFF candidate, pinned by main's own ledger row. The claim the figure supports is unmoved: `unpinned_sites(load_budgets(), inventory())` is still **4368**, `completeness_problems(load_budgets(), inventory())` is still **0**, and the base-side counterfactual is still exactly **7**. (This also means the one-site disagreement I reported in round 1 against the lane's printed total has the same explanation.)
- `early_cutoff._planned_room`'s seam moved from `early_cutoff.py:249` to `:260`. The N-no-expiry allow-list is keyed by (module, function) with an exact count, so the barrier is unmoved — which the arm's own run above confirms.

## Not in this pull request's diff, noted once (not a block)

`pr-contract`'s advisory pre-flight step calls `preflight.sh` with no intended-issue list, so it prints `REFUSE 'Closes #2229/#2233/#2226 ... not in the intended list'` for every closing keyword. The step ends `|| true`, the job is green, and neither `governance.yml` nor `preflight.sh` is in this pull request's diff — it is main's, and the body's three `Closes #N` are one per line, the shape that closes all three.

## Standing from rounds 1-2 (unchanged, and re-stated so this verdict carries them)

The `harness` block of round 1 remains cleared: the new body discloses `sweep_n_no_expiry.py --perturb`'s dead anchor, and I re-derived its class rule (22 multi-line-literal anchors, 19 alive at the head, 2 dead at both ends, exactly 1 dead-at-head-alive-at-base — that one). The mutation proof, the five class enumerators, the two barriers with their discriminating planted controls, the ledger counterfactual, `VERSION`/manifest/notes untouched, and the forward-carry into `R10-BRIEFS-FOLD` all stand as verified in rounds 1-2; the head they were taken at is an ancestor of this one and the authored diff is byte-identical.
