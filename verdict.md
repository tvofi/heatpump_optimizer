Design review: approve a37706d599ca28414378bda7813068b79fd716d6

Judged at base 31117b1029de63938d949e78dcbcd8f9451e5e33. The note names 98847b99d7. `git diff 98847b99d7 31117b1029 -- tools/audit/seat tools/pr tools/ci tools/release .github .claude/hooks` touches only `tools/pr/ci_predict.py`, which the note does not name, so every anchor below holds at both. This is round 4, the re-cut after round 3 of 3: the round-3 point [R3] is p1's first acceptance row, and [dr11]..[dr13] are carries.

## Round-3 point [R3]: answered

- Seat (design.md:21, :48-60): one owner. `merge_train.py` owns the mirror, `_outside_gate` and `outside_is_mains`. `merge_pr.sh` gets the mirror root from a train verb, as it already reads the train's constants (`merge_pr.sh:67-71`). Checked at the base: `_outside_gate` loads `ROOT / OUTSIDE_PATH` (`merge_train.py:1264-1274`). outside.py resolves every code input from its own `ROOT = parents[2]` (`tools/pr/outside.py:75`): `load_gate` `:91-97`, `carries` `:138`, `policy_patterns` `:152`, `gate_files` `:166`. Its data reads go through `show(ref, …)` `:130-132`. So loading outside.py from the mirror makes all of its code main's, and design.md:55-57 is correct. `app_approve.sh:166` resolves `gh_read.py` relative to itself, which is the alternative's argument at design.md:97-99.
- Shape: merge flow no longer depends on promotion or machinery status (design.md:60). This removes the all-merge stop that round 3 named, and design.md:95-96 states why the owner-routing alternative loses.
- Sibling sites: I ran the widened enumerator (design.md:71) at the base. It now matches `merge_pr.sh:75` (`"origin/main:$rel"`). Every hit is either in the section 3 table (design.md:77-84) or in the dismissed list (design.md:86-90). I also grepped `pr/outside\.py|OUTSIDE_PATH|outside_is_mains` across `tools .claude .github`. The one executor the note does not list is `bus.sh adopt` (`bus.sh:370-387`, `:405`). It already runs outside.py from a throwaway worktree at a freshly fetched main, so the pin does not reach it. No site is missing.
- Evidence plan (design.md:108-109): the failing tests fail on today's code. `fork_head` calls `outside_is_mains((OUTSIDE_PATH,))` at `merge_train.py:2676`, which raises a Stop when the checkout's copy differs (`:2716-2720`). The `FAKE_STALE` rows at `merge_pr.sh:284` and `:288-292` expect `OUTSIDE REFUSE` today. The null control (an unmovable mirror Stops by name) would move under the perturbation that round 3 named. No harness of a finder applies (owner ruling on a process audit).

## Round-3 notes

- [dr11] answered (design.md:34-38). `gate.py:245` already reports a skipped required job as `SKIPPED` in `bad`, so a run concluded success never holds one. The self-test row at design.md:111 asserts that the shortcut equals the function.
- [dr12] and [dr13] are carried (design.md:137-140).

## Sibling designs in flight

I scanned every open `design/*` ref for `outside_is_mains|_outside_gate|OUTSIDE_MAIN_COPIES|merge_pr.sh|toolchain|fork_head|pr_tools_fresh`. Only two match:
- `design/R11-PRE-SHARED-FILES` (20cafac7df, design.md:168) carries its stale-checkout half to this group, consistent with design.md:82 and :122-123.
- `design/R11-PRE-STANDING-SCRIPTS` (375ce7ff3f) touches none of this seam, consistent with [dr12].

## Notes for the fixer

- The mirror is one mutable worktree that two processes move: the train and `merge_pr.sh` through its train verb. If one moves it while the other is between `_outside_gate()`'s import and outside.py's later reads of `ROOT` files (`app_approve.sh --carry` `:138`, `policy_lint.mjs` `:152`, `closure.py` `:166`), one contract run can mix files from two main shas. Serialise the move and the run under one lock, or follow `bus.sh adopt`'s precedent (`bus.sh:375-386`): a throwaway detached worktree per call at the fetched sha. Either way, one self-test row should move the mirror mid-run. Carry: R11-PRE-TOOLCHAIN-PIN (item dr17)
- The train's own `_mandate_gate()` (`merge_train.py:1277-1290`) still loads `budget_raise_gate.py` from the checkout, which will be at `toolchain/stable`. That is outside the outside contract, which loads its own copy through `load_gate(root)`. Once [dr15] removes `GATE_PATHS[-1]` from the compared set, state in the instrument doc that the train's mandate reads are the stable ref's. Carry: R11-PRE-TOOLCHAIN-PIN (item dr18)

## Routed decisions (unchanged; no revise point)

- decision: owner: the `main_green` question; who may push `toolchain/stable` and whether a ruleset protects it; whether decision 0018's `product_green` moves to A_prod (design.md:125-126).
- decision: orchestrator: carries 3, 4, 5, 6 and 8, and the A/B/C split (design.md:124-125).

Tokens: this seat's count is not reported by the harness; no subagents.
