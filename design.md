# Design: R11-PRE-NO-READ-BUILDERS (size L, decision 0014), round 5: parts C and D, re-based

- Base: c82f014a639954b0f8930f29cf30fed3f0b20a6a (`origin/main` at dispatch). Previous note 9edf64948f (base 030a4d377f), approved by `Design review: approve 9edf64948f7522213ca07a313f5121fe4c20a72a` (18fc037aed). This round answers that verdict's three fixer notes: [runs-json-width], [d-hotfile-enumerator], [branch-reuse]. It also re-bases the note and folds in the carry [d-p2-head-text]. Part C is unchanged from 9edf64948f. In part D only the PR-match key and the `runs.json` construction change.
- Parts A and B are on main: #3683 (merge cc2a14d02e). This note no longer designs them. Parts C and D remain unbuilt (carry 4847b00a).
- What moved since 030a4d377f, re-read at the base:
  - R11-PRE-ROUND-METRICS part 2 merged as #3657 (merge 2c911234e1, branch head c1a69f7a02).
  - R11-PRE-TOOLCHAIN-PIN merged as #3645 (merge e352724335).
  - R11-PRE-ROUND-METRICS part 3 is unmerged (`handoff/r11-pre-round-metrics-p3` at a527be6f19).
  - R11-PRE-TOKEN-LEDGER has no fix branch. `git log c82f014a --grep=token-ledger -i` lists only `roster_edit` carry commits.
- Cards re-read in `dev/audit/yardstick/round11/EVALUATION.json` at the base. That is the approved evaluation (`review` approve), landed by 4241fefad0 from eval/r11 c04cef7fca. All four cards are `decision: accepted` with `gates_finders: false`. None is rewritten or dropped.
- Finder harness: none (owner-directed instrument cards). Evidence: each card's `null_control`.

## Parts left, by owning seam

| part | card | owning module | after |
|---|---|---|---|
| C | RULE-YIELD loads; INSTRUMENT-YIELD; GATE-CAUSE's workflow run line | a new session-yield seat instrument under `tools/audit/seat/` (named in the body), importing R11-PRE-TOKEN-LEDGER's per-session iterator | R11-PRE-TOKEN-LEDGER's merge |
| D | GATE-CAUSE (a cause per red run) | `roster_lib.convergence_why`'s cause test and `loop_ledger.py`; `round_metrics.py` `fetch_runs` keeps four more fields | R11-PRE-ROUND-METRICS part 3 merged (part 2 is merged) |

[routed] C and D share no file and dispatch as separate parts, each on its own `after` edge. D's other edge, part 2's merge, and the TOOLCHAIN-PIN column it needed are both satisfied at the base.

### C. Session reads: loads, refusals with outcome, workflow runs
Unchanged from 9edf64948f section C, which the round-4 verdict approved: loads per rule from `nested_memory` lines; refusal by exit status less the structural `usage`, `crash`, `not-run`, `killed` rows and the [c-deferred] `deferred` row; `masked` when the instrument is not the last simple command; `marked at exit 0` as a scope row; outcome `fix`, `override` or `nothing` from the next run; one line per Workflow call; subagent files read beside the sessions read [c-subagent]. The fixer reads that section at 9edf64948f; nothing in it moved. Its cited refusal sites are re-checked at the part's own merge base by the [P1] enumerator.

### D. A cause per red run, in P7's vocabulary
**The record.** `roster_lib.convergence_why` at part 2's merge 2c911234e1 (`tools/audit/seat/roster_lib.py:907`), with `CAUSES` at :856. A red is a run attempt whose `gate` job concluded `failure`. It is read per attempt from `jobs/jobs_<id>.json`, the record `round_metrics.gate_conclusions` (`round_metrics.py:151`) reads at the latest attempt. It counts on a pull-request head or on main's push. Its cause is a word `convergence_why` already admits, derived from the clearing event:
- the PR's own later commit cleared it: `#<that PR>`;
- red at the merge base on main too: `#<n>`, the PR merged at main's first red push run after its last green. That number comes from parsing the merge subject; an unparsed subject gives `unread`.
- a later attempt of the same run id, or another run at the same `head_sha`, went green: `external`.

