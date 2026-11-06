R10-HOTFIX-STAMP-BASE (lane C, fix, size S), repair round 2. v7.1.2 was tagged by hand at b8e823699, on a tree whose VERSION, manifest version and notes still read 7.1.1. `tools/release/stamp.py` bumped from VERSION alone, so it proposed v7.1.2 again, and rule 3 refuses that as an existing tag. Rules "flush", 4 and 5 (`window_log_args`, `rule4_problem`, `disposition_gate`) also took their window from the newest v* tag, and no stamp had made that tag. v7.1.2 is kept. Nothing is deleted or retagged.

What changes:

- `stamp.py` gets two pure functions. `bump_base(current, tags)` returns the higher of VERSION and the highest `TAG_RE` tag. `last_stamped_tag(tags, version_at)` returns the newest release tag whose own tree's VERSION equals its name. The VERSION lookup is passed in, so the self-test needs no git. `tag_version` reads `git show <tag>:VERSION` through the module's `sh` seam. After Rule 1's `fetch --tags`, the Rule 3 block computes `base = bump_base(current, tags + remote)` and then `nxt = next_version(base, ...)`. `last_tag = last_stamped_tag(tags, tag_version)` feeds flush, rule 4 and rule 5. Rule 3's exists refusal and above-every-tag refusal stay as the backstop.
- `release.yml` gets a new step, `Refuse a tag whose tree does not carry its version`, which runs before `Create the GitHub release`. It refuses unless VERSION is the tag, the manifest version is the tag and RELEASE_NOTES.md has an exact `## $TAG` line, and it prints every problem it finds. The publish step reads the asset back `attempts=5` times, with a `sleep 10` between reads and none after the last, then fails. `RELEASE_READBACK_ATTEMPTS` names that bound in stamp.py, and the self-test pins the two to agree.
- The self-test cuts each step's own `run: |` block out of release.yml with `release_step_script`. It never runs a copy of the step's logic.

Round 2 builds the review's three findings at 66577738. None is carried.

1. The previous body's `## Head` figure was false. This body is re-taken whole from the template, and every figure below was re-derived at the final head by the command shown with it (see `## Head` for the corrected claim).
2. The pin `flush: main runs it after rule 3 and before rule 4` searched `main()` for `last_tag = "v"`, which this diff removed. `find` returned -1, so the after-rule-3 half held for any order. The pin is now anchored on `last_tag = last_stamped_tag(tags, tag_version)` and starts its chain with `-1 <`, so a missing anchor fails it.
3. The self-test ran the release.yml steps with no bound, so an endless read-back hung it instead of failing it. Both step seams now go through one runner, `_run_step`. It starts `bash -e -c <step>` in its own session, waits up to `RELEASE_STEP_TIMEOUT_S` (10 s) and kills the whole process group at that bound, returning `None`, which every caller's `== 0` / `== 1` check reads as FAIL. Two smaller fixes go with it: the publish stub's read count tolerates an empty file (`-1`), and the tree step uses the same runner (one more seam found by the census in Figures).

Alternatives considered for (3), and why each lost: (a) `subprocess.run(..., timeout=)`, which this branch took first (cb0909079). The kill reaches only bash, so the stub `gh` it started kept writing in the temporary directory. In 10 runs of the unbounded mutant at 60fb6879, 2 crashed with `ValueError: invalid literal for int() with base 10: ''`. With the read made tolerant, 1 run in 10 still crashed with `OSError: [Errno 39] Directory not empty` while the directory was being removed. Killing the process group removes the cause, and 20 runs out of 20 then fail cleanly (Figures). (b) `TemporaryDirectory(ignore_cleanup_errors=True)` hides the symptom and leaves a live stub behind. (c) Bounding only by the CI job's timeout is what the review found: a hang, not a FAIL. Alternatives for the base fix: (a) reading the base from the tag list alone, ignoring VERSION, loses the case where VERSION is ahead of every tag (a first stamp after a manual VERSION fix). (b) Hand tags listed by name would be a spelling list the next hand tag defeats. (c) Deleting or retagging v7.1.2 is excluded by the brief.

