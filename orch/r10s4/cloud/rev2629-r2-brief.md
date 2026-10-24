Fix reviewer, round 2, PR #2629 (tvofi/heatpump_optimizer), R10-RECORD-API-BUDGET. Head b7d2b645faf0a440f269b5734d16025058d53e61. Follow dev/governance/roles/fix-review.md from a detached worktree at that head. Re-read the head first; if it moved, the verdict is blocked.

Round 1 (git fetch origin probe/rev-2629-5c5034eb; read verdict.md) blocked on unpinned sites: the --window-cache wiring in the record job, and two cache guards (a failed enumeration cached or served, and a foreign-key file served). Verify the round-2 delta:
1. Each new check fails on its mutant and passes on the fix:
   - the R1 and R1b acceptance arm in tools/policy/policy_lint.mjs (a failing pulls stand-in is read twice: fetched twice, no file left, write guard);
   - the R2 foreign-key arm;
   - the two tests/entities.py checks on the record job's five --window-cache invocations (null: all five found; mutants M1-yaml and Y1 fail).
   Run your own mutants, not only the fixer's.
2. Acceptance reads FIXTURE ok: 92 error(s) hold 253 pins. mutation_table.py --pin-killed --base origin/main reports 0 new unpinned sites.
3. The fixer measured at 63a4dce67 and then update_pr merged main again into b7d2b645. Re-run the touched checks at the real head.
4. The body (sha1 24ff8c3b): carry_audit pr 2629 reads 0 unrouted and 0 bad. The toolchain carry now names R10-FLY-CLOUD-SETUP-TOOLCHAIN.
5. Read CI at the head from check-runs. Answer every red in ## Red checks.
Round 1's other evidence carries over unless the code it covered moved.

ev/HEAD.txt must hold the full 40-hex head sha, or the relay refuses the verdict.
Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
