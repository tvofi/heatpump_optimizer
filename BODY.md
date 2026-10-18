_Requested by **tvofi**_

policy: O17 items 1 and 3, the policy half, from the roster-cost pre-study the orchestrator accepted on 2026-10-18 (tvofi asked to keep the roster and state docs from costing CI). Part of #201. No roster group lists an issue for this work, so this body closes none. The tooling halves are `handoff/r10-roster-fastpath` (readers default to the roster branch, the beat watches it) and `handoff/r10-codeql-lang-skip`. The tick's line for unlanded roster commits is the coordinator's own, in the tick seat.

**Owner gate.** This is policy: `dev/governance/rules/finding-propagation.md` and `dev/governance/roles/{orchestrator,fix-review}.md` are in `POLICY_GLOBS` and code-owned, so tvofi approves this before it merges.

**Why.** A producing PR waited on a roster PR because the rule said the carry must be "in the tree", meaning on main. #2373 waited on roster PR #2384. Yet no check reads a roster carry's content from main:
- `policy_lint.mjs --pr-body` tests only that a `## Forward-carry` path exists, and the roster path always does. `brief_lint.mjs` documents this as cases 3 and 4, existence and not authorship.
- What enforced the wait was this text and `fix-review.md` step 10.

The pre-study measured the cost of that wait: 14 roster-only PRs merged in round 10 (median 49 min open to merge), and 54.1 runner-min on #2380's head.

**The change.**
- **`finding-propagation` (canon `dev/governance/rules/`, both generated copies via `rules_sync.mjs`).**
  - Enforcement: a roster carry is in the tree once it is on the round's roster branch `handoff/audit-r<N>-roster`. That branch lands on main at each stamp and before branch cleanup, and stays while `git diff origin/main...<branch> -- dev/programme/rosters/` prints anything. That is the durability guard: the carry survives a session because the ref outlives it, and cleanup may not delete it unlanded. The body names the branch SHA.
  - The stale home `.claude/workflows/wave-*-groups.json` becomes `dev/programme/rosters/`, in the text and in the `paths:` glob. `roster_lib.py` already says rosters are NOT under `.claude/workflows/`.
- **`orchestrator.md` section 10.** Land the roster on main only when the tree needs it: a carry a PR names, a `Closes` needing a `fixes` edit (pr-contract derives the allowed closes from the PR's tree), each stamp, and before branch cleanup, which keeps the roster branch while it differs.
- **`fix-review.md` step 10.** Open a roster carry at the body's roster-branch SHA.
- **Paid in-file, no cap raised.** All three files were at zero headroom. The words paid were incident detail and a duplicate pointer:
  - commit shas beside issue numbers;
  - "it has happened twice";
  - `Your other reusable scripts land too, by fixer.md step 18.`, which section 13's preceding sentence already states;
  - a lane-without-roster example;
  - wording.

  `policy_lint`'s `duplicates` entry for orchestrator.md drops from 8 to 6 and is re-recorded.
- **Out-of-scope fix, folded.** `node tools/policy/policy_lint.mjs --record-known-bad` crashed with `TypeError: at is not a function`: in `cmdRecord`, a local `const at = recordedAtSha()` shadowed the module's `at(path)`. `git log -L` puts the shadowing at `98ee99263` (R9-RO-2), so every re-record since has needed a hand edit. The local is renamed `sha`.

**Alternatives considered.**
1. Make CI read carries from the roster ref. Refused: a PR check that reads a mutable, unreviewed branch is not reproducible at a fixed head, and no CI check reads carry content anyway.
2. Keep "in the tree" as main and batch roster PRs only. Refused: the producing PR still waits on a roster PR's full CI.
3. Raise the three caps. Refused: each was payable in-file.

## Head

`36b4a1cf4e33b7f343c99e41e49e14a2b050547a`, one commit on origin/main `63816b857`.

## Approval

Owed: tvofi's approval of this policy change before it merges (`CLAUDE.md`; the coordinator listed this PR as policy for tvofi at merge). Not given yet; nothing here claims it.

## Mutation proof

- **Caps.** The first draft, the rule text added with nothing paid, measured `.claude/rules/finding-propagation.md 104 lines / ~1408 tokens` against caps 101 and 1336 (`node tools/policy/policy_lint.mjs --budgets`). orchestrator.md measured 322 and ~4576 against 319 and 4513; fix-review.md 141 and ~2460 against 140 and 2451. The head is 98/1335, 319/4513 and 140/2451.
- **Citations.** A draft naming `dev/programme/rosters/wave-r<N>-groups.json` was refused by `policy_lint.mjs`: `[citations] .claude/rules/finding-propagation.md:57: path groups.json: not in the tree`. The head names the directory.
- **Generated copy.** Restoring origin/main's `.cursor/rules/finding-propagation.mdc` over the head's makes `node tools/policy/rules_sync.mjs --check` print `RULES-SYNC: 1 file(s) out of date`. Restored.
- **Known-bad.** Before the re-record, `policy_lint.mjs` printed `[known-bad] ... 6 occurrence(s) left of 8 recorded: duplicates|tools/audit/briefs/orchestrator.md`, and `--record-known-bad` crashed with `TypeError: at is not a function`. After the rename it printed `recorded 7 entr(ies), 13 occurrence(s) ... ~ 8 -> 6`, and the lint `TOTAL: 0 error(s)`.

## Null control

At origin/main `63816b857` the unmodified tree's `policy_lint.mjs --budgets` reads 100/1329 (finding-propagation), 319/4513 (orchestrator.md) and 140/2451 (fix-review.md). The head's `## Enforcement` paragraph is the only text that adds an obligation. Every other changed line either rewords a sentence without changing what it requires, or removes an incident detail or a duplicate pointer, listed above.

## Figures

- `node tools/policy/policy_lint.mjs --budgets`: finding-propagation 98 lines (cap 101) and ~1335 tokens (cap 1336); orchestrator.md 319/319 and ~4513/4513; fix-review.md 140/140 and ~2451/2451; corpus ~61136 (base ~61130; cap 61026 plus band 500).
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- **Gate scope.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out` (`tests/entities.py`), left to CI under the owner's heavy-scripts rule.

## Unpinned sites

`policy_lint.mjs`'s `cmdRecord` write path: no fixture drives `--record-known-bad`, which is how a crash on every call went unseen. Triage: the run above is its one exercise. A pin belongs in `policy_lint_mutants.mjs`'s fixture drive. It is owed and stays open: the orchestrator dispatches it (out-of-scope findings get fixed), since that file is outside this group.

## Red checks

none

## Forward-carry

none. This change is itself the rule text the next round's orchestrator reads.

## Friction

finding-propagation: stale: the rule named `.claude/workflows/wave-*-groups.json` as the roster's home, while `roster_lib.py` states rosters are not there.
