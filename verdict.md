Fix review: merge 411270a40b14a235482fa37c2af55132cfc74760

bus-nonce: 05477ad9f26176951efce2a566b7d405

Round 2. I worked from detached worktrees at head `411270a40b14a235482fa37c2af55132cfc74760` and at origin/main `dc0a170b671814be196a54b1c71e29449f54d6d7`, which is also the merge base. The role files have not drifted between the merge base and main: `git diff <mb>...origin/main -- dev/governance/roles/` is empty. Round 1 blocked at 3cbcbd5d as mutation-vacuous because M3 and M4 survived. Both are now killed by new acceptance cases, and the new rmtree branch is pinned by its own case.

## Findings

- Residual: the rename -> link-back gap in `_steal` (round-1 plant W3) is still open, as the body states under Forward-carry. A valid owner C replaces a broken slot after the read, and a fourth taker D creates the slot inside the gap. D keeps the slot, and C loses it silently while still believing it holds slot 0. I re-ran my W3 plant at the head: `slot_owner=D`, `C kept: False` (ev/windows.txt). The new case `broken_rename_gap` pins the bound: one owner and no stale grave. The same gap was already in main's orphaned-owner `_steal(path, owner)` path from #2267, so this PR does not open it. Reaching it needs a hand-made or corrupt slot file plus two takers within microseconds. Carry: dismissed: no atomic compare-and-remove exists on POSIX; bound pinned by broken_rename_gap in tests/gate_lock.py
- Residual: a symlink at the slot path that points to a directory gets reclaimed, and the target is untouched (`target_intact=True`). But `grave.is_dir()` follows the link, `shutil.rmtree` refuses a symlink, and `ignore_errors=True` swallows that refusal, so one `stale-*` symlink is left in the pool dir (ev/dirprobe.txt D3). This leaks one dirent per hand-made symlink and loses no data. Main looped forever on the same input (`create=False`). Carry: dismissed: only a hand-made symlink reaches it; harmless leak, no data loss; noted for the next touch of _steal
- Follow-up: the M2-shaped mutant (restore the `is_file` second read, still reaping via `_steal(path, None)`) is killed by only one case, `directory_slot`, because `is_file` is False for a directory. `delayed_read` passes under it, since the put-back in `_steal` saves the rival. I agree with round 1 and the body that this mutant is behaviourally near-equivalent for files. Carry: dismissed: near-equivalent; put-back keeps the rival's owner and the create arbitrates

## Evidence

- Acceptance at head: `PYTHONPATH=tests/hastub python3 tests/gate_lock.py --accept` -> `ALL 46 gate lock acceptance checks PASSED` (ev/accept-head.txt). The body's figure of 46 is re-derived.
- (a) Mutants, re-derived with my own edits to `tests/gate_lock.py`, each restored afterwards (ev/accept-*.txt):
  - M3, `_steal(path, None)` reverted to `path.unlink(missing_ok=True)`: `3 of 46 FAILED`. The failing cases are `a valid owner landing after the broken read survives the reap` (`kept=None`), `a rival in the reap's rename gap leaves one owner and no grave` (`owner=None`), and `a directory at the slot path is reclaimed, not raised` (`IsADirectoryError`).
  - M4, the `_steal(path, None)` line deleted: `3 of 46 FAILED`. The failing cases are `a garbage slot is reaped and a following create wins` (`reaped=False create_won=False`), the rename-gap case (`owner=C`), and the directory case.
  - M6, rmtree branch disabled (`if False and grave.is_dir()`): `1 of 46 FAILED`, the directory case (`IsADirectoryError`).
  - M7, put-back `os.link` removed: `1 of 46 FAILED`, `broken_put_back` (`kept=None`).
  - M1c, merge base's `_read_at`/`is_file`/unlink form restored: `4 of 46 FAILED` (`delayed_read`, put-back, rename gap, directory).
  - M1b, `_read_at` plus `is_file` plus `_steal`: `1 of 46 FAILED` (directory). See the Follow-up above.
  - Every row matches the body's Mutation proof table.
- W2 and broken-reclaim plants, my own and carried over from round 1 (`windows.py`, deterministic hooks, ev/windows.txt):
  - broken-reclaimed: free=0 and `then create wins: True` at both head and main.
  - W2: head `C kept: True`, main `C kept: False`.
  - W3: head D keeps the slot. This is the residual above.
  - W5: harmless at both ends.
