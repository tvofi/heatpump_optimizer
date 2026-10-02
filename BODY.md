_Requested by **tvofi**_

Part of #201. Truths every `docs/delivery/<N>.md` that read **open** at origin/main aab94eea2 for a PR that is now merged, per `delivery-status-tracking.md`. Each row now reads `**merged** <8-hex merge commit>, <existing text>`; only `docs/delivery/*.md` changes, one line per file.

Changed (5, all merged, 0 closed-unmerged, 0 still open): #1838 #1842 #1843 #1844 #1849

## Head

67fff54d2980e3cc7ce5568ef7f22f268ce78675

## Mutation proof

n/a: record-only change to `docs/delivery/*.md`; no production or check code changes.

## Null control

n/a: no cost, gain or timing claim. Before the change `git grep -l '\*\*open\*\*' origin/main -- docs/delivery` listed these 5 files; after it lists none.

## Figures

- merged 5, closed-unmerged 0, still-open 0: `git grep -l '\*\*open\*\*' origin/main -- docs/delivery`, then `gh pr view N --json state,mergeCommit` per file.

## Red checks

none

## Forward-carry

none

## Friction

none
