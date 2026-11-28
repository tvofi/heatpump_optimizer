# BLOCKED: r11-late-p2-zone-gate (fixer-r11-late-p2-zone-gate)

Question: R11-LATE-P2-ZONE-GATE merged as #3925 (merge 98541868ad, an ancestor of origin/main ac9045c223) before this dispatch (20e790465e) was cut. Its only open roster item is carry 0063935f, an open-branch port that applies once R11-OWNER-FEATURES-SPLIT (#3940) merges. This group has no open branch and #3940 has not merged, so no port is possible. Should the orchestrator close the carry and move the group's `resume.stage` from `carries-open` to `done`, with the growth below left to #3940's own manifest re-record?

## Measured (2026-11-28T15:10Z, origin/main ac9045c223)

- `git merge-base --is-ancestor 98541868ad origin/main` exits 0. On the roster branch (handoff/audit-r11-roster 8db83c0639) the group shows `resume.stage: carries-open`, `pr: 3925`. On main it still shows `not-started`.
- The carry's port tool, `dev/audit/harnesses/features_freeze.py`, exists only on handoff/r11-owner-features-split (94d05d861c), not on main, so it cannot be run on a branch cut from main.
- `features_freeze.py --check` at 94d05d861c alone: `HOLDS (0 refusal(s))`, exit 0 (the null control).
- The same check on a scratch merge of origin/main with 94d05d861c (merge-tree clean, commit 6a1109c2ca, not pushed): exit 1, with one refusal. It is `lines`: 104990 against the manifest's 104695. There is no new-span refusal.
- The manifest was recorded at cb2026c3, which predates #3925 (`git merge-base --is-ancestor 98541868ad cb2026c3` exits 1). `git diff --numstat cb2026c3 origin/main -- tests/features.py` reads 310 added and 15 deleted, a net of 295. Of that, #3925 (`git diff --numstat 98541868ad^1 98541868ad -- tests/features.py`) adds 130 and deletes 0. #3934 is the only other merge since.

The growth is on main and was not added by a branch the freeze can refuse. It is absorbed by #3940's re-record of `lines` through budget-raise-gate. Carry: R11-OWNER-FEATURES-SPLIT

No code was changed and no handoff ref was pushed.
