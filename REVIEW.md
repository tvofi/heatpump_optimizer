Design review: revise

Independent read-only review seat; neither designer. Reviewed against `origin/main` at
`07a09406a1cc97076a6f28581f87f313b322a6b6`:
- phase 1, `probe/design-ci-layout` at `b7a76185` (cited `P1:<line>`, its `DESIGN.md`);
- phase 2, `probe/design-ci-umbrella` at `7fdd39c4` (cited `P2:<line>`).

Policy read: `CLAUDE.md`, `fix-review.md`, `judge.md`, `ci-autofix.md`, `gate-scoping.md`
and `orchestrator.md` section 11, all from origin/main. Every command below was run by
this seat. Evidence is under `ev/` and this seat's own instruments under `tools/`; each
instrument is disclosed as this seat's (`fix-review.md` step 9).

**Re-runs of the designers' scripts.** Every phase 2 enumerator re-ran byte-identical
to its committed output:
- `c1_counterfactual`, `critpath`, `gate_replay`, `dupes`, `heads`, `durations`
  (`ev/rerun_*.txt`);
- `unitcheck --self-test` prints `SELF-TEST ok`.

Phase 1's enumerators re-ran too:
- `measure`, `noop_tail` and `dispatch` reproduce `summary.md`, `jobs.tsv`, `tail.txt`,
  `noop_tail.txt` and `dispatch.txt` unchanged;
- `stepset` reproduces its three control rows: `88/88 lost 0 gained 0`, `gained 2`, and
  `lost 16 gained 2` (`ev/rerun_p1_stepset.txt`).

The numbers are real. The items below are about what the numbers do **not** cover.

## Items that must change before a fixer is dispatched

1. **The single `ci.yml` concurrency group loses runs, and the design claims the
   opposite.**
   - P2:153-159 puts code and verdict events of a PR in one group, `CI-<pr>`. Verdict
     events get `cancel-in-progress: false`.
   - P2:479-481 says verdict events "queue, never cancel, and are never cancelled by
     another verdict event".
   - GitHub's rule (`ev/gh_docs_actions-group-concurrency.md`): "any existing `pending`
     job or workflow in the same concurrency group will be canceled and the new queued
     job or workflow will take its place". That holds whatever `cancel-in-progress`
     says. Only one run can be pending.
   - Measured: 13 of the 14 body edits in phase 2's own sample land 0–4 s after the code
     event at the same head (`ev/edit_after_push.txt`, from `raw/runsat_*.json`).
   - Failure path: a push lands while the previous head's run is still running. The new
     code run C2 is created and cancels the old run, but **C2 stays pending until the
     cancellation completes**. The edit arrives 0–4 s later and replaces pending C2.
   - Result: no code run exists at the head. The verdict run's gate fails "no code
     verdict at this head", and nothing queues another code run until the next push
     (`ev/gate41_model.txt`, case E).
   - The same rule lets **anyone who can post a review on this public repository**
     cancel a pending code run, so a new outside actor can stall a PR. Today a review
     starts only `budget-raise-gate.yml`, which shares no group with Tests.
   - Required change: put verdict events in a group of their own (or by run id), so they
     never share a pending slot with code runs. Keep the prelude's wait for code runs.
     Restate P2:479-481 with the documented rule.

