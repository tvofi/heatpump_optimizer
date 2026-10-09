Idle steps publish an exact sub-code when the solved plan shows why, and the Advisor hot-water row writes that recommended setpoint through `apply_schedule`, which stores it and the comfort target in the entry options. The card says Because for a published sub-code and keeps Likely because when the step is only idle. The what-if prices an active away setback. The payload's minimum temperature is the floor that solve used, and the configured floor is named beside it while they differ. The comfort-at-risk event carries the coldest step's published reason.

Part of #201. Leaves #201 open.

Closes #1795

_Requested by **tvofi**_.

## Head

`941d42ff04a791e7cbdc1d6d5904c7b3203c0d8f` merges `origin/main` into the reviewed head. The reviewed code is unchanged; the only conflict was `tests/golden/claimed_drift.txt`, whose merge driver REFUSED because both sides rewrote the bare claim list — that refusal is the orchestrator's to settle by hand (claim-files.md), and it was settled as the union of the two claim sets with no key in common, correcting main's clause that claimed a single set. `tests/env_drift.py --claims-only origin/main` prints `claims hygiene: origin/main ok` at this head; CI's `env_drift --all` is the drift authority. The head the figures below were taken at is `87849cd27`.

`87849cd277485bd28bc85d64bc104293c5c7e6de` merges main `b2b6acd64` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`cdb7c38b46cc734253a313c2923281a24813ebf3` merges origin/main `f84d891e1` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head. The only conflict was `tests/closures.json`, resolved with `python3 tools/merge/ledger_merge.py --resolve tests/closures.json`; no other file needed a resolution (git merged the rest automatically).

`d67d8a44ec6e6a2c93e2cedf126ba10ea00b2470` merges `f6d28bb76` into this PR's previous head 6eafd3a5. f6d28bb7 is itself the merge of origin/main `af79f2114` (v6.7.17) into 6eafd3a5, with the claim resolution described below, so the head's tree equals f6d28bb7's. The script's own merge of origin/main afterwards found nothing new.

The head is stated by the line above this paragraph, written by `tools/audit/seat/update_pr.sh`; no other line of this body names it. This body is re-cut (fourth round) and replaces the previous one whole.

