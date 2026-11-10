Repairs the batch 130 ruling after verdict/3383 (blocked, stale-base). P401 is re-ruled **REJECT, a duplicate of P362**: `1e994e484` (in this PR's merge base and on main) already fixes the directory at source time, so the defect no longer reproduces and the first ACCEPT would have re-dispatched landed work.

- **Measured at origin/main `b07627250`:** a fresh worktree sources `pr_args.sh` by a relative path, then `cd`s into a stale sibling and calls `pr_tools_fresh`. The tree passes; the same probe with the `# mut:argsdir` line deleted refuses `STALE CHECKOUT`. `PR_ARGS_DIR` is in `pr_args.sh` at origin/main and absent at `294a880da`, the base the first ruling read.
- **Dropped:** the 175-commit lag and the 77-notice count, taken before `1e994e484`.
- **Not a repo change:** the dispatch seat's `HPO_ALLOW_STALE_TOOLS=1` exports are host-local script state.

The diff is the ruling and the delivery row. No product behaviour changes.

## Head

`9fe80a402e9122b3a3e2ade8816c4070f7946886`

## Mutation proof

The ruling's consumer is the triage gate in `tools/audit/seat/roster_edit.py`. `triage_refusal` on a carry citing `s6-batch130.md#P401` is refused as "not an ACCEPT ruling (REJECT)". With the verdict line flipped to ACCEPT, the same carry passes (returns None), so the gate reads the verdict.

## Null control

P402 reads `None` from `ruling_verdict`. For the reproduction, the mutant with `# mut:argsdir` deleted refuses where the tree passes, so a clean run can fail.

## Figures

- `git diff --stat origin/main...9fe80a402e9122b3a3e2ade8816c4070f7946886`: the ruling and the delivery row.
- Reproduction: the probe described above, run at origin/main `b07627250` on 2026-11-10; its mutant names the line it deletes.
- No capped file is touched.

## Red checks

`none`. Verdict/3383 (stale-base) is a review verdict, not a check.

## Forward-carry

none

## Friction

none