**The one vocabulary change.** The cause test at `roster_lib.py:934` becomes a function. `convergence_why` and the derived row both call it. A derived row carries no `rca`, is never written to the roster and never feeds `injected`, so the root-cause seat keeps every injected cause. `found_by`: `ci-main` on a main row; absent on a PR-head row, because a pre-merge red is not an escape.

**Change 1, `fetch_runs` (`round_metrics.py:391`).** Each `ci_runs.json` row keeps `head_sha`, `event`, `head_branch` and `pr`, each read with `.get`. `pr` is the first `pull_requests[].number`, or null. The keys `id, t, c, attempt` stay.
- [runs-json-width] Today `main` at :396 filters the same dicts it writes to `ci_runs.json`, so the wide row would reach `runs.json` too. `runs.json` is therefore built from the narrow keys `id, t, c, attempt`, projected before the wide fields are added. `scorecard.py`'s docstring (`tools/audit/seat/scorecard.py:14`) and `instruments/scorecard.py.md` stay true unedited.
- A producer arm pins this: a fake listing carrying all four fields leaves every `runs.json` row with exactly four keys. A mutant that writes the wide dicts fails that arm.
- `round_metrics.py`'s INPUTS docstring line for `ci_runs.json` (:52) and `instruments/round_metrics.py.md` name the four fields.
- `gate_conclusions`, `runner_line` (:216), `restore` and their self-test arms pass unedited.

