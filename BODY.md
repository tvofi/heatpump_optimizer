record: refresh HANDOVER.md as round 10's durable state (R10-HANDOVER-REFRESH)

`dev/programme/HANDOVER.md` named `a77faf30d` as its `updated-for:`. This rewrites it in place as round 10's durable state, under `writing-for-agents.md`. Its `updated-for:` now names the base merge, `0cc148b2f`.

- **Carried decisions.**
  - Mandate 6175172275. Its first line, scope and window were read from the #201 comment through the API, and no revoking comment names it.
  - The open-PR soft cap of 6 gates only the start of a new roster group, and a pull request for an owed handoff is never refused (tvofi, 2026-10-21).
  - Cloud seats are dispatched through `cloud_dispatch.py` and a remote-trigger dispatcher routine, never through interactive session cards (tvofi, 2026-10-21).
  - The record beat leaves the `updated-for:` line manual.
  - The v7.0.2 stamp's `--allow-red` and `--allow-rowless` precedents.
- **Corrections to the record.**
  - The rulesets were read live. `main-protect` (22628467) now has no bypass actor, so the owed item asking for a ruling on the `hpo-ledger` bypass is retired. A third ruleset, `release-tags-protect`, is recorded.
  - "This file is not policy" now states where `policy_budgets.json` names the file: only in `roles.record.opens`.
- **Owed work.**
  - Retired, each with the check that shows it spent:
    - #1116's `--list` gap was closed by #1137.
    - `mutation_budgets.json`: `last_measured.full` is now populated.
    - #954 is closed.
    - `tests.yml` no longer carries the #1122 sentence.
    - All seven friction issues are closed.
    - #558 is closed.
  - New: the soft-cap instrument does not yet implement the 2026-10-21 ruling. `open_pr.sh` calls `pr_cap.py gate` on every open.
- **Traps.**
  - 1–46 keep their numbers, because `.claude/hooks/session-start.sh` cites "HANDOVER trap 11".
  - Six round-10 traps are added (47–52).
