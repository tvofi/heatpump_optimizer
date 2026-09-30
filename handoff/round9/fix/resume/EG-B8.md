# R9-EG-B8 resume note

Branch: `handoff/r9-eg-b8` (the coordinator's name; the roster's `resume.branch` says `handoff/r9-eg-dhw-block-replan`, which was never pushed). Base: origin/main `3dfebc16`.

Stage: handed off. The code head is `03bb26f1`. This note and `handoff/round9/fix/EG-B8-body.md` ride in one transport commit above it.

Code commits:
- `82b1a27f` test: the replan block (`wood_coil`, -2.0) and the DHW profile restart round-trip. At base the four new checks are red.
- `0d28d81b` fix: `blocked=h.dhw_blocked` goes into `_co_optimize`'s replan build. `normalize_profile` becomes a projection, and the learner seeds through it.
- `e6d7b737` test: three checks that pinned the raw default and the sub-one peaky mean are updated.
- `03bb26f1` test: the claim list is rewritten for this diff (5 `coord_*` captures: `dhw_usage_profile` only), and the non-finite check reads a real learner's seed.

Evidence is in `/mnt/project-files/audit-r9/fix/evidence/EG-B8/`: the probe, the fuzz, the enumerator and the mutant runner, with their outputs.

Next: the orchestrator reviews and opens the draft PR from code head `03bb26f1`. A reviewer runs the finder's probe from `handoff/audit-r9-alt`.

## Root cause draft for #1747 (for the RCA seat; not posted)

- Cause: `_build_dhw_requirements` has two call sites. The replan already existed (extracted as `_co_optimize` in c1b53971, 2026-08-22). v5.3.0 (64a54195, #80, 2026-08-28) added `blocked=dhw_blocked` to the first build only. The builder defaults `blocked=False`, so omitting it meant "not blocked" and raised no error.
- Process state: (a). No process compares the call sites of one builder. The v5.3.0 tests exercise the blocked path only at prices where the replan is not adopted (the `winter_typical` `_mb_*` fixture). The replan is reached only when its candidate scores better, and at positive prices it never does.
- Class instrument: `kwarg_seams.py` (AST, per module). It returns 11 at the base and 10 at the head, all 10 dispositioned in the body.
- Cost test, as a candidate countermeasure: a check that runs `kwarg_seams.py` over the package with an allow-list. Standing cost is about 0.2 s per run. P(recurrence) comes from the measured class frequency: 1 instance of a defaulted keyword omitted at a second call site, found in rounds 1-9. A per-seam allow-list is keyed on (method, keyword, enclosing function), which `fixer.md` step 14 warns about. The decision is the RCA seat's.
