Fix review: merge ad0cdbef2d2301f8feb719b08f03580214b3a7e8

bus-nonce: c49e3f651c95562a4a32beeeed21b231

## Verdict

Round 1. PR #3064 (the mandate-guard group, issue #2724). Reviewed at head ad0cdbef2d2301f8feb719b08f03580214b3a7e8. Before writing this verdict I re-read the PR's live head and it is still that SHA. I worked from detached worktrees at the head, at the merge base f3c9144b8 and at a7dd7f50d, plus an export of origin/main 61b0076f4.

Both defects are fixed, by the finder's harness at both ends:
- The guard now refuses the field text and posts the null control.
- The gate now refuses the false score figure, measured by the base's scorer, and accepts the true one.

All 8 of the fixer's plants are killed. Of my own 5 mutants, 3 are killed. The 2 that survive are both on the fail-closed side.

CI at this head is GREEN. The branch merges cleanly with origin/main. No metric moves.

The findings below are residuals, figure corrections and instrument notes. None of them is a defect in the fix that this PR owes.

Policy note, which I note and do not decide: the PR touches `.github/workflows/governance.yml`, which is code-owned, and two policy instruments, `tools/policy/budget_raise_gate.py` and `tools/pr/gh_comment.py`. It merges only on tvofi's approving review at the head, or under a mandate in force that covers it.

## Findings

