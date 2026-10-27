Fix review: blocked 88b452c6ac61231c83967bd4de148c18f7ee407c predicate-over-fire: `carried_from` refuses on the bare PR number found anywhere in a destination carry, so a destination already holding one finding from PR X drops every other distinct finding from X (measured end to end: a genuine second `Carry:` row lost) and a prose comparison like `beside #2447's` suppresses X's carries
bus-nonce: 2f6de5647d1742d8128e24d78a316309

Head reviewed: `88b452c6ac61231c83967bd4de148c18f7ee407c` -- re-read immediately before publishing; it is still the head, `mergeable: MERGEABLE`, `merge-tree --write-tree origin/main <head>` exit 0. Detached worktree created by me under `~/hpo-seats/r10s6/review-2889/wt`, `git status --porcelain` empty at start and after the mutation proof. Three-dot diff from merge base `a0e7664ea` is exactly two files, +57/-1.

## B1 (blocking) -- the dedupe key is the pull request, not the finding, and it matches prose

**Claim.** The body states "a derived item for a pull request the destination already carries a finding from is refused, not appended". The brief's case (b) requires a carry from the same PR that is genuinely different text and not already in the destination to still append. Measured, it does not.

**Evidence.** `tools/audit/seat/roster_sync.py:390` `carried_from` searches every destination carry for `(?<![\w-])#<n>(?!\d)` and returns the first hit; it never compares the derived row's text, so it cannot tell one finding from another under the same PR. My driver `~/hpo-seats/r10s6/review-2889/driver.py` (mine, disclosed): `b_ii_same_pr_distinct_finding_refused` returns the held text for a distinct finding; end to end, `e_two_rows_one_held` -- two distinct `Carry:` rows to `R9-DEST`, one held -- plans **zero** appends and two refusals, so the genuinely-new second finding is dropped while the pass writes; the null control `f_null_control_both_append` appends both. Live corpus at `origin/handoff/audit-r10-roster`: 52 (group, PR) pairs already hold more than one carry naming the same PR (`R10-ADVISOR`/#2452 holds 5, `R10-ARCH-DOCS`/#2609 holds 4), so "one finding per PR per destination" is false in 52 observed cases. Separately, a carry from another PR whose text reads "a second instance beside #2447's" matches `carried_from(..., 2447)`. Files `ev/predicate.txt`, `ev/corpus.txt`.
Carry: dismissed: the correction belongs in this pull request, so it is not carried to a later stage

