Fix review: blocked e96ff8d23690b2371229d9bcf2188eda8b1af0a5 architecture-unsound: the stale-bootstrap refusal reddens the second reader's PR under the base-copy grader, so the deadlock moves rather than breaks

bus-nonce: fb28f2fb99fc19299a2fc22dd8552752

## Head

Measured `e96ff8d23690b2371229d9bcf2188eda8b1af0a5` from detached worktrees at the head and at the base `8f286293be2d03817a2de23a3a0c884ec2e94fab` (= origin/main = merge base). Round 1, full review. The role contract has not changed between the merge base and origin/main (the three-dot diff of `dev/governance/roles/` is empty).

## Block

The carry (stranded carry 35) is not built. The design is sound only when the reader PR is graded by its own copy of `agreement.mjs`. `governance.yml` (the pinned list near L1098) restores `tools/policy/agreement.mjs`, and with it `SHARED_GRAMMARS`, from `PINNED` before the agreement step runs under `set -euo pipefail`. That gives this sequence, measured in a detached worktree at the head with a synthetic grammar (`ev/two-pr-simulation.txt`):

1. main1, with one reader and no entry: `RESULT ... dead=0 refused=0`.
2. PR A adds `"bootstrap:second reader lands in #9999"`. Its own grader reads `dead=0 refused=0`, which is the improvement: before this PR the same tree read DEAD on main's push run. CI on PR A never sees the entry, because it grades with the base's copy.
3. PR B adds the second reader. CI grades it with main2's restored `agreement.mjs`, which still says `bootstrap:`, and prints `REFUSED discovery "zz-boot-grammar-(\\d+)-q": declared bootstrap but tools/policy/zz1.mjs, tools/policy/zz2.mjs already read it: re-disposition it as pair:, module: or identical:` with `refused=1`, rc=1. PR B's own re-disposition (`identical:`) reads `refused=0`, but CI never runs PR B's copy.

So the reader PR's lane is red either way. Before this PR it read UNREGISTERED. After it, it reads REFUSED as stale, and the only cure lives in a file CI pins. The body claims "the reader's PR is graded by a base that already holds the entry (no UNREGISTERED)". That is true, but it leaves out that the same base refuses the entry as stale. The rejected alternative (b) was "loosen the pinned grader for every PR". The chosen path (a) needs one more piece to work under the pinned grader: the stale state must not be fatal in the PR that lands the second reader. One way is to accept a bootstrap entry that spans two files as a note, and refuse it only once `PINNED` itself already shows two readers, which is one merge later, when a follow-up PR can re-disposition it from a base that agrees. Another is to make the stale state fatal only on the push to main.

The fixer chooses the design. Whatever the fix, it owes a test that runs the reader PR against the base's registry, which no self-test probe does now: every probe passes one registry to one tree.

## Findings

- The fix is architecturally unsound under the base-copy rule: the second reader's PR is refused as stale by the pinned grader (above), so the deadlock carry 35 names is relocated, not removed. Carry: R10-AGREEMENT-BOOTSTRAP
- No expiry or bound. The reason check is syntactic only. `bootstrap:#1`, `bootstrap:due 1999-01-01` (a past date) and `bootstrap:copied #3100` each pass on a one-reader grammar (`dead=0 refused=0`). An entry marked bootstrap therefore never goes red while only one file reads the grammar, and a date in the reason is never compared with today. A steady-state bypass is limited: a one-reader grammar needs no registration, and two readers trip the stale arm. The body's "a bootstrap entry expires by itself" holds only through the stale arm, which is the arm that blocks above. The re-cut should bound the marker (expire the date, or require the `#N` to be open) or drop the claim. Carry: R10-AGREEMENT-BOOTSTRAP
- A surviving mutant: deleting the stale-refusal branch (`if (d.startsWith('bootstrap:')) report.refused.push(...)` → `if (false) ...`) leaves 220 of 220 probes held. The unknown-kind refusal still counts one, and the probe checks only `refused.length === 1`, never the message. The stale probe passes for the same reason under origin/main's grader. The probe should key on the stale message. Carry: R10-AGREEMENT-BOOTSTRAP

