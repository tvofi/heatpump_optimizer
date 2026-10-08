# R9-RCA-stamp-race: the stamp self-test's throwaway repository loses a race with git's detached repack

Root-cause and fixer seat `r9-rca-stamp-race`, 2026-10-08, branched at origin/main `6b91e238`.
The seat ran under `dev/governance/roles/root-cause.md` and `dev/governance/rules/defect-root-cause.md`.

**Trigger:** the second one in `defect-root-cause.md`. An intermittent red check that no diff
caused. `tests/entities.py` runs the check "tools/release/stamp.py's --self-test passes", and
that check failed with `OSError: [Errno 39] Directory not empty: '/tmp/tmp…/.git/objects/pack'`.
There are two sightings:

- the R9-CI-1 proof #2048 (run 37711053129). The orchestrator reported this one; the seat did
  not re-read its log;
- #2049's `fast (3.14)` check-run 113149021777 (run 37727537796, attempt 1). Its log line
  7847 reads `FAIL tools/release/stamp.py's --self-test passes [... OSError: [Errno 39]
  Directory not empty: '/tmp/tmp3ta3eh7p/.git/objects/pack']`.

Both runners print `git version 2.55.0`.

## 1. Named cause

`stamp.py --self-test` builds two real throwaway repositories under
`tempfile.TemporaryDirectory`: the record-class repository and the undo repository. Git ≥ 2.54
starts auto-maintenance after every `commit` and `merge`. The auto-maintenance runs **detached**
(`maintenance.autoDetach`, true by default since 2.47) and uses the **geometric** strategy
(git 2.54 release notes: "`git maintenance` starts using the `geometric` strategy by default").
The geometric repack's `--auto` condition (`builtin/gc.c` `geometric_repack_auto_condition`, at
v2.55.0) calls `too_many_loose_objects(100)`. That function rounds the threshold up to 256 and
estimates the loose-object count as **the number of loose objects in `objects/17`, times 256**
(`odb/source-loose.c`, `ODB_COUNT_OBJECTS_APPROXIMATE`). So a repository of any size repacks as
soon as two of its loose objects share the `17` shard. The repack is a detached child that writes
into `.git/objects/pack`. `TemporaryDirectory.cleanup()` runs while that child is still writing,
and `rmtree` fails with `ENOTEMPTY`.

**Why this site.** The undo repository commits the blob `# Notes\n`, whose id is `17e0f0de…`.
That id is fixed by content, so `objects/17` already holds one object. Each of the repository's
two commits has an id that depends on the commit time, and lands in `17` with probability 1/256.
That gives about **2/256 ≈ 0.8 % per self-test run** that a repack is spawned. The second commit
is followed only by `tag -d`, `reset --hard` and `status`, all of them milliseconds, and then the
cleanup. The record-class repository has no deterministic object in `17` (its 11 blob and tree
ids are listed in the reproduction). It needs two of its 7 commits to land there, about
C(7,2)/65536 ≈ 0.03 % per run.

**Which side moved.** Neither `stamp.py` nor the check moved; the runner's git did. Before 2.54,
auto-maintenance ran only the `gc` task, gated on `gc.auto = 6700`. That threshold rounds to 6912
and so needs 27 loose objects in `objects/17`. A throwaway repository of a few dozen objects never
reaches it.

## 2. Process state: (d)

The process is the suite's convention for throwaway repositories: a pinned identity,
`GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`. It was sound against every git this
repository had run. Its unstated precondition was that a tiny repository never triggers
background maintenance. The runner image's git upgrade (to ≥ 2.54; 2.55.0 at both sightings)
removed that precondition. The convention was neither absent (a) nor disobeyed (b), and it
produced its intended result until the precondition changed (not c).

## 3. Reproduction

The seat's git is 2.38.1, which never reaches the condition above on its own. Colima has been
removed, so no Linux container was available either. The perturbation is therefore a
**model**: `dev/audit/harnesses/git_auto_maintenance_race.sh`. Its shim runs the real git, and
after `commit` or `merge` applies git 2.55's own gate (`run-command.c`
`prepare_auto_maintenance`: `maintenance.auto`, falling back to `gc.auto > 0`). It reads that
gate through the real `git config`, and when the gate is open it forks a detached writer into
`objects/pack`. A separate arm uses no model at all: it asks the real git, through `GIT_TRACE`,
whether a commit spawns `git maintenance run --auto`.