- (b) Directory probe (my own `dirprobe.py`, ev/dirprobe.txt). Head against main:
  - D1, empty dir: head free=0, create=True. Main create=False, a take_slot livelock.
  - D2, non-empty hand-made dir: head reclaimed and contents removed. That is intended: any directory at a slot path is broken state, and no in-tree writer makes one.
  - D3, symlink to an outside dir: target intact, one leaked symlink grave. This is the residual above.
  - D4, the dir replaced by valid owner C between the read and the reap: C kept and no grave, so the put-back covers the rmtree branch too.
  - D5, orphaned-owner file steal: unchanged.
  - The grave path is private (`stale-<pid>-<monotonic_ns>`), so no other writer can swap it between `rename` and `is_dir`/`rmtree`. I found no new window and no data-loss path outside a hand-made directory.
- (c) W3 is stated in the body under Forward-carry with `Carry: dismissed: ...` and is pinned by `broken_rename_gap`.
- (d) Finder's delay-only plant: `gl_toctou.py`, a 30 ms sleep after `_read_at` returns None for a slot path, copied verbatim from round 1's probe/rev-3243-e9e2db9e, which copied it from probe/rev-3170-63a83911. Results, each over 20 runs:
  - At main (null control): `RESULT one_winner widened-TOCTOU wt=main red 4 of 20`.
  - At head, with the same plant at `_read_at`: `RESULT one_winner widened-TOCTOU wt=head red 0 of 20`.
  - At head, with the plant at the equivalent point (sleep after the slot read raises FileNotFoundError, `gl_toctou_head.py`): `RESULT one_winner widened-TOCTOU(head-point) wt=head red 0 of 20`.
  - At main, with the head-point variant: `RESULT one_winner widened-TOCTOU(head-point) wt=main red 2 of 20` (ev/finder-main-headpoint.txt). The body quotes 3 of 20 here.
  - The body quotes 5 of 20 at main. I measured 4 of 20, and round 1 measured 2 of 20. The rate depends on the box; the null control is red in every measurement.
- Both roster carries for R10-GATE-LEASE-TOCTOU (handoff/audit-r10-roster f85b3b4d, wave-r10-groups.json) require the delay plant to go green at the fix. It is 0 of 20 at the head, so both are discharged.
- (e) Live checks: `get_check_runs` returned total_count 68 on one page of 100, and every run is completed with conclusion success or skipped. Gate jobs 127846717213, 127846358338 and 127843898001 all succeeded. The brief expected busy() mutual-deferral gate reds at this head; the live checks show none, so there is no concluded red for `## Red checks` to name. `pr-contract / pr-contract` 127843628154 succeeded at 10:31Z. The body's sentence "no concluded checks yet" is stale but not wrong in substance, because no red exists.
- `python3 tools/audit/seat/merge_train.py classify 411270a4... --pr 3243` -> `GREEN 411270a40b14a235482fa37c2af55132cfc74760 pending: none red: none`, rc=0.
- Merge: `git merge-tree --write-tree origin/main 411270a4` exits 0 with tree df700c41a445d89f5635a88fa1219dc1127117ac (ev/merge_tree.txt). No claim file conflicts.
- Scripts (ev/scripts.txt):
  - Closure select at head: `MODE: SCOPED -- 2 script(s) run`, which are doc_claims and entities. At main it prints `MODE: FULL`, because main's diff is empty.
  - `tests/entities.py`: head `ALL 2637 ENTITY CHECKS PASSED`, main `ALL 2632`.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED` at both ends.
  - `tests/doc_claims.py`: `ALL 296 checks PASSED` at both ends.
  - The body's figures (2637, 296, SCOPED) are re-derived.
- Diff, read three-dot: `tests/gate_lock.py` and `dev/programme/delivery/3243.md` only. The delivery row is present. VERSION, the manifest and the notes heading are untouched, and there are no claim files.
- Body Head names `411270a40b14a235482fa37c2af55132cfc74760`, which is the head I measured.
- Seam enumeration: `grep -n is_file` at the head returns `_read_at`'s use plus the grave's `is_dir`, which reads a private path. I agree the shared-slot class is one seam.
- Cosmetic: the diff writes `cases = [        ("priority: ...` on one line, because a newline was lost. It changes no behaviour. Not a finding.
- The closing self-audit, `carry_audit.py check`, returned `CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)`, rc=0 (ev/carry_audit.txt). It ran against my local copy of the PR body, which is abridged: its Head, Red checks, Forward-carry and Carry lines are verbatim, and its figure sections are omitted.
- I built my own instruments `windows.py` (round 1) and `dirprobe.py` (this round), and disclose them as mine. They are in ev/tools/. The finder's `gl_toctou.py` is also in ev/tools/.
