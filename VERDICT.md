Fix review: blocked b96aab8b85f167f25ac72ba840ef10095f655229 root-cause-unanswered: closures went red, unanswered

Round 1, the first review of #2554 (R10-ROSTER-OPS's roster-sync deliverable, branch `fix/r10-roster-sync`). I measured head `b96aab8b85f167f25ac72ba840ef10095f655229` (the `ls-remote` re-check before posting found the same head) from a detached worktree, merge base `265d3bf1acc1`. `git diff <mb>...origin/main -- dev/governance/roles/` touches only `orchestrator.md`; I read `fix-review.md` from origin/main.

## Blocking

1. **`closures` is red at this head, and `## Red checks` does not name it.** Check run 119202770035 (SCOPE_CASE full) printed `INERT READS UNDER-APPROXIMATED` for `tests/entities.py: tools/audit/carry_audit.py`, `tools/audit/seat/roster_edit.py` and `tools/audit/seat/roster_sync.py`. `closures-autofix` (119216792955) then reported `AUTOFIX: skip-merge-failed -- THE REPAIR DID NOT HAPPEN`, so no bot commit is coming. The cause is this diff. `state_docs.py`, which `tests/closure.py`'s exception list moves out of the INERT `tools/audit/` prefix because entities.py loads it, now imports `roster_sync` and through it `roster_edit` and `carry_audit`. None of the three was added beside `ref_privacy.py`, which is the exact precedent at closure.py:765 (#2310). The consequence is a real gate hole as well as a red check. With a one-line plant in `roster_sync.py`, `tests/closure.py select --diff HEAD` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, even though entities.py executes that file (ev/underscope-plant.txt). Both red runs concluded before `pr-contract` 119217234807 started (12:18:32 against 12:19:20), and that run checked the body. Carry: dismissed: owed by this pull request's next round (item 8fac8b5b)

2. **`pr-contract` is red at this head**: `BAD-DEST body item b79e7e68` and `00bf85b5`: `R10-ORCH-MACHINERY is not a group of the roster`, `CARRY-AUDIT: 4 finding item(s): 2 routed, 0 unrouted, 2 bad destination(s)`. The head's tree roster, at merge base 265d3bf1a, has no `R10-ORCH-MACHINERY`. origin/main (57f0c9c77) and the live `handoff/audit-r10-roster` (23ef06dc6) both have it, so merging main should clear this. It is still red on the head under review. Carry: dismissed: owed by this pull request's next round (item c0223ec1)

3. **Forward-carry not on the roster (step 10).** The two `## Forward-carry` findings appear on the live roster at 23ef06dc6 under neither destination: `ci_predict.py` does not run the layout guard (to R10-ORCH-MACHINERY), and `ref_privacy --check` ignores `\b` on a macOS seat (to R10-POLICY-GATE-SCOPING). I searched every group's `carry` for `ci_predict`, `ref_privacy`, `cloud_dispatch` and `2554` (ev/forward-carry-on-roster.txt). The only matches are older items from #2441 and #2447 on R10-CI-LAYOUT, which are not these findings. The body names no roster SHA. Class `carry-missing: not carried to R10-ORCH-MACHINERY, R10-POLICY-GATE-SCOPING`. `roster_sync.py` would append the items only after the merge, and `finding-propagation.md` requires them in the brief before it. Carry: dismissed: owed by this pull request's next round (item 4ddebe42)

4. **The group's design trace is not disposed (step 9, `harness: design-trace-missing`).** R10-ROSTER-OPS's roster `carry[3]` and the approved design (`handoff/orch-machinery` 09174d94, DESIGN.md section 6.4) assign three predicates to "the roster-sync step this brief requires", and say "this group is their one owner". They are (1) gate coverage, class times mandate scope; (2) absorbed-edge closure, `ABSORB-EDGE-MISSING`; and (3) commit resolution by prefix with `git rev-parse --disambiguate`, `RECORD-INVALID`. `carry[4]` (from #2545) adds a brief pinned at handoff and compared on a later pass, which also belongs to the 6.4 roster-sync step. `roster_sync.py` implements none of the four: a grep for `absorb|mandate|budget_raise|disambig|RECORD-INVALID|GATE-READY` finds only `absorbed` in `PROTECTED_STAGES`. The body cites 6.4 for B13 and B11 only and dispositions none of the four. I found no waiver from tvofi. R10-ROSTER-OPS is now `done` on the roster at `929275e8`, so after this PR merges nothing owns them. Each needs building here, or an explicit disposition with a live destination. Carry: dismissed: owed by this pull request's next round (item b1ecb708)

5. **A sibling group's pull request decides another group's stage (a step-6 attack at a configuration the harness accepts).** `matches()` applies B13's `name.startswith(topic + "-")` arm, and `derive()` lets one pull request decide every group whose topic is a prefix of its head. My probe (ev/sibling-probe.txt, run against this head's `roster_sync.derive`) gives two results. First, a merged `fix/r10-stale-paths-2` moved **both** `R10-STALE-PATHS` and `R10-STALE-PATHS-2` to `done` at the same commit (`caseA_misattributed=1`). Second, an open `fix/r10-deeplink-census` moved the **done** `R10-DEEPLINK` back to `in-progress` (`caseB_done_reopened=1`). The live roster at 23ef06dc6 has 3 such prefix pairs: DEEPLINK/DEEPLINK-CENSUS, DEEPLINK/DEEPLINK-HANDLERS and STALE-PATHS/STALE-PATHS-2 (ev/topic-collisions.txt, `topic_collisions= 3`). All six groups are `done` today, so the live harm right now is case B: any new open PR on a `-2`, `-census` or `-handlers` branch reopens a settled group. The fixture never plants a sibling pair. The brief says the step "derives only what the repository measures", and a sibling's merge does not measure this group. The fix is to prefer the longest matching topic, or to exclude a head that another group matches more specifically, with a sibling-pair arm and a mutant. Carry: dismissed: owed by this pull request's next round (item bf644354)

