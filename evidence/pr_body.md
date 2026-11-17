R11-PRE-NO-READ-BUILDERS, part D of the approved design (design/R11-PRE-NO-READ-BUILDERS de4e49ddc1558abbc64d26049015d16592a42ef2, `Design review: approve` at design-verdict 02b7a5e8c41cd47e5764fa9332b36287b2f6ae1c): a cause per red gate run, in the vocabulary the convergence record already holds (decision 0018 section 3; card E11-N-GATE-CAUSE, and for main card E11-GATE-REDS). Both cards re-read in `dev/audit/yardstick/round11/EVALUATION.json` at the merge base, landed from eval/r11 c04cef7fca50e00fa23466dab28f941a4d5034af (`review.verdict` approve, of 83dc9488180379b859042b5f24b87d94a5a02c95): `decision: accepted`, neither rewritten nor dropped.

**Part C is not in this pull request, and cannot be built at this base.** The design orders C after R11-PRE-TOKEN-LEDGER's merge, and the per-session iterator C imports does not exist (`## Figures`). The load count of E11-N-RULE-YIELD, E11-N-INSTRUMENT-YIELD and the workflow run line of E11-N-GATE-CAUSE stay open on the group.

**D. A cause per red run.** `loop_ledger.py --runs DIR` reads `ci_runs.json` and `jobs/jobs_<id>.json` from the directory `round_metrics.py produce` writes and makes no API call. A red is a run attempt whose `gate` job concluded `failure`: a main row on main's push (`event` push and `head_branch` main, `found_by ci-main`), a head row on any other run (no `found_by`). One row per red; its cause is the first of these that holds:

1. a later attempt of the same run went green: `external`;
2. main was red (the row's own run on main; for a head row, main's last push run at or before it, each main run read at its latest attempt): `#<n>`, the pull request merged at main's first red push run after its last green one, parsed by `round_metrics.SUBJECT` from that commit's subject in `--repo`;
3. a later run at the same `head_sha` went green: `external`;
4. on a head row, a later run of the same pull request went green: `#<pr>`. The pull request is the run's `pr`, else the `pr` of a run at its `head_sha`; `head_branch` is never a key.

`roster_lib.is_cause` is the cause test taken out of `convergence_why`, which calls it; a derived cause is held to the same function, and one it refuses reads `unread`. A derived row carries no `rca`, is written to no roster and feeds no other read. `fetch_runs` keeps `head_sha`, `event`, `head_branch` and `pr` on each `ci_runs.json` row; `runs.json` is built from the narrow rows before the four fields are added, so `scorecard.py`'s input is unchanged.

`unread` is a read state, never passed through the cause test (verdict note d-unread-not-a-cause): a merge subject naming no pull request, a head no run names a pull request for, a derived word the test refuses. A run with no job listing at its latest attempt can hold a red no one read (a first-attempt success aside): it prints its own `unread` row and the count becomes `gate_reds unread (k of n runs ...)` with the reds read beside it, by the file's no-partial-value rule.

**The product/machinery column prints `unread`** (verdict note P1, item d-toolchain-p2-column): `tools/ci/gate.py` at the merge base holds no verdict function (`## Figures`). Each row lists the attempt's failed jobs as `gate.machinery_line` splits them, over the set `gate.gate_required()` plus `prelude` and `gate`. `gate.py` is unchanged.

## Departures from the design note, raised

- **A red nothing cleared reads `uncleared`, a second read state.** The note derives the cause from the clearing event and names no word for a red with none (an abandoned head, a main red with no red spell read). `unread` would say an input is missing when every input was read. It is counted beside the causes and is held to no vocabulary. Changing it to `unread` is one constant.
- **The note lists three clearing events and no order among them.** The order built is the list above: a green later attempt of the same run first, since it is the same tree; main's red spell before a green at the same `head_sha`, since a pull-request run tests the head merged into main at that time and a later run at the same head can go green because main was fixed. The self-test pins that order with a plant.
- **Step 4 has no `head_sha` test.** A later green run at the red's own `head_sha` already read `external` at step 3, so the note's "at a later sha" is implied, and the clause was an unkillable mutant. With a null `head_sha` on both runs, a later green of the same pull request reads `#<pr>`.
- **`runs.json` projection, as the note asks, by building the narrow rows first** and widening a copy, in place of projecting keys out of the wide row.

