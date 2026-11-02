`tools/audit/seat/bus.sh orphans` died on macOS bash 3.2 under `set -u` (`arms[@]: unbound variable`) whenever neither `--no-ancestry` nor `--no-content` was given, so `pulse.py`'s opener arm read UNREADABLE and orphaned handoffs were invisible (triage P303). Fix: the ledger.py call uses `${arms[@]+"${arms[@]}"}`. Class barrier: `tools/audit/seat/bare_array.py`, a static rule over every tracked `tools/**/*.sh` file, with or without `set -u` of its own (a sourced library runs under its caller's `-u`, and nounset has spellings a textual test misses): a bare `"${a[@]}"` is refused unless guarded, or unless `# never-empty: <reason>` sits on the line or on a comment-only line directly above it. It is pinned in `tests/entities.py`, run as a governance step and listed in `tools/audit/seat/INSTRUMENTS.md`. CI's bash 5 expands an empty array cleanly, so a run-time row would pass on the defect; the rule is therefore static. A never-empty reason placed after a `# mut:<name>` marker is refused in every file, because the self-tests find their mutant line by that marker at the line's end. Alternative rejected: plain variables in bus.sh lose the two-flag list the call forwards; the guard is the smaller change.

Departure from the group brief, stated: the roster brief asks for the check over files "running under `set -u`" with the null control "a file without `set -u` is not judged". Commit 07f79c3cf inverts that control: every tracked tools script is judged. Reason: the sourced `pr_args.sh` has no `set -u` of its own yet runs under its callers', and five of its sites would otherwise stay invisible to the rule. The control is now the twin pair "a file without set -u is judged too" and "the guarded form passes in a file without set -u (null)".

