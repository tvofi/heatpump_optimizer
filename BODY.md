R10-PREPR-DARWIN-SELFTEST-LANE (re-cut by triage r10-round-end P761; the paid macOS lane is refused, so this builds the pre-merge detectors): the round-10 macOS-only `prepr.sh --self-test` class and the pipefail-sigpipe family get one diff-scoped shell-hazard lint, and the static half of `harness_headers` runs in prepr.

Carries as dispositioned: Carry 0 and Carry 2 (duplicates) are the stub rule and the raw-wc lint, built. Carry 1: (a) built, (b) void with the lane. Carry 3 is item (d), `inline_walk_line` as prepr step 3f9. Carry 4 is the same item and its instance f0b75645 (a drifted inlined walk) is the arm the step's scratch row plants. Carry 5 is the widened macOS leg, void with the refused lane (triage P761, tvofi 2026-11-15). Carry 6 is the early-pipe rule, built; its existing sites are not judged.

## Head

f9f1537051f60d87f13f5e070575bfb85562d2ee (repair of 78e578010065c691fd66032154fe0ddcca6453f1: one re-record commit 53d750ded4, then a merge of origin/main e352724335c136b65562cd3e71f728549ad04a82, forced by a conflict `git merge-tree --write-tree origin/main HEAD` reported in `.claude/workflows/audit-find.js`; measured 2026-11-16, `date -u`). The conflict is the generated FINDING-SCHEMA block: main's side taken, then `python3 tools/audit/fold_ledger.py sync` rewrote it from the merged `finding.schema.json` (`fold_ledger.py check` printed `0 violation(s)`; `node tools/policy/check-wave-script.mjs` printed `249 passed, 0 failed`). The figures below the Red checks section were measured at fe7cb1beb3 and describe the unchanged diff; the merge touched none of its files but the generated block.

## Mutation proof

