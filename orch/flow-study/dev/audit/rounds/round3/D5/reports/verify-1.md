# D5 — verifier 1 of 2, refute-first

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`. Tree: the `git archive`
export at `…/audit-r3/verify/D5-1` (no `.git`; `docs/audit-*.md`,
`docs/backlog.md` and `RELEASE_NOTES.md` excised). Box: 8-core Apple M1, 8 GB,
python3 3.11.5, certifi 2026.06.17. Shared and busy: `load1` 6.6–11.7 across
the session. **Every number below is a count over static text, over a driven
`_page_schema` render, or an HTTP status.** No wall, CPU or RSS number is
claimed, so contention cannot move any of them; each harness prints
`thread_factor=1.0` and its `load1` anyway.

Four harnesses written for this seat, under `tools/audit/round3/D5/verify-1/`:

| file | what it measures |
|---|---|
| `ext_links.py` | external URL liveness, HEAD-then-GET, own extractor, certifi trust |
| `option_doc_coverage_v2.py` | option-field doc coverage under 2 matching rules × 4 corpora |
| `comment_symbols_v2.py` | dangling comment symbols resolved **in the file the comment lives in** |
| `link_and_supersession_breadth.py` | the link shapes and supersession phrasings the finder's instruments cannot see |

Plus `linkcheck_certifi.py` — the finder's own `linkcheck.py` with the one-line
TLS fix, unchanged otherwise.

## 0. The external arm, run for the first time

The attached correction is confirmed by my own probe before I leaned on it:
`ssl.get_default_verify_paths()` returns `cafile=None` and names
`/Library/Frameworks/Python.framework/Versions/3.11/etc/openssl/cert.pem`,
which does not exist; `urllib` on the default context raises
`CERTIFICATE_VERIFY_FAILED` for `https://www.python.org`, and the same request
on `ssl.create_default_context(cafile=certifi.where())` returns **200**. The
box has outbound network. The finder's `211/211 URLError` was a TLS trust
failure, not a sandbox.

Run both ways, and they agree:

| instrument | distinct URLs | dead |
|---|---|---|
| the finder's `linkcheck.py --external` + the certifi line | **211** | **`external_head_failures=3`** |
| `verify-1/ext_links.py` (own extractor, HEAD then GET) | **215** | **`external_dead=3`** |

The three, identical in both runs:

```
404  https://example.com/not-an-issue                        <- .claude/workflows/fixtures/policy-loop/render-links-rotten.md
404  https://github.com/tvofi/heatpump_optimizer/issues/9002  <- .claude/workflows/fixtures/policy-loop/render-links-healthy.md
404  https://github.com/tvofi/heatpump_optimizer/pull/9001    <- .claude/workflows/fixtures/policy-loop/render-links-healthy.md
```

All three are **synthetic fixtures**: `#9001`/`#9002` are placeholder numbers in
a two-file pair that exercises a `#NNN`-link-shape renderer, one named
`-healthy` and one `-rotten`. They are not documentation and were never meant
to resolve.

- `external_dead` with at least one user-facing source (README, `docs/`,
  `DISCLAIMER.md`): **0**.
- `external_head_refused_get_ok=0` — no host in this corpus refuses HEAD, so
  the finder's HEAD-only rule would not have over-fired either.
- `external_transport_errors_on_head=0`; **0 redirects** — all 212 live URLs
  answer 200 at the exact URL written.
- Perturbation: append `[x](https://not-a-real-host-d5verify.invalid/)` to a
  copy's README → `external_dead` **3 → 4**, exactly +1. Instrument live.

**Nothing about external links is a finding.** The finder's one open item
closes clean, and `README.md`'s four `img.shields.io` badges, its
`hacs.xyz`, `home-assistant.io` and `python.org` targets all return 200.

One instrument note, measured not inferred: `linkcheck.py`'s `LINK_RE` *does*
scan a plain `![alt](target)` image — proved by perturbation, `links_scanned`
338 → 339 and `broken_file_links` 0 → 1 when a broken image is appended. What
it misses is only the **inner image of a nested `[![alt](img)](href)`**, which
is exactly the four README badges. All four are 200, so `links_scanned=338`
undercounts by 4 and hides nothing.

