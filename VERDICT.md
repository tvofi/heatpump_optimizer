Fix review: merge de676fcc705b4f791d7588c14a9348f9fc700363

bus-nonce: 7e546b2dddedd4cdce42d86b8d4d559b

## Round

This is the review of the body's round six (round-six repair of round four's red; round five was blocked at `a11db7fe`). Measured at head `de676fcc705b4f791d7588c14a9348f9fc700363`, still the PR head when this was written (`ev/head-at-verdict.txt`). Role contract current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.

## Findings

- Surviving mutant on an added line: deleting `[ -z "${PR_ATTEMPT:-}" ] || return 0` from `op_close_unrowed` (open_pr.sh:60 at the head) leaves `bash tools/audit/seat/open_pr.sh --self-test` at rc=0, `158 checks, 0 failed` (`ev/mut-own-attemptguard.txt`). PR state cannot go wrong under it on the current tree, because the success path's last act is `PR_ATTEMPT=opened` and origin's tip is then `H`, so the mutant routes to `op_row_landed`. But every successful open would then print a false `open_pr: ROW LANDED: ... the row push then failed` line, or `ROWLESS` if `ls-remote` fails. No arm asserts that a successful open prints neither line. The fix is to make `racerun -` assert `! grep -qF 'ROW LANDED'` and pin the line as `# mut:attemptguard`. Carry: R10-FLY-OPENPR-ATOMIC
- The unreadable-tip branch (`tip=unread`) is unpinned, as the body's `## Unpinned sites` discloses. My own mutant, which deletes `&& [ "$tip" != unread ]`, draws no FAIL in the opener's arms. Its one FAIL is the unrelated timing arm `mutant mut:unlock ... the holder is still alive when the run returns` (`ev/mut-own-unread.txt`), which I read as a flake, not a kill. Carry: R10-FLY-OPENPR-ATOMIC
- Deferred by the body and left on the roster: carry 4 (P71, default Closes from roster `fixes`), carry 6 (V64, auto-open in `cloud_relay.sh`), carry 7 (V141, delete a merged leftover branch; until it lands, a re-run after a close opens from `fix/<topic>-pr`) and carry 8's `handoff_push.sh` seams. Carry: R10-FLY-OPENPR-ATOMIC
- The body's root-cause answer for the round-five red on `governance / instrument-self-tests` names process state (a): no local step maps a changed seat script to the instrument self-tests that read its text. It defers the countermeasure and its cost test to a root-cause seat, and nothing is built here. Carry: R10-FLY-OPENPR-ATOMIC
- The body quotes the class-rule-1 output as lines 120-141. That `awk` rule prints 121-142 both at the head and at the code head `ba4a8320` (`ev/class-rule-1.txt`). The line-by-line dispositions still map one to one, shifted by one. Carry: dismissed: off-by-one line numbers, enumeration content and dispositions unchanged

## Evidence

- RESULT head self-test: `bash tools/audit/seat/open_pr.sh --self-test` rc=0, `delivery_row self-test: 6 checks, 0 failed`, `pr_args self-test: 158 checks, 0 failed`, 164 `  ok` lines. These match the body (`ev/selftest-head.txt`, `ev/local-runs.txt`).
- RESULT ledger: `ledger self-test: 77 checks, 0 failed`. RESULT `r10_ledger_mutants self-test: 135 checks, 0 failed`.
- RESULT mutation proof (step 1), each named `# mut:` line deleted from open_pr.sh at the head:
  - roworigin: rc=1, 1 failed (the post-push arm).
  - trapclose: rc=1, 5 failed.
  - rowclose: rc=1, 3 failed.
  - rowreset: rc=1, 2 failed.
  - mergeabort: rc=1, 1 failed (the conflict arm).
  - `PR_EXIT_FIRST=` deleted from pr_args.sh: rc=1, 8 failed.
  - `r10_ledger_mutants.py O1_no_attempt_on_exit`: `RESULT mutant=O1_no_attempt_on_exit rc=1 fails=3`, `plants: 1, without a FAIL line: none`.
  - The body's counts for trapclose (5) and the `PR_EXIT_FIRST` deletion (8) re-derive exactly. All files were restored and `git status --porcelain` is empty.
- RESULT failing-test-first: open_pr.sh taken from `a11db7fe` gives rc=1, `158 checks, 1 failed`, and the FAIL is `open_pr: a row push that lands on origin and then fails leaves the PR open with its row, and says so`. This matches the body.
- Finder's harness: none named in the packet. The finding's harness is the in-tree self-test arm built from round five's review probe (`p2postfail`), disclosed as such in the body.
- Class (step 6): rule 1 (`awk` over open_pr.sh) returns the N=..PR_ATTEMPT range, and every line is dispositioned in the body (see the offset under Findings). Rule 2 returns 8 `app_push.sh` sites (537, 541, 545, 548, 350, 351, 364, 366), the same as the body. The close keys on origin's tip, not on which site fired, so every site is covered by the one tip read. No seam is open.
- `ledger.py attempt` takes free text for the outcome (`attempts()` stores it verbatim, and `escalate` prints it as `last attempt <x>`), so the new `closed,PR=N` value is accepted.
- Merge (step 13): `git merge-tree --write-tree origin/main de676fcc...` exits 0 against origin/main `ca0a6cfbc2e5538e6e2220793831443719ff6e98` (`ev/merge-tree.txt`). There is no conflict, so the claim driver was not invoked.
- Step 5: `git diff --stat <mb>...HEAD -- VERSION RELEASE_NOTES.md tests/golden custom_components/*/manifest.json` is empty. No claim file is touched, so step 4 is moot.
- `git diff ba4a8320..de676fcc -- tools/` is empty, so the main merge added nothing to the authored tools.
- CI (step 11), from the check-runs API at this head: all 42 runs have concluded. Every one is success or skipped, CodeQL included. That covers `gate`, `pr-contract`, `governance / instrument-self-tests`, `tests / closures`, `tests / mutation` and `codeql / Analyze (python)`. No check is red at this head. The round-five red (`instrument-self-tests` at `a11db7fe`) is named and answered in `## Red checks` with a cheaper detector and a process state, which is what step 11 asks for. The heavy runs (gate, mutation table) are cited from CI and were not re-run.
- Not re-derived: the body's 89-step local replay of the `instrument-self-tests` job. I cite CI's green run of that job at this head instead. The figure-lint `unverified` items are flag-only.
- Architecture (step 15): the close is one EXIT-trap path chained through `PR_EXIT_FIRST`, and the old inline close is removed, so there is no second copy. No breach found.
- Forward-carry: the body says `none`. Its deferrals stay on the roster group, carried above.
