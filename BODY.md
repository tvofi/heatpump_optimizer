R10-PREPR-DARWIN-SELFTEST-LANE (re-cut by triage r10-round-end P761; the paid macOS lane is refused, so this builds the pre-merge detectors): the round-10 macOS-only `prepr.sh --self-test` class and the pipefail-sigpipe family get one diff-scoped shell-hazard lint, and the static half of `harness_headers` runs in prepr.

Carries as dispositioned: Carry 0 and Carry 2 (duplicates) are the stub rule and the raw-wc lint, built. Carry 1: (a) built, (b) void with the lane. Carry 3 is item (d), `inline_walk_line` as prepr step 3f9. Carry 4 is the same item and its instance f0b75645 (a drifted inlined walk) is the arm the step's scratch row plants. Carry 5 is the widened macOS leg, void with the refused lane (triage P761, tvofi 2026-11-15). Carry 6 is the early-pipe rule, built; its existing sites are not judged.

## Head

3d12f40a506961f777d05c101c4a6db57102911f (repair, round 3, of e0238c1fe8bc36541e3ecb9fea4c1e59e71e5245, blocked by verdict/3639 as mutation-vacuous: one commit on it, two added lines in `self_test()` of `tools/audit/seat/shell_hazard.py`, no production line changed; `git merge-tree --write-tree origin/main HEAD` reported no conflict, so main is not merged). The figures in the sections below that were not re-measured describe the unchanged rest of the diff.

prepr: passed rc=0 at 3d12f40a506961f777d05c101c4a6db57102911f

## Mutation proof

Round 3, the survivor: in `string_compared()`, replacing the last-opener loop (`opener = None` / `for opener in TEST_OPEN.finditer(pre): pass`) with `opener = TEST_OPEN.search(pre)` (the first opener) left `--self-test` at ok. The repair is one self-test row: `[ "$a" = b ] && [ "$(wc -l <f)" = 3 ]` must be refused. Failing test first: with the row added and the first-opener mutant applied, `--self-test` printed `FAILED` (rc 1) with one FAIL row, that row, `got [], want ['wc-compare']`. Null control: the same row at the unmutated head passes, `shell_hazard self-test: ok` (rc 0); and the first-opener mutant without the row still prints ok (rc 0), so the row is what kills it.

The reviewer's mutant replacements (ev/mutants.txt, ev/mutants2.txt), re-run at 3d12f40a50, one replacement on the file, then `--self-test`, then restore; the count is FAIL rows, not counting the summary line: `STR_SUBJECT` always False: killed, 5. `STR_SUBJECT` without `case`: killed, 1. Without `st`: killed, 4. Closed-bracket check removed: killed, 1. Opener-None check removed: killed, rc 1 with 0 rows (the run raises on `None.end()`). `STR_OP_AFTER` removed: killed, 54. `STR_OP_BEFORE` removed: killed, 50. `!=` dropped from `STR_OP_AFTER`: killed, 18; from `STR_OP_BEFORE`: killed, 17. `==` dropped from `STR_OP_AFTER`: killed, 18. First opener instead of last: killed, 1 (was the survivor). `TEST_OPEN` without `[[`: killed, 50. `NORMALISE` exemption removed: killed, 3. `RAW` exemption removed: killed, 1. `string_compared` always True: killed, 199. `break` removed: survived, 0 (dismissed by the reviewer, not touched). Unmutated control: ok, rc 0. The file keeps no mutant list, so none was extended.

Round 2:

The block: deleting ` or NUMERIC.search(line)` left `--self-test` at ok, and the line-wide search excused a raw wc string compare on any line also holding `-eq`, `((` or `$((`. The repair deletes `NUMERIC` and the line-wide `STRING_CMP`. A new `string_compared(line, m)` judges only the compare that holds the substitution: it is `st`'s or `case`'s subject (`STR_SUBJECT`), or a side of `=`, `==` or `!=` (`STR_OP_AFTER`, `STR_OP_BEFORE`) inside the `[`/`[[` test that holds it (`TEST_OPEN`, and no `]` between that opener and the substitution).

Failing test first: at 296a0a30d4 with only the new rows added, `--self-test` printed `FAILED` with three FAIL rows: `st "$(a | wc -l)" 0 m && [ $n -eq 0 ]` passed and `[ "$(wc -l <f)" = 3 ] || exit $((1))` passed (both should be refused), and `[ -n "$x" ] && echo "$(wc -l <f)" = 3` was refused (should pass).

