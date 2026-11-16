R11-PRE-TOOLCHAIN-PIN part 2 as dispatched (carries 5-10), at the approved design `a37706d599ca28414378bda7813068b79fd716d6` (`design-verdict/R11-PRE-TOOLCHAIN-PIN` 72c0fda351, `Design review: approve`). Owner ruling 2026-11-13 on card P1: seats and the beat run their tools from a promoted stable ref, and main reports product and machinery status separately. This diff builds the first seam of carry 9, the stable tools ref itself, and nothing that reads it yet:

- `tools/ci/gate.py` gains the tuple of machinery jobs and one pure function, `status`: a run's latest jobs and an event class in, PRODUCT and MACHINERY out, each green, red or unread. The `gate` job's conclusion, `REQUIRED`, `event_class` and the summary lines are untouched.
- `tools/audit/seat/toolchain.py` is the new instrument: the one place the ref name `toolchain/stable` and the seat paths exist. `behind` counts what the ref holds over a checkout; `promote` moves the ref along main to the newest commit whose push run reads MACHINERY green.
- `tools/audit/seat/prune_refs.py` `classify` keeps `toolchain/*` (design invariant vi).
- The beat gains a `toolchain-promote` row, and the toolchain self-test is a measured step of `instrument-self-tests`.

Scope decision, and why. The payload's part line is "build carries 5-10"; carry 9 names the design's whole p1 and p2, and carries 5, 6 and 8 call the verdict function (design df3267eba7 section 6, carry 5). Built in one diff that is the group's XL remainder, past `fixer.md`'s preamble (one subsystem, about 400 production lines). This diff is the part every other one depends on, and it is inert on merge: no freshness site, train or relay reads the ref, so nothing refuses on an absent ref until a later part repoints a site, by which time the beat has been promoting it. The design's own rollout (new-code callers refuse by invariant iii until the orchestrator runs init) is avoided for every site.

Departure from the design, raised here: section 6 states p1 and p2 touch disjoint files, while p1's promote reads MACHINERY, which section 1 gives to `tools/ci/gate.py`, a p2 file. The function and its tuple land here with their first caller; p2's other items (the gate summary's two lines, the scorecard's A_prod and A_mach, stamp rule 2 and its check flag, the policy sentences) do not.

