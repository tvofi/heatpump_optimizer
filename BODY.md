Closes the R10-GATE-LEASE-TOCTOU free-slot race carried from PR 3170 (item 42008ca4). `_free_slot` looked a second time (`is_file`) after a missing read, and its unparseable-slot branch unlinked a rival's fresh owner, so two takers held one slot. One `read_text` now decides absent (`FileNotFoundError`, return the index; `Owner.create`'s hard-link arbitrates) against broken, and a broken slot is reaped through `_steal(path, None)`. Repair round 2 (verdict/3243, blocked at 3cbcbd5d: mutation-vacuous) adds the acceptance cases that pin the reap and its put-back, and one production change: `_steal` removes a directory-valued grave (`shutil.rmtree`) instead of raising `IsADirectoryError` out of `take_slot`.

Alternatives that lost: a lock around `_free_slot` (the pool takes no flock by design); a retry loop on the test side (hides the race); an inode re-check before the rename (narrows, does not close, and adds a second look of the kind this PR removes).

## Head

`af5302867a664bdd89c76bdb8fd463c297210d3d`, merge base `dc0a170b671814be196a54b1c71e29449f54d6d7` = origin/main at `date -u` 2026-11-06 (unmoved since the merge; `git merge-base HEAD origin/main` prints it), so one `prepr.sh` run covers this head: `PRE-PR: af5302867a66... rc=0`.

## Mutation proof

Every row: mutate `tests/gate_lock.py`, run `PYTHONPATH=tests/hastub python3 tests/gate_lock.py --accept`, restore. Null control row: unmutated head.

| mutant | change | result |
|---|---|---|
| null | none | `ALL 46 gate lock acceptance checks PASSED` |
| M1 | merge base's `_read_at` / `is_file` / unlink form of `_free_slot` | `4 of 46 FAILED`: `delayed_read`, `broken_put_back`, `broken_rename_gap`, `directory_slot` |
| M3 | `_steal(path, None)` reverted to `path.unlink(missing_ok=True)` | `3 of 46 FAILED`: put-back (`kept=None`), rename gap, directory |
| M4 | the `_steal(path, None)` line deleted (reviewer M4) | `3 of 46 FAILED`: `broken_reclaimed` (`reaped=False create_won=False`), rename gap, directory |
| M6 | `shutil.rmtree` directory branch disabled | `1 of 46 FAILED`: `directory_slot` (`IsADirectoryError`) |
| M7 | put-back `os.link(grave, owner_path)` removed | `1 of 46 FAILED`: `broken_put_back` (`kept=None`) |

The M4 and directory cases use `_free_slot` plus `create`, not `take_slot`: `take_slot` retries a lost create forever, so with the reap deleted the first version of these cases hung (`timeout` rc=124) instead of going red. The final cases fail fast (rc=1, measured above). Reviewer M2 and M5 are not rebuilt: M2 (second read, reap via `_steal`) is near-equivalent because `_steal` puts back the rival; M5 (FileNotFoundError as broken) is equivalent because `_steal` returns on a missing path and the create arbitrates.

## Null control

Finder's delay-only plant (`gl_toctou.py`, 30 ms after a slot's missing read, 20 runs of `one_winner`) and the reviewer's head-point variant (`gl_toctou_head.py`), run from worktrees at origin/main `dc0a170b` and at this head: `widened-TOCTOU wt=main red 5 of 20`, `head-point wt=main red 3 of 20`, `widened-TOCTOU wt=head red 0 of 20`, `head-point wt=head red 0 of 20`. The baseline reds are the plant's null control (a plant that never reddens the baseline proves nothing); the rate is box-dependent (reviewer measured 2 of 20). The acceptance cases are deterministic hooks rather than delays: the new cases fire at the read and at the rename of the slot path.

## Figures

- Acceptance: `PYTHONPATH=tests/hastub python3 tests/gate_lock.py --accept` printed `ALL 46 gate lock acceptance checks PASSED` at the head.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED`, running `tests/doc_claims.py` (`ALL 296 checks PASSED`) and `tests/entities.py` (`ALL 2637 ENTITY CHECKS PASSED`); `python3 tests/structure.py` ended `STRUCTURE RATCHET PASSED`.
- Seam enumeration for "check a slot, then act on a second look": `grep -n is_file tests/gate_lock.py` returns `_read_at`'s own use plus `_steal`'s `grave.is_dir()` (a read of the private grave, not of the shared slot): the shared-slot class is one seam.
- Windows pinned (reviewer's plants W1-W5 as hooks): read-then-valid-owner (`broken_put_back`), rename-gap rival (`broken_rename_gap`), absent-then-rival (`delayed_read`), garbage (`broken_reclaimed`), directory (`directory_slot`).
- `HPO_ALLOW_STALE_TOOLS=1 bash tools/pr/prepr.sh` rc=0 at the head; claim files byte-identical to origin/main; no VERSION, manifest or notes edit.

## Red checks

At the previous head `3cbcbd5d`, `gate` jobs 127794397203 and 127797085107 concluded failure with the placeholder `FAIL run(s) [42188289030] at this head are still being judged; their gate decides`, written while run 42188289030 was in progress. Class: a gate read before its run concluded. Cheaper detector: none; the placeholder is the gate's own interim state and the run's conclusion supersedes it. This head has no concluded checks yet (its CI starts when the handoff moves the PR head); none of its reds is known.

## Forward-carry

- The `_steal` rename -> link-back gap (reviewer plant W3), reachable from the broken-slot path, is not closable here: a POSIX rename-aside is the only atomic claim, and the put-back happens after the slot path is empty, so a rival's `create` there wins by hard-link arbitration. Measured by `broken_rename_gap` (rival D inside the gap): exactly one owner remains (`owner=D`), no `stale-*` grave, no torn slot; the displaced owner C loses the slot silently. Pinned in `tests/gate_lock.py` so the bound cannot widen. Needs a broken slot file, a valid owner replacing it and a third taker inside microseconds, none writable by any in-tree writer. Carry: dismissed: no atomic compare-and-remove exists; bound pinned by broken_rename_gap in tests/gate_lock.py
- Reviewer M2 and M5 near-equivalent mutants, recorded under Mutation proof. Carry: dismissed: put-back and create arbitration make both harmless; see Mutation proof

## Friction

none
