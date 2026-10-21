record: refresh HANDOVER.md as round 10's durable state (R10-HANDOVER-REFRESH)

`dev/programme/HANDOVER.md` named `a77faf30d` as its `updated-for:`. This rewrites it in place as round 10's durable state, under `writing-for-agents.md`. Its `updated-for:` names `0cc148b2f`, the base the dispatch named. That commit is still an ancestor of this head after the `origin/main` merge. This pull request also lands the group's roster carry: `tools/audit/seat/handover_prompt.py` printing `git fetch origin None`.

**The handover rewrite** (commit `c2902d6c`):

- **Carried decisions:**
  - mandate 6175172275;
  - the open-PR soft cap of 6, which gates only the start of a new roster group (tvofi, 2026-10-21);
  - cloud seats dispatched through `cloud_dispatch.py` and a dispatcher routine (tvofi, 2026-10-21);
  - the manual `updated-for:` line;
  - the v7.0.2 stamp's `--allow-red` and `--allow-rowless` precedents.
- **Corrections to the record:**
  - The rulesets were read live. `main-protect` (22628467) has no bypass actor, so the owed `hpo-ledger` item is retired.
  - `release-tags-protect` is now recorded.
  - "This file is not policy" now says where `policy_budgets.json` names the file.
- **Owed work.** These items are retired, each with the check that shows it is spent:
  - #1116's `--list` gap;
  - `mutation_budgets.json`'s `last_measured.full`;
  - #954, #558 and the seven friction issues;
  - the #1122 sentence in `tests.yml`.

  One item is new: the soft-cap instrument does not yet implement the 2026-10-21 ruling.
- **Traps:** 1–46 keep their numbers, because `.claude/hooks/session-start.sh` cites "HANDOVER trap 11". Six round-10 traps are added (47–52).
- **Removed:** chronology that is no longer state. It stays readable at `git show a77faf30d:dev/programme/HANDOVER.md`, which the preamble names. The critical-path republish carry and every in-flight state stay on #201. Nothing is in both places.

**This round** (commits `eb7c8e9e` and `efb0532f`), against the two refusals `open_pr.sh` returned on `c2902d6c`:

1. **Layout guard `new-reference`.** The rewrite said "`CORPUS_EXCLUDED` still spells its pre-move path, `docs/HANDOVER.md`", as if it were a residual defect. I checked the source and it is not stale. `policy_lint.mjs` reads the tracked listing through `canon()` (`trackedFiles()` → `canonList`), which spells a moved file by its old path. So `'docs/HANDOVER.md'` is the key that excludes the file. The move-map loop beside the Set then adds `dev/programme/HANDOVER.md` from `tests/layout.json`.

   Re-keying the Set at the new path turns `policy_lint.mjs` red (see Null control), so that is not a sound fix. The sentence was the defect, and it is deleted. The residual beside it ("prose moved here leaves the corpus") stays. The guard itself is untouched.
