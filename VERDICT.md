Fix review: merge 9865a77546e7d46ea5204f1e84f378129a16a902

Round: 1
bus-nonce: d6d94866e307dd8be8bf9f4de88f1912
seat: review-2078
Evidence: /Users/timmalmstrom/hpo-seats/review-2078/evidence/

Measured at head 9865a77546e7d46ea5204f1e84f378129a16a902 (re-read immediately
before this push; it did not move during the review). Detached worktree at the
head; every number below re-derived by this seat, none inherited. Instruments
this seat built (disclosed per fix-review.md step 9, the finding here being an
owner ruling with no committed harness): `null_control.py`, `mandate_probe.py`
and a fail-closed probe, all under /Users/timmalmstrom/hpo-seats/review-2078/,
driving the head worktree's own `merge_train.py`/`budget_raise_gate.py`.

## RESULT lines

RESULT self-test merge_train head: 92 checks, 0 failed (body: 92/0 -- confirmed)
RESULT self-test merge_train origin/main d0f085ffb: 81 checks, 0 failed (body's null control: 81/0 -- confirmed)
RESULT self-test merge_train failing-first 00512415e: 91 checks, 10 failed; the 10 FAIL lines are exactly the ten new policy arms (evidence/failing-first-arms.txt) -- confirmed
RESULT self-test budget_raise_gate at origin/main, at bef73f43c and at head: 206/0, 206/0, 206/0 -- extraction preserved the gate's own tally, confirmed at all three
RESULT mutation RM3 (window check disabled in shared mandate_state): merge_train 92/1 (expiry arm only) AND budget_raise_gate 206/2 ("after until", "exactly at until") -- one mutation reddens BOTH readers; the reading is shared, not copied (body M3 -- reproduced)
RESULT mutation RM1 (MANDATE_COVERS_POLICY widened to code-owned+budget-raise+all): 92/2, exactly the budget-raise-scope and code-owned-scope arms (body M1 -- reproduced)
RESULT mutation RM2 (cite-by-id requirement deleted): 92/1, exactly the no-mandate fallback arm (body M2 -- reproduced)
RESULT mutation RM5 (_policy_move removed from the refusal line): 92/1, exactly the content-moved arm (body M4 -- reproduced)
RESULT live control #2063 at 7c1d3b1b: ANSWER LAND -- mandate 6067089637 (scope all, from 2026-10-08T19:30Z until 2026-10-11T12:00Z) -- reproduced against the live API
RESULT live control #2063 at stale f1181615: ANSWER REFUSE -- "policy content changed after the owner's review at 7c1d3b1b740b (dev/governance/roles/fix-review.md, dev/governance/roles/orchestrator.md): a fresh owner review, not a carry" -- the planted attack on a REAL object; refusal names the move, not silence
RESULT live control #2036 (closed policy head, no owner approval): ANSWER REFUSE -- "no decisive review by tvofi (id 70032254)" -- the fallback on the real thing, reproduced
RESULT live control #2072 at 316a3641: ANSWER LAND -- mandate 6067089637 -- second real positive reproduced
RESULT live mandate probe (shared reader, judged at merge-now 2026-10-09T18:45:25Z): 6067089637 IN FORCE; 5951564627 REFUSED -- expired at 2026-10-09T12:00Z, before the merge -- the lapsed mandate behaves exactly as no mandate
RESULT fail-closed probe (reviewer-built stub): sentinel-probe failure, reviews read rc!=0, malformed reviews JSON, mandate read HTTP 500, mandate-thread read failure each raise Stop("policy") with its own named reason; nothing lands on any of them
RESULT no-policy head: policy_gate returned None with ZERO gh API reads (2 local node corpus-filter runs only) -- confirmed by instrumented command log, not by reading alone
RESULT check-runs at head, latest per name: 38 names, every one completed success/skipped; all 17 required contexts of ruleset 23698884 PRESENT and green; ABSENT contexts: none
RESULT red history of the range (00512415e, bef73f43c, d22172b6e, 5f8237b07, 9865a7754): zero `failure` conclusions anywhere; one `cancelled` Analyze (python) at 5f8237b07, superseded by the green Analyze (python) at this head -- under the corpus's own red predicate (policy_lint.mjs failingCheckNames: completed+failure only) the body's "Red checks: none" is accurate
RESULT merge-tree origin/main x head: exit 0, clean tree, no conflicting paths; GitHub's mergeStateStatus BLOCKED is the draft state + the owed owner review, not DIRTY
RESULT hygiene: claim files byte-identical to origin/main (card twin absent at merge base, head and main); three-dot diff touches no *_budgets.json, no VERSION, no manifest, no RELEASE_NOTES (3 files: merge_train.py, budget_raise_gate.py, dev/programme/delivery/2078.md); tests/structure.py STRUCTURE RATCHET PASSED; policy_lint.mjs --budgets rc=0, zero refusals; corpus-filter over both changed files prints nothing
RESULT run_always lines re-run at head: "claims hygiene: d8a4bd36f... ok" and "ALL 57 closure shrink pins PASSED"
RESULT scoped gate re-derived at head: MODE: SCOPED -- 0 script(s) run, 33 scoped out, changed files (3) -- the body's (2) was measured at the code head d22172b6e before the row commit; same mode line, consistent

## The four refusals each fire (step 14 arms)

For two of them the guard was broken and ONLY the intended arms went red
(RM2: the no-mandate fallback arm alone; RM5: the content-moved arm alone;
RM1 and RM3 above are the scope and window breaks). For the content-moved
guard the attack was planted on a live object (#2063's pre-recarry head,
above): refusal naming the moved policy files, not silence. The expiry,
revocation, no-approval, wrong-head, two-mandates-cited, edited-mandate and
code-owned/budget-raise-scope refusals were additionally unit-driven through
the train's own validator path (evidence/unit-mandate-rules.txt): every one
REFUSEs; the gate's own reader still ACCEPTs a budget-raise-scope mandate for
a raise, so the extraction did not bleed the train's stricter scope into the
gate.

## One decision, no third path

`Train.policy_gate` is defined once (:337) and called from exactly two sites:
`land()` at the merge itself (:525, under `self.real`) and batch admission
(:613, early refusal before any proof is spent -- the batch fallback arm shows
admission stops with nothing pushed or merged). `gh pr merge` appears at one
site only, inside `land()`. Caller enumeration: `run` -> `one()` -> `land()`;
`batch` kept entries -> `land()`; batch serial and dropped entries ->
`one()` -> `land()`. Every path re-passes the gate at the merge, so admission
cannot be bypassed by `run`, and a serial-routed policy head (which skips
admission's early refusal by returning before it) is still gated at `land`.
The batch rehearsal base (`--base batch/...`) skips the read by pre-existing
design and merges into a throwaway branch, never main. `wait-ci` merges
nothing. The App cannot self-approve: `approval()` filters on the pinned owner
login/id/type, and the train's own mandate approval posts as the App, which
that filter excludes.

## What survives / what moved

The head did not move during the review; all numbers above are at
9865a77546e7d46ea5204f1e84f378129a16a902 and all survive as taken.

## Observations (not blocking)

1. RM6 (this seat's mutant, not the fixer's): narrowing policy_gate's
   fail-closed catch-all (`except Exception`) to `except ZeroDivisionError`
   leaves 92/0 -- no pinned arm exercises the catch-all itself. The behaviour
   is real (this seat's stub probe drove malformed JSON through it and got
   Stop: "the policy read failed ... an unread mandate grants nothing"), but
   it is unpinned by the suite. Worth an arm in a later pass; the guard fires
   today.
2. `tools/audit/seat/merge_pr.sh` is a second merging instrument outside the
   train. Its owner mode is hard-coded to a mandate that expired
   2026-09-25T08:40Z (refuses), and its app mode routes through
   app_approve.sh, which refuses code-owned paths; the ruleset's code-owner
   rule is the backstop. Pre-existing, untouched by this PR, outside its
   claimed class (the train's decision), named here so it is dispositioned
   rather than silently assumed away.
3. The body's "origin/main moved six contract files since the merge base" I
   could not re-derive: the distinct dev/governance files moved since
   b2b6acd64 are four (fix-review.md, fixer.md, ci-autofix.md,
   claim-files.md; eight paths counting the .claude/.cursor twins). No
   reading of the tree gives six with "four roles files" among them. The
   spot-check the dispatch asked for passes: fixer.md step 5 at main does
   newly name `run_always`, and this seat re-read all four current texts
   (plus orchestrator.md sections 11/13 and decision 0013's 2026-10-02
   amendment) at this head; none changes what the branch does. The count is
   the body's and is unconfirmed.
4. The PR is DRAFT and mergeStateStatus is BLOCKED (draft + the owed code-
   owned review); `land()` marks it ready before merging, so neither is a
   defect. This PR touches tools/policy/budget_raise_gate.py, which
   CODEOWNERS gives to @tvofi: the code-owner review is STILL OWED after this
   verdict and is the owner's to post, not this seat's.
5. A third mandate comment (6003649101, scope all, until 2026-10-09T22:00Z)
   is also live at measurement time; the shared reader would accept it too.
   That is the pin doing its job (any owner-written `all` mandate in force),
   noted only so the orchestrator is not surprised by which id a landing
   cites.

Verdict: merge. The fallback is the default world: with no mandate, an
expired mandate, a revoked mandate, a wrong-scope mandate, an edited mandate
comment, a missing owner approval, a moved policy blob or an approval off
this head, the train refuses and names what it found; every one of those arms
fires, the two readers share one mandate reading (RM3 reddens both), and the
live API reproduces all five null controls.
