R11-PRE-RELAY-REBUILD part 1 of 3 (owner card P12, 2026-11-13): roster carries 0-4. Carries 5-12 are later parts, dispatched at this handoff, and none is answered here.

- **Carry 0 (#3358's silent skip).** The skip came from the handoff arm's topic. `cloud_relay.sh` turned `fix/<t>-pr` into `<t>` alone (`topic_grammar.pr_topic`). `review_packet.py`'s handoff-not-applied read tries `<t>-pr` first and then `<t>`. #3358's repair returned under `handoff/r10-combi-tank-pr`, so the arm read only `handoff/r10-combi-tank`. That ref held an older tip, already in the head, whose body the relay had applied (its last update of #3358 ended OK on 2026-11-09). So the arm took the `continue` for "ancestor, body applied", with no line, while `bus.sh dispatch` refused handoff-not-applied. The rule now has one owner, `topic_grammar.handoff_topics`, moved out of `review_packet.py` and used by both readers through `topic_grammar.py handoff-topics`. The first topic that has a `handoff/` ref decides. `handoff_level`'s open and merged topic lists use the same rule, so `handoff/<t>-pr` with an open PR is no longer `handoff-no-pr`. Every other skip of a handoff that the head lacks is now owed on `<log>.level`. A missing body is `handoff-held ... NOBODY`, mirroring HELD-BODY. A hold-file skip is `handoff-held ... HOLD`. An unreadable ref or head, a busy tools tree, a BUSY update and an unreadable body are each `handoff-skipped <ref> <tip> #<pr> <why>`. These kinds are rewritten every pass.
- **Carry 1 (S14-TICK-STALE-SILENT).** `tick_loop.sh`'s `fresh_check` now restarts a branch-backed checkout that is clean and holds no commit outside origin/main (`checkout -q -B <branch> origin/main`). A branch that has commits of its own stays stale, with the why `the branch <b> holds <n> commit(s) origin/main lacks; it is never moved`. When a stale state lasts into a second consecutive pass (counted in `<out>.stale`), the board ends with `-> OWED relay-skipped code=<sha7> behind=<n>: <why> (stale <k> consecutive passes)`.
- **Carry 2 (S14-RELAY-CADENCE).** In the sleep between passes, `relay_gap_sleep` reaps a finished relay and starts the next one under the same lock once `HPO_TICK_RELAY_GAP` seconds (default 120, digits only) have passed since that relay ended. The holder now writes the end epoch as a third field of `<out>.relay.rc`. The tick keeps `--interval`. A stale pass starts no relay in its sleep, and neither does a relay that is still in flight.
- **Carry 3 (HELD-REVIEW over a returned verdict).** `review_freeze` now asks whether the dispatch's own `probe/rev-<pr>-<nonce8>` exists and is in `cloud-relayed.refused` or disposed in the ledger. If so, the review is over: the arm prints `RELEASED-REVIEW` and runs the update. Otherwise the HELD-REVIEW line and its level line name the probe's state: `probe=none (in flight)`, `probe=<sha8> relayed, not yet on verdict/<pr>`, or `probe=<sha8> held by the relay (dispose it to release)`.
- **Carry 4 (owed red text to a cloud seat).** Take a `handoff-wip/<topic>` BLOCKED.md that names `body_push: REFUSED PREDICTOR` and whose `PREDICT <check>` lines name a check in `merge_train.py owed-reds`. For it, the carry-fold arm reads that check at the topic's open PR head (`failure_logs.sh`: name, conclusion, error lines) into `<state>/cloud-owed-red-<topic>.md`, and the `carry-fold` level line names that file for the seat's next message. The carry-fold memo keeps the judged line, so the check is read once for each (wip, body) pair.

Alternatives not taken, and why each lost:
- Carry 0: stripping `-pr` in the relay and adding `<t>-pr` as a second read beside it. That would keep two copies of the rule that diverged once already.
- Carry 0: "any candidate not an ancestor decides". The relay would then disagree with `review_packet.py`'s first-with-a-ref rule.
- Carry 3: a timer release. It would release a review that is genuinely in flight.

## Head

`981cad4189b75d063894454ada80085b872c1b61`. It is `e9c80fbad11d02cb66f3129bf04a48030ef6bfe1` plus one repair commit for the red `tests / fast (3.14)` at #3648's head `16945f40` (see `## Red checks`): `dev/audit/harnesses/r11_relay_3358_skip.py` finds its root with the canonical `repo_root` walk in place of `Path(__file__).resolve().parents[3]`. The carries' figures below were measured 2026-11-15 20:20Z to 22:10Z at `e9c80fba` against `origin/main` `98847b99d7bb3238686efd6869f805c89c6d1ff1`; the repair touches only the harness's root line, and its harness figure is re-taken at this head. Merge base unchanged; `git merge-tree --write-tree origin/main HEAD` reports no conflict.

## Mutation proof

Each mutant is applied in its own worktree at the head by `perl -0pi` on its `# mut:` line, and that file's self-test is run. Failing rows:

- `mut:handofftopics` (`handoff-topics` back to `pr-topic`): FAIL `#3358's shape: fix/<t>-pr behind handoff/<t>-pr, handoff/<t> an older tip in its head, runs update_pr at handoff/<t>-pr`. This is the failing test first: the base's behaviour.
- `mut:nobody` (the NOBODY level line dropped): FAIL `and is owed HELD-NOBODY on the level, never skipped in silence (#3358)`.
- `mut:holdowed` (the HOLD level line dropped): FAIL `and owes handoff-held HOLD on the level, never skipped in silence (#3358)`.
- `mut:skipbusy` (a BUSY update unowed): FAIL `but owed handoff-skipped BUSY on the level, once, never skipped in silence (#3358)`.
- `mut:skiptools` (a busy tools tree unowed): FAIL `a tools tree held by a live relay is busy: no update`, and FAIL `and owed handoff-skipped BUSY on the level, never skipped in silence (#3358)`.
- `mut:reviewrelease` (the release predicate made false): FAIL `the dispatch's verdict refused by the relay releases HELD-REVIEW: update_pr runs`, FAIL `and says RELEASED-REVIEW naming the dispatch`, and FAIL `the dispatch's verdict disposed releases HELD-REVIEW too`.
- `mut:owedred` (the PREDICTOR case deleted): FAIL `a PREDICTOR refusal naming an owed red: the carry-fold level line names the owed red text for the seat's next message`, and FAIL `... which carries the check's name, conclusion and error lines, read at PR #77's head`.
- `mut:owednone` (the no-owed-red return dropped): FAIL `null control: a PREDICTOR refusal naming no owed red adds no text and reads no check`.
- `mut:gapstart` (no in-sleep relay start): FAIL `a relay that ends during the sleep is followed by another after the gap, with no tick pass between`.
- `mut:staleowed` (no board line): FAIL `freshness: a second consecutive stale pass ends the board with one '-> OWED relay-skipped' line: why, code and behind`.
- `mut:branchown` (the own-commit refusal made false): FAIL `freshness: a branch holding a commit origin/main lacks is never moved, and says why`.
- `mut:branchrestart` (`-B <branch>` replaced by `--detach`): FAIL `freshness: a clean branch-backed checkout behind origin/main with no commit of its own restarts on its branch at origin/main`.

For the four `tick_loop.sh` mutants, the nested self-test rows (branch, detached, GIT_DIR, poison, offline_spy) also fail, each naming the same nested row. `mut:tghandoff` in `topic_grammar.py` is pinned by its self-test row `handoff_topics: fix/<t>-pr reads <t>-pr then <t>, ...`. The diff adds no `.py` production line outside that function, and `review_packet.py` now binds the name to it.

## Unpinned sites

`prepr.sh` step 6d is run with `MUTANT_IN_PLACE=1` and `MUTANT_CMD` set to the self-tests of `topic_grammar.py`, `ledger.py` and `review_packet.py`. It leaves two survivors, both `STMT_DEL` of a `ck(...)` row inside `topic_grammar.self_test`: `tools/audit/seat/topic_grammar.py:122` (the `handoff_topics` row) and `:133` (the `handoff-topics` CLI row). Deleting a check row removes a pin, not production behaviour, so no check can kill it. Each row was shown to fail on its production mutant. The CLI row kills the five `main()` survivors that an earlier run at `b38dead5b9` reported, and `mut:tghandoff` is pinned by the `handoff_topics` row. Disposition: a self-test row, not a production site.

## Null control

- #3358's null at both ends: a head that holds `handoff/r10-combi-tank-pr` (`d07f8e9e`, the head the handoff was applied at by hand) gives `null_updated=0 null_owed=0` at both the base and the head. The self-test pins the same case on synthetic refs (`#3358's null control: a head holding handoff/<t>-pr has neither an update nor a level line nor a skip line`).
- A predicted red outside the owed set adds no text and runs no `failure_logs.sh` (`mut:owednone` kills that row).
- One stale pass writes no board line (`freshness null control: one stale pass writes no OWED line on the board`). A fresh pass clears the count.
- A relay still in flight at the gap starts none (`null control: a relay still in flight at the gap starts none`).
- A verdict-less in-flight dispatch still holds, as before: `a dispatch at the head with no verdict holds the handoff: no update_pr call`, its level line now ending `probe=none (in flight)`. A probe that is neither refused nor disposed holds again (`null control: the same probe no longer refused holds again`).

## Figures

- `python3 dev/audit/harnesses/r11_relay_3358_skip.py --seat <base worktree>/tools/audit/seat`, with the base worktree at `98847b99d7`: `RESULT defect_updated=0 defect_owed=0` and `RESULT null_updated=0 null_owed=0`. This is #3358's silent skip, replayed on its real commits.
- `python3 dev/audit/harnesses/r11_relay_3358_skip.py` at the head: `RESULT defect_updated=1 defect_owed=0` and `RESULT null_updated=0 null_owed=0`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: at `e9c80fba` `1 of 115 HARNESS HEADER CHECKS FAILED` (`FAIL every inlined walk matches the canonical helper and no depth root remains [FAIL depth seams: dev/audit/harnesses/r11_relay_3358_skip.py:34: ROOT = Path(__file__).resolve().parents[3]]`), the `tests / fast (3.14)` failure; at `981cad4189` `ALL 115 HARNESS HEADER CHECKS PASSED`.
- `python3 -c "import sys;sys.path[:0]=['tests'];import harness_headers as h;print(h.depth_root_seams())"`, the depth-seam arm alone: one seam (`r11_relay_3358_skip.py:34`) at `e9c80fba`, `[]` at `981cad4189`, 0.54 s and 0.51 s wall.
- `bash tools/audit/seat/cloud_relay.sh --self-test`: `cloud_relay self-test: 515 checks, 0 failed` (at `1325b217e0`; the commit after it changes `ledger.py` and `tick_loop.sh` only).
- `python3 -I tools/audit/seat/ledger.py --self-test`: `ledger self-test: 104 checks, 0 failed`. Its census `every kind cloud_relay.sh writes is a ledger kind` failed at `1325b217e0` until `handoff-skipped` was registered as a derived kind.
- Wall time for `bash tools/audit/seat/tick_loop.sh --self-test`, measured with `time` on one host under the same load: 1m47s at the base and 2m00s at the head. The step replay's bound is `SELF_TEST_TIMEOUT` (180 s). The two relay-gap rows (about 10 s of wall clock) run in the outer run only, as the nesting block already does. The base copy runs itself nested about nine times, and left ungated the rows timed out the replay (rc 124 at `1325b217e0`).
- `bash tools/audit/seat/tick_loop.sh --self-test`: `tick_loop self-test: 48 checks, 0 failed`.
- `python3 -I tools/audit/seat/topic_grammar.py --self-test`: `topic_grammar self-test: ok`.
- `python3 -I tools/audit/seat/review_packet.py --self-test`: `review_packet self-test: 133 checks, 0 failed`.
- The class seams: `awk '/^handoff_arm\(\) \{/,/^}$/' tools/audit/seat/cloud_relay.sh | grep -n continue` enumerates the arm's skip sites. Each is either owed or a head that holds its handoff:
  - no listed row: nothing to apply.
  - no `handoff/` ref under any topic: nothing to apply.
  - unreadable ref or head: `handoff-skipped`.
  - handoff in the head (no body, body applied, seed): nothing owed.
  - no body ref: `handoff-held NOBODY`.
  - hold file: `handoff-held HOLD`, or `handoff-body-unapplied` for a body-only skip.
  - freeze: `handoff-held VERDICT/REVIEW/UNREAD`.
  - recorded failure and backoff: `handoff-update`.
  - no body directory, or unreadable body: `handoff-skipped`.
  - body names another code head: `handoff-body-stale`.
  - body-only with no `Code:` trailer: `handoff-body-unapplied`, or recorded as applied.
  - HELD-BODY: `handoff-held BODY`.
  - tools tree busy or refused: `handoff-skipped`, or `handoff-update`.
  - update BUSY: `handoff-skipped`.
  - update failed: `handoff-update`.
  - BODIED: applied.
  - no new head after the update: the ledger's `dispatch`.

  A PR outside the open-PR listing's 100-row page never enters the loop. Its handoff is owed by `handoff_level` as `handoff-no-pr`, because no listed open PR carries its topic.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 98847b99d7bb3238686efd6869f805c89c6d1ff1`: `Architecture score: dS +0.0000 NULL`.
- `python3 tools/pr/ci_predict.py --base origin/main`, after `--apply-inert` registered the new harness as an INERT READ of `tests/harness_headers.py`: `no closures, fast, governance or instrument red predicted`.

- `python3 tests/closure.py select --diff 98847b99d7bb3238686efd6869f805c89c6d1ff1` with the head's own `closure.py`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/entities.py`, `tests/doc_claims.py`). Run at `981cad4189` with `PYTHONPATH=tests/hastub`, with the `run_always` pair and the ratchet: `ALL 2723 ENTITY CHECKS PASSED`, `ALL 410 checks PASSED`, `layout self-test: ok`, `ALL 115 HARNESS HEADER CHECKS PASSED`, `STRUCTURE RATCHET PASSED`. The rendered block below comes from the current `origin/main`'s registered instrument, as `pr-contract` verifies it, and prints `MODE: FULL`; CI's gate is the authority on which mode runs.

<!-- figure-block: scope-line mb=98847b99d7bb3238686efd6869f805c89c6d1ff1 head=981cad4189b75d063894454ada80085b872c1b61 -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->

## Red checks

- `tests / fast (3.14)` at `16945f40` (run 43777623561, job 133008866653): `tests/harness_headers.py` refused the new harness's depth-counted root (`ROOT = Path(__file__).resolve().parents[3]`, added at `bc727cfd5b`), a check already on `98847b99d7`. Fixed in this diff (the harness inlines `tools/audit/repo_root.py`'s `repo_root`); the before/after is in `## Figures`. Cheaper detector: exists. `tests/harness_headers.py` is `run_always`, which `fixer.md` step 5 already requires running locally before the handoff, and its depth-seam arm alone (`harness_headers.depth_root_seams()`) reads the defect in about half a second (`## Figures`). Standing cost of a new detector: none built, because the existing one was owed at the final head and not run there; `prepr.sh` leaves `harness_headers.py` to CI deliberately (it takes the EXCLUSIVE lease). Process state (b).
- `pr-contract / pr-contract` and `gate` at `16945f40`: downstream of the red above. `pr-contract` refused the body for not naming `tests / fast (3.14)` under `## Red checks` (answered above); `gate` aggregates the required checks.

## Brief carries

Roster carries of R11-PRE-RELAY-REBUILD, by position. Carries 0-4 are built here, as above. Carries 5-12 are later parts.

- Carry 0: built. The predicate is the topic resolution. The silent site was the "ancestor, body applied" `continue` reached through `handoff/r10-combi-tank`. Every non-ancestor skip is owed.
- Carry 1: built. Clean branch restart, the own-commit why, and the second-pass board line.
- Carry 2: built. `HPO_TICK_RELAY_GAP` is the in-sleep relay start.
- Carry 3: built. Refused or disposed releases. The level names the probe's state.
- Carry 4: built in the relay, the side that has `gh`. `cloud_dispatch.py` is untouched.

## Forward-carry

none

## Friction

none
