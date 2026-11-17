Fix review: blocked 3099d416f40cf3e5468b6d93b6c410394cbbdfb2 harness: r10_seat_selftests_mutants.py pins cloud_dispatch-15 and cloud_dispatch-16 match nothing at this head and print NOT RUN

bus-nonce: 03de65e296c3d10b84ce689ee61102bc

## Block

This diff rewrites two production lines of `tools/audit/seat/cloud_dispatch.py` that a committed mutant harness pins by their exact text, and does not re-spell the pins. `dev/audit/harnesses/r10_seat_selftests_mutants.py`:

- `cloud_dispatch-15` plants on `if not design_approved(repo_dir, group_id):`. At this head that line is `approved = design_approved(repo_dir, group_id)` and then `if not approved:`.
- `cloud_dispatch-16` plants on `return first == f"Design review: approve {tip}"`. At this head the line is `return tip if first == f"Design review: approve {tip}" else ""`.

`mutate()` returns -1 on a pattern found other than once. `main()` counts that as a survivor (`survivors += rc <= 0`), so the harness exits 1 on any tree carrying this diff:

- At the merge base 174e78cebf, each one alone prints `KILLED rc=1` and `RESULT survivors=0`.
- At this head, each one prints `NOT RUN rc=-1 | PATTERN FOUND 0 TIMES` and `RESULT survivors=1` (ev/r10_pins_base.txt, ev/r10_pins_head.txt).

This is the stale-marker shape the body itself repairs in `r11_honest_starts_runs.py`. No CI lane runs this harness, so CI cannot see it (`git grep` finds no workflow or test reference).

The production predicates are still pinned by the self-test. I planted the two mutants' intent on the new spellings by hand at this head:

- `if not approved:` → `if False:` gives 4 FAIL rows.
- `first == f"…{tip}"` → `first.startswith("Design review: approve ")` gives `181 checks, 1 failed`.

So the repair is to re-spell the two pins' `old`/`new` strings to the new lines. Re-run both named mutants to `KILLED`. No production change is owed.

## Findings

- The stale pins above, the block itself; the fixer re-spells them on this branch before re-handoff. Carry: dismissed: this verdict's block, owed by this PR's own fixer before merge, not a later stage's

## Evidence

Round 1 (first review of this head). Measured from a detached worktree at 3099d416f40cf3e5468b6d93b6c410394cbbdfb2.

- `git diff 174e78cebf...origin/main -- dev/governance/roles/` is empty, so the contract read is current.
- The PR body's `## Head` names 3099d416f4, the head measured.

RESULT lines:

- RESULT classify `GREEN 3099d416f40cf3e5468b6d93b6c410394cbbdfb2 pending: none red: none` (ev/classify.final). `owed-reds` does not include `nightly-status`, the packet digest's only red, so no `## Red checks` answer is owed.
- RESULT merge-tree origin/main head: rc=0, no conflict (ev/merge_tree.txt).
- RESULT `cloud_dispatch.py --self-test`: `181 checks, 0 failed`. Body: same.
- RESULT `cloud-setup.sh --self-test`: `30 checks, 0 failed`. Body: same.
- RESULT `r11_toolchain_mutants.py`: `mutants=37 survived=0`. Each D- and K- mutant is `killed`, and M0 is null-ok for all five files. Body: same (ev/mutants.log).
- RESULT targeted mutants of my own on the changed predicates: the two above, both killed by the self-test.
- RESULT real-BLAS `--kernels` probe at this head, seat pinned to Haswell: `ran SkylakeX Haswell Sandybridge Nehalem; red on none; not run none`. Body: same.
- RESULT `r11_honest_starts_runs.py kernels` at this head: exit 0, `blocks that failed a check or did not complete 0` (ev/hsr_head.log).
  - Duty-switch `REPLACED False` under SkylakeX only.
  - Starts-and-runs `REPLACED False` under SkylakeX, Sandybridge and Nehalem, and True under Haswell. That matches the body.
  - The starts-and-runs block reads `ALL 57 FEATURES BLOCK PASSED`, where the body quotes 51. The body's figure is from a3183c1fef, before the main merge f1e36ef847, so it is a stale figure, not a defect.
- RESULT `_next_header` at this head resolves to `# --- #3616: an implausible slab seed is refused ---`, the first header after the group's section (1059 lines in). That is the block the body says the stale marker crossed into.
- RESULT VERSION, manifest and RELEASE_NOTES are untouched in the three-dot diff. No claim file and no `*_budgets.json` is touched.
- RESULT the class rules the body names are not re-run beyond the `design_approved` callers. `git grep design_approved` returns the dispatcher, its self-test and the r10 harness pin. The pin is the block above.

Not re-derived:

- The #3602-era worktree figures at 5d9f00db01 and 303e10f8c8.
- The carry-12 ls-remote reading.
- The roster `part_split` count at f223cd88f6.

Those figures are the fixer's.
