Lands two stranded root-cause records under dev/audit/rca/. R10-HANDOFF-PREPR-BOUNCE.md is cited from tools/audit/seat/body_push.sh:17, tools/audit/seat/INSTRUMENTS.md:127 and dev/audit/config/bugclasses.json:2336, and was not in the tree. It is taken from 5fa9ffce0 with `git show` (no merge; that ref is 3959 commits behind), plus a status section re-derived at origin/main 50af6174f. R10-RCA-BODY-CHECK-PARITY.md existed only on handoff-body/r10-rca-body-check-parity (4fd3eef16), and that ref is no longer on origin. It is written in the shape of its neighbours, with a status section. Documentation only: no code, policy, claim file or version is touched.

This head repairs fix review `blocked 4a81d718e carry-missing` (review/2691). Each point is answered below:

- **G3's destination has finished.** R10-POLICY-LINT-FAMILY merged as #2669 without G3, so G3 is now routed to R10-FLOW-JIDOKA, in the record (section 4's "Who owns what" and `## Forward-carry`) and in this body.
- **G1 and G2 are not in JIDOKA's brief.** The roster seat appended a carry to R10-FLOW-JIDOKA at `a72ff1128` (`roster_edit append-carry`). This seat cannot edit the roster. `## Forward-carry` below says exactly what that item holds, as read back at 2026-10-24T12:24Z.
- **The stale status line.** The record's status section now reads the roster handoff, not main's copy: POLICY-LINT-FAMILY is `done` (pr 2669), JIDOKA is `in-progress`. The figure line below says the same.
- **"99 handoff refs" is not re-derivable.** It is dropped from R10-HANDOFF-PREPR-BOUNCE.md and from this body, and labelled there as a live count.

## Head

`3b5eea2062c8a444f5f921fc30a2fe4dd18150bd` merges the authored code head `3fc563ad83b2a563726bf68920196e8481dce980` and then merges origin/main `fa4dad4a7` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`3fc563ad83b2a563726bf68920196e8481dce980` is the code head. It is one commit on the previous PR head `4a81d718e`, whose last commit holds only this PR's row, `dev/programme/delivery/2691.md`. The new commit edits only the two records.

3fc563ad83b2a563726bf68920196e8481dce980

## Mutation proof

n/a: two markdown records under dev/audit/rca/. No production code, check or fixture changes.

## Null control

n/a: nothing here is a detector. The existing citations resolve once the file exists: `git ls-tree origin/main dev/audit/rca/R10-HANDOFF-PREPR-BOUNCE.md` printed nothing before this branch and prints the path on it.

## Figures

- Status-section figures for R10-HANDOFF-PREPR-BOUNCE at 50af6174f: harness siblings 102 (`ls dev/audit/harnesses/*.py | wc -l`); 139 listed under `inert_reads["tests/harness_headers.py"]` (python3 over tests/closures.json); 35 closures bot commits since 2026-09-25 and 15 since 2026-10-12 (`git log origin/main --since=<date> --grep='re-record closures' --oneline | wc -l`); `grep -c rederive tools/pr/ci_predict.py` 0; `grep -c -i 'predict\|prepr' dev/governance/rules/ci-autofix.md` 2. The handoff-ref count is a live `git ls-remote` reading, not a figure of the tree, so it is not stated.
- Status-section figures for R10-RCA-BODY-CHECK-PARITY at 50af6174f: `grep -c carry_audit tools/pr/prepr.sh tools/audit/seat/body_push.sh` 0 for both; `policy_lint.mjs:6244` isNone; `carry_audit.py:94` NONE_ITEM.
- Group stages, read on `handoff/audit-r10-roster` at `a72ff1128` (`git show a72ff1128:dev/programme/rosters/wave-r10-groups.json`, 2026-10-24T12:24Z): R10-POLICY-LINT-FAMILY `resume.stage: done`, `pr: 2669`; R10-FLOW-JIDOKA `resume.stage: in-progress`. main's copy of the same file at `ac5788f26` still reads `not-started` for both, which is not their state.
- `git ls-remote origin 'refs/heads/handoff-body/r10-rca-body*'` printed nothing at 12:24Z.
- Every other figure in both records is the original seat's measurement at its own base and is labelled so in each record. None was re-run.

## Red checks

none

## Forward-carry

- G1 and G2 of the parity record (every workflow step that reads the PR body, and a twin table pinning each step's run line, with section 4's mutants: one edited carry-step argument, one deleted arch-score row). Read back at `handoff/audit-r10-roster` `a72ff1128`: R10-FLOW-JIDOKA's last carry item names R10-RCA-BODY-CHECK-PARITY and tells its fixer to "Read section 4 of that body for the three requirements this fixer owes". It holds them by reference to `handoff-body/r10-rca-body-check-parity` `4fd3eef16`, not as text, and that ref is not on origin. Section 4 of `dev/audit/rca/R10-RCA-BODY-CHECK-PARITY.md` on this branch is the readable copy. Carry: R10-FLOW-JIDOKA
- G3 of the parity record: `## Forward-carry` has two graders with different grammars (policy_lint.mjs isNone and its path demand, carry_audit.py NONE_ITEM and seg_dests), and one parser must own the section. R10-POLICY-LINT-FAMILY merged as #2669 without it, so it is routed to JIDOKA. The same roster item at `a72ff1128` covers it by reference only: its "three requirements" are G1 to G3, but `4fd3eef16`'s own section 4 still names R10-POLICY-LINT-FAMILY for G3. Carry: R10-FLOW-JIDOKA

## Friction

none
