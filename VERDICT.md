Fix review: blocked 2f15a24cd6d64945fab6bbcfef5b443c5b78df77 root-cause-detectable: six checks are red at the head, the body's Red checks section says none, and tests/closure.py selftest fails in about three seconds on this box
bus-nonce: 5183a3a83c758221243b4e9c30303c66

# Fix review — PR #2869 (R10-FLOW-AUDIT-PLAN), round 1

Measured at `2f15a24cd6d64945fab6bbcfef5b443c5b78df77` from a detached worktree at
`/tmp/rev-2869`. The SHA was the PR head when I started and is the head I measured.

This is not a solver change; I judged it as a plan/instrument change. No policy file
is in the diff: `dev/governance/`, `.cursor/rules/` and `CLAUDE.md` are all absent
from the three-dot name list (`evidence/diff-three-dot.txt`), so there is no
owner-approval flag to raise. No `VERSION`, manifest, `RELEASE_NOTES.md` heading,
budget file, golden fixture, claim file or mutation ledger is in the diff either.

I am posting a verdict rather than handing back unverdicted although
`pr-contract / pr-contract` is itself red: findings 2–5 are defects a body edit
cannot cure, and they were reproduced here without reading the body's account.

## Findings

### 1. Six checks are red at the head and the body answers none of them — `root-cause-detectable`

`evidence/check-runs-non-green.txt`, every non-green context by full name:

```
gate=failure
governance / instrument-self-tests=failure
pr-contract / pr-contract=failure
tests / closures=failure
tests / closures-autofix=failure
tests / fast (3.14)=failure
```

The body's `## Red checks` section reads `none`. `pr-contract / pr-contract`
(job 121993616354, started 2026-10-27T03:33:58Z, i.e. after the last red concluded)
refuses the body with the same sentence four times
(`evidence/pr-contract-reds.txt`):

```
ERROR [pr-body] /tmp/pr-body.md: check `tests / fast (3.14)` is red and `## Red checks` does not name it.
```

Cheaper detectors, both seconds, both runnable on the author's own box:

- `python3 tests/closure.py selftest` — this fails **on macOS, at this head, in about
  three seconds** (`evidence/closure-selftest-failure.txt`). There is no environment
  excuse for finding 3.
- `python3 -I tools/audit/seat/plan_audit.py --self-test` under a scrubbed git identity
  (`evidence/plan-audit-selftest.txt`) — about two seconds, and it reproduces the Linux
  traceback exactly.

Note the interaction: the scoped gate the body quotes runs three scripts
(`tests/doc_claims.py`, `tests/entities.py`, `tests/harness_headers.py`) and does **not**
select `tests/closure.py`, so the scoped run could not have shown finding 3. Running
`prepr.sh` and `tests/closure.py selftest` directly is the standing cost.

Carry: R10-FLOW-AUDIT-PLAN

### 2. `plan_audit.py --self-test` is not portable: it crashes wherever no global git identity exists

`governance / instrument-self-tests` (job 121982854726) dies in the step this PR adds to
`.github/workflows/governance.yml`:

```
File ".../tools/audit/seat/plan_audit.py", line 553, in self_test
    git("add", "-A", cwd=repo); git("commit", "-qm", "a", cwd=repo)
subprocess.CalledProcessError: Command '['git', '-C', '/tmp/plan-audit-couple-oto5h4fb',
'commit', '-qm', 'a']' returned non-zero exit status 128.
```

Reproduced here, same tree, macOS, only the ambient git identity removed
(`evidence/plan-audit-selftest.txt`):

```
$ env -i PATH=... HOME=/tmp/emptyhome GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null \
    python3 -I tools/audit/seat/plan_audit.py --self-test
subprocess.CalledProcessError: Command '['git', '-C', '/tmp/plan-audit-couple-rw_afzdi',
'commit', '-qm', 'a']' returned non-zero exit status 128.
```

Cause, exact: `tools/audit/seat/plan_audit.py:550` binds
`env = throwaway_git_init(repo, "-q", "-b", "main")` and never uses it; `git()`
(`plan_audit.py:76-77`) takes no `env` argument, so every commit runs under the ambient
environment. `tests/throwaway_git.py:109`'s `throwaway_git_env()` is what carries the
identity (`env.update(IDENTITY, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", ...)`);
`throwaway_git_init` writes only `CONFIG` (auto-maintenance) into the repository's own
config. The module imports `throwaway_git_env` at `plan_audit.py:547` and never calls it.
`tests/throwaway_git.py:121` `throwaway_git_environ()` exists for exactly this shape —
its docstring: *"for a self-test whose every git call ... passes no env= then inherits the
env layer too"*.

Consequence for the body's own claims: `## Figures`'
`plan_audit self-test: 25 checks, 0 failed` and the mutation proof's "each restoring to
`plan_audit self-test: 25 checks, 0 failed`" hold only on a box with a global identity.
I measured both arms: `25 checks, 0 failed` with the identity, `exit status 128` without
(`evidence/plan-audit-selftest.txt`). The restoration baseline the 25-mutation battery
rests on is therefore environment-dependent.

Carry: R10-FLOW-AUDIT-PLAN

### 3. `plan_audit.py:314` takes a `--name-only` diff without rename detection

`tests/closure.py selftest` fails on this head, reproduced here
(`evidence/closure-selftest-failure.txt`):

```
$ python3 tests/closure.py selftest
  FAIL no rename-detecting --name-only diff under RENAME_SITES  [tools/audit/seat/plan_audit.py:314:
  changed = [p for p in git("diff", "--name-only", parent, sha, "--", PKG, cwd=repo).splitlines()]
1 of 117 closure shrink pins FAILED
```

`RENAME_SITES` covers `tools/audit/seat/*.py` (`tests/closure.py:2765`), so the line must
carry `-M`/`--find-renames` or be registered in the tree's exact-and-per-file allow shape.
Beyond the check, `coupling()` counts a renamed module as one side changed only, so the
change-coupling holdout can mis-count any merge that renames a module — the metric
`plan_audit.py` exists to hold steady.

Carry: R10-FLOW-AUDIT-PLAN

### 4. The new workflow is classified INERT while the gate reads it

`is_inert(".claude/workflows/audit-plan.js")` is `True` at this head
(`evidence/inert-reads.txt`), while the tree's two other read workflow scripts are not:
`web-fix-wave.js` and `audit-find.js` are both `INERT_EXCEPT`. Both CI closures jobs
report the contradiction:

- `tests / closures` (job 121983008811): `INERT READS UNDER-APPROXIMATED ... tests/entities.py: .claude/workflows/audit-plan.js`
- `tests / closures-autofix` (job 121990578626): `files on the INERT list are actually read by tests: .claude/workflows/audit-plan.js — remove them from INERT in tests/closure.py, or except them`, then `AUTOFIX: skip-merge-failed`

The two messages do not agree on the remedy — `check --partial` asks for the path in
`inert_reads`, and the merge path (`_fold_inert_reads`) refuses that pair as a
contradiction — so the only consistent route is the one the tree's own comments describe
for this exact case: `INERT_EXCEPT` plus a recorded closure entry, which is how
`web-fix-wave.js` and `audit-find.js` are already classified. The PR added
`tools/audit/seat/plan_audit.py` to `tests/entities.py`'s `inert_reads` (correct for an
INERT file) and stopped there.