2. **The gate can go green with a required job never run. The brief asked for such a
   scenario; here is one.**
   - P2:233 and P2:461 say a retarget (`edited` with `changes.base`) is `kind = code` and
     re-runs everything.
   - Its `cancel-in-progress` is false (`action == 'edited'`), so if anything is running
     in `CI-<pr>`, the retarget run R is pending.
   - A body edit or a review then replaces R, which is cancelled before any job (item 1).
   - The verdict run V carries "the newest COMPLETED ci.yml run at head with kind ==
     code" (P2:416). That is the pre-retarget run C1, scoped (`GATE_SCOPE=auto`,
     `closure-scope`, mutation's changed lines) against the **old** base.
   - So the gate passes, and no code unit ever ran against the new base
     (`ev/gate41_model.txt`, case D).
   - This is no worse than today, where Tests never re-runs on a retarget. But it breaks
     the guarantee P2 states.
   - Underneath it: **the predicate cannot be built from the API P2 names.** The runs
     API returns no `action` and no job outputs. `gate.py` therefore cannot learn a past
     run's `kind`, or whether a cancelled-before-start run was a code run. P2:416 must
     say how kind is recorded, for example by an artifact the prelude writes and the gate
     reads.
   - Hardening (`ev/gate41_model.txt`, case B, a planted `pr=''`): the gate takes
     applicability (`† only when a PR is named`, P2:408) from the prelude it is judging,
     and never requires `prelude` to have succeeded. A prelude that emits `pr=''` on a
     `pull_request` event yields a green gate with `pr-contract` and `budget-raise-gate`
     never run.
   - Required change: derive applicability from `github.event_name` (and the verified
     dispatch input), and fail on any prelude conclusion other than `success`.

3. **A retarget run's gate is always red, by the design's own guards.**
   - `governance`, `hassfest` and `validate` carry
     `if: github.event.action != 'edited' && …` (P2:184, 187-188). So on a retarget,
     which is `kind = code` and so carries nothing, they are skipped.
   - The gate then reports `governance / policy-docs: ABSENT` and the rest
     (`ev/gate41_model.txt`, case C).
   - Every later verdict run carries that same run, so the PR stays red until a new push.
   - Required change: key those three guards on `needs.prelude.outputs.kind`, as the
     code units are. Otherwise 4.3's retarget row is false.

4. **Deleting `budget-raise-gate-rerun.yml` contradicts a measurement already in the
   tree.**
   - Its header (`.github/workflows/budget-raise-gate-rerun.yml:3-9`) and commit
     `5f1ca69d5` record that after the owner approves, "the pull_request_review run …
     passes but the earlier pull_request run's red stays on the pull request until
     someone runs gh run rerun".
   - P2's review path depends on the opposite: the review run's newer `gate` displacing
     the code run's red `gate` (P2:472-474). P2 lists exactly that behaviour as not
     measured (P2:829-831).
   - Every budget raise goes through this path.
   - Required change: keep a re-run hook until U8 shows on a live PR that the review
     run's `gate` binds the merge box. The hook must re-run the code run's failed jobs:
     `budget-raise-gate`, `pr-contract` and `gate`, because the gate reads only its own
     run (P2:414). Re-running only `gate` would re-read the stale red. P2:818-823's
     fallback should be corrected to say this.

5. **`pr-contract-rerun.yml`'s deletion rests on a false premise.**
   - P2:470-471 says no workflow outside the umbrella writes a check at a PR head.
   - The code-scanning check `CodeQL` (app `github-advanced-security`) is at 17 of the 22
     sampled heads (`raw/checks_*.json`). It is red at two, each time after the last
     `pr-contract` run had concluded:
     - `b931d0f44a`: CodeQL red at 17:57:04, last `pr-contract` 17:55:44;
     - `acf14d8f22`: CodeQL red at 18:19:08, last `pr-contract` 18:18:06.
   - `pr-contract`'s red list has no app filter (`.github/workflows/pr-contract.yml:250-253`),
     so the body owes an answer to that red.
   - This is not a regression: today's rerun watches workflows, not that app.
   - Required change: state the gap, then either make `pr-contract` wait for the
     code-scanning check or record its exclusion as policy, owner-approved. The deletion
     itself is acceptable once its stated reason is true.

