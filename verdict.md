Fix review: blocked 95c7e60422baf9333ae6e25fad972865698a4215 class-open: review_owed still carries a blocked verdict's head, which re-enters as a prior through the bus dispatch record

bus-nonce: 1b6e0c73217c5b9853e3df1fdcf83a9a

## Round

Round 2 of the fix review of #3241 (R10-CARRY-RESIDUE). Opus reviewer, cloud seat, detached worktrees at head 95c7e60422baf9333ae6e25fad972865698a4215 and merge base dc0a170b671814be196a54b1c71e29449f54d6d7. `git diff <base>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.

## Block

The round-1 defect "a blocked verdict carried" is not closed in production. The repair takes `review_owed`'s priors from the heads of `merge` verdicts **plus every dispatched head** (`tools/audit/seat/ledger.py`, `priors = [...] + sorted(h for k, h in dispatched if k == str(n))`). The tick builds `dispatched` from bus.sh's dispatch record (`orchestrator_tick.py` `_dispatched`). bus.sh appends every dispatch to that record and never prunes it (`bus.sh:624`), and it refuses a verdict whose head has no dispatch at that head (`bus.sh:195-198`). So every blocked verdict's head is always in `dispatched`. When such a PR's head then moves only by a clean merge of main, `git_recarry(blocked_head, new_head)` is True and the tick prints an unflagged `CARRY:`. It does not print `REVIEW OWED`. That is the case fix-review.md step 12 rules out: only a merge verdict carries, and a red CI never carries.

My own probe, `ev/blocked_dispatched.py`, run against the head's ledger.py (`ev/probe_blocked_dispatched.txt`):

    blocked verdict, head X not in dispatch record : ['REVIEW OWED: #9 cb8d7b749b6d']
    blocked verdict, head X in dispatch record     : ['CARRY: #9 cb8d7b749b6d']

The in-tree null controls do not catch this:
- ledger.py's "a blocked verdict's head is no prior, whatever its class" passes `dispatched=set()`;
- the tick's "same head after a blocked verdict is REVIEW OWED" runs with an empty `bus-ro` record.

Both model a state the bus cannot produce. The C9 plant is killed, but only inside that unreal state.

A concrete trigger: a PR is blocked on a red that main's own breakage caused, and the fixer merges the repaired main. The re-review is owed, and the board shows `CARRY`.

Repair direction, for the fixer to own:
- a dispatched head stops being a prior once any verdict names it, or once the newest verdict at it is blocked;
- add a fixture whose blocked head is also in `dispatched`, and a plant that drops that exclusion.

## Findings

- Defect: `review_owed` takes a dispatched head as a prior even after a blocked verdict at that head. Under bus.sh's append-only dispatch record this re-opens the blocked-carry path that the body says round 2 closed. The in-tree null controls (ledger.py C9 row, tick CARRY/RECORD-OWED row) pass an empty dispatch set, so they cannot see it. Probe and output in `ev/`. Carry: R10-CARRY-RESIDUE
- Follow-up: the body leaves `dev/governance/roles/standing-tick.md` unedited "for the owner", although that file states the ancestor-recarry test that the new `CARRY:` line implements. The brief allows no deferral, and a policy edit needs the owner's approval before merging, not before drafting (CLAUDE.md). So the repair round should draft the line naming `CARRY:` in this PR and surface it for the owner's review, or the body should record the owner's refusal. Carry: R10-CARRY-RESIDUE

## Evidence

- Head measured: 95c7e60422baf9333ae6e25fad972865698a4215 (`ev/HEAD.txt`). The PR body's Head section names it. Its tree differs from code head 725767534 only by the no-ff merge commit: `git diff 725767534 <head>` is empty.
- Merge with main: `git merge-tree --write-tree origin/main <head>` gives exit 0 and tree c86f527ab. No conflict.
- CI: `merge_train.py classify <head> --pr 3241` printed `GREEN 95c7e60422baf9333ae6e25fad972865698a4215 pending: none red: none` (rc=0, `ev/classify.txt`). No red concluded at this head, so no Red-checks answer is owed for it. The body answers the previous head's reds.
- Three-dot diff: 8 files. It includes `dev/programme/delivery/3241.md`. It does not touch `VERSION`, the manifest or RELEASE_NOTES (0 lines), and it touches no golden or claim file.
- Self-tests at base and head (`ev/selftests.txt`). These reproduce every count in the body's Null control and Figures:
  - ledger: 77 → 89
  - orchestrator_tick: 272 → 275
  - owed_unactioned: 46 → 47
  - beat_jobs: 107 → 107
  - r10_ledger_mutants: 135 → 177
