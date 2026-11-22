R11-SELFTEST-ABSORB (round 11): the countermeasure for main's red `governance` drift step (run 44922703115 at a8efe1d1c2), built from proposal P-R11-SELFTEST-ABSORB items 1 to 5. Its root cause: every instrument change that adds a read to a gated self-test reddens main's drift step until somebody re-derives `tools/ci/selftest_closures.json` by hand, and the bot's half of that repair, absorbing the push run's measured reads, was never built. 17 such repairs outside any round are recorded under the new bug class `R11-SELFTEST-TABLE-ADDITIONS`. This change is instrument and workflow code plus one policy sentence; it touches no `custom_components/` line.

- **Drift-red reclassification (item 2).** `selftest_scope.py check --absorb-out PATH` re-grades drift over the table with the run's own reads absorbed (`carried()`: only reads that name something at this head, only steps whose run text the run measured). When nothing is still refused, the step passes with `... 0 refusal(s); ABSORB OWED: n read(s), m step(s)`, writes the absorbed table to PATH and the job summary, and leaves the checkout's table alone. An `UNMEASURED` or `STALE` step, or any refusal absorb cannot repair, stays red and is named (`remains:`). The workflow's separate absorb step is folded into drift, and the `selftest-absorbed` artifact is uploaded wherever drift wrote one.
- **`grows --old --new`.** This is the "table only grows" half of the review. It reuses drift's coverage semantics, so a `D/**` collapse counts as covered and a moved `run_sha` is not a drop. It names every read of the old table the new one drops.
- **The beat row `selftest-absorb` (item 1).** `tools/audit/seat/selftest_absorb.py beat` reads main's push runs of `governance` back to the last clean one (capped at `--max-runs`) and grades each run red, owed or clean. In a scratch clone at origin/main's tip, it runs that tip's own `selftest_scope.py absorb` over the red and owed runs' `selftest-measured` artifacts. With `--push`, it commits the table alone and force-pushes the one standing ref `handoff/selftest-absorb` through `tools/pr/app_push.sh --branch-only`, which now accepts that ref and forces it alone. The commit message names `--at <tip> --run ...`. rc: 0 CLEAN, 1 OWED, 2 UNREADABLE, 4 RECORD-OWED. `beat_jobs.py` maps those to the board lines `OWED selftest-absorb n read(s) m step(s) on handoff/selftest-absorb` (plus `PUSH-REFUSED`), `RECORD-OWED: selftest-absorb ...` naming the Linux `record` command, and `UNREADABLE`. The row is in `beatd.jobs.json` (every 1800 s, timeout 900 s).
- **`verify` (item 3, the mechanical review).** `selftest_absorb.py verify --repo-dir <checkout> --head <head40>` checks three things: the head changes the table alone, the message's `--at` is the head's parent, and regenerating at the parent over the named runs gives a byte-identical (`cmp`) table. It then runs the parent's `selftest_scope.py grows`. It prints `SELFTEST-ABSORB VERIFIED` only when all of that holds.
- **The tick's main-red brief (item 4).** `orchestrator_tick.py` reads the failed steps of the red `governance` job (jobs API). When the drift step alone failed, the brief reads `held by selftest-absorb <sha>` (the standing ref's sha when it is ahead of main) and tells the orchestrator to dispatch no fixer to re-derive the table. A second failed step gets the fixer brief as before.
- **Records (item 5).** `dev/audit/config/bugclasses.json` gains class `R11-SELFTEST-TABLE-ADDITIONS` (barriered, 17 non-round instances), and its `_rca` entry `R11-RCA-SELFTEST-TABLE-DRIFT` points at the existing `dev/audit/rca/R11-RCA-SELFTEST-TABLE-DRIFT.md`. The countermeasure sentence of `R10-RCA-SELFTEST-SCOPE-DRIFT` no longer says the bot's half was not built. `selftest_scope.py`'s THE BOT'S HALF paragraph and `base_drift` docstring now name the beat row. `INSTRUMENTS.md`, `instruments/selftest_absorb.py.md` and `instruments/beat_jobs.py.md` describe the row.
- **Gating.** The new self-test is a gated step `selftest-absorb` in `governance.yml` (`selftest_absorb self-test: N checks, 0 failed`). Its `tools/ci/selftest_closures.json` entry was entered by hand, as `scorecard`'s was, because `record` needs Linux strace and this seat runs on Darwin. Its read set was measured with a Python audit hook over the self-test (4 files, 4 probes). `selftest_scope.py static`: 128 gated steps, 0 problems.

