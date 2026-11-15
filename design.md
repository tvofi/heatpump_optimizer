# R11-PRE-SHARED-FILES: a pull request carries its own measurement; the shared tables are folded after merge

Designer round 2, answering `Design review: revise 281e74a24e6844ad40a96110d1e85889a826b05f architecture-unsound` (design-verdict/R11-PRE-SHARED-FILES at a8bf24be448babb1875eb0d9c4ca1d0afd57941d). Code read at the base b3831ff64eca1936f0b618193ee86c3e337b51a9 (origin/main); the group has no `after`, so there is no predecessor head. Brief read from the roster branch handoff/audit-r10-roster at 032023814b92837747f1d1a4f7d7fa33cdddb000, `dev/programme/rosters/wave-r11-groups.json`: 11 carries there (0-10), two more than the payload's snapshot. Triage `dev/programme/triage/r10-round-end.md` P748, P774, P781; evidence `dev/audit/rounds/round10/process-convergence-audit.md` at d5d7ff81878fe9bc17ee6fcc9e3803d848cbc7f7, section 4 row 5 and section 6 row b1; `dev/audit/rca/R10-RCA-FAMILY-SELFTEST-SCOPE-DRIFT.md`, `dev/audit/rca/R10-RCA-FAMILY-FIGURE-BLOCK-STALE.md`; `dev/governance/dimensions/D7.md` methods 1 and 8. No finder harness: the evidence is the audit's instrument, `tools/audit/seat/flow_metrics.py`. The note is over two pages: R3 asks for every reader by name, and precision outranks the page bound.

**Where each revise point is answered:** R1 section 3 M2 and section 6; R2 section 3 "the window" and G4; R3 section 2; R4 section 5; R5 section 7's carry table. D1-D4 are routed in section 7.

## Figures

Window W = the newest 200 first-parent commits of main at the base (`git log --first-parent -200 --format=%H origin/main`). Literals are snapshots; re-measure at your merge base.

| id | figure | literal | enumerator |
|---|---|---|---|
| F1 | merges in W touching each file | closures table 42; features script 35; self-test table 22; `tests/entities.py` 18; D6 register 17; structure budgets 14; claim file 11; instruments index 10; sweep template 8; `tests/closure.py` 6 | `git log --first-parent --format=%H <oldest of W>^..origin/main -- <path>` piped to `wc -l` |
| F2 | bot commits inside the branches W merged, by subject, and merges carrying one | re-record closures 3 in 3; merge main 23 in 14; pin killed mutants 33 in 23; drop inherited claims 0 | `git log --format=%s <merge>^1..<merge>^2` per merge of W, grepped for the `ci:` subject |
| F3 | the audit's figure this group is judged by | mean 3.61 over 835 | `flow_metrics.py --window 2026-10-14T13:27Z..2026-11-13T18:00Z`, line "main absorbs per fix branch" |
| F4 | features script: lines; top-level section calls; recorded seconds | 92325; 238; 1040.5 | `wc -l tests/features.py`; `grep -c '^R.section(' tests/features.py`; the `recorded` entry of `tests/closures.json` |
| F5 | mutation-ledger files whose kill names the features script | not measured here | `grep -rl '"killed_by": "tests/features.py"' tests/mutation_ledger` piped to `wc -l` |
| F6 | one structure measurement, wall | 15 s | `time python3 tests/structure.py` |

F2-F4 and F6 were measured at 26dbf7c43e, two commits behind the base (the difference is `tests/requirements-typing.txt`); the reviewer re-measured F1 equal at the base and this round added its three new rows there.

## 1. Finding

