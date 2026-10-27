# Evidence for fix review of #2881 at 1a7484a36d0e797d73f4c1bca3a619d4bf6b6dfc

Worktree: /Users/timmalmstrom/hpo-seats/r10s6/s7-review-2881/wt (detached, sparse, at the head).
All commands below run from that worktree. Merge base 524c1896b = origin/main at review time.

RESULT head=1a7484a36d0e797d73f4c1bca3a619d4bf6b6dfc merge_base=524c1896b6943b3da03d6cad61420ced31e14c9c diff_files=2 added=82 removed=0
RESULT path:tools/pr/prepr.sh=OK path:tests/gate_lock.py=OK path:tests/closures.json=OK path:tests/run.sh=OK path:dev/programme/triage/s6-batch37.md=MISSING resolved=4 unresolved=1
RESULT recorded:stress.py=936.3 recorded:harness_headers.py=241.1 two_runs_minutes=31.21
RESULT LEASE_SECONDS=1800@78 RENEW_REFUSED_RC=75@120 renew_def=568 take_def=511 take_end=565 needs_lease_def=918 needs_lease_end=954 SLOT_MIN_SECONDS=69@116
RESULT needs_lease:two-ordinary=slot needs_lease:stress.py=lease needs_lease:harness_headers.py=lease
RESULT MACHINE_MEASURING=tests/stress.py,tests/harness_headers.py
RESULT lease_holders_claimed=2 lease_holders_in_tree=3 (run.sh/prepr.sh via needs-lease; tools/audit/judge_batch.py direct)
RESULT roster_groups=208 run.sh_in_no_group_files=true R10-PREPR-CAP.files=tools/pr/prepr.sh,tests/gate_lock.py R10-PREPR-CAP.stage=done R10-PREPR-CAP.carry=[]
RESULT triage_gate:P206=ACCEPT triage_gate:P999=None triage_gate:mutant=DEFER triage_gate:mutant_refusal_matches_body=true
RESULT check_runs_head=55 failures=0 check_runs_earlier=27 failures=0 cancellations=6
RESULT merge_tree_rc=0 brief_lint_exit=0 brief_lint_scope_covers_triage=false
RESULT delivery_row:count=1 pr=2881 batch_named=true state=open
RESULT numbering:batch35=P199-P203/V119-V123 batch36=P204/V124(open branch) batch37=P205/V125(open branch) batch38=P206/V126

## F1: the arm-2 universal

    $ git grep -n 'import gate_lock\|gate_lock\.take(' HEAD -- tools | head
    HEAD:tools/audit/judge_batch.py:90:import gate_lock  # noqa: E402
    HEAD:tools/audit/judge_batch.py:185:        gate_lock.take(self.label, lock_dir=self.lock_dir, lease_seconds=self.seconds,

    $ git show HEAD:tools/audit/judge_batch.py | sed -n '178,190p'
    class Lease:
        """The gate lease held across the batch; flock is the child's to take."""
        ...
        def _take(self) -> None:
            gate_lock.take(self.label, lock_dir=self.lock_dir, lease_seconds=self.seconds,
                           owner_pid=os.getpid())

    $ git grep -ln 'judge_batch' HEAD | head
    .claude/workflows/audit-verify.js, tests/closure.py, tests/closures.json, ...

A second route: `git show HEAD:tools/pr/prepr.sh | grep -n needs-lease` -> line 344 defers
lease-classified scripts through `needs-lease`, so prepr is not itself a counterexample to the
*classification*, but judge_batch takes the lease directly and is not in MACHINE_MEASURING.

## F2: the predecessor path

    $ git cat-file -e HEAD:dev/programme/triage/s6-batch37.md ; echo $?
    (fails)
    $ git ls-tree -r --name-only origin/main dev/programme/triage/ | sort -V | tail -2
    s6-batch34.md
    s6-batch35.md
    $ git ls-remote origin refs/heads/fix/triage-s6-batch37
    a63c6bfd59a2703f03638054410d672cc0ae1af4
    $ git show a63c6bfd:dev/programme/triage/s6-batch37.md | head -1
    # Proposal triage, session s7, batch 37 (P205)

## Figures re-derived

    $ python3 -c "import json; print(json.load(open('tests/closures.json'))['recorded']['tests/stress.py'])"
    {'rc': 0, 'seconds': 936.3}
    $ printf 'tests/foo.py tests/bar.py\n' > /tmp/scope2.txt; python3 tests/gate_lock.py needs-lease /tmp/scope2.txt
    slot
    $ printf 'tests/stress.py\n' > /tmp/scope1.txt; python3 tests/gate_lock.py needs-lease /tmp/scope1.txt
    lease
    $ grep -n 'timeout\|deadline\|max_wait' tests/gate_lock.py
    895: proc.wait(timeout=10) / 1867: holder.wait(timeout=5) / 1934: holder.wait(timeout=5)
    $ grep -n 'keeps its expiry rule' tests/gate_lock.py   -> docstring line 57, matches the batch quote

## Checks

    $ git diff --stat 51dd6d00b7c2321fe4f3acb6e3c8b68c74d6d55c 1a7484a3   -> 1 file, delivery/2881.md
    $ git merge-tree --write-tree origin/main 1a7484a3   -> tree sha, rc=0
    $ node tools/policy/brief_lint.mjs   -> exit 0 (ROSTER ok / CARRY ok; errors printed are fixtures)

## Limits

The 38-minute wait, pid 62391 and the four timestamps come from the orchestrator's live lock state
(/tmp/hpo-gate.lock/owner is not in the tree). The batch discloses that. Its bridge from the
recordings to 38 minutes ("first run's tail plus queueing") carries no command.