2. **pr-body.** The refusal's real error was the attribution footer, which sat after `## Friction` and so was read as an unparseable Friction line (see Red checks). The diff raises no budget leaf, and the body claims none. This body is rewritten whole against the new head.
3. **Carry (roster `carry[0]`, #201 comment 6310616463).** `render()` interpolated `resume.branch` and `resume.note_file` unconditionally. A group dispatched before its first push therefore printed `git fetch origin None`. The round-10 roster keeps no `note_file`, so every in-flight line printed `` note `None` `` and told the seat to read it. The new `pickup()` names only the fields the roster carries:
   - with no branch: `no branch pushed yet, so nothing to fetch`;
   - with no note: no note clause.

   It does not guess the branch-to-be: missing input is refused, never guessed (fixer step 17).
4. **Trap 51.** It described the `git fetch origin None` line that item 3 removes, so it was no longer true. Nothing outside the file cites trap 51 (`git grep -n -iE "trap 51" -- . ':!dev/programme/HANDOVER.md'` returns nothing). The number now carries this handoff's friction: `body_push.sh`'s predictor `tools/pr/ci_predict.py` has no layout-guard arm (`grep -n layout tools/pr/ci_predict.py` hits only a `closure.layout_errors` docstring). The trap names the guard command to run before `body_push.sh`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01LZmVuEHqE1xysY87Gg9x1j

## Head

`efb0532fb9608936eb3d971a05db146984d92745`.

- Merge base: `03b49e1521a2490335922093c9177aec8f6119d9`, which was `origin/main` at 2026-10-21T11:38:45Z. `origin/main` was merged into `c2902d6c`, never rebased.
- Code commits: the handover rewrite `c2902d6c`, which describes `0cc148b2f`, and this round's `eb7c8e9e` and `efb0532f`.
- Main's merged delta (`0cc148b2f..03b49e152`) is #2526 (gate priority) plus record and autofix rows. A `grep` of the handover for `gate_lock`, `lease` and `priority` finds no statement it falsifies.

## Mutation proof

Instrument: `python3 -I tools/audit/seat/handover_prompt.py --self-test`, the command `governance.yml` runs. Each predicate in `pickup()` was mutated, one at a time, and then restored. `git diff --stat` was empty afterwards.

- M1 `if not branch:` → `if False:` gives `15 checks, 1 failed`: `FAIL in-flight group without branch or note names neither`.
- M2 `` (f", note `{note}`" if note else "") `` → unconditional gives `15 checks, 1 failed`: `FAIL in-flight group with a branch and no note fetches it, names no note`.
- M3 `if note:` → `if True:` gives `15 checks, 1 failed`: the same check as M2.
- M0, a control that drops the pickup line entirely, gives `15 checks, 3 failed`, including the pre-existing `in-flight pickup command`.
- Failing test first: with the two new checks in place and the old `render()` body, the self-test gave `14 checks, 1 failed`. That was the first new check, whose output contained `git fetch origin None`. At that point the second check had not been written.

Handover sentence: restoring it is the `c2902d6c` state. `python3 -I tests/layout.py --guard --base 0cc148b2f` at `c2902d6c` returns rc=1 with `new-reference: dev/programme/HANDOVER.md cites retired path docs/HANDOVER.md`, and `GUARD: 1 refusal(s)`.

## Null control

- **Re-keying `CORPUS_EXCLUDED`, the rejected fix.** With `'docs/HANDOVER.md'` replaced by `'dev/programme/HANDOVER.md'` in `tools/policy/policy_lint.mjs`, `node tools/policy/policy_lint.mjs` returns rc=1 with `TOTAL: 1 error(s)`: `ERROR [named-docs] docs/HANDOVER.md: is named by .claude/rules/brief-citations.md but has no cap`. Unedited, the same command returns rc=0 with `TOTAL: 0 error(s)`. The change was reverted (`git checkout`).
- **Layout guard.** At head, `python3 -I tests/layout.py --guard --base 03b49e152` returns rc=0 with `GUARD: 0 refusal(s)`. At `c2902d6c` against its base it returns rc=1 with 1 refusal (see Mutation proof).
- **Generator at the merge base vs head**, against the live round-10 roster: `python3 tools/audit/seat/handover_prompt.py --roster-ref origin/handoff/audit-r10-roster`, with the roster at `61eaa993`.
  - At the base (worktree `03b49e152`): 23 in-flight lines, `grep -c None` = 23, `grep -c 'git fetch origin None'` = 4.
  - At head: 23 in-flight lines, `None` = 0, `git fetch origin None` = 0, `no branch pushed yet` = 4.
  - `diff` of the two outputs: 23 changed lines, exactly the in-flight lines.

## Figures

- Gate scope: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` gives `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` = `tests/entities.py`.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` at head: rc=0 and `ALL 2375 ENTITY CHECKS PASSED`. The `updated-for:` block is ok, because `0cc148b2f` is reachable from both HEAD and origin/main.
- run_always lines (`tests/run.sh`), with `PATH=/opt/hpo/venv-ci/bin:$PATH`: `tests/env_drift.py --claims-only 03b49e152` rc=0 (`claims hygiene: ... ok`); `tests/closure.py selftest` rc=0 (`ALL 124 closure shrink pins PASSED`); `tests/layout.py` rc=0 (`layout self-test: ok`); `tests/harness_headers.py` rc=0 (`ALL 109 HARNESS HEADER CHECKS PASSED`).
- `python3 tests/structure.py`: rc=0, `STRUCTURE RATCHET PASSED`. No `*_budgets.json` is touched (`git diff --name-only 03b49e152 HEAD` names only `dev/programme/HANDOVER.md` and `tools/audit/seat/handover_prompt.py`).
- `node tools/policy/policy_lint.mjs`: rc=0, `TOTAL: 0 error(s) across 41 policy file(s)`. The output is byte-identical (`diff` rc=0) to the same command on the merged tree before this round's edits.
- `node tools/policy/policy_lint.mjs --budgets`: rc=0. The last 8 lines (the aggregates) are identical before and after this round's edits (`diff` rc=0).
- `node tools/policy/rules_sync.mjs --check`: rc=0.
- `handover_prompt.py --self-test` at head: `15 checks, 0 failed`. At the merge base it gives `13 checks, 0 failed`.
- Step-8 seam rule, for "a resume field rendered unchecked": `grep -n "get('" tools/audit/seat/handover_prompt.py`. At head it returns one site, line 73, `r.get('stage')`. That site is already guarded, because `in_flight()` admits only a truthy stage that is neither done nor not-started. `branch` and `note_file`, the other two sites at the base, are closed in this diff.
- Seam rule for the `CORPUS_EXCLUDED` class: `sed -n '/^const CORPUS_EXCLUDED = new Set/,/^])/p' tools/policy/policy_lint.mjs | grep -o "'docs/[^']*'"`. It returns the old-path keys `docs/audit-2026-09.md`, `docs/plan-2026-09-open-issues.md` and `docs/HANDOVER.md`. Each is the canonical spelling `canon()` reads, so it is already correct by design (null control above), and none is a defect.
- Handover's lag at the dispatched base: `git rev-list --count a77faf30d..0cc148b2f` = 2086.
- Live reads, re-taken 2026-10-21 for this head with `gh api repos/tvofi/heatpump_optimizer/...`:
  - ruleset 22628467: `bypass=` (none), rules `deletion,non_fast_forward`;
  - ruleset 23698884: `DeployKey::always Integration:5094721:always`;
  - ruleset 23937752: `DeployKey:always`;
  - issues #954, #1848, #558, #1069, #1070, #1078, #1079, #1087, #1094, #1095: `.state` = `closed` for each;
  - comment 6175172275, first line: `MANDATE: agents may approve as tvofi, scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z`.
- `grep -n "which no gate lane has" tests/typing_ruler.py .github/workflows/tests.yml` hits only `tests/typing_ruler.py:33`.
- `jq -c '.last_measured.full|keys' tests/mutation_budgets.json` gives `["at","equivalent","evaluated","run","survivor_lines","survivors"]`.
- Figures inside traps 1–46, the corrections and the decisions are records anchored to their own SHA or PR (fixer step 10: "a measurement record stays as written"). None is restated as current.

## Red checks

The handoff at `c2902d6c` was refused before the pull request opened by `prepr.sh`, inside `open_pr.sh`, on the layout guard and on pr-body. No CI check ran red.

- **Layout guard.** It is the cheaper detector, it fired, and it runs in `prepr.sh` before the push. The body predictor `tools/pr/ci_predict.py`, run by `body_push.sh`, did not catch it. That is answered in Friction.
- **pr-body.** Its one error was not about budgets. It was `## Friction line does not parse`, on the attribution footer, which sat after the last heading and so was read as a Friction line. `prepr.sh` prints only the check's last line, the budget-gate summary `no budget leaf raised`, so the cause was invisible in the refusal. This body puts the footer before `## Head`. Running the checker directly shows the real error: `node tools/policy/policy_lint.mjs --pr-body <body> --head <sha> --title <t> --paths-file <f>`.

## Forward-carry

none

## Friction

- `cloud-seat-env: stale`: the dispatch says the venv is on PATH, but here `python3` resolved to `/usr/local/bin/python3` (3.11). `/opt/hpo/venv-ci/bin` had to be prepended. This is already trap 52 in this file. Carry: dev/programme/HANDOVER.md
- `handoff-gate: unenforced`: `body_push.sh`'s static predictor passed `c2902d6c`, and `prepr.sh`'s layout guard then refused it inside `open_pr.sh`. The handoff paid a full round trip for a refusal that one command gives in seconds: `python3 -I tests/layout.py --guard --base <merge-base>`. It is recorded as trap 51. Carry: dev/programme/HANDOVER.md