The code head b0f90860 is two commits on 217f7cef (the bot's `ci: re-record closures` on 05927892):

- 57cac088 changes `idle_codes` in `custom_components/heatpump_optimizer/optimizer.py` and adds two checks to `tests/features.py`. The solar test drops the `(idx < len(surplus))` conjunct, and the sunny steps are read from the whole `surplus` instead of `surplus[:min(len(pw), len(surplus))]`. Both terms decided nothing: `nxt_sun < nxt_run` holds only for a sunny step before the channel's next run, and the next run is never past `len(pw)`. The commit deletes the `killed_by` row of the sunny line's old text (`idle_codes.CMP_BOUND.a87d46e1`), because the text it pinned is gone. The new text's site is re-pinned by CI.
- b0f90860 adds one `survivor_triage` row, `optimizer.py/idle_codes.CMP_BOUND.a02b3552.json`, for the `if n <= 0:` bound.
- 05bbf393, on a249933a, adds the four `killed_by` rows CI measured at a249933a (see `mutation-autofix` under `## Red checks`).
- 75a6aee4, on 9a8255b3, moves the probe into the tree as `dev/audit/harnesses/ux5_idle_codes_sites.py` (fixer.md step 18). It also lists the file in `inert_reads["tests/harness_headers.py"]` and points the triage row at the tree path. `mutation_table.py --normalize` left every other row unchanged.

The previous head ac2fd413 merged b0f90860 and origin/main 9cac1947 (#2055: `tests/closures.json` and `dev/programme/delivery/2055.md`, `git diff --stat 816547ef 9cac1947`). GitHub then read the pull request as DIRTY, because main's #2053 also changed `tests/closures.json`, and no `pull_request` run started at ac2fd413. a249933a then merged main past #2053, which made it mergeable. #2053 changes `.github/workflows/budget-raise-gate.yml`, `tools/policy/budget_raise_gate.py`, `tools/audit/seat/run_twins.py`, `tools/audit/seat/INSTRUMENTS.md`, `tests/entities.py`, `tests/closures.json` and its delivery row (`git diff --stat 9cac1947 dcc77dd0`). The ledger driver resolved `tests/closures.json` (seconds take the larger, `inert_reads` merged as a set). 9a8255b3 then merged #2056: `tests/nightly_ha.py`, `tests/debug_collect.py`, its delivery row and 27 `tests/mutation_ledger/killed_by/` rows, none of them for `idle_codes` (`git diff --name-only dcc77dd0 4647321d`). This is the nightly-ha fix that answers the `nightly-ha` reds below. None of these files touches this pull request's lines.

**Claim resolution after the v6.7.17 stamp (f6d28bb7).** f6d28bb7 merges origin/main af79f211, which is v6.7.17 and includes #2060. The stamp emptied both claim files and set `claims-for: 6.7.17`, so the merge conflicted in `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt`. Each file is resolved as main's v6.7.17 text with this branch's own R9-UX-5 lines appended unchanged:

- `claimed_drift.txt` gets the 31 scenario claims and their note.
- `card_claimed_drift.txt` gets the `shared_steps_hover` and `tooltip_hover` claims and their note.

`git diff af79f211 f6d28bb7 -- tests/golden/` has no removed line. `tests/env_drift.py --claims-only origin/main` printed `claims hygiene: origin/main ok`. Its null control, the same tree with `claims-for: 6.7.16`, is under `## Figures`.

## Mutation proof

These are the six sites `mutation` counted as added and unpinned at b78e5810, and what happened to each. The probe is `dev/audit/harnesses/ux5_idle_codes_sites.py`. It takes a `git archive` of 57cac088, replaces one line per variant, imports that tree fresh and drives the real `idle_codes` on the inputs of the named `tests/features.py` checks. `tests/features.py` itself is CI's.

    B RESTORED {'dust on this step still leaves a later surplus as a wait': True, 'dust ahead is not surplus to wait for': True, 'surplus that arrives with the next run is not a wait': True, 'a negative step count has no idle codes': True}
    B MUTANT 1053 GUARD_OFF: failing checks = ['a negative step count has no idle codes']
    B MUTANT 1075 CMP_BOUND: failing checks = ['dust ahead is not surplus to wait for']
    B MUTANT 1078 CMP_BOUND sp: failing checks = ['dust on this step still leaves a later surplus as a wait']
    B MUTANT 1078 CMP_BOUND next-run: failing checks = ['surplus that arrives with the next run is not a wait']

The check names are the `UX-5 ...` checks of `tests/features.py`. "surplus that arrives with the next run is not a wait" and "a negative step count has no idle codes" are new in 57cac088. Each was written for the mutant it kills.

Two sites are gone, because both were equivalent:

- `1075 CLAMP_DROP` (`k = min(len(pw), len(surplus))`). Slicing clips, so `surplus[:len(pw)]` equals `surplus[:k]`.
- The `idx < len(surplus)` bound on the solar line. For `idx >= len(surplus)` the next sunny step is the sentinel `iinfo(int64).max`, which is never below `nxt_run <= len(pw)`.

The second shared its line's ledger anchor with two killable bounds. `pin_results` pins an anchor only when every site under it is killed, so that line could never pin. A triage on the anchor would have called its two killable twins equivalent too. With the redundant terms removed, the line has two bounds, and both are killed above. The other choice was a triage of the clamp. It lost under fixer.md step 17, because removing the term is the simpler code.

`1053 CMP_BOUND` (`n <= 0` to `n < 0`) is equivalent and is triaged. Probe section C is its measurement (see `## Null control`). No form of that guard avoids an equivalent bound at n == 0, and the guard keeps a negative count from raising in `np.full`.

The PR's original fix, measured at c75b7770 with mutation and restore:

- Deleting `codes[_padded(caps, n) <= threshold] = REASON_IDLE_FUSE` turned "UX-5 an idle step whose fuse cap leaves no room says the fuse" red (`got=idle want=idle_fuse`).
- Deleting `_fold_away`'s `if floor == float(configured): return view` turned "UX-5 a setback equal to the floor does not name a second one" red (`second_floor=True`).

Both were green restored.

## Null control

Simplification, probe section A. Over 4000 seeded cases (channel lengths n-2..n+3, values 0, 0.05, 1e-6, NaN, +-inf and random, each array absent with p=0.15), 217f7cef against 57cac088 through `idle_codes`, `classify_dhw_steps` and `classify_space_steps` gave `prev-vs-head differing=0`. Its control, the head with `nxt_sun < nxt_run` moved to `<=`, gave `differing=714`.

Triage, probe section C. Over 4000 cases at n in {-2..3}, 1522 of them at n == 0, the head against the `n < 0` mutant gave `differing=0`. The control is that mutant plus a body that answers `["n0"]` for an empty plan, so it differs only where the body runs at n == 0. It gave `differing=1522`.

Kills, section B. The restored head passes all four checks, and each mutant fails exactly the check named for it.

## Figures

The local figures below were taken under the CI venv's Python 3.14 with `PYTHONPATH=tests/hastub`. Each line names its tree: b0f90860, or 75a6aee4, the code head after main's #2055, #2053 and #2056 were merged.

- `python3 dev/audit/harnesses/ux5_idle_codes_sites.py 217f7cefe95848c6d22f3172e61ab6419fb0b316 57cac0889c2af50fdf4205839710eead4d0ee3e6` -- the A, B and C lines quoted above. They were printed identically by the scratch copy at b0f90860 and by the tree copy at 75a6aee4.
- at b0f90860: `python3 dev/audit/harnesses/ux5_idle_codes.py 97f89cdaf5fb7fbcc046b40d0d26f16164f3e88e b0f90860 816547efe270a08e18e3b92f52185fe8c1fee2ef 1 20000` -- `cases=216223`, `mismatches=0`. This is the per-step `idle_reason` at 97f89cda against `idle_codes` at b0f90860. The same command with NEW=217f7cef printed the same two lines. The harness header records its null control: a solar test reading `>= 1e-6` printed `mismatches=509`.
- `python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED`, at b0f90860 and at 75a6aee4.
- `python3 tests/entities.py` -- `ALL 2212 ENTITY CHECKS PASSED` at b0f90860 and `ALL 2214 ENTITY CHECKS PASSED` at 75a6aee4, whose merged #2053 adds entity checks. That includes the check by `TRIAGE_JUDGE` that every mark still names a mutant this tree generates.
- `python3 tests/harness_headers.py` -- `ALL 109 HARNESS HEADER CHECKS PASSED`, at b0f90860 and at 75a6aee4, which adds the harness.
- `python3 -I tools/audit/seat/tmp_paths.py --check` -- `0 refused, 0 stale allow entries`, at b0f90860 and at 75a6aee4.
- at f6d28bb7: `python3 tests/env_drift.py --claims-only origin/main` -- `claims hygiene: origin/main ok`. Null control: the same tree with `claims-for: 6.7.16` in `tests/golden/claimed_drift.txt` exits 1 with `STALE CLAIM FILE: tests/golden/claimed_drift.txt declares claims for v6.7.16 but this tree is v6.7.17`.
- at f6d28bb7: `python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED`; `python3 tests/entities.py` -- `ALL 2214 ENTITY CHECKS PASSED`.
- at b0f90860: `python3 tools/pr/ci_predict.py --base 816547efe270a08e18e3b92f52185fe8c1fee2ef` -- `3 unpinned site(s) the diff adds` (the three lines under `## Unpinned sites`) and `no closures or fast red predicted`.
- at b0f90860: `python3 tests/closure.py select --diff 816547efe270a08e18e3b92f52185fe8c1fee2ef --workdir "$D"` -- `MODE: FULL`, so every script is CI's. Heavy scripts (`tests/features.py`, `tests/stress.py`, `tests/golden.py`, the mutation drives) run in CI by tvofi's 2026-10-07 rule. Their results are the check-runs at the head, not figures here.

## Red checks

Settled at the head (`commits/<head>/check-runs`, 40 check-runs, nothing pending, 2026-10-08T20:31Z): every check is success or skipped except `nightly-status` (113492436544), main's: `NIGHTLY FAILED: closures, mutation-nightly, nightly-ha (2025.2.0), nightly-ha (stable) failed last night`. `mutation` (113492436907), `fast (3.14)`, `closures`, `typing`, `pr-contract` and both `budget-raise-gate` runs are green. The entries below are every red an earlier commit of this branch carried.

Every red that any commit of this branch past the merge base carries, read through the API (`commits/<sha>/check-runs`, 2026-10-08T11:15Z), with the answer to each.

`mutation` (113297684200 at a249933a, 113277549988 at 217f7cef, 113263323707 at 05927892, 113233800551 at b78e5810, 113191548694 at d30236a5 and earlier) -- this diff's added unpinned sites. At b78e5810 six were left; this diff answers each one (`## Unpinned sites`). At a249933a it read `4673 unpinned site(s) against 4670 at the ratchet base dcc77dd0..., 4 of them added by this diff`, and `mutation-pins (1)` (113298028599) printed `PIN KILLED: 4 pinned, 0 left unpinned`, all four killed by `tests/features.py`. Those four rows are committed in 05bbf393. Cheaper detector: `tools/pr/ci_predict.py`'s ADDED UNPINNED arm, in seconds. It names sites but cannot say which survive.

`mutation-autofix` (113330956557 at a249933a) -- `skip-no-measurement -- THE REPAIR DID NOT HAPPEN`, although the one pin shard measured. Its artifact `mutation-pins-1` (id 11552898083) holds `status` `measured`, `head` a249933a and the four entries, but `merge_pin_shards` found no shard directory under the download path, so it reported no measurement. download-artifact extracts a lone matching artifact into the download path itself, not into a subdirectory. As `ci-autofix.md` directs for a red autofix, the rows were applied by hand: that artifact, through `mutation_table.apply_pins` at a249933a (`changed`), committed as 05bbf393. Cheaper detector: none in this pull request. The defect was in `merge_pin_shards`, and main's #2060 (R9-CI-2, in v6.7.17, merged here at f6d28bb7) fixed it by reading a download path that holds a `status` file as that one shard.

`mutation-autofix` (earlier: 112560320989 at ace05371, 112902087980 at 5eaf0982, 113165362694 at dc4e3f13) -- `skip-no-measurement`, red while `mutation` measured nothing. It succeeded at d30236a5 and pushed b78e5810. Cheaper detector: none, because it only reports what `mutation` measured.

`closures` (113263423959 at 05927892, 113164048164 at dc4e3f13, 112899052762 at 5eaf0982) -- `INERT READS UNDER-APPROXIMATED` under `tests/harness_headers.py`. At 05927892 the file was `dev/audit/harnesses/git_auto_maintenance_race.sh`, main's: #2051 landed without the entry, `closures-autofix` pushed 217f7cef, and #2055 adds the same entry on main. At dc4e3f13 the file was `dev/audit/harnesses/r9_ro12_batch_mutants.sh`, main's, repaired by main's cf0bba2b. At 5eaf0982 it was this branch's own `dev/audit/harnesses/ux5_idle_codes.py`, now listed in `inert_reads["tests/harness_headers.py"]`. Cheaper detector: `tools/pr/ci_predict.py`, which does not see a data-file read, so the `closures` job is the check.

`closures-autofix` (112922379387 at 5eaf0982, 113178838676 at dc4e3f13) -- `skip-manual-repair-owed`, the status `ci-autofix.md` gives an INERT READS failure. The hand repairs are the entries above. Cheaper detector: the same `ci_predict.py` arm.

`nightly-ha (stable)` and `nightly-ha (2025.2.0)` (113277493085, 113277493053 at 217f7cef) -- `FAIL a16:debug_inline` and `FAIL a16:debug_capped`. These are main's after #2041, and the fix-forward is #2056. This diff touches no download path. Cheaper detector: not this pull request's to name.

`delivery-status` (113277540404, 113263324849 and earlier) and `nightly-status` (113263322912 and earlier) -- main's, not required. They report delivery rows and nightly jobs that are not this pull request's. Cheaper detector: not this pull request's to name.

`env-matrix` (112557999944 at ace05371) -- red on origin/main at that commit's base (governance run 37531301054), and green at 5eaf0982 and 05927892 (113263324598). It is main's. Cheaper detector: not this pull request's to name.

`typing` (112558412302 at ace05371) -- `FAIL errors did not grow [recorded 0, measured 5 (+5)]`. It was fixed by `_fold_away`'s `AwayFold` return type and is green at b78e5810 (113233800391) and 05927892 (113263323619). Cheaper detector: `tests/typing_ruler.py --mypy` under the pinned toolchain, about 90 s once its venv exists.

`fast (3.14)` (112558412447 at ace05371) -- `tests/stress.py`'s production-call ratchet. It was fixed by c75b7770's `idle_codes`, one pass per channel, and is green at b78e5810 (113233800493). Cheaper detector: `tests/stress.py` run directly, which CI owns by the 2026-10-07 heavy-script rule.

`budget-raise-gate` (113263322635 at 05927892) -- cancelled, not failed. Its twins 113263331428 and 113265418831 succeeded at the same SHA. No `*_budgets.json` is in this diff.

## Unpinned sites

The sites `tools/pr/ci_predict.py` listed as added and unpinned at b0f90860 (and `mutation` at a249933a), by their line here:

- `custom_components/heatpump_optimizer/optimizer.py:1053 GUARD_OFF` (`if n <= 0:`) -- killed by the new value check "UX-5 a negative step count has no idle codes". Pinned in 05bbf393 from CI's pin shard.
- `custom_components/heatpump_optimizer/optimizer.py:1075 CMP_BOUND` (the sunny line's new text) -- killed by "UX-5 dust ahead is not surplus to wait for". Pinned in 05bbf393 from CI's pin shard.
- `custom_components/heatpump_optimizer/optimizer.py:1078 CMP_BOUND` (two sites on the solar line, `sp > 1e-6` and `nxt_sun < nxt_run`) -- killed by "UX-5 dust on this step still leaves a later surplus as a wait" and by the new "UX-5 surplus that arrives with the next run is not a wait". Both sites under the anchor are killed, so it is pinned in 05bbf393 from CI's pin shard.

The six sites `mutation` counted at b78e5810, by their line there, and where each went:

- `1053 GUARD_OFF` -- the first line above.
- `1053 CMP_BOUND` (`n <= 0` to `n < 0`) -- written triage, `tests/mutation_ledger/survivor_triage/optimizer.py/idle_codes.CMP_BOUND.a02b3552.json`, verdict `equivalent`, measured by probe section C.
- `1075 CLAMP_DROP` (`k = min(len(pw), len(surplus))`) -- removed with the redundant clamp. The new text of its line is the second site above.
- `1079 CMP_BOUND`, three sites on the solar line -- `idx < len(surplus)` is removed as redundant. The other two are the third line above.

## Forward-carry

none

## Friction

fixer.md-step-2: unenforced: `mutation_table.py --pin-killed` cannot run on a Mac for a diff whose sites only `tests/features.py` drives, so a killing check is proved by a scratch probe on the check's inputs and pinned only by CI's pin shards.


