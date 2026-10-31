R10-FLY-RAISE-REVIEWABLE (S, instrument; triage P345, batch 95). Every budget raise is red at `budget-raise-gate` until the owner's approval (or a mandated one) names its head, and that approval comes after the verdict. So the reviewer-dispatch readers refused the review that the approval needs (#3045 at 9ef51b82, hand override; #3006's pre-approval reds). This adds `merge_train.approval_owed(train, pr, head, red)` as the single owner of that state, built on `Train.raise_hold` and so on budget_raise_gate's own `raises_between` and `approval`. Every reviewer-dispatch reader now asks it. `classify` itself, the train and the merge state do not change.

- `merge_train.py classify --pr N`: when the head is RED and `approval_owed` returns a reason, it prints `APPROVAL-OWED <sha> <why>` and exits 4. Without `--pr`, the result is the same as before.
- `bus.sh dispatch` passes `--pr "$pr"`, dispatches on rc 4 the same way as on 0 and 3, and prints the line.
- `orchestrator_tick.one_pr` prints `#N: RAISE APPROVAL OWED at <head8>: review it, then approve under the owner or the mandate (0013) -- not its fixer (K15 (d))` in place of NOT REVIEWABLE.
- `review_packet.py render`: when classify `--pr` answers APPROVAL-OWED for a required red, the red becomes the `approval-owed` advisory and is not the `required-red` refusal (that refusal is what made `bus.sh dispatch` die). This reader is the third layer the dispatch measured.
- `cloud_dispatch.py`'s reviewer prompt waits on `classify <head> --pr <pr>` and treats 4 as reviewable. Without that change the reviewer would get a 1 and block.
- Instrument pages updated: merge_train, orchestrator_tick, bus.sh, review_packet.
- `dev/audit/harnesses/r10_fly_raise_reviewable.py` is the real-head control (fixer step 18). It is INERT through `ci_predict.py --apply-inert`.

**One departure from the triage text, and the reason.** P345 says `approval_owed` should get "the red set" in which `classify` "reports `gate` and `budget-raise-gate / budget-raise-gate` red". The `classify` red set is taken over the ruleset's contexts, and the only one is `gate` (`tools/policy/fixtures/required-contexts.json` `contexts`). At #3045, `classify` prints `red: gate` and never names the unit (see Figures F1). If the predicate were fed that set, it would never fire. Every caller therefore passes the red set over `merge_train.gating_names(required)`: the ruleset contexts plus every unit gate.py can owe. That is the same expansion `gating_names` already provides for exactly this purpose. Mutation M5 pins this. The names come from `git diff --no-renames --name-only <merge-base> <head>`: P345's command, with `--no-renames` added because `closure.py selftest`'s RENAME_SITES pin requires it.

## Head

c7ccdbf7e5a16dabc37a14bb3d26da635f4c5c63, the merge of origin/main 2b6bef7453a8bdaf97d42f382a116ce226b35ccc into 5b189b35217a1b81e36a041b54dc4d70f29ffa68, which carried the code the figures below measure (base f3c9144b8088). Main's three new commits touch only delivery rows (`git diff --stat f3c9144b8088 2b6bef7453a8` lists 9 files, all under `dev/programme/delivery/`), so none of the measured files moved. `tools/pr/prepr.sh` was re-run on this body at this head after the merge.

## Mutation proof

Each mutant was applied to the head, the named self-test was run, and the tree was restored.
- M1: approval_owed's test (b) is dropped (`return why if raises and not held else None` -> `return why`). `merge_train.py --self-test`: `FAIL P345 row 3 (null): budget-raise-gate red with no raise in the diff ... stays RED, rc 1` and `FAIL P345 (null): a raise the owner's mandated approval already holds at the head owes nothing`; 388 checks, 2 failed.
- M2: test (a)'s "only gate units" is dropped (`if RAISE_GATE not in red or red - {GATE, RAISE_GATE}` -> `if RAISE_GATE not in red`). `FAIL P345 row 2 (null): the same plus tests / fast (3.14) red stays RED, rc 1`; 388 checks, 1 failed.
- M3: bus.sh's `4)` arm is deleted. `bus.sh --self-test`: `FAIL P345: a raise whose only red is its owed approval (classify --pr APPROVAL-OWED) dispatches, records, and prints the line`; 111 checks, 2 failed.
- M4: bus.sh's `--pr "$pr"` is dropped. `FAIL a head whose required context concluded failure (classify RED) is not dispatched, and nothing is recorded` (the argv pin); 111 checks, 1 failed.
- M5: the tick's owed call is set to `owed = None`, and separately its red set is changed from `gating_names(req)` to `req`. `orchestrator_tick.py --self-test`, both mutants: `FAIL P345 PRS #3045 shape: RAISE APPROVAL OWED present, naming the raise` and `... NOT REVIEWABLE absent`; 241 checks, 2 failed.
- M6: review_packet's `if owed:` -> `if False:`. `review_packet.py --self-test`: `FAIL P345: a required red that is only a raise's owed approval renders`; 53 checks, 1 failed. `approval_owed_line`'s `r.returncode == 4 and` is dropped: `FAIL P345: the reason is classify --pr's own APPROVAL-OWED line at rc 4`; 53 checks, 1 failed.
- Survivor, equivalent: in `return why if raises and not held else None`, dropping only `raises and` survives. On each of its three no-raise returns, `raise_hold` returns `held=True` (`no budget file changed`, the `#2401` `raises_between: 0` path, both `[], True, ...`), so `not held` already implies a raise. The conjunct is kept because it states P345's test (b) in its own words.