## Head

`3fe03e1480a1149d529b46373a7ba275ac47681b` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

prepr: passed rc=0 at 921ce1748771a804f0ad28c75b926f2aa0f9ba09

921ce1748771a804f0ad28c75b926f2aa0f9ba09, merge base 54cb7211642364d762ba47f42d5f7b8a5953f742, measured 2026-11-17T01:35:36Z with origin/main at 38bf516bdd73f926ee9639ffda7b9ca5163fd50e. `git merge-tree --write-tree origin/main HEAD` exits 0, so main is not merged in.

## Mutation proof

`python3 -I tools/audit/seat/loop_ledger.py --self-test` carries the proof in the tree: its `MUTANTS` table holds one exact one-occurrence swap per predicate of the read, each run on a copy of the file, and the self-test fails on a survivor or a needle that no longer occurs once. The design's five targets, each with the check that fails:

- the clearing-event match: `later attempt` (`reds: a gate red at attempt 1 and green at attempt 2 ...`), `clearing run later`, `clearing run green`, `clearing run same head`, `own commit, any pull request` (`reds: another pull request's green clears nothing`);
- the cause call: `cause call`, `and not roster_lib.is_cause(word, ())` to `and False` (`reds: a derived word the cause test refuses reads unread, never the word`);
- the sibling-sha key: `pr key from head_branch`, the sibling looked up by `head_branch` (`reds: a reused head_branch never lends a later pull request's number to an earlier red`); `pr key without sibling` (`reds: a red naming no pull request takes the one a run at its head_sha names`);
- the `pr` extraction and the `runs.json` projection, in `round_metrics_selftest.py`'s `MUTANTS`: `producer first pull request` (the last listed number in place of the first) and `producer narrow runs.json` (the wide rows filtered into `runs.json`), killed by `producer: ci_runs.json keeps ...` and `producer: a runs.json row holds exactly id, t, c and attempt`.

The runner's own null control: the unmutated copy run by the same command exits 0 with no `FAIL` line, so a kill is the mutant's.

`roster_lib.is_cause`, by hand (one `sed` swap, the two self-tests run, the file restored):
- the `#<n>` pattern dropped (`isinstance(cause, str)` alone): `FAIL  reds: a derived word the cause test refuses reads unread, never the word`;
- `cause in CAUSES or` dropped: `FAIL  a fully recorded roster reads every line`, and one more;
- the roster-group arm dropped: `roster_edit.py --self-test` prints `FAIL set-field caused_by is refused with no root-cause record of the group, and read back with its own`;
- `and cause != me` dropped: survived both self-tests at the merge base's text too; now `FAIL  is_cause: a pull request, external, original or another roster group; never the group itself or a bare word`.

Failing test first: with the two producer checks added and `fetch_runs` unchanged, `round_metrics.py --self-test` ended `FAIL producer: ci_runs.json keeps head_sha, event, head_branch and the first pull request's number; producer: a run listed with no head_sha and no pull request keeps both null`.

## Unpinned sites