## 1. Re-runs at baseline — all four exact

| harness | result | matches report |
|---|---|---|
| `linkcheck.py` | `broken_links_total=1`, `broken_file_links=0`, `broken_anchors=1`, `links_scanned=338`, `markdown_files=98`, `broken_links_excised=6`, `external_links_distinct=211` | yes (`load1=11.74`) |
| `option_doc_coverage.py` | `option_fields_rendered=180`, `option_fields_undocumented=10`, `option_schema_keys_rendered=213`, `wood_economics_fields_rendered=4`, `wood_economics_doc_lines=0` | yes (`load1=11.52`) |
| `comment_symbols.py` | `dangling_comment_symbols=27`, `dangling_card=18`, `dangling_card_private_distinct=13`, `dangling_py=9`, `backticked_identifier_mentions=739`, `code_vocab_tokens=25442` | yes (`load1=10.99`) |
| `doc_structure.py` | `superseded_docs_without_forward_pointer=1`, `readme_links_to_superseded_doc=1`, `readme_index_omissions=4`, `supersession_statements=1`, `unreachable_docs=15` | yes (`load1=10.99`) |

**Header defect, `option_doc_coverage.py`:** its `EXPECTED` block says
`RESULT option_fields_rendered=174 count`. It prints **180**, and `REPORT.md`
says 180. A judge re-running the harness without reading the finding is told
to expect a number the harness does not produce. Wrong line, right finding.

## 2. D5-01 — my own rule reproduces the 10 exactly; the error is an undercount

`option_doc_coverage_v2.py` drives the same production symbol
(`config_flow._page_schema`, all 21 pages, every boolean flag on) through an
independently written schema walk, label lookup and matcher.

Render side reproduces exactly: **180 labelled fields**, 21 pages, 33
unlabelled/section keys.

**Two matching rules, four corpora:**