Each mutant is one predicate of `tools/audit/seat/shell_hazard.py` made inert by `sed` on a copy, then `python3 -I tools/audit/seat/shell_hazard.py --self-test`, then restored: `STRING_CMP.search(line)` replaced by `False` (5 rows red: the #3455 compare, the bracket compare and the diff-scope row among them); `pipefail and EARLY.search` (7 red); `STUB_WC.search` (2 red, the padded stub row among them); `or RAW.search(line)` (2 red, the wc-raw null control); `and not DRAINED.search` (2 red, the drained-pipe null control). No mutant printed "ok". prepr's own rows (`hazard_line`, `inline_walk_line`, and each step's call site) are in `bash tools/pr/prepr.sh --self-test`.

## Null control

Instance heads, `shell_hazard.py --check --base <parent> --head <commit>` at the commit that reached CI or macOS, then at its repair: `003f89cf9c^..003f89cf9c` refuses `tools/pr/prepr.sh:2396: wc-compare` (#3455); `1386441425^..1386441425` refuses `:2405: wc-stub` and `:2406: wc-compare`; `09b7856fc0^..09b7856fc0` refuses `tools/pr/app_approve.sh:303: early-pipe` (the carry-tip read); the repair `cb803e9eed^..cb803e9eed` prints no `app_approve.sh` line (the here-string passes). Null controls inside the self-test: the stripped compare, a numeric `-eq` test, a here-string, `|| true`, a `# pipe-small:` reason, a `# wc-raw:` reason, and `c8780ea33d`'s stub, each pass; a marker with no reason does not excuse. The diff scope is a scratch repository: only added lines of nested `tools/**/*.sh` are named, not the old line, a `.py` or a root `.sh`. `inline_scan` in prepr: a scratch tree whose copies match passes, one planted line in a harness's `repo_root` is refused and named.

Stub host-independence rule (carry 0): in `tools/audit/seat/instruments/shell_hazard.py.md`, enforced by the `wc-stub` and `wc-compare` rules. Why not `tests/README.md`: it is at its per-file token cap (`policy_lint.mjs --budgets`), and the section took it 190 tokens over; the instrument record has no cap.

Brief item (a): the RCA body is landed verbatim as `dev/audit/rca/R10-RCA-PREPR-DARWIN-SELFTEST.md` (`git show cce3f946f5e8b48497e2f89486bbf4798a44c6e2:BODY.md`, diff identical); class `N-host-platform-unrun` is new in `bugclasses.json` (no class named macOS-only prepr self-test failures) with its `_rca` index and the id in `finding.schema.json`, `audit-find.js` synced by `fold_ledger.py sync`. Its three instances are process incidents, not counted in `total`, as `R10-SELFTEST-RED-INTRODUCED` does.

## Figures

- Standing cost per prepr run: `time python3 -I tools/audit/seat/shell_hazard.py --check --base origin/main` printed 0.044 s real; `time python3 -I -c "import sys; sys.path.insert(0,'tests'); import harness_headers; raise SystemExit(harness_headers.inline_scan())"` printed 0.897 s real; together 0.94 s, under the one-second bound, on this container. Null control: the bound would be false at 1.0 s or over; `inline_scan` is 0.45 s `depth_root_seams` plus 0.4 s the walk compare, so it has under 0.1 s of headroom here.
- Shadow count (L2, the lint over the last 20 first-parent merges of origin/main at the merge base, each `shell_hazard.py --check --base <m>^1 --head <m>^2`): the number of merges with at least one refusal is printed by `for m in $(git log --first-parent --merges --format=%h -20 origin/main); do ...; done | awk`; it read 2 of 20 (a39627da59 with 11 early-pipe lines in `bus.sh`, dc46b1222f with 1 in `remerge_main.sh`); the hits are real early-exit pipes, the way out is a here-string or `# pipe-small:`. Null control: the same loop at a merge adding no shell line prints 0.
- Seam census (fixer.md step 8): `git grep -nE '\|[[:space:]]*grep[[:space:]]+-[a-zA-Z]*q' -- tools/pr tools/audit/seat` lists the existing early-pipe sites; they are not judged (only added lines), a distinct finding by id P761 carry 6, closed by the lint for new lines only. The existing `wc` seam: the RCA found one site (#3455), repaired on main by `c8780ea33d`.
- T_mac and the lane's break-even are void with the lane (carry 1 void by triage).
- `python3 tools/audit/fold_ledger.py check` printed `0 violation(s)`; `node tools/policy/check-wave-script.mjs` printed `223 passed, 0 failed`; `python3 tests/structure.py` and `GOLDEN_MODE` are untouched (no production file moved).

## Red checks

- `governance / instrument-self-tests` (job 132987213402, at 78e5780100), red at the head and not at the merge base. Cause: `tools/ci/selftest_closures.json` was stale. The diff added `python3 -I tools/audit/seat/shell_hazard.py --self-test` to the run text of step `bare-array-expansion` in `.github/workflows/governance.yml`, so that step's recorded `run_sha` no longer matched and the table was refused. Repair: `python3 -I tools/ci/selftest_scope.py record --step bare-array-expansion` on Linux under strace (commit 53d750ded4). The three-dot diff of the table moves only that entry: its `run_sha`, plus `tools/audit/seat/shell_hazard.py` added to its `files`. Control: `python3 -I tools/ci/selftest_scope.py static` at 78e5780100 printed `STALE ... ['bare-array-expansion']` and `1 problem(s)` (rc 1). At the new head it prints `0 problem(s)` (rc 0). Cheaper detector: run `selftest_scope.py static` locally in prepr whenever a diff changes a `run:` text in `governance.yml`. It is a static read with no strace that names the step to re-record before CI runs. Standing cost: `time python3 -I tools/ci/selftest_scope.py static` printed 0.084 s real at this head, on this container. `git grep -n selftest_scope tools/pr/prepr.sh` prints nothing, so no local path runs it today. Re-recording stays Linux-only, which is why the detector is the static check and not the record. Process state (a): no local process re-read the table after a run-text edit.

## Forward-carry

- The GNU-only `sed -i` sites at `tools/audit/seat/pr_args.sh` stay unverified on macOS; the lint does not cover them (named in the instrument record). Carry: dismissed: the paid macOS lane is refused (tvofi 2026-11-12) and macOS-only checks run on local seats
- A count assigned to a variable and compared later is not seen by `wc-compare` (named in the instrument record). Carry: dismissed: a static rule over one line; no instance of the shape in the class

## Friction

none
