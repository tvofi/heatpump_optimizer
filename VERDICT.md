Fix review: blocked 5f6d8fbd7141a01c9e30afae5b6d8a28f7368088 mutation: audit-find.js's cut-off arm is unpinned -- replyField reading unparseable text as an empty collection fails no check (197/0), so a finder report whose findings come back cut off reads as a seat with no findings, the exact (e)/(h) claim the body makes
bus-nonce: 1ac839ad92bd59b8f6043a6e2e988cf0

Round 1. Measured head 5f6d8fbd7141a01c9e30afae5b6d8a28f7368088 (still the PR head at posting); base = merge base 932f5d6019e5 (origin/main). Detached worktrees at both.
Code-owned: .claude/workflows/audit-find.js, audit-verify.js, tools/audit/fold_ledger.py -> tvofi approves at merge, whatever this verdict.

## The blocking item (step 1)
The body: "Anything else, including cut-off text, is refused with the reply named and is never read as empty. In audit-find.js, a report that fails this is a seat not reported."
Mutant R1 (audit-find.js replyField, `catch { throw ... }` -> `catch { x = kind === 'array' ? [] : {} }`): check-wave-script 197 passed, 0 failed -- survives.
The same mutant in audit-verify.js (R2) is killed (196/1). The gather cut-off arm passes under R1 only because an empty reports object leaves the box's seats missing anyway.
Behaviour difference is real: reviewer probe (evidence/reviewer_probe.patch), a finder report D1-s2 whose findings is JSON text cut at 25 chars:
  head: ok (D1-s2 not reported); under R1: FAIL {"missing":[],"err":"","intake":true} -- the seat reaches intake with no findings.
Repair: one pin of this shape in check-wave-script.mjs (the probe in evidence is one). The head's code is correct; only the pin is missing.

## RESULT lines (finder-group harness dev/audit/harnesses/r10_tick_drivers.py, --evidence = head tree)
base: findings=44 form_file_rej=35 form_driver_rej=0 form_gap=35 form_both_ok=9 gather_replies=1 gather_max_kb=193.9 gather_missing=3 text_gather=-1 text_read=-1
head: findings=44 form_file_rej=35 form_driver_rej=35 form_gap=0 form_both_ok=9 gather_replies=10 gather_max_kb=34.0 gather_missing=3 text_gather=3 text_read=44
head --perturb: form_gap=11 form_driver_rej=24
All match the body's figures (body took base at 64b1f82a3958; mine is the merge base 932f5d60, same numbers).
Null controls hold: form_file_rej and form_both_ok flat at both ends; gather_missing=3 flat (D15 seats on B11, outside BOXES).
Step 9: the harness is new in this diff and its header says "Written by the R10-TICK-DRIVERS fixer"; #2265's evidence had no committed harness. Disclosed, but the body's Figures calls it "the finder's harness" -- it is the fixer's.
Step 8: --perturb deletes perturbation.properties wholesale, not only the expected_direction enum the body and the harness's own label name; form_gap=11 is the effect of dropping every perturbation sub-property. Description inaccuracy, not blocking.

## Mutation proof (fixer's) and my mutants -- evidence/mutants.txt
Killed: R2 verify cut-off, R3 BOXES precedence, R5 off-box seat taken, R6 fold without sync (4 FAIL), R7 no-predictor guard (prepr 286/1), R8 predictor rc ignored (prepr 286/1).
Survives: R1 (blocking, above); R4 (`r[k] ?? []` -> `r[k]`), no PR claim; recorded only.

## Cheap checks at head
fold_ledger --self-test 0 FAIL; check 0 violation(s); sync "already carries" (tree clean after).
check-wave-script 197 passed, 0 failed. agreement: pair finder-report-form 214 items 0 divergent; RESULT divergent=0 unregistered=0 dead=0 refused=0.
throwaway_git.py --check: 0 refused. structure.py: STRUCTURE RATCHET PASSED. closure select: MODE: SCOPED -- 1 script(s) run, 32 scoped out.
VERSION, manifest, RELEASE_NOTES.md, both claim files: untouched (three-dot). merge-tree --write-tree origin/main HEAD: rc 0.
closures.json: one inert_reads line, earned by the new harness file (step 14).

## CI (cited, not re-run) -- commits/5f6d8fbd7141a01c9e30afae5b6d8a28f7368088/check-runs, 34 runs
No failure. Concluded success include instrument-self-tests, pr-contract, wave-script, mutation, closure-scope, policy-docs, typing, env-matrix, arch-score, budget-raise-gate, fast (3.14).
Still in progress when posted: coverage, CodeQL Analyze (python). Job logs unreadable from this seat (the blob host is refused by the proxy), so mutation's green is cited by conclusion only; the body says no changed line is in the mutation inventory.

## Red checks (step 11)
Range reds: 03c0766bf only -- instrument-self-tests (117649560197) and pr-contract (117650396148). db9267d4, d95f4431, 559b8bda: none red.
Both are named in ## Red checks; instrument-self-tests gives its cheaper detector (throwaway_git.py --check, seconds) and the prepr gap; pr-contract names its cause. Answered. pr-contract at head: success.

## Forward-carry and scope (step 10)
The body says none. The tick-fold follow-up is recorded by tvofi on #2265 (comment 6249063431): brief O14, tick-drivers-2, L03 L04 L05 P02 P55 P57 L12 b/c + --carry-sweep, cut from main after #2390 merges.
No O14 brief exists in the tree on origin/main or any fetched ref -- consistent with "cut from main after #2390 merges".
Not in this PR: the diff has no carry-sweep, and touches only the (e)(g)(h)(i)+M2+M3 sites the body lists.
NOT VERIFIED: the item IDs L03..P57, L-T1 and L12(a)/(b)/(c) are defined nowhere I can read (tree, #2265, #201's 1776 comments, PR reviews). I cannot map them to code, so I cannot confirm that L12(a) is in this PR or that L-T1 is out; #2265's list names "L12 b/c" and omits L-T1. That mapping is the orchestrator's to confirm.
