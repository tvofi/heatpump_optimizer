# BLOCKED: r11-owner-cooling-guard

Seat: fixer-r11-owner-cooling-guard. Base given: origin/main fd93aa3e9b161e92ead26e04ba8311b3fc0fc7e5.

Question: this group's build has already merged (#3864, merge d3d66c4040, 2026-11-25), and the roster lists no carry. Should the roster mark R11-OWNER-COOLING-GUARD landed, or does a part remain that should be named as a carry before a fixer is dispatched again?

Why it stops: at fd93aa3e9b, main has `pump_arbiter.cooling_mode`, `supply_hold.supply_write` and `supply_hold.note_cooling`, plus the `pump_mode_cooling` repair in strings.json. `handoff/r11-owner-cooling-guard` (a586328d78) and `handoff-wip/r11-owner-cooling-guard` (aebf62c457) are both ancestors of main. The roster's `resume` says stage `carries-open` and next_step `fixer`, but `carry` is `[]`, so there is nothing to build. No BLOCKED.md was ever left on this topic. The one that was left (6a2e8085e6) belongs to R11-OWNER-COOLING-AUTORETURN, on handoff-wip/r11-owner-cooling-autoreturn-fix, and that group is waiting on #3872. The returning cooling-release work therefore lives on that other topic, not on this one.

Issue #3858 is still open. Its body says the PR that lands this group closes it; closing it belongs to the orchestrator.

What resumes it: a roster edit marking the group landed, or a named carry.

No code was written.
