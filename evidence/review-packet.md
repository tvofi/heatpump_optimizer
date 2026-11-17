# Review packet #3698
head: be2d6def14ea4d2c4c30f1016af1ab6a1b7c3592
base: 38bf516bdd73f926ee9639ffda7b9ca5163fd50e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=133821157862 success
arch-score / arch-score id=133821691949 success
arm id=133820808150 skipped
budget-raise-gate / budget-raise-gate id=133821692043 success
cancel-superseded id=133821455557 success
codeql id=133821694400 skipped
codeql / Analyze (actions) id=133821082423 success
codeql / Analyze (javascript-typescript) id=133821082436 success
codeql / Analyze (python) id=133821082451 success
gate id=133822290850 failure
governance id=133821693336 skipped
governance / env-matrix id=133821082476 in_progress
governance / instrument-self-tests id=133821082548 in_progress
governance / policy-docs id=133821082700 in_progress
governance / record id=133821084564 skipped
governance / wave-script id=133821082552 success
hassfest id=133821693425 skipped
hassfest / hassfest id=133821082394 success
kernel-points id=133821694134 skipped
pr-contract id=133822292298 skipped
prelude id=133821455303 success
refresh id=133821455110 success
sweep-self id=133822574154 skipped
tests id=133821694318 skipped
tests / arch-instrument id=133821568011 in_progress
tests / briefs id=133821082555 success
tests / browser id=133821568096 in_progress
tests / closure-scope id=133821082588 success
tests / closures id=133821568127 in_progress
tests / coverage id=133821568012 in_progress
tests / fast (3.14) id=133821568157 in_progress
tests / mutation id=133821082482 success
tests / mutation-autofix id=133821521718 skipped
tests / mutation-pins id=133821521225 skipped
tests / nightly-ha id=133821570224 skipped
tests / nightly-status id=133821082357 failure
tests / replay id=133821570300 skipped
tests / typing id=133821568051 success
validate id=133821693200 skipped
validate / validate-hacs id=133821082534 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 133821082548: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
required-wait: required context `gate` reads concluded failure at be2d6def14ea4d2c4c30f1016af1ab6a1b7c3592 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item c3a1b4ef: R11-INTAKE-R10-RESIDUE
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: FULL -- every test script runs, nothing is scoped out.
             no segment of this names a program this check knows

FIGURES: 0 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head 4bfd3c06fa7316f88ffa19621d3df1ac0b1b69c3)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 4bfd3c06fa7316f88ffa19621d3df1ac0b1b69c3
Fix review: blocked 4bfd3c06fa7316f88ffa19621d3df1ac0b1b69c3 class-open: dev/audit/rounds/round11/product-reads/operation.tsv still names the retired `duty=control | running` cells and product_reads.py operation refuses it at this head; neither in the diff nor dispositioned in the body

bus-nonce: a0d6676cef67e11ef0fb4130b6ae6623

## Block

The body's cause is that #3665 built product_reads on the old `d16-writes --cells` format, which #3672 retired. The PR moves product_reads.py's fixture and `token_holds` to the new format. It leaves the other #3665 artifact on the old format: the committed round-11 seed ledger `dev/audit/rounds/round11/product-reads/operation.tsv` (77de985de7). All 6 of its rows are `... | duty=control | running`. At this head, `python3 -I tools/audit/product_reads.py operation --repo . --ledger dev/audit/rounds/round11/product-reads/operation.tsv` exits 2 with `REFUSE: ...operation.tsv:2: '... _write | duty=control | running' is no item of this universe as printed` (ev/seed-ledger-at-head.txt). The instrument this hotfix repairs therefore still cannot read its own committed input.

This was already broken at the base (ev/seed-ledger-at-base.txt), so the PR does not introduce it. By fix-review.md step 6, though, a site of the stated class that is neither in the diff nor dispositioned in the body is `class-open`. Either of these clears the block:
- re-cut the 6 rows to the new cell text, choosing a plan-state token per row, which is a judgement because `running` has no 1:1 successor; or
- disposition the file in the body with a route.

The sibling `generality.tsv` reads fine at the head: `RESULT read=generality universe=18897 examined=3 levels=3 pairs=0 reached-only=4`, exit 0 (ev/generality-at-head.txt).

## Findings