Tracked files that are measurements of the tree are edited by every fix branch at the same lines: the closures table and the structure budgets (both need the `ledgermerge` driver of `.gitattributes`, so GitHub, which has no driver, reports the head unmergeable and `tools/pr/merge_main_bot.py` moves it: F2's 23), the instruments index, the D6 claim register (count rows), and the features script (every new block lands before its closing `sys.exit`). At most 3 of F1's 42 table merges carry an autofix commit; seats made the rest before the handoff. The two refusing rules read these files: rule 1 through `tests/closure.py` (`select`, `check`'s UNDER-SCOPED, `orphan_files`); rule 2 through `tests/structure.py`'s `ratchet`, which returns 2 on an improvement not yet recorded (`improvement_rows`), forcing the edit into the pull request.

**The limit of this group.** The pipeline design (design/R11-PRE-PARALLEL-PIPELINE at 22fdbabafb30647a27332d6096df1feb02fc8fb7) measured that 83 % of merges of main into a branch conflict nowhere; its day 1 stops those, whoever made them. This group removes the conflicts that remain. F3's target (b1: at most 2) is joint; this group's own claim is section 6's last item. decision: orchestrator.

## 2. Owning seams, and every reader and writer with its disposition

One owner per artifact; none is product code. The registry (last row) holds path and generate command only and computes nothing (D7 method 8: it is a list of owners, not a second implementation; `tools/audit/archscore/` before and after part 2).

| artifact | owner |
|---|---|
| closures table and its fragments | `tests/closure.py` |
| structure budgets | `tests/structure.py` |
| instruments index | `tools/audit/seat/selftest_wiring.py` (`index_gaps`) |
| self-test table and its fragments | `tools/ci/selftest_scope.py` |
| D6 claim register | `dev/audit/rounds/round4/D6/claims.py`; checked by `tests/harness_headers.py` |
| figure blocks | `tools/pr/figure_block.py` |
| which commits leave a body's `## Head` valid | `tools/audit/seat/review_carry.py` |
| line pins | `tools/policy/brief_lint.mjs` (`checkPathLine`) |
| claim stamp line | `tools/release/stamp.py` (`rewrite_claims`); merge rule in `tests/env_drift.py` |
| the fold | one new module under `tools/ci/`, called by the `record-autofix` job of `.github/workflows/nightly.yml` |

**The loader's two faces.** A function in `closure.py` returns the effective table (table plus fragments, less paths no longer tracked) for the working tree or for a revision (blobs by `git ls-tree` and `git show`, the way `base_closures` reads the table today); a subcommand prints the same as JSON for a caller that cannot import it.

**Closures: readers.**
- *Through the function:* `closure.py`'s own `select`, `check`, `orphan_files`, `affected`; `tests/entities.py:17012` and its sibling reads of the `closures` map; `tests/lane_skip.py:169`; `tests/gate_lock.py:983` (`recorded` seconds); `tests/mutation_table.py:107` (entries, and `recorded` at :3341); `tools/pr/ci_predict.py:1136` and :1203; `tools/ci/prelude.py:89` (the script-name set: a fragment may add a script); the embedded Python of `tools/pr/prepr.sh:1304` and :2881 and of `tools/audit/prepare_baseline.sh:42`.
- *Through the function at a revision:* `tools/audit/seat/merge_train.py:4165` (base and merged sha; it already holds the module for `unit_of`).
- *Through the subcommand:* `tests/card_browser.mjs:1542` (at HEAD), `tools/policy/counts.mjs:122` (the script count keeps its meaning only through the loader).
- *Reads the table file itself, unchanged:* `tests/entities.py:1058` (its comment key); `tools/merge/ledger_merge.py:95` (the driver entry stays; with the fold as the table's one writer it no longer fires).
- *Names the path, moves to the unit:* `tools/policy/policy_lint.mjs:6753` (what a re-record commit may touch becomes the branch's fragment), `.github/workflows/tests.yml:2465` (the autofix adds its fragment), `tools/audit/seat/bus.sh:2421` (copies table and fragments), `tools/audit/seat/merge_train.py:1151`, `tools/pr/outside.py:210`, `tools/pr/app_approve.sh:251`.
- *Dated harnesses under `dev/audit/harnesses/` (`r10_ci_slim`, `r10_rca_ci_critpath_3`):* history; they read the table alone and stay.

**Closures: writers.** `write_closures` stays the only write call and gains its target.
- *Write the branch's fragment:* `merge` under `--partial` (`tests/derive_closures.sh:193`), `apply_under_scoped_recordings` (the `closures-autofix` job), `ci_predict.py:1181` (the inert-reads apply).
- *Fold-only, refused elsewhere by G1:* `merge` without `--partial` (`derive_closures.sh:251`, the Linux full derive), `prune` (:1869, how the fold drops PHANTOM), `canonical` (:1970).
- *Writes nothing:* `proof_consume` (:2860); unchanged.

**Budgets: readers.** `tools/policy/budget_raise_gate.py:176` compares base and head values, unchanged (the fold only lowers). `tools/policy/brief_lint.mjs:463` (key names, and values to refuse a literal), `tools/policy/counts.mjs:120` (key count) and `tools/policy/field_coverage.mjs:534` (key names) read the file and keep their meaning: the file stays a cap per key and its key set still changes only with `structure.py`. `tools/pr/prepr.sh:2252`, `tools/audit/seat/merge_train.py:1334` and `tools/audit/seat/orchestrator_tick.py:4144` are fixtures. `tests/entities.py:35305` runs the real `ratchet` over a shifted copy: it must drive both the pull-request and the push rule of section 3. `tests/features.py:42562` drives `record_budgets` on a throwaway table: unchanged, and `--record` becomes fold-only. The `structure-ratchet` instrument of `tools/pr/figure_registry.json` accepts exit 0 and 1: exit 2 no longer occurs on a pull request. `ledger_merge.py:94`: as for the table. `.github/workflows/governance.yml:1756` and `.github/workflows/arch-score.yml` run the base's `structure.py`: the p1/p2 cut.

## 3. The shape: three mechanisms, chosen per artifact by what regeneration costs

**M1, derive at read time (the source is already in the tree).**
- *Instruments index.* The owner gains one function returning the index from the entry files under `tools/audit/seat/instruments/`; `tools/policy/role_pack.py` (`named_entries`), `tools/audit/seat/roster_edit.py` (`INDEX_FILES`) and `tools/audit/seat/hooks/liveness.py` take it from there. `tools/audit/seat/INSTRUMENTS.md` keeps its prose header; the list is a generated file for human readers. `index_gaps` keeps refusing an entry outside the grammar and a duplicate name.
- *Figure blocks.* The body stores no rendered block. `pr-contract`'s step renders the registered instruments at the merge base and the head into its job summary; `figure_block.py verify` and `figureBlockProblems` refuse a body that still carries a typed or stored block; `open_pr.sh`, `update_pr.sh` and `body_push.sh` stop calling `refresh` (`prepr.sh:263` calls `verify` and keeps it). No head-mover rewrites a body.
- *Carry 3, the scope line.* `run_instrument` checks the base's `tests/closure.py` out over the head's worktree, and `changed_files` adds `git diff HEAD`, so the overlay is counted as the branch's change to a gate file. The render runs the pinned program from outside the head's worktree (the pinned-copy precedent of `tests.yml:2393-2404`), so the tree `select` diffs is clean.
- *`## Head`.* `checkPrBody` already passes a head reached from the named sha by autofix commits (`autofixChain`). The accepted chain becomes "no branch-authored commit since", the rule `review_carry.py` owns (CARRY); `pr-contract` hands `checkPrBody` that instrument's answer, so a merge of main by the bot or a recarry needs no body edit, and `app_push.sh`'s `head_note.py` prefix becomes unnecessary. One rule, one owner (D7 method 8).
- *Structure budgets.* `ratchet` resolves the merge base of HEAD with origin/main itself, as `recorded_at_sha` already asks git; it refuses when that cannot be resolved. **On a pull request** (merge base is not HEAD) the ceiling for a key is the head's budget if the head raised it above the base's (`budget-raise-gate`, unchanged), otherwise the smaller of the base's budget and the value measured on the merge-base tree with the running copy's counting rules (F6: one more measurement). An improvement is no longer exit 2. **On a push to main** (merge base is HEAD) the ceiling is the file's value and a gain is a printed line naming what the fold will record. #350's gap cannot open: the pull-request ceiling is what main measures, not what the file says.
- *D6 register.* `harness_headers.py` regenerates on a copy and, on a pull request, refuses a claim whose verdict differs from the committed one, not a count row that moved; `dirty_registers` applies at the record pull request's head only.

**M2, a per-branch fragment (the measurement is expensive and only the branch has it).**
- *Closures.* A branch writes its delta (added reads per script, `recorded` entries, `inert_reads`) to one file of its own, named for its topic, in a fragment directory under `tests/`. Fragments have unique names: no driver, no conflict, on GitHub too. Where two sources set `recorded` for one script the loader and the fold take the larger (the driver's rule). A fragment only adds; narrowing happens in the fold (`prune`).
- **How a fragment is classified (R1).** `UNIT_DIRS` (`closure.py:455`) becomes a map from a directory to the closure entry its files count as, and the fragment directory maps to `CLOSURES_REL`: a fragment is part of the table. Three consequences, no new list:
  1. `orphan_files` passes it by `unit_of(f) in covered`, as it passes a ledger row. It is neither INERT nor a new closure entry, and a recorded open of a fragment is recorded as the table.
  2. `select` asks `is_gate_file` and the `known` test of the unit, so a fragment gets the table's exemption at `closure.py:3147-3153`, and `known` is built from the loader, so a new file a fragment names is not unmapped.
  3. `moved` becomes: for a diff touching any path of the unit, the scripts whose effective entry differs between the loader at the merge base and the loader at the head. `select` runs those plus every script whose closure lists the table, as today.
  So an added or edited fragment selects the scripts whose reads it changes and the table's readers; the fold's commit (fragments deleted, table grown by the same reads) moves no entry and selects the readers only; a fragment deleted alone is a shrink and selects its scripts.
- *Self-test table (after part 1).* The same mechanism in `selftest_scope.py`: a seat-side record writes the branch's fragment; `check` and `prelude.py`'s selection read table plus fragments. Where the fragments and the table live is D1.

**M3, fold after merge, through the route part 1 uses.** The `record-autofix` job runs the registry: fold fragments into the table and delete them, record the budgets at main (never upward), write the index list and the D6 register, re-pin moved line pins, union the self-test table with the run's `selftest-closures` artifact. Any difference joins its one commit on `record/autofix`. `automerge_refusals` of `tools/audit/seat/record_row.py` admits, beside a delivery row, a registry path whose content at the head equals the owner's regeneration there (D2).

```
seat: single-script record ──> own fragment ──> PR (table, budgets, index, register untouched) ──> gate reads table+fragments; ratchet vs merge-base tree
merge ──> main's forced full run (same loader, push rule) ──> record-autofix: registry fold ──> record PR (generated-only diff, verified by regeneration) ──> main
```

**The window between a merge and its fold: what main's push run compares (R2).**

| artifact | main's push run | red in the window? |
|---|---|---|
| closures | reads against the loader (table plus unfolded fragments); never table against fold | no |
| budgets | measured at most the file's value; a gain is a line | no |
| index, D6 register | entry grammar; claim verdicts; never the generated bytes | no |
| line pins | a moved pin with one resolvable anchor is a warning | no |
| self-test table | the drift step, as ruled for part 1: red on a read no pull-request run could see, until the bot's commit | yes, by the ruling; M2 removes the cases a seat can see |

**Invariants.** G1: no fix branch's diff touches a generated artifact. Two exceptions, each verified: a budget raise (its gate), and a budget key added or removed in a diff that also changes `tests/structure.py`, whose value must equal the head's measurement. G2: the scoped gate selects from table plus every fragment reachable from the merge base, so a merged delta binds the next branch with no window. G3: no metric rises against the merge-base tree without an owner-gated raise. G4: at the record pull request's head, each regenerable artifact equals its owner's output at that head (M3's check); main's push run asserts only the table above.

**The other L9 artifacts.**
- *Line pins:* `brief_lint.mjs` gains a re-pin mode rewriting a `path:line` whose anchor resolves at exactly one other place in the cited file; M3 runs it. In a pull request such a pin is a warning naming the new line, an error only when the anchor is gone or ambiguous. This touches `dev/governance/rules/brief-citations.md`. decision: owner.
- *Claim stamp line:* a branch never writes it. `merge_claim_decision` stops refusing differing stamps when only main's side moved the stamp and emptied the list: the result is main's stamp and reason block plus the claim lines the branch added over the ancestor; a scenario both sides rewrote is still refused (`merge_marker_decision` unchanged). `merge_main_bot.py` then resolves a post-stamp head without a hand merge.

**Features script.** Split into one script per production module under `tests/`, plus one shared helper module (one definition; the no-copies check stays green), by a committed, re-runnable splitter under `dev/audit/harnesses/`: a block is the text between consecutive section calls; its script is the production module its names resolve to most often (ties to the earlier name); earlier top-level statements a block reads follow it. Each script has its own `Results` and close, a line in `tests/run.sh` and a measured closure; `DRIVEN_BY_OTHERS` names the script that drives `dst_checks.py`; `tools/audit/seat/features_block.py` takes the script as an argument. The splitter rewrites F5's ledger entries to the killing script.

## 4. Alternatives, and why each lost in terms of the code

- **Closures by overlay: no file in the branch, main's run records and a bot pushes.** Main's run of the merge commit reads an unfolded table, so `check` and `orphan_files` go red on every delta merge or need a freshness stamp in three readers; the next branch selects from a stale table; and it needs a write to main per delta merge (F1: 42 of 200), each a forced full run.
- **Fragments on `INERT`.** `select` would run nothing for a fragment that adds or drops a read; the `moved` rule exists because a shrink is how a dependency is hidden.
- **Fragments as a closure entry of their own.** Every table reader's closure would need the new entry recorded before the first fragment lands, and `select` would hold two exemptions for one table.
- **Every head-mover re-renders the body.** Five writers (three bots, the recarry, the seat), each needing the body and a token; M1 has one renderer and no stored state. The same reason loses "the merge-main bot re-heads `## Head`".
- **Claim stamp: `update_pr.sh` merges main into the handoff tip first (PC-1113-18's first shape).** It repairs one of three callers; the bot and a hand merge still meet the refusal. The driver rule serves all three.
- **Self-test table: refuse `record` while a merge driver is configured (carry 2's second arm).** The session-start hook installs the drivers in every seat, so every seat would be refused; a scratch clone reads as CI's checkout does.
- **Keep the improvement refusal and add a merge driver on GitHub's side.** There is none to add; the `recorded_at` line alone conflicts between two re-recording branches.
- **Claims as per-branch fragments too.** It removes the `claimnotes` driver, but rewrites rule 3's files, which no finding here names. A proposal. decision: owner.
- **Features: freeze the script and move blocks as they are touched.** Every later move conflicts with the open branches touching it (F1: 35 of 200).

## 5. Sibling sites

- Files with a merge driver, `grep -n 'merge=' .gitattributes`: the two claim files (stamp line), the structure budgets and the closures table (covered), `tests/mutation_budgets.json` (no merge in W touched it: out), `dev/audit/config/bugclasses.json` (appended by root-cause pull requests; note n4).
- Generated registers checked byte for byte, `grep -l 'live-header' dev/audit/rounds/*/D6/*.py`: `dev/audit/rounds/round4/D6/claims.json` and `claims.md` are the live pair (F1: 17, above the budgets). Two branches that each add a documentation link merge clean and leave the count wrong on main. Covered: a registry row, regenerated by M3 (0.2 s for the copy, per `prepr.sh:315`), verdict-only on a pull request. The copies under rounds 3, 9 and 10 are history.
- Budget files, `git ls-files '*_budgets.json'`: only the structure file forces a lowering edit; the others keep one-sided caps (`dev/governance/rules/ratchet-budgets.md`).
- `tests/entities.py` (F1: 18) stays: hand-written checks, not a measurement, and the ruling names the features script alone; section 6's census reports its conflicts after part 4, and a split is proposed only on that figure.
- `tools/audit/seat/sweep_template.md` (F1: 8) stays: hand-written prompt text whose steps are single long lines; nothing can generate it, and reflowing it is not this group's.
- Names of the features script, `git grep -l 'features\.py' -- . ':!tests/mutation_ledger' ':!tests/features.py'`: live code and workflows are rewritten; dated records under `dev/audit/rounds/` stay.
- Body fields naming the head, `grep -n 'head=' tools/policy/policy_lint.mjs`: the figure block's and `## Head`; both covered by M1.
- Bot head moves not caused by these files: the mutation pin bot (F2's largest row); note n3.

## 6. Evidence, by file

- `tests/closure.py` self-test and `tests/entities.py`:
  - failing first, two branches that each add a read to one script conflict in the table under a driver-free merge; with fragments they merge clean and `select` on a third branch picks the script for either file. Null: with a fragment removed, `check` prints UNDER-SCOPED.
  - R1, failing first at the base: a branch whose only gate-file change is its fragment prints `MODE: FULL` and fails the classification check; then `MODE: SCOPED`. Null: a fragment that adds a read to script S selects S. Also: the fold's commit selects the table's readers only; a fragment at the merge base and absent at the head selects its scripts.
  - Mutation targets: the loader's union and its revision arm, the untracked-path filter, the unit map's fragment row, the `moved` comparison, the fold's delete.
- `tests/structure.py` self-test: failing first, a tree improved on main and not recorded lets a branch spend the headroom; then refused against the merge-base measurement. R2: on the push rule a tree with an unrecorded gain passes and prints the gain; null: a measurement above the file's value refuses on both rules. Nulls: an owner-raised key passes; an unresolvable origin/main refuses. Mutation targets: the ceiling's minimum, the raise arm, the merge-base-is-HEAD branch.
- Registry self-test and `nightly.yml`: the record pull request refused when a generated file is hand-edited, admitted when it equals regeneration; R2: a main tree holding an unfolded fragment, an unlisted index entry and a moved count row passes the push run. Null: a push with no delta writes nothing.
- Part 1: the job red on a planted unrecorded read and green after the bot commit; null: a green push writes nothing. Carry 1: `prepr.sh` red on a planted read in a gated step whose script the diff touches, printing its skip where strace is missing. Carry 2: a clone with a merge driver configured records the same read set as one without. The analysis is cited from `bugclasses.json` (both RCA files: neither is cited at the base).
- `tools/pr/figure_block.py` self-test: a head moved by a merge of main fails `verify` today and passes with no stored block; null: a typed figure is refused. Carry 3: a branch whose merge base predates a change of `tests/closure.py` on main renders `MODE: SCOPED`; null: a branch that edits that file itself renders `MODE: FULL`.
- `tools/policy/policy_lint.mjs` self-test: `## Head` naming the last branch-authored commit passes under a bot merge of main; null: a branch-authored commit after it is refused; an agreement test against `review_carry.py` over the same chains.
- `tests/env_drift.py` self-test: the post-stamp merge of a claiming branch refuses today and resolves; null: a scenario both sides rewrote still refuses.
- `tests/harness_headers.py`: two branches each adding a link pass alone and after merge, and the fold writes the count; null: a claim that flips to failing is refused on the pull request.
- Features split, a harness under `dev/audit/harnesses/`: the multiset of check names and results over the new scripts equals the old script's at the merge base; re-running the splitter on the base reproduces the committed tree byte for byte; a sample of F5's kills per module still kills. No golden moves; neither claim file is touched.
- The group's claim: over merges after the last part, zero `ci: merge main` commits whose driver-free conflict set lies inside registry paths or the features scripts (F2's enumerator plus the pipeline appendix's absorb census), and F3's line re-run over that window.

## 7. Cost, split, serial position, carries

Larger than L; one merge per part, graders before their use because CI restores the base's copy of a pinned grader (`fixer.md`, the p1/p2 rule):

| part | content | size | after |
|---|---|---|---|
| 1 | self-test table: union record (#3551, absorbed when it lands), the bot re-record, scratch-clone tracing, the `prepr.sh` and `ci_predict.py` check, one item written once | M | none |
| 2 (p1) | graders accept both regimes: the loader and unit map, the two ratchet rules, the index from entries, the register's verdict check, the registry and its check, not yet enforced | M | none |
| 3 (p2) | the switch: fragments from the writers of section 2 (self-test table included), M3 in `record-autofix`, G1 enforced, policy text | M | 1, 2 |
| 4 | features split | L | 3; D3 |
| 5 | figure blocks, `## Head`, carry 3, re-pin, claim stamp rule, with a sweep of open bodies | M | 2; R11-HOTFIX-FIGURE-BLOCK-BASE |

**Carries (roster at 032023814b).**

| carry | where it is built |
|---|---|
| 0, 8, 9 (union record; the bot commits main's artifact by union over the live table at its own head) | part 1 |
| 1 (run the scope check before the handoff when a gated step's script changes) | part 1: `prepr.sh` and `ci_predict.py` trace the gated steps whose recorded files the diff touches and refuse on drift |
| 2 (the recording seat's git config narrows the read set) | part 1: `record` and the local check trace in a scratch clone |
| 3 (scope line `MODE: FULL` from the overlay) | part 5, section 3; re-read the hotfix's merged diff first |
| 4 (class barrier, main-side union) | part 1, with the `bugclasses.json` citation |
| 5 (L9's four artifacts) | parts 1, 3 (table), 5 (blocks, pins, stamp) |
| 6 (stored block; `## Head` at a recarry head) | part 5 |
| 6, stale-checkout half (`train.sh` has no freshness check; `tick_loop.sh:111-143` has one) | Carry: R11-PRE-TOOLCHAIN-PIN (its instrument owns "behind"; `train.sh` and `remerge_main.sh` join `pr_tools_fresh`'s callers) |
| 7 (stamp strands pre-stamp handoffs) | part 5; its aside, a topic `open_driver.py` never listed: Carry: R11-PRE-TOOLCHAIN-PIN |
| 8's aside (`tools/audit/seat/body_push.sh` is mode 100644 at the base) | part 5, which edits that file |
| 10 (`write_table` lists an item twice through `compact_probes`) | part 1 |

**Routed decisions.**
- D1, decision: owner. `/tools/ci/` is code-owned (`.github/CODEOWNERS:113`). Proposed: the self-test table and its fragments live outside that directory and `automerge_refusals` admits the table only as a superset of main's (a union can widen what runs, never narrow it). Otherwise the record pull request splits and the table's half waits for review while main's drift step is red.
- D2, decision: owner. The auto-merge predicate widens from delivery rows to registry paths verified by regeneration, as M3 states it.
- D3, decision: orchestrator. Part 4 goes after design/R11-OUTSIDE-HONEST-STARTS-RUNS and design/R10-START-COUNTER-EDGES, or both are re-anchored after it.
- D4, decision: orchestrator. R11-PRE-TOOLCHAIN-PIN (design at 5caeadfa90) adds instruments, table entries and edits `governance.yml`, `open_pr.sh`, `update_pr.sh`. Proposed order: its p1 before part 3; a seat on tools older than part 3 that edits the table meets G1, whose refusal names the fragment command, and its parts record under whichever regime main holds at their merge base.

Hot files: `tests/closure.py`, `tests/structure.py`, `tools/ci/selftest_scope.py`, `tools/pr/prepr.sh`, `tools/policy/policy_lint.mjs`, `.github/workflows/tests.yml`, `nightly.yml`, `governance.yml`, `pr-contract.yml`; `open_pr.sh` and `update_pr.sh` with R11-PRE-PARALLEL-PIPELINE's part 1, R11-PRE-TOOLCHAIN-PIN and the figure-block hotfix; `fixer.md` with R11-PRE-HANDOFF-BOOKKEEPING. Policy the owner reviews before merge: `CLAUDE.md` rules 1 and 2, `gate-scoping.md`, `ci-autofix.md`, `claim-files.md`, `brief-citations.md`, `fixer.md`, the pull-request template's `## Head`, and every workflow path.

## Notes for the fixer

- The fragment name must survive a branch restarted under the same name after its merge: the fold has deleted the old file, so the new one is an add. Test it. Carry: R11-PRE-SHARED-FILES (item n1)
- The splitter's majority rule was not run in the design's time box; if one module script comes out above a quarter of F4's lines, report the distribution before moving anything. decision: orchestrator. Carry: R11-PRE-SHARED-FILES (item n2)
- The mutation pin bot moves more heads than any file here (F2). Carry: R11-PRE-PARALLEL-PIPELINE (item n3)
- `dev/audit/config/bugclasses.json` is the same append-at-one-place class. Carry: R11-PRE-HANDOFF-BOOKKEEPING (item n4)
- `features_block.py` slices on two literal lines of the old script, and its emitted prelude is a run-until-no-NameError loop, not a dependency graph: it does not follow a block that depends on an earlier block's side effects. Section 6's equality harness catches that; report each block moved by a hand-written exception. Carry: R11-PRE-SHARED-FILES (item n6)
- `figureBlockProblems` re-implements the block parse and moves with `verify`. Carry: R11-PRE-SHARED-FILES (item r1)
- `pr-contract` restores `tools/pr/*.py` from the base, so part 5's step may call only what the base's `figure_block.py` has (`render NAME` exists) or takes the p1/p2 cut; `tests/closure.py`, `tests/mutation_table.py` and `tests/env_drift.py` are base-pinned in the three autofix jobs (`tests.yml:2393`, :2666, :2925), which bears on part 4's `DRIVEN_BY_OTHERS` edit and ledger rewrite. Run `ci_predict.py` for `BOOTSTRAP` on every part. Carry: R11-PRE-SHARED-FILES (item r2)
- Once `verify` refuses a stored block, every open pull request whose body carries one goes red at its next run: part 5 lands with the body sweep. Carry: R11-PRE-SHARED-FILES (item r3)
- Only ledger files whose kill field names the features script are rewritten (F5's enumerator); a triage reason is prose. Carry: R11-PRE-SHARED-FILES (item r5)
- An entry file's index line is its line 3 and differs from the index's prose for at least `figure_block.py.md`, `open_pr.sh.md`, `update_pr.sh.md`; the entry file is the source, and the body lists each line that changes. Carry: R11-PRE-SHARED-FILES (item r7)
- The D6 register's `result` text carries the measured count, so the verdict a pull request compares must be a field without it; if the register has none, `claims.py` gains one in part 2. Carry: R11-PRE-SHARED-FILES (item d1)
- The local self-test trace needs strace; where it is missing the step prints its skip (the rc 3 convention of `prepr.sh`'s claims step) and CI's drift step remains the detector. Carry: R11-PRE-SHARED-FILES (item d2)
- A script added with no entry file is outside `index_gaps` today and stays outside it. Carry: dismissed: unchanged by this design (item n5)
