Group: R10-ROSTER-OPS. Roster batch s8: the round-10 roster branch `handoff/audit-r10-roster` at c7026896d075d24b8d5dcc25bf70bb395fc954af merged with `origin/main` at 039eee1dc9c210edd31a6e1a806f4ceb9c0d048b so the roster carries main's own roster edits and lints against main's tree. The only file touched against main is `dev/programme/rosters/wave-r10-groups.json` (236 groups; main carries 215).

The merge conflicted in that one file, in three groups both sides had edited, and was resolved by union, never by taking a side: R10-BUFFER-STORE keeps the roster branch's `done` stage and commit and main's `fixes` entry 2500; R10-FLY-SUITE-ENV-FLAKES keeps main's three-seam brief and carries from both sides (the wc -l seam appears once from each, plus the cloud-fixer-prompt carry); R10-NIGHTLY-HB-RESPAWN keeps both carries. Every other group is taken from the one side that changed it. The merged file was read back: no conflict markers, 236 groups, the three groups' fields as above.

## Head

c7dd644459cb9578592c9145f656f58ecfb64463

## Mutation proof

n/a: roster data, no production or instrument code changes.

## Null control

n/a: no quantified claim. The lint control: before the merge-resolution the file held conflict markers and `node tools/policy/brief_lint.mjs` could not read it; at the head it prints `TOTAL: 0 error(s) across 1 file(s)`.

## Figures

- `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` prints `TOTAL: 0 error(s) across 1 file(s)`, exit 0, at the head.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`, exit 0, at the head.

## Red checks

none

## Forward-carry

none

## Friction

none
