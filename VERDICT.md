Fix review: blocked 1f6ea62fd0345ac0759997621fffe315ea11b139 mutation-vacuous: net-all-pages

bus-nonce: fc42609dfe13e7214fa00e623094f1d0

Round 2 of review for #3658. This is a delta review over the reviewed head 321d7f9f34526984b5eca8d18870cd14cffbe6f6. The PR's own delta is ba18cacb13 and 411d996cdd. The rest is main merges, which change no file of this PR at the head: `git diff 411d996cdd 1f6ea62fd0` is empty for all three round_metrics files.

## Block

All nine survivors from round 1 are now killed (see Evidence). One new mutant survives, and it reverts a line this delta changed. `slip_line` now prints the net move from the daily samples: `(daily[-1][1] - daily[0][1]) / DAY_S`, where it used `hist` before. The mutant `net-all-pages` puts `hist` back, and the self-test still passes under `--no-mutants` (ev/spec-r2.json, ev/mutant_run-spec-r2.txt).

The two forms are not equivalent. They differ whenever the first sampled day holds more than one page with a forecast. A history of `[reg: +10 d, reg+0.5 d: +12 d, reg+1 d+1 s: +13 d]` prints `net +1.00 days` at the head and `net +3.00 days` under the mutant (ev/net-survivor-demo.txt). The only intra-day case, `closure_slip: read at a fixed daily cadence`, has the same forecast (+10 d) on the first page and on the first day's last page, so it cannot tell the two forms apart.

What the repair needs: a history whose first day has more than one page with different forecasts, asserted on the `net` figure, plus the matching in-file `MUTANTS` entry. If the net is meant to be over all pages instead, then state that and pin it. Either way, the instrument page should say which one it is. The current text says "net move" without saying over what.

## Evidence

- Head: `git ls-remote origin refs/pull/3658/head` returns 1f6ea62fd0345ac0759997621fffe315ea11b139. The body's `## Head` names it. ev/HEAD.txt, ev/merge-roles-head.txt.
- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Merge: `git merge-tree --write-tree origin/main 1f6ea62fd0` (origin/main ef6363d5f2) returns rc 0 (tree 630a6c5ba6). No conflict.
- VERSION, the manifest, the notes heading, `custom_components/` and golden or claim files are untouched in the three-dot diff. The delta has no production code, so the scope stays the delta and is not widened.
- Self-test at head: `python3 -I tools/audit/seat/round_metrics.py --self-test` returns rc 0. It prints 98 `ok` lines and 49 `mutant killed` (39 + 10, as the body states), and ends `round_metrics self-test: ok (with mutants)`. ev/selftest-head.txt.
- Previous findings resolved: my own spec re-spells round 1's nine survivors in a different shape from the fixer's in-file needles. All are KILLED: ceiling-proposed-key, produce-same-round, groups-round-open, groups-stage-wrong, groups-kind-wrong, groups-write-elsewhere, plans-write-elsewhere, baselines-all, register-head. The cadence change is also KILLED under sample-half-day, sample-epoch-days, sample-first-of-day, span-all-pages, later-all-pages and pages-count-hist. NULL SURVIVED. The one survivor is net-all-pages. ev/mutant_run-spec-r2.txt.
- Cadence disclosure (round 1's ask): the code reads at a fixed daily cadence, and the instrument page and the docstring both state it. I re-derived it on the live `origin/handoff/audit-r10-plan` (tip ef9c90680b): register 1792054747, 564 pages with 1 null, and `closure_slip 1.27 days per day (17.60 days later over 13.89 days ..., 15 daily samples of 564 pages; net +14.94 days; ...)`. This matches the body and the instrument page (563 forecast pages, 15 samples). ev/round10-cadence.txt.
- Figures not re-derived by me: the structure ratchet, archscore `dS +0.0000 NULL` and `MODE: SCOPED -- 0 script(s) run`. These are CI's, and they were still pending at this head. The block does not turn on them.
- CI: `merge_train.py classify 1f6ea62fd0 --pr 3658` printed `WAIT ... pending: gate red: none` at 18:56Z and 18:57Z (ev/classify.log). I stopped polling once the block was established. No red, so no `## Red checks` answer is owed.
- Body carries: carry_audit at the head reports 2 routed items and 0 unrouted.

## Findings

- No committed finder's harness for `closure_slip` on real data. The round 10 run is mine (ev/round10-cadence.txt), and so is the body's scratch `r10slip.py`. The producer and report cases now serve as the committed fixture harness. Carry: dismissed: the in-tree producer and report cases now pin the reads; the real-data run is evidence only
