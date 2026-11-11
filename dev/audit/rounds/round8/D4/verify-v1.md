# D4 verify — round 8, sole verifier (v1)

Tree: `/home/claude/audit-r8/seats/D4-v1`. This round runs a single verifier
per dimension and one common judge in total (owner's call, relayed in the
dispatch); I carry both halves of `tools/audit/briefs/verifier.md` for both
findings below rather than splitting across three verifiers.

Environment: `PYTHONPATH=tests/hastub`, the five BLAS thread vars pinned to
`1`, `NODE_PATH=/home/claude/audit-r8/pw/node_modules`,
`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`, `TMPDIR=/home/claude/audit-r8/tmp/D4-v1`.
`load1` on this shared box during measurement: ~17.8–18.8 (quoted, not
gated, per `tools/audit/README.md`). Both findings here are exact counts
(Tab-stop inversions; identical-string residual), not timings, so they are
contention-immune as the finders state.

## D4-01 — keyboard Tab order jumps backward (medium)

**1. Re-ran the finder's harness exactly**, `tools/audit/round8/D4/s1_tab_order.mjs`,
at all three required viewports, with a freshly generated plan payload
(`tests/plan_view.py` -> `/tmp/plandata-c57de68050e0.json`, this tree's own
hash):

| viewport | finder's reported value | my re-run |
|---|---|---|
| 375x812 | 3 | **3** |
| 768x1024 | 1 | **1** |
| 1280x800 | 2 | **2** |

Exact match at all three viewports, `thread_factor=1.0`. Sample inversion
pairs match the finder's report (e.g. `wi-revert -> wi-day-start` at
375x812).

**2. My own harness, my own metric**: `tools/audit/round8/D4/v1_reading_order.mjs`.
Metric definition: `reading_order_violations` = count of **all pairs** (i<j)
of Tab stops, not just adjacent ones, where stop j's top edge sits a full
row-height or more above stop i's top edge — a global "does the Tab
sequence later revisit something a top-to-bottom reader already passed"
check, with no x-position condition at all (the finder's `inversions` metric
is adjacent-pairs-only and requires the later stop not be to the right).
Results, same plan payload and viewports:

| viewport | reading_order_violations |
|---|---|
| 375x812 | 35 |
| 768x1024 | 4 |
| 1280x800 | 21 |

Nonzero at all three viewports under a structurally different metric,
independently confirming the underlying phenomenon (DOM/visual order
mismatch in the expanded what-if dialog) rather than an artifact of the
finder's specific adjacency/x-position rule.

**3. Attacked the method:**
- *Contention*: counts, not timings; `load1` was ~18 during measurement but
  this metric is a deterministic count over a fixed sequence of real
  keypresses against a fixed DOM, immune to scheduling noise. Re-ran
  375x812 twice; identical 3/3.
- *Gate mode*: not applicable — no suite-gap or golden-drift claim here.
- *Grid artefact*: single number per viewport, not an aggregate; not
  applicable.
- *Null control*: the finder's perturbation (`.whatif .wi-row { flex-wrap:
  wrap }` -> `nowrap`, restored) is the null-control-equivalent for a
  CSS-mechanism claim. I re-ran it myself: 375x812 inversions 3 -> **2**,
  confirming the finder's exact observed value and direction, and
  confirming other contributors remain (the finder's own caveat — I did not
  chase them further, since the claim is about *this* mechanism, and the
  finder explicitly scoped the remainder as "additional non-flex-wrap
  contributors, named in the harness output" rather than claiming
  `flex-wrap` is the sole cause).
- *Stub vs real HA*: this is real Chromium via Playwright,
  `page.keyboard.press("Tab")`, against the actual shipped card file
  (`custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`)
  loaded with `page.addScriptTag`. Not `FakeHass`, not a DOM stub. Fully
  reachable in real Home Assistant's frontend, which loads this same card
  file and lets a browser drive real Tab order.
- *Severity*: medium is earned. This is a genuine accessibility regression
  for sighted keyboard-only users (motor-impaired users navigating via
  keyboard, not screen-reader users, since it is a visual/spatial
  mismatch, not a missing-label issue) in a dialog that is reachable and
  exercised (`what_if:true`), at every required viewport, not a single
  edge case. It is not high/critical because it does not block any
  action — every control is still reachable by continuing to Tab through
  it, and revert/apply/save all remain functionally operable; it costs
  orientation, not capability.

**Production tree left clean**: perturbation was applied and reverted with a
verified `diff -q` no-op; the final tree is byte-identical to
`/home/claude/audit-r8/export` outside of the new
`tools/audit/round8/D4/` evidence files.

**Vote: verify.** Severity: medium (as filed). Both the finder's exact
harness and an independently authored, structurally different metric
reproduce nonzero backward jumps at all three required viewports, and the
perturbation reproduces the finder's exact observed direction and value.

## D4-s2-01 — one options-flow label left in English on sv locale (low)

**1. Re-ran the finder's harness exactly**, `tools/audit/round8/D4/s2_translation_gap.py`:

- baseline: `identical_strings_total=8`, `allowlisted_legitimate=7`,
  `untranslated_residual=1`, residual = `/options/step/heat_curve/data/ecl110_mqtt_qos`
  = `'MQTT quality of service'`. Matches the finding's `value:1` exactly.
- `--perturb`: `untranslated_residual=0`. Matches the finder's stated
  perturbation outcome exactly.
- Confirmed by direct read of both catalogs: `en.json` and `sv.json` hold
  the identical string `'MQTT quality of service'` at that path, while the
  sibling field on the same page/section, `ecl110_mqtt_retain`, is
  translated (`en`: `'Retain MQTT messages'`, `sv`: `'Behåll
  MQTT-meddelanden'`) — exactly as the claim states.

