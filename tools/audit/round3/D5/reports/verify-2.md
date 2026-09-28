# D5 — verifier seat 2 of 3

Stance: refute-first. Every number below was executed on this box, in the
working copy at
`scratchpad/audit-r3/verify/D5-2`, against baseline `ae36eff`.

**Box and contention.** 8-core Apple M1, python3 3.11.5, `certifi` present.
`load1` ran **5.11 – 15.02** across my session, `thread_factor` (load1/ncpu)
**0.64 – 1.88**. Every figure I report is a **count over static text, or over a
driven code path** — no wall, CPU or RSS number is claimed — so contention
cannot move any of them. The per-run `load1` is recorded beside each number.

My instruments are under `tools/audit/round3/D5/verify-2/`:
`v2_card_scope.py`, `v2_comment_symbols.py`, `v2_rename_locator.py`,
`v2_option_doc_coverage.py`, `v2_rule_null.py`,
`v2_anchor_and_supersession.py`, `v2_external_links.py`.
The production tree was not modified; every perturbation ran against a copy at
`scratchpad/d5v2_pert` via `D5_ROOT`.

---

## Harness re-runs — all four reproduce exactly

| harness | headline metric | finder | me | load1 |
|---|---|---|---|---|
| `option_doc_coverage.py` | `option_fields_undocumented` | 10 | **10** | 5.83 |
| `option_doc_coverage.py` | `wood_economics_doc_lines` | 0 | **0** | 5.83 |
| `comment_symbols.py` | `dangling_comment_symbols` | 27 | **27** | 5.55 |
| `comment_symbols.py` | `dangling_card` / `dangling_py` | 18 / 9 | **18 / 9** | 5.55 |
| `linkcheck.py` | `broken_links_total` | 1 | **1** | 5.46 |
| `doc_structure.py` | `superseded_docs_without_forward_pointer` | 1 | **1** | 5.46 |
| `doc_structure.py` | `readme_links_to_superseded_doc` | 1 | **1** | 5.46 |

**One mismatch, in a denominator, not a finding.** `option_doc_coverage.py`'s
header block claims `EXPECTED ... option_fields_rendered=174`; the script prints
**180**, which is also what the finder's own `REPORT.md` body states ("180 of
them labelled user fields"). The header's `174` is stale. It does not touch any
claim, but a header that disagrees with its own script is a re-run trap for the
next seat.

**Instruments are live.** All four moved in both directions under their own
stated perturbations, run against the copy:

| perturbation | metric | before → after |
|---|---|---|
| add a `Wood type` row to `configuration.md` | `option_fields_undocumented` | 10 → **9** (and `wood_economics_doc_lines` 0 → **1**) |
| delete the `Wood tank volume` row | `option_fields_undocumented` | 10 → **11** |
| add `` # see `_no_such_helper_xyz` `` to `optimizer.py` | `dangling_comment_symbols` | 27 → **28** |
| rewrite the `ProcessPoolExecutor` sentence | `dangling_comment_symbols` | 27 → **26** |
| append `[x](docs/definitely-not-here.md)` to README | `broken_links_total` | 7 → **8** *(copy baseline 7, not 1 — my copy omits `LICENSE`/`NOTICE`, so 6 extra file links break in it; the delta is the control, and it is exactly +1)* |
| repoint the anchor at `#switches-climate-and-datetime-entities` | `broken_anchors` | 1 → **0** |
| give `plan-open-issues.md` a forward pointer | `superseded_docs_without_forward_pointer` | 1 → **0** (`readme_links_to_superseded_doc` unmoved at 1) |
| link the successor from README | `readme_links_to_superseded_doc` | 1 → **0** (`superseded_docs_without_forward_pointer` unmoved at 1) |

The last two matter: the two D5-04 metrics move independently, so the finding is
two separable defects and not one counted twice.

---

## D5-01 — verify, severity medium

**My metric definition**, written before I looked at the finder's rule set and
deliberately more generous than it:

