Fix review: merge f851f243976a2a5e67b9813de47ae32b9b7814cd

bus-nonce: bd7253fb188b7fed951255060f847f45

PR #2486, group R10-RECORD-BODY, head f851f243976a2a5e67b9813de47ae32b9b7814cd, round 1.
Reviewed from a detached worktree at the head; the head was still that SHA when this was
written. Merge base with origin/main is 76bb45628745ff8843f61c1708641f271643a224;
`git merge-tree --write-tree origin/main <head>` exits 0, no conflicting path. The diff is
two files -- `tools/audit/seat/record_row.py` and the PR's own row
`dev/programme/delivery/2486.md` -- so `VERSION`, the manifest version and the
`RELEASE_NOTES.md` heading are untouched.

RESULT head=f851f243976a2a5e67b9813de47ae32b9b7814cd (unchanged at write)
RESULT merge-tree=rc 0, no conflicting paths
RESULT body-check at head (record path set; reds record + nightly-status + delivery-status)=`PR-BODY: 0 error(s)`, rc 0
RESULT null control (the two reporter names stripped from `## Red checks`)=`PR-BODY: 2 error(s)`, rc 1, both `check ... is red and ## Red checks does not name it`
RESULT base generator at 76bb456, same fixture=`PR-BODY: 2 error(s)`, rc 1 (the same two reporter errors); the same base body under the own-row exemption (empty `--existing-file`) is rc 0, so the fixture -- not the generator -- is what discriminates
RESULT mutation (production `## Red checks` reverted to the single-`record` text)=2 self-test checks failed -- `main-state reporters named` and `body check passes the generated body over the reporter reds (rc 1: PR-BODY: 2 error(s) ...)`; restored, `record_row self-test: all checks passed`, `git status --porcelain` empty
RESULT self-test at head=`record_row self-test: all checks passed`
RESULT generated text=`## Red checks` opens "`record`, `nightly-status` and `delivery-status` may stand red on main ..."; it does not assert they are red
RESULT scoped gate (CI fast 3.14, run 39428879047 job 118649149609)=`MODE: SCOPED -- 1 script(s) run, 32 scoped out`; `RUN tests/entities.py` -> `ok (417s)`; `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT`; entities includes `ok tools/audit/seat/record_row.py --self-test passes`
RESULT structure=`STRUCTURE RATCHET PASSED` (every metric at its recorded budget)
RESULT layout guard=`GUARD: 0 refusal(s) against 76bb456`
RESULT delivery_status=`21 rowed, 3 pending, 0 overdue`
RESULT carry_audit #2486=`CARRY-AUDIT #2486: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`
RESULT head checks concluded=delivery-status success, pr-contract success x2, instrument-self-tests success, mutation success, scope success, fast (3.14) success; nightly-status failure only (exempt, note below)
RESULT head checks pending at write=coverage and Analyze (python) in_progress, not red

## What I re-derived rather than accepted

The generator's `_body_check` drives `node tools/policy/policy_lint.mjs --pr-body ...` --
`checkPrBody` itself, not a copy of its rule. I re-ran the null control by hand: stripping
`nightly-status` and `delivery-status` from the fixed body's `## Red checks` and rerunning
the record-PR fixture (two delivery rows that existed at the base, so the main-state
reporter exemption is void) returns rc 1 with both `... is red and ## Red checks does not
name it`; with the names present it returns rc 0. The green is therefore not vacuous.

The "supplies the value it asserts" trap: my first mutation harness copied `policy_lint.mjs`
behind a symlink; Node's `import.meta.url` no longer matched `process.argv[1]`, so its main
block was skipped and it returned rc 0 with empty output. I discarded that arm and re-ran
the mutation in the real worktree against the real file, where the two named checks fail
exactly as the body states. That failure mode is also what the self-test's null-control arm
guards against: it requires `rc 1` and the refusal text from a stripped body, so a
silently no-op checker turns the arm red rather than green.

At the head the generated body also passes the ordinary configurations: no reds, `record`
alone, and the own-row-only exemption all return rc 0.

## Notes (non-blocking)

- `nightly-status` is red at this head. Its only failing step is `Report the last scheduled
  run's conclusion` -- it grades main. This diff touches no `REPORTER_INPUTS` and adds only
  its own new row, so the reporter exemption holds and `pr-contract` is green; the red is
  the orchestrator's on main. `Carry: dismissed: main-state red, exempt for this diff (own-row only, no reporter input touched); pr-contract green`
- The generated `## Red checks` bullet says "the red is the batch this beat exists to
  close" beneath a lead that says "may stand red". The controlling sentence is the lead; the
  bullet is the answer's rationale. `Carry: dismissed: the lead already reads "may stand red"; no assertion of a present red`
- The `.claude/workflows/policy_lint.mjs` fallback in `_body_check` is a retired path that
  does not exist at this base or head; the primary `tools/policy/policy_lint.mjs` always
  resolves first, and the dual-path line is the sanctioned `tests/layout.py` exemption. Dead
  but harmless and guard-approved. `Carry: dismissed: dead defensive fallback, primary path always present`
