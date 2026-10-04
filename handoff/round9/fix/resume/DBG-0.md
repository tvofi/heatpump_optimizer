# R9-DBG-0 resume — debugger pre-study (STUDY seat, no fix PR)

- stage: complete — pre-study doc, bundle-format prototype, ingest smoke, roster shapes all delivered
- branch: handoff/r9-dbg-0 (from origin/main @ ed0151ad2)
- doc: tools/audit/round9/prestudy/debugger-prestudy.md (also on handoff-body/r9-dbg-0 as BODY.md)
- prototypes: tools/audit/round9/prestudy/dbg_bundle_gen.py (synthetic-week bundle writer, hpo-debug/1), dbg_ingest_smoke.py (12-stage ingest/replay/monitor smoke, pass 12/12; --corrupt accuracy fails 11/12); runs/ carries the gzipped week bundle (132,629 B), day-1 arm, generator log, both smoke logs
- key results: week bundle 1,435,346 B raw / 132,629 B gz (synthetic DHW-only floor); reuse spine = export.py hpo-replay/1 + tests/replay.py run_fixture + QuarantiningStore/DOMAINS + diagnostics.py TO_REDACT/_coarsen/_coordinator_snapshot; proposed groups R9-DBG-1 (module, w15, opus), R9-DBG-2 (self-tests+diagnostics surface, w16, sonnet), R9-DBG-3 (harness under tools/replay/, w15, sonnet)
- open decisions for orchestrator/owner: coordinate coarsening 1dp vs 2dp; harness home tools/replay vs tools/audit/harnesses (F11 edge); diagnostics inline-bundle cap 8 MB
- next_step: none for this seat; fold group shapes into wave-r9-groups.json
