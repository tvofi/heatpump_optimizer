Fix review: blocked 737823acd1b143311e19d4b8ac5066100d136ccc carry-missing: not carried to R10-ADVISOR-STEADY-START

bus-nonce: fa66ced039f603714294f037e0cfffcf

Round 3, a delta review over the reviewed head 338c53d77a7a171bcbb04b554bb7bc1d07a9ecec (the merge verdict on probe/rev-3481-e5d5e223 at 058ae4dac). Measured head 737823acd1b143311e19d4b8ac5066100d136ccc, still refs/heads/handoff/r10-advisor-steady-start when this was written; the body is BODY.md at handoff-body/r10-advisor-steady-start 07985b1316929a0d423e578a7cd0283f4380b3ad. The code delta (`git diff 338c53d7 737823ac`) earns the merge verdict: every check on it below holds. The block is on the body alone.

## Block

fix-review.md step 10 and finding-propagation.md's Enforcement ("the producing PR does not merge until the carry is in the tree"). The body's first Forward-carry item is new since the head the merge verdict names (that round's carry audit counted three items, this body holds four), and it is in no brief or carry:

- Body item 29bbcce6, "The background steady pair breaks the recorded day's cycle-cost budget and needs a ruling this seat cannot make", `Carry: R10-ADVISOR-STEADY-START`. The group's carry list at origin/handoff/audit-r10-roster 4058c036b06f6ec22a17ef81ff43bcbf76cf261e holds eight entries and none names the cycle-cost budget, `cpu_ratio` or the replay lane; neither does its brief. `carry_audit.py landed --body BODY.md` prints `CARRY-MISSING R10-ADVISOR-STEADY-START body item 29bbcce6` and `CARRY-LANDED: 2 missing`, rc 1 (ev/body_carries.txt). The body names no roster SHA for it.
- The second line of that output is body item 5e937702, the real high-spread price day. Its text was reworded this round (it now adds that whether the synthetic day discharges condition 2 is the orchestrator's ruling), so its hash no longer matches roster carries 2 and 5, which hold the earlier wording with the same control. It needs re-landing or its landed wording restored; on its own I would not have blocked on it.

Why the first one matters past the form: the item says `tests / replay` on this pull request and the nightly `slow` lane on main after the merge are red until an owner ruling (re-record the owner fixture's `cpu_ratio` and `loop_cpu_ratio`, or move the cap tile's and the advisor's pair off the per-solve path). The pull request closes #2257, so this group's stage ends at the merge, and the control (the replay triple at the merge base, the head, and the head with `steady=False` at the two call sites) would then exist only in a merged body. I read the own-group destination as fixer.md's pending-owner-ruling exception, as the earlier rounds read the price-day item; the block is that it is not landed, not where it points.

Either settles it, with no code change and no new review of the code delta:
- Land the item in the roster (and re-land the reworded price-day item), and name the roster SHA in the body.
- Or record the owner's or orchestrator's ruling on the replay budget and cite it in the item.

I did not re-measure the replay figures (292.0 at the merge base, 442.8 at the head, 290.1 with `steady` off, budget 332.8); they are the body's. The two call sites are production code the delta does not touch, already under the merge verdict, and `tests / replay` is outside `merge_train.py owed-reds`, so the red itself blocks nothing.

## Findings

No finding beyond the block.

## Evidence

- Setup: `cloud-setup.sh --check` OK; role pack rendered; `git diff merge-base...origin/main -- dev/governance/roles/` empty. No review packet and no CI at this head: no pull request existed for it when the review began, as the dispatch says.
- The delta: `review_carry.py 338c53d7 737823ac` prints `FRESH-REVIEW` (two authored commits, d788f83a8 and 2050adb3b, and their merge with 338c53d77), so this is a delta round (ev/review_carry.txt). `git diff --stat 338c53d7 737823ac`: tests/features.py +72 and fifteen new files under tests/mutation_ledger/ (twelve killed_by, three survivor_triage), 162 insertions, nothing under custom_components/ (ev/delta_stat.txt). No production code moved, so the review is not widened.
- The merge commit resolves nothing by hand: `git merge-tree --write-tree 2050adb3 338c53d7` gives tree 082561cafe, the head's own tree.
- Merge with main: `git merge-tree --write-tree origin/main 737823ac` exits 0 at origin/main 26072317b5556a2baa1ff562d8fbbc9588e2ba5c (tree b6132c695c). The body's `## Head` names an older main; the head merges cleanly with the current one.
- Step 1, mutants, each one edit on a `git archive` copy, whole `tests/features.py` (ev/features_*.log, ev/mutants_summary.txt). The copies have no `.git`, so "stamps a resolvable recorded_at (#363)" fails on every copy and is not counted.
  - RESULT control at the head: 1 of 5340 red, the #363 check only. The body says 5340 on the merged head.
  - RESULT M1, `day = (n_steps)` in `reference_day` (pin CLAMP_DROP cbe42979): red "#2257: an outdoor series under a day prices no day although the prices cover one ... and a two-day horizon prices one day of 96 steps".
  - RESULT M1n, the same edit on d788f83a8, before 2050adb3b lengthened every series to two days: 1 of 5283 red, the #363 check only, so the mutant survives there. The pin is earned by 2050adb3b's change to the check, as its message says, and 5283 is the body's pre-merge count.
  - RESULT M2, `n_steps = (len(series.prices))` (pin CLAMP_DROP b9947f73): the same #2257 check red.
  - RESULT M3, `if hum.size < n_steps:` to `if False:` (pin GUARD_OFF 39006914): red "the horizon's weather, as every solve and reference_day read it".
  - RESULT M4, free heat `> 0.0` to `>= 0.0` (pin CMP_BOUND 362ff97e): the same check red.
  - RESULT M5, `base is None or _whatif_banded(...)` in `async_simulate` (pin BOOLOP 19646b85): red "#1795: the card's what-if on a house that is not away reads the hubs unbanded", detail `([True], False)`.
  - No mutant I ran survived at the head. Not driven by me: the other seven pins (three `_horizon_weather` GUARD_OFF sites, the three operators on `day * dt >= 24.0` and the RETURN_DEL); CI's `tests / mutation-pins` re-drives them.
- The three triaged survivors, read against the code at the head: `<` to `<=` on the humidity pad appends `np.full(0, nan)` at the one input that tells them apart (measured: `[1.0, 2.0, 3.0, 4.0]`); `limited_answer`'s closing `return None` replaced by `pass` returns None; `scratch_copies` with the empty-spec guard off assigns `parse_windows("")` and `parse_weekly_windows("")`, measured `[] None`, the two values the guarded branch assigns, and raises nothing. All three are equivalent as the ledger rows say.
- Step 14: the diff moves the mutation ledger only. `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED; `python3 tools/pr/ci_predict.py` predicts no closures, fast, governance or instrument red against 2ced371c1 and lists no unpinned site, as the body states (ev/checks.txt). No budget, closure, golden or claim file is in the delta.
- Step 5: `git diff merge-base...HEAD -- VERSION manifest.json RELEASE_NOTES.md tests/golden` is empty.
- Step 7: the body's `## Head` is 737823acd1b143311e19d4b8ac5066100d136ccc.
- Step 10, the other carries: `carry_audit.py check --body BODY.md` prints 4 routed, 0 unrouted, 0 bad destinations, rc 0; it checks that a destination exists, not that the text is there. `carry_audit.py landed` with `--topic r10-advisor-steady-start` prints `CARRY-LANDED: 0 missing` on the same body, against `2 missing` without the flag; I read the roster directly and the item is absent (ev/body_carries.txt), and I did not establish why the two invocations differ.
- Step 11: `merge_train.py owed-reds` prints `tests / coverage-ratchet`, `tests / fast (3.14)`, `tests / mutation`, `tests / typing`, `validate / validate-hacs`. No check has run on 737823ac. `merge_train.py classify 338c53d7 --pr 3481` printed `WAIT ... pending: gate red: none` during the review.
- Step 12, the head re-read at return: refs/heads/handoff/r10-advisor-steady-start is still 737823ac. refs/pull/3481/head moved during the review from 338c53d77 to 18b5f950b12b29ea17d256dbeef7d33aeea27561, a merge of 737823ac into the bot's pin commit 40be5b2f7; its tree is 082561cafe, identical to the tree reviewed here. I did not read the pull request's body or the checks at that head (ev/HEAD.txt).
- Not re-run: every harness figure of rounds 1 and 2 (the delta touches no production line and no harness), the replay triple, the scoped gate, the mutation table.