- **Removed: chronology that is no longer state.** This covers the 2026-09-19, 2026-09-20/21 and 2026-10-13/14 sections, Wave 1067's close-out narrative, the UX-programme section, and the decomposition-stage and S12 seam rulings. All of it stays readable at `git show a77faf30d:dev/programme/HANDOVER.md`, which the file's preamble names.
- **Not moved here.** The critical-path republish carry (#201 comment 6308996721) and every in-flight state stay on #201. Nothing goes in both places.

## Head

`c2902d6cab0d205804b212303cced5335d4e5c95` (merge base `0cc148b2f80fe224ffe2c504b29fd4f0908183df`, the base the dispatch named). Measured 2026-10-21. At handoff, `origin/main` read `6961f06637964001a2ed544e495ea0312eeefa37` at 2026-10-21T09:37:14Z, 12 commits past the base (`git rev-list --count 0cc148b2f..origin/main`), and this head has not absorbed them. Every figure here describes the base `0cc148b2f`; the `updated-for:` line names it and stays reachable through any later main merge.

## Mutation proof

The check that pins this file is `tests/entities.py`'s `updated-for:` block. It has three checks: the line exists, its commit is reachable from HEAD, and that commit is reachable from origin/main.

Mutant: `updated-for:` re-pointed at this branch's own commit `c2902d6c` (an ancestor of HEAD but not of origin/main). `tests/entities.py` exits rc=1 with `1 of 2363 ENTITY CHECKS FAILED`. The failing check is `FAIL and reachable from origin/main, so a squash cannot orphan it [updated-for: c2902d6c… is not an ancestor of origin/main …]`, while `and that commit is reachable from HEAD` stays `ok`. The line was then restored to `0cc148b2f`.

## Null control

- At the merge base (unmodified tree), `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` gives rc=0 and `ALL 2363 ENTITY CHECKS PASSED` (detached worktree at `0cc148b2f`).
- `policy_lint.mjs --budgets` prints byte-identical aggregates at base and head. The probe shows why:
  - Appending 300 lines to this file leaves them unchanged.
  - The same 300 lines appended to `AGENTS.md` move `corpus` from ~61152 to ~64875 tokens.
  - So no cap reads this file's text, and none grew.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` gives `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and the one script run is `tests/entities.py`.
- `tests/entities.py` at head: rc=0 and `ALL 2363 ENTITY CHECKS PASSED`, including `ok the handover names the commit it reflects`, `ok and that commit is reachable from HEAD` and `ok and reachable from origin/main, so a squash cannot orphan it`.
- Commits the old `updated-for:` lagged at this base: `git rev-list --count a77faf30d..0cc148b2f` = 2086. The tick's earlier 2072 was taken at an older `origin/main`, so it is a sliding figure.
- `node tools/policy/policy_lint.mjs` (bare, the refusing form): rc=0, `TOTAL: 0 error(s)` at head.
- `node tools/policy/policy_lint.mjs --record --since v7.0.2`: rc=0, `TOTAL: 0 error(s)`. Output is byte-identical at base and head except the `RENDER` line, whose list-item count rises 58 → 64 (the six new traps).
- `node tools/policy/policy_lint.mjs --record --since v6.5.0` (the widest window, through the API enumerator): rc=1 with `TOTAL: 24 error(s) over 872 merged pull request(s)` at both base and head, the output byte-identical except `RENDER` (`diff` rc=0). The 24 are pre-existing rowless merges (#1157–#1780), and cutting this file's prose removed no merge's only disposition. `--since v7.0.0` gives rc=0, `0 error(s) over 236`, at both.
- `policy_lint.mjs --budgets`: the last 8 lines (the aggregates) are identical at base and head (`diff` rc=0).
- Rulesets, read 2026-10-21 with `gh api repos/tvofi/heatpump_optimizer/rulesets/<id>`:
  - 22628467: `bypass=` (none), rules `deletion,non_fast_forward`.
  - 23698884: `DeployKey:always`, `Integration:5094721:always`.
  - 23937752 (tag target): `DeployKey:always`.
- Retired owed items, each re-checked at the base:
  - #954, #1848, #558 and the seven friction issues #1069, #1070, #1078, #1079, #1087, #1094, #1095: `gh api repos/tvofi/heatpump_optimizer/issues/<n> --jq .state` = `closed` for each.
  - `grep -n "which no gate lane has" tests/typing_ruler.py .github/workflows/tests.yml` hits only `tests/typing_ruler.py:33`.
  - `jq .last_measured.full tests/mutation_budgets.json`: populated (run `35395283955`).
- Mandate: `gh api repos/tvofi/heatpump_optimizer/issues/comments/6175172275` first line `MANDATE: agents may approve as tvofi, scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z`. A scan of every #201 comment for both "revoke" and the id returns nothing.
- Unreproduced figure, corrected rather than carried: trap 46's "main moved 17 times on 2026-10-14". `git log --first-parent` over that day gives 37 commits, or 32 PR merges, under local-time dating, and no rule found yields 17. The number was cut, and so was trap 44's dated casualty list.
- Figures inside traps 1–45, the corrections and the decisions are records anchored to their own SHA or PR (fixer.md step 10: "a measurement record stays as written"). They are not current-state figures, and none of them is restated as current.

## Red checks

none

## Forward-carry

none

## Friction

- `cloud-seat-env: stale`: the dispatch says the toolchain is on PATH. In this container `python3` was 3.11 with `/opt/hpo/venv-ci/bin` not on PATH, and `tests/entities.py` fails to parse there. It is recorded as trap 52. Carry: dev/programme/HANDOVER.md
- `gh-paginate-proxy: cost`: `gh api --paginate` on #201's comments returns 403 after the first page. It follows a numeric-id `Link` URL that the proxy refuses, so the comments were fetched with a manual `?page=N` loop (trap 52). Carry: dev/programme/HANDOVER.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01Efa8rC2u92nVdiiYqryks9
