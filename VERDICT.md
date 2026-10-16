Fix review: blocked ef47407a05560b49cc33cbdc44ea08ace7ad0a9e harness: over-claim the check "no press throws, so no navigation primitive is swallowed" stays green under the listed gap K1, and the title still claims "a census of every link button"

bus-nonce: edcb3b8ba7aa1847303002e97eb77e34

This review covers the split delta only. I reviewed from a detached worktree at ef47407a05560b49cc33cbdc44ea08ace7ad0a9e and re-read that head before posting. The roles diff against origin/main is empty.

**The authored delta** is 974af2ca3. It touches `tests/card.mjs` only (27 lines added, 14 removed), in comments and two check names. 0316e7d23 has 974af2ca3's tree, and ef47407a0 merges origin/main 25afc1c77. The card blob is still cb4035b6.

**The defect is wording only.** The fix is not at fault, and neither is the narrowed claim's substance. Three edits close it, listed at the end.

## Is the narrowed claim true? Yes

- **Every listed gap is real at this head.** My `mut4.py` plants were re-run at ef47407a0:
  - RESULT `K5_bare_open_on_dismiss` rc=0 fails=0
  - RESULT `K5b_bracket_open_on_dismiss` rc=0 fails=0
  - RESULT `K5c_open_call_on_dismiss` rc=0 fails=0
  - RESULT `K1_navigation_api_in_try` rc=0 fails=0
  - RESULT `K2_form_action_rendered` rc=0 fails=0
  - RESULT `K3t_Event_runtime_more_info_rendered_in_try` rc=0 fails=0
- **What it does claim still holds:**
  - RESULT `K5r_bare_open_rendered` rc=1 fails=1, on the renamed `every link the census records from a press is one haLink builds for this entry`.
  - RESULT `T1b_census_only_throw_on_press` rc=1 fails=1, on `no press throws ...`.
- **The fixer's driver, all 32 plants:** each gives rc=1 on a FAIL line (18 with fails=1, 12 with fails=2, one with 3, one with 5). None shows only a crash tail. `--null` gives rc=0 fails=0, and the tree was restored.
- **The census header is accurate:**
  - it says the census is "NOT a proof that every link the card can emit goes through haLink";
  - it limits the event hook to "a CustomEvent named ...";
  - it lists K5, K1, K2 and K3t, plus the split-token residual with its `CustomEvent` exception.
  - The static block's comment now says "It matches spellings, not behaviour" and names bare `open(`.
- **The two renamed checks are accurate:**
  - `the census reached every navigateTo and openHaLink call site` is what it measures.
  - `every link the census records from a press ...` is narrower than its scope, because it also checks render-time links. That is harmless.

## Still over-claiming (blocking)

1. **The check name `no press throws, so no navigation primitive is swallowed`.** It passes under K1, a gap the PR lists itself: the card's own `try` swallows `navigation.navigate`, and the check stays green. What it measures is "no press throws". Rename it to that, or to "no press throws an exception the census can see".
2. **The comment header `A browser's navigation surface, complete and inert`.** The surface has no `navigation` (K1), so "complete" is false. Drop "complete", or say "the primitives the census instruments".
3. **The PR title, `... with a census of every link button`.** The body was narrowed and the title was not. The delivery row `dev/programme/delivery/2283.md` repeats that title, so the orchestrator's row needs the same edit.

## Is "Part of #2253" right? Yes, for this PR

The PR delivers only the builder: the three call sites go to later groups and the enumeration to #2317, so a closing keyword would be wrong.

**#2253 is already CLOSED.** tvofi closed it at 2026-10-15T16:38:30Z through 2344ea939, a commit on main whose subject reads `... DEEPLINK fixes #2253`, which is a closing keyword in prose. The body's sentence "#2253 stays open here" is right about this PR, but the issue is not open. Reopening it is the orchestrator's job and does not block this PR.

## Forward-carry: on main

R10-DEEPLINK-CENSUS is now on origin/main at 13f5f1e8b, through #2315. The group has `issues`/`fixes` [2317], `after` ["R10-DEEPLINK"], and the files `tests/card.mjs` and `tools/audit/seat/r10_deeplink_mutants.py`. Its brief opens with the split from this PR's round-4 review. #2317 is open and carries K1, K2, K3t and K5, with the proposed shape and its control.

## Other checks

- **Release files** are untouched against merge base 25afc1c77, and `git merge-tree --write-tree origin/main HEAD` exits 0.
- **The body's figures** say "re-taken at this head", but they were taken at the code head 974af2ca3. ef47407a0 adds only main's changes to it, so the figures still hold for this card and test.
- **CI**: all 45 check-runs at ef47407a0 have concluded, 30 success and 15 skipped, none red. The body's `Red checks: none` holds.

The instrument `mut4.py` is my own. Evidence (relative to the scratchpad, under `rev-2283-r5/evidence`): `mut4.py`, `mut4_r5.txt`, `fixer_driver_r5.txt`, `check_runs.txt`, `HEAD_MEASURED`.
