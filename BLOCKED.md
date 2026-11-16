# BLOCKED: R11-OUTSIDE-ROOMS-P2 (fixer, base f9b680fee4)

Question: The approved note (design/R11-OUTSIDE-ROOMS-P2 4784b5940e, `Design review: approve` at design-verdict/R11-OUTSIDE-ROOMS-P2 e59dcfd724) builds phase 2 on what phase 1 adds, and phase 1 has no code anywhere. Is R11-OUTSIDE-ROOMS-P1's fixer dispatched first and this seat re-dispatched on its handoff head, or is this group re-scoped to carry phase 1's rooms module, room read and list option as well?

Evidence, measured at origin/main f9b680fee4:
- `git ls-remote origin | grep -i rooms` returns five refs, all for this group (design, design-verdict, and the designer, design-reviewer and fixer dispatches): no dispatch/, handoff/, handoff-wip/, fix/ or archive ref for R11-OUTSIDE-ROOMS-P1.
- dev/programme/rosters/wave-r11-groups.json on handoff/audit-r10-roster 1427bf2ac0: R11-OUTSIDE-ROOMS-P1 is `resume.stage: not-started`, `commit: null`; this group's `after` is [R11-OUTSIDE-ROOMS-P1].
- `git ls-tree --name-only origin/main custom_components/heatpump_optimizer/ | grep -i room` prints nothing, and `git grep -n -i -E "room_list|CONF_ROOM|room_entities|RoomReading" origin/main -- custom_components` prints nothing: the tree holds no room list key, room read or rooms module.
- What the note assigns to phase 1 and phase 2 reads: the rooms module with its reading record and per-coordinator side table, the room read beside `InputReader.read`, the list option and its `EntryConfig` tuple, and the two sensors the lift attribute lands on. The note's serial order is "R11-OUTSIDE-SLAB-SEED-GUARD, then P1, P2, P3a", and its carries r1, r2, r3, r5, s1, 5a1c0e01, 5a1c0e02 and 5a1c0e03 are addressed to R11-OUTSIDE-ROOMS-P1.
- Building those here would put two fixers on one owning seam (`fixer.md` step 17: a departure from the architect note is raised, not made).

Also open before phase 2's gates can be final, each routed "decision: owner" and absent from dev/programme/RULINGS.md (`git grep -n -i -E "room|3616|holiday" origin/main -- dev/programme/RULINGS.md` prints nothing): whether the holiday profile gates the lift as away does (the verdict's routed decision), the cap under the band (note: 1.0 K), and phase 2 as its own opt-in flag, default off.

No code was written.
