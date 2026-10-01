<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Round-9 process change PROC-1: the policy half of process-review items 1, 4, 6 (brief half), 8 and 10, which tvofi adopted on 2026-10-01T16:51Z ("fold in all changes as soon as possible in the ongoing plan"). Roster group `R9-PROC-1` at `0b442c06`; item 7 moved to PROC-3 in that re-cut, so this PR does not touch `delivery-status-tracking.md`. Policy text only, under the owner's mandate: the orchestrator's approval on the merge verdict is tvofi's approval here.

Before: a clean main merge into a verdicted PR cost an opus reviewer turn; seats ended turns on detached jobs and sat idle until a stall check; a post-handoff conflict forced a re-cut branch with every red-first test and mutant re-run; fixers ran `--pin-killed` locally before handoff.

After:
- **Item 1** (`fix-review.md` step 12, `orchestrator.md` section 11): a `merge` verdict carries with no reviewer turn when `tools/audit/app_approve.sh --carry <verdict> <head>` reports carried, the files `git diff --name-only <verdict> <head>` names miss the branch's own diff, and the claim files equal `origin/main`'s. Any other main merge goes to the same reviewer as a resolution delta, which alone it judges. `--carry` already refuses a hand-resolved merge and a branch diff that moved (`carry()` in `app_approve.sh`); the same-file and claim-file clauses are the two the review named that `--carry` does not test, so they are written as the orchestrator's predicate.
- **Item 4** (`fixer.md` preamble, referenced from `fix-review.md`, `root-cause.md`, `orchestrator.md` section 11): a job that outlives the turn runs as a background task whose exit wakes the seat; never end a turn on a detached one. The orchestrator watches CI from such a task, never on a timer.
- **Item 8** (`fixer.md` step 6, `orchestrator.md` section 7, `fix-review.md` step 12): a post-handoff conflict is resolved by merging `origin/main` into the head (the orchestrator, or the fixer when semantic), never by a re-cut; the same reviewer judges the resolution delta, and steps 2-8 re-execute only where that delta reaches. This retires the rule "never merge main into handoff branches", which was never in the tree (it lived in the coordinator's brief add-ons); the in-tree sentence it overrides is `fixer.md` step 6's "do not merge it yourself".
- **Item 6, brief half** (`fixer.md` step 2): no local `--pin-killed`; `mutation-autofix` pins what CI kills, and the body lists survivors on touched sites (`mutation_table.py --scope changed`), each with a value check or a written triage. `ci-autofix.md`'s "when `mutation-autofix` goes red, run `--pin-killed` yourself" stands: it is the red-autofix fallback, not a pre-handoff step.
- **Item 10** (`fixer.md` preamble, `orchestrator.md` section 5): a seat reads only its own roster group with `jq`; judgement-free turns (relays, delivery rows) go to the cheapest model that does them.

Every per-file policy cap is met by cutting prose another file already carries (each cut names its surviving copy below); no cap is raised.

## Head

`5aaef98e` (code head; this body travels as a transport commit above it). Merge base `90335cbd`.

## Mutation proof

n/a: no production or test code changes; the diff is four role contracts under `tools/audit/briefs/`. The check that binds this text is `policy_lint.mjs`, and it moved under this diff's own first draft: backticking the harness option as a symbol, naming the `gh` binary for the CI watch, and repeating the background sentence verbatim in two contracts drew 7 errors (`citations` x4, `no-gh` x2, `duplicates` x1); each was reworded, not suppressed.

## Null control

`node .claude/workflows/policy_lint.mjs` at the merge base `90335cbd`: `TOTAL: 0 error(s)`; at the head: `TOTAL: 0 error(s)`. The intermediate draft above is the non-null case.

## Figures

- Per-file caps (`files`, `files_tokens`) for the four contracts: `node .claude/workflows/policy_lint.mjs --budgets` prints each within its cap at the head, rc 0.
- Corpus and role aggregates: the same command, within cap plus `_band`.
- `node .claude/workflows/policy_lint.mjs`: rc 1 at the first draft (7 errors, above), `TOTAL: 0 error(s)` at the head.
- `node .claude/workflows/brief_lint.mjs`: rc 0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc 0.
- `node .claude/workflows/rules_sync.mjs --check`: rc 0 (no rule under `.claude/rules/` changed).
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run`; every changed file is outside every measured closure.
- Seams of the retired rules, by `git grep -n -i -E "merge-delta|merge delta|merges main and waits|merge main and wait|do not merge it yourself|merge main into|re-cut|recut|pin-killed" -- CLAUDE.md AGENTS.md .claude/rules .claude/skills tools/audit/briefs tools/audit/README.md docs/HANDOVER.md .claude/workflows/*.md .claude/workflows/*.js .claude/workflows/*.mjs`, each against its disposition:
  - `fix-review.md` step 11 "if main moved, it merges main and waits": closed here (replaced by step 12's carry and resolution delta).
  - `fixer.md` step 6 "do not merge it yourself": closed here.
  - `fixer.md` "Past three rounds, re-cut rather than repair", `fix-review.md` "re-cut body", `docs/HANDOVER.md` body re-cut lines: a different sense (re-cutting a PR body at round four), left.
  - `ci-autofix.md` "run `--pin-killed` yourself" when `mutation-autofix` goes red: consistent with item 6, left.
  - `web-fragments.md` and its four `web-*.js` copies, the merge seat's "do not merge main into the branch yourself, the fixer must": left. That seat holds no worktree and returns `needs repair` to its workflow, which item 8 still allows (a semantic resolution is the fixer's); its stated reason, that a rebase invalidates the evidence, still holds. A change there is a `fragments_sync.mjs` edit across five files for a runner the programme's orchestrator does not use.
- Live roster briefs naming `--pin-killed` or "never merge main": `git show origin/handoff/audit-r9-fixplan:.claude/workflows/wave-r9-groups.json | jq -r '.groups[] | select(.resume.stage != "done") | select(.brief|test("pin-killed|never merge main")) | .group'` at `ea77625d` prints only `R9-PROC-1`.
- Cuts that paid for the lines, each with the surviving copy: the sliding-window bullet (`fixer.md` step 3), the #373 sentence (`fixer.md` step 8), the gate-lease expiry clause (`gate-scoping.md`), the handover enforcement clause (`writing-for-agents.md`), the cost-test unit sentence in `root-cause.md` (`defect-root-cause.md`), "paying for the lines is the first question" (`CLAUDE.md` rule 2), the hpo-author key-file clause (`app_push.sh` header); the merge-commit incident in `orchestrator.md` section 4 kept its SHAs and dropped its timestamps.

## Red checks

none at handoff (no CI has run on this head yet).

## Forward-carry

Each item is a rule for every seat of a role, so it lands once in that role contract (`finding-propagation.md`): `tools/audit/briefs/fixer.md`, `fix-review.md`, `orchestrator.md`, `root-cause.md`. Out of tree, the coordinator's brief add-ons still carry "pin new mutation sites with `--pin-killed` before handoff" and "never merge main into handoff branches"; both are retired by this PR and are the coordinator's to drop at merge.

## Approval

Policy (four role contracts), so the owner approves before merge. tvofi adopted every change written here on 2026-10-01T16:51Z ("fold in all changes as soon as possible in the ongoing plan") and gave the orchestrator the mandate to approve as tvofi on a merge verdict (2026-09-30T20:19Z: "you have the mandate to approve as tvofi. There is no self-approval in this scenario"). That approving review, at this PR's head, is the record; this body is not.

## Friction

ratchet-budgets: cost: every role contract sat at zero token headroom, so each added clause was paid by a cut elsewhere in the same file
fixer: stale: step 5 says seats are LOCAL-ONLY and the orchestrator pushes, while cloud seats push handoff branches themselves; left, outside this group

🤖 Generated with [Claude Code](https://claude.com/claude-code)
