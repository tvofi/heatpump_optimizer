`tools/audit/seat/bus.sh orphans` died on macOS bash 3.2 under `set -u` (`arms[@]: unbound variable`) whenever neither `--no-ancestry` nor `--no-content` was given, so `pulse.py`'s opener arm read UNREADABLE and orphaned handoffs were invisible (triage P303). Fix: the ledger.py call uses `${arms[@]+"${arms[@]}"}`. Class barrier: `tools/audit/seat/bare_array.py`, a static rule over every tracked `tools/**/*.sh` (a file with `set -u` may not expand a bare `"${a[@]}"` unless guarded, or unless `# never-empty: <reason>` sits on the line or on a comment-only line directly above it), pinned in `tests/entities.py`, run as a governance step and listed in `tools/audit/seat/INSTRUMENTS.md`. CI's bash 5 expands an empty array cleanly, so a run-time row would pass on the defect; the rule is therefore static. Design choices stated: a file without `set -u` is not judged (the sourced `pr_args.sh` is guarded or marked by hand, see Figures); a never-empty reason placed after a `# mut:<name>` marker is refused in every file, because the self-tests find their mutant line by that marker at the line's end. Alternative rejected: plain variables in bus.sh lose the two-flag list the call forwards; the guard is the smaller change.

Carry 1 (the roster's carry from the R10-FLY-RAISE-REVIEWABLE round-2 fixer: `bus.sh orphans` fails on a macOS seat with `arms[@]: unbound variable`, with a bash-3.2 self-test row and a non-empty-array null control asked for): the empty-array expansion is guarded in `bus.sh orphans` as described above. Departure, stated: the pin is the static `bare_array.py` rule rather than a self-test row run under `/bin/bash 3.2`, because CI's bash 5 expands an empty array cleanly and a run-time row would pass on the defect; the rule's self-test and the `tests/entities.py` rows carry the null control (the guarded form and a non-empty array are not refused). The reviewer decides whether that departure discharges the carry.

## Head

07f79c3cf11335c49355c094105a35e6b8367614 (handoff re-publish by the opener seat, 2026-11-01): two fixer commits sit on the head this body was written at (b2d4905d, merged as 07280b77b): b93a1d4c3 (bare_array: refuse a never-empty reason after a mut marker in a set -u file too) and 07f79c3cf (bare_array: judge every tracked tools script, set -u or not; adds zero sites at this head). The sections below were measured at b2d4905d and are not re-measured by this seat; the Carry destinations are re-pointed from the done group R10-FLY-SUITE-ENV-FLAKES to the live group R10-SUITE-HOST-DETERMINISM. The pull request's push re-runs prepr at this head.

b2d4905d394a2b06618ba3fbffdf9f0463a46ca6 (round 2: the round-2 commit 6f95914c294da3183eabe4f709e0962e91704ebf on the round-1 head 6a988a237f91a853d006f7908e41cfbd30bc9bc9, then origin/main f3c9144b80883ae510f0207c30855b8c93c51a0a merged in, stamped 2026-10-31T21:54Z). origin/main had moved by the handoff check (it was a7dd7f50d at the round-1 review), so it was merged (no conflict; it touches nothing under `tools/`, and of the gate files only `tests/closures.json` and `tests/structure_budgets.json`) and every check below was re-run at this head. Self-disclosed: `handoff/r10-fly-bus-bash32` was pushed once at 6f95914c2 before main's move was seen; this head fast-forwards it.

## Round-1 findings, all answered

1. **Regression, the never-empty markers unanchored `mut:contract` and `mut:grace`.** Taken: the reason moves to a comment-only line directly above each marked line, and `bare_array.py` reads a reason there (`sites`: the `above` flag excuses exactly the next line); a reason that follows a `# mut:` marker on its line no longer excuses and is refused in every file, judged or not (`marked` and the `tails` list), so the collision cannot recur. Why this over the alternatives: `... # never-empty: <reason>  # mut:contract` (reason before the marker) satisfies both regexes, but leaves two conventions sharing one line whose order is the only thing keeping a mutant pinned, which is exactly the coupling that broke; the preceding-line form keeps `# mut:<name>` alone at the end, which `pr_args.sh`'s header states as the rule, and is also accepted (self-test "a reason before the mut marker excuses"). Teaching the self-test locators to tolerate a trailing comment was rejected: it changes five locators in two instruments to fit one checker. Locator counts at this head: `grep -c '# mut:contract$' tools/audit/seat/body_patch.sh` 1, `grep -c '# mut:grace$' tools/audit/seat/pr_args.sh` 1 (0 and 0 at the round-1 head, per the verdict's ev/mut_locator.txt).
2. **Red check unanswered.** Answered in `## Red checks` below: `governance / instrument-self-tests` and `pr-contract / pr-contract`, each with its cause and the cheaper detector.
3. **Instrument unlisted.** `tools/audit/seat/INSTRUMENTS.md` lists `bare_array.py` under `## tools/audit/seat/`, with its page `tools/audit/seat/instruments/bare_array.py.md` (classified inert by `tests/closure.py` `is_inert`, as every instruments page is). `python3 tools/audit/seat/selftest_wiring.py --check`: 0 unwired, 0 index gaps.
4. **Matcher false-negative domain** (`set -e -o nounset`, `#!/bin/bash -u`, unquoted or embedded `${a[@]}`, slices). Dismissed, with the verdict: no live site at the head (the verdict's ev/enum_tools.txt); the only live forms outside the matcher are `train.sh`'s two slices inside a length-checked loop. Not widened here; the orchestrator may route it to R10-SUITE-HOST-DETERMINISM.
5. **20 bare expansions under `set -u` in dev/audit harness, rca and rounds scripts.** Dismissed, with the verdict: outside the `tools/**` scope the brief fixed; none is a seat instrument the operator runs on macOS.
6. **`scan("HEAD")` adds no .sh file to the entities.py closure.** Routed: the class barrier holds on every pull request through the governance `instrument-self-tests` step, which has no job-level `if:`; the HEAD-versus-working-tree seam is carried. Carry: R10-SUITE-HOST-DETERMINISM

## Mutation proof

Failing test first for round 2: `python3 -I tools/audit/seat/bare_array.py --check --ref 6a988a237f91a853d006f7908e41cfbd30bc9bc9` rc 1, listing `tools/audit/seat/body_patch.sh:98` and `tools/audit/seat/pr_args.sh:249` (each a never-empty reason after its mut marker); at this head `--check` rc 0 with no output.

Mutants of the round-2 lines of `bare_array.py`, each applied in place and restored (`git diff --quiet` afterwards):
- M7, `marked` ignores marker order (`return bool(mark)`): self-test red on "a reason after a mut marker does not excuse: it unanchors the mutant" and "a reason after a mut marker is refused in an unjudged file too".
- M8, the line-above reason ignored (`if comment or marked(line):`): self-test red on "a reason on the comment line above excuses the next line (null)", and `--check` rc 1 at `tools/audit/seat/body_patch.sh:99`.
- M9, unjudged files return `[]`: self-test red on "a reason after a mut marker is refused in an unjudged file too".
`tests/entities.py` calls `_ba.self_test` as the row "bare_array: its own self-test passes", so each mutant is red there too; its two new rows are "a never-empty reason after a mut marker is refused (it unanchors the mutant)" and "a reason on the line above keeps the mut marker last (control)".

The round-1 mutants of `sites` (guard recognition dropped, `sites` returning `[]`) stand as recorded by the round-1 review (its ev/mutants.txt: M1 to M6 killed).

The production predicates the regression unpinned are pinned again, `env -u BASH_ENV`:
- `bash tools/audit/seat/body_patch.sh --self-test`: `body_patch self-test: 64 checks, 0 failed`, rc 0 (round-1 head: 1 failed, `FAIL mutant lint changed nothing`).
- `bash tools/audit/seat/pr_args.sh --self-test`: `pr_args self-test: 158 checks, 0 failed`, rc 0, including `ok mutant mut:grace (the KILL line deleted): the TERM-proof child survives` (round-1 head: 1 failed on that line).
- `python3 -I tools/audit/seat/bare_array.py --self-test`: `bare_array self-test: ok`, rc 0.

## Null control

Controls driven by the self-test, green on the unmutated code: the guarded form passes; `# never-empty: <reason>` on the line passes; a reason on the comment line above passes; a reason before a mut marker passes; a file with `set -e` only is not judged. Their refusing twins: a marker with no reason does not excuse; a reason above excuses only the line directly below it (a blank line between is refused); a reason after a mut marker is refused. At the base, `python3 -I tools/audit/seat/bare_array.py --check --ref 3759d49a5` lists `tools/audit/seat/bus.sh` (line 654). No macOS bash 3.2 exists in this container, so the `bus.sh orphans` rc 0 run on 3.2 is not recorded; the static rule stands in for it.

## Figures

- Sites, by the rule's own enumeration `python3 -I tools/audit/seat/bare_array.py --check --ref 3759d49a5` (set -u files only), each against its disposition: bus.sh ledger call: guarded (the fix). cloud-setup.sh `parts`: guarded. prepr.sh body_check call with `reds`: guarded. Marked never-empty with the reason on the line: body_patch.sh `args` (reason on the line above, the line ends in `# mut:contract`), cloud_relay.sh `upd`, cloud-setup.sh `vars` x3, app_approve.sh `d`, prepr.sh `args`, `TRANSPORT_ROOTS`, `PIPE_GREP_Q_FILES`. pr_args.sh has no `set -u` of its own but is sourced into set -u callers: `PR_FRESH_PATHS` guarded; the four `PR_REAP_PIDS`/`alive` sites marked with the early return that makes each non-empty (the KILL line's reason on the line above, it ends in `# mut:grace`). At this head `--check` prints nothing, rc 0.
- The mut-marker collision class, by the rule `grep -rnE '# mut:[A-Za-z0-9_-]+\s+\S' --include=*.sh tools dev .claude` (a mut marker not at its line's end): at the round-1 head, 2 lines (body_patch.sh:98, pr_args.sh:249), both closed in this diff; at this head, none, and `bare_array.py --check` now refuses any such line that carries a never-empty reason.
- Residual seams: `tests/entities.py` reads blobs of HEAD (`scan("HEAD")`), so an uncommitted edit is judged at its last commit; `bare_array.py --check` with no ref reads the working tree. A sourced library with no `set -u` of its own is not judged for bare expansions (pr_args.sh was classified by hand). Carry: R10-SUITE-HOST-DETERMINISM
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL` (`tests/closure.py` changes the gate itself). Ran locally: `PYTHONPATH=tests/hastub python3 tests/entities.py` rc 0, `ALL 2501 ENTITY CHECKS PASSED`, its seven `bare_array:` rows (`grep -c "ok   bare_array"` on the log) and the class row each `ok`, `python3 tests/structure.py` STRUCTURE RATCHET PASSED, `tools/pr/prepr.sh <body>` rc 0, `PRE-PR: b2d4905d394a2b06618ba3fbffdf9f0463a46ca6` (its only WARN the push order this handoff discharges); the rest of the FULL suite is CI's.
- `tests/closures.json` is unchanged in round 2; its round-1 change (bare_array.py added to the `tests/entities.py` closure) was checked correct by the round-1 review (its ev/closure.txt).

## Red checks

- `governance / instrument-self-tests` (red at 6a988a237f91a853d006f7908e41cfbd30bc9bc9): cause, the never-empty reasons appended after `# mut:contract` and `# mut:grace` unanchored both self-tests' end-anchored mutant locators, so `body_patch.sh --self-test` and `pr_args.sh --self-test` each failed one mutant. Cheaper detector: running every touched tool's `--self-test` before the handoff (`bash tools/audit/seat/body_patch.sh --self-test`, `bash tools/audit/seat/pr_args.sh --self-test`), at a standing cost of a few minutes per handoff that edits a tool; it was not run in round 1 and is run in round 2 (Mutation proof). The class is now also refused statically by `bare_array.py --check`.
- `pr-contract / pr-contract` (red at 6a988a237f91a853d006f7908e41cfbd30bc9bc9): cause, the body's `## Red checks` said `none` while `governance / instrument-self-tests` was red. Cheaper detector: the same per-tool `--self-test` run before the handoff, whose red the body would then have named; this body names it.
- `gate` (red at the same head): the aggregate of the two above.

## Forward-carry

none

## Friction

none