## Red checks

Read from the commit's check-runs API (all pages) at `e96ff8d2`:
- `codeql / Analyze (python)` (id 125145128242): cancelled at 08:00:10Z after about 45 minutes, in query evaluation (48 of 52 queries done). The diff touches no Python. Carry: R10-AGREEMENT-BOOTSTRAP
- `gate` (ids 125160592563, run 41404989872; and 125161518121, run 41404989734): failure, because `FAIL codeql / Analyze (python): cancelled (this run)`. The body's `## Red checks: none` predates the red, and the re-cut's body owes the answer: re-run the cancelled job, or name it as a runner cancellation with no cheaper detector. Carry: R10-AGREEMENT-BOOTSTRAP

## Evidence

- RESULT self-test at the head: `SELF-TEST 220 of 220 probes held`. At the base: `212 of 212` (`ev/selftest-head.txt`).
- RESULT full grader with no `--py-json`, which the CI lane supplies: identical at base and head, `divergent=0 unregistered=0 dead=0 refused=6`, where the 6 are the missing-py-json refusals (`ev/agreement-base.txt`, `ev/agreement-head.txt`). On a tree with no bootstrap entry the old and new graders agree: the change does not weaken either check there.
- RESULT failing-first: with the production hunks reverted and the new probes kept, 3 FAIL and `217 of 220`, which matches the body (`ev/failing-first.txt`).
- RESULT null controls, as self-test probes, all hold at the head: an undeclared one-file entry reads DEAD; `bootstrap:` and `bootstrap:soon` are refused; a two-file `identical:` entry is unaffected.
- RESULT mutants (`ev/mutants.txt`). The fixer's mutant (non-bootstrap DEAD → false) is killed, `218 of 220`, re-derived. My own mutants: dropping the reason check is killed (218), dropping the no-reader DEAD is killed (219), dropping the marker branch is killed (217), widening `#\d+` to `#\d{9}` is killed (217). Dropping the stale refusal survives (220), as listed under Findings.
- This PR's own policy-docs check: `governance / policy-docs` is green in the packet digest. Under the base-copy rule CI ran origin/main's `agreement.mjs` on this tree, which adds no SHARED_GRAMMARS entry and no new shared grammar. The new `BOOTSTRAP_REASON` regex lives only in `agreement.mjs`, which is restored from the base. So the green is expected and says nothing about the bootstrap path.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc=0. No `*_budgets.json` is in the diff.
- `git merge-tree --write-tree origin/main e96ff8d2`: rc=0, no conflict.
- Claim files, VERSION, manifest and RELEASE_NOTES are untouched in the three-dot diff. No host path is in the added lines.
- The delivery row `dev/programme/delivery/3166.md` is present in the three-dot diff.
- The figures in the body re-derive: self-test 220 of 220; `--only discovery` gives dead=0 unregistered=0; structure passed.
- The finder's harness: the carry names none committed. The measured `RESULT ... dead=1` from the split of 98b532ab1 has no committed instrument. The two-PR simulation in `ev/two-pr-simulation.txt` is my own instrument, built for this review, not the finder's.
- Scoped gate: `GATE_SCOPE=auto` at the head printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` and ended `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT AND NOT RUN`, rc=0 (`ev/gate.txt`).
- CI: `merge_train.py classify e96ff8d2 --pr 3166` gave WAIT (rc=3) until about 08:04Z, then `RED e96ff8d23690b2371229d9bcf2188eda8b1af0a5 pending: none red: gate` with rc=1 (`ev/classify-final.txt`). That red is the cancelled CodeQL job above, not this diff. All other required lanes concluded success, including `governance / policy-docs`, `tests / mutation`, `tests / closures`, `tests / fast (3.14)` and `budget-raise-gate`.
