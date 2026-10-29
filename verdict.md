Fix review: merge 6e7f2a1881b015e9de3038bd479e4db96671ca40

bus-nonce: e0379f075b1790900f016e84eed1f4c9

## Scope

This is a delta review following the merge verdict at 000eae090. The head `6e7f2a1881b015e9de3038bd479e4db96671ca40` merges `0c209ba2c` into 000eae090. That commit is a hand-resolved merge of origin/main `b87019b86` (#2933) into 000eae090. The tree at the head equals the tree at 0c209ba2c.

## Evidence

- The resolution is confined to one file. `git merge-tree --write-tree --name-only 000eae090 b87019b86` reports its only conflict in `dev/governance/roles/fix-review.md`. The resolved tree differs from git's automatic tree only in that file (ev/delta.txt).
- The branch's own diff is otherwise unchanged. Diffed three-dot against its merge base, 8 of its 9 files have identical +/- lines at 000eae090 (over 66974d473) and at this head (over b87019b86). The one difference is `fix-review.md` (ev/delta.txt).
- I read the merged `fix-review.md` back (orchestrator.md section 6), and every clause from both sides survives.
  - The main side's clauses (#2933, lines 134-138 at b87019b86):
    - the first-line grammar `Fix review: merge <head40>` / `blocked <head40> <class>: <reason>`
    - class `[a-z-]+` and "(a script routes on it)"
    - then the `bus-nonce: <nonce>` line
    - "an evidence file names the head", kept as "(a file there names the head)"
    - "a cloud seat, with no `push-verdict`"
    - `cloud_relay.sh`'s layout: `ev/` and subject `verdict <pr> <head40>`
    - "to a fresh repository"
    - `probe/rev-<pr>-<nonce first 8>`

    All of these now sit in the line-7 paragraph.
  - The branch side's clauses (P200):
    - the four relay checks
    - "report its output to be confirmed"
    - the nonce carried in the verdict, now "then your brief's `bus-nonce: <nonce>`"
    - the shortened `fixer.md` preamble
    - "one that does not parse is refused", now covering both the first line and the `bus-nonce:` line
  - Only text stated twice was dropped: the main side's closing paragraph, whose content moved into line 7. Nothing else was lost.
- `review_carry.py 000eae090 6e7f2a1881b015e9de3038bd479e4db96671ca40` prints `FRESH-REVIEW` (why: 0c209ba2c is not the automatic merge of its parents). That is why this delta review is owed, not a carry (ev/review_carry.txt). Its `--self-test` passes: 26 checks, 0 failed.
- Figures at this head (ev/figures.txt):
  - `policy_lint.mjs --budgets`: fix-review.md 2439/2451 tokens and 137/140 lines; fixer.md 5216/5216 tokens.
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
  - `rules_sync.mjs --check`: ok.
  - `review_packet.py --self-test`: 42 checks, 0 failed.
  - `structure.py`: STRUCTURE RATCHET PASSED.
  - The body's fix-review.md figure (2447/2451, 139/140) was measured at b51ffa069, as the body states. It is still under the cap at this head.
- Merge with current main: `git merge-tree --write-tree origin/main(741cc6932) 6e7f2a1881b015e9de3038bd479e4db96671ca40` is clean (tree 1adf8d28f). No file under `dev/governance/roles/` changed on main since b87019b86.
- Review packet: rendered at this head with no refusals (ev/review-packet.md). Its one advisory is hot-file: HPO_BUS_TRAIN_STATE is unset. carry_audit routes 2 of 2 items. figure_lint: 8 resolved, 0 refused.
- Live CI on this head (check-runs API, re-read after the render):
  - `gate` passed (123459287575, 123458371412, 123458354517).
  - `pr-contract` passed (123458912125).
  - Every other completed run passed or was skipped, except `tests / nightly-status` (123458368828).
  - nightly-status is not a required check and does not block: `gate` concluded green. The body answers it under its second `## Red checks`. I did not re-derive main's Nightly state.
- The body names this head and its two parents (step 7).

## Findings

- The body's `## Head` entry for this head says "any resolution inside the code head is described below". No description of the `fix-review.md` conflict resolution in 0c209ba2c appears anywhere in the body. The resolution itself is sound (see Evidence), so this is a body-only gap: it voids no verdict and needs no commit, and the orchestrator can add one line before merge. Carry: R10-ORCH-REVIEW-PACKET
- The body has two `## Red checks` sections: the first says "none" and the second answers nightly-status. Its opening paragraph also carries a garbled code span (`## Review carries\n\n- Carry: dismissed: ...## Forward-carry`), apparently a body-tool insertion. pr-contract passed regardless. A body edit should collapse these into one section. Carry: R10-ORCH-REVIEW-PACKET