Deployment owed by the orchestrator once this merges:
- give the standing PR a roster group or an open-titles override for the `selftest-absorb` topic, so the opener keeps the one standing pull request open from `handoff/selftest-absorb`;
- land the root-cause note's evidence in-tree if wanted (this PR records the class and points at the existing RCA file);
- run the beat in shadow over the next 20 push runs of `governance` before acting on its OWED lines.

## Head

`e247f929d46fce3f39216cdff4d034ca1cda5c70`, on `origin/main` at `63c6d1cff9` (the merge base, 2026-11-22); `git merge-tree --write-tree origin/main HEAD` exits 0. It is a one-line repair on top of `1ab809af50` (the head reviewed for the delta): `dev/README.md`'s machinery-figure row for `fixer, reviewer and design seats -runs-> bus.sh` cites `fix-review.md`'s shortened `bus.sh push-verdict <pr>`, the text `880f254423` left when it fit `fix-review.md` to its token cap. Restoring the path-qualified text instead puts `fix-review.md` at 2779 against its 2775 cap (`node tools/policy/policy_lint.mjs --budgets`). At e247f929: `python3 tests/doc_claims.py` `ALL 441 checks PASSED` (at 1ab809af: `2 of 441 checks FAILED`); `node tools/policy/policy_lint.mjs` `TOTAL: 0 error(s)`; prepr passed rc=0 (`PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`).

Earlier record, kept: `6f895244fd19cc43cb21a19a09280b7bcbf3105b`, on `origin/main` at `a8efe1d1c2` (the merge base); `git merge-tree --write-tree origin/main HEAD` exits 0. The code and every measurement below are at `c037e9bfe152`. The two commits after it answer prepr's predicted reds and change no instrument line: `R11-SELFTEST-TABLE-ADDITIONS` joins `finding.schema.json`'s `class_guess` enum, with `.claude/workflows/audit-find.js`'s generated block rewritten by `python3 tools/audit/fold_ledger.py sync` (`fold_ledger: 0 violation(s)`); and `tests/closures.json` adds `tools/audit/seat/selftest_absorb.py` to `tests/entities.py`'s closure (`ci_predict.py --apply-inert`). After both, `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` predicts no closures, fast, governance or instrument red.

