Fix review: blocked 811846b5419615864429a7908ad3910ce4bb24b9 root-cause-unanswered: fast (3.14) went red, unanswered

bus-nonce: e36d61e0f127aca914b360004c12de23

Round 1. Measured head 811846b5419615864429a7908ad3910ce4bb24b9 (live head at posting, re-read from the pulls API). Merge base ef3ca6571f5f6ef6b3cc0360b7ce4835f56eb702. The contract (`dev/governance/roles/`) shows no diff between the merge base and origin/main 0c25836e.

## Blocking

`blocked 811846b5419615864429a7908ad3910ce4bb24b9 root-cause-unanswered: fast (3.14) went red, unanswered`

- Check-run 113185847660, `fast (3.14)`, run 37739163225, on this head, ended `failure` at 06:47:47Z. The cause is `tests/harness_headers.py`. It is `run_always`, so the scoped gate ran it although `MODE: SCOPED -- 2 script(s) run` listed it as skipped. It printed `1 of 109 HARNESS HEADER CHECKS FAILED`, and the failing line is `FAIL depth seams: dev/audit/harnesses/git_auto_maintenance_race.sh:34: ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"`.
- This diff caused that red, and it is not a flake. `harness_headers.depth_root_seams()` returns `[]` at the merge base and returns that one seam at the head. I ran both locally, and `evidence/harness_headers-head.txt` shows the same FAIL. The new harness has to take the canonical `repo_root` walk (`tools/audit/repo_root.sh`, which inline_scan compares byte-for-byte) in place of the `../../..` depth root.
- The body's `## Red checks` section says "none. This head has no CI run yet." The head has a run, and it is red. The body therefore does not name the check or answer it. A cheaper detector already exists: `python3 tests/harness_headers.py` (about 105 s), or `tests/run.sh`, which runs every `run_always` script. The body ran `closure.py select` and named scripts only, and that selection does not include `run_always` scripts.

Not this PR's, and not blocking: `delivery-status` failed with `UNCHECKED — 72 rowed, 0 pending, 0 overdue`, which is not a required context. `budget-raise-gate` was `cancelled`; rerun its twin before merging, or the cancelled run blocks the merge.

## The claims under test: all four hold

(1) The cause. I verified it against git's own source at tag v2.55.0 (a clone of git/git), not against the fixer's summary.
- The 2.54.0 RelNotes line 58 reads: `"git maintenance" starts using the "geometric" strategy by default.`
- `builtin/gc.c` `initialize_task_config` uses `strategy = geometric_strategy` for unscheduled runs.
- `geometric_repack_auto_condition` uses `auto_value = 100` and then `too_many_loose_objects(100)`. That rounds the threshold to `DIV_ROUND_UP(100,256)*256 = 256`, and the condition is `loose_count > 256`.
- In `odb/source-loose.c` under `ODB_COUNT_OBJECTS_APPROXIMATE`, the loose count is the entries in `objects/17` times 256. So two objects in shard 17 trigger a repack.
- `printf '# Notes\n' | git hash-object --stdin` = `17e0f0dedfdc83c924c6399a21434fc8240f488c`, so the claim is confirmed.

I then built real git 2.55.0 from that tag, so these results use no model:

    RESULT realgit cfg=default  shard17 objs=2 -> maint_spawn=1 repack=1 packs=1   (repo with '# Notes\n' + 'x132\n', both 17xx blobs)
    RESULT realgit cfg=null     shard17 objs=1 -> maint_spawn=1 repack=0 packs=0   (null control: one object in 17, no repack)
    RESULT realgit cfg=off      shard17 objs=2 -> maint_spawn=0 repack=0 packs=0   (maintenance.auto=false via GIT_CONFIG_COUNT)

The stamp self-test under real git 2.55.0, with the repack forced on every commit through `GIT_CONFIG_PARAMETERS` `maintenance.geometric-repack.auto=-1`. That is the `-c` channel, separate from the `GIT_CONFIG_COUNT` channel the fix uses, so the head cannot simply overwrite the injection:

    RESULT tree=ef3ca657 arm=forced git=2.55.0 runs=20 directory_not_empty=6 nonzero_exit=6   (base: reproduces, 'OSError: [Errno 66] Directory not empty: .git')
    RESULT tree=811846b5 arm=forced git=2.55.0 runs=20 directory_not_empty=0 nonzero_exit=0   (head)
    RESULT tree=ef3ca657 arm=natural git=2.55.0 runs=300 directory_not_empty=0 nonzero_exit=0
    RESULT tree=811846b5 arm=natural git=2.55.0 runs=300 directory_not_empty=0 nonzero_exit=0