One documentation-only discrepancy, immaterial to the count: the
harness's own docstring says "the 10 ALLOWLIST entries" but the `ALLOWLIST`
dict in the same file has 7 keys (confirmed: `allowlisted_legitimate=7`,
matching the finding's own `metric_definition`, which says "a 7-path
reviewed ALLOWLIST"). The docstring's "10" is stale/wrong; the code and the
finding text agree at 7. Not a finding on its own (a one-line self-inconsistent
comment, no behavioral effect) — noting it for the judge rather than filing
it separately, per `CLAUDE.md`'s fix-first/verify/file-last chain.

**2. My own harness, my own metric**: `tools/audit/round8/D4/v1_locale_residual.py`.
Metric definition: `english_looking_residual` = count of identical
(en, sv) string pairs (same exclusion of `/exceptions/*` as the finder,
since that is a structural exclusion — format-only message bodies, not a
translation judgment) whose string contains at least one token from a
small, generic, path-agnostic set of English function/content words
("of", "the", "quality", "service", "hours", "price", "message", "control",
"settings", "enable", "disable", "minimum", "maximum", "value", "device",
"sensor", "source", "and"). This does not use the finder's path-based
`ALLOWLIST` at all — it is a content heuristic with no knowledge of which
paths are "supposed" to match.

Result: `english_looking_residual=1`, same key
(`/options/step/heat_curve/data/ecl110_mqtt_qos`), same string. All 7 of the
finder's allowlisted paths (Legionella, Tank, Open-Meteo, two bare numeric
ranges, Tibber, the Swedish-language Goteborg Energi product name) correctly
produced **zero** false positives under this independent heuristic — none of
them contain an English-tell token — so the two methods agree on both the
residual and the exclusions without sharing logic. `--perturb` drops my
metric to 0 as well.

**3. Attacked the method:**
- *Contention*: pure JSON text comparison, no timing; `load1` ~17.8–18.8,
  irrelevant to a deterministic string count.
- *Gate mode*: not applicable.
- *Grid artefact*: not an aggregate.
- *Null control*: the finder's own null control (7 allowlisted
  identical-string paths, each with a stated reason) held under my
  independent heuristic too — genuine evidence the residual is a real gap,
  not an artifact of "identical string" being too blunt a test.
- *Stub vs real path*: `en.json`/`sv.json` are read exactly as HA's frontend
  translation loader reads them (by JSON path, verbatim), per the harness's
  own header and confirmed by direct inspection — this is the real
  production catalog pair, not a test fixture.
- *Severity*: low is earned, not higher. One field, one language, one
  options-flow page a user visits rarely (ECL110 heat-curve MQTT settings);
  it degrades polish, not function — the field is fully usable in English,
  and every other control on the page is translated. Not medium: it does
  not block a workflow or misrepresent behavior (the raw-English label
  correctly names what the control does).

**Production tree left clean**: no production file was mutated for this
finding (the harness perturbs `sv` only in-memory); `diff -r` against
`/home/claude/audit-r8/export` confirms no changes outside
`tools/audit/round8/D4/`.

**Vote: verify.** Severity: low (as filed). Exact reproduction of the
finder's harness and an independently authored, path-agnostic heuristic
both land on the same single residual key, and the perturbation resolves it
in both.

## Cross-finding note

D4-01 and D4-s2-01 are not one mechanism (one is Tab/focus-order geometry in
the what-if dialog's CSS; the other is a translation-catalog content gap on
an unrelated options-flow page) — no shared-mechanism note applies to either
vote.
