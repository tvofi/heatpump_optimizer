Fix review: merge 7d83298850c5364e961a2e63cfdfeeb517b255a3

bus-nonce: c8f319e4129b550591656f4d3c21f47f

## Round

Round 2 delta review. Head reviewed: 7d83298850c5364e961a2e63cfdfeeb517b255a3. Round 1 reviewed 1a7225e826d44b009a37905e19512ab0eafb1035 and blocked it as carry-dest-done (verdict/2807 502e8331). I reviewed only the P110 re-route, as the brief scopes it.

## Findings

- P110 still calls `merge_train.py` "a 2000-line hot file" (line 67). Round 1 measured 4978 lines at 60cd447a0 and 5553 at origin/main. The figure is in the Considered argument against a priority drain. Correcting it would strengthen that argument, and it decides nothing in the ruling. Carry: dismissed: a wording figure that strengthens the same REJECT of the priority-drain variant when corrected, and the round-2 scope is the re-route only.
- The PR body's opening sentence still says "four rulings, P106-P109 (S6-V38 to S6-V41)". The file has five (P106-P110, V38-V42). The body's Verdicts list and Figures are correct. The title is still the merge-commit subject, and the delivery row copies it. Round 1 recorded the title. Carry: dismissed: body prose and title only, outside the file the merge records; the orchestrator can retitle or patch the body at merge with handoff_push.sh / body_patch.sh, as round 1 stated.
- R10-TRAIN-OVERLAP-GRADE is one of the groups R10-FLOW-MQ-PROBE's carry (tvofi card 4) may close as moot after the merge-queue probe. If that happens, P110's re-open condition loses its destination. The roster lists no `after` edge on OVERLAP-GRADE, although that carry says one holds it. Carry: R10-FLOW-MQ-PROBE

## Evidence

- (1) Destination text: on P110 at the head, the `Verdict:` line (61), Considered (66) and What would change the answer (70) all name R10-TRAIN-OVERLAP-GRADE. R10-FLOW-AUTOTRAIN and R10-TRAIN-UPGRADE appear only as rejected candidates ("done, so neither takes a carry"). Line 62 quotes the coordinator's original routing request and is not a destination. No carry text names either done group as a destination (ev/figures.txt).
- Delta: `git diff 1a7225e8 7d832988` touches only `dev/programme/triage/s6-batch23.md`, 3 lines, all inside P110: its Verdict line, one Considered bullet and its What would change the answer line. P106 to P109 and the delivery row are byte-identical to the round-1 head (ev/diff.txt).
- (2) Roster: on origin/handoff/audit-r10-roster at e64be204d, R10-TRAIN-OVERLAP-GRADE has `resume.stage` `queued`, so it is neither done nor absorbed. Its files are `tools/audit/seat/merge_train.py` and `tools/audit/seat/INSTRUMENTS.md`, with hot_files `merge_train.py`. R10-FLOW-AUTOTRAIN has stage `done` (pr 2780) and R10-TRAIN-UPGRADE has stage `done` (ev/carry_audit.txt).
- (3) carry-dest-done: at the head, `tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check` reads a Findings item carried to R10-TRAIN-OVERLAP-GRADE as routed (0 bad destinations). Controls on the same instrument and roster: carrying the same item to R10-FLOW-AUTOTRAIN gives `BAD-DEST ... is done (resume.stage done)`. The same happens for R10-TRAIN-UPGRADE, and R10-NO-SUCH gives `not a group of the roster`. So the check discriminates, and the round-1 block no longer holds (ev/carry_audit.txt).
- (4) Scope: the three-dot diff from the merge base touches exactly `dev/programme/delivery/2807.md` (+1) and `dev/programme/triage/s6-batch23.md` (+70). A grep for home/host path prefixes (`/home/`, `/Users/`, `/root/`) over that diff finds 0 hits.
- Verdict figure: `grep -oE '^Verdict: (ACCEPT|DEFER|REJECT)' | sort | uniq -c` at the head gives 3 DEFER and 2 REJECT over 5 `## P` entries. This matches the body's Figures and its Verdicts list, which now names P110 -> R10-TRAIN-OVERLAP-GRADE.
- Merges: `git merge-tree --write-tree origin/main 7d832988` exits 0 with no conflict (ev/diff.txt).
- CI on 7d832988, from the check-runs API (43 runs): none concluded failure. Concluded success: closures, fast (3.14), typing, coverage, coverage-ratchet, browser, arch-instrument, arch-score, policy-docs, closure-scope, wave-script, nightly-status, delivery-status, env-matrix, mutation, briefs, budget-raise-gate, hassfest, validate-hacs, lane-proofs, graders-head-copy and the codeql analyses. Skipped: the autofix jobs, ci-ratchet, mutation-pins, replay, nightly-ha, record, kernel-points. Still `in_progress` when read: `governance / instrument-self-tests`, and `prelude` in run 40201289445. The body's `## Red checks: none` is consistent with this.
- Mutation proof: n/a, because the PR is a ruling record. The consumer `roster_edit.ruling_verdict` was proved in round 1, and the Verdict lines it reads are unchanged in kind (P110 is still DEFER).
- I did not run bus.sh. This verdict returns on probe/rev-2807-c8f319e4.