- Surviving mutants on the new `if tok in ("observe", "off"): return first` branch in `token_holds`: replacing `return first` with `return False` (M3) or with `return True` (M6) both leave `--self-test` at `SELF-TEST passed (85 arms)`, exit 0 (ev/mutants.tsv). No arm witnesses an `observe` or `off` cell holding, and none refuses one on a restart pass or an unavailable write. Arms `v(6)` and `v(15)` only exercise the duty-mismatch guard, which returns before this branch. To kill both: add one positive arm (an `off` cell under `duty=off`, first pass) and one negative arm (the same cell with `ordinal>0`). Carry: R11-HOTFIX-SELFTEST-SCOPES

## Evidence

- Head reviewed: 4bfd3c06fa7316f88ffa19621d3df1ac0b1b69c3 (ev/HEAD.txt). It still equals refs/pull/3698/head. Merge base: 38bf516bdd73f926ee9639ffda7b9ca5163fd50e. Code head 20e8f10a91 differs from the head only by dev/programme/delivery/3698.md.
- Role contracts: `git diff MB...origin/main -- dev/governance/roles/` touches only architect-planner.md, so fix-review.md is current.
- Merge: `git merge-tree --write-tree origin/main <head>` gives a clean tree, 6e32d8dc364a8f74651abaef032343a771cef8fb.
- Null control, both ends: at base `product_reads.py --self-test` exits 1 with the `enumerate.Refuse: const.py PUMP_DUTY_MODES ['control', 'off'] ...` the body quotes (ev/selftest-base.log). At head it prints `SELF-TEST passed (85 arms)` and exits 0 (ev/selftest-head.log).
- Mutation proof (body a, b) reproduced:
  - (a) the fixture reverted to `('off', 'control')` brings back the Refuse (ev/mutant-a.txt).
  - M1, which deletes the DUTY_OF guard and is equivalent to (b), is KILLED.
  - My own mutants: M2 (plan-state tokens without `first`), M4 (`first` ignoring unavailable) and M5 (`first` ignoring ordinal) are KILLED. M3 and M6 SURVIVE (see Findings).
- Scope: `selftest_scope.py static` prints `122 gated step(s), 0 problem(s)` at both ends. `select --change M:tools/audit/enumerate.py` and `--change M:tools/audit/product_reads.py` both select `self-tests-outside-seat` at base and head (ev/selftest-scope.txt). The closures re-record is measured data from the CI artifact. I did not re-record it: strace record is main-only and heavy.
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched (ev/figures.txt).
- Finder's harness: none named. The defect's harness is the CI step itself (`instrument-self-tests` / self-tests-outside-seat), re-run above at both ends.
- CI at this head: classify printed `WAIT 4bfd3c06fa7316f88ffa19621d3df1ac0b1b69c3 pending: gate red: none` on every poll (ev/classify-polls.txt, ev/classify-final.txt). No red is known at this head. The review_packet's `introduced-red: unreadable` refusal was the queued instrument-self-tests job (ev/review-packet.md).
- Note: figure: the body says `selftest_scope.py --self-test` prints `118 checks, 0 failed`. At the head it prints `selftest_scope self-test: 128 checks, 0 failed` (ev/figures.txt).
- Note: figure: the body says `check_scopes.py --self-test` prints `SELF-TEST passed (161 arms)` (from main's log). At the head it prints `SELF-TEST passed (every perturbed scope refused)` with no count, so 161 is not re-derived.

## Friction

none

## Delta diff: git diff 4bfd3c06fa7316f88ffa19621d3df1ac0b1b69c3 be2d6def14ea4d2c4c30f1016af1ab6a1b7c3592
diff --git a/tools/audit/product_reads.py b/tools/audit/product_reads.py
index a9d73ae8c7..4e667ea1b8 100644
--- a/tools/audit/product_reads.py
+++ b/tools/audit/product_reads.py
@@ -835,6 +835,8 @@ def self_test():
             arm("token: a write outside every pass holds no token", token_holds("idle", None, None), False)
             arm("token: a plan-state token reads the recorded plan state", (token_holds("idle", {**ps, "plan_state": "idle"}, None),
                 token_holds("both", {**ps, "plan_state": "idle"}, None)), (True, False))
+            arm("token: off holds under duty=off on the first pass, not on a restart pass",
+                (token_holds("off", {**ps, "duty": "off"}, None), token_holds("off", {**ps, "duty": "off", "ordinal": 1}, None)), (True, False))
             # generality
             gl = root / "gen.tsv"
             gen = [("level CONF_A_ENTITY=present", "has-a"), ("level CONF_B_ENTITY=present", "has-b"),

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
