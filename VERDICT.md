Fix review: merge 6b9e873394a02ec82ec24d23dc454a99418e2366

bus-nonce: f6636253afbf42e1c8ab1f7f1d2bf863

## Round

First review, at the handoff, before a pull request exists. Measured head 6b9e873394a02ec82ec24d23dc454a99418e2366, merge base 005eed2573da9e946fa4838de147401d0ff36cc1; the handoff branch still pointed at that head when this was written (ev/head_readback.log).

## Findings

- A booked episode reads as one fewer a second later: `n` is floored at the reading's time, so five stops at one instant publish 5.0 and 4.0 one second on, and a single fresh stop publishes `p` 1.0 beside `n` 0.0 and `stopped` 1 an hour later (ev/probe_wt-head.log, P4 and P7). It is what the docstring says ("rounded down") and the section pins it, so it does not block; a reader or a person reading the sensor must take the published `n` as up to one under the weight, never as the count of episodes. Control: the mutant rounding to nearest fails three section checks (ev/mut_n_nearest.log). Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B
- The docstring of `published` and the body say age alone moves only `n`; `span_days` also moves with age alone, from 1 to 0 on the pass whose decay takes the weight under `SPAN_FLOOR_N` (ev/probe_wt-head.log, P1: step 13 with the pass's decay, none on reads alone). The behaviour is part A's and already carried as item 90bc5153; only the new sentence is wrong, and the new check's window (one day at a weight near six) does not reach it. The later pull request corrects the sentence. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B
- The approved design's "Published" paragraph and its acceptance item 7 list `k` among the attributes; this head drops `k` and adds `p`, and edits the attribute-set check to match. Carry: dismissed: the roster carry c7d068a1 hands the publication's resolution to this part, the note records the change under its own heading with the approved text unchanged, and part A is in no tag (`git tag --contains 005eed2573` prints none), so no released attribute is renamed
- The three own-group carries that are not the owner's ruling (items 1b22f416, 90bc5153, d088605d) rest on `fixer.md`'s "a split part the approved plan names". The split of this group into two pull requests is named by the dispatch and by the note's new section at this head, not by a plan I could open; I took the dispatch as the plan. Carry: dismissed: the orchestrator's dispatch names this pull request part 1 and the reader part 2, and all six items are already in the group's roster carry at handoff/audit-r10-roster 05faf264002e234f879a805de4006fc16c099818
- The section harness `dev/audit/harnesses/r10_duty_switch_section.py` is part A's fixer's instrument, not a finder's: the group is a feature with no finder. The two probes the roster carries name (`attr_churn`, `fifth_episode`) are part A's reviewer's and are not in the tree by those names; the head rebuilds them as section checks. My own probe is ev/probe.py, the builder's being me. Carry: dismissed: a feature's harness is its design's, the section runs the tree's own checks, and the probes now live as checks in `tests/features.py`

## Evidence

No review packet and no CI exist before the pull request opens: nothing was read from a check run, and no heavy run could be cited. The full scoped gate, the mutation table and `env_drift.py --all` were not run by me.

The factory-reset decision (item 3c666f5b) does not matter before part 2. The diff touches three files (`duty_switch.py`, the design note, `tests/features.py`) and in production only `DutySwitchLearner.published`. The only production reader of the estimate at this head is `sensor.py`'s call of `starts_attributes`, which published `k` and `n` from the same store at the base; `pump_arbiter.py` only writes into the learner (record, mode write, pass, attach, detach) and reads the constant `STOP_WINDOW_S`. Nothing reads `usable`, `p` or `median_off_s` to change a plan or a write.

RESULT harness base 005eed2573: 59 of 59 section checks pass (ev/harness_base.log).
RESULT harness head 6b9e873394: 61 of 61 section checks pass (ev/harness_head.log).

Mutation proof, each applied to the head's `duty_switch.py` alone and restored (worktree clean after):
- RESULT `n` at two places: 3 of 61 fail, the three checks the body names (ev/mut_n_two_places.log).
- RESULT `n` to nearest: the same 3 fail (ev/mut_n_nearest.log).
- RESULT `p` from the decayed `k`: the same 3 fail (ev/mut_p_decayed_k.log).
- RESULT base module under the head's section: stops at `KeyError: 'duty_switch_dhw_space_p'` (ev/base_module_new_section.log).
- Mine: `n` rounded up, 3 fail; `n` undecayed, 2 fail; `p` to one place, 2 fail; `k` still published, 3 fail; `N_ON` 4.5, 2 fail; `N_ON` 5.5, 3 fail (ev/mut_*.log). No mutant survived.

Null controls, re-run:
- RESULT churn: at the head 0 changes across 96 quarter-hour reads; at the base the same reads move `n` (ev/probe_wt-head.log P8; the base's two-place `n` moves daily in P1 of ev/probe_wt-base.log, whose head is cut to its tail; the base run stops at my own whole-step assertion, as it should).
- RESULT spread weights after each of six stops ten hours apart: 1.0, 1.9796, 2.9392, 3.8792, 4.7999, 5.7019, so the fifth is under five and the sixth over (P5). The body's "fails under any N_ON at or under the five spread stops' weight" holds at 4.5.
- RESULT empty learner publishes `{}`; a void-only direction publishes `p` 0.0, `n` 0.0 and a span of 0 (P6).
- RESULT 120 days of quarter-hour passes with decay restamped each time: 29 steps of `n`, each of exactly one, none upward, `p` never moves (P2).
- RESULT read behind the stamp: `n` reads 6.0 a day before the stamp after reading 4.0 five days after it (P3); `weights` is unchanged from the base, so this is not the diff's.
- Flat-price control: not applicable to a quantity here; the diff changes no plan and no write, no file under `tests/golden/` names a `duty_switch_` key (0 hits) and neither claim file is touched.

Figures:
- Scope line re-derived: `MODE: SCOPED -- 22 script(s) run, 11 scoped out.` from `python3 tests/closure.py select --diff 005eed2573`, and `figure_block.py verify` on the body: 1 block, 0 refused (ev/scope.log, ev/figure_verify.log).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc 0 (ev/structure.log). No budget, closure, golden or claim file is in the diff (ev/protected.log), so step 14 has no moved number to earn.
- `env_drift.py --claims-only` at the merge base: ok (ev/claims_only.log).
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched.
- `policy_lint.mjs --pr-body`: 0 errors; `carry_audit.py check` on the body: 4 routed, 0 unrouted, 0 bad destinations (ev/pr_body_lint.log).
- `git merge-tree --write-tree origin/main 6b9e873394`: rc 0 against main 3254c38b14 and again against 4145f28526, to which main moved during the review; no conflict (ev/merge_tree.log).
- `git diff` of `dev/governance/roles/` between the head's base and main: empty, so the contract read is current.

Class: the body states no enumeration rule and the two items are one seam each (`published`, the `N_ON` reading); no other file in the tree outside `tests/features.py` names a published `duty_switch_` key, so no second consumer of `k` exists.

Forward-carry: opened. The note's new section names the items still owed; the roster group R10-DUTY-SWITCH-RESTART-LEARNING-PR-B at handoff/audit-r10-roster 05faf26400 holds items 1b22f416, 3c666f5b, ef5d3875, c7d068a1, 90bc5153 and d088605d, each with its control and a re-measurement instruction, and its brief already rules that n has a ceiling.

## Red checks

none: no check has run on this head, and `policy_lint.mjs --pr-body` records no failure across the range.