> A rendered, labelled option field is **undocumented** when none of these is
> found in the user-facing corpus: (a) the config key verbatim; (b) the English
> `strings.json` label whole; (c) that label minus a trailing parenthetical;
> (d) the **Swedish** label from `translations/sv.json`, whole or minus
> parenthetical; (e) every content word of (c) inside one **200-character
> window** of the corpus with whitespace collapsed.

The three counting-rule questions, answered explicitly:

- **Which files are user-facing?** Not hand-listed. BFS from `README.md` over
  relative markdown links, minus development records (`docs/plan-*`,
  `docs/HANDOVER.md`, `docs/decisions/`, `docs/superpowers/`, `tests/`,
  `CLAUDE.md`, `tools/`), plus `DISCLAIMER.md`. That derives **8 documents**:
  README, DISCLAIMER, `docs/{dashboard-card,ecl110,configuration,architecture,automations,how-it-works}.md`
  — the finder's hand-listed 7, plus `DISCLAIMER.md`.
- **Does a field named only in an example count?** **Yes** under my rule: fenced
  blocks and YAML samples are in the corpus. I measured the alternative —
  `undocumented_prose_only` with fences stripped is **8**, identical. No field
  in this tree is documented only by an example, so the question does not bite.
- **Does a field named in Swedish count?** **Yes** under my rule (arm (d)). It
  changes nothing: no Swedish label appears in any user-facing document.

### My number

```
RESULT labelled_fields_rendered=180        RESULT undocumented_fields=8
RESULT documented_fraction=0.9556          RESULT undocumented_strict_no_window=17
RESULT corpus_documents=8                  load1=7.43  thread_factor=0.93
```

My rule gives **8**, two fewer than the finder's 10. I then attacked my own
rule and it lost: **both differences are false rescues of my window arm.**

- `wood_type` — "wood" and "type" land in one 200-char window of the README
  options-overview table, from *"the wood furnace tank"* and *"building type"*.
  Nothing there documents a wood type.
- `holiday_day_start_hour` — "holiday", "day", "starts", "at" scattered across
  an unrelated `how-it-works.md` paragraph about away toggles and recovery ramps.

**Null control on the matching rules** (`v2_rule_null.py`, 1998 synthetic labels
built from the real label word-bag, excluding word-sets that match a real label):

```
RESULT line_rule_null_rescue_rate=0.2212   (442/1998)   # the finder's rule (d)
RESULT window_rule_null_rescue_rate=0.3128 (625/1998)   # my rule (e)
```

My window rule "documents" 31% of labels that name nothing; the finder's
per-line rule, 22%. **Both rules are over-generous, so 10 is a lower bound on
the real gap, not an inflated one.** My strict arm — verbatim key or verbatim
label only, which cannot rescue by coincidence — gives **17 undocumented of 180**.
The honest bracket is 10 ≤ gap ≤ 17, and the finding takes the conservative end.

### Attacks

- **Grid artefact — drop the wood group and re-aggregate.** Survives, smaller:
  `undocumented_excluding_wood=5` under my rule, **6 under the finder's**;
  `documented_fraction_excluding_wood=0.9716`. So roughly 40% of the headline is
  the wood group. The group is the sharp end, but six scattered fields remain.
- **Missing null control — what fraction ARE documented?** Supplied, and it
  reframes the claim: **170 of 180 (94.4%)** under the finder's rule, 172/180
  (95.6%) under mine, 163/180 (90.6%) strict. This is a 5.6% tail, not
  "10 out of 12".
- **Is `wood_economics_doc_lines=0` an artefact of a narrow needle list?** No.
  An independent grep with a wider needle set — `wood.?type|packing|packed|loose|cubic met(re|er)|furnace efficiency|sek/m3|sek_m3|birch|pine|björk|firewood|stacked|cord of wood` —
  over all 8 user-facing documents returns **zero lines**. Meanwhile "wood"
  appears 41 times in them (README 6, `configuration.md` 17, `how-it-works.md`
  17, `architecture.md` 1). The docs raise the wood furnace repeatedly and never
  once name its four money inputs.
