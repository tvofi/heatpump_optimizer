Fix review: merge 7e5838a02eac4736e6c2ea0f5b6f85f51328f0f1

bus-nonce: 221c5d948d38601d851762209533ccea

Round: 1 (first review of #2710 by this seat).

## Findings

- #2710 must merge only after #2742 (`carries-open` joins `PROTECTED_STAGES` in `tools/audit/seat/roster_sync.py`). At this head alone `roster_sync.py --self-test` prints `53 checks, 1 failed` (carries-open unclassified), so `governance / instrument-self-tests` stays red until #2742 lands; #2742 is still a draft. Carry: R10-ROSTER-SYNC-CARRIES-OPEN
- The PR title is the raw merge-commit subject ("Merge branch 'handoff/audit-r10-roster' ... into fix/audit-r10-roster-pr5") rather than a description of the roster landing. Carry: dismissed: cosmetic; the body states the content, and no gate reads the title for this kind of PR.

## Evidence

- Head measured: 7e5838a02eac4736e6c2ea0f5b6f85f51328f0f1, still the head of fix/audit-r10-roster-pr5 when this verdict was written (ev/head_at_post.txt).
- Scope: `git diff --stat 73b69fe0a 7e5838a02eac4736e6c2ea0f5b6f85f51328f0f1` shows two files, `dev/programme/rosters/wave-r10-groups.json` (+888/-168) and `dev/programme/delivery/2710.md` (+1). VERSION, the manifest and RELEASE_NOTES.md are untouched. There is no production or test code, so the mutation proof is n/a as the body says, and no harness, class rule or claim file applies.
- Policy banner: the brief marks this a POLICY CHANGE. The diff touches no file that CLAUDE.md names as policy: no CLAUDE.md, no .claude/rules, no dev/governance and no dimension brief. A roster under dev/programme/rosters is roster state written by `roster_edit.py` ops. The body quotes no tvofi wording, so there was no owner text to check sentence by sentence; nothing adds, drops or loosens a binding.
- Figures re-derived with the body's own jq rule:
  - origin/main 73b69fe0a against this head: 171 groups, then 181; removed []; new = the 10 groups the body lists; changed 69.
  - The same rule run on ac5788f against 50c690758 gives the identical result.
  - Stages, main then head: done 96→102, in-progress 8→21, not-started 60→45, queued 6→6, absorbed 1→1, carries-open 0→6. All match the body.
- `git rev-list --count ac5788f..50c690758` prints 231, matching the body.
- The head's roster is byte-identical to 50c690758 (`git diff --exit-code`, rc 0).
- Null control re-run: `git diff --exit-code 3b4b615e0 ac5788f -- roster` gives rc 0. Against the current origin/main 73b69fe0a it also gives rc 0, so nothing main wrote to the roster is overwritten.
- `git merge-tree --write-tree origin/main 7e5838a02eac4736e6c2ea0f5b6f85f51328f0f1` gives rc 0: no conflict, and no claim file is involved.
- Lints at head (ev/lints.txt):
  - `brief_lint.mjs` on the roster prints `TOTAL: 0 error(s) across 1 file(s)`.
  - `ref_privacy.py --check` prints `0 refused`.
- Red check: `governance / instrument-self-tests` was failure at ce69a3f2e, 19ab022ea and 6fdf9bf5d.
  - Reproduced at this head: `roster_sync self-test: 53 checks, 1 failed`, got {'carries-open': 'wave-r10-groups.json'} (ev/roster_sync_selftest_head.txt).
  - Merging this head with #2742's head 7dc281cd3 (merge-tree rc 0) prints `55 checks, 0 failed` (ev/roster_sync_selftest_merged_with_2742.txt).
  - The body names the check, its cause and the cheaper detector (the self-test itself, with no new standing cost). The trigger is answered.
- `gate` failure at ce69a3f2e: the "CI edit" job printed "FAIL run(s) [40101560799] at this head are still being judged; their gate decides". The "CI code" gate at the same head is success, so this was a pending-judgement exit and not a failing check.
- CI at this head: only prelude, refresh and cancel-superseded runs exist, all queued (read at 15:23 UTC, 8 minutes after the push). The merge train must read this head's concluded runs before merging. Expected: the instrument-self-tests red persists until #2742 merges.
- Forward-carry: the body says "none", and none is owed. The carries this roster lands are the carry destinations themselves.