Carry: R10-FLOW-AUDIT-PLAN

### 5. The body's scoped-gate figure is stale and measured over the wrong range

Body: `python3 tests/closure.py select --diff 6fe5170cd7ce01e60ffebfc93e598c216e628fa3`
→ `MODE: SCOPED -- 2 script(s) run, 31 scoped out`.

Re-taken at this head (`evidence/select-figure.txt`):

```
  MODE: SCOPED -- 3 script(s) run, 30 scoped out.
```

and the changed-file list it prints contains `dev/programme/delivery/2834.md`, `2858.md`,
`2862.md`, `2864.md`, `2865.md`, `2866.md`, `2867.md`, `dev/programme/rosters/wave-r10-groups.json`
and `dev/programme/triage/s6-batch35.md`. None of those is in this PR: the three-dot name
list is nine files (`evidence/diff-three-dot.txt`). `6fe5170cd` is an ancestor of the
branch through the merged main, so the command diffs two dots' worth of main, not the
branch against its merge base — the range `CLAUDE.md` warns against, and the remedy is the
three-dot merge base `484d9902222031f8e081df9f53b52ffd50fcc0af`.

Carry: R10-FLOW-AUDIT-PLAN

## Non-findings — measured here, all holding

- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`, every metric at its budget
  (`evidence/instruments-green.txt`).
- `node tools/policy/brief_lint.mjs` → `rc=0`, `TOTAL: 0 error(s) across 48 file(s)`
  (`evidence/brief-lint.txt`).
- `node tools/policy/check-wave-script.mjs` → `224 passed, 0 failed` — matches the body;
  I counted the 15 `t(...)` calls inside the new P3 block and they are 15.
- `python3 tools/audit/seat/ref_privacy.py --check` → `0 refused` — matches the body.
- `python3 tools/audit/seat/selftest_wiring.py --check` → `98 self-testing, 98 wired,
  0 unwired` — matches the body.
- `git merge-tree --write-tree origin/main HEAD` → `rc=0`; no conflict, so nothing to
  classify by `claim-files.md` (`evidence/instruments-green.txt`).
- `tests/entities.py`'s py-spy stub fix works: CI `tests / fast (3.14)` prints
  `ALL 2463 ENTITY CHECKS PASSED`. I did not re-run `entities.py` myself (heavy; CI's
  lane is the authority).
- `brief-citations.md`: the linter needed no extension here. `brief_lint.mjs` does not
  read the plan, `PLAN.json` is new and machine-read by `plan_audit.py`, and the roster
  draft it writes keeps the existing `resume`/`brief` shape and is itself linted in the
  workflow (`writePlan.brief_lint_rc !== 0` throws).

## Not re-taken — say so rather than trust them

- `python3 tools/audit/archscore/score.py --diff 399098f63 57f0c9c77` — the body's
  `dS +74.6109 WORSENS` at `6:41.14`. Not re-run: six-plus minutes on a shared box, and
  no blocking finding turns on it.
- The body's null control (`plan_audit.py snapshot` twice, then `compare`) — not re-run;
  two multi-minute snapshots. The claimed `REGRESSED structure dead_methods: 0 -> 1` /
  `REGRESSED tripwire computed_attr_access: 31 -> 32` pair is unverified by me.
- The 25-mutation battery — not re-run in full. Its restoration baseline is the self-test
  that fails without a global git identity (finding 2), so it cannot be trusted as stated
  even if the battery reddens correctly here.

## Mutation proof and the finding's harness

This PR is a new-instrument change, not a fix for one verified finding, so the
class-enumeration obligation of `fix-review.md` step 6 does not apply and the body states
no seam. The committed harness is the deliverable itself (`plan_audit.py --self-test` and
the 15 P3 arms in `check-wave-script.mjs`), and the body discloses it. My measurements
above use those committed harnesses plus CI's own lanes, never a harness the fixer wrote
for this review — I wrote no harness.

Round 1 for this PR; no re-cut is owed yet.