**Harness.** My own driver, disclosed as mine (the PR names no finder's harness). It imports the head's `roster_sync` and drives `carried_from` and `carry_plan` against a synthetic roster, and cross-checks the live roster read from the round branch.
Carry: dismissed: instrument is this review's evidence, not a downstream stage's work

**Metric.** Four constructions: (a) duplicate -> refuse; (b) destination holds nothing from the PR -> append; (c) different PR `#1525` vs `#15` -> append; (d) null control -> append; then (b-ii) same PR, genuinely distinct finding, destination names the PR -> **refused**. End to end: 0 of 2 appends with one held, 2 of 2 in the null control. Corpus: 52 same-PR multi-carry pairs of 692 carries; 396 name a PR.
Carry: dismissed: these are the review's measurements, not a later stage's inputs

**Perturbation.** Deleting the six added production lines (the PR's own mutant, `ev/mutation.txt`) reddens exactly three self-test checks and reproduces the live refusal `triage gate: proposal-sourced text cites no triage ruling ... 'the same finding again, where triage P3 gives it. Carry: R9-FROM'; nothing written`; restore is byte-identical and the self-test returns `68 checks, 0 failed`. That pins the duplicate arm. Nothing perturbs the distinct-second-finding arm, because the `R9-FROM` fixture encodes it as a duplicate.
Carry: dismissed: mutation evidence for this review, no downstream destination

**Why this blocks, not a comment.** The brief names this the case that matters and says refusing (b) "turns one livelock into a silent loss of carries, which is worse". The end-to-end measurement is that loss, and the corpus shows the shape is the norm rather than an edge: one PR legitimately routes several findings to one destination, and only the first would survive.

**Shape of the fix (not designing it).** Key the dedupe on the finding, not the PR: require a provenance marker (`From #N` / `Source: #N`) *and* that the derived row is the same finding as the held one (the row's `id`/normalised text), or record the routed finding's origin so the plan can tell which body row already landed. Add a self-test arm for two distinct rows from one PR to one destination with one held, and keep the nested-number null control.
Carry: dismissed: guidance returned in this blocked verdict

## Accepted, with the measurements that decided it

**A1 -- the fix does cure the recorded livelock, and the new refusal happens before the triage gate.** `carry_plan` runs in `sync()` (line 532) and again in `write_roster`'s `edit` callback (line 573); its refusals are printed as `REFUSED Carry:` and never reach `apply_plan`, so `added_texts` never contains the duplicate and `triage_refusal` never sees it, while the remaining appends and every stage change write. The mutant's apply arm reproduces the old abort (`ev/mutation.txt`). Carry: dismissed: accepted measurement for this review

**A2 -- the four cases measure as the brief names them, except (b-ii).** (a) refuse, (b) append, (c) append, (d) append -- all as required; (b-ii), the same PR with a distinct finding, refuses and is B1. Carry: dismissed: accepted measurement for this review

**A3 -- the self-test at this head.** `roster_sync self-test: 68 checks, 0 failed` (`python3 tools/audit/seat/roster_sync.py --self-test`); the diff adds four `check(...)` arms -- two dry-run, two apply -- and the two `R9-FROM`/`R9-FROM-2` fixtures. Carry: dismissed: accepted measurement for this review

**A4 -- the delivery row.** `dev/programme/delivery/2889.md:1` equals `open_row_line(2889, OPEN_ROW_TITLE)` byte for byte, and it is the self-row (no group), correct for a record PR. File `ev/row.txt`. Carry: dismissed: accepted measurement for this review

**A5 -- the change is what it says.** Three-dot diff `a0e7664ea...88b452c6a` is exactly two files, +57/-1 (`roster_sync.py` 56/1, `delivery/2889.md` 1/0); no `VERSION`, `RELEASE_NOTES.md`, manifest, claim file or `*_budgets.json`. File `ev/diff.txt`. Carry: dismissed: accepted measurement for this review

**A6 -- checks and merge state.** 47 check-runs read: 0 failure, 29 success, 9 skipped, 1 neutral, 8 still pending; the body's `Red checks: none` holds, so no root-cause trigger. `mergeable: MERGEABLE`, `merge-tree` exit 0. File `ev/checks.txt`. Carry: dismissed: accepted measurement for this review

**A7 -- the body's figures I re-derived.** `396 of 692 roster carries name a source pull request` reproduces exactly under the body's stated regex; `68 checks, 0 failed` reproduces. File `ev/corpus.txt`, `ev/selftest.txt`. Carry: dismissed: accepted measurement for this review

## What could not be established

- I did not run the CI gate, the mutation table or `prepr.sh`, per the contract's ban on re-running heavy CI and this dispatch's cost bound. Carry: dismissed: not owed by this review
- I did not read the merged bodies of #2625/#2825, so I cannot say which of the two held carries the observed pass matched; the incident's abort is reproduced from the self-test arm, not from the live body. Carry: dismissed: not reachable within this review's cost bound
- Eight check-runs were pending at read; if one later concludes red, the root-cause obligation is separate and this verdict does not answer it. Carry: dismissed: a later red is its own trigger

Evidence: `~/hpo-seats/r10s6/review-2889/ev/` (`head.txt`, `diff.txt`, `predicate.txt`, `corpus.txt`, `mutation.txt`, `row.txt`, `selftest.txt`, `carry-audit.txt`, `checks.txt`, `driver.py`), plus `~/hpo-seats/r10s6/review-2889/driver.py` and `mutation.sh`.