## Mutation proof (step 1)

The fixer's driver reproduces the body's table exactly: `NULL_no_plant rc=0 fails=0`, and M1–M5 `rc=1 fails=2`, M6 `rc=1 fails=1` (ev/fixer-mutants.txt). My own plants against `roster_sync.py` (ev/reviewer-mutants.txt, driver `tools/rev_mutants.py`, reviewer-built):

- RESULT mutant=NULL rc=0 (34 checks, 0 failed)
- RESULT mutant=R1_done_rerecorded rc=1 (a crash, not a named check)
- RESULT mutant=R3_pr_number_not_written rc=1 (named)
- RESULT mutant=R7_open_beats_merged_flipped rc=1 (named)
- RESULT mutant=R2_exact_match_only rc=0 SURVIVES
- RESULT mutant=R9_suffix_not_stripped rc=0 SURVIVES
- RESULT mutant=R6_carry_dedupe_dropped rc=0 SURVIVES
- RESULT mutant=R8_issue_dest_appended rc=0 SURVIVES
- RESULT mutant=R5_closed_decides rc=0 SURVIVES (equivalent in effect: a closed PR has no merge commit and is skipped)

Unpinned behaviour, non-blocking on its own: R2 and R9 survive because the only positive fixture, `fix/r9-live-pr`, matches through either arm, so neither the `<topic>-` arm nor the `-pr` strip is pinned alone. R8 survives because "only a group token is appended" has no issue-destination arm, and R6 because no fixture repeats a carry. The rc-path `_reset` is unpinned too, though the exception-path reset is pinned (ev/R4b-all-resets-removed.txt). Carry: dismissed: owed by this pull request's next round (item d470e3e7)

## Figures re-measured at this head (step 8)

Every figure below reproduces (ev/figures.txt, ev/roster_sync-selftest.txt, ev/other-selftests.txt):

- `roster_sync self-test: 34 checks, 0 failed`, `roster_edit self-test: 64 checks, 0 failed`, `state_docs self-test: all checks passed` Carry: dismissed: confirmed at this head (item d78658d3)
- base harness: `RESULT base_apply_rc=2 head_apply_rc=0`, `base_stage=in-progress head_stage=done`, `head_noapply_stage=in-progress`, `base_deferred=deferred head_deferred=deferred`, `control=PASS` Carry: dismissed: confirmed at this head (item 64862426)
- `selftest_wiring: 38 self-testing, 38 wired, 0 unwired`; `tmp_paths: 0 refused`; `layout: GUARD: 0 refusal(s)`; `AGREEMENT ok` with `unregistered=0`; `STRUCTURE RATCHET PASSED`; `claims hygiene: origin/main ok` Carry: dismissed: confirmed at this head (item 8922b477)
- `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (RUN entities.py, harness_headers.py). It now counts 9 changed files against the body's 8, because the delivery row is included. Carry: dismissed: confirmed at this head (item 63503396)

From CI, not re-run by me: `instrument-self-tests`, `arch-score`, `coverage`, `mutation` and `fast (3.14)` are all green. `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (step 5). No golden or claim file moved (step 4). `git merge-tree --write-tree origin/main <head>` exits 0, with `LEDGER-MERGE: resolved tests/closures.json` (ev/merge-tree.txt). Carry: dismissed: confirmed at this head (item 96349e06)

## Notes

- `nightly-status` is red, but it grades main (the replay `loop_cpu_ratio` budget), and the body routes it correctly. Carry: R10-REPLAY-CAP (item 57bf9e90)
- `roster_sync.py`'s docstring keeps the "2 of the live roster's 48 merged groups; this one finds 47" count. The body withdrew that count as not re-taken, and the docstring cites the design as `dev/audit/machinery`, while the file is `dev/audit/design/orch-machinery/DESIGN.md` on `handoff/orch-machinery`. Carry: dismissed: owed by this pull request's next round (item 5ed82be8)
- No committed finder harness exists. The finding is the owner's brief, and `r10_roster_sync_base.py` is the fixer's own. I measured with it and with my own probes, which I disclose here: `rev_mutants.py`, `sibling_probe.py`, the closure plant and the topic-collision count. They are evidence under `ev/` and are not landed. Carry: dismissed: reviewer probes, evidence only (item 2dcbe60e)
- In this seat, `gh` was unauthenticated (`GH_TOKEN` invalid), the job-log blob download returned 403, and `python3` was the system 3.11. I read logs through the MCP job-log tool. This is the same payload-environment drift the body's Friction records. Carry: R10-ORCH-MACHINERY (item 4c5f0868)

bus-nonce: 2c937958e5f677f2c0d4fd6424652617
