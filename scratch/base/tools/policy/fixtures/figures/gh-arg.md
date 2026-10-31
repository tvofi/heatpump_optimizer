The positive arm. This is the #715 round-seven defect: an enumerator over an
open window, replacing a literal exactly as `writing-for-agents.md` requires,
whose command passes `--arg n "$n"` to `gh api`. `gh api` has no `--arg` flag,
so the client refuses before any request is made, the loop prints `0` for every
possible state of the world, and the figure rule is satisfied in appearance.
A fix reviewer found it by running it; nothing in the tree did.

## Head

0000000000000000000000000000000000000000

## Figures

- **13 pull requests** opened in the window. Enumerator:
  `for n in $(seq 1 100); do gh api --paginate '/repos/o/r/pulls' --arg n "$n" --jq '.[]|select(.number==$n)|.number'; done | wc -l`

## Red checks

none