The natural arm, with nothing injected, did not reproduce on this Mac, even at base: 0/300. The body's 2/256 is the rate at which a repack is triggered, not the rate at which the run fails. Turning a trigger into an `ENOTEMPTY` also needs the repack to outlast the cleanup, and on a fast local disk it evidently usually does not. So the failure rate per CI run is not re-derived here. The mechanism is proven by the forced and deterministic rows; the frequency is not.

(2) The gate. `run-command.c` `prepare_auto_maintenance` at v2.55.0 reads `maintenance.auto`, falls back to `gc.auto > 0` when it is unset, and returns 0 before building the `maintenance run --auto` child when the setting is false. `run_auto_maintenance` is the path that commit and merge take. The env route is read as command-scope config whatever `GIT_CONFIG_NOSYSTEM` says (the real-git `cfg=off` row above). The other git temp dirs in `self_test()` (lines 929, 1370 and 1516) never run `git init` or commit, so the two patched sites are the whole of stamp's exposure.

(3) The shim model. I ran it myself:
- head: `shim 5` = 0/0, `plain 5` = 0/0;
- base (harness copied in, then removed): `shim 5` = `directory_not_empty=5 nonzero_exit=5`, `plain 5` = 0/0;
- `spawn` under git 2.38.1 and under real git 2.55.0: `default maintenance_spawns=1`, `off maintenance_spawns=0`.

The model's gate is faithful to `prepare_auto_maintenance`. The model is stronger than reality in two ways: it fires on every commit or merge, with no shard-17 condition, and it writes for 4 s. So it is fair as a test of the gate. It is not a rate. The real-git arm above replaces it as the measurement.

Mutation proof: I deleted the three `GIT_CONFIG_*` keys at the head. The self-test then printed `FAIL throwaway repo: git itself reads auto-maintenance as off ...` and `RESULT stamp_self_test=fail`. Real git 2.55.0 forced gave `directory_not_empty=4 nonzero_exit=20`. After restoring, the tree was clean and the self-test printed `RESULT stamp_self_test=pass`.

(4) Stamp semantics. The diff touches only `_throwaway_git_env()`, its two call sites inside `self_test()`, and one new `check()`. Nothing outside `self_test()` calls the helper. `VERSION`, the manifest and the notes heading are untouched.

## Not blocking, but owed in the RCA

- RCA section 4's alternative "`gc.auto=0` alone does not close the race" is false as written. When `maintenance.auto` is unset, as it is in these repositories, `prepare_auto_maintenance` uses `gc.auto > 0` as the gate. Real git 2.55.0 with `gc.auto=0` gave `maint_spawn=0 packs=0` with two objects in shard 17 (`evidence/realgit/gcauto0.txt`). `maintenance.auto=false` is still the better key, because it is the primary gate. The sentence needs correcting.
- Body figures: the per-run 2/256 for the undo repository is consistent with the mechanism, but I did not re-derive it as a rate. The CI sighting (check-run 113149021777) I did not re-read. The census figure `37` I did not re-run.

## The workflow-level env, an owner decision (not blocking)

If the cause is true, and it is, every throwaway repository that commits or merges and then removes its directory is exposed on git ≥ 2.54. The rate depends on its shard-17 collisions. A workflow env covers CI only: a seat whose git is ≥ 2.54 (Homebrew stable is 2.56.0) stays exposed locally. So the env is a cheap CI barrier, not the complete answer. A per-site helper, or a shared test helper, is the full closure. The cause makes a barrier for the other 34 sites warranted. It does not make the workflow form specifically necessary.

## Reviewer's instruments (disclosed as mine)

`evidence/realgit_race.sh` uses a real git 2.55.0 that I built from git/git v2.55.0 into the review scratch directory. The real-git control and mutation transcripts are under `evidence/`.