Mutants, one replacement per predicate on the file, then `python3 -I tools/audit/seat/shell_hazard.py --self-test`, then restore; the count is the `FAIL` rows printed, not counting the summary line. Every mutant exited rc 1:
- `STR_SUBJECT` limited to `st` (the `case` arm gone): 1; limited to `case`: 4; the `STR_SUBJECT` arm deleted: 5.
- `TEST_OPEN` without `[[`: 50. The test-bracket requirement dropped (`opener is not None and ...`): 1, the `(( == ))` null row. The closed-bracket check dropped: 1, the `echo ... =` null row.
- `STR_OP_AFTER` never matching: 53; `STR_OP_BEFORE` never matching: 50; `==` dropped from the operator: 18; `!=` dropped: 18; `-eq` added as a string operator: 19.
- The operator search widened back to the whole line: 50. The line-wide `NUMERIC` exemption re-added: 51 (the verdict's survivor, now killed).
- `string_compared` returning False: 107. The unchanged predicates, re-measured: `EARLY` 6, `STUB_WC` 1, `RAW` 1, `DRAINED` 1, `NORMALISE` 3.

A generated spelling corpus drives the rule: `[`/`[[` x double-quoted or bare substitution x left or right side x nine operators (`=`, `==`, `!=`, `-eq`, `-ne`, `-lt`, `-gt`, `-le`, `-ge`) x four tails (none, `&& [ $n -eq 0 ]`, `|| exit $((1))`, `|| [ "$a" = b ]`), 288 lines; the self-test asserts the count and zero misjudged. Null control: the same corpus through 296a0a30d4's `hazards()` misjudges 48 of 288, every one a string compare with a numeric tail.

## Null control

Instance heads, `shell_hazard.py --check --base <parent> --head <commit>` at the commit that reached CI or macOS, then at its repair: `003f89cf9c^..003f89cf9c` refuses `tools/pr/prepr.sh:2396: wc-compare` (#3455); `1386441425^..1386441425` refuses `:2405: wc-stub` and `:2406: wc-compare`; `09b7856fc0^..09b7856fc0` refuses `tools/pr/app_approve.sh:303: early-pipe` (the carry-tip read); the repair `cb803e9eed^..cb803e9eed` prints no `app_approve.sh` line (the here-string passes). Null controls inside the self-test: the stripped compare, a numeric `-eq` test, a numeric compare of wc beside an unrelated string compare, `(( $(wc -l <f) == 3 ))`, `$(( $(wc -l <f) + 1 ))`, an `=` outside any test bracket, a here-string, `|| true`, a `# pipe-small:` reason, a `# wc-raw:` reason, and `c8780ea33d`'s stub, each pass; a marker with no reason does not excuse. The diff scope is a scratch repository: only added lines of nested `tools/**/*.sh` are named, not the old line, a `.py` or a root `.sh`. `inline_scan` in prepr: a scratch tree whose copies match passes, one planted line in a harness's `repo_root` is refused and named.

Stub host-independence rule (carry 0): in `tools/audit/seat/instruments/shell_hazard.py.md`, enforced by the `wc-stub` and `wc-compare` rules. Why not `tests/README.md`: it is at its per-file token cap (`policy_lint.mjs --budgets`), and the section took it 190 tokens over; the instrument record has no cap.

Brief item (a): the RCA body is landed verbatim as `dev/audit/rca/R10-RCA-PREPR-DARWIN-SELFTEST.md` (`git show cce3f946f5e8b48497e2f89486bbf4798a44c6e2:BODY.md`, diff identical); class `N-host-platform-unrun` is new in `bugclasses.json` (no class named macOS-only prepr self-test failures) with its `_rca` index and the id in `finding.schema.json`, `audit-find.js` synced by `fold_ledger.py sync`. Its three instances are process incidents, not counted in `total`, as `R10-SELFTEST-RED-INTRODUCED` does.

## Figures

- Standing cost per prepr run: `time python3 -I tools/audit/seat/shell_hazard.py --check --base origin/main` printed 0.044 s real; `time python3 -I -c "import sys; sys.path.insert(0,'tests'); import harness_headers; raise SystemExit(harness_headers.inline_scan())"` printed 0.897 s real; together 0.94 s, under the one-second bound, on this container. Null control: the bound would be false at 1.0 s or over; `inline_scan` is 0.45 s `depth_root_seams` plus 0.4 s the walk compare, so it has under 0.1 s of headroom here.
- Shadow count (L2, the lint over the last 20 first-parent merges of origin/main at the merge base, each `shell_hazard.py --check --base <m>^1 --head <m>^2`): the number of merges with at least one refusal is printed by `for m in $(git log --first-parent --merges --format=%h -20 origin/main); do ...; done | awk`; it read 2 of 20 (a39627da59 with 11 early-pipe lines in `bus.sh`, dc46b1222f with 1 in `remerge_main.sh`); the hits are real early-exit pipes, the way out is a here-string or `# pipe-small:`. Null control: the same loop at a merge adding no shell line prints 0.
- Seam census (fixer.md step 8): `git grep -nE '\|[[:space:]]*grep[[:space:]]+-[a-zA-Z]*q' -- tools/pr tools/audit/seat` lists the existing early-pipe sites; they are not judged (only added lines), a distinct finding by id P761 carry 6, closed by the lint for new lines only. The existing `wc` seam: the RCA found one site (#3455), repaired on main by `c8780ea33d`.
- T_mac and the lane's break-even are void with the lane (carry 1 void by triage).
- `python3 tools/audit/fold_ledger.py check` printed `0 violation(s)`; `node tools/policy/check-wave-script.mjs` printed `223 passed, 0 failed`; `python3 tests/structure.py` and `GOLDEN_MODE` are untouched (no production file moved).

## Unpinned sites

- `NUMERIC.search(line)` in `hazards()` (verdict/3639's round-1 survivor): deleted, with the line-wide `STRING_CMP` it qualified. Its replacement's predicates are each killed above, the last-opener loop by the round-3 row.
- The `break` after `out.append((n, "wc-compare", ...))` in `hazards()`: removing it survives the self-test. Disposition: a value check, dismissed by the round-2 reviewer: without it a line with two raw wc compares yields a duplicate report line on a line already refused, so no refusal changes.
- prepr step 6d', `MUTANT_CMD="python3 -I tools/audit/seat/shell_hazard.py --self-test"` at 8d2eb5c41a, printed 11 `SURVIVED` lines (the round-3 row shifts the later self-test line numbers by 2), all inside `self_test()` and none in `hazards()` or `string_compared()`: `shell_hazard.py:134` GUARD_OFF (`if got != want:` in the `st` helper) and `:135` CALL_DEL (its `fails.append`) disable the assertion itself; `:143`-`:147` and `:155`-`:158` CALL_DEL each delete one self-test row. Disposition: a value check. A mutant of the self-test's own assertion or rows cannot be killed by that same self-test. Each deleted row is the check that kills a production mutant named in the Mutation proof (for example `:158`, the `case` row, is the one row that kills M1 `STR_SUBJECT` limited to `st`), and those production mutants were run on the file by hand above, each rc 1.
- `test "$(wc -l <f)" = 3`, which the verdict names as optional and outside the stated rule: not matched (the rule knows `st`, `case`, `[` and `[[`). Left alone, as the brief scopes this repair to the numeric exemption.

## Red checks

- `governance / instrument-self-tests` (job 132987213402, at 78e5780100), red at the head and not at the merge base. Cause: `tools/ci/selftest_closures.json` was stale. The diff added `python3 -I tools/audit/seat/shell_hazard.py --self-test` to the run text of step `bare-array-expansion` in `.github/workflows/governance.yml`, so that step's recorded `run_sha` no longer matched and the table was refused. Repair: `python3 -I tools/ci/selftest_scope.py record --step bare-array-expansion` on Linux under strace (commit 53d750ded4). The three-dot diff of the table moves only that entry: its `run_sha`, plus `tools/audit/seat/shell_hazard.py` added to its `files`. Control: `python3 -I tools/ci/selftest_scope.py static` at 78e5780100 printed `STALE ... ['bare-array-expansion']` and `1 problem(s)` (rc 1). At the new head it prints `0 problem(s)` (rc 0). Cheaper detector: run `selftest_scope.py static` locally in prepr whenever a diff changes a `run:` text in `governance.yml`. It is a static read with no strace that names the step to re-record before CI runs. Standing cost: `time python3 -I tools/ci/selftest_scope.py static` printed 0.084 s real at this head, on this container. `git grep -n selftest_scope tools/pr/prepr.sh` prints nothing, so no local path runs it today. Re-recording stays Linux-only, which is why the detector is the static check and not the record. Process state (a): no local process re-read the table after a run-text edit.

## Forward-carry

- The GNU-only `sed -i` sites at `tools/audit/seat/pr_args.sh` stay unverified on macOS; the lint does not cover them (named in the instrument record). Carry: dismissed: the paid macOS lane is refused (tvofi 2026-11-12) and macOS-only checks run on local seats
- A count assigned to a variable and compared later is not seen by `wc-compare` (named in the instrument record). Carry: dismissed: a static rule over one line; no instance of the shape in the class

## Friction

none