prepr: passed rc=0 at 6f895244fd19cc43cb21a19a09280b7bcbf3105b (`PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`, the seat's overlays)

## Mutation proof

Each production line was mutated in this checkout, the instrument's own self-test run, and the line restored (`git checkout`). Failing checks per mutant:

- `selftest_scope.check_cli`, `absorbed = bool(added) and not remain` to `absorbed = False`: "the bot's step: drift over a run with an unrecorded read is a note, not a red ...".
- The same line to `absorbed = bool(added)`: "the bot's step: drift stays red on an UNMEASURED step beside an absorbable read: the absorbed table is kept, the refusal it still makes is named".
- `selftest_scope.drops`, the new table's `run_sha` replaced by the old one's: "grows: the absorbed table covers the live one, its run_sha moves included (null control)".
- `selftest_scope.absorb_write`, the `remain |= set(drift(...)[0])` line to `pass`: "absorb: a STALE step a source measured, with no new read, remains and is named; nothing written".
- `orchestrator_tick`, `if held is not None:` to `if False:`: 3 checks, among them "main-red held by selftest-absorb: run 44922703115's job 136902224642, the drift step its one failed step, reads held by selftest-absorb and the standing ref's sha, never a fixer dispatch".
- `orchestrator_tick.absorb_hold`, the one-failed-step test dropped: "main-red held by selftest-absorb: null control: a second failed step beside the drift step is the fixer brief".
- `app_push.sh`, `--branch-only` no longer accepting `$STANDING_ABSORB`: 4 checks, among them "--branch-only pushes the standing handoff/selftest-absorb ref without a body".
- `app_push.sh`, the refspec unforced: 3 checks, among them "force-pushed, it alone (a batch/ branch is not forced)".
- `app_push.sh`, every refspec forced: 5 checks, among them "force-pushed, it alone (a batch/ branch is not forced)".
- `selftest_absorb.py --self-test` carries 16 planted mutants of its own (`41 checks, 0 failed`, each mutant killed), and `beat_jobs.py --self-test` carries 5 for the row (absorb_owed_dropped, absorb_owed_any_rc1, absorb_push_refusal_dropped, absorb_record_owed_silent, absorb_unpushed).

## Null control

- **Failing first.** This head's `selftest_scope.py --self-test --workflow <origin/main's governance.yml>` gives `159 checks, 3 failed`, all three "the bot's step" checks; with this head's workflow it gives `159 checks, 0 failed`.
- **The root cause's three runs as fixtures**, through `selftest_absorb.py beat --run <id> --at <sha>` without `--push`:
  - defect, run 44922703115 at this head: rc 1, `OWED 738 read(s), 7 step(s)`.
  - the same run at this head with the hotfix's table (`25238b470a`'s `tools/ci/selftest_closures.json`): rc 0, `CLEAN ... (a repair merged since)`.
  - null, green run 44379511133: rc 0, `CLEAN (run 44379511133): nothing to absorb`, with no clone made.
  - the whole window from main (no `--run`): rc 1, the same 738 reads and 7 steps over 12 runs (44922703115 back to 44677469341).
- **The beat reproduces the hand repair.** The defect run's absorbed table and the window's, each less this branch's own `selftest-absorb` entry, are byte-identical to the hotfix's table at `25238b470a`.
- **verify.** The beat's commit made locally (the App push intercepted) is `84c7bce5b148`, parent this head: `SELFTEST-ABSORB VERIFIED`. The same commit with one read planted out (`alert-lister-mutants` drops `tools/ci/alert_list.py`) gives rc 1, `VERIFY-REFUSED the head's table differs from the regeneration`. `grows` over that planted table refuses with `UNDER-SCOPED step alert-lister-mutants: files misses ['tools/ci/alert_list.py']`; over the beat's own table (null control) it reports `0 read(s) of the old table the new one drops`.
- **Darwin, pre-existing.** `bash tools/pr/app_push.sh --self-test` fails the same 2 "real git (c)" checks at the merge base as at this head; every check this change adds passes.

## Figures

- `python3 -I tools/ci/selftest_scope.py --self-test`: `159 checks, 0 failed`.
- `python3 tools/audit/seat/selftest_absorb.py --self-test`: `41 checks, 0 failed`.
- `python3 tools/audit/seat/beat_jobs.py --self-test`: `309 checks, 0 failed`.
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: `391 checks, 0 failed`.
- `python3 tools/audit/seat/beatd.py --self-test`: `157 checks, 0 failed`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `0 index gap(s)`.
- `python3 -I tools/ci/selftest_scope.py static`: `128 gated step(s), 0 problem(s)`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, no budget moved.
- `python3 -I tools/audit/seat/selftest_absorb.py beat --repo-dir . --run 44922703115 --at c037e9bfe15285692c5f7412732a1c13a3159968 --work <dir>`: `SELFTEST-ABSORB OWED 738 read(s), 7 step(s)`.

<!-- figure-block: scope-line mb=63c6d1cff9a29ec0c99bcbd5e12c229b61e7c184 head=e247f929d46fce3f39216cdff4d034ca1cda5c70 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Red checks

- `tests / fast (3.14)` (job 136998957300, run 44952149596, head 1ab809af): `tests/doc_claims.py` failed `every arrow is cited, every citation holds in the tree, and the figure has one entry` and `reversing any one arrow of the page's figure is a finding`, both caused by `880f254423` shortening the string the figure cites. Fixed at e247f929. Defect answer (`defect-root-cause.md`, second trigger): a cheaper detector existed and was not run. `python3 tests/doc_claims.py` takes about 3 minutes locally, against the 51 minutes the CI job ran. The scoped prepr this branch used (`PREPR_SKIP_CODE=1`) skips the code-keyed steps, so a text edit to a file that a doc_claims figure cites reached CI unchecked. The standing cost of the detector is about 3 minutes per prepr on a branch whose diff selects `tests/doc_claims.py`. Carry: dismissed: one instance; the cost test and any countermeasure belong to a root-cause seat, not this fixer (`defect-root-cause.md` step 2)

## Forward-carry

none

## Friction

none

## Approval

This is a policy change. `dev/governance/roles/fix-review.md` gains the bullet "The standing absorb pull request (P-R11-SELFTEST-ABSORB)". That changes what a fix reviewer must do: for a head that changes `tools/ci/selftest_closures.json` alone, the bullet replaces steps 1 to 16 with `selftest_absorb.py verify`, which is a regeneration `cmp` plus the parent's `grows` check that the table only grows. Any other line is `blocked <sha> absorb-verify: <line>`, and a head that changes any other path is reviewed in full. The owner authorised approval of this policy part under mandate 6893738184. It merges only on an approving review at its head.
