Fix review: merge 00e31e8a364e2657d8db32e97d1853895c476170

bus-nonce: c7da52cc659a2de683f91ffb25b11b38
Seat: r9-review-2072 (adversarial fix reviewer, PR #2072, group R9-RCA-HARNESS-PATH). Reviewed head
`00e31e8a364e2657d8db32e97d1853895c476170`, detached worktree `/Users/timmalmstrom/hpo-seats/r9-review-2072/head2`.
Merge base = live `origin/main` `7cd5a588cbbbef354c00148040da2d720b8a888c`. Branch `fix/rca-harness-path`, 5 files
three-dot (CLAUDE.md, dev/governance/roles/fixer.md, dev/programme/carries/carry-1922.json,
dev/programme/delivery/2072.md, tools/pr/prepr.sh +71 -2).

THE CENTRAL JOB, answer first: **the rule was not weakened, widened, narrowed or exempted anywhere.** I
extracted the rule's own text — `PIPE_GREP_Q_FILES` (six files) and the `pipe_grep_q_sites` body — from
`tools/pr/prepr.sh` at the reviewed head, at its landing commit `09d2061b247a` (PR #2067, merge `d0f085ffb`)
and at live `origin/main`, and all three extractions are byte-identical, sha256
`b6a99032765240fcd18b85a3c96231de2bde6e49d7a6a14c237e876ba621d302`. The rule's own null-control arms
(`no early-exit grep reads a pipe...`, `and a planted early-exit grep site is found`) are also byte-identical
vs live main. The branch's diff does not touch the rule region (`prepr.sh:1005-1017`): the branch's added
lines are `moved_line` (new), its self-test arms, and step 6e. The file list still contains `tools/pr/prepr.sh`
itself, so the branch could not have exempted itself, and did not: the pass comes from rewriting its own two
offending lines. This is the failure mode this lane exists to prevent, and it is absent.

RESULT rule text + site list identical at head / landing / main (sha256 b6a9903276...): reproduced
RESULT rule detector at the reviewed head: 0 sites, rc 0 (`grep -nE '<pat>'` over the six files, comment lines skipped)
RESULT rule detector at the judged red head `04d10721b`: exactly `tools/pr/prepr.sh:1398` `printf '%s\n' "$flow" | grep -q 'moved_line "'` — the branch's own new arm, reproduced
RESULT added-line sweep (my own): the branch's added lines carry exactly one `grep`, `first=$(grep -m1 '^    ' <<<"$out" | sed 's/^ *//')` — a here-string, not `printf|echo | grep`; **0** added lines match `| grep` of any form. Sweep re-taken, none remains.
RESULT the sweep's second site: commit `bca74aa97` rewrites exactly 2 lines — `printf '%s\n' "$out" | grep -m1 ... ` → `grep -m1 ... <<<"$out"`, and removes `printf '%s\n' "$flow" | grep -q 'moved_line "'` in favour of the file's own `case` idiom. No exemption, no allow-list.
RESULT the two remaining piped `grep -m1` sites (head `prepr.sh:390`, `:676`) are pre-existing: both lines are byte-identical at the merge base `7cd5a588c`, and neither is in any hunk of the branch's diff. The fixer's attribution is correct, not a miss.
RESULT provenance: `git merge-base --is-ancestor 09d2061b247a77e27ba625c81ef25a9909726ef9 <sha>` is NO for the judged head `316a364148` and YES for the recarry `04d10721b`; `d0f085ffb` is `Merge pull request #2067`. The rule entered under the reviewed head, as the body says.

RESULT `bash tools/pr/prepr.sh --self-test` at the head: **247 passed, 0 failed**, exit 0 (script exits 2 iff `st_fail != 0`; prepr.sh:2027). I re-ran it; my run took about 30 min wall at load average 58-66 on 8 cores with two self-tests running, so the fixer's 221/406/551 s are not comparable to mine and I do not quote mine as a cost.
RESULT the two rule arms are `ok` at the head: `no early-exit grep reads a pipe under pipefail in the drained scripts` and `and a planted early-exit grep site is found (null control)`.
RESULT `PYTHONPATH=tests/hastub python3 tests/entities.py`: **ALL 2250 ENTITY CHECKS PASSED**, rc 0. Reproduced.
RESULT mutation proof re-taken at the head: replacing the guard call in `moved_line` with `out=ok; r=0` gives **240 passed, 7 failed** (rc 2). The 7 FAIL rows are exactly `a new file under a landed-retired directory is refused`, `and the refusal names the new path`, `and the ok line is the guard's own, so it ran`, `a new line citing a retired path is refused`, `and the hint says to re-point the citation, not to place a file`, `a new file in no category is refused`, `and a refusal with no new path does not say to move it there` — 247 = 240 + 7, so no other row moved. Matches the body's list exactly.
RESULT the mutation is not vacuous under MY harness (the reviewer's own, `evidence/moved_line_harness.sh`, disclosed as mine, driving the production `moved_line`): at the head arm A (a file re-added under the retired dir) rc 1 naming `dev/audit/harnesses/`, arm B (same file at the new home) rc 0 with the guard's own `GUARD: 0 refusal(s)`, arm C (a line citing the retired path) rc 1 with the re-point hint, arm D (no tests/layout.py) rc 3; under the mutant, arms A and C move to rc 0 and B/D do not — the number moves under its own perturbation.
RESULT layout guard at the head: `layout: GUARD: 0 refusal(s) against 7cd5a588cbbb`, rc 0.
RESULT `python3 tests/env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok`, rc 0.
RESULT `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc 0; every metric at its cap, none exceeded.
RESULT scoped gate on a FRESH workdir: `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` (`scope.run` 1 byte). Re-run in each fresh `mktemp` dir, per the closure.py `--workdir` trap.
RESULT step 13: `git merge-tree --write-tree origin/main 00e31e8a3` → rc 0, tree `548ae2243237a9f78cdb9f9891004d2ebee47f1e`, no `MERGE-CLAIM` marker on stderr, no conflict. Nothing main brought in reddens the head: the guard, the claims, the ratchet and the self-test are all clean at this head (see the merge-context note below).
RESULT hygiene: both claim files (`tests/golden/claimed_drift.txt`, `tests/golden/card_claimed_drift.txt`) byte-identical to `origin/main`; `VERSION`, the manifest and `RELEASE_NOTES.md` untouched; no `*_budgets.json` leaf moved; the diff touches only the five files named above.
RESULT the class search is grounded: `tests/layout.py --stale` at the head is **867** lines, and the body's `## Figures` says 867 (the previous body's 871 is gone). The finding's own shape — an instruction that directs a seat to place a file under the retired harness/round tree — is re-pointed in CLAUDE.md and fixer.md (in the diff) and carried for `.claude/workflows/audit-find.js` / `audit-verify.js` to R9-RO-9 in `carry-1922.json` (I read the destination; the entry and its `brief` precondition are there). The remaining stale citations are other landed moves, dispositioned as the move stage's report-only backlog, and `.claude/rules/` is `GUARD_EXEMPT` (tests/layout.py:310) so its own `tools/audit/round*` citations are exempt by design, not missed. The branch's added lines spell no retired path literally (verified), which is why its own guard does not refuse them.

## Red checks (step 11)

The fixer's `## Red checks` names `instrument-self-tests` and answers it. I re-took the enumeration from the
commit check-runs API, not the body's account: at `04d10721b` the reds are **`instrument-self-tests`**
(243 passed, 1 failed) and **`pr-contract`** (the cascade: `check instrument-self-tests is red and ## Red
checks does not name it`). `fast (3.14)` was **success** at `04d10721b` and at every other branch head, so if
any account says `fast (3.14)` was the red, that is wrong; the fixer's handoff body does not — it names
`instrument-self-tests`, correctly. `nightly-status` is red at `71f7a612a0`, `91b77d0cd3`, `8766b840f5` and is
exempt (`defect-root-cause.md`: it grades main; this diff does not reach its scripts, tests.yml,
governance.yml, the plan, HANDOVER.md or a row it did not add). The cheaper detector is named with its cost
(the local self-test arm, reachable before the push) and the process state (d) is recorded; the trigger is
answered.

## Check-runs at the reviewed head

`gh api .../commits/00e31e8a3.../check-runs` → **0 runs: ABSENT, not green.** The reviewed head is published
on `refs/heads/handoff/r9-harness-path-r2` (= `00e31e8a3`) with its body on
`refs/heads/handoff-body/r9-harness-path-r2` (= `596d33f4c`), but `refs/heads/fix/rca-harness-path` still reads
`04d10721b` at my post time, so no `pull_request` run exists at the head yet. Nothing is pending: nothing ran.
The graded check is therefore my own `prepr --self-test` run above.

## The live PR body is stale; the push must carry the handoff body

`gh pr view 2072` still serves the pre-fix body: `## Head` names `04d10721b`, `## Figures` says `220 passed, 0
failed`, and `## Red checks` says `none` — i.e. it does **not** answer the `instrument-self-tests` red. The
fixer's handoff body (`handoff-body/r9-harness-path-r2`, `596d33f4c`) is correct: head `00e31e8a3`, `867`
stale lines, `247 passed, 0 failed`, `240 passed, 7 failed`, and `## Red checks` answering
`instrument-self-tests`. I judged the fix against that body, which is the body prepared for this head. The
orchestrator's push to `fix/rca-harness-path` must replace the live body with it, or `pr-contract` will refuse
the range's red history on the next push. This is an action on the push, not a defect in the fix.

## Declined

- The detector's 0.036 s class-arm cost and the 221/406/551 s self-test series: not re-taken. My box was at
  load 58-66 on 8 cores with two self-tests in flight, so my wall times are not the fixer's conditions and I
  quote none of them as a cost. The graded claim — 247 passed, 0 failed — I re-ran and reproduced.
- The heavy CI lanes `features.py`, `optimality.py`, `golden.py` and the mutation table: cited, not run
  (`fix-review.md` step 11; a green mutation does not mean a green baseline, so I re-took the targeted mutant
  myself instead). The head has no check-runs to cite, so these are carried by the push.

## Merge-context note (R9-RC-POSTREVIEW-MERGE)

I looked for another instance of the class a root-cause seat is investigating tonight — a head reddened by
what a post-review recarry brought in. Here the recarry is the *fix*: main `09d2061b247a` entered at
`04d10721b` and reddened the head on `instrument-self-tests`, and `bca74aa97` repairs it. At the reviewed head
`00e31e8a3` I find no further instance: merge-tree, the layout guard, the claims check, the ratchet, the full
self-test and `entities.py` are all clean. I name the one instance above (the recarry itself) and no other.

Evidence: /Users/timmalmstrom/hpo-seats/r9-review-2072/evidence (HEAD.txt names the head;
rule_00e31e8a36.txt / rule_09d2061b24.txt / rule_7cd5a588cb.txt carry the three rule extractions;
selftest.log, selftest_mut.log, entities.log, scope_select.txt, stale.txt, moved_line_harness.sh).
