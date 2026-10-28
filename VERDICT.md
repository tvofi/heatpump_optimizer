Fix review: blocked 71987ff1ee4f3f411c772681d3bcb32490832c53 root-cause-detectable: tests/closures -- red at this head (INERT READS UNDER-APPROXIMATED: tests/entities.py opens dev/programme/rosters/critical-path.json and wave-r9-groups.json), closures-autofix skip-manual-repair-owed, and ## Red checks names neither it nor the red tests / nightly-status, which pr-contract refuses because the diff touches governance.yml
bus-nonce: 773253debde59287022b258898625ee3

# Fix review -- PR #2883, R10-FLOW-BOARD, round 3

Third fix review. Reviewed head: 71987ff1ee4f3f411c772681d3bcb32490832c53, in a detached worktree at
that head (`ev/head.txt`), and still the head when I posted this. The baseline is the round-2 blocked
head `3bd284f74`, in its own detached worktree. `dev/governance/roles/` has no diff between the merge
base and origin/main.

The fix since round 2 is `70928ca4e` (`merge_throughput.py` and `roster_lib.py`). The other commits
in the range are main merges. `git merge-tree --write-tree origin/main <head>` exits 0
(`ev/merge-tree.txt`).

**The round-2 block is answered on the code.** This verdict blocks only on the check state at the
new head.

## Harnesses

The finder's harness is round 2's: `class_open.py`, `class_open2.py` and `class_open_control.py`,
taken from `verdict/2883` at `2678416c5`. I retargeted only the `WT` pin and changed nothing else.
I ran it myself at both ends (`ev/harness_both_ends.txt`).

Reviewer-built and disclosed as mine: `harness/mutants_r3.py` and `harness/lead_unreadable.py`.

## Results

- `flow_closed.state()` on an unreadable roster blob:
  - At `3bd284f74`: `closed_for_unreadable_object = (0, '')` and `is_zero_without_reason = True`.
  - At this head: `(None, 'cannot read dev/programme/rosters/wave-r1-groups.json at 6782967ae4aa:
    fatal: bad object ...')` and `False`.
- `critical_path_read()` on an unreadable critical-path blob:
  - At `3bd284f74`: `(set(), '')`, and `wip_lanes = {'A': 0, 'B': 1, 'C': 0, 'F': 0}`.
  - At this head: `(None, 'cannot read ...')` and `wip_lanes = None`.
- Null control at both ends: `control_closed_intact_blob = (1, '')` and
  `control_critical_intact = ({'r1-a'}, '')`.
- The fixer's departure from the round-2 brief is sound. It uses `roster_lib.blob_at` via
  `git ls-tree -z --full-tree` at all three sites (`state()`, `critical_path_read()` and the
  `roster_path()` override), instead of the brief's `rev-parse --verify --quiet`. The rev-parse
  swap, run as mutant M5, answers `(False, '')` for an unreadable tree on the way to the path, and
  it reads a directory as a file.
- Mutants, my own driver (`ev/mutants.txt`). Each replacement matched exactly once, both
  `--self-test`s ran, and the file was restored. **7 of 7 killed:** M0 `cat-file -e` 10 FAIL lines,
  M1 rc check off 3, M2 the `critical_path_read` guard 1, M3 the `state()` guard 1 plus its
  self-test FAILED line, M4 `why` dropped 1, M5 the rev-parse swap 4, M6 kind always blob 1.
  `git status --porcelain` is empty afterwards.
- Unmutated self-tests: `ok: merge_throughput.py self-test` and
  `roster_lib self-test: 51 checks, 0 failed` (`ev/selftests.txt`).
- Class open: no `cat-file -e` or `rev-parse --verify ... :<path>` probe remains in the diff's
  Python files; the only hits are comments. `_lead_hours` with an unreadable branch commit returns
  `None`, not a number, and its intact control returns `6.0` (`ev/lead_unreadable.txt`).
- `carry_audit` at the head reports 4 items, all routed. The three-dot diff touches no claim file,
  no `VERSION`, no manifest and no `RELEASE_NOTES.md`.

## Block

All of this head's workflows had concluded by 03:29Z (`ev/check-runs.txt`: 32 success, 16 skipped,
7 failure).

- **`tests / closures` is red at this head.** Check-run 122599859589 ran with `SCOPE_CASE: full`
  and concluded at 03:20:16Z (`ev/closures.log`) with
  `INERT READS UNDER-APPROXIMATED: ... tests/entities.py: dev/programme/rosters/critical-path.json`
  and `tests/entities.py: dev/programme/rosters/wave-r9-groups.json`.
  - `tests / closures-autofix` (122611263783) printed `skip-manual-repair-owed -- THE REPAIR DID
    NOT HAPPEN`, so no bot commit is coming.
  - The reads are new at this head. `tests / closures` was green at the round-2 head `3bd284f74`
    (job 122482244383, per round 2), at main `6e5995e51` (122584782151) and at main `b9e286254`
    (122590255408). `tests/closures.json`, `tests/closure.py` and `state_docs.py` are unchanged
    between `3bd284f74` and this head. That puts the change in `70928ca4e` or its merge with main.
    I did not establish which line opens the two files.
  - The cheaper detector is the one the body itself names for the round-1 red:
    `./tests/derive_closures.sh --single tests/entities.py` plus
    `python3 tests/closure.py check --in-dir <dir> --partial`, at a standing cost of 1280 s.
  - `## Red checks` describes only `8f05b74d` and `3bd284f7`.
- **`tests / nightly-status` is red** (122599133664,
  `NIGHTLY FAILED: record-autofix failed in the last verification dispatch`). The body does not
  name it. `pr-contract` refuses on it twice, in runs 122611481226 and 122613316471. Both started
  after the last red concluded, the second at 03:26:53Z. The refusal reads: "It grades `main`, but
  this diff touches what it reads (.github/workflows/governance.yml)". The diff does touch
  `.github/workflows/governance.yml`. So this is the body's to answer, either with the main-side
  cause and its owner or with the lane's fix. The exemption in `fix-review.md` step 11 does not
  apply.
- `gate` is red (122612066136 and 122613516759) on
  `FAIL tests / closures: failure (run 40622272637)` and
  `pr-contract / pr-contract: failure (this run)`, the two reds above.

Repair:
1. Re-derive `tests/entities.py`'s closure at this head, or remove the new working-tree reads.
2. Answer both reds under `## Red checks`, including the cheaper detector for `tests / closures`.
3. Re-take the head. The code findings above carry to the new head only if `70928ca4e`'s two
   files are unchanged.

## Findings

- F1 (blocking, root-cause-detectable): the `tests / closures` red above. Carry: dismissed:
  blocking; this PR's next round owes the repair
- F2 (blocking, the same trigger): the `tests / nightly-status` red, unanswered while `pr-contract`
  refuses. Carry: dismissed: blocking; this PR's next round owes the answer
- F3 (non-blocking): the round-2 note about `roster_lib.py:177` is repaired. Under the override, an
  unreadable tree now refuses with git's reason, and M4 kills that arm. Carry: dismissed: verified
  repaired
