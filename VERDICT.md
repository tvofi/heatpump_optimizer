Fix review: blocked 50c4a681d0e3bee30e415a1ecc663ff5eab158f8 mutant-survives: read-back retry-exhaustion die -> break passes the self-test and prints OK for a body never read back

Round: 1 (first review of this head). Reviewed from a detached worktree at 50c4a681d0e3bee30e415a1ecc663ff5eab158f8; head re-read on origin before writing: unchanged. Role file current (no diff under dev/governance/roles/ between merge base 49c222280 and origin/main). Group JSON and STUDY K14 read at pin 78117030 (claude/dazzling-gauss-7l3u2b).

## RESULT lines
RESULT self-test body_patch at head: 51 checks, 0 failed (ev/body_patch_selftest.txt) -- matches body
RESULT self-test app_push at head: 135/0; at base 49c222280: 135/0 -- matches body (ev/app_push_selftest.txt, ev/at_base_49c22228.txt)
RESULT selftest_wiring --check at head: 39 self-testing, 39 wired, 0 unwired; at 18e7a7c6 (code head) and at base 49c22228: 38/38 -- body says 38/38: measured before the ce1a78d2 merge, stale at this head; the +1 claim holds
RESULT structure.py at head: STRUCTURE RATCHET PASSED; closure select: MODE: SCOPED -- 2 script(s) run, 31 scoped out (ev/tree_checks.txt). entities.py not re-run here (no HA deps in this container): cite CI.
RESULT merge-tree --write-tree origin/main head: rc=0, tree ebb3cfa2 -- merges clean (ev/merge_tree.txt)
RESULT VERSION / manifest / RELEASE_NOTES / claim files / *_budgets.json: untouched
RESULT spec: 3 positional args; live-head refusal before mint/contract; contract = pr-contract's exact policy_lint argument set (title, author, --no-renames three-dot paths, --diff-filter=a existing, one --red per name excluding pr-contract) + carry_audit check --body; mint factored into tools/pr/app_mint.sh and sourced by both (no copy); body read back; head re-read before and after the PATCH; --dry-run prints URL+payload and makes zero curl calls; self-test wired in governance.yml instrument-self-tests; INSTRUMENTS.md entry present -- all present

## Step 1: mutation proof (ev/reviewer_mutants.txt, ev/reviewer_fixture_rbfail.txt)
The PR's six tagged arms are killed by its self-test, and my independent mutants of the head check (live==live), the contract call (|| die -> true), each contract rc, eq1 always-ok, dry-run no-return, check-runs fail-open, dropped --red, state!=open and token revoke are all killed.
SURVIVORS (the PR's self-test stays 51/0):
1. READ-BACK, blocking: body_patch.sh:166 `[ "$attempt" -lt "$RB_TRIES" ] || die "...could not be read back..."` -> `|| break`. On a PATCH whose read-backs all fail, the mutant prints `body_patch: OK: ... read back identical; head ... unmoved` and exits 0. No fixture makes every read-back fail. A two-line reviewer fixture (curl GET fails from the 2nd read on) kills it: unmutated 53/0, mutant 2 FAIL (rc 0, an OK line). The brief requires that read-back mutants be killed; this one is the arm's fail-closed path, and the beat keys on that OK line.
2. READ-BACK: verdict() eq1 relaxed to `a.strip() == b.strip()` survives -- no fixture differs only in whitespace, so "byte-identical modulo one trailing newline" is not pinned past "different text".
3. CONTRACT ARM: dropping `--diff-filter=a` from the existing-file derivation survives. The node stub copies the existing list to $STUB/existing and no check reads it, so the `--existing-file` content pr-contract relies on (the delivery-row exemption) is unasserted.
4. CONTRACT ARM: `git diff base...head` -> two-dot `git diff base head` survives. The check named "three-dot: b.txt, not the later c.txt" separates head from the moved commit, not two-dot from three-dot (base is an ancestor of head in the fixture), so its name claims a property it does not test.
Repair is small: an all-read-backs-fail fixture, a whitespace-only-mismatch fixture, assert $STUB/existing (e.g. a head that edits a base file and adds one), and a base that is not an ancestor of head (main moved) for the three-dot check.

## Steps 2-3: harness and null control
No committed finder's harness: this is an instrument group (issues/findings empty); its controls are the brief's. The self-test is the fixer's own instrument, disclosed as such. Null controls pair every refusal (healthy run patches once; dry-run and moved-head leave `the old body, 111`) -- confirmed. No live PATCH was sent by me (stubs only).

## Step 6: class
Body's rule `grep -rn "POST.*access_tokens" tools/pr tools/audit/seat | grep -v "STUB\|printf"` -- re-run: app_mint.sh (the shared author mint), app_approve.sh/app_comment.sh (hpo-approver identity, dispositioned). No open seam.

## Step 11: checks (ev/check_runs.txt)
Red: nightly-status only -- named and answered in ## Red checks; not this PR's. Pending: Analyze (python), typing, browser, fast (3.14), coverage, policy-docs, instrument-self-tests, env-matrix; judged on the rest. pr-contract success at this head.

## Notes (not the block)
- Body cites "#2560's 111 to 113 figure is the open case"; STUDY K14 revision 4 at pin 78117030 states it was not a live case. Correct the sentence.
- ## Red checks says "No other check has run: this is a handoff head with no pull request yet" -- stale at this head.
- Dispatch says "carry_audit check --body with the roster ref"; the pinned pack says only `carry_audit.py check --body`, which is what pr-contract runs. The tool runs the caller's checkout's policy_lint/carry_audit/roster (pr-contract: base's policy_lint, PR tree's carry_audit and roster), and policy_lint's red-history walk reads only when GITHUB_TOKEN/GH_TOKEN is set in the caller's env (else `skip red-history`). An offline pass can therefore diverge from pr-contract; worth one sentence in the header or INSTRUMENTS.md.
- No Group line in the body (verdict note only, per brief).
- app_push.sh refactor: no leftover $key/$appid/cleanup references; mint_cleanup now guards an unset PRIV.

bus-nonce: a40c3488651515a962e45d98fbdbf21c