6. **Deleting the held-run approvals ignores the tree's measurement of held runs.**
   - P2:536-539 calls a held run a "harmless second verdict", and P2:832-835 says "the
     design works either way".
   - `tools/pr/approve_held_runs.sh:12-15` records PR #1276, run 35500365827: a held
     `Tests` run "sat action_required beside green workflow_dispatch equivalents … and
     its held check shadowed the dispatched one in the merge box".
   - P2 never mentions that tool, `dev/governance/roles/nudge.md:85` ("Run
     `tools/pr/approve_held_runs.sh` after every App push"),
     `tools/audit/seat/INSTRUMENTS.md:36`, or the `hpo-runs` identity in `CLAUDE.md`.
   - Required change: measure in U0/U10 whether a held `ci.yml` run shadows a dispatched
     `gate` before deleting the approval steps. Add the tool and nudge.md to section 9.

7. **`ci.yml` silently drops tests.yml's `recheck` and `no-skip` inputs.**
   - `lane-proofs` and the `laneskip` step key on `github.event.inputs.recheck` and
     `github.event.inputs.no-skip` (`.github/workflows/tests.yml:2103-2104, 2224-2225`).
   - In a called workflow, `github.event` is the caller's payload, and `ci.yml` declares
     only `pr` (P2:144-146).
   - P2:675 also changes `merge_train.py`'s `DISPATCH` to `(("ci.yml", ()),)`, dropping
     `-f recheck=true`.
   - Effect: the batch proof loses its lane proofs and lane skip, and R9-CI-SKIP's
     force-every-lane switch disappears. Phase 1 kept both inputs on purpose (P1:336-339).
   - Required change: declare both inputs on `ci.yml`, pass them as `workflow_call`
     inputs, and read `inputs.*` in tests.yml.

8. **Dropping the C1 composition: the proof given up is redundant, but the numbers and
   the scope are wrong.**
   - **Redundancy holds, on one condition.** With V1 nothing consumes a traced
     recording, so nothing is left for traced-equals-bare to prove. Removing the consume
     steps and the job makes the fail-closed bare path the only path, as P2:296-298
     says. But the condition is that the composition is removed at its source **in the
     same PR**:
     - `tools/coverage/coverage_tree.sh:190-200` still runs every
       `tests/composed_closures.json` script through `closure.py record` under strace
       inside `coverage`;
     - P2:307-311 defers deleting that ("can later delete"), and P2:670 says
       "removed with W1 (PR 1)", so the design contradicts itself;
     - left in place, `coverage` keeps paying strace for a recording nobody reads.
   - **The "upper bound" is not one.** P2:79-81 and P2:302 charge 239.1 s, the
     `tests/closures.json` recorded seconds.
     - On the CI runner the bare recording measured 221 / 430 / 424 / 480 s
       (`ev/boost_bare_seconds.txt`, from closures job logs `116310058507`,
       `116863532407`, `117338282214` and `117616974645`).
     - The designers' replay, with only that constant changed
       (`tools/c1_boost_{427,480}.py`), gives a V1 median gain of 264 / 232 s, not
       342 s. Runs slower: 2/24, by up to 351 / 404 s, not 1/24 by 163 s
       (`ev/c1_counterfactual_boost_*.txt`).
     - V2 stays at 343 s, so "V1 is as fast" (P2:305) is false at measured cost.
     - Unmeasured offset: V1 also removes strace from `coverage`'s run of the script.
     - V1 may still win on simplicity, but D-4 must go to the owner with these numbers.
   - **The combined PR 1 is unspecified.** Phase 1 still moves `composed-proof` into
     `nightly.yml` as a self arm and adds it to `REQUIRED_LANES` (P1:148, P1:170, P1:400).
     Its nightly-arm tree-named upload and coverage-restore check are kept for that arm
     (P1:155-156). With W1 all of that must go, and section 8 of P2 says only "replace
     2(c)".

9. **The per-unit null control does not detect a dropped step, except the kind its own
   self-test plants.**
   - The self-test removes the first step of a job, which always executes.
   - This seat planted three defects into a U5-style AFTER. The BEFORE is Tests dispatch
     39158300302, which executes 12 of 28 jobs (`ev/plant_unitcheck.txt`,
     `tools/plant_unitcheck.py`):
     - P1: the whole `closures-autofix` job deleted;
     - P2: every step of `fast (3.14)` that the BEFORE skipped deleted (19 → 17);
     - P3: a step's body gutted under its unchanged name.
   - `unitcheck.py` returns **rc 0 on all three**. Phase 1's `stepset.py` uses the same
     step-name rule.
   - The permission half fails open: with no saved log header both sides read `UNREAD`,
     and `UNREAD == UNREAD` passes (`unitcheck.py`, `perms()`).
   - Events do not match either. U4, U6, U7 and U8 compare a dispatch AFTER against a
     `pull_request` BEFORE, which breaks phase 1's own rule that each pair must match
     event, sender class and scoping case (P1:441-443).
   - Required change:
     - add a **static** half: per job, the set of (step name, hash of `run`/`uses`/`with`/`if`)
       from the workflow YAML before and after, under the closed map;
     - make `UNREAD` a refusal;
     - give every PR-only job a `pull_request` AFTER.

10. **`gate_replay.py`'s 22/22 replays a different function from section 4.1.**
    - It takes the newest check per name across every run at the head, over all 17 names
      unconditionally (`measure/gate_replay.py:38-48`). It has no `pr` applicability, no
      verdict carry, no `kind`, and no push exemption for `closure-scope`.
    - So the agreement is evidence for the name map and the skip rule only, and is no
      null control for the new mechanisms.
    - Required change: replay 4.1 itself (this seat's `tools/gate41_model.py` is a
      starting shape), with verdict, retarget and dispatch cases.

11. **Readers neither design names** (this seat's own survey, `tools/readers_diff.sh` →
    `ev/readers_diff.txt`). Each was then read by hand.

    Missed by both designs:
    - `tools/pr/approve_held_runs.sh`, `dev/governance/roles/nudge.md:85` and
      `tools/audit/seat/INSTRUMENTS.md:36` (item 6).
    - `dev/governance/roles/nudge.md:93`: the stamp precondition "the latest Tests run on
      the current `origin/main` is green". Under P2 it becomes `gate`.
    - `dev/governance/rules/defect-root-cause.md:143`: names `tests.yml` as what
      `nightly-status` reads. P1 updates only :146.
    - `dev/audit/harnesses/ci_script_seconds.py:37`: `gh run list -w Tests --branch main`.
      Under P2 there are no Tests push runs.
    - `dev/audit/harnesses/superseded_runs.py:55-56`: lists runs per workflow file
      (`actions/workflows/<file>.yml/runs`) for six files. Under P2 those PR runs all
      belong to `ci.yml`, so the harness measures nothing.
    - The `github-advanced-security` `CodeQL` check as a check writer at PR heads
      (item 5).

    Phase 2, and missed in substance:
    - `tools/audit/seat/orchestrator_tick.py:921-925`. P2 calls NIGHTLY_CLASS
      "unaffected". But with `req = {gate}`, every unit check is non-required, so a red
      `tests / closures` on main is printed as "non-required red (nightly/record class)"
      because the regex has `closures`.

    The citations both designs did make were spot-checked and are exact: `entities.py`
    :1636, :24852, :27701, :28003 and :28511; `merge_main_bot.py:146`;
    `a1_dispatch_arms.sh:67,135`; `merge_train.py:286,2971,3097`;
    `orchestrator_tick.py:120`; `nightly_status.py:209`; `policy_lint.mjs:6077,6096`;
    `ci_ratchet.py:177,185`; `closure.py:476`; `stamp.py:13,173`.

12. **Smaller corrections.**
    - (a) Rollback order (P2:614). The revert PR's head runs the old workflows and
      writes no `gate`, so it cannot merge under `[gate]`. Restore the saved ruleset
      first, then revert.
    - (b) One required name means one forgery point. Pin in `entities.py` that no
      workflow file other than `ci.yml` defines a job id or `name:` equal to `gate`. A
      dispatch of any such workflow on a PR branch would write a newer `gate` at the head.
    - (c) Say which side wins when a carried job and a skipped row in this run share a
      name (P2:418 says "∪"). It must be the carried one, or 4.3's carry is order-luck.
    - (d) U9 is not independent of U0–U8 (P2:732). `entities.py` reads the actual
      workflow files, so its scoped-gate control is meaningful only on
      `probe/ci-layout-all`.
    - (e) State that each callee keeps its top-level `permissions:` floor, for example
      tests.yml's `contents: read`. That floor, not the caller's cap, is what a callee
      job without its own block receives. This answers half of P2:826-828.

## Rulings on the specific questions (no change required unless stated)

- **D-1 (phase 1: `record-autofix` out of the Tests push run): approve.**
  - Both measured reds were operational, not code verdicts: run 39156244284 is
    `RECORD AUTOFIX: skip-push-refused`, and run 39156632994 is `HTTP Error 403`
    (`ev/ci_log_extracts/record_autofix_*.txt`).
  - `stamp.py` rule 2 is documented as "fast + closures" (`tools/release/stamp.py:13`).
    It reads only `--event push` runs of Tests (:1413-1415), and rule 5 re-applies the
    record predicate itself through `delivery_status.py --require-rows` (:34-38). So the
    stamp loses no protection, and stops refusing on a record race.
  - `merge_train.main_green` waits on required contexts only (`merge_train.py:1415`).
  - The tick still sees a red `record-autofix`: it reads per-commit check runs
    (`orchestrator_tick.py:296-305`), and NIGHTLY_CLASS matches `record` (:168, :921-925).
  - Optional: a one-job `record.yml` would spare `nightly.yml` its push trigger and six
    skipped rows per push to main.
- **One PR or two: two, phase 1 first. Agreed with P2 section 8.**
  - P2's ruleset cut-over needs a freeze. Phase 1's closures re-record cycle and its
    nightly-status window (P1 R-4) should not share that merge.
  - PR 1 = phase 1 + W1 (corrected per item 8) + the inert `ci.yml` stub.
- **Required-check plan against ruleset 23698884: consistent.**
  - Live ruleset read this session (`ev/ruleset_23698884_live.json`): 17 contexts, equal
    to `tools/policy/fixtures/required-contexts.json`. Only `budget-raise-gate` is pinned
    (15368).
  - `arch-score` is not required (D-2 stands).
  - Branch rules: deletion, non_fast_forward, required_status_checks, pull_request.
    There is no merge-queue rule, and 0 `merge_group` runs exist (D-3 stands).
  - `[{"context": "gate", "integration_id": 15368}]` is sound, provided the edit keeps
    the rest of the ruleset unchanged: the `pull_request` rule
    (`require_code_owner_review`) and both `always` bypass actors (Integration 5094721,
    DeployKey). Plus items 4, 6 and 12(a).
- **Scoping, per workflow.**
  - `tests`: scoped by measured closures — **sound**.
  - `codeql`: always-on, with O17 kept **only** on an owner D-5 ruling. O17 is a suffix
    allow-list, not a measured closure, so the brief's rule does not cover it otherwise.
  - `governance`, `hassfest`, `validate`, `pr-contract`, `arch-score`,
    `budget-raise-gate`: always-on — **sound**.
  - `nightly.yml`: unscoped — **sound**.
- **Permissions and secrets.**
  - This seat recomputed each workflow's union of job-level grants from the YAML. P2's
    caller grants (P2:176-207) equal them: tests `contents/actions: write`,
    `pull-requests: read`; governance `issues: write`; pr-contract `checks: read`; and
    so on.
  - The secrets tests.yml reads (`HPO_LEDGER_*`, `HPO_RECORD_*`, `HPO_APPROVER_*` in
    `record-autofix`) leave with phase 1. That leaves `CLOSURES_PUSH_TOKEN` and, until
    item 6 is settled, `HPO_RUNS_*`.
  - That holds **only if D-1 is approved**. P2 does not handle the D-1-refused branch,
    where `record-autofix`, its `environment: record-writer` and its App secrets stay in
    the called tests.yml.
  - The environments API is closed to this seat (`ev/environments_live.json`), so
    phase 1's R-3 stays unverified.
- **Bot loop guards: sound.**
  - Subjects are unchanged, and the autofix jobs stay `pull_request`-only. In a callee,
    `github.event_name` is the caller's, so a `ci.yml` dispatch runs no autofix.
  - No `workflow_run` re-runner remains, until item 4 adds one back. That hook must keep
    its `stale_run` guard against its own completion.
- **pr-contract's `edited` trigger.**
  - Moving it into `ci.yml` as a verdict event is sound in shape. The #1514 rows it
    skips are caller rows named `tests`, `codeql` and so on, not required names.
  - Its safety depends on items 1–3.