Carry 1 (the roster's carry from the R10-FLY-RAISE-REVIEWABLE round-2 fixer: `bus.sh orphans` fails on a macOS seat with `arms[@]: unbound variable`, bash-3.2 self-test row and a non-empty-array null control asked for): the empty-array expansion is guarded in `bus.sh orphans`. Departure, stated: the pin is the static `bare_array.py` rule rather than a self-test row run under `/bin/bash 3.2`, because CI's bash 5 expands an empty array cleanly and a run-time row would pass on the defect; the rule's self-test and the `tests/entities.py` rows carry the null control (the guarded form and a non-empty array are not refused). The reviewer decides whether that departure discharges the carry.

## Head

1dae4b62f59189943fe1038be2b7c6d69c3a2a2a: merge-forward of PR head 757c71eb905b9152d853054b754325d04206f8d1 over origin/main a568a2e128f8df25eb6a960838737c0bda277fac (#3065 merged; stamped 2026-11-02, `date -u` at the run). `git merge-tree --write-tree origin/main 757c71eb` reported a content conflict in `tools/pr/app_approve.sh`. What the merge resolved:
- Main's intent in `app_approve.sh` (`carry()`'s `norm()`): collapse each context line of a `*.md` file to a bare ` ` so prose main rewrote beside the branch's lines does not force a re-review; code files keep their context.
- This PR's intent in the same function: the line carries a `# never-empty` reason so `bare_array.py` accepts `"${d[@]}"` (`d` is the literal git diff command).
- Resolution keeps both: main's two-line `norm()` with its `awk` stage unchanged, and the reason as a comment-only line directly above it (a trailing comment is impossible after the continuation backslash). `git diff origin/main -- tools/pr/app_approve.sh` is that one comment line.
- Semantic interaction (commit after the merge): main's `tick_loop.sh` (R10-FLY-RELAY-REVIEW-FF) added three bare sites the rule refuses: lines 96 and 98 (`CODE_PATHS`, `SELF_PATHS`, literal lists: reasons given) and line 111 (`ARGV=("$@")`, empty when the loop starts with no arguments: guarded as `${ARGV[@]+"${ARGV[@]}"}`, so the restart no longer dies on bash 3.2 either). The other auto-merged files (`cloud-setup.sh`, `cloud_relay.sh`, `pr_args.sh`, `prepr.sh`) were read: this PR's edits there are reasons and guards and main's changes touch other lines; `bare_array.py --check` on the merged tree is the instrument.
- Earlier verdict (verdict/3055, body-stale) is answered: this body states the every-file design and the departure, the twin null controls, the seam list without the closed sourced-library seam, and re-taken figures. All round-1 answers below are kept.

Everything below was measured at 1dae4b62f unless it names another SHA. origin/main did not move between the final `tools/pr/prepr.sh` run and the handoff (`git rev-parse origin/main` a568a2e12 at both).

## Round-1 findings, all answered

1. **Regression, never-empty markers unanchored `mut:contract` and `mut:grace`.** Taken: the reason moves to a comment-only line directly above each marked line, `bare_array.py` reads a reason there (`sites`: the `above` flag excuses exactly the next line); a reason after a `# mut:` marker no longer excuses and is refused in every file (`marked`), so the collision cannot recur. The trailing form with the reason before the marker is accepted too (self-test "a reason before the mut marker excuses"). Teaching the self-test locators to tolerate a trailing comment was rejected: it changes five locators in two instruments to fit one checker. Main's new sites follow the same rule: `tick_loop.sh` line 96 and `app_approve.sh` `norm()` carry the reason on the line above because line 96 ends in `# mut:paths`.
2. **Red check unanswered.** Answered in `## Red checks`.
3. **Instrument unlisted.** `INSTRUMENTS.md` lists `bare_array.py` with its page `tools/audit/seat/instruments/bare_array.py.md`; `python3 tools/audit/seat/selftest_wiring.py --check`: 0 unwired, 0 index gaps (round-2 measurement).
4. **Matcher false-negative domain** (`set -e -o nounset`, `#!/bin/bash -u`, unquoted or embedded `${a[@]}`, slices). Dismissed: no live site (verdict ev/enum_tools.txt); only `train.sh`'s two slices inside a length-checked loop. Not widened.
5. **20 bare expansions in dev/audit harness, rca and rounds scripts.** Dismissed: outside the `tools/**` scope the brief fixed.
6. **`scan("HEAD")` adds no .sh file to the entities.py closure.** Routed: the class barrier holds on every pull request through the governance `instrument-self-tests` step. The HEAD-versus-working-tree seam is carried to roster 9ddd1c689 R10-SUITE-HOST-DETERMINISM carry[5]. Carry: R10-SUITE-HOST-DETERMINISM

## Mutation proof

Failing test first: `python3 -I tools/audit/seat/bare_array.py --check --ref 6a988a237f91a853d006f7908e41cfbd30bc9bc9` rc 1, listing `body_patch.sh:98` and `pr_args.sh:249`; at 757c71eb the check is clean, and at the merge (before the post-merge commit) it listed the four main-side sites above (`tick_loop.sh` 96, 98, 111 and `app_approve.sh` 480), now rc 0.

Mutants, each applied in place and restored (`git diff --quiet`):
- Merge, this PR's side: delete the `# never-empty: d is the literal git diff command` line from `app_approve.sh`: `bare_array.py --check` lists `tools/pr/app_approve.sh:480`, rc 1.
- Merge, main's side: replace `norm()`'s `awk` stage with `cat`: `app_approve.sh --self-test` red on "CARRY: main rewrote a context line beside the branch's lines in a .md file (P17)" (316 checks, 1 failed).
- Round-2 `bare_array.py` mutants (review of 757c71eb, all killed): MA the reason-after-marker set emptied (self-test red on 3 rows, entities red on 3), MB `marked` ignores marker order (4 and 3), MC line-above reason ignored (red, `--check` lists `body_patch.sh:120`, `pr_args.sh:250`), MD `above` persists past the next line, ME files without `set -u` return `[]` (4 self-test rows, 3 entities rows), MF guard recognition dropped (red, 3 guarded sites listed). Round-1 mutants M1 to M6 stand as recorded by the round-1 review.
- `tick_loop.sh` guard: `${ARGV[@]+"${ARGV[@]}"}` reverted to bare makes `--check` list line 111 (the rule's own twin of this change, same predicate as MF).

## Null control

- Merge, main's side unchanged on a main-only input: `bash tools/pr/app_approve.sh --self-test` prints `app_approve self-test: 316 checks, 0 failed` at the head; the file differs from origin/main by the one comment line only.
- Merge, this PR's side present on a branch-only input: `python3 -I tools/audit/seat/bare_array.py --check` rc 0 with the reason and rc 1 without it (mutant above).
- `bash tools/audit/seat/tick_loop.sh --self-test`: `tick_loop self-test: 26 checks, 0 failed`.
- Self-test controls, green on unmutated code: the guarded form passes; a reason on the line passes; a reason on the comment line above passes; a reason before a mut marker passes; a file with `set -e` only is judged too; the guarded form passes in a file without `set -u` (null). Refusing twins: a marker with no reason; a reason above excuses only the line directly below (a blank line between is refused); a reason after a mut marker, in a judged file, on a line with no bare expansion, and on a guarded line.
- At the base, `--check --ref 3759d49a5` lists `tools/audit/seat/bus.sh` (the defect). No macOS bash 3.2 exists in this container, so the `bus.sh orphans` rc 0 run on 3.2 is not recorded; the static rule stands in for it.

## Figures

- Sites by the rule `python3 -I tools/audit/seat/bare_array.py --check --ref 3759d49a5` (every tracked tools script): 17 lines. Dispositions: `bus.sh` ledger call: guarded (the fix). `cloud-setup.sh` `parts`: guarded. `prepr.sh` `body_check` call with `reds`: guarded. Marked never-empty: `body_patch.sh` `args` (reason above, line ends in `# mut:contract`), `cloud_relay.sh` `upd`, `cloud-setup.sh` `vars` x3, `app_approve.sh` `d`, `prepr.sh` `args`, `TRANSPORT_ROOTS`, `PIPE_GREP_Q_FILES`. `pr_args.sh` (sourced, no `set -u` of its own, judged): `PR_FRESH_PATHS` guarded; the four `PR_REAP_PIDS`/`alive` sites marked with the early return that makes each non-empty (the KILL line's reason above, it ends in `# mut:grace`). At 1dae4b62f `--check` prints nothing, rc 0.
- Main-side sites added by the merge, same rule at the merge result: `tick_loop.sh` 96, 98, 111 and `app_approve.sh` 480, dispositioned in `## Head`.
- Mut-marker collision class, `grep -rnE '# mut:[A-Za-z0-9_-]+\s+\S' --include=*.sh tools dev .claude | wc -l`: 0 at the head (2 at the round-1 head).
- `grep -c "ok   bare_array"` on `PYTHONPATH=tests/hastub python3 tests/entities.py` output: 9 rows, each ok; the run ends `ALL 2602 ENTITY CHECKS PASSED`, rc 0.
- Residual seams: `tests/entities.py` reads blobs of HEAD (`scan("HEAD")`), so an uncommitted edit is judged at its last commit; `bare_array.py --check` with no ref reads the working tree. Carry: R10-SUITE-HOST-DETERMINISM (roster 9ddd1c689 carry[5], with its planted-defect control). The sourced-library seam is closed in code by 07f79c3cf (`pr_args.sh` is judged; mutant ME).
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL` (`tests/closure.py` changes the gate itself). `python3 tests/structure.py` STRUCTURE RATCHET PASSED. `tools/pr/prepr.sh` rc 0, `PRE-PR: 1dae4b62f59189943fe1038be2b7c6d69c3a2a2a` (closures step skipped by the script itself, a full derive being forbidden off the canonical environment; CI re-records). Claim files byte-identical to origin/main. The rest of the FULL suite is CI's.
- `tests/closures.json` changed in round 1 only (bare_array.py added to the `tests/entities.py` closure; checked by the round-1 review).

## Red checks

At 757c71eb905b9152d853054b754325d04206f8d1 (the previous head, whole check-run set, `merge_train.py classify`): GREEN, none concluded failure. At 1dae4b62f no check has concluded yet (the head is not pushed to the pull request branch), so none is red to name; a red there is the carry's owner's to answer.

Earlier reds, answered in round 2 and kept:
- `governance / instrument-self-tests` (red at 6a988a237f91a853d006f7908e41cfbd30bc9bc9): cause, the never-empty reasons appended after `# mut:contract` and `# mut:grace` unanchored both self-tests' end-anchored mutant locators. Cheaper detector: running every touched tool's `--self-test` before the handoff (`body_patch.sh --self-test`, `pr_args.sh --self-test`, plus `app_approve.sh` and `tick_loop.sh` at this head), a few minutes per handoff that edits a tool. The class is also refused statically by `bare_array.py --check`.
- `pr-contract / pr-contract` (same head): cause, the body's `## Red checks` said `none` while the check above was red. Cheaper detector: the same per-tool `--self-test` run.
- `gate` (same head): the aggregate of the two above.

## Forward-carry

none

## Friction

none