## Head

0375c5019442ab96646462a2fb17e4129418c791: the round-2 commits cb0909079, 60fb6879e and 68d9a47ba on top of PR head ee63326c8, merged with origin/main twice because main moved during this round. The first merge (67d943bc3) was at 9315526f8, read 2026-11-06 07:15 UTC. The second (0375c5019) was at dc0a170b671814be196a54b1c71e29449f54d6d7, read 08:49 UTC. The merge base is dc0a170b6. The second merge brought in only `dev/programme/delivery/3237.md` and `dev/programme/triage/s6-batch125.md`, and `git diff --stat 9315526f8 dc0a170b6 -- <the four paths below>` prints nothing. Every figure below was re-taken at 0375c5019 after that merge, and each matched its value at 67d943bc3.

The corrected claim, as measured: main's delta touches tests/closures.json and tests/entities.py, and never stamp.py or release.yml.
- `git diff --stat c679f4b69 dc0a170b6 -- tools/release/stamp.py .github/workflows/release.yml tests/entities.py tests/closures.json` prints `tests/closures.json | 30 ++++++++++++++++++++++++++++--` and `tests/entities.py | 2 +-`.
- `git diff --stat 8a39977cb dc0a170b6 -- <same four paths>` prints `tests/closures.json | 4 ++++` and `tests/entities.py | 2 +-`.
- `git diff --stat b88684a21 dc0a170b6 -- <same four paths>` prints nothing. The first merge (to 9315526f8) brought in only `dev/programme/delivery/3212.md` and `dev/programme/triage/s6-batch122.md`.

Every check in this body was run at 0375c5019.

## Mutation proof

