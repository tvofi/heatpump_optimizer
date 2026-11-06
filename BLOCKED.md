BLOCKED: R10-CARRY-RESIDUE round 3 -- the brief's part-2 carry destination is refused by carry_audit

Code head ready: bcbdcfb377d78433b122370bb21dc29b66371cfa (the parent of this commit). The ONE finding is built: failing test first
(9d16d843a, red at 95c7e604: `ledger self-test: 91 checks, 1 failed`), fix in review_owed (newest verdict per head; a
dispatched head that any verdict names is no longer a prior unless that newest verdict is merge), plant C15 added, C9/C14
re-anchored; `r10_ledger_mutants.py` sweep `plants: 63, without a FAIL line: none`, `--null` rc=0 for all six owners;
scoped gate `MODE: SCOPED -- 4 script(s) run, 29 scoped out`, all green; structure PASSED; `tools/pr/prepr.sh` (no body)
`PRE-PR: bcbdcfb377d7... rc=0`. origin/main unmoved at dc0a170b6.

Question for the orchestrator: the brief requires `Carry: R10-CARRY-RESIDUE-2` for the standing-tick.md follow-up, but
`python3 tools/audit/carry_audit.py check --body BODY.md --branch fix/r10-carry-residue` and prepr's body check both refuse:
  BAD-DEST body item a7dcb16a: R10-CARRY-RESIDUE-2: R10-CARRY-RESIDUE-2 is not a group of the roster or of origin/handoff/audit-r10-roster
  CARRY-AUDIT: 1 finding item(s): 0 routed, 0 unrouted, 1 bad destination(s)
`PR-BODY: 0 error(s)` otherwise. A fixer may not edit the roster (standing-roster's roster_edit.py) or file an issue, and
working around the refusal is forbidden, so I did not push handoff/r10-carry-residue or run body_push.sh.
Unblock: add group R10-CARRY-RESIDUE-2 to the roster (or name another destination), then push bcbdcfb to
handoff/r10-carry-residue and body_push.sh the draft BODY.md at refs/heads/handoff-wip/r10-carry-residue-body unchanged.