**Change 2, `loop_ledger.py --runs DIR`.** It reads `ci_runs.json` and `jobs/jobs_<id>.json` and makes no API call.
- [branch-reuse] The PR key of a run is its `pr`. When that is null, the key is the `pr` of another run at the same `head_sha`. When neither exists, the cause is `unread`. `head_branch` is never a PR key: it is used only to pick main push runs (`event == "push"` and `head_branch == "main"`).
- Why: an internal branch name can be reused across PRs, and the round-4 note's `head_branch` fallback would then read a later PR's commit as the earlier red's `#<pr>`. A `head_sha` belongs to one commit, so the sibling-run key cannot cross PRs.
- The limit, stated in the body: a fork run whose `pull_requests[]` is empty at every run of its sha reads `unread`, never a guessed PR.
- A red with no jobs file, or with one cached at an older `attempt` (`runner_line`'s rule at :227), reads `unread` and is never dropped. With no `--runs`, the read prints `unread`. With `--runs` and no red, it prints 0.

**Product/machinery column.** This is R11-PRE-TOOLCHAIN-PIN's `gate.py` function, now on main (#3645), applied to the run's job listing. The fixer cites the function by name at D's merge base. `gate.py` is unchanged by D.

**Lost:** gate.py stamping a cause at run time (the clearing event does not exist yet); new cause words (a second vocabulary); a second run fetcher (two caches of one listing); `head_branch` as a PR key (it crosses PRs on branch reuse; see above); widening `runs.json` and its two docs (it widens scorecard's input for no reader: `scorecard.py` indexes only `id, t, c`).

## Evidence plan (`fixer.md` steps 2-4)
| part | failing test first: a planted event prints its row | null control | mutation target |
|---|---|---|---|
| C | as 9edf64948f's C row, plus the [c-deferred] plants (exit 75; `merge_pr.sh` exit 3 WAIT) reading `deferred` | as 9edf64948f's C row | as 9edf64948f's C row, plus the `deferred` arm |
| D | A `--runs` dir of `ci_runs.json` and `jobs/jobs_<id>.json` fixtures, one plant per case:<br>- red then green at one `head_sha` reads `external`;<br>- one jobs file with `gate` at `run_attempt` 1 `failure` and 2 `success` reads `external`, and the same run with no jobs file reads `unread`;<br>- a red cleared by the same `pr` at a later sha reads `#<pr>`;<br>- a red inherited from main reads main's PR.<br>[branch-reuse]:<br>- two `pull_request` runs share `head_branch`, have null `pr` and belong to different PRs (distinct `head_sha`, no sibling run): the earlier red reads `unread`, not `#<later pr>`;<br>- a null-`pr` red whose `head_sha` has a sibling run with `pr` N, cleared by N's later commit, reads `#N`.<br>Producer arm: four fields kept in `ci_runs.json`; `runs.json` rows have exactly `id, t, c, attempt`. | a green-only dir: reds 0, no cause row; no `--runs`: `unread`; the existing `runner_s`, `product_green`, `restore` and producer arms pass unedited | the clearing-event match; the cause call; the `pr` extraction; the sibling-sha key (a mutant keying on `head_branch` turns the reuse plant into `#<later pr>`); the `runs.json` projection |

No golden moves, and neither claim file is touched.

## Hot files and serial position
- [d-hotfile-enumerator] Re-run at this base with the corrected enumerator. For `design/*`, a ref holding only design.md, the test is `git show <ref>:design.md | grep -E 'round_metrics|fetch_runs|ci_runs'`. For `handoff/*` it is `git diff --name-only $(git merge-base c82f014a <ref>) <ref>`, filtered on `round_metrics|loop_ledger|roster_lib`; a ref with no merge base (the audit-find and plan refs) carries no code.
  - Results over the `design/*` and `handoff/*` refs at the base: `design/R11-ARCH-OBJECTIVE` names `round_metrics.py` only to say it is not imported. `design/R11-PRE-PARALLEL-PIPELINE` names an unrelated harness `fetch_runs.sh`. Neither changes the file. Four handoff refs print a match:
    - `handoff/r11-pre-round-metrics-p3` a527be6f19 changes `round_metrics.py`, its self-test and its instrument page, and touches no `fetch_runs`, `ci_runs` or `run_attempt` line. Order: part 3 first, then D.
    - `handoff/r11-pre-round-metrics-p2` e3f232aa84 is three commits past its merged head c1a69f7a02. They change `rca_subjects` (`roster_lib.py:894`), not the cause test at :934, and no derived row reads rca. If they merge first, D rebases onto them.
    - `handoff/r11-pre-plan-render` a03ff5d77e and `handoff/r11-pre-round-check-gate-p2` 2cb653f2dd add new functions to `roster_lib.py` and leave `convergence_why` untouched. A textual rebase only; no serial edge.
  - The fixer re-runs the enumerator at D's own merge base.
- C's one new file goes into `tests/closures.json` or `tests/closure.py`'s INERT list, and into `.github/CODEOWNERS` as an enumerator. D adds no file.

## Notes for the fixer
- [paths] E11-N-INSTRUMENT-YIELD's `paths` becomes C's new file. E11-N-GATE-CAUSE's `paths` becomes `tools/audit/seat/roster_lib.py`, `tools/audit/seat/loop_ledger.py` and `tools/audit/seat/round_metrics.py` in place of `tools/ci/gate.py`, plus C's file for the run line. Each is written in the evaluation before the card is recorded merged. Carry: R11-PRE-NO-READ-BUILDERS
- [d-p2-head] [d-p2-head-text] Part 2 merged at 2c911234e1 (head c1a69f7a02), and the body cites that merge. If `handoff/r11-pre-round-metrics-p2`'s later commits merge before D, re-read `convergence_why` there before D's failing test. Carry: R11-PRE-NO-READ-BUILDERS
- [P1] Before C's failing test, re-run 9edf64948f's literal enumerator (part C step 2) at the part's merge base. List every literal printed at exit 0 in the body. Carry: R11-PRE-NO-READ-BUILDERS
- [c-deferred] C's `deferred` row covers 75 plus each instrument-declared wait code (`git grep -n -E "WAIT|return 75|exit 75" -- tools .claude/hooks` at the merge base). The body lists the report-by-exit instruments (`postmerge.py`, `mutant_run.py`). Carry: R11-PRE-NO-READ-BUILDERS
- Owed to R11-PRE-TOKEN-LEDGER: the per-session iteration is an importable function that also yields each session's subagent transcript files. Carry: R11-PRE-TOKEN-LEDGER
- Re-derive every count at the part's own merge base; the figures above name their commands only. Carry: R11-PRE-NO-READ-BUILDERS