Round-2 driver: `python3 $S/mutants_r2.py` (sha1 42b24e73640dd6c8fbaeb4979b3156e7ffc76e5c; `$S` is the seat's scratch directory, not in the tree). It edits each mutant into the tree, runs `python3 -I tools/release/stamp.py --self-test`, kills the run's process group at 120 s, prints the FAIL lines and restores the file. At 0375c5019:

- The flush call moved above the `last_stamped_tag` anchor: exit 1; FAIL flush: main runs it after rule 3 and before rule 4, and a dry run's deferral reaches rule 5 only as that deferral.
- The anchor line replaced by the old newest-tag form (`find` returns -1): exit 1; FAIL flush: main runs it after rule 3 and before rule 4, ... and FAIL last stamp: main() anchors rules flush, 4 and 5 on the last stamped tag.
- release.yml read-back unbounded (`for attempt in $(seq ...)` turned into `while attempt=$((attempt+1))`): exit 1 in 10.5 s; FAIL release publish: an asset never read back fails after 5 reads, unpublished.
- release.yml tree step never ends (`while :; do :; done;` prepended): exit 1 in 40.4 s; the four FAIL release tree lines (4 x 10 s bounds).
- Deleting the fix's line under each unbounded mutant (`return proc.wait(timeout=RELEASE_STEP_TIMEOUT_S)` to `return proc.wait()`): `HUNG(driver killed the process group at 120 s)` for both the read-back and the tree step, which is the review's finding reproduced.

Failing first, for (2): the same flush-above-anchor mutant at the previous head ee63326c8 (`cd $S/wt_pre && python3 $S/mutants_r2.py NULL "flush call moved"`) exits 0 with 0 FAIL. The old pin let it through.

The round-1 mutants, re-run at the final head with the reviewer's own driver (`git show origin/probe/rev-3236-179d029f:ev/mutants.py > $S/rev/mutants.py; python3 $S/rev/mutants.py`, sha1 c3522e2df95b73915bc25201c4aeabbf31ab42c1): 14 mutants, 14 KILLED, 0 SURVIVED. `MUTANT release.yml: unbounded readback (while true): exit 1, 1 FAIL KILLED` is the one that hung in the review. The rest are the review's list (bump_base x2, last_stamped_tag x2, main() x3, tree step x4, read-back attempts=1, read-back exit 0), each killed with the FAIL line the review recorded, except `main(): last_tag = newest tag`, which now also fails the re-anchored flush pin (2 FAIL).

## Null control

- Unmutated, and restored after every mutant, in both drivers: `RESULT stamp_self_test=pass`, exit 0, 0 FAIL, 0.5 s.
- Anchor census at the previous head ee63326c8 (`cd $S/wt_pre && python3 -I $S/anchor_census.py`): `MISSING stamp.py:1929 _main_src.find("last_tag = \"v\"") -> -1`, `anchors 23, missing 1`. At 0375c5019: `anchors 23, missing 0`.
- Process-group kill: `python3 $S/race.py 10` (sha1 19799ca4693e60f7361a4ac48b6a7c442dc29a26) runs the unbounded read-back mutant N times and counts clean FAILs against crashes. At 60fb6879e (timeout= only, no group kill): `N=10 clean_fail=8 crash=2` (`ValueError ... ''`). At 0375c5019 with `python3 $S/race.py 20`: `N=20 clean_fail=20 crash=0 other=0`.
- The bound against the shipped step's real runtime: `python3 $S/time_publish.py` (sha1 3c35110dc57aef45a58ae68b14e499da16b8965c) runs the shipped publish step 20 times per arm against the stub gh. Never read back: rc 1, 5 reads, max 0.072 s. Read back on the first read: rc 0, 1 read, max 0.014 s. On the third: rc 0, 3 reads, max 0.030 s. A 10 s bound sits over 100 times above the slowest measured run and still fails the endless mutant in 10.5 s.

## Figures

- Stamp self-test at 0375c5019: `python3 -I tools/release/stamp.py --self-test` prints `RESULT stamp_self_test=pass`.
- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 3 script(s) run, 30 scoped out.`, and `scope.run` names tests/doc_claims.py, tests/entities.py and tests/harness_headers.py. Each was run with `PYTHONPATH=tests/hastub python3 tests/<name>.py`, together with run_always and the ratchet. All exited 0:
  - doc_claims: `ALL 296 checks PASSED`
  - entities: `ALL 2632 ENTITY CHECKS PASSED`
  - harness_headers: `ALL 112 HARNESS HEADER CHECKS PASSED`
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`
  - `python3 tests/layout.py`: `layout self-test: ok`
  - `python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)`: `claims hygiene: dc0a170b671814be196a54b1c71e29449f54d6d7 ok`
  - `python3 tests/closure.py selftest`: `ALL 118 closure shrink pins PASSED`
- Architecture score: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` prints `Architecture score: dS +0.0000 NULL`.
- Scope: `git diff --stat $(git merge-base origin/main HEAD)...HEAD` touches only `.github/workflows/release.yml`, `dev/programme/delivery/3236.md` and `tools/release/stamp.py`. This passes, so those files are byte-identical to the merge base: `git diff --quiet $(git merge-base origin/main HEAD)...HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt tests/closures.json && echo byte-identical`. No `*budgets*.json` is in the diff.
- Real tags, through the reviewer's driver: `git show origin/probe/rev-3236-179d029f:ev/real_tags.py > $S/rev/real_tags.py; python3 -I $S/rev/real_tags.py` (sha1 d02a136f94ced6844cbc0aa59d38a7b96de98456). Rule: every local tag matching `TAG_RE`. Result: VERSION 7.1.3, 156 tags, `bump_base` 7.1.3, next 7.1.4, `last_stamped_tag` v7.1.3. Tags whose tree VERSION is not their name: v3.1.0, v3.1.1, v3.1.2, v3.2.0 and v7.1.2. Main now carries the v7.1.3 stamp, so at this tree the old rule (VERSION, then newest tag) gives the same 7.1.4 and v7.1.3. The two rules split only on the hand-tag case, and the self-test's v7.1.2 arms pin that case.
- Release tree step on real tags: `python3 $S/rev/tree_step.py`. This is the reviewer's ev/tree_step.py, which takes the step text through PyYAML, with v7.1.3 added to its tag list (sha1 e23452200f23053f2a6840690637a3afaab85814). Step order: tree 3, create 7. v7.1.0, v7.1.1 and v7.1.3 exit 0. v7.1.2 exits 1 with `VERSION reads 7.1.1`, `the manifest version reads 7.1.1` and `RELEASE_NOTES.md has no '## v7.1.2' section`. The real publish step, with a stub gh that never reads back: exit 1, 5 reads, sleeps `10 10 10 10`, not published.
- Census for (2), pins that read a source position. `python3 -I $S/anchor_census.py` (sha1 6a968af45d89cea084943b2dc955d4d9aa8d1af5) evaluates every literal matched by `(_main_src|_push_src|_r4_src)\.(find|index|rindex)\("…"\)` in stamp.py against the slice it searches. At 0375c5019: 23 anchors, 0 missing. At ee63326c8: 1 missing, the flush pin's, which is closed here. Every `.find` ordering chain (stamp.py around the `git tag` publish pin, both `dry_run` pins, the flush pin and the bump-base pin) now starts with `-1 <`, and `.index`/`.rindex` raise on a miss. This instrument covers stamp.py only.
- Census for (3), self-test seams that run release.yml step text. `grep -nE 'release_step_script\(|subprocess\.(run|Popen)\(\["bash"' tools/release/stamp.py` returns the definition (stamp.py `def release_step_script`) and one call, inside `_run_step`. At ee63326c8 the same rule returns two unbounded `subprocess.run` calls, `_tree_check` and `_publish_step`. Both are closed here.

## Red checks

none. 0375c5019 is no pull request's head yet, and `list_workflow_runs` for branch `handoff-wip/r10-hotfix-stamp-base` returns `total_count: 0`, so no check run has concluded on it. On PR head ee63326c8, `get_check_runs` for #3236 (55 runs, one page of 100) shows none concluded other than success or skipped. `tests / closures` was success there, and it recorded the same two closures this diff reaches.

`tools/pr/prepr.sh` at 67d943bc3 (against origin/main 9315526f8), and again at 0375c5019 (against dc0a170b6), gives rc=1 on one step, `closures` (step 6b's local recording). Every other step is ok or skip: no version edit, claim files, claims hygiene, `ci predict` (`no closures, fast, governance or instrument red predicted`), merged structure, layout guard, throwaway git and claims register. The refusal is `INERT READS UNDER-APPROXIMATED` for tests/entities.py, and it is inherited, not this diff's:
- Null control: the same recording at origin/main 9315526f8, in a detached worktree (`./tests/derive_closures.sh --scripts-from <entities.py> --record-only --out-dir $D; PYTHONPATH=tests/hastub python3 tests/closure.py check --in-dir $D --partial`), refuses the same way, with 3856 unlisted INERT reads. The head's recording has 3762.
- The two sets differ by 301 head-only and 395 main-only paths (`comm` of the sorted lines). Every head-only path exists in main's tree (`git cat-file -e 9315526f8:<path>`). None is a file this diff touches (`grep -cE 'tools/release/stamp.py|workflows/release.yml|delivery/3236.md'` gives 0). The local recorder varies between runs and disagrees with CI's committed recording (59 entries for entities.py).
- I did not commit a local re-derive. It would replace CI's Linux recording with a recording that varies between runs, put a gate file into the diff (MODE: FULL), and duplicate `closures-autofix` (ci-autofix.md). CI's required `tests / closures` records these scripts at the PR head.

## Forward-carry

none

## Friction

none
