Fix review: blocked 82daaab4421a380e3e73c570e58dffe19dc0d588 harness: class-open finite_inline (nowTemp, refit.scale)

bus-nonce: 22ae2ad2ea2c5bac7f924ea56cb3ac39

Measured head: 82daaab4421a380e3e73c570e58dffe19dc0d588, from a detached worktree
at /private/tmp/rev-2346/tree. Everything below was re-derived on this machine
against merge-base e3f3b312fff572904f24d78a44a2c4492b1a8ddb.

## What passes (re-derived, not taken from the body)

- Mutation proof, run by me in my own worktree (evidence/mutants-run.log):
  M0 null -> `ALL CARD CHECKS PASSED`; M1 (4 FAIL), M2 (11 FAIL), M8 (1 FAIL),
  M3 (1), M4 (1), M5 (1), M6 (1), M7 (1) each kill the named check(s). Every
  mutant is an exact production-line replacement, restored with `git checkout`.
- Finder's harnesses, at both ends:
  - card_shapes.mjs (sha1 677b75421c…, out of tree, named) —
    base `total=31 char_width_inline=2 finite_inline=7 no_plan_state=2 dead=2`;
    head `total=24 char_width_inline=0 finite_inline=3 no_plan_state=1 dead=0`.
  - v2_card_lines.mjs (in tree) — base `total=34 isfinite=7 char_width=3
    no_plan=4`; head `total=27 isfinite=3 char_width=1 no_plan=3`.
  - wizard_widgets.py (sha1 66b390554c…, out of tree, named) — base
    `menu_disagree=1 menu_fallbacks=23`; head `menu_disagree=0
    menu_fallbacks=23`; `golden_equal=1` at both ends. Perturbation
    `--bump heat_pump_cop_nominal` moves `disagree` 0 -> 2, so the census is
    live, not vacuous.
- Claim files against real drift: `node tests/card_drift.mjs <merge-base>` ->
  `39 state(s) moved and claimed, 1 identical` (evidence/card_drift.log).
  `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all <merge-base>` ->
  `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56`; the
  config_flow leaf is claimed, not may-drift (evidence/envdrift-all.log).
- `claims-for:` is `7.0.0` in both claim files, equal to VERSION `7.0.0`.
- VERSION, manifest.json version, and RELEASE_NOTES heading are untouched.
- Forward-carry is present: `dev/programme/rosters/wave-r10-groups.json`,
  R10-ARCHSCORE-COVERAGE's `brief`, carries the precondition that the card's
  dead-definition row and clone census be recorded at a base already carrying
  these C1/C4 folds, stated as a precondition with its control.
- Red checks: CI check-runs for the head are green (`browser` success,
  `env-matrix` success, `mutation` success, `pr-contract` success). The body's
  two local reds are answered and real: `P9 grid: no two text runs share ink`
  fails with the same pair (`text "2" x text "3", 2 px`) at the merge base
  (evidence via /private/tmp/r10-ux-setup/browser-base.log), so it is main's
  own; `env_drift.py --all` reds are the re-record-then-claim sequence the
  body describes.

## What blocks

`harness: class-open finite_inline` — the enumeration rule the body names
(card_shapes.mjs `finite_inline`, v2_card_lines.mjs `isfinite_lines`) returns
two seams at the head that are neither deduped in the diff nor dispositioned
in the body, and the check that should own them does not see them.

The check in `tests/card.mjs` reads:

    const finite = cardSrc.split("\n")
      .filter((l) => /typeof n === "number" && Number\.isFinite\(n\)/.test(l)
        && !/^\s*(const finiteNum|\*|\/\/)/.test(l));
    check("the finite-number test is spelled in exactly one place", …)

Its regex matches only the literal parameter name `n`, so it pins the four
`n`-named receipt spellings the C4 fold did dedupe (money/pct/amount/neg) —
that part is real and M7 kills it. But the finite-number rule is still spelled
inline in two more places, with different variable names, which the regex does
not match:

- `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:7071`
  `if (typeof nowTemp === "number" && Number.isFinite(nowTemp) && axes.temp)`
- `…/heatpump-optimizer-card.js:8684`
  `if (refit && typeof refit.scale === "number" && Number.isFinite(refit.scale))`

The finder's own metric reports `finite_inline=3` at the head (the two above
plus the `finiteNum` owner), and the finding's recorded target in
`dev/audit/rounds/round10/CATCHUP-VERIFY.json` is `C4 … finite 7->3` — three
places, not "exactly one". The check's comment — "neither is re-spelled inline
anywhere else in the card" — is therefore false, and a mutation that re-spells
the rule inline under a non-`n` name would pass the check while its name
claims it cannot.

These two seams are not in the C4 diff (the finder's C4 patch, and this PR,
leave `nowTemp`/`refit.scale` untouched) and are not dispositioned in the
body, which reports `finite_inline=3` without saying what the three are or
why the two remain. Per `fix-review.md` step 6 this is a class-open seam. The
fix is small: either dedupe both to `finiteNum(…)` and widen the check to the
finder's pattern (`typeof (\w+(?:\.\w+)?) === "number" && Number\.isFinite\(\1\)`),
or narrow the check's name/comment to the `n`-named spelling it actually
enforces. (The fixer's own later, unpushed commit 5295fa06a — "the finite
census widened, a comment this PR made false" — does the former.)

## Secondary note (not a block on its own)

`d408fa76a` ("a place with no options page names itself, not undefined") adds
a `page ? L(page) : placeLabel(b.place)` fallback for a place the backend adds
ahead of the card, but no test topology renders such a place (every place in
`qaTopologies`/`layoutCatalogTopo` is in `SETUP_CONFIGURE_PAGE`), and no check
in this head pins the fallback. It is not in the body's mutation table. Worth
pinning or acknowledging when the finite census is revisited.

RESULT mutation M0 null: 0 FAIL (passes)
RESULT mutation M1..M8: each killed (4/11/1/1/1/1/1/1 FAIL respectively)
RESULT card_shapes base total=31 finite_inline=7 char_width_inline=2 no_plan_state=2 dead=2
RESULT card_shapes head total=24 finite_inline=3 char_width_inline=0 no_plan_state=1 dead=0
RESULT v2_card_lines base total=34 isfinite=7 char_width=3 no_plan=4
RESULT v2_card_lines head total=27 isfinite=3 char_width=1 no_plan=3
RESULT wizard base menu_disagree=1 menu_fallbacks=23 golden_equal=1
RESULT wizard head menu_disagree=0 menu_fallbacks=23 golden_equal=1
RESULT wizard perturbation --bump heat_pump_cop_nominal disagree 0 -> 2
RESULT card_drift 39 state(s) moved and claimed, 1 identical
RESULT env_drift NO UNCLAIMED DRIFT (56), NO STALE FIXTURE (56)
RESULT class-open finite_inline: nowTemp (card.js:7071) and refit.scale (card.js:8684) remain inline; check matches only literal `n`