- **A false score line beside the true one passes, and the true one can be hidden (residual, stated in the body).** I built a `## Raise justification` with the true line `Architecture score: dS +0.0000 NULL` inside an HTML comment (`<!--` on the line before, `-->` on the line after) and `Architecture score: dS +0.0500 IMPROVES` as the only rendered line. `justified()` accepts it (`ev/residuals.txt`). The body's "Residual: a false line beside the true one passes" covers this, but it understates it: on the rendered page, the false figure can be the only one a reader sees. An agent approver reading the raw body through the API still sees both lines. A cheap tightening would be to require the measured figure on the section's first score line, or to strip HTML comments before matching. Carry: #2724
- **An expired grant is unguarded, but the gate still applies later comments to it.** `mandate_state` judges a review at its own submission instant. However, it treats every owner comment in the thread since the grant as a kill-switch hit, whatever that comment's date. Case: a review approves inside a grant's window, the window then closes, and later an owner-account comment with the stem names that grant's id. A gate re-run on that still-open PR then refuses. `ev/residuals.txt` shows `in_force= True` without the later comment and `False` with it. `revocable()` reads that grant as not guarded (`False`), so `gh_comment.py` posts such a comment. The body's design choice "An expired grant is not guarded" does not state this case. Its reach is narrow: only unmerged PRs approved inside a closed window. Carry: #2724
- **Body figure: B2 fails 10 checks, not "8 checks".** At this head, `r10_mandate_guard_mutants.py` B2 fails 10 checks (`ev/mutants_driver.txt`): the body's 8, plus `e2e: a planted false IMPROVES ...` and `e2e: ... and on a head whose own scorer prints it ...`. The kill holds, with more failing checks rather than fewer. Carry: dismissed: the figure is corrected here; the claim it supports (B2 killed) holds.
- **Body figure: the scoped gate runs 2 scripts, not "0 script(s) run, 33 scoped out".** At this head, and at the code head 86123b4 against a7dd7f50d, `tests/closure.py select --diff <merge-base>` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` The 2 scripts are `tests/entities.py` and `tests/harness_headers.py`. CI's `tests / fast (3.14)` log prints the same line, and that job concluded success. The mode line the body keys on is right; the count is not. Carry: dismissed: corrected here, and CI's own run of the 2 scripts is green.
- **Surviving mutant M2: `measured_score`'s `if r.returncode != 0: raise` replaced by `if False:`; no check fails.** No self-test drives a real scorer to a non-zero exit after it prints a parseable line. The body's "a scorer that fails is a refusal" row tests `decide()`'s except arm through a fake `score_fn`, not this line. In practice the mutant is equivalent: `score.py --diff` returns 0 whenever it prints, and a crash prints nothing parseable, which `score_check` refuses. Carry: dismissed: equivalent under score.py --diff's exit contract, and the unparsed-line refusal stays fail-closed.
- **Surviving mutant M4: `measured_score` returns the last stdout line instead of the first; no check fails.** The e2e stub scorer prints a single line, so first and last are the same. With the real multi-line report, the last line is a term line. That line does not parse, so every mandated raise would be refused, which fails closed. Carry: dismissed: fail-closed direction only; worth a two-line stub in a later touch of the e2e.
- **My mutant M1 (dS compared at 1 decimal instead of 4) is killed only by the refusal-message check.** No row plants the same verdict word with a different dS at small magnitude. For example, a body claiming `+0.0300 IMPROVES` against a measured `+0.0012 IMPROVES` would pass under M1. The kill is real, but it is incidental. Carry: dismissed: killed at this head; a same-word, different-dS row would make the kill direct.
- **The guard arm of the finder's harness cannot run from a cloud seat.** It reads comment 6546832523's first text through GitHub GraphQL. This session's proxy refuses GraphQL with HTTP 403. The proxy also refuses the `repositories/{id}` next-page links that `gh api --paginate` follows. So in a cloud session, `gh_comment.py`'s thread read fails and refuses every #201 body holding the stem, mandate id or not. That is fail-closed, and cloud seats do not post to #201. Carry: dismissed: environment-specific; local seats and CI are unaffected, and the substitute replay below re-derives the field result.

## Evidence

- **Contract.** The roles diff against origin/main is empty, so the contract is current. The PR head is the head I measured: the body names ad0cdbef2 and code head 86123b4, and `git log` agrees.
- **The finder's harness, `dev/audit/harnesses/r10_mandate_guard_instances.py`, lands in this PR** (commit c8b25df90, built with the fix). I ran it as the brief names it.
  - Score arm, base export of origin/main:
    `RESULT claim='+0.0012 IMPROVES' measured=None accepted=True` and `RESULT claim='+0.0000 NULL' measured=None accepted=True`. This is the defect: both claims are accepted with nothing measured.
  - Score arm, head:
    `RESULT claim='+0.0012 IMPROVES' measured='Architecture score: dS +0.0000 NULL' accepted=False` and `RESULT claim='+0.0000 NULL' measured='Architecture score: dS +0.0000 NULL' accepted=True`. This run used #3045's round-1 head b02ffd17 and took 88 s wall, 80 s user, for two scorer runs.
  - Guard arm, both ends: GraphQL HTTP 403 (`ev/harness_guard_*.txt`). I substituted my own driver (`drive_guard.py`, disclosed here), which hands the harness the in-tree arm-6 FIELD excerpt in place of `first_text()`.
    - I checked that excerpt against the live comment. Every line other than the group name is in the live body. The live body was edited afterwards and now holds neither the name nor the stem (`ev/excerpt_vs_live.txt`).
    - Base: `RESULT body=field rc=0` and `RESULT body=field-without-word rc=0`. This is the defect: the field text posts.
    - Head: `body=field rc=2`, but the refusal came from a failed thread read (proxy pagination), not from the guard. I re-ran through `gh_comment.run()` with a thread reader that pages over REST `?page=N` (`ev/guard_live_head.txt`, live #201 thread):
      - the field text is refused, naming mandate comment 6329234399;
      - the field text with the name replaced gives rc=0;
      - a legitimate state comment naming the group by its full name, with no mandate id, gives rc=0. The guard does not over-fire on the stem alone;
      - the stem inside a code span beside a live mandate id is refused. That is consistent with the gate, which reads the raw text;
      - the spelling "REVOCATION" beside a live id gives rc=0. The gate's pattern does not match it either, so the guard and the gate agree. There is no bypass in either direction, because both import one predicate.
- **Self-tests at the head.**
  - `budget_raise_gate.py --self-test`: `255 checks, 0 failed`. At a7dd7f50d and at merge base f3c9144b8 it is `237 checks, 0 failed`. On the non-git export of origin/main it is `202 checks, 2 failed`; both failures are "the tracked budget files could not be listed", an artifact of the export not being a git repository.
  - `gh_comment.py self-test`: `TOTAL: 0 failed`, `SELF-TEST PASSED`.
- **The fixer's driver** (`ev/mutants_driver.txt`): `RESULT plants=8 killed=8`, with G1=1, G2=2, G3=1, G4=6, B1=2, B2=10, B3=1 and B4=1 failing checks. `--null` gives `RESULT mutant=null rc=0 fails=0`. `--self-test` gives `8 checks, 0 failed`.
- **My own mutants** (`ev/my_mutants.txt`, `mymut.py`):
  - M1 (round to 1 decimal): KILLED, 1 check.
  - M2 (scorer exit code ignored): SURVIVED.
  - M3 (`revocable` always True, so expired grants are guarded): KILLED by `arm6_an_expired_grant_is_not_guarded`. This is a null row perturbed, and the arm goes red.
  - M4 (last stdout line): SURVIVED.
  - M5 (owner test dropped from `revocable`): KILLED by `arm6_a_grant_by_another_account_is_not_guarded`. Another null row perturbed, and its arm goes red.
- **Score rounding.** `round(float('-0.0000'), 4) == 0.0`, so `-0.0000` and `+0.0000` compare equal; the self-test row "score: -0.0000 is the same figure as +0.0000" passes. A scorer line in another format does not match `JUSTIFICATION_SCORE` and is refused ("score: a scorer line that does not read is a refusal").
- **Mandated-arm CPU and timeouts.** `measured_score` sets no subprocess timeout. On a slow runner, the job's `timeout-minutes: 5` kills it, so the `budget-raise-gate` context concludes cancelled or failure, never success. That is fail-closed. The gate's source and the scorer both come from the base: the workflow restores `tools/policy/*.py` from PINNED, and `measured_score` adds a worktree at `--base`. `score.py --diff` returns 0 whenever it prints. Here, one scorer run took about 44 s wall.
- **Stated gaps.** I checked that each is true and none is silently widened:
  - `gh_comment.py` is the only patched poster. A raw `gh api` or `gh issue comment` post is untouched, and the module docstring records that.
  - `merge_train.py` is not in the diff, so its approve and `--check-body` still judge shape only.
- **Other checks.**
  - pr_args.sh: `pr_args.sh --self-test` on Linux gives `158 checks, 0 failed` at both the head and the merge base, and the two FAIL sets are identical (both empty). The body's 156 checks / 6 failed were that macOS host's own figures.
  - Merge: `git merge-tree --write-tree origin/main ad0cdbef2` exits 0 (`ev/merge_tree.txt`). It conflicts on no path, so the claim driver was not invoked.
  - Untouched files: VERSION, the manifest, RELEASE_NOTES.md and both claim files are untouched in the three-dot diff (`ev/untouched.txt`), so the claim files are byte-identical.
  - Delivery row: `dev/programme/delivery/3064.md` is in the three-dot diff and holds the open row.
  - Structure: `python3 tests/structure.py | tail -1` prints `STRUCTURE RATCHET PASSED`. No budget file is in the diff.
  - Prediction: `ci_predict.py --base origin/main` predicts no closures, fast, governance or instrument red.
  - Closures: `tests/closures.json` adds only the two INERT entries for the two new files.
  - Architecture score: the diff touches nothing under `custom_components/`, so the score does not move.
- **CI and red checks.**
  - `merge_train.py classify ad0cdbef2...` prints `GREEN ... pending: none red: none`, rc=0.
  - At head ad0cdbef2 no check run has a failure, cancelled or timed-out conclusion. Commit 71ca051 shows only cancelled `gate`, `prelude` and `refresh` runs, superseded when the next head was pushed; none of them is a red gate check.
  - The `pr-contract` log prints `record red-history 6 commit(s) between origin/main and this head, every failure conclusion across them: none` and `red checks the body must answer:` with an empty list.
  - The body's `## Red checks` answers the two triggering reds, #3006's `budget-raise-gate` and #3045's metric-gamed approval, each with its detector and standing cost.
- **Not re-derived.** The body's "about 59 s of CPU", measured on the fixer's machine; I measured 88 s wall and 80 s user for two scorer runs here. The prepr figures on the fixer's host (`self-test 431 passed`). I did not re-run `prepr.sh`.
