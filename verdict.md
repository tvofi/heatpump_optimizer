Fix review: blocked 5e83e3d8897aeb3661aa20278c2fd872284f04fb carry-missing: carry 6 (triage P163, the lock-age STUCK andon) is neither implemented at the head nor dispositioned in the body, which answers only carries 1-5

bus-nonce: 70ea12a8be0ecb401a4acb820ee0b975

Round 4, a full review at head `5e83e3d8897aeb3661aa20278c2fd872284f04fb`. The fixer's delta since round 3 (`e414c7eab`) is `37bd04858`, one file, `tools/audit/seat/pr_args.sh`, 6 lines added and 2 removed. The rest of the delta is main merges, and inside this PR's files the head-vs-round-3 diff is exactly `37bd04858` (`ev/`). I measured from a detached worktree at the head. `refs/pull/2825/head` and `fix/r10-update-pr-signals` still named it when I wrote this. The roles diff (`merge-base...origin/main -- dev/governance/roles/`) is empty, so the contract is current.

This is the fourth review round. Under the three-round rule `fixer.md` owes a re-cut, not a repair. The code is sound: round 3's block is closed, and so are every block before it. What remains is one unanswered roster carry. It can be closed by routing it, without new code.

## Block

1. **carry-missing: carry 6 of 6 (triage P163, the lock-age andon, V84).**
   - What the carry asks for:
     - `pr_branch_lock` writes its start epoch next to the pid.
     - `cloud_relay.sh` reports any lock older than `HPO_PUSH_STUCK_SECS` (default 900) as `STUCK <branch> <pid> <age>s`.
     - Its controls: a lock aged 901 s is reported and one aged 899 s is not; a released lock is never reported; a mutant that reads the file's mtime fails.
   - What the head has: `git grep -nE 'STUCK|HPO_PUSH_STUCK' 5e83e3d8 -- tools/audit/seat` is empty (`ev/carry6-grep.txt`). There is no fixture and no mutant.
   - What the body has: its "Carries, item by item" lists `[0]`–`[4]`, which are carries 1–5. P163 appears nowhere: not as met, not as dismissed, not as forward-carried.
   - Timing: the ruling (`dev/programme/triage/s6-batch29.md#P163`, commit `9ddadc766`, 2026-10-25 20:02Z) is older than this round's code commit (2026-10-26 00:35Z). The fixer's dispatch rendered no carries (a known `--group` defect, per my brief), so the omission may not be the fixer's fault. The verdict still has to block on it.
   - How to resolve. Either:
     - implement it, with its three controls;
     - or put a disposition in the body with a destination. P163 itself names the follow-on fixer `dispatch/fixer-r10-pusher-reap` as the owner of stuck push runs, so a `roster_edit.py` re-route of the carry to that group, plus one body line `Carry: <that group>`, would answer it without code in this PR.
   - That choice belongs to the orchestrator: a re-cut on round 4, or a re-route.

## Findings