- **Reachability.** The four wood fields render only with
  `wood_furnace_enabled` on: `_page_schema` over all 21 pages yields **200 keys
  with defaults and 213 with the flag on**, and the wood four are in the
  difference. So the affected population is wood-furnace owners only.

### Is the severity earned by consequence? Yes — but not by the finder's argument

The finder's rationale is that a user "has no reference to consult" for what
*Packing* means. **That argument is weak and I measured it false.** All ten
fields carry a substantive `data_description` in-flow help string — including
`wood_packing`: *"Packed is stacked (travad); loose is dumped (stjälpt) and
billed at 0.60 of packed."* and `wood_furnace_efficiency`: *"Share of the wood's
energy that reaches the tank, percent."* Ten of ten have one; none is empty.

The severity is earned on a chain the finder did not follow. I traced it:

- `README.md:483` documents the user-facing entity **"Wood cheaper than heat
  pump"**, stating its availability condition as *"Unavailable until the wood
  tank is usable"*.
- `binary_sensor.py:203-206` — `WoodCheaperBinarySensor.available` returns
  `super().available and fuel.get("ready")`.
- `wood_fuel.py:428` — `ready = wood_fuel_ready(config)`.
- `wood_fuel.py:86-109` — `wood_fuel_ready` additionally requires `wood_type` in
  `WOOD_KWH_M3`, a valid `wood_packing`, `price > 0.0`, and
  `10.0 <= eff <= 95.0`.