Alternatives that lost. *Promote keeps its own list of machinery jobs*: a second owner of the split the design gives to `gate.py`, and stale the day `REQUIRED` moves. *Promote reads the run's `gate` job*: `gate` covers product and machinery together, so a product-red main would hold the tools ref, the coupling the ruling removes. *The walk reads only the newest three concluded runs*: a green fourth-newest commit past the ref would never promote when three merges land inside one beat interval; the walk instead stops at the first run the ref already holds, bounded by `SCAN_RUNS`. *`--force --why`* (design round 3): dropped by the round-4 minimal shape, not built. *The prune guard as a literal in `prune_refs.py`*: a second copy of the ref's family name; it imports `REF_PREFIX`. *A seat path list per caller* (today's three): the instrument holds their union, so a later repoint deletes a constant and narrows no site.

## Head

a2c094d8c0e7aa8d8e4f9263e2e0179da914ac28, merge base 921214bf4246338c1a83fbc5269eaa0bfe91b7d5 with origin/main (Mon Nov 16 2026 01:47Z).

## Mutation proof

Predicates mutated, never tails. `python3 dev/audit/harnesses/r11_toolchain_mutants.py` makes each mutant as one exact one-occurrence replacement in a copy of `tools/`, runs the mutated file's own self-test there and requires a `FAIL` row; a crash is no kill.

- `toolchain.py`, each `verdict=killed`: `M-absent-behind`, `M-absent-promote` (the absent ref's refusal, each verb), `M-init-present`, `M-offmain`, `M-ff`, `M-green-sha`, `M-green-walk` (the three refusals the design's evidence plan names, dropped in turn, the walk's and the explicit sha's separately), `M-concluded`, `M-stop-at-ref`, `M-machinery` (promotion reading PRODUCT), `M-held-count`, `M-held-any`, `M-readback`, `M-current-sha`, `M-sha-filter`, `M-paths`, `M-from`, `M-fetch`, `M-direction`.
- `M-ff` is killed on the refusal's text: with the check dropped, git's own non-forced push still refuses the move, so the ref does not move under the mutant either. The check exists to refuse before the GitHub reads and to name the rule.
- `prune_refs.py`: `M-keep` (the keep dropped) turns `toolchain/stable, always a commit of main, is kept` red.
- `gate.py`: `G-empty` (the tuple emptied), `G-unread-green` (unread read as green), `G-neither` (a required name in neither verdict), the design's three targets, and `G-skip-required`, `G-cancelled-red`, `G-na`.
- `beat_jobs.py`, in its own self-test's mutant table: `toolchain_held_dropped`, `toolchain_rc_clean`, `toolchain_answer_dropped`, `toolchain_sha_pinned`, `toolchain_overlay_unread`, each `killed by` the row it names.
- Failing test first: at the merge base with only the new self-test rows applied, `python3 -I tools/ci/gate.py --self-test` stopped on `NameError: name 'status' is not defined`, and `python3 tools/audit/seat/prune_refs.py --self-test` printed `FAIL  toolchain/stable, always a commit of main, is kept: the merged-ref rule would delete the tools ref`. The toolchain self-test and the beat row's cases were written beside their code, not before it; the harness above is their proof.

## Null control

- `status`: a push run with every job green reads green, green; a run red in `tests / fast (3.14)` reads PRODUCT red and MACHINERY green, the mirror of the closures-red case; `tests / ci-ratchet` red moves neither verdict; for every event class, each required name reddens exactly one verdict.
- `promote`: beside each refusal sits the call that moves the ref on the same fixture: a green commit of main past the ref promotes and the read-back equals the pushed sha; `--init` creates the ref while absent; two bad runs above a green third are not a hold; one bad run past the ref is not three; an empty run listing reads and promotes nothing.
- `behind`: without `--fetch` a ref moved on origin is not seen; `--from` a commit behind a seat-path change counts it.
- `prune_refs.py`: a merged ref named `toolchain`, `toolchains/stable` or `fix/toolchain/stable` is still deleted.
- Beat row: a promotion leaves the digest empty.
- `M0` of each of the harness's three files, nothing mutated, prints `failed=0 verdict=null-ok`.

## Figures

- `python3 -I tools/audit/seat/toolchain.py --self-test`: `toolchain self-test: 42 checks, 0 failed`.
- `python3 -I tools/ci/gate.py --self-test`: `gate self-test: 120 checks, 0 failed`.
- `python3 tools/audit/seat/prune_refs.py --self-test`: `SELF-TEST PASS (79 checks)`.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: `beat_jobs self-test: 261 checks, 0 failed`.
- `python3 dev/audit/harnesses/r11_toolchain_mutants.py`: `RESULT mutants=26`, `RESULT survived=0`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs --budgets`: exit 0.
- `python3 tools/pr/ci_predict.py`: `CI PREDICT: no closures, fast, governance or instrument red predicted against 921214bf4246`, after `--apply-inert` wrote the three `inert_reads` entries for the new files, the push site was registered in `ref_privacy.py` `PUSHERS` and `python3 -I tools/ci/selftest_scope.py record --step toolchain --step ref-pruner` recorded the two steps whose read set this diff changes.
- Gate scope: `python3 tests/closure.py select --diff 921214bf42 --workdir <dir>` prints `MODE: FULL`, reason `tools/ci/gate.py changes the gate itself`; run here: `tests/entities.py`, `tests/harness_headers.py`, `tests/layout.py`, `tests/closure.py selftest`, `tests/env_drift.py --claims-only`, each exit 0. The rest is CI's.
- No finder harness exists for this group (an owner ruling on a process audit; design section header). The done criterion's first half, the product-green share of the last 20 main push runs printed by an instrument, is not met by this diff: it is the scorecard's A_prod line, carried below. Its second half is: the promotion step is a tracked instrument, a beat row and a step of `instrument-self-tests`.
- Step 8, the class's seams. The design's enumerators, run at this head: (a) `git grep -n -E '\.\.origin/main|detach[^|]*origin/main|-B [^ ]+ origin/main|origin/main:\$?\{?(rel|tools)' -- tools/audit/seat tools/pr .claude/hooks ':!*selftest*' ':!*/instruments/*' ':!*/fixtures/*'`; (b) `git grep -ln "pr_args.sh" -- tools/audit/seat ':!*selftest*' ':!*.md'` less `git grep -l "pr_tools_fresh" -- tools/audit/seat`; (c) `git grep -n -E 'fork_head\(|outside_is_mains' -- tools/audit/seat`. No seam they return is closed in this diff: every freshness site of design section 3 still compares with `origin/main` or launches unchecked, and each is carried below as one item. (b) newly returns `toolchain.py` (the name in a comment) and nothing else new.

<!-- figure-block: scope-line mb=921214bf4246338c1a83fbc5269eaa0bfe91b7d5 head=a2c094d8c0e7aa8d8e4f9263e2e0179da914ac28 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Unpinned sites

`prepr.sh`'s diff-mutant step drew its first 40 mutants from the added lines and left 8 alive, every one in the self-test's own text, none in a production line. Its command was the four self-tests with `beat_jobs.py --self-test --no-mutants` among them; the full self-test is 80 s a mutant.

- tools/audit/seat/beat_jobs_selftest.py:549 STMT_DEL: deletes one case row; killed by the full self-test, whose mutant-table row `toolchain_answer_dropped` names that case.
- tools/audit/seat/beat_jobs_selftest.py:551 STMT_DEL: the same, by `toolchain_sha_pinned`.
- tools/audit/seat/beat_jobs_selftest.py:555 STMT_DEL: the same, by `toolchain_held_dropped`.
- tools/audit/seat/beat_jobs_selftest.py:559 STMT_DEL: the same, by `toolchain_rc_clean`.
- tools/audit/seat/beat_jobs_selftest.py:564 STMT_DEL: the same, by `toolchain_overlay_unread`, the row added for it after the step's run.
- tools/audit/seat/beat_jobs_selftest.py:1180 STMT_DEL: deletes the mutant table; the full self-test stops on a NameError.
- tools/audit/seat/beat_jobs_selftest.py:553 CONST_SWAP: the fake instrument's exit code 3 read as 4. Equivalent: the row's rule is any non-zero exit beside a `PROMOTE-HELD` line, and `toolchain_rc_clean` and `toolchain_held_dropped` pin both halves.
- tools/audit/seat/beat_jobs_selftest.py:562 CONST_SWAP: `plan_slots` 10 read as 11 in an overlay whose point is that it lacks `repo`. Equivalent: the row under test reads no `plan_slots`.

How the six kills were measured: a one-off probe, not in the tree, replaced the statement at each line with `pass` in a detached worktree of this branch and ran `python3 -I tools/audit/seat/beat_jobs.py --self-test` with mutants on. Each run exited 1 with exactly one FAIL row, the mutant row named above (the NameError for line 1180). Null control: the same probe with nothing replaced exited 0 with no FAIL row. A first attempt in a bare copy of the seat directory was discarded: its null control exited 1 (the darwin-selftest wiring row reads the real tree), so its exit codes proved nothing.

## Red checks

none

## Forward-carry

- After the merge the orchestrator runs `python3 -I tools/audit/seat/toolchain.py promote --init --repo tvofi/heatpump_optimizer` once from the tools checkout. Until then the beat's `toolchain-promote` row prints `toolchain-promote: rc=1: toolchain: REFUSED origin/toolchain/stable is absent ...` every pass, and nothing else reads the ref. The beat's credentials must be able to push `refs/heads/toolchain/stable`; who may push it and whether a ruleset protects it is the design's open owner decision. Carry: R11-PRE-TOOLCHAIN-PIN (item tp2)
- Carry 9, the rest of the design's p1, not built: the section 3 freshness sites repointed at `toolchain.py behind` (`pr_args.sh` `pr_tools_fresh`, `beatd.py` `fresh` and STALE-CODE, `tick_loop.sh` `fresh_check`, `cloud_relay.sh` `tools_level`, `orchestrator_tick.py`'s behind count), the `merge_train.py` main mirror with `merge_pr.sh` (design [R3], notes dr14-dr16), which must land with or before the train's site. Precondition for that part: `toolchain/stable` exists on origin and the beat row has promoted it at least once, read from the last answer the row keeps under the beat's state directory (the instrument doc names the file). Carry: R11-PRE-TOOLCHAIN-PIN (item tp2)
- Carry 7, not built: `train.sh`, `remerge_main.sh` and `merge_pr.sh` refuse on `behind` > 0 (design section 3); it rides the sites part above. Re-measured at this head: enumerator (b) still returns all three. Carry: R11-PRE-TOOLCHAIN-PIN (item tp2)
- Carry 9, the design's p2 less the verdict function, not built: the gate summary's PRODUCT and MACHINERY lines, `scorecard.py` A_prod and A_mach, stamp rule 2 on PRODUCT with its read-only check flag, the stamp sentences of the nudge and orchestrator role contracts (policy). The function they call is `gate.status(jobs, cls)`; its `jobs` is `prelude.run_jobs`' shape, name to (status, conclusion). The design's `after` edges (R11-PRE-PARALLEL-PIPELINE part 2, R11-PRE-ROUND-METRICS's cache producer) still hold for these. Carry: R11-PRE-TOOLCHAIN-PIN (item tp2)
- Carries 5, 6 and 8 (the L3 helper for a process check's unreadable input, the `introduced-red: pending` packet, `introduced_at` over a cancelled main run), not built. The word unread for a CI run's jobs now has its owner on main: `gate.status`; the helper calls it and owns only the advisory line, the count of three and the escalation (design df3267eba7 section 6, carry 5). Carry: R11-PRE-TOOLCHAIN-PIN (item tp2)
- `tools/pr/cancel_superseded.py main` still has no beat row (carry 9's last sentence); part 1 has not merged, so the verb is not on this base. Carry: R11-PRE-TOOLCHAIN-PIN (item tp2)
- For R11-PRE-PARALLEL-PIPELINE part 2, which edits `REQUIRED` and `event_class` in `tools/ci/gate.py`: `status` computes product as `REQUIRED[cls]` less `MACHINERY_JOBS`, and the self-test row `<class>: every required name reddens exactly one verdict` runs over every key of `REQUIRED`, so a new event class or required name is covered without an edit; a renamed machinery job must be renamed in the tuple, which the row `the machinery tuple names push-required jobs and the one self-tests lane` refuses otherwise. Carry: R11-PRE-PARALLEL-PIPELINE

## Friction

- fixer.md: contradiction: carry 10 stands at this part too. The payload's part line cuts by carry index ("Part 2 of 2: build carries 5-10") and carry 9 inside that range is the design's whole p1 and p2, an XL remainder against the preamble's one subsystem and about 400 production lines; the part line and the design's parts still do not name each other. This seat built the design's first seam and carried the rest. Carry: R11-PRE-TOOLCHAIN-PIN (item tp2)
- fixer.md: contradiction: the approved design's section 6 states p1 and p2 touch disjoint files, and p1's promote reads the verdict section 1 assigns to a p2 file. Carry: R11-PRE-TOOLCHAIN-PIN (item tp2)
