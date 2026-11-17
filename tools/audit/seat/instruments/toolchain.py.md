# `toolchain.py`

- `toolchain.py` — the stable tools ref (R11-PRE-TOOLCHAIN-PIN; owner ruling
  2026-11-13, card P1): the branch `toolchain/stable`, always a commit of
  main. This file is the one place the ref's name and the seat paths
  (`tools/audit/seat`, `tools/pr`, `tools/audit/carry_audit.py`) exist.
  - `behind [<dir>] [--from <sha>] [--all] [--fetch]` prints the count of
    commits the ref holds that the checkout (or `<sha>`) lacks, over the seat
    paths; `--all` counts every commit. A checkout level with or ahead of the
    ref prints 0, so a caller that acts on the count never moves a checkout
    backwards. `--fetch` reads the ref from origin first.
  - `promote [<sha>] --repo <owner/name> [--dir <checkout>]` moves the ref to
    the newest main commit whose `ci.yml` push run reads MACHINERY green
    (`tools/ci/gate.py` `status`), or to `<sha>`. It refuses a commit not on
    origin/main, a move that is not a fast-forward and a verdict that is not
    green, pushes without force and reads the ref back. Its answers:
    `PROMOTE <utc> <old> -> <new> run=<id>`; `PROMOTE-CURRENT` when nothing
    newer is green; `PROMOTE-HELD`, exit 3, when the newest three concluded
    main runs past the ref all read machinery red or unread. PRODUCT is not
    read: a product-red, machinery-green commit promotes.
  - `promote --init` creates the ref, and only while it is absent. Until it
    exists every verb refuses naming this command; an absent ref is never
    read as main.

  Exit 0 a count, a promotion or nothing newer; 1 a refusal; 2 a failed read
  (git or GitHub), which concludes nothing; 3 held. When: the beat's
  `toolchain-promote` row runs `promote` every ten minutes and keeps the last
  answer in `S/beatd/toolchain.txt`; a hold, a refusal or a failed read is the
  row's digest line. By hand: `promote --init` once after the merge that adds
  this file, and `promote <sha>` to move the ref to a named green commit.
  `prune_refs.py` keeps `toolchain/*`. `--self-test`: real git over a
  throwaway origin with GitHub faked, each refusal beside the case that moves
  the ref; `dev/audit/harnesses/r11_toolchain_mutants.py` drops each rule in
  turn.
