# R11-PRE-SHARED-FILES: a pull request carries its own measurement; the shared tables are folded after merge

Designer round 1. Code read at origin/main 26dbf7c43ec3742101398b098dbdcc61bbee8f19 (the base); no predecessor handoff head is on origin for its one `after` group, R10-CATALOG-PR. Brief: `dev/programme/rosters/wave-r10-groups.json`, group R11-PRE-SHARED-FILES; triage `dev/programme/triage/r10-round-end.md` P748, P762, P763, P774, P781; evidence `dev/audit/rounds/round10/process-convergence-audit.md` at d5d7ff81878fe9bc17ee6fcc9e3803d848cbc7f7, section 4 row 5 and section 6 row b1; `dev/audit/rca/R10-RCA-FAMILY-SELFTEST-SCOPE-DRIFT.md`, `dev/audit/rca/R10-RCA-FAMILY-FIGURE-BLOCK-STALE.md`. Sibling design read: design/R11-PRE-PARALLEL-PIPELINE at 22fdbabafb30647a27332d6096df1feb02fc8fb7. No finder harness: the evidence is the audit's instrument, `tools/audit/seat/flow_metrics.py`.

## Figures

Window W = the newest 200 first-parent commits of main at the base (`git log --first-parent -200 --format=%H origin/main`). Literals are snapshots; re-measure at your merge base.

| id | figure | literal | enumerator |
|---|---|---|---|
| F1 | merges in W touching each file | closures table 42; features script 35; self-test table 22; structure budgets 14; claim file 11; instruments index 10; `tests/closure.py` 6 | `git log --first-parent --format=%H <oldest of W>^..origin/main -- <path>` piped to `wc -l` |
| F2 | bot commits inside the branches W merged, by subject, and merges carrying one | re-record closures 3 in 3; merge main 23 in 14; pin killed mutants 33 in 23; drop inherited claims 0 | `git log --format=%s <merge>^1..<merge>^2` per merge of W, grepped for the `ci:` subject |
| F3 | the audit's figure this group is judged by | mean 3.61 over 835 | `flow_metrics.py --window 2026-10-14T13:27Z..2026-11-13T18:00Z`, line "main absorbs per fix branch" |
| F4 | features script: lines; top-level section calls; recorded seconds | 92325; 238; 1040.5 | `wc -l tests/features.py`; `grep -c '^R.section(' tests/features.py`; the `recorded` entry of `tests/closures.json` |
| F5 | mutation-ledger files naming the features script | 3610 | `grep -rl 'features\.py' tests/mutation_ledger` piped to `wc -l` |
| F6 | one structure measurement, wall | 15 s | `time python3 tests/structure.py` |

## 1. Finding

