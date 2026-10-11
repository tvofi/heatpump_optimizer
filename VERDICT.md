Fix review: merge 5bfddc1bd917798b28408759f6afa7ab14c2dee0

Resolution delta a4c134fce…5bfddc1bd, round 5 of the PR (contract step 12:
a `merge a4c134fce…` verdict's own resolution delta, production tree
byte-identical). Reviewer worktree detached at the head,
/Users/timmalmstrom/hpo-seats/r9rev-2119d/wt; seat venv (venv-ci) first on
PATH; scratch /Users/timmalmstrom/hpo-seats/r9rev-2119d/, evidence in
evidence/.

Delta commits (evidence/delta-commits.txt): the branch's one authored commit
db7b569bd (`fix(#2119): the drift gate's baseline worktree add refuses with
git's own reason`), plus main's own #2117 side (77d66d707, 48d47ab19,
a27c7bd44, 88cfe2cb9, merge 0f1ccbe52) and the two merges 00e5b5cdb and
5bfddc1bd that carry them. Every non-test file in the full delta diffstat
(.github/workflows/governance.yml, dev/programme/delivery/2117.md,
tools/audit/seat/merge_train.py, tools/pr/app_push.sh) is byte-identical to
main tip 0f1ccbe52 -- main-side content arriving through the merge, not
authored here. The authored change is tests/entities.py +97 (three new
checks) and tests/env_drift.py +61/-5 (the repair); ledger.py,
tests/features.py, tests/doc_claims.py and the whole custom_components tree
are byte-identical to a4c134fc (evidence/production-identity.txt).

Repair sound and minimal (tests/env_drift.py): `add_baseline_worktree` drops
`check=True, capture_output=True` for an explicit returncode check; on a
non-zero add it captures `(add.stderr or add.stdout or "no message")`, prints
git's own reason per attempt, and retries ONCE (candidates from
`baseline_worktree_candidates(tmp, attempts=2)`) on a fresh name
`baseline-{pid}-{n}` -- pid separates concurrent gate instances, ordinal
separates one instance's own retries, so no two adds contend for one
registered name and no retry meets its own half-built directory. A double
failure refuses READABLY: `BASELINE WORKTREE REFUSED: git could not check
out ... (reason)` and return 1, after cleaning tmp -- not a crash, not
silence. Same shape as stress.py's precedent the body cites.

Failing-first arm, re-run by me (not the fixer's numbers): env_drift.py
reverted at the head to a4c134fc's copy, `PYTHONPATH=tests/hastub python3
tests/entities.py` -> `3 of 2254 ENTITY CHECKS FAILED`, and the three are
exactly the new named checks ("a refused baseline worktree add reports git's
own reason, not a bare exit 128 (#2119)", "a resolvable ref builds the
baseline worktree and unregisters cleanly (null control)", "concurrent gate
instances name distinct baseline worktrees (#2119)") -- AttributeError on
the missing functions (evidence/reverted-fails.txt). Restored ->
`ALL 2254 ENTITY CHECKS PASSED` (evidence/restored-summary.txt).

`## Red checks` truthfulness: the body's `mutation` at `a4c134fc` entry
quotes the crash's own line -- run 38129371794, job 114440311454,
concluded 2026-10-11T09:47Z, `MUTATION TABLE REFUSED -- the null control
custom_components/heatpump_optimizer/accuracy.py:44 NULL_COMMENT was killed
by tests/env_drift.py (subprocess.CalledProcessError: Command '['git',
'worktree', 'add', '--detach', '/tmp/env_drift_a5dktzj3/baseline',
'e1501bf480d0d6430875f3a7334402cb00cc4dd3']' returned non-zero exit status
128.)` -- and I read that line verbatim from the job's own log
(evidence/mutation-red-quote.txt); the body names this repair at db7b569bd.
Check-runs API at a4c134fc: that `mutation` is the ONLY completed failure;
everything else green or skipped (evidence/check-runs-a4c134fc.txt). At the
measured head 5bfddc1bd: every completed check is success/neutral/skipped;
mutation, coverage, fast (3.14), closures and Analyze (python) are
in_progress at publish time -- pending, not unanswered reds
(evidence/check-runs-head.txt). No other unanswered red.

prepr at the head with the seat venv on PATH: `PRE-PR:
5bfddc1bd917798b28408759f6afa7ab14c2dee0 0000…` clean, no version edit, claim
files byte-identical to origin/main. `git merge-tree --write-tree origin/main
5bfddc1bd` exit 0.

RESULT env_drift repair: sound, minimal, failing-first confirmed at the head
RESULT delta: one authored commit, production tree byte-identical to a4c134fc
RESULT red-checks: mutation@a4c134fc quoted verbatim and answered; no other red at either head

Head-moved check at publish: ls-remote = 5bfddc1bd917798b28408759f6afa7ab14c2dee0.

bus-nonce: 84a0eec83769c1303956603d0d805720