| arm | tree | result |
|---|---|---|
| `5 shim` | base `6b91e238` | `directory_not_empty=5 nonzero_exit=5` (`OSError: [Errno 66] Directory not empty: 'pack'`) |
| `5 plain` (null control) | base `6b91e238` | `directory_not_empty=0 nonzero_exit=0` |
| `5 shim` | fix `c0664ae6` | `directory_not_empty=0 nonzero_exit=0` |
| `5 plain` | fix `c0664ae6` | `directory_not_empty=0 nonzero_exit=0` |
| `3 shim`, the three `GIT_CONFIG_*` keys deleted (mutant) | fix less its line | `directory_not_empty=3 nonzero_exit=3` |
| `0 spawn` (real git 2.38.1) | n/a | `config=default maintenance_spawns=1`, `config=off maintenance_spawns=0` |

## 4. The fix

The two throwaway repositories had duplicated environment blocks. Both now take one helper,
`_throwaway_git_env()`, which adds `maintenance.auto=false` through
`GIT_CONFIG_COUNT`/`KEY_0`/`VALUE_0`. That is the gate git consults before it spawns
auto-maintenance at all, so no repack starts. Every child git inherits the value, and it
survives `GIT_CONFIG_NOSYSTEM`. A new self-test check reads `maintenance.auto` back through the
real `git config` inside the repository. The mutant above turns that check `FAIL`.

The stamp's semantics do not change: the helper is reached only from `self_test()`.

Alternatives considered:

- `TemporaryDirectory(ignore_cleanup_errors=True)` silences the symptom and leaves a detached
  repack writing into a deleted tree.
- Waiting for the child is not possible: it is daemonised, so the self-test holds no handle on
  it.
- `gc.auto=0` alone does not close the race. In 2.55 it is consulted only when
  `maintenance.auto` is unset, and the geometric task does not read it.

## 5. How far the class reaches

The rule that enumerates the class's seams:
`git grep -n -E '"git", "init"|git init|"init", "-q"' -- tests tools .claude .github`. At
`6b91e238` it returns 37 lines: one comment (`.claude/hooks/stop-selfcheck.sh:152`), stamp's
two sites and 34 other `git init` sites. Every site that then commits or merges
and removes the directory is exposed on git ≥ 2.54. How exposed each one is depends on whether
it commits a fixed-content object in the `17` shard; the seat measured that only for stamp's
two repositories. Disposition: stamp's two are closed in this diff. The other 34 are not closed
here, and the barrier below is proposed for them.

## 6. Cost test

- **cost(defect):** one red required check that no diff caused, plus a rerun of `fast` (about
  36 min of wall-clock: run 37727537796's `fast (3.14)` ran from 04:27Z to 05:03Z), plus the
  seat triage that attributes the red. A real stamp runs the same self-check and would refuse
  on it.
- **P(recurrence):** measured at 2 sightings in about 4 h on 2026-10-08, from one site. The
  per-run estimate for the stamp site is 2/256, from the mechanism in section 1.
- **cost(countermeasure, recurring):** the in-module fix adds about 0 s per run: three
  environment keys, plus one `git config` call of a few milliseconds.

Verdict: build. It is built in this diff for the sighted site.

The class barrier passes the same test, at a standing cost of about 0 s. It is one job-level
or workflow-level `env:` in `.github/workflows/tests.yml` and `governance.yml`
(`GIT_CONFIG_COUNT=1`, `GIT_CONFIG_KEY_0=maintenance.auto`, `GIT_CONFIG_VALUE_0=false`). That
covers every throwaway repository in CI whose environment inherits `os.environ`. It is a
code-owned workflow edit with its own `entities.py` pins, so it is owed as the next pull request
and is not folded into this one. The orchestrator holds that decision.
