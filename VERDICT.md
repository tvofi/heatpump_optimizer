Fix review: merge 94f172036b6a239b3cb804673ed944a987bd7b65

bus-nonce: ffa1fd3dd8eee4713eea77d5de91acd0

Round 1. Measured at head 94f172036b6a239b3cb804673ed944a987bd7b65 (detached worktree). The PR is a triage ruling file (`dev/programme/triage/s6-batch68.md`) plus its delivery row; no production code, no VERSION, manifest or notes change (three-dot diff is those two files).

## Findings

- The R10-FLY-SEAT-ALIVE-ID group the P299 ruling accepts is not on the roster branch yet (`wave-r10-groups.json` at `1bc6fe234` has no such group); the append is the post-merge step this ruling gates, via `roster_edit.py append-group` with the triage gate. Carry: R10-FLY-SEAT-ALIVE-ID | #2985 | O1 | dismissed: the roster append is the ruling's own consumer and the gate refuses it until this file is on main
- The P300 carries (a) and (b) are texts to append to R10-ORCH-ROSTER-SCHEMA after the merge; the ruling holds them as held roster ops. Carry: R10-ORCH-ROSTER-SCHEMA | #2985 | O2 | dismissed: the ruling carries both texts verbatim and the same gate checks them on append
- The out-of-tree half of P299 (nonce check in orch_sweep.sh, `--stop` lines for dead s7 nonces, stranded P63 re-route) is sent to the orchestrator, not carried, per the P236 precedent; the body's Forward-carry says none. Carry: R10-ORCH-BEATD | #2985 | O3 | dismissed: out of tree (git ls-files count 0, re-derived) and stated in the ruling as the orchestrator's call

## Evidence

- RESULT merge: `git merge-tree --write-tree origin/main 94f172036b6a239b3cb804673ed944a987bd7b65` exit 0, tree 5975a0a14, no conflicting path (ev/merge-tree.txt).
- RESULT mutation: ruling_verdict reads P299 and P300 ACCEPT. Mutant (P299 changed to REJECT) makes triage_refusal return "...#P299 is not an ACCEPT ruling (REJECT)". Null (file absent) returns "the triage ruling ... is not on the roster branch or origin/main" (ev/mutation.txt). Matches the body.
- RESULT figures re-derived: parse_line('set-stage G done  # #2955 merged aced2589') returns ['#','#2955','merged','aced2589'] as args at head; shlex comments=True gives ['append-carry','G','@/p/b'] and ['append-carry','G','text']; `git ls-files | grep -c 'orch_sweep\|seat-launch'` = 0; `git grep seat-alive|DUPLICATE seat` in pulse.py at origin/main = nothing; R10-ORCH-BEATD resume stage done, pr 2916, commit 0b17333c2 on the roster branch; merge dates #2982/#2981/#2983 at 09:22:58Z/09:23:38Z/09:32:03Z match the main log (+01:00 local); cited triage files s6-batch2/5/21/32/36/48 exist.
- Figures I could not re-derive: seat-ledger.md:2463, launch-ledger, `seat-launch.sh --dup` output, the 374/181/136/16/3 queue counts and roster-loop line counts live in the orchestrator's state directory, not the tree. Not verified.
- Claim files, structure budgets and goldens: not touched by the diff (two markdown files); nothing to claim.
- CI at read time (check-runs API): completed checks all success or skipped (CodeQL neutral); arch-score, budget-raise-gate, policy-docs, briefs, mutation, coverage, typing, delivery-status success. In progress at read: tests / fast, closures, browser, governance / env-matrix, instrument-self-tests, prelude. No red check; body's "Red checks: none" agrees. The merge train gates on those finishing; I did not re-run any gate.
- Head: PR head is 94f172036b6a239b3cb804673ed944a987bd7b65, the head named in the body and measured here.
