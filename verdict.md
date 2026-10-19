Fix review: merge 22803f99bd8be29012a668ef22140dd12ae3aa5e

bus-nonce: bacf5bc62239185cd601055924974fcf

**Round 9.** This is the ninth `Fix review:` verdict on #2406. Rounds 1 to 8 blocked at `a7d97f55b`, `89d2b9465`, `af391637b`, `b965c4ab9`, `d1becac2b`, `2d9f20009`, `22803f99b` and `22803f99b`. Round 8 blocked only on a stale second `## Forward-carry` spliced into the body. The head has not moved since round 7, and this round's repair is a body-only re-cut.

I measured head `22803f99bd8be29012a668ef22140dd12ae3aa5e` (`ev/HEAD`). `pulls/2406` still reported that head after `fast (3.14)` concluded.

**Contract currency.** Origin/main moved to `fa424fd91` (#2408, #2419, #2426) after the merge base `06c6f3cf2`. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is not empty: #2408 rewords `fix-review.md` step 10 and `orchestrator.md`. So I judged against main's `fix-review.md` and `finding-propagation.md`, not the head's copies. Main's step 10 now names the roster carry at the body's `handoff/audit-r<N>-roster` SHA. Main's `finding-propagation.md` Enforcement says a carry to the round's roster lands "once on its branch `handoff/audit-r<N>-roster`". This carry is of exactly that form.

## The round-8 block is cleared

- **Body** (`ev/body.md`, `ev/body-headings.txt`): each of `## Head`, `## Mutation proof`, `## Null control`, `## Figures`, `## Unpinned sites`, `## Red checks`, `## Forward-carry` and `## Friction` appears once. The broken "## Friction`." heading and the duplicated red-check entries are gone. The one `## Forward-carry` names `Carry: R10-STAMP` at `73bb15fe8f5bf05ec3568927118a8d678dd8b99f`. The CodeQL entry and the stale R10-TICK-DRIVERS copies are dismissed, each with its reason. The `## Friction` item reads `Carry: dismissed:` with its reason.
- **Roster carry** (step 10, `ev/carry.txt`): `origin/handoff/audit-r10-roster` is still at `73bb15fe8`. In R10-STAMP, `resume.stage` is `not-started`. The last `carry` entry gives the post-merge state-docs beat restart as a precondition ("after #2406 merges, restart ... with no --roster-ref and no --watch-ref refs/heads/main"), followed by its control ("Check: the beat's memo file holds two SHAs ... a roster-only commit regenerates the plan within one beat").
  - Stage form (not blocking, as earlier rounds found): the carry is in R10-STAMP's `carry` list, not its `brief` string.
- **carry_audit** comes from #2404's head `b419463b1`: it is not in the tree on main. Its self-test prints `144 checks, 0 failed`.
  - Against `--roster-ref origin/handoff/audit-r10-roster`: `CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)`, rc 0 (`ev/carry_audit.txt`).
  - Null control: the same body with `Carry: R10-TICK-DRIVERS` in place of `Carry: R10-STAMP` gives `BAD-DEST ... R10-TICK-DRIVERS is done`, rc 1 (`ev/carry_audit_null.txt`).
  - Against `origin/main`: `BAD-DEST ... R10-STAMP is not a group of the roster`, rc 1 (`ev/carry_audit_main.txt`). This is the main-roster lag that the body's `## Red checks` names (R10-STAMP lands with roster PR #2417). It is not this PR's.

## CI (step 11)

Source: the check-runs API on this head (`ev/checkruns.tsv`). There are 54 runs, all `completed`, and none concluded `failure`.
- `fast (3.14)` concluded `success` at 03:09:21Z, with `ALL TEST SCRIPTS PASSED` in the job log.
- `closures`, `wave-script` and `delivery-status` are success.
- All four `pr-contract` runs are success. The last one started at 03:05:41Z, after the body edit at 03:05:35Z.
- The expected `pr-contract` BAD-DEST red did not occur, so no step-11 allowance was needed.
- Earlier-head reds were answered in the body. Rounds 6 to 8 accepted those answers, and the body is unchanged on them.

## Merge with current main (step 13)

- `git merge-tree --write-tree origin/main 22803f99b` (main `fa424fd91`) returns rc 0, tree `5fb7aae14`, with no conflict and no MERGE-CLAIM line (`ev/merge-tree.txt`).
- Two files change on both sides: `tools/policy/policy_lint.mjs` (#2408) and `tools/audit/seat/INSTRUMENTS.md`. I ran the cheap checks on a probe commit of the merged tree (`a6db8b2d3`, local only, `ev/merged-checks.txt`):
  - `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`, `FIXTURE ok`, no VACUOUS;
  - `closure.rename_sites()`: `([], [])`;
  - `tests/closure.py selftest`: `ALL 124 closure shrink pins PASSED`.

## Other steps

- **Code (steps 1 to 3, 6, 14, 15).** Round 7's verification stands, because the head is unchanged. I did not re-run the mutation proof or the heavy figures; per step 11 I cite CI's heavy runs.
- **Steps 4 and 5.** `VERSION`, the manifest, `RELEASE_NOTES.md`, both claim files and every `*_budgets.json` are untouched over the three-dot range. `env_drift.py --claims-only origin/main` prints `claims hygiene: origin/main ok`. At the head, `rename_sites` is `([], [])` (`ev/local.txt`).
- **Step 7.** The body's `## Head` names `22803f99b`, the head I measured.

RESULT round=9 head=22803f99bd8be29012a668ef22140dd12ae3aa5e moved=no
RESULT body_forward_carry_sections=1 dest=R10-STAMP(not-started) roster_sha=73bb15fe8 control=present
RESULT carry_audit roster_ref=handoff rc=0 routed=3 unrouted=0 bad_dest=0 null_control rc=1
RESULT ci check_runs=54 incomplete=0 failure=0 fast(3.14)=success pr-contract=success(x4)
RESULT merge_tree main=fa424fd91 rc=0 merged_policy_lint=0err merged_closure_selftest=124/124