So README states **one** of six availability conditions and omits the four that
this finding says are undocumented. A wood-furnace owner whose entity is
permanently unavailable reads the README, is told it is about the wood tank, and
has no user-facing text anywhere naming the price field that is actually gating
it — while `strings.json:572` says precisely that (*"Empty keeps the
cheaper-than-pump sensor unavailable — there is no silent default."*) in a place
the README never points at. `configuration.md:370-374` tables the neighbouring
wood-*tank* sensor fields in full, so this is an omission inside a covered area,
not an uncovered area.

That is a user-visible symptom with a documented-but-wrong cause. **medium
stands.** (The README:483 availability sentence is also a false documentation
claim — **for D6**.)

**Vote: verify, medium.** Executed number **10** (finder's definition,
reproduced) / **8** under my own definition, whose 2-field difference I
demonstrated to be coincidence at a 31% measured false-rescue rate.

---

## D5-02 — weaken, severity low

The claim handed to me is: *"27 comment sites name identifiers that exist
nowhere; 18 of those are the card's private methods, 5 have no counterpart at
all."* The **27 reproduces exactly**. The words **"exist nowhere"** and
**"no counterpart at all"** do not survive.

### The scope-artefact attack, run explicitly — it fails

I was asked to test whether the 18-of-27 concentration is the harness simply not
reading the JS. `v2_card_scope.py`:

```
RESULT card_js_in_vocab=1 bool   (7/7 probes present)
RESULT card_only_identifiers_in_vocab=1775 count
RESULT card_backticked_mentions=73 count
RESULT card_dangling=18 count
RESULT card_dangling_fraction=0.2466 ratio
```

The card contributes **1775 identifiers that no Python file has**, all seven
un-prefixed probe names are in the vocabulary, and **55 of the card's own 73
backticked identifier mentions resolve**. If the harness were blind to the JS,
all 73 would dangle. **The concentration is not a scope artefact** — the harness
reads `.js`, and the card is simply where the stale names are. Reported as
asked, and it is a point in the finding's favour.

### My metric, and my number

> **`unresolvable_sites`** = comment sites naming a backticked bare identifier a
> reader cannot find by any of: (1) exact token in executable code (the finder's
> rule); (2) the token with a leading underscore dropped, exact; (3)
> case-insensitive substring of the de-underscored token over **every** file in
> the tree, comments stripped from code files. Anything (2) or (3) rescues is
> `stale_but_findable`, not unresolvable.

```
RESULT backticked_identifier_sites=739     RESULT exact_miss_sites=27
RESULT stale_but_findable_underscore=12    RESULT stale_but_findable_ci=9
RESULT unresolvable_sites=6                RESULT resolvable_fraction=0.9919
```

Then `v2_rename_locator.py` tests the specific hypothesis — the card's
decomposition promoted `_fooBar` methods to classes where the class name absorbed
the prefix. The rule: a counterpart exists if a function in scope has a camelCase
word-list that is a **subsequence** of the token's.

```
RESULT card_dangling=18
RESULT card_dangling_with_live_counterpart=11   (enclosing scope)
RESULT wide_with_counterpart=17                 (anywhere in the card)
RESULT wide_no_counterpart=1
RESULT null_rescue_rate=0.0053       (19/3600)   # scoped arm
RESULT wide_null_rescue_rate=0.0383  (138/3600)  # wide arm
```

Both null rates are **Monte Carlo estimates**, not fixed counts: across repeat
runs the wide arm sampled 0.0383 and 0.0403 (138 and 145 of 3600). Read it as
**~4%**. The scoped arm sampled 0.0053 both times.

**The null control is real, not circular.** My first version drew donor words
from a pool that excluded every in-scope method word, which made a subsequence
match impossible by construction and printed a free 0.0000 — I threw it out. The
version above draws donors from the card's **own** 2922-identifier word stock
without filtering, and synthesises tokens of the same word length that are not
real identifiers. At a ~4% false-rescue rate the wide arm's 17/18 (94%) is not
coincidence.

### What the 27 actually are

**Card, 18 sites — 17 name a function that exists.** I located each by line:

| named in a comment | what it is now |
|---|---|
| `_lineLabel` (3), `_fieldPoints`, `_extraFields` (2), `_seriesUnit`, `_resolveEntity` (2), `_onSlotEdit`, `_laneGroupInner` | the same name without the `_` — module function or method, 11 sites |
| `_refreshLayout` (2) | `LayoutEditor.refresh()` — `:9134`, 199 lines below the comment at `:8935`, in the same class |
| `_applyView` | `ViewWindow.apply(defaultStart, defaultEnd, dataEnd)` — `:4361` |
| `_restoreSlotFocus` | `LaneEditor.restoreFocus(channel, index, svgIndex)` — `:6907` |
| `_runWhatIf` | `WhatIfPanel.run()` — `:7867` |
| `_currency()` | `PlanSource.currency()` — `:4054`, and called as `plan.currency()` on `:5765`, the **next code line after the comment naming it** |
| `_chartWidthDrifted` | **nothing, anywhere** — the one real one |

Two corrections to the finder's own table. It says the last five *"have nothing
under any name — case-insensitive search over the whole 10k-line card returns
only the comment itself"*: true of the literal token, false of the function, for
four of the five. And its `_currency` row says *"`currency` appears only as a
translation key"* — `currency()` is a method at `:4054` with five call sites.
The decomposition these comments predate did land: `ViewWindow` `:4310`,
`LaneEditor` `:6487`, `WhatIfPanel` `:7237`, `LayoutEditor` `:8831` are all real
classes, and `docs/plan-card-decomposition.md:159,168,171` is the rename table.

**Python, 9 sites — 1 is a defect.** Classified by execution:

- Correct references to non-repository names, so not defects at all:
  `__float__` (a Python protocol method), `has_value` ×2 (a Home Assistant
  **template function**, and both docstrings are about what a template sees),
  `tuya_heat_pump` (a third-party integration domain the comment explicitly
  frames as external).
- Shorthand for symbols that exist: `MIN_POWER` → `CONF_HEAT_PUMP_MIN_POWER`
  (`config_flow.py:114`), `UPPER_FLOOR_TEMP` → `upper_floor_temperature`
  (`battery.py:177`), `MixedHotWater` → `MixedHotWaterSensor`
  (`sensor.py:2264`), `current_option` → HA's `SelectEntity.current_option`,
  beside `declares_current_option` (`pump_mode.py:270`).
- **`ProcessPoolExecutor` (`optimizer.py:6455`) — a real defect.** The docstring
  says *"``ProcessPoolExecutor`` has to pickle the callable"*; the route is a
  long-lived `subprocess.Popen` on `process_worker.py` (`coordinator.py:714`,
  `:752-762`, `_run_in_process` `:835`). The class is used nowhere.

**My number: 2 of 739 sites (0.27%) name something a reader cannot find** —
`_chartWidthDrifted` (`heatpump-optimizer-card.js:9943`) and
`ProcessPoolExecutor` (`optimizer.py:6455`). Seventeen card sites carry a stale
`_` prefix across a refactor; seven Python sites are correct prose the harness
cannot recognise.

### Severity

Unchanged at **low** — nothing user-visible, and the finder's own framing
("squarely the brief's *comments that are wrong*") is right in kind. But the
headline is inflated roughly **13x** against its own wording, and the report's
"sharp end" paragraph — the part a judge would act on — is false for four of the
five names it lists. A fixer handed "5 functions the reader cannot find at all"
would go looking for five deletions and find one.

**Vote: weaken, low.** Executed number **2** unresolvable sites of 739
(finder's metric 27, reproduced exactly; 17/18 card sites rescued at a measured
~4% false-rescue rate).

---

## D5-03 — verify, severity low

Reproduced: `broken_links_total=1`, `broken_file_links=0`, `links_scanned=338`,
`markdown_files=98`, load1 5.46.

**My own instrument, my own slugger** (`v2_anchor_and_supersession.py`), with an
extra generosity arm the finder does not have — a heading also matches if the
fragment equals its slug **with all non-alphanumerics removed**, so a pure
punctuation difference cannot manufacture a dead anchor:

```
RESULT readme_headings=36   RESULT readme_same_doc_anchor_links=6
RESULT readme_dead_anchors=1
  #switch-and-climate-entity   closest heading slug: #switches-climate-and-datetime-entities  (token overlap 0.29)
```

Still dead under the looser rule. The 0.29 overlap matters: this is not a typo
of a section that exists under slightly different punctuation, it is a reference
to a section **name** that does not exist. The heading is
`### Switches, climate and datetime entities` (`README.md:494`); the anchor is
singular and omits "datetime".

**Attack on the denominator.** "1 of 338 links" is the wrong frame and it
understates. Of README's **6** same-document anchor links, **1 is dead** — and
it is the first of the three in the `README.md:194` sentence whose entire job is
to route a reader to the control path their hardware supports
(*"Each path in full: …"*). The other two resolve. On GitHub the first link is
inert. That is 1 of 3 in the paragraph, not 1 of 338.

Severity stays **low**: the section is 300 lines below, reachable by scrolling
and by the README's own structure, and the two working links disclose the
pattern.

**Also settled, as a by-product: external links.** The finder correctly claimed
nothing, having got 211/211 `URLError` — that was the sandbox's missing CA
bundle, not the links. Re-run with `certifi` (`v2_external_links.py`):

```
RESULT external_urls_distinct=211   RESULT external_ok=208
RESULT external_dead=3
RESULT external_dead_user_doc=0     RESULT external_dead_dev_record=3
RESULT probe_failures_inconclusive=0
```

All three dead are synthetic fixtures under
`.claude/workflows/fixtures/policy-loop/` (`example.com/not-an-issue`, and two
`issues/9002` / `pull/9001` placeholders). **Zero dead external links with a
user-facing source, and zero inconclusive probes**, so the zero is a real zero
and not a swallowed refusal. There is no external-link finding to make.

**Vote: verify, low.** Executed number **1** dead anchor (of 338 links scanned;
of 6 README same-document anchors; of 3 in the `:194` navigation sentence).

---

## D5-04 — verify, severity low

Reproduced: `superseded_docs_without_forward_pointer=1`,
`readme_links_to_superseded_doc=1`, load1 5.46.

**My own instrument, independent detection.** The finder matches a supersession
statement one way; I match **both** directions (`X supersedes Y` and
`Y is superseded by X`) across every markdown file in the tree, and resolve by
filename **stem** rather than by the literal path string:

```
RESULT supersession_pairs=1        docs/plan-2026-09-open-issues.md supersedes docs/plan-open-issues.md
RESULT stale_plan_links=1          README -> docs/plan-open-issues.md (successor unlinked)
RESULT forward_pointer_missing=1   docs/plan-open-issues.md never names its successor
```

Same answer by a different route. Confirmed by reading: `README.md:786` —
*"alongside the open-issues program ([docs/plan-open-issues.md](…))"* — inside
`## Project status` at `:775`. The current plan is linked from nowhere in README.

**Attacks.**

- **Is the aggregate one defect counted twice?** No — the perturbation table
  above shows the two metrics move independently. Adding a forward pointer fixes
  one and leaves the other at 1; linking the successor from README does the
  reverse. Two separable defects.
- **Is the severity earned?** Weakly, and `low` is right. `plan-open-issues.md`
  is a development record, not a user document; the consequence is that a reader
  who follows README's Project status reads a **completed** plan (covering
  #86–#101) believing it is the live one, with nothing in the document saying
  otherwise. No functional consequence, no wrong configuration.
- **Is `readme_index_omissions=4` part of this finding or padding?** It
  reproduces (`docs/automations.md` plus the three plan documents), but three of
  the four are development records whose absence from a user-facing index is
  arguably correct. Only `docs/automations.md` — a genuine user document, cited
  from README's Services section and from `configuration.md:55` — is an index
  omission that costs a reader anything. I would not carry the `4` as stated.

**Vote: verify, low.** Executed number **1** supersession pair, both halves
broken (README links the superseded document and not its successor; the
superseded document carries no forward pointer), of 1 supersession statement in
the tree.

---

## Where my numbers differ from the finder's, in one place

| finding | finder's number | mine | why they differ |
|---|---|---|---|
| D5-01 | 10 undocumented / 180 | 10 (their rule) · 8 (mine) · 17 (strict) | my 200-char window rule rescues 2 by coincidence; measured false-rescue rate 31% vs their rule's 22%. Both rules over-count *documented*, so 10 is a floor |
| D5-02 | 27 "exist nowhere" | **2** unresolvable | 17 of 18 card sites name a function that exists post-refactor; 7 of 9 Python sites name correct external or shorthand identifiers |
| D5-03 | 1 of 338 | 1 of 6 README anchors, 1 of 3 in the `:194` sentence | different denominator; same defect |
| D5-04 | 1 + 1 | 1 + 1 | same, by a two-directional regex and stem resolution |

---

## Read after my numbers were fixed: where I differ from seat 1

Per the contract I formed every number above before opening `verify-1.md`. This
section is only the metric-definition diff, and two places where our executed
numbers actually conflict.

**We agree, independently, on:** the four harness re-runs; the stale
`option_fields_rendered=174` header line; that the finder's rule (d) is
over-generous and its 10 is therefore a floor; that the wood-fuel group is
genuinely undocumented in every user-facing document; that the finder's
`_currency` table row is false; that the Python misses include correct
references to non-repository names; and D5-03 and D5-04 at `verify`/`low`. Our
external-link runs match exactly — 211 distinct, 3 dead, the same three
synthetic fixtures, 0 with a user-facing source.

### D5-01 — same instrument reading, opposite severity vote

Seat 1 votes `weaken`/`low`; I vote `verify`/`medium`. Our **corpus
definitions differ**: seat 1 measures four corpora (7 docs, `configuration.md`
alone, 12 README-reachable, every `.md`); mine is one BFS-derived corpus of 8
(the 7 plus `DISCLAIMER.md`) with development records excluded by path rule.
Both land on the same ten fields.

Our **counts converge from opposite directions and bracket each other**: seat 1
hand-adjudicates the seven fields its two rules disagree on and gets **12 of
180**; my strict verbatim arm gets **17**; my null control puts the finder's
rule at a **22.1%** false-rescue rate on synthetic labels. Seat 1's 12 sits
inside my 10–17 bracket and is the better point estimate — it is the only one
of the three produced by reading the lines rather than by a rule.

The severity split is a genuine disagreement about which consequence counts,
not about a number:

- Seat 1 rests `low` on **actuation**: the advisor is diagnostic, the solver
  never chooses wood, README:469 says *"never lights the stove"*, so a misread
  field moves no money. That is correct and I did not measure it.
- I rest `medium` on **troubleshooting**: `README.md:483` documents the
  `wood_cheaper` entity and gives *one* of its six availability conditions,
  while the four undocumented fields are the other gates
  (`binary_sensor.py:203-206` → `wood_fuel.py:428` → `wood_fuel_ready`
  `:86-109`). A user whose entity never appears is sent to the wrong cause with
  no user-facing text naming the right one.

Seat 1's argument does not defeat mine — nothing about advisory-only makes the
README's availability sentence less wrong — and mine does not defeat seat 1's.
I hold `medium`, and flag for the judge that this is the one severity call on
the panel that turns on a judgement, not a measurement. Note that seat 1 routes
the same underlying issue to D6 (README's index claiming *"Every setup field
and options page"*), so both of us found a false user-facing doc claim in this
area; we differ on whether it lifts D5-01's severity or belongs wholly to D6.

### D5-02 — same measurement, opposite inference; this one is resolvable

Seat 1 votes `verify`; I vote `weaken`. **Our raw measurements do not
conflict.** Seat 1 measures that the tokens `refreshLayout`, `restoreSlotFocus`,
`chartWidthDrifted`, `applyView`, `runWhatIf` occur 0 times in the card's
non-comment text. I measured the same thing and agree.

The difference is the **metric definition**. Seat 1's existence test is
*token occurrence*; mine is *can a reader find the function* — exact match, then
underscore dropped, then a null-controlled subsequence rule for the
decomposition's renames. Under mine, four of seat 1's "sharp five" resolve, and
I give the line:

| token, 0 occurrences | the function, located |
|---|---|
| `_refreshLayout` | `LayoutEditor.refresh()` — `:9134`, same class as the comment at `:8935` |
| `_applyView` | `ViewWindow.apply(defaultStart, defaultEnd, dataEnd)` — `:4361` |
| `_restoreSlotFocus` | `LaneEditor.restoreFocus(channel, index, svgIndex)` — `:6907` |
| `_runWhatIf` | `WhatIfPanel.run()` — `:7867` |
| `_chartWidthDrifted` | **nothing** — the one that survives both rules |

`wide_null_rescue_rate` ~0.04 (138–145 of 3600 synthetic same-length tokens
across repeat samples) says this is not a rule that rescues anything put to
it.

**Seat 1's own new evidence supports the rename reading.** It reports a 19th
site, `_onWhatIfInput`, kept alive only by `tests/card_drift.mjs:149`:
`c.whatIf ? c.whatIf.onInput(ev) : c._onWhatIfInput(ev)`. The live branch calls
`onInput` — and `WhatIfPanel.onInput(ev)` is at `card.js:7647`. That shim is a
rename record, and it makes seat 1's 19th site a 19th *stale prefix*, not a 19th
missing function. Seat 1's scope extension (16 further sites in `tests/*.mjs`)
widens the same stale-prefix class; it does not widen the two genuine misses.

We also both correct the finder's `_currency` row and both count five call
sites. **Seat 1's five line numbers are drifted and mine are not.** Seat 1 cites
`:3752, :5260, :5676, :8891, :9167`; a raw `grep -n "\.currency()"` on the
untouched file shows those lines hold `return "";`, an SVG path fragment, a
closing brace, `const ed = this.edit;` and a comment. The five real call sites
are **`:4069, :5765, :6254, :9708, :10010`**, with the definition at `:4054`
(where we agree). Seat 1 diagnosed exactly this class of bug in its own first
pass — blanking block comments in a way that eats newlines — and reported it
corrected; this row indicates the correction did not reach it. Its *count* of
five is right.

### D5-03 / D5-04 — complementary, no conflict

Seat 1 attacks breadth (image links, raw HTML anchors, reference-style links;
ten supersession phrasings). I attack the rules themselves (a slugger arm that
ignores all punctuation, so a punctuation-only difference cannot fake a dead
anchor; a two-directional supersession regex resolving by filename stem) and
the denominator (1 of 6 README same-document anchors, 1 of 3 in the `:194`
navigation sentence, rather than 1 of 338). Both routes confirm both findings.
