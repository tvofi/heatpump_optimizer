# BLOCKED: r11-seam-governance-text (R11-SEAM-governance-text)

Question: the brief says "Do your work inline, with no subagents" and "Never work around a hook or a refusal", but the frugal plugin's PreToolUse guard (`frugal: inline search op N this prompt exceeds budget of 5`) refuses every further inline Read and Bash search in this one-prompt scheduled run, and `Edit` requires a prior `Read`. Which governs this seat: may it delegate discovery reads to a haiku/sonnet subagent as the guard asks, or does the dispatcher re-fire it with the guard's budget raised or off for this seat?

No file was changed. State at the stop, worktree cut at origin/main `bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f`.

## Baseline readings at bc658f9 (finders' harnesses run from the plan export at `819aa2e354b4e5baaf824b8568fd72bea8168a75`, cwd = worktree root)

Every finding reproduces at main; none is "not reproduced at main".

| finding | command (under `PYTHONPATH=tests/hastub PYTHONUTF8=1`) | reading at bc658f9 |
|---|---|---|
| D6-s5-01 | `claims.py --repo <wt> --only c_mock` / `--only c_fix_review_j5` | `mock_users=5`; `fix_review_j5_refs=0` |
| D6-s5-02 | `claims.py --only c_round4_d6` | `round4_d6_rewritten_at_doc_path=0` (gate rewrites `dev/audit/rounds/round4/D6/claims.json`, `claims.md`) |
| D6-s5-03 | `claims.py --only c_brief_exclude` | `round2_symbol_found=1`, null control `claude_symbol_found_null_control=0` |
| D6-s5-04 | `claims.py --only c_handover_docs` | `handovers_under_docs=0` (handover is `dev/programme/HANDOVER.md`) |
| D6-s5-05 | `claims.py --only c_unleased` | `leased_or_slotted_besides_stress=9` |
| D6-s5-06 | `claims.py --only c_instrument_dirs` | `instrument_record_dirs_absent=19` of 19 |
| D6-s5-07 | `claims.py --only c_worktree_apply` | `worktree_gc_apply_refused=1` |
| D6-s5-08 | `claims.py --only c_event_hub` | `event_hub_cited_name_files=0`, nearest `dev/audit/harnesses/r10_livestate_event_hub_writes.py` |
| D6-s2-02, D6-s2-03 | `D6/s2/probes.py --probe gov_paths` | `gov_paths=2` (`fixer.md` and `orchestrator.md`, `docs/decisions/` -> `dev/governance/decisions/`) |
| D6-s7-02 | `D6/s7/plan_claims.py --repo <wt>` | `wrong_rows=9` of `units=2628` |
| D11-s2-04 | `D11/s2/policy_health.py --list` | `dup_units=16`, `rulings_overlap=1` |
| D15-s1-02 | `D15/s1/privacy_gate.py --bundle B` | not run: needs a debug bundle not in the tree |

Harness paths are relative to `dev/audit/rounds/round11/` at `819aa2e3`.

## Scope note for the re-fire

The architect note says "no instrument code changes here", so D11-s2-04's proposed mechanisation (a `policy_lint` class) is outside this group; D4.md, D5.md and D11.md are owner's-words briefs and `RULINGS.md` is verbatim, so the duplicate's pointer belongs in the criteria/second file, not the owner's text.
