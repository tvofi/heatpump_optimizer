Fix review: blocked 321d7f9f34526984b5eca8d18870cd14cffbe6f6 mutation-vacuous: ceiling-value-key, produce-prior-round, groups-json-round, groups-json-stage, groups-json-kind, groups-json-write, plans-json-write, baselines-ref, register-ref

bus-nonce: 6834d873547e825b894a72b50f2e0739

Round 1 of review for #3658 (first round; no earlier verdict).

## Block

The 16 mutants the body names are all killed (verified), but the half of the change that feeds the two reads in production has no case. With `tools/audit/seat/mutant_run.py --spec` at this head, running `python3 -I tools/audit/seat/round_metrics.py --self-test --no-mutants` (NULL SURVIVED, as required), these mutants of added lines in `tools/audit/seat/round_metrics.py` survive. Each one is a whole token named below:

- ceiling-value-key: `main`'s `closure_slip_ceiling` read with `.get("value")` dropped. `cap` becomes a dict, and `report --round` raises `TypeError: '<=' not supported between instances of 'float' and 'dict'` once a round has two forecast pages after its register. Demonstrated with a two-page plans.json for round 11: the head prints `closure_slip 2.00 days per day (...; ceiling unset, undecided; ...)` and the mutant raises. No case drives `main --round` past the slip read.
- produce-prior-round: `produce` scans only round N's plan history, not N-1's. The body's claim that rounds N-1 and N are cached is unpinned.
- groups-json-round, groups-json-stage, groups-json-kind, groups-json-write: `produce`'s `groups.json` writer, where each field is blanked or the write is dropped. Under groups-json-stage, the count of groups at the deferral stage beside `closure_slip` reads 0 for every round, silently. With the PR's own formula on the real `handoff/audit-r10-roster` it is 8 for round 10. Under groups-json-kind, every unexamined merge reads `unkinded`. The cases write `groups.json` by hand and never read the producer's output.
- plans-json-write: `produce` drops the `plans.json` write. Then `closure_slip` is unread forever in production, and the cache that is meant to outlive the state ref's deletion never exists.
- baselines-ref: `round_baselines` greps `HEAD` instead of `origin/main`. This is equivalent in the fixture only because the fixture points `origin/main` at `main`.
- register-ref: `plan_history` takes the register from `--all` instead of `origin/main`. A `JUDGE.json` first added on a branch would then set the register early. The fixture has no such branch.

What the repair needs: a producer case that runs `produce` (the fake paginator already exists for the API half) over a fixture repo with a `wave-r<N>` roster carrying kind and `resume.stage`, and state refs for rounds N-1 and N. Then assert `groups.json` and `plans.json` field by field, and a `main(["report", "--round", ...])` case with an `objective.json` whose ceiling is set and one where it is null. Put each new predicate in `MUTANTS`.

Also disclose in the same repair, since it decides how `closure_slip` compares across rounds. Summing only later moves makes the read depend on how often the plan page is committed, not only on the forecast's path. On round 10's real history (register 1792054747, 563 forecast pages), the same series reads 2.57 days/day from all pages (37.08 later over 14.43 days), 1.52 from the last page per 6 h (59 pages) and 1.22 from the last page per 24 h (16 pages), against a net +15.24 days. `thresholds.band_closure_slip` (proposed 0.2 relative) would read a cadence change as a move. The instrument page or the read should state this, for example by printing the page cadence beside it or reading at a fixed cadence. Cadence measurement: ev/cadence.txt.

## Evidence

- Head: `git ls-remote origin refs/pull/3658/head` returns 321d7f9f34526984b5eca8d18870cd14cffbe6f6, the head reviewed. The body's `## Head` names it. ev/HEAD.txt.
- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Merge: `git merge-tree --write-tree origin/main 321d7f9f34526984b5eca8d18870cd14cffbe6f6` returns rc 0 (tree 95d9aac62b46825f57823a859ef43200bde3c38b). No conflict.
- Self-test at head: `python3 -I tools/audit/seat/round_metrics.py --self-test` returns rc 0. It prints 81 `ok` lines, 39 of them `mutant killed` (the 23 existing plus the 16 new), and `round_metrics self-test: ok (with mutants)`. This matches the body's figure. ev/selftest-head.txt.
- Reviewer mutants: ev/spec1.json with ev/mutant_run-spec1.txt, and ev/spec2.json with ev/mutant_run-spec2.txt (both `mutant_run.py --spec`, run from a worktree at the head). Killed: newest-from-window, unexamined-window, closure-seconds, plan-sort. The survivors are listed under Block.
- Real-data run (finder's harness: none committed, see the Findings carry; these runs are mine): `plan_history` on `origin/handoff/audit-r10-plan` (tip ef9c90680b) reads 564 page commits with 1 null. That null is commit 94205a821c, whose page is a genuine `UNAVAILABLE — 1 plan violation(s): freshness`, so the regex matched every forecast page. Round 11's register is None (no `dev/audit/rounds/round11/JUDGE.json` on main). `report --round 11` with an empty dir prints both new lines `unread`, as the body's null control states.
- Claims, VERSION: the three-dot diff touches 4 files (`dev/programme/delivery/3658.md`, the instrument page, `round_metrics.py`, its self-test). No golden fixture, no claim file, no `VERSION`, manifest or notes heading.
- Figures not re-derived by me: `tests/structure.py` `STRUCTURE RATCHET PASSED`, archscore `dS +0.0000 NULL` and `MODE: SCOPED -- 0 script(s) run`. These are CI's checks, which were pending at this head. The block does not turn on them.
- CI: `merge_train.py classify 321d7f9f34526984b5eca8d18870cd14cffbe6f6 --pr 3658` printed `WAIT 321d7f9f34526984b5eca8d18870cd14cffbe6f6 pending: gate red: none` at every poll from 17:56Z to 18:00Z (ev/classify.log). I stopped polling once the block was established. No red, so no `## Red checks` answer is owed.
- Body carries: carry_audit at the head reports 2 routed items, 0 unrouted.

## Findings

- No committed finder's harness for `closure_slip` or `unexamined`. The real-data runs above are the reviewer's, against the live state refs. The repair's producer case would serve as one. Carry: dismissed: answered by the block's repair, same pull request
