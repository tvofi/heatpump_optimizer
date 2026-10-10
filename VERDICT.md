Fix review: merge 466b1be77156734304aad7f991aed193cbe11d38

bus-nonce: a1f8dccf90b2d60b467ca8544b36f33a

Head measured: 466b1be77156734304aad7f991aed193cbe11d38, detached worktree
/Users/timmalmstrom/hpo-seats/r9rev-2070b/wt, seat interpreter (venv-ci 3.14.7)
via tools/audit/seat/shims. The substance is round 1-6's, long-reviewed; this
pass measures the delta from a15508b7a and the head's own checks, per dispatch.

RESULT delta a15508b7a..466b1be77: ZERO files under custom_components/ — no
production change beyond the repair's description. Files: tests/features.py
(+53: exactly the three killing checks — 251 low bound "first step's end",
251 ragged far bound, 264 MIN_ON strict-< twin), one survivor_triage row
(tests/mutation_ledger/survivor_triage/early_cutoff.py/_cycle_guard.CMP_BOUND.ea4781b3.json,
verdict equivalent, reason naming which twin survives), and the origin/main
merge's prestudy evidence + dev/programme/delivery/2109.md + delivery row 2070.md.
early_cutoff.py and coordinator.py are byte-identical to a9b1b48c4's.

RESULT verify_eight.py HEAD "251 CMP_BOUND" "264 CMP_BOUND" "275 CMP_BOUND"
"304 GUARD_OFF" -> "total 6 killed 5 survivors 1"; the sole survivor is the
triaged 264 clock-skew twin; every KILLED is FAIL-line-visible. Matches the
body's ## Mutation proof table arm for arm (evidence/r6-verify2.log).

RESULT census: tests/mutation_table.py --scope changed --base origin/main ->
"MUTATION TABLE REFUSED -- 4612 unpinned site(s) against 4608 at the ratchet
base 969c3a5c8, 4 of them added by this diff", and the ADDED UNPINNED list is
exactly early_cutoff.py:251 CMP_BOUND*2, :275 CMP_BOUND, :304 GUARD_OFF —
the pins the bot's a15508b7a left are intact, and the :264 anchor is disposed
by the committed triage row (evidence/census.log).

RESULT red checks at the head (check-runs API): exactly one completed red,
`mutation` — named and answered under ## Red checks (cheaper detector: the
deterministic census, standing cost stated; the pinning is the canonical Linux
drive's at this head). pr-contract, arch-score, fast, nightly-status all green
at this head. `mutation-pins (1)`, `closures`, `coverage` were still
in_progress when read; `mutation` is the body's stated expected red pending
that drive (evidence/checkruns-head.txt).

RESULT corroborated figures: tests/structure.py -> STRUCTURE RATCHET PASSED
(seam_cut_total 762 <= 762); archscore --diff origin/main HEAD -> dS -0.0006
WORSENS (coord_footprint 2586->2587), the explained rise, identical to the
body. Claim files, VERSION, manifest, notes headings: untouched vs origin/main.

Forward-carry: body says `none`; the null-control requirement it names lives
in the tree (early_cutoff.py:224 comment, confirmed at the head); the
instrument findings are routed to #201 root-cause, not a stage brief.

Nothing blocked.