| corpus | strict (contiguous name only) | bag-of-words (the finder's rule) |
|---|---|---|
| the finder's 7 user docs | **17** | **10** |
| `docs/configuration.md` alone | 17 | 10 |
| every doc reachable from README (12) | 17 | 10 |
| **every `.md` in the tree** | 13 | **6** |

The bag-of-words column at `7docs` is **10, and the ten are the same ten
fields the finder names** — key for key. An independently written matcher over
an independently written render lands on the identical set.

### The metric over-fires once and under-fires three times — net, it is low by 2

I adjudicated all seven fields the two rules disagree on, by reading the lines.

*Correctly rescued (rule (d) doing its job) — 4:* `comfort_temp_day_weekend`,
`comfort_temp_night_weekend`, `holiday_comfort_temp_day`,
`holiday_comfort_temp_night` are genuinely documented by the merged rows
`docs/configuration.md:89` *"Weekend daytime / night comfort"* and `:90`
*"Holiday daytime / night comfort"*. The generous rule is justified.

*Spuriously rescued — 3, all substring accidents:*

- `day_end_hour_weekend` (*'Weekend day ends at'*) is spared by
  `README.md:614`, *"own history, kept separate for weekdays and weekends, and
  it never displaces a"* — `weekend`⊂`weekends`, `day`⊂`weekdays`,
  `ends`⊂`weekends`, `at`⊂`separate`. A sentence about savings history.
  This one matters: the finder's own prose says docs *"never [document] the
  weekend or holiday hours"*, and there are **four** such fields; its metric
  catches three.
- `mixing_valve_write_target_kind` (*'What the control entity expects'*) — the
  stoplist eats `what`/`the`/`expects`, leaving `[control, entity]`, matched by
  6 unrelated lines.
- `space_setpoint_unit` (*'What that set-point entity expects'*) — reduces to
  `[set, point, entity]`, matched by `docs/configuration.md:350`, a row about
  frequency sensors.

*Over-fired — 1:* `price_surcharge` is covered by `docs/configuration.md:339`,
*"| VAT multiplier / surcharge | 1.0 / 0 | 0–2 | Applied as value × VAT +
surcharge. |"* — default, range and formula. A user searching "surcharge" finds
it. The finder calls this "the one soft entry" itself; it should not be in the
10.

**Adjudicated: 12 of 180**, not 10. The finding's direction of error is
conservative.

### The wood-fuel claim survives every attack I could put to it

- The commissioned grep returns **nothing**:
  `grep -rniE 'wood_type|wood_packing|wood_price|furnace efficiency|cubic metre|birch' README.md docs/*.md` → exit 1, zero lines. That sweep is
  *wider* than the finder's corpus (it includes the plan documents).
- Alias sweep over 16 phrasings across the 7 docs (3 995 lines, each file
  asserted present so a missing path cannot print a false zero — an earlier
  pass of mine produced exactly that false zero through zsh word-splitting and
  was discarded): `firewood` 0, `species` 0, `stacked` 0, `dumped` 0,
  `cheaper.?than.?pump` 0, `wood_cheaper` 0, `travad` 0, `0\.60` 0,
  `sek ?/ ?kwh` 1 (a grid-fee plausibility bound), `flow temperature` 1 (4-way
  valve hydraulics). **None of the four is documented under any name a user
  would search.**
- The docs talk about the wood *tank* at length — volume, probes, the DHW coil,
  the hydronic catalog — which is what makes the economics gap easy to miss and
  hard to argue away: the store is documented, the price basis is not.

### One correction to the claim as summarised

`wood_economics_doc_lines=0` is scoped to the seven user documents, and
`REPORT.md` states that scope correctly. The compressed claim — *"with 0
documentation lines anywhere"* — is **false**. Widening to every `.md` in the
tree drops the undocumented count 10 → 6, because all four fields are named,
with their enums and semantics, in
`docs/superpowers/specs/2026-09-05-wood-furnace-economics-design.md` (12 lines)
and `docs/superpowers/plans/2026-09-05-wood-furnace-economics.md` (36 lines).
Both are development records, both are in `doc_structure.py`'s
`unreachable_docs`, and `writing-for-agents.md` puts them outside the reader
path — so **"named by no user-facing document" stands**; "no documentation
lines anywhere" does not.

### Reachability and severity

Not a stub artefact: `_page_schema("building", …)` renders 14 keys with
`wood_furnace_enabled` off and **27 with it on**, the four economics fields
appearing only in the second. They reach exactly the users who need them.

But every one of the four carries substantive in-flow help — *"Packed is
stacked (travad); loose is dumped (stjälpt) and billed at 0.60 of packed"*,
*"Empty keeps the cheaper-than-pump sensor unavailable — there is no silent
default"* — and the decision they feed is advisory only: the approved design
says *"The live solver does not choose wood"* and *"Lighting a fire stays a
human decision"*, and README:469 marks the advisor *"Diagnostic; advisory only
— never lights the stove"*. Nothing is actuated on a misread field and no money
moves automatically. The consequence is "cannot look it up afterwards", which
is `low` in this scheme, not `medium`. The genuinely sharper item — README's
index calling `docs/configuration.md` *"Every setup field and options page"*
while a whole feature group is absent — is a false claim, and the finder
correctly hands it to D6 rather than resting D5-01 on it.

Perturbation: delete `docs/configuration.md`'s "Wood tank volume" row on a copy
→ `undoc_strict_7docs` 17 → 18 and `undoc_bagofwords_7docs` 10 → 11. Live.

## 3. D5-02 — I hunted false positives and found none; the 18 is a floor

`dangling_comment_symbols=27`, `dangling_card=18`, distinct 13 all reproduce.

**Every false-positive vector I was asked to test came back negative:**

- *A name alive in a different-language or test file.* `_lineLabel`,
  `_extraFields`, `_onSlotEdit` and `_runWhatIf` **do** appear in
  `tests/card.mjs` — at lines 673, 5543, 5641, 5646, 5974 and 5978, and every
  one of those is inside a `//` comment. The harness strips comments before
  building its vocabulary, so it excluded them correctly.
- *A substring of a longer real name.* A raw grep for `_currency` hits
  `coordinator.py`, `config_flow.py`, `currency.py`, `narrative.py` and
  `tests/entities.py` — all of them the substring inside `resolve_currency`.
  The harness uses `IDENT.findall`, which tokenises, so it is right and my
  grep was the sloppy instrument.
- *A JSON key or generated file.* `.json`, `.yaml`, `.sh`, `.toml`, `.cfg` are
  all in the vocabulary already; no miss turned out to live in one.

**The evidence table's line numbers are all exact.** `lineLabel`:3776,
`fieldPoints`:3692, `extraFields`:3712, `seriesUnit`:4074, `resolveEntity`:3923,
`laneGroupInner`:6540, `onSlotEdit`:7676 — seven for seven. My first pass
disagreed with every one of them; that was my own bug (I blanked block comments
with `" " * len(match)`, which eats their newlines and shifts every later line
number). Corrected, the finder is right and I was wrong.

**The five with no counterpart are confirmed:** `refreshLayout`,
`restoreSlotFocus`, `chartWidthDrifted`, `applyView`, `runWhatIf` each occur
**0** times case-insensitively in the card's 10 491 lines of non-comment text,
and once in the comment that names them.

### One wrong cell in the evidence table

> `` `_currency()` `` | *"`currency` appears only as a translation key"*

**False.** `currency() {` is defined at `heatpump-optimizer-card.js:4054` and
called five times as `.currency()` (`:5260`, `:5676`, `:8891`, `:9167`, and
`:3752` via `this.currency()`). `_currency` is still a genuine miss, but its
counterpart exists and is obvious, exactly like `_lineLabel` → `lineLabel`.
The row belongs in the upper group. The "sharp end" is five, and stays five.

### My own rule finds one more, not one fewer

`comment_symbols_v2.py` asks the reader's question instead of the
repository's: can a `_camelCase` name backticked in a card comment be resolved
**in the card file itself**? That gives **`dangling_card_local=19`, 14
distinct** — one above the finder. The extra is `_onWhatIfInput`
(`card.js:7573`), which the cross-file vocabulary rescues through
`tests/card_drift.mjs:149`:

```js
whatIfInput: (c, ev) => (c.whatIf ? c.whatIf.onInput(ev) : c._onWhatIfInput(ev)),
```

— a dead fallback branch in a test rig pointing at a card method that no longer
exists. That is the same defect, kept alive by the shim.

**Scope extension:** the same rule over `tests/*.mjs` comments finds **16**
sites naming card symbols the card does not have, and five of those names —
`_onSaveSchedule`, `_hidden`, `_attachSetupEvents`, `_onLegendClick`,
`_closeSlotMenu` — are absent from the finder's whole-repository vocabulary
too, so they are dangling by its own rule and merely outside its
production-only scope. The defect is roughly twice as wide as 18.

### Two reporting over-reaches

- *"identifiers that exist nowhere"* is true of **this repository** and no
  wider. Four of the nine Python misses name real symbols outside it:
  `ProcessPoolExecutor` (`concurrent.futures`), `__float__` (a dunder),
  `has_value` and `current_option` (Home Assistant entity properties this tree
  does not vendor). Naming them in a comment is correct documentation. The
  metric's own wording ("nowhere in the repository") is literally right; the
  gloss is not, and the distinction is invisible to the instrument.
  `ProcessPoolExecutor` is claimed on separate grounds — that the sentence
  misdescribes the runtime — and that is a content claim, not a stale name.
- The report says the remaining eight Python misses *"are listed as
  non-findings below"*. **There is no such list.** The Non-findings table has
  no row for them.

Also loose: *"the card was refactored from methods to module-level
functions"* — the card still defines **24** `_camelCase` methods in live code
(`_render`, `_refitCharts`, `_attachChartEvents`, …) and carries 36 `this._x`
references. The refactor was partial. The 13 dangling names are unaffected.

Perturbation: rewrite one of the three `` `_lineLabel` `` spans to
`` `lineLabel` `` on a copy → `dangling_card_local` 19 → 18. Live.

## 4. D5-03 — instance real, and `1 of 338` is a rate, not an instrument limit

Instance verified by reading both ends. `README.md:194`:

> Each path in full: [Switch and climate entity](#switch-and-climate-entity),

and the only matching section, `README.md:494`, is
`### Switches, climate and datetime entities` → slug
`switches-climate-and-datetime-entities`. No heading and no `<a name>` yields
`switch-and-climate-entity`. Dead on GitHub.

**Breadth attack.** `link_and_supersession_breadth.py` adds every shape
`linkcheck.py` cannot see, across all 98 markdown files:

| shape | scanned | broken |
|---|---|---|
| image links `![alt](target)` | 13 | **0** |
| raw HTML `<a href=…>` | 0 | 0 |
| raw HTML `<img src=…>` | 0 | 0 |
| reference-style usages `[text][label]` | 0 | 0 |

There is no other link shape in this tree carrying breakage — no HTML anchors
at all, no reference-style links at all, and all 13 images resolve. Combined
with §0's finding that plain images *are* already scanned and only the four
nested badge images are missed (all 200), **`1 of 338` is a real rate.**

Perturbation: append `![x](docs/img/no-such-image.svg)` to a copy's README →
`broken_wide_images` 0 → 1. Live.

## 5. D5-04 — instance real, and `1 of 1` is a measurement, not a regex's reach

Instance verified at both ends:

- `docs/plan-2026-09-open-issues.md:10` — *"It supersedes
  `docs/plan-open-issues.md`, which covered #86–#101 and is complete."*
- README links three plan documents, at `:781` (`plan-v4.0.0-program.md`),
  `:786` (`plan-open-issues.md`, as "program") and `:788`
  (`plan-card-decomposition.md`). **None is `plan-2026-09-open-issues.md`**,
  which `doc_structure.py` confirms is unreachable from README by any path.
- `docs/plan-open-issues.md` carries no forward pointer:
  `grep -ncE "supersed|plan-2026|2026-09|successor|replaced by|obsolet"` → **0**
  (run without a pipe, so the exit status is grep's own: 1). Its own header
  dates it to `83b7ea0` (v5.5.0) and nothing tells the arriving reader it is
  finished.

**Breadth attack.** The finder detects supersession with exactly
`` supersedes\s+`X.md` `` — one literal verb, one tense, backticks required.
I swept ten phrasings (`supersedes`, `superseded by`, `replaces`, `replaced
by`, `obsoletes`, `deprecated in favour of`, `retired in favour of`, `moved
to`, `successor is`, `see instead`) over every markdown file:
`supersession_candidates_wide=1` — the same statement. So
`supersession_statements=1` is what the tree contains, not what the regex can
reach, and the metric's denominator is honest.

`readme_index_omissions=4` reproduces. The `## Documentation` table has 7 rows,
one of which (`docs/backlog.md`) is excised from this export, and the README
separately links `docs/automations.md` plus the three plan documents.

## 6. Votes

| finding | vote | severity | my number |
|---|---|---|---|
| D5-01 | **weaken** | `low` (finder: `medium`) | `undoc_bagofwords_7docs=10`, identical set; adjudicated **12 of 180**; wood group 4/4 confirmed, 0 lines in 7 docs, 48 lines in 2 unreachable development records |
| D5-02 | **verify** | `low` | `27 / 18 / 13` reproduced exactly; my card-local rule gives **19 / 14**; 0 false positives found |
| D5-03 | **verify** | `low` | `broken_links_total=1` of `links_scanned=338`; wide scan adds 13 shapes and **0** further breakage |
| D5-04 | **verify** | `low` | `superseded_docs_without_forward_pointer=1`, `readme_links_to_superseded_doc=1`; wide phrase sweep still **1** |

Nothing on this panel rests on a timing number, so no vote is `unresolved` for
contention.

### Carried to whoever fixes these

1. `option_doc_coverage.py`'s `EXPECTED` header says `option_fields_rendered=174`; it prints `180`.
2. `option_doc_coverage.py`'s rule (d) is a substring bag-of-words test; it spares `day_end_hour_weekend`, `mixing_valve_write_target_kind` and `space_setpoint_unit` on unrelated prose, and flags `price_surcharge` which `configuration.md:339` covers.
3. `REPORT.md`'s `_currency()` row is wrong: `currency()` is defined at `card.js:4054`.
4. `REPORT.md` promises a list of the eight Python non-findings "below"; it is not there.
5. `linkcheck.py`'s `LINK_RE` misses the inner image of `[![alt](img)](href)` — 4 URLs, all 200.
6. The external arm needs no networked box; it needs `context=ssl.create_default_context(cafile=certifi.where())`. `verify-1/linkcheck_certifi.py` is that diff and nothing else.