`prepr.sh`'s draw (`MUTANT_CMD="sh -c 'python3 -I tools/audit/seat/loop_ledger.py --self-test --no-mutants >/dev/null'"`, the first 40 mutants of the added lines) left six at f893e2a228. Two are killed since: `or 0` to `or 1` in `_gates` (`reds: a gate job listed with no attempt is the run's first`), and the deleted `sys.path.insert` before `import gate`, which the self-test's own insert masked and which now ends the self-test with `ModuleNotFoundError: No module named 'gate'`. The other four are equivalent, each named by its text in `gate_reds`:

- `CMP_BOUND` `k > attempt and c == "success"` to `k >= attempt`: the attempt's own conclusion is `failure`, so the equal case never holds.
- `CMP_BOUND` `_when(m) <= _when(r)` to `<` in `before`: `_when` ends in the run id, so two runs are equal only when they are one run, and this arm is a head row's, never a main run's.
- `CMP_BOUND` `_when(x) > _when(r)` to `>=` in `later`: the equal case is the red's own run, which is green only when a later attempt went green, and step 1 has returned by then.
- `CONST_SWAP` `sys.path.insert(0, ...)` to `insert(1, ...)`: `tools/ci` is the only path entry holding `gate`, so either position imports it.

## Null control

- A green-only directory prints `gate_reds 0 (main 0, heads 0) caused {}; cause unread 0; uncleared 0; ...` and no row (the card's null control: a successful run carries no cause and reads as before). No `--runs` prints `gate_reds unread (no --runs directory)`; a directory with no `ci_runs.json` prints `gate_reds unread`. Each is a self-test check (`NULL reds: ...`).
- The reads that share the inputs pass unedited: no existing check of `round_metrics_selftest.py` or of `loop_ledger.py`'s self-test changed text (`git diff 54cb721164 HEAD -- tools/audit/seat/round_metrics_selftest.py tools/audit/seat/loop_ledger.py | grep -c '^-.*check(\|^-.*r\["'` prints 0); two fixture lines are edited: the fake listing's second run gains `head_sha` and `pull_requests`, and the throwaway repository's commits take a merge subject.
- A red run prints its row: every `reds:` check plants one.

## Figures

<!-- figure-block: scope-line mb=38bf516bdd73f926ee9639ffda7b9ca5163fd50e head=3fe03e1480a1149d529b46373a7ba275ac47681b -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- Self-tests at the head: `python3 -I tools/audit/seat/loop_ledger.py --self-test` ends `loop_ledger self-test: 0 failed`; its `ok` lines counted by `grep -c '^ok'`, the mutants among them by `grep -c '^ok    mutant killed'`. `python3 -I tools/audit/seat/round_metrics.py --self-test` ends `round_metrics self-test: ok (with mutants)`. `python3 -I tools/audit/seat/roster_edit.py --self-test` and `python3 -I tools/audit/seat/scorecard.py --self-test` end with 0 failed and `ok (with mutants)`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` (the one script `scope.run` names): ends `ALL 2723 ENTITY CHECKS PASSED` at the head.
- No live read was taken. The read's input is `round_metrics.py produce`'s directory, which this seat cannot fill: the session has no Actions API access. `python3 -I tools/audit/seat/loop_ledger.py --repo .` at the head ends `gate_reds unread (no --runs directory)`. The first live figure is the beat's, from `<state>/scorecard`.
- Part C's edge is open: `git ls-remote origin 'refs/heads/*token-ledger*'` prints nothing, and `git grep -c nested_memory origin/main -- tools` prints nothing (no reader of the session lines C counts loads from).
- The column's function is absent at the merge base: `git grep -n -E '^def status|^MACHINERY_JOBS' 54cb721164 -- tools/ci/gate.py` prints nothing; the same grep over `git show origin/handoff/r11-pre-toolchain-pin-p2:tools/ci/gate.py` (a2c094d8c0) prints both.
- [d-p2-head]: the cause test read at the merge base is `convergence_why`'s `if not (cause in CAUSES or ...)` line, the text part 2 merged (#3657, merge 2c911234e1). `handoff/r11-pre-round-metrics-p2` e3f232aa84 is past that merge and does not touch it: `git diff $(git merge-base HEAD origin/handoff/r11-pre-round-metrics-p2) origin/handoff/r11-pre-round-metrics-p2 -- tools/audit/seat/roster_lib.py | grep -c -E '^[-+].*(CAUSES|cause in|def convergence_why)'` prints 0.
- [d-hotfile-enumerator] at this merge base: for each `refs/remotes/origin/handoff/*` ref with a merge base, `git diff --name-only <merge base> <ref>` filtered on `round_metrics|loop_ledger|roster_lib|tools/ci/gate.py` prints five refs: `r11-pre-plan-render` 11e9a4e964, `r11-pre-round-check-gate-p2` 2cb653f2dd and `r11-pre-round-metrics-p2` e3f232aa84 (`roster_lib.py`; the last also `instruments/loop_ledger.py.md`), `r11-pre-security-privacy` 75b8f26b4c and `r11-pre-toolchain-pin-p2` a2c094d8c0 (`tools/ci/gate.py`, which this diff does not change). `git merge-tree --write-tree HEAD <ref>` exits 0 for the first three; for `r11-pre-toolchain-pin-p2` it exits 1 on `.github/workflows/governance.yml`, as `git merge-tree --write-tree origin/main <ref>` does, so the conflict is that branch's with main.
- `python3 tools/audit/archscore/score.py --diff 54cb721164 HEAD` prints `Architecture score: dS +0.0000 NULL`. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- `tools/ci/selftest_closures.json`: the `loop-ledger` step gains `tools/audit/seat/round_metrics.py`, `tools/ci/gate.py`, `tools/ci/ghapi.py`, `tools/ci/prelude.py` and `dev/audit/rca/R10-N-log-flood.md`, measured by `python3 -I tools/ci/selftest_scope.py record --step loop-ledger`; the recorder's changes to six other steps are not taken. `python3 -I tools/ci/selftest_scope.py select --change M:tools/ci/gate.py` names `loop-ledger` at the head and not at the merge base.
- No file is added, so nothing new is classified; no golden moves and neither claim file is touched.

## Red checks

none

## Forward-carry

- Carry 0 (part D built in this handoff, with the verdict's notes runs-json-width, d-hotfile-enumerator and branch-reuse and the design note's [d-p2-head]; part C not built): part C of the approved design is unbuilt (the load count per rule, an instrument's refusal with its outcome, a run line per workflow script), with the design note's fixer notes [paths], [P1] and [c-deferred]: the orchestrator dispatches it once R11-PRE-TOKEN-LEDGER is on main with an importable per-session iterator that also yields each session's subagent transcript files. [paths] is owed with it: E11-N-GATE-CAUSE's `paths` in `dev/audit/yardstick/round11/EVALUATION.json` become `tools/audit/seat/roster_lib.py`, `tools/audit/seat/loop_ledger.py` and `tools/audit/seat/round_metrics.py` in place of `tools/ci/gate.py`, plus C's file, written before the card is recorded merged; this pull request does not write them, because the card is whole only with C's run line. Lands in R11-PRE-TOKEN-LEDGER's row of the round-11 roster on handoff/audit-r10-roster, the group whose merge opens part C; this group's own row is at stage carries-open and takes no carry. Carry: R11-PRE-TOKEN-LEDGER
- Item d-toolchain-p2-column: once `gate.status` is on main (R11-PRE-TOOLCHAIN-PIN part 2, `handoff/r11-pre-toolchain-pin-p2`), the row's `product/machinery unread` becomes that function's pair over the attempt's jobs, in `loop_ledger.red_lines`. `status` takes an event class (`push`, `no-pr`, `pr`, `pr-cc`), and `pr-cc` is not derivable from a cached run row: whoever wires it decides whether the run's title supplies it. Control: the self-test check `reds: a red attempt's failed jobs split as gate.machinery_line splits them, per attempt; the column unread` pins today's text and fails when the column changes. Lands in R11-PRE-PARALLEL-PIPELINE's row of that roster, the live group the dispatch names as this group's consumer (it holds `tools/ci/gate.py`). Carry: R11-PRE-PARALLEL-PIPELINE
- The four departures above await the orchestrator's ruling; lands in R11-PRE-PARALLEL-PIPELINE's row of that roster, the surface being `tools/audit/seat/loop_ledger.py`. Carry: R11-PRE-PARALLEL-PIPELINE
- A limit of the design's rule, measured by reading `.github/workflows/ci.yml`'s triggers: a `pull_request` `edited` or `labeled` event and a `pull_request_review` event each start a run at the unchanged `head_sha`, so a red cleared by a body edit or a review at the same head reads `external`, as a re-run does. The instrument page says so. Splitting the two needs the run's kind, which the run listing the producer caches does not keep (it is in the run's `display_title`). Lands in R11-PRE-PARALLEL-PIPELINE's row of that roster, the live group the dispatch names as this group's consumer (it holds `tools/ci/gate.py`). Carry: R11-PRE-PARALLEL-PIPELINE

## Friction

- gate-scoping.md: cost: `python3 -I tools/ci/selftest_scope.py record --step loop-ledger` rewrote six steps it was not asked to record (`open-pr`, `policy-lint-mutants`, `pr-args`, `push-names-the-host`, `temp-or-machine-path`, `update-pr`), deleting ignore entries; the wanted step was copied out by hand. The second sighting in this group: #3683's body records the same for `--step review-strength-enumerator`. Carry: dismissed: no live roster group owns `tools/ci/selftest_scope.py`; left for the round-end proposal triage
