Lands two stranded root-cause records under dev/audit/rca/. R10-HANDOFF-PREPR-BOUNCE.md is cited from tools/audit/seat/body_push.sh:17, tools/audit/seat/INSTRUMENTS.md:127 and dev/audit/config/bugclasses.json:2336 and was not in the tree; it is taken from 5fa9ffce0 with `git show` (no merge; that ref is 3959 commits behind) plus a status section re-derived at origin/main 50af6174f. R10-RCA-BODY-CHECK-PARITY.md existed only on handoff-body/r10-rca-body-check-parity (4fd3eef16); it is written in the shape of its neighbours, with a status section. Documentation only; no code, policy, claim file or version is touched.

## Head

16500c7403f49e8b53bd215695ba2c2af74405b3

## Mutation proof

n/a: two new markdown records under dev/audit/rca/; no production code, check or fixture changes.

## Null control

n/a: nothing here is a detector. The existing citations resolve once the file exists: `git ls-tree origin/main dev/audit/rca/R10-HANDOFF-PREPR-BOUNCE.md` printed nothing before this branch and prints the path on it.

## Figures

- Status-section figures for R10-HANDOFF-PREPR-BOUNCE at 50af6174f: harness siblings 102 (`ls dev/audit/harnesses/*.py | wc -l`), 139 listed under `inert_reads["tests/harness_headers.py"]` (python3 over tests/closures.json), 35 closures bot commits since 2026-09-25 and 15 since 2026-10-12 (`git log origin/main --since=<date> --grep='re-record closures' --oneline | wc -l`), 99 handoff refs (`git ls-remote origin 'refs/heads/handoff/*' | wc -l`), `grep -c rederive tools/pr/ci_predict.py` 0, `grep -c -i 'predict\|prepr' dev/governance/rules/ci-autofix.md` 2.
- Status-section figures for R10-RCA-BODY-CHECK-PARITY at 50af6174f: `grep -c carry_audit tools/pr/prepr.sh tools/audit/seat/body_push.sh` 0 for both; `policy_lint.mjs:6244` isNone; `carry_audit.py:94` NONE_ITEM; R10-FLOW-JIDOKA and R10-POLICY-LINT-FAMILY at stage not-started in dev/programme/rosters/wave-r10-groups.json.
- Every other figure in both records is the original seat's measurement at its own base and is labelled so in each record; none was re-run.

## Red checks

none

## Forward-carry

- G3 of the parity record: `## Forward-carry` has two graders with different grammars (policy_lint.mjs isNone, carry_audit.py NONE_ITEM); one parser must own the section. Lands in dev/programme/rosters/wave-r10-groups.json. Carry: R10-POLICY-LINT-FAMILY
- G1 and G2 of the parity record (every body-reading workflow step; a twin table pinning each run line). Lands in dev/programme/rosters/wave-r10-groups.json. Carry: R10-FLOW-JIDOKA

## Friction

none