## Null control

- Real heads, through `dev/audit/harnesses/r10_fly_raise_reviewable.py`. Its only change to the classifier is a transport shim: a `gh api --paginate --slurp P` call is read as one page, because this cloud seat's proxy refuses `--paginate`'s numeric-id follow-up links. Without the shim, `raise_hold` Stops here and `approval_owed` fails closed (RED rc 1), which is the designed answer.
  - #3045 at 9ef51b82: at the base (f3c9144 checkout, no `--pr` there) `RED ... red: gate` rc=1. At the head with `--pr 3045`: `APPROVAL-OWED 9ef51b82... 1 budget raise(s), first tests/ci_budgets.json: critical_path_minutes_band: None -> 1.3 (a pinned value the gate cannot sign as routine): a raise is the owner's (0013): tvofi's approval is on b02ffd170d50, not this head 9ef51b8215dd ...` rc=4.
  - Null #3055 at 6a988a23: `RED ... red: gate` rc=1 at both ends.
  - The merge state is unchanged: at the head, without `--pr`, #3045 still reads `RED ... red: gate` rc=1 (F1).
- Self-test rows, each against its null: P345 rows 1-5 in `merge_train.py --self-test`, plus a held raise (an owner's mandated approval at the head) staying RED, and a red gate without the raise unit staying RED. In bus.sh, RED/GREEN/WAIT/unreadable are unchanged, and APPROVAL-OWED dispatches. In the tick, the #3045 shape prints RAISE APPROVAL OWED, while `tests / fast (3.14)` red too, or no raise in the diff, still prints NOT REVIEWABLE. In review_packet, the advisory replaces the refusal only at rc 4 with the head's own line.

## Figures

- F1 (the departure's evidence): `python3 tools/audit/seat/merge_train.py classify 9ef51b8215dd7216950f177386fb2f5a8f010a47 --repo tvofi/heatpump_optimizer` at f3c9144 prints `RED 9ef51b82... pending: none red: gate`, rc 1. The gating red set (`classify(latest_runs(runs), gating_names(required))[2]`, read live) is `['budget-raise-gate / budget-raise-gate', 'gate']`.
- F2 (the real-head control above): `python3 dev/audit/harnesses/r10_fly_raise_reviewable.py <checkout> classify <sha> --repo tvofi/heatpump_optimizer [--pr N]`, with <checkout> a merge-base worktree and the head. #3045: rc 1 -> 4. #3055: rc 1 -> 1.
- F3 (self-tests at the head): `python3 tools/audit/seat/merge_train.py --self-test` (388 checks, 0 failed); `bash tools/audit/seat/bus.sh --self-test` (111, 0 failed); `python3 tools/audit/seat/orchestrator_tick.py --self-test` (241, 0 failed); `python3 -I tools/audit/seat/review_packet.py --self-test` (53, 0 failed); `python3 tools/audit/seat/cloud_dispatch.py --self-test` (124, 0 failed).
- F4 (scope): `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run`, naming `tests/doc_claims.py` and `tests/entities.py`. Both were run with `PYTHONPATH=tests/hastub`, together with the `run_always` lines (`env_drift.py --claims-only`, `closure.py selftest`, `layout.py`) and `tests/structure.py`, at the head: `ALL 2493 ENTITY CHECKS PASSED`, `ALL 255 checks PASSED`, `claims hygiene: f3c9144b8088... ok`, `ALL 117 closure shrink pins PASSED`, `layout self-test: ok`, `STRUCTURE RATCHET PASSED`. The first closure run refused `no rename-detecting --name-only diff under RENAME_SITES` at approval_owed's diff and the two stubs; the diff is `--no-renames` now, because a rename-detecting `--name-only` would name a renamed budget file by its new path alone.
- F5 (the class's seams). The rule is `git grep -nE "classify\(|merge_train.py\"?\}? classify|merge_train.py classify|& set\(REQUIRED\)|req_red|req_bad" -- 'tools/audit/seat/*.py' 'tools/audit/seat/*.sh'` (self-test lines excluded). The gate-conclusion readers it returns, each with its disposition:
  - `bus.sh` dispatch's classify: closed here.
  - `cloud_dispatch.py` reviewer wait: closed here.
  - `review_packet.py` required-red (`& set(REQUIRED)`): closed here.
  - `orchestrator_tick.one_pr` `req_red`: closed here.
  - `orchestrator_tick` main-tip `req_bad`: main's tip, not a review, left alone.
  - `merge_train` `wait_ci` / `main_green` `classify(` and `proof_watch.required_state`: the merge judgement, deliberately unchanged (P345: "the merge state, the train and main stay as they are").
  - The other `classify(` hits are homonyms that read no check run: `ledger.py`, `prune_refs.py`, `row_position.py`, `run_twins.py`, `tmp_paths.py`, and `review_carry.py`. The dispatch named "the review-carry check" as a layer, but `review_carry.classify(repo, reviewed, new, main)` reads only the commit range and never the gate, so it holds no seam.

## Red checks

none

## Forward-carry

none

## Friction

none
