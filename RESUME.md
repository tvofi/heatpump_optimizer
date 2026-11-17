Repair of #3696 after `Fix review: blocked` at 3fe03e1480. Code head ad36eefec030b7e38c99c583a0da145795562d93 on handoff/r11-pre-no-read-builders.

- The step ref handoff-wip/r11-pre-no-read-builders held the first handoff's BLOCKED.md commit b5fb726267, not an ancestor of the pull request's head. Its deletion is refused (HTTP 403), so each step was pushed as a fast-forward: a commit with the code head's tree and parents (code head, the ref's tip). The code on handoff/ is the linear head, without those commits.
- The forward-carry for the column is re-written, so its item id is new; item 6889317b on R11-PRE-PARALLEL-PIPELINE's row is the text it replaces.
- prepr: the full scoped run passed every code step and refused two body items (a carry naming a file not in the tree, an unrendered figure block); after their repair the body-delta run (PREPR_SKIP_CODE=1) ended rc=0. A container restart killed one run in between; nothing was lost.