Four tracked files are measurements of the tree that every fix branch edits at the same lines: the closures table and the structure budgets (both need the `ledgermerge` driver of `.gitattributes`, so GitHub, which has no driver, reports the head unmergeable and `tools/pr/merge_main_bot.py` moves it: F2's 23), the instruments index (one line per instrument, added at the same place), and the features script (every new block lands before its closing `sys.exit`). F2's first row says the table edits are not the autofix's: at most 3 of F1's 42 merges carry an autofix commit; seats made the rest before the handoff. The two refusing rules read these files: rule 1 through `tests/closure.py` (`select`, `check`'s UNDER-SCOPED) and `tests/entities.py`'s classification check; rule 2 through `tests/structure.py`'s `ratchet`, which also refuses an improvement not yet recorded (`improvement_rows`), forcing the edit into the pull request.

**The limit of this group, stated before the shape.** The pipeline design measured that 83 % of merges of main into a branch conflict nowhere (its F3) and were made by instruments, which its day 1 stops. This group removes the conflicts that remain. F3's target (b1: at most 2) is therefore joint with R11-PRE-PARALLEL-PIPELINE; this group's own claim is section 7's. decision: orchestrator.

## 2. Owning seams (one owner per artifact; none of them is product code)

| artifact | owner (computes, writes) | callers only |
|---|---|---|
| closures table and its per-branch fragments | `tests/closure.py` | `tests/gate_lock.py`, `tests/lane_skip.py`, `tests/run.sh`, `tools/pr/ci_predict.py`, `tools/pr/prepr.sh`, `tests/entities.py` |
| structure budgets | `tests/structure.py` | `tools/policy/budget_raise_gate.py` (raises only, unchanged) |
| instruments index | `tools/audit/seat/selftest_wiring.py` (`index_gaps`) | `tools/policy/role_pack.py` (`named_entries`), `tools/audit/seat/roster_edit.py` (`INDEX_FILES`), `tools/audit/seat/hooks/liveness.py` |
| self-test table | `tools/ci/selftest_scope.py` | `.github/workflows/governance.yml` |
| figure blocks | `tools/pr/figure_block.py` | `.github/workflows/pr-contract.yml`, `open_pr.sh`, `update_pr.sh`, `body_push.sh`, `prepr.sh` |
| line pins | `tools/policy/brief_lint.mjs` (`checkPathLine`) | the `briefs` job of `.github/workflows/tests.yml` |
| claim stamp line | `tools/release/stamp.py` (`rewrite_claims`); merge rule in `tests/env_drift.py` (`merge_marker_decision`) | `merge_main_bot.py` |
| the fold after merge | one new small module under `tools/ci/` (the generated-artifact registry: path, owner's generate command, whether the check can regenerate it) | the `record-autofix` job of `.github/workflows/nightly.yml` |

The registry computes nothing itself: it calls each owner's command. No concern has two owners.

## 3. The shape: three mechanisms, chosen per artifact by what regeneration costs

**M1, derive at read time (where the source is already in the tree).**
- *Instruments index.* Each entry file under `tools/audit/seat/instruments/` already opens with its index line. The owner gains one function returning the index from the entry files; the three callers take it from there. `tools/audit/seat/INSTRUMENTS.md` keeps its prose header; the list is a generated file beside the entries. `index_gaps` keeps refusing an entry whose opening line is outside the grammar and a duplicate name; "an entry no index line links" cannot occur any more.
- *Figure blocks.* The body stores no rendered block. `pr-contract`'s step renders the registered instruments of `tools/pr/figure_registry.json` at the recorded base and the head into its job summary, and `figure_block.py verify` refuses a body that still carries a typed or stored block. The three seat scripts and `prepr.sh` stop calling `refresh`. A reviewer renders at the head it reviews. This is the RCA's second arm ("or by `pr-contract` itself"), so no head-mover has to rewrite a body.
- *Structure budgets.* On a pull request the ratchet's ceiling for a key is the head's budget if the head raised it above the base's (the raise path, `budget-raise-gate`, unchanged), otherwise the smaller of the base's budget and the value measured on the merge-base tree with the head's own counting rules (F6: one more measurement). An improvement is no longer refused: it is recorded after merge. #350's gap (headroom between a gain and its record) cannot open, because the ceiling is what main measures, not what the file says.

**M2, a per-branch fragment (where the measurement is expensive and only the branch has it).**
- *Closures.* A branch writes its delta (added reads per script, `recorded` entries, `inert_reads`) to one file of its own in a fragment directory beside the table, named for its topic; `derive_closures.sh --single`, `ci_predict.py --apply-inert` and `closures-autofix` (`apply_under_scoped_recordings`) write there instead of the table. One loader in `closure.py` returns table plus fragments, less paths no longer tracked; every reader in section 2 goes through it. Fragments have unique names, so no driver and no conflict, on GitHub too. `select`, UNDER-SCOPED, the INERT pair and the classification check read the loader and refuse exactly as today; main's forced full run reads it too, so the merge's own run is green with no fold yet. PHANTOM is refused in a fragment and pruned from the table by the fold.

**M3, fold after merge, through the route part 1 already uses.** The `record-autofix` job runs the registry: fold fragments into the table and delete them, record the budgets at main, write the index list, re-pin moved line pins, take the self-test table from the run's artifact. Any difference joins its one commit on `record/autofix`, merged as a pull request by the App: no new credential, no bypass. **The refusal that replaces trust in the author:** a diff that touches a generated artifact must touch only registry paths and delivery rows, and each regenerable artifact at its head must equal the owner's output there. A budget raise is the one exception and keeps its gate.

```
seat: single-script record ──> own fragment ──> PR (table, budgets, index untouched) ──> gate reads table+fragments; ratchet vs merge-base tree
merge ──> main's forced full run (same loader: green) ──> record-autofix: registry fold ──> record PR (generated-only diff, verified by regeneration) ──> main
```

**Invariants.** G1: no fix branch's diff touches a generated artifact (raise excepted). G2: the scoped gate selects from table plus every fragment reachable from the merge base, so a merged delta binds the next branch with no window. G3: no metric rises against the merge-base tree without an owner-gated raise. G4: a generated artifact on main equals its owner's output or main's push run refuses.

**The other L9 artifacts.**
- *Self-test table (part 1, ruled, no new design):* `record --step` unions through `union_entries` instead of replacing; on a refused drift step on main the bot lands the uploaded `selftest-closures` artifact through M3. The registry marks it not regenerable in a check.
- *Line pins:* `brief_lint.mjs` gains a re-pin mode that rewrites a `path:line` whose anchor resolves at exactly one other place in the cited file; M3 runs it on the tracked rosters and carries. In a pull request such a pin is a warning naming the new line, an error only when the anchor is gone or ambiguous. This touches `dev/governance/rules/brief-citations.md`. decision: owner.
- *Claim stamp line:* a branch never writes the stamp line. The `claimnotes` driver (`merge_claim_decision`, `merge_marker_decision`) stops refusing "different releases" when only main's side moved the stamp and emptied the list: the result is main's stamp and reason block plus the claim lines the branch itself added over the ancestor; a scenario both sides rewrote is still refused. `merge_main_bot.py` then resolves a post-stamp head without a hand merge (PC-1113-18).

**Features script.** Split into one script per production module under `tests/`, named for the module, plus one shared helper module holding today's header and every helper two scripts read (one definition; `closure.py`'s no-copies check stays green). The split is made by a committed, re-runnable splitter under `dev/audit/harnesses/`, never by hand: a block is the text between consecutive section calls; its script is the production module its names resolve to most often (ties to the earlier module in sorted order); earlier top-level statements a block reads follow it by the dependency walk `tools/audit/seat/features_block.py` already does for its emitted prelude. Each script has its own `Results` and close, a line in `tests/run.sh`, and a measured closure; `DRIVEN_BY_OTHERS` names the script that drives `dst_checks.py`; `features_block.py` takes the script as an argument. The splitter rewrites F5's ledger entries to the killing script.

## 4. Alternatives, and why each lost in terms of the code

- **Closures by overlay: no file in the branch, main's run records and a bot pushes.** Main's own run of the merge commit reads an unfolded table, so `check` and the classification check go red on every delta merge or need a freshness stamp read by three readers; the next branch selects from a stale table until the push lands; and it needs a write path to main per delta merge (F1: 42 of 200), each starting a forced full run. The fragment needs none of the three.
- **Every head-mover re-renders the figure block.** Five writers of a body (three bots, the train's recarry, the seat), each needing the body ref and a token; M1 has one renderer and no stored state.
- **Keep the improvement refusal and add a merge driver on GitHub's side.** There is none to add; the `recorded_at` line alone conflicts between any two re-recording branches.
- **Claims as per-branch fragments too.** It removes the `claimnotes` driver and the inherited-claims class, but rewrites rule 3's files, which no finding here names. Recorded as a proposal. decision: owner.
- **Features: freeze the script and move blocks as they are touched.** Every later move conflicts with the open branches touching it (F1: 35 of 200); the round boundary is the one point with none.

## 5. Sibling sites

- Files with a merge driver, `grep -n 'merge=' .gitattributes`: the two claim files (stamp line above), `tests/structure_budgets.json` and `tests/closures.json` (covered), `tests/mutation_budgets.json` (no merge in W touched it: out of scope), `dev/audit/config/bugclasses.json` (appended by root-cause pull requests: same class, not in the brief; note n4).
- Budget files, `git ls-files '*_budgets.json'`: only the structure file forces a lowering edit into the pull request; the others keep one-sided caps (`dev/governance/rules/ratchet-budgets.md`) and stay as they are.
- Readers of the table, `git grep -n 'closures\.json' -- tests tools .github`: every one moves to the loader or is listed in the pull request as not reading entries.
- Names of the features script, `git grep -l 'features\.py' -- . ':!tests/mutation_ledger' ':!tests/features.py'`: live code and workflows are rewritten; dated records under `dev/audit/rounds/` are history and stay.
- Bot head moves not caused by these files: the mutation pin bot (F2's largest row). Out of scope; note n3.

## 6. Evidence, by file

- `tests/closure.py` self-test and `tests/entities.py`: failing first, two branches that each add a read to one script conflict in the table under a driver-free merge; then, with fragments, they merge clean and `select` on a third branch picks the script for either file. Null: with a fragment removed, `check` prints UNDER-SCOPED as today. Mutation targets: the loader's union, the untracked-path filter, the fold's delete.
- `tests/structure.py` self-test: failing first, a tree improved on main and not recorded lets a branch spend the headroom under today's rule; then it is refused against the merge-base measurement. Nulls: an owner-raised key passes; a branch that changes nothing passes with a stale file. Mutation targets: the ceiling's minimum and the raise arm.
- Registry self-test and `.github/workflows/nightly.yml`: the record pull request red when a generated file is hand-edited, green when it equals regeneration; null: a push with no delta writes nothing.
- Part 1, as its analysis states: the job red on a planted unrecorded read and green after the bot commit; null: a green push writes nothing. The analysis lands under `dev/audit/rca/` with its `bugclasses.json` entry if round 10 did not land it.
- `tools/pr/figure_block.py` self-test: a head moved by a merge of main fails `verify` today and passes with no stored block; null: a typed figure is still refused.
- `tests/env_drift.py` self-test: the post-stamp merge of a claiming branch refuses today and resolves; null: a scenario both sides rewrote still refuses.
- Features split, a harness under `dev/audit/harnesses/`: the multiset of check names and results over the new scripts equals the old script's at the merge base; re-running the splitter on the base reproduces the committed tree byte for byte; a sample of F5's kills per module still kills. No golden moves; neither claim file is touched.
- The group's claim: over merges after the last part, zero `ci: merge main` commits whose driver-free conflict set lies inside registry paths or the features scripts (F2's enumerator plus the pipeline appendix's absorb census); and F3's line re-run over that window.

## 7. Cost, split, serial position

The whole is larger than L; proposed parts, one merge each, graders before their use because CI restores the base's copy of a pinned grader (`fixer.md`, the p1/p2 rule):

| part | content | size | after |
|---|---|---|---|
| 1 | self-test table: union record, bot re-record (ruled; absorbs #3551's union half) | S | none |
| 2 (p1) | graders accept both regimes: the loader, the merge-base ceiling, the index from entries, the registry and its check, not yet enforced | M | none |
| 3 (p2) | the switch: fragments written by the three recorders of section 3, M3 in `record-autofix`, G1 enforced, policy text | M | 2 |
| 4 | features split, at a point with no open branch touching the script | L | 3 |
| 5 | figure blocks, re-pin, claim stamp rule | M | 2 |

Hot files: `tests/closure.py`, `tests/structure.py`, `tools/pr/prepr.sh`, `.github/workflows/tests.yml`, `nightly.yml`, `governance.yml`, `pr-contract.yml`; `open_pr.sh` and `update_pr.sh` with R11-PRE-PARALLEL-PIPELINE's part 1 and R11-HOTFIX-FIGURE-BLOCK-BASE (part 5 goes after both); `fixer.md` with R11-PRE-HANDOFF-BOOKKEEPING. Policy the owner reviews before merge: `CLAUDE.md` rules 1 and 2, `gate-scoping.md`, `ci-autofix.md`, `claim-files.md`, `brief-citations.md`, `fixer.md`, and every workflow path. Carries: receives carry 0 (part 1); owes none yet.

## Notes for the fixer

- The fragment name must survive a branch restarted under the same name after its merge: the fold has deleted the old file, so the new one is an add. Test it. Carry: R11-PRE-SHARED-FILES (item n1)
- The splitter's majority rule was not run in the design's time box; if one module script comes out above a quarter of F4's lines, report the distribution before moving anything. decision: orchestrator. Carry: R11-PRE-SHARED-FILES (item n2)
- The mutation pin bot moves more heads than any file here (F2). Carry: R11-PRE-PARALLEL-PIPELINE (item n3)
- `dev/audit/config/bugclasses.json` is the same append-at-one-place class. Carry: R11-PRE-HANDOFF-BOOKKEEPING (item n4)
- A script added with no entry file is outside `index_gaps` today and stays outside it. Carry: dismissed: unchanged by this design (item n5)
- `tools/audit/seat/features_block.py` slices on two literal lines of the old script; its self-test is the first thing part 4 breaks. Carry: R11-PRE-SHARED-FILES (item n6)
