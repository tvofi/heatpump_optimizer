Fix review: blocked 755949528b55769455419754a8ba57e5154d5cbd mutation-survivor: the red-check arm's wiring is pinned by text greps only; two of my mutants of it pass the self-test

bus-nonce: 41608c617bc90cc807a94238222a1a3f

Round 1. Head measured: 755949528b55769455419754a8ba57e5154d5cbd (detached worktree, finder-independent harness: my own mutants and my own dq_backticks fixtures).

## Block

Carry 5's whole claim is that an unanswered red is refused before the heavy slot is taken. The self-test pins the function (`reds_arm` rc 1/0/3 via stubs) and the call ORDER by an awk grep over the flow text, but nothing drives the wiring that acts on the rc. I planted two mutants; `bash tools/pr/prepr.sh --self-test` stays 451 passed, 0 failed on both (ev/mutant-a.diff, ev/mutant-b.diff, ev/ma.txt, ev/mb.txt):

- Mutant A, step 1a2 ignores a concluded red: `EARLY_REDS_RC=$?` replaced by `EARLY_REDS_RC=0`. The arm is still called before the slot and step 7c still prints, yet the early refusal never fires. SURVIVES.
- Mutant B, `--body-check` drops `--pr-branch`: the guard `if [ "${3:-}" = "--pr-branch" ] && ...` replaced by `if false`. The case still textually contains `--pr-branch` ... `reds_arm`, so the grep passes. SURVIVES.
- Mutant C, body_push never passes `--pr-branch`: caught by "body_push passes --pr-branch when origin holds fix/<topic>" (450 passed, 1 failed). Null control: clean head 451 passed, 0 failed.

Needed: a behavioural row for each, e.g. run the extracted step 1a2 block (and the `--body-check ... --pr-branch` entry) with the stubbed arm returning rc 1 and assert the `ancestry reds` step line and the exit code, plus the same with rc 0/3 as the null control.

## Findings

- Mutants A and B above survive; the wiring of carry 5 (early refusal in the main flow, `--body-check --pr-branch` refusal) has no behavioural pin. Fix: add the two behavioural rows. Carry: R10-PREPR-CAP
- The body's figure "git diff --stat origin/main...HEAD shows 2 files, 128 insertions, 26 deletions" does not hold at this head: the three-dot diff is 3 files, 129 insertions, 26 deletions (the delivery row added after the figure was taken). Fix: restate it. Carry: R10-PREPR-CAP
- Carry 7's 5 s cost cap is unmeasured by me as well as by the body: the claims generator needs scipy/homeassistant deps absent from this seat's venvs, so I could not time 6g on a strings.json-only diff. The body's statement that it is unmeasured is accurate; the cap check is still owed. Carry: R10-PREPR-CAP

## Evidence

- Self-test at the head: `bash tools/pr/prepr.sh --self-test` 451 passed, 0 failed, rc 0 (ev/selftest.txt); matches the body.
- The body's three named mutants were not re-run individually; I ran the self-test with the structural pins as is and my own three mutants (above).
- Carry 6, own fixtures against the extracted `dq_backticks`: bare backtick in unquoted heredoc body reported (line 2); inside double quotes in that body reported; quoted `<<'EOF'` hidden; `<<"EOF"` hidden and scan resumes after (line 4 reported); escaped delimiter hidden; `<<-EOF` closes and scan resumes; heredoc inside `$( )` reported. All as intended.
- Carry 7: `CLAIMS_READS` = CLAIMS_INPUTS + generator; trigger and the `pinned_touched` use are consistent in step 6g and in the main flow's claims-register step.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED; no budget file, closure, claim file, VERSION, manifest or RELEASE_NOTES touched (three-dot name list); no host path in added lines.
- `git merge-tree --write-tree origin/main <head>`: exit 0, clean.
- Delivery row dev/programme/delivery/3150.md is in the three-dot diff. `## Red checks` says none; at render time no check run had concluded red (packet digest). carry_audit at the head: 1 finding item, 1 routed, 0 unrouted. Forward-carry routes carries 8-27 with `Carry: R10-PREPR-CAP`.
- CI: `merge_train.py classify` returned 3 (WAIT, "pending: gate red: none") on each run; several heads' jobs (fast, coverage, closures, browser, python CodeQL) were still in progress. CI is therefore not concluded; this block does not rest on CI.
- Ran as one round: this is round 1.
