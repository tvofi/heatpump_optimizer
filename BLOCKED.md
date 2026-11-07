# BLOCKED: R10-PARTLOAD-RESIDUE repair round 2

Code head 306a0b76e8bdd3e82e7370e3f1ad7bc08be832c1 is pushed to `handoff/r10-partload-residue`. The body passed `prepr.sh --body-check --pr-branch fix/r10-partload-residue` (0 errors; carry audit 2 routed). `body_push.sh` then refused it, so `handoff-body/r10-partload-residue` was not pushed:

    CARRY-MISSING R10-SAV-COMFORT body item 213e8a10: not in its brief or carries
    body_push: refused body kept at handoff-wip/r10-partload-residue-body a8a8646832507049a220cb6ed221d2482aaff940

The question for the dispatch seat: land the carry text in that body's `## Carry for the roster` section onto R10-SAV-COMFORT's `carry`, on `handoff/audit-r10-roster` (append-carry op; a fixer may not write the roster). Then re-run `bash tools/audit/seat/body_push.sh r10-partload-residue <that body>` unchanged.

Cure (b) was measured and does not settle the carry: at the plan's own energy-weighted draw, the terminal error is up to 3.714491 per horizon. So cure (a) is taken.
