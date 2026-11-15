Design review: revise df3267eba7d6e70490afcbdb8aa1802dc0a0c14d class-open

Judged at base e75ad291ff5c58f7c8362b0a20fbe6b230adf717. The note names e0ad8b2bd3 and calls it origin/main. It is now three merges behind (#3612, #3619, #3621). Over the files the note names, `git diff e0ad8b2bd3 e75ad291ff` changes `merge_pr.sh` (+157), `merge_train.py` (+52) and `governance.yml` (+14). It does not touch `scorecard.py`, `scorecard_selftest.py`, `gate.py` or `stamp.py`. Line numbers below are at e75ad291ff. This is round 3 of 3.

## Round-2 points

R1 is answered. The 20-run window now has one owner, `scorecard.py` `line_a` (`:102-111`), with one input (the beat cache) and one unread rule. The single-run reader is a read-only flag of the stamp, and invariant (vii) forbids a second window. I checked the claims at the base:
- The shortcut is at `:106`.
- There is no GitHub call (`:8-10`).
- `merge_train.py:629` loads `gate.py` by path.
- The self-test anchors hold: `cases` `:38`, the report-length assertion `:146`, and `MUTANTS` `:157-170`.
- `ci.yml:212-215` calls `governance.yml` as a reusable workflow, so `governance / instrument-self-tests` is in the cached CI run listing that A_mach reads.

Notes dr6 to dr10 each have a row or a carry.

## Revise point

1. class-open: design.md:113 (row `merge_train.py` `outside_is_mains`), and design.md:91-92 (the last alternative). Both are anchored on a blast radius that no longer holds at the base. #3619 (436ee9878e and the `fork_head` change) added two comparisons of the checkout's copies against origin/main's blobs that run for every pull request, ours included:
   - `merge_train.py:2676`: `fork_head` calls `self.outside_is_mains((OUTSIDE_PATH,))` before the pull read, and the train calls `fork_head` for each item (`:2761`, `:2938`, `:2953`, `:3366` and others).
   - `merge_pr.sh:147`: `outside_is_mains outside` runs before `head_is_ours`. Its `contract` arm (`:64-79`, `:151`) mirrors `OUTSIDE_MAIN_COPIES`.

   Under the pin, the train and the hand-merge launcher run from a checkout at `toolchain/stable`. The design moves `merge_pr.sh` there in design.md:112. After any merge that changes `tools/pr/outside.py`, both would therefore refuse every merge until the next promotion, not only outside pull requests as design.md:113 states. `git log --oneline --since=2026-10-15 e75ad291ff -- tools/pr/outside.py | wc -l` prints 7. Promotion is gated on machinery green and holds with `PROMOTE-HELD`, so a machinery-red main would also stop all merges. That couples merge flow to machinery status, which is what the ruling separates. Your section 4 enumerator also misses the bash site: its pattern `origin/main:\{?(rel|tools)` does not match `"origin/main:$rel"` (`merge_pr.sh:75`).

   Fix wanted: add both sites to section 4 with a disposition. One option is that the train and `merge_pr.sh` execute outside.py and the contract copies from origin/main's blobs, read with `git show` into a scratch path. That keeps `outside_is_mains`' rule ("origin/main's blob or none") and removes the dependence on the checkout. The other is to keep the checkout comparison, state the all-merge stop with its enumerator, and route it as `decision: owner`. Either way, correct design.md:113 and :91-92, and widen the enumerator to the `$rel` form. By the contract this is the third note, so if you re-cut to the minimal shape, this point can become p1's first acceptance row.

## Notes for the fixer

- A run whose conclusion is success can contain `skipped` jobs. The shortcut at design.md:47-48 counts it green in A_mach without reading its listing, while the function calls a member that is absent or did not finish "unread". State whether `skipped` is green, unread or out of scope for the machinery tuple, and add one self-test case. Carry: R11-PRE-TOOLCHAIN-PIN (item dr11)
- `design/R11-PRE-STANDING-SCRIPTS` has moved from d1a4ae6a74 to 375ce7ff3f. Its part 1 moves `orchestrator_tick.py` payloads into a new module ("move only"), and its row 1 serialises `beatd.jobs.json` against this group. The dr9 row (an edit of the existing `:1846` count only) still holds. Re-anchor `:1846` after its part 1 merges. Carry: R11-PRE-TOOLCHAIN-PIN (item dr12)
- #3612 (R11-PRE-ROUND-METRICS p1) merged at 66865be375 and leaves `scorecard.py` unchanged. The `after` edge at design.md:171-173 still applies to the part that builds the cache producer. Carry: R11-PRE-TOOLCHAIN-PIN (item dr13)

## Routed decisions (unchanged; no revise point)

- decision: owner: the `main_green` question, who may push `toolchain/stable` and whether a ruleset protects it, and whether decision 0018's `product_green` moves to A_prod (design.md:210-212).
- decision: orchestrator: the A/B/C split (design.md:205-209), and the `after` edge on R11-PRE-ROUND-METRICS (design.md:173).

## Checked and sound

- `gate.py` at the base: `PUSH_ONLY` `:69`, `PUSH_REPORT_ONLY` `:74`, `REQUIRED["push"]` `:94`, `machinery_line` `:293`. This matches section 2's before-state.
- `merge_pr.sh` sources `pr_args.sh` only inside the self-test bound (`:23`). Its argument parse is now at `:490`, not `:359`, so re-anchor design.md:112.
- The open `design/*` refs I checked (OUTSIDE-ROOMS-P2, OUTSIDE-HONEST-STARTS-RUNS) do not name `outside_is_mains`, `merge_pr.sh` or `toolchain`.

Tokens: this seat's count is not reported by the harness; no subagents.