- Carry 6 (P163) is not implemented and not dispositioned. This is Block 1. Carry: R10-UPDATE-PR-SIGNALS
- The body is stale on round 4. It describes rounds 1–3 only, and its figures are "at the head `cfc707961`". It names neither `37bd04858`'s change (the `mut:drain` and `mut:pushhold` arms now wait for the lock free, bounded at 200 ticks) nor any measurement of that change. Its `## Red checks` says "This head has no CI run yet". `fixer.md` owes the round's own figures. Carry: R10-UPDATE-PR-SIGNALS
- Round 4's bound counts ticks, not seconds. Its comment says "bounded at 10 s, a third of the stub's 30 s push". Under 6-way load on 4 CPUs, my timing probe measured the 200-tick wait at 15.4 s and 15.5 s of wall time (`ev/nullctl-wait-7.txt`, `ev/nullctl-wait-8.txt`). That is still under the push, so the arm is not vacuous today. But each tick spawns a Python process, so under heavier load the bound grows with load. If it ever passed the push's remaining time, the two mutant arms would read `free` against a correct holder and pass without testing anything. A deadline on wall time (`date +%s`) would make the comment true. Carry: R10-UPDATE-PR-SIGNALS
- Carry 4 (quiet output) stays deferred to R10-FLOW-JIDOKA, which owns `prepr.sh`'s convention; `prepr.sh` has no quiet flag on origin/main. The deferral is sound. I did not open the roster to confirm the carry landed there. Carry: R10-FLOW-JIDOKA
- The 12 seat self-tests outside this group's files that do not yet enter through `pr_bounded` are routed by the body, which also states that the bound must survive a group KILL. Carry: R10-FLOW-JIDOKA
- Carried over from round 3: the millisecond startup window in `PR_BOUND_PY` before the watchdog's `setsid`. Carry: dismissed: a group KILL would have to land in the self-test's first millisecond; no realistic caller does that, and the fix costs a handshake pipe (round 3's disposition, unchanged)

## Evidence

The round-3 block (a nondeterministic `mut:drain`/`mut:pushhold` arm) is closed. I measured it under round 3's own perturbation: six head runs of `pr_args.sh --self-test` in parallel on 4 CPUs.
- RESULT par6: 6 of 6 green, each `pr_args self-test: 123 checks, 0 failed`, rc 0, real 3m12s–3m16s (`ev/par6-1..6.txt`, `ev/par6-summary.txt`).
- Round 3 measured 4 of 6 red under the same load at `e414c7eab`.
- 2 more head runs under a second 6-way load were green, 123/0 (`ev/load-5.txt`, `ev/load-6.txt`).
- In total, 8 of 8 head runs were green under load.

Null control for round 4's new wait. My own probe, not the finder's (`ev/nullctl-probe.diff`):
- It adds a `ctl` arm that deletes no line but goes through the same `untilfree "$lf" 200` path, and requires `held`.
- RESULT nullctl: 2 of 2 runs under load gave `124 checks, 0 failed`, with `NULLCTL ... reads held at the drain/pushhold bound` ok.
- So a correct holder still reads `held` at the bound, and the mutant arms can tell the two apart.

Real-file mutation proof. I deleted one line from the head's real `pr_args.sh` and ran the whole self-test, under load:
- `# mut:drain` (`ev/mutant-drain-real.diff`): `123 checks, 4 failed`, rc 1. The failures were the SIGKILL lock-held, BUSY and worktree arms, plus the `mut:stop` BUSY arm (`ev/mutant-drain-real.txt`).
- `# mut:pushhold` (`ev/mutant-pushhold-real.diff`): `123 checks, 4 failed`, rc 1, the same four arms (`ev/mutant-pushhold-real.txt`).
- Both mutants are killed by the positive arms, not only by their own mutant arms.

Carry check, item by item:
- [1] the #2469 split:
  - SIGKILL frees the lock early: met. `mut:drain` and `mut:pushhold` are killed, as above.
  - A group signal reaches the holder: met. The grpTERM and grpHUP arms and `mut:holdsig` pass in every head run.
  - 75 under `set -e`: met. The `mut:busy75` arm passes.
  - Determinism across containers: met now, by the par6 RESULT above.
- [2] Revision 12:
  - Lock half: shown not to apply, as accepted since round 1.
  - Self-test half: met by `pr_bounded`, including a group KILL (round 3's measurement). Unchanged in round 4.
- [3] The worktree left on the branch: met, for SIGKILL too. `mut:detach` passes in every head run.
- [4] Quiet output: deferred to R10-FLOW-JIDOKA; see Findings.
- [5] #2549's relay half: met in round 2. `cloud_relay.sh` is unchanged since then, so I did not re-run it this round.
- [6] P163: not met; see Block 1.

Merge and record:
- `git merge-tree --write-tree origin/main 5e83e3d8` (origin/main `63a1c5fe8`) gives tree `c8e8e18ea`, exit 0, no conflict (`ev/merge-tree.txt`).
- `dev/programme/delivery/2825.md` is in the three-dot diff.
- No `*_budgets.json`, `VERSION`, manifest or notes heading is touched.

CI on this head, read from the check-runs API:
- Every completed gate check is green, including `governance / instrument-self-tests` (which runs this self-test), `tests / closures`, `tests / mutation`, `tests / fast (3.14)`, `budget-raise-gate` and `policy-docs`.
- `governance / delivery-status` is red on main's own overdue rows, as in rounds 2 and 3. The diff adds only its own delivery row, so the red is not this PR's. It is not a required check and does not block.
- `tests / coverage` and `codeql / Analyze (python)` were still in progress when I read them.

Figures I did not re-derive: the body's round-1 to round-3 failing-test-first runs, the class greps, the structure, archscore, closure and `ci_predict` rows (CI's own runs are green), and the `cloud_relay-29` harness mutant (unchanged since round 2, which reproduced it).

Instruments: `ev/nullctl-probe.diff` and its timing lines are my own, built for this review. The par6 load is round 3's perturbation, re-run.
