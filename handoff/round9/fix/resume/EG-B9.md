# R9-EG-B9 resume (fixer seat)

Branch `handoff/r9-eg-action-copy`, from origin/main `89d1ddf5` (EG-R0's
#1763 merged mid-branch; merged locally, never rebased).

- Failing tests FIRST: `47353326` — the S1/S2 probe arms ported into
  `tests/features.py` (`_r9egb9_*`), nine red at base, five nulls green.
- Fix: `ac65f2aa` — `boost.adopt_plan` holds the plan base in boost's weak
  map (coordinator attrs are at zero ratchet headroom); `boost.apply` lays
  the overlay on a copy each cycle; `async_simulate(limited=...)`, the tile
  and the advisor pass `limited=False`; the borrow and its dead arms are
  deleted. `ec86d3d2` re-records five structure rows DOWN. `367730d6` makes
  the entities producer scan follow `adopt_plan` (its second argument is the
  value) and pins the #1752 null to off/0 kW/turn_off.
- Mutation proof: six mutants (M1, M1b, M2 own-design; M3, M4, M5
  own-design), each killed by exactly its own defect's checks; logs in
  `/tmp/r9egb9/mut_*.log` (transport files off the branch).
- Gate: `MODE: SCOPED -- 16 script(s) run`; features and entities re-run
  green at the final head. `R9-F2.1 P3` (storage multi-start) is red on this
  arm64 box at the CLEAN base too, identical figures — main's, not this
  branch's; optimizer-only check, out of this diff's reach.
- Root cause on #1752 posted and read back (comment 5881724247); #201 intent
  posted and read back (comment 5881722407).
- Next: fix-review.md from a detached worktree at this head (review branch
  `handoff/r9-eg-action-copy-review` per the roster). After handoff the head
  is the reviewer's; only the orchestrator moves it.
