Fix review: merge 6a10b7e26fdf20b958fd31068b46bcef0f09ee1c

Fix review: merge 6a10b7e26fdf20b958fd31068b46bcef0f09ee1c

Measured at the head; re-read before posting — `origin/fix/r9-fr-2`, the PR head and the worktree agree on the SHA.

- **The arm**: range is `merge-base(origin/main, HEAD)..pr_head_ref` (step 7b's rule; no `@{u}` anywhere in the derivation); `REDS_JQ` matches `pr-contract.yml`'s "List the red checks at this head" key verbatim (completed + failure + name != pr-contract, `sort -u`); one `--red` per name into the same `body_check` — `policy_lint.mjs` is untouched, so the nightly/delivery exemption stays where it lives. Every visibility boundary (gh absent, no credential, non-GitHub remote, no merge base, nothing pushed, no check runs, read failure) returns rc 3 and prints its skip line.
- **Head-only mutant (`rev-list -n 1`), killed by me**: 159 passed, 3 failed — the unanswered-red row goes green, which is the #1860 defect. Restored; worktree clean.
- **Self-test at head: 162/0. Failing-first at 68b1c5f86: 148/14** — all fourteen new rows fail, pre-existing rows green.
- **Stats re-run** (`policy_lint.mjs --stats --since v6.7.16` with a token): 1 merged pull request, `root-cause-unanswered` 1/1, `WOULD OPEN: 0`, `GAP: 0` — body figures confirmed.
- **Closure**: `MODE: SCOPED -- 0 script(s) run, 30 scoped out.` Diff scope is prepr.sh + fixtures only; no production code; VERSION/notes untouched; no claim files moved.
- **Body**: armed `Closes #1860` in prose, the only armed keyword; `pr-contract` passed at head over this body (its log shows the red list `nightly-status` and the armed close), so CI saw the armed form; template headings present; `_Requested by **tvofi**_` first line; `nightly-status` answered in Red checks under the standing exemption (diff touches no reporter input).
- **CI at head**: only `nightly-status` red (main's); CodeQL python in progress, not red.
- **CODEOWNERS**: `tools/audit/prepr.sh` is under the pinned, unowned `tools/audit/*.sh` set; the fixtures are unowned — no owner review is owed beyond the approver App's.
- **merge-tree origin/main..head**: clean.

Evidence: `evidence/` on review/1891; head named in `evidence/head-6a10b7e26.txt`.

Evidence (absolute): /Users/timmalmstrom/hpo-orch/notes/rev1891/ — local copy of review/1891's VERDICT.md and evidence/ (reviewer push d659a0461); measured head 6a10b7e26fdf20b958fd31068b46bcef0f09ee1c.
