# BLOCKED: r10-flow-toolkit-model

No code is committed. Setup finished: unshallowed, cloud-setup --check OK, worktree cut from origin/main (7e8939d38).

Blocker: the session's PreToolUse frugal routing hook ("inline search op N this prompt exceeds budget of 5") refuses every Read and Bash call after a few reads. Its budget did not reset after two delegations (a scout and an extractor). The hook's bypass is the FRUGAL_ALLOW_INLINE=1 environment variable, which the brief forbids using ("never work around a hook"). Without reads I cannot edit tools/plan/replan.py.

Question for the owner: may this seat set FRUGAL_ALLOW_INLINE=1, or should the hook's budget be raised for fixer seats?

Design worked out so far, for whoever continues (active carries 0, 2, 3, 8, 9, 10, 11, 12; carries 1 and 7 are moved to R10-BODY-CONTRACT; carries 4 to 6 are dismissed duplicates):
- Carry 2: add "absorbed" to is_done (DONE_STAGES), and print each absorbed group with the absorber named in its resume note, with an advisory when the note names no group.
- Carries 10/11: split out post-closure groups (an owner-step whose next_step names the closeout stamp, or one whose after names R10-STAMP-ROUND-MAJOR, plus descendants). Schedule them after the closing stamp's `at`, keep them out of closure and stamp carries, and compute the critical path on the in-round graph only.
- Carry 8: start a ready TIER_CRITICAL group on an overflow slot (slots+100+n). free_slot must ignore overflow slots, and check_plan must exempt those groups from the in-flight, seats and wave checks.
- Carry 9: take the stamp cadence from a --since-tag input, pre-crediting production groups already done since the tag. Count groups, not PRs, and ignore comment-only diffs under custom_components/.
- Carries 0/3: --live-refs (an ls-remote listing) and --in-flight (a PR JSON) demote a stage-word live group that has no ref and no PR. An open-PR group starts at t=0 with credit; a design-only group starts at t=0 without credit. Add a binding-chain print and an inflow_groups_per_hour field that is 0 by default. --measure-sizes already exists in tools/plan/size_durations.py.
- Carry 12: a new gantt-drift instrument in tools/audit/seat/, wired into governance.yml, INSTRUMENTS.md and the closure classification.
- Consumers to re-check after editing replan.py: tools/audit/seat/plan_page.py, state_docs.py, size_durations.py, beat_jobs.py. The only place that pins stamp_every is replan.py (the DEFAULT_CAPS default of 5, a self-test at about line 1379, and the --stamp-every default).
