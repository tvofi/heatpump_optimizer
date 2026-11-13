R10-ROUND-PLAYBOOK-FINAL part 2 (Carry 42, brief items 2 to 4): the delta re-read of the eleven residue groups, folded into the playbook README and recorded in the handover.

## Head

6d39a63552d2431e7c96ca6a8196c06d376131ff

## Mutation proof

No production line: n/a for code. The README's cited paths: with `tools/audit/carry_audit.py` renamed in a scratch edit, `node tools/policy/brief_lint.mjs` prints `ERROR [(playbook)] playbook path: tools/audit/carry_auditX.py: not in the tree`; restored, it prints 0 errors and `PLAYBOOK ok`.

## Null control

At the merge base the README names no census path and the handover holds no re-read line for any of the eleven groups; here both exist (red before, green after). Every group has a line, "nothing" included.

## Figures

- `node tools/policy/policy_lint.mjs --budgets`: the cap keyed tools/audit/README.md is under both its line and token caps at this head; unraised.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `node tools/policy/brief_lint.mjs`: 0 errors; the PLAYBOOK fixture refused, the null fixture clean.

## Red checks

none

## Approval

Pending: the owner's approving review at this head. dev/audit/README.md is policy (CLAUDE.md, "Where the policy is").

## Forward-carry

- Carry 42 re-read: one line per group in dev/programme/HANDOVER.md; every group reads "nothing" to fold, because each merged diff touched internals of instruments the phase table only names. The README's other edits are the three brief items. Carry: dismissed: built in this diff
- The four open residue pull requests (3499 at e3622cb3d8, 3451 at 07941da7b5, 3491 at ece5ee3b58, 3490 at 0e64c66e3b) were read at those heads; the README says nothing about them. Pull request 3491 adds a seat-generation instrument absent from main, which brief_lint refuses in the README until it lands. The orchestrator addendum asks for a Carry to R10-CLOSEOUT-PREP for a one-line re-check at closure, but the carry audit refuses that destination (the group is carries-open, so not receivable). The re-check request is in the HANDOVER record instead. Carry: dismissed: R10-CLOSEOUT-PREP cannot receive a carry marker; pending owner confirmation of where the closure re-check goes
- The 20% correction (the exemption bar read 10%, now 20% citing dev/governance/rules/ratchet-budgets.md). Carry: dismissed: built in this diff
- The round-11 pointer bullet's list of carry contents was cut; it survives in the carries of R11-INTAKE-R10-RESIDUE on the roster branch, which lands on main at the stamp. Carry: dismissed: survives in that group's carries
- Carry 31's D11 and D13 paragraphs were not found in R11-INTAKE-R10-RESIDUE at the roster branch tip I read; the pointer bullet states their content. Carry: R11-INTAKE-R10-RESIDUE (landed on the roster branch at c01f40f5c)
- The README cites the census directory, not its CENSUS.md file: policy_lint's named-docs check refuses a named file with no cap or exclusion, and dev/governance/config/corpus_excluded.json is outside this part's files. The brief asked for the file path. Carry: R11-INTAKE-R10-RESIDUE (landed on the roster branch at c01f40f5c)
- A grep found no logic in cloud_dispatch.py for phase 6's "only arms not on main are briefed"; not this part's scope. Carry: R11-INTAKE-R10-RESIDUE (landed on the roster branch at c01f40f5c)

## Friction

none