- Mutation sweep, my run at the head (`ev/mutants_all.txt`): `plants: 62, without a FAIL line: none`. Each of C1-C14 and T3 gives rc=1 with fails>=1 (T3 fails=6, C12 fails=2). `--null` gives rc=0 fails=0 for all six owners (`ev/mutants_null.txt`). These match the body's table.
- Gate scripts (`ev/gate_head2.txt`, `ev/gate_base.txt`), identical at the head and at the base:
  - `closure.py select` at the head: `MODE: SCOPED -- 4 script(s) run, 29 scoped out`, naming debug_collect, doc_claims, entities and features. This matches the body.
  - Results: STRUCTURE RATCHET PASSED; ALL 2632 ENTITY CHECKS PASSED; 162 DEBUG COLLECT; 296 doc_claims; 4876 FEATURE.
  - The head run used a separate worktree from the mutant sweep, so the sweep's in-place plants cannot have touched it.
- Carry 1 at the base (null control), delivered:
  - df9bfd301 removes the `pending.attribution` entry from `tools/policy/field_coverage.mjs`; only the `ignore` entry is left at dc0a170b6 line 114.
  - `node tools/policy/field_coverage.mjs` gives rc=0 (`ev/carries123_base.txt`).
- Carry 2 at the base, delivered:
  - `.claude/hooks/pre-bash.sh` is wired in `.claude/settings.json`; policy_lint has `HOOK_TOOLS` and REQUIRED lists it; 408644f7f is an ancestor of the base.
  - The hook self-test gives 26 passed, 0 failed.
  - My stdin probes: `pkill -f x`, `killall python3` and `kill $(pgrep -f x)` give rc=2; `kill $!` and `grep -n pkill f` give rc=0.
  - `policy_lint --hooks`: `HOOKS ok: 4 wired hook(s)`.
- Carry 3 at the base, delivered. `dev/audit/harnesses/agreement_two_pr.mjs` was run with the base grader:
  - `identical:... (awaits {P})` gives TWO-PR HELD, rc=0 (`ev/agreement_two_pr_base.txt`).
  - Null control without the `(awaits ...)` clause gives `TWO-PR BROKEN at main2 push, PR C by mainU`, rc=1 (`ev/agreement_two_pr_base_null.txt`). The deadlock is answered at the base by 82f333b9c.
- Carry 4 at the base, delivered.
  - The owner fixture's `loop_cpu_ratio` budget is 0.249 at both base and head (tests/replay.py), and the head changes only the comment.
  - I re-read two of the five cited CI logs myself:
    - job 125240101580: `loop_cpu_ratio 0.128`, ref_ms 30.7, owner `cycle_cost` ok;
    - job 125461180429: `loop_cpu_ratio 0.189`, ref_ms 24.1, owner `cycle_cost` ok.
  - Not re-read by me: 0.1339, 0.1418 and 0.1433 (jobs 125160076828, 125097530406, 125316010511).
  - The margins re-derive: 0.128/0.1245 = 1.028 and 1 - 0.189/0.249 = 0.241.
  - The floor margin is thin (2.8 %), but every cited CI reading is in the band, and the tree comment now records the margin. Carry: dismissed: evidence, not a finding.
- Carries 5 and 6 are absent at the base. `git grep -E "RECORD-OWED|record_owed|git_recarry"` finds none of them in base ledger.py. The base hits for `CARRY:` are other mechanisms: queue_pre_flight's `CARRY: yes`, and the tick's weekly carry sweep. So building them here is not duplicate work.
- The body's `owed_unactioned.py` key_of fix, `RECORD-OWED:` keyed on head12, is confirmed by its row and by plant C10.
- Harness: none named by a finder. The instrument is the fixer's in-tree `r10_ledger_mutants.py`. My own probe is `ev/blocked_dispatched.py`, which is out of tree and disclosed as mine.
