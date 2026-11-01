Fix review: merge 1a6a7e6a8bf1cbe04f37989aaedbab66165df624

bus-nonce: 0e7ef8ba666b40f1ebce5484314286be

Round 2 scoped re-check (round 1 blocked this head root-cause-unanswered). Head measured: 1a6a7e6a8bf1cbe04f37989aaedbab66165df624, unmoved since round 1.

## Findings

- The round-1 non-blocking findings stay carried and are not blockers: the self-test scaffolding survivors (about 60 of 81 on the driver's own added lines) and the migration of the other seat-local mutant drivers remain open. Carry: R10-MUTANT-RUN-DRIVER

## Evidence

- Head: PR head is 1a6a7e6a8bf1cbe04f37989aaedbab66165df624, equal to the round-1 head; the body's ## Head names it.
- Check-runs API, all pages, at this head: the only concluded red is governance / delivery-status (id 125000395367). pr-contract / pr-contract (three runs, last concluded 22:31:32Z) and gate (three runs) are now success.
- Body ## Red checks names governance / delivery-status and answers it: OVERDUE row for #3096 (13 commits since), plus #3066; the log prints "NOT a required context and a red here blocks no merge". #3151 is not in the log's list. Cheaper detector: none (the check is the detector); state d, no countermeasure recorded.
- Causal claim verified: three-dot diff touches governance.yml with one 7-line hunk adding a step in the instrument-self-tests job; the delivery-status job is untouched. The log shows the check graded main's pinned rows, not this branch's. The only delivery-adjacent change is the new row dev/programme/delivery/3151.md, which is not in the overdue list.
- mutant_run.py --self-test: 40 checks, 0 failed (re-run here). Round-1 mutants stand.
- git merge-tree --write-tree origin/main head: rc 0, no conflict.
- merge_train.py classify: GREEN (pending none, red none), rc 0.
- Commit messages carry no Claude footer, trailer or session link.
- Round 2 of this review.
