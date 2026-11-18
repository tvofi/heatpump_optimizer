# BLOCKED: r11-seam-ratchets (R11-SEAM-ratchets: D7-s1-02, D7-s1-03, D14-s2-03)

Question: The brief says "Do your work inline, with no subagents" and "never set FRUGAL_ALLOW_INLINE ... Never work around a hook or a refusal". The frugal@synced PreToolUse hook refuses every inline read past 5 per prompt ("frugal: inline search op 7 this prompt exceeds budget of 5 ... Delegate the remaining discovery to frugal:scout"), on Bash and on the Read tool alike, and in a scheduled single-prompt run that budget never resets. Which governs this seat: may it delegate reads to a frugal:scout/extractor subagent, may it set FRUGAL_ALLOW_INLINE=1, or is the hook to be lifted for the cloud fixer seat?

## State at the stop (no code written)

- Base: origin/main = bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f (the head the brief names); plan/r11 at 819aa2e354b4e5baaf824b8568fd72bea8168a75.
- `cloud-setup.sh --check`: OK.
- Harnesses run from a `git archive` export of 819aa2e3 against the main tree, PYTHONPATH=tests/hastub:
  - `dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py` (sha1 e2f94c69129a1e2840e5b4b83e67dab96b576f7b): `unused_package_imports=14` (the 14 UNUSED lines of D7-s1-03 unchanged), `in_function_copies=6` (the 6 COPY lines of D7-s1-02 unchanged), `ratchet_duplication_copies=8`, `recount_mismatches=0`, `ratchet_rows_off_budget=0`.
  - `dev/audit/rounds/round11/D14/s2/logflood_shape.py` (sha1 ef9a2072891916165b2096e6613d0d4637ad6dfd): `counted_warning=1`, `counted_exception=0`, `counted_critical=0`, `counted_log_level=0`, `counted_alias=0`, `live_blind_sites=1` (SITE sysid.py:1850 `_LOGGER.exception`).
- All three findings reproduce at main; none is "not reproduced at main".

## Plan the resuming seat can take (ADR-009)

1. `tests/structure.py`: a new row `unused_package_imports` from the `import_bindings` machinery (a `from .<pkg> import N` binding with no load of N in the importer, no re-export, no string naming it), recorded at its measured value (14 at bc658f9d).
2. `tests/structure.py`: a new place-keyed row for windows written at two disjoint places of one function, beside `duplicate_clones`, which stays unchanged (the score reads its window); recorded at its measured value (6 at bc658f9d).
3. `tests/entities.py` `_r10_unlatched_logs`: count `.exception` and `.critical`, `_LOGGER.log` at WARNING or above, and refuse another logger binding; add sysid.py `_finish` to the once-per-event reasoned group.
