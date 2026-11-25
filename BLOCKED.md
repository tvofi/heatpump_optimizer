# BLOCKED: r11-owner-extheat-override review repair

The review repair is done and pushed: handoff/r11-owner-extheat-override at 80412b13b21110010499820e9799fe7dd4a0b3ce (delta dc972220f313..80412b13b2: b4b8d88a adds the two block_ignored-true checks, each failing on its mutant and passing on the head; 80412b13 records class_excess_loc 17290 -> 17283, an improvement that the bot merge of main brought in). Scoped gate at 80412b13: `31 TEST SCRIPT(S) PASSED; 4 SCOPED OUT AND NOT RUN`, exit 0.

body_push.sh refused the body (REFUSED BODY-LINT, exit 1, not 4). Its only refusal is the existing Forward-carry item, which this repair did not touch:

    REFUSE carry: BAD-DEST body item 6b7a7d71: R11-OWNER-CARD-EXTERNAL-HEAT: R11-OWNER-CARD-EXTERNAL-HEAT is carries-open (resume.stage carries-open); a carry goes to the live group owning the seam, else the producing group keeps the fix; valid targets: unknown (no --pr-group) -- CARRY-AUDIT: 1 finding item(s): 0 routed, 0 unrouted, 1 bad destination(s), at origin/handoff/audit-r11-roster c02eba79d0

The refused body is at handoff-wip/r11-owner-extheat-override-body e7befe0d7fffc1e78cd16d32f742dfb29cb84523; it passes every other check.

Question: R11-OWNER-CARD-EXTERNAL-HEAT is now carries-open, and the body says this carry already landed at 58e94013. Which should the body's Forward-carry do: (a) name a live group that owns the card's statusPill seam, (b) be kept by this group as its own fix, or (c) be dropped because it has already landed? Re-routing a roster carry is outside the fixer seat.
