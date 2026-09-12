# The open-issues program, September 2026

Written 2026-09-03 against `main` at `4b6e076` (v6.3.9, eight merges
unstamped). This is the worklist for every issue open at that moment — 61 of
them — planned in one pass after three sessions stood down and handed over
(`tvofi-claude-09` and `tvofi-claude-40`, both on #201; `cloud-ratchet` is
one-way). What those stand-downs established that is still in force was folded
into `docs/HANDOVER.md` when the dated handover series was retired (#518).

It supersedes `docs/plan-open-issues.md`, which covered #86–#101 and is
complete. The audit register stays `docs/audit-2026-09.md`; this file is the
delivery plan, that file is the evidence.

**Session:** `tvofi-claude-web`, label `owner:claude-web`, branch prefix
`claude-web/` — an identity, not a runner; see Model routing, every seat is a
Cursor Task agent. Owner decisions recorded 2026-09-03: full merge-and-stamp
authority under the standing protocol; #372, #373 and #374 released from
`owner:cloud-ratchet` to this session on the owner's instruction; the triage
judge settles the money-attached questions with numbers; the #193
decomposition program runs to its end state.

## Why this order

Five principles decide it, each a measured fact rather than a preference.

1. **Instruments before the fixes they judge.** `structure.py --record` cannot
   tell an improvement from a regression (#370), headroom never fails (#350),
   `duplication_blocks` has never been able to fire (#369), the ratchet has no
   method-level metric (#374), `stamp.py --self-test` has never run (#372) and
   the closure table contradicts the INERT list (#357). Every later wave is
   judged by these, so they land first.
2. **Budget-table writers never run in parallel.** `tests/structure_budgets.json`
   is rewritten by six separate pieces of work; one at a time, each rebasing
   on the last.
3. **A behaviour fix in a region lands before that region's move PR.** A fix
   inside relocated lines is reverted silently by the move's rebase, with no
   conflict and no failing test — #324 nearly lost that way inside #340.
4. **Fixture-movers share a fork and a stamp**, and a mover never claims a
   fixture that is already `may-drift` (`env_drift.may_drift_error` refuses
   the pair).
5. **Measure-first issues are triaged, not coded.** Eight close on a number;
   nine are re-scoped before a fixer is spent on them.
6. **A check that judges a window lands before the tag that empties the
   window.** The `record` job measures `<last v* tag>..main`, so a release
   stamp resets its window to near-nothing. Tightening it *after* a stamp
   means it lands against almost no merges and goes green because there is
   nothing left to judge — a check over an empty set, which is the shape this
   programme keeps finding rather than a proof. Tightening it *before* the
   next stamp means it lands against every merge then in the window — 31 at
   `d08a56a`, and growing — two of which are known to satisfy it only by
   accident. So the record check's
   anchor rewrite runs **after `10-adr-corpus` closes the queue** — the check
   does not exist until `07-loop` lands, and `06b-record3` supplies the rows
   that let a stricter rule pass — **and before the next release stamp**.
   Measured at `d08a56a`, this branch's own merge base: **31** merges in the
   window, 28 satisfying the current bare-token rule, 26 satisfying an anchored
   one, and 0 failing an anchored one once this pull request's rows land. The
   base is named because the window grows with every merge — an earlier draft
   said 30, which was already stale when it was written.

## Delivery status

Updated as the program lands; each row names the release that carried it.
Where this table and a wave body disagree, this table is the truth.

| Wave | Scope | Issues | Release | Status |
|---|---|---|---|---|
| 0 | stamp REST fallback (#376); then #367, #368 | #364, #282 | **v6.3.10** | **done** — all three merged, both reviews `merge`, tag `d7fa97f`, 0 unstamped |
| triage A | closed or re-scoped on a measured number | #197 #233 closed; #195 #244 #325 #334 re-scoped | — | **done** |
| 1a | the stress ruler, alone on an idle box | #346 | v6.3.11 | **done** — W1-G7 merged PR #378 (`291ae76`), 0 unstamped |
| triage B1 | read-only judges, run beside the ruler | #281 #225 closed; #303 #224 #193 re-scoped | — | **done** |
| triage B2 | solver, suite, browser and timing judges | #304 #258 re-scoped; #242 weakened to a structural zero; **#291 closed** (keep `_MULTI_START_SOLVES=4`); **#232 scoped** (smooth top-k alone → W3-G1) | — | **done** |
| 1b half I | gate instruments, suite gaps, ratchet, entity pins | 16 issues in 7 groups: #369 #370 (W1-G1), #350 #374 (W1-G2), #372 #357 (W1-G3), #373 (W1-G4), #334 (W1-G5), #247 #248 #249 #250 #251 #252 (W1-G10), #246 #251 #395 (W1-G11) | **v6.3.12** (tag `84a27b6`) | **done and released, 2026-09-04** — all seven groups merged, issues closed: PR #383, #406, #397, #384, #386, #385, #402 (merge SHAs in `.claude/workflows/wave-1b-groups.json`, each group's `resume.merge_sha`). `main` green after every merge, head `841fe0f`, stamped `84a27b6`. Five more PRs landed in the same run with no tracked issue of their own — #396 (roster/plan truth-up), #399 (the #387 coverage-floor backstop), #407 (operational docs), #409 (the ratchet-raise policy), #410 (claim priority) |
| 1b half II | card contrast/geometry, coordinator loaders, wood_share, may-drift partition, layout-editor recovery | 12 issues in 8 groups: #288 (W1-G6), #238 (W1-G8), #260 #261 #263 #266 (W1-G12), #262 #258 (W1-G13), #403 (W1-G16, added 2026-09-04), #265 (W1-G14), #254 (W1-G15), #245 (W1-G9) | **v6.3.13** (tag `f94ae13`) | **done and released, 2026-09-05** — all eight groups merged, issues closed: PR #419 (`7cc75a1`, W1-G6/#288), #421 (`a7c1e54`, W1-G8/#238), #424 (`47ded95`, W1-G14/#265), #427 (`598c83d`, W1-G15/#254), #431 (`cabcce1`, W1-G9/#245), #428 (`6bee53f`, W1-G12/#260 #261 #263 #266), #432 (`1801b76`, W1-G13/#262 #258), #433 (`ac35bf8`, W1-G16/#403). Record/tooling since v6.3.12 stamp: #414/#398, #415, #417, #418, #416/#411, #420, #426, #413; inherited-card-claims fix `7044a27` before stamp. Stamped `f94ae13`, 0 unstamped |
| — | **#387, the blocker**: the basin coverage floor is runner-dependent | #387 | v6.3.12 | **fixed** — merged as `32f309f` (PR #388); sixth acceptance criterion ruled (comment 5541519696): the WORK-channel stale-cheap downgrade is kept as necessary to the `env_drift` shape, and the coverage floor's strictness is restored by a follow-up PR that hard-codes it |
| 2 | coordinator lifecycle, learners, options grouping | #236 #237 #240 #239 #243 #283 #284 #277 #244 #325 #279 #278 #280 #198 | **v6.3.14** (tag `ef539be`) | **done and released, 2026-09-05** — seven groups merged, issues closed: PR #437 (`44a6351`, W2-G1/#236 #237 #240), #440 (`90c71c4`, W2-G2/#239 #243; duplicate #441 closed unmerged), #444 (`dc3bb8e`, W2-G3/#283 #284), #447 (`851c555`, W2-G4/#279 #278), #449 (`f492b1f`, W2-G5/#277), #451 (`efe5a27`, W2-G5 follow-up/#244 #325, review `merge` 5551113810: mid-step abort 36→0, 21 leftovers named), #438 (`e1a14f9`, W2-G6/#280), #436 (`3c141d7`, W2-G7/#198). Record/tooling since v6.3.13 stamp: #434, #435, #439, #442, #443, #446, #448, #450. Stamped `ef539be` as v6.3.14. Next seat **W3-G1** |
| 3 | solver, DHW planner, GIL process route | #232 #234 #289 #290 #199 | **v6.3.15** (tag `f0866c8`) | **done and released, 2026-09-06** — three groups merged, issues closed: PR #454 (`1585435`, W3-G1/#232 #234), #455 (`aa61130`, W3-G1 follow-up), #456 (`ebf7170`, W3-G2/#289), #461 (`8542e51`, W3-G3/#290 #199; review `merge` at `7076075`, comment 5554485684). Record/tooling since v6.3.14 stamp: #452, #458, #459, #468, #469. Stamped `f0866c8`. **W3-G4 is struck**. Everything after this tag was stamped by **v6.3.16** and **v6.3.17**; the individual PRs are named in the rows below and in the record-PR class, not summarised as a range here — a range reads as complete while naming a fraction of what it covers |
| **3L** | mid-programme leftovers, one burst | #400 #401 #404 #405 #408 #457 #460 #463 #465 | after Wave 3 | **done** — **3L-G1** #470 (`81aa0c3`). **3L-G2** #472 (`2abe2f7`). **3L-G3** #474 (`e8adfe4`) + #479 (`8ea27d4`) + #480 (`162e759`). **3L-G4** #477 (`531d8b7`). **3L-G5** #483 (`6f02b8a`) closed #408. **3L-G7** #485 (`bf08217`) closed #460. **3L-G8** #487 (`a19ba03`). **3L-G9** #489 (`b29fd1e`) closed #463. **3L-G10** #492 (`e4bc375`) closed #465. **3L-G6** (#457) never implemented: the seat returned NEEDS_CONTEXT (no production `conflict` symbol; nearest twins are read-only `setup_overview` and `reconfigure`), and the owner then closed #457 as `COMPLETED` by hand on 2026-09-06T03:40:23Z with no PR and no commits. Discharged, not blocked — do not reopen it and do not invent a backend. **W4-G6** (S5) merged #529 (`8281f54`); **W4-G7** (S6) merged #537 (`d04ed89`); **W4-G8** (S7) merged #551 (`0f9eb71`); **W4-G9** (S8) merged #555 (`52d38d9`); **W4-G11** (S10) merged #543 (`e072b2d`, closed #304). Next is W4-G10 (S9, #224). Do not stamp. #481 leftover closed. #412 stays last of the programme |
| 4 | the #193 decomposition programme, S0–S13 | #193 #223 #224 #225, and **#304 as S11's precursor** | one per stage | **CLOSED — S0–S13 delivered or recorded-halted; #193 closes with the W4-G14 close-out, #740 (its row below)** — S9 landed in eight pull requests (#557, #586, #631, #642 the recorded optimize 30–50 halt, #646, #657, #663, #666) and **#224 closed 2026-09-10** on the owner's instruction with stage 5 delivered as a design brief on the issue; **S12 (W4-G13) is a recorded halt, #637 (`30a202e`)** — no subsystem API to migrate tests to, re-confirmed at the close-out's merge base, the S0/S1 facades stay, and the seam moves once sequenced to S12 are owed by no stage; S11 #597 (`0323c5b`), which **shut #223** — it is CLOSED — S0 #497 (`c197b01`), S1 #500 (`67e1cf3`, closed #377; **corrected 2026-09-06**: the reported 138-point drop across all five cuts was `structure.py` losing sight of `getattr(self, "_ctx", self)` references S1 introduced 131 of, not decoupling — fixed by #512, S1's other results (`CoordinatorContext`, the attribute count, the facades) stand unchanged), S2 #502 (`d979110`, review `merge` 5558785350), S3 #506 (`5a4e6ff`, review `merge` 5559638736 at `258b245`: cut_views 94→85, coordinator_loc/max_class_loc 10305→10164, functions_cc_over_15 39→38, methods_over_150 21→20; earlier `blocked` 5559418212 at `341c596` cleared). **S4 (W4-G5, fetch) is a RECORDED HALT, merged as `e46fb15` (#508), with no production change** — measured then as 92 of cut_fetch's 115 being other seams reading the 15 fetch-owned attrs (60) and calling into fetch (32); **re-measured after #512**, cut_fetch is 132, not 115 (the whole +17 is fetch's own reads of attributes it does not own, previously invisible through the same idiom — see the roster note for the full recount), the other-seams-reaching-in share is unchanged in absolute count at 92, and the halt's actual basis — the judge's #193 finding that no component of size>1 detaches at any k — is untouched, so the seam move stays sequenced to S12/W4-G13, not banned. **S5 (W4-G6, dhw) merged as `8281f54` (#529, review `merge` 5561488083)**: cut_dhw 194→103 (-91, -47%), cut_learning 350→321, total cut across all five seams 1022→902 and `core` 15→14 (the control that distinguishes a real decoupling from moving points to a neighbouring seam). **The constraint S5 produced, carried into the W4-G7/G8/G9/G13 briefs:** the ownership lever is legitimate only where a seam's entire contact with an attribute is the assignment — no reads, no other writes — demonstrated per attribute, never assumed; `_helper(self, ...)` at S3 and `getattr(self, "_ctx", self)` at S1 were both refused on exactly that. Measured by moving twelve non-hot-water attributes `_init_dhw_learning` misplaced into a new `_init_thermal_learning` (learning seam). #193 closed by W4-G14. Roster `.claude/workflows/wave-4-groups.json`. #225 stays closed. #412 not in this wave. Do not stamp |
| R | reliability, instruments and harness — hotfixes and findings made alongside Wave 4, not wave work | #510 #511 #513 #518 closed | v6.3.16 (`#512`, `#515`); unstamped (`#517`, `#519`) | **delivered 2026-09-06** — #512 fixed `structure.py`'s cut-walk blindness to `getattr(self, "_ctx", self)`, closed #510; #515 fixed the release-critical unpickle failure (every install produced no plan), closed #511; #517 added `tests/deployment_shape.py`, closed #513; #519 consolidated the handover series into one file, closed #518. Detail below |
| UX | the UX programme: **34 items in five lanes**, B/C/D/E concurrent with the waves, **F immediately after Wave 5 and #412** (owner, 2026-09-10) | tracking **#558**; items land under their own numbers (#509 done, #516 = E4) | **B, C, D, E and F are all on `main`** | **lanes B, C, D started 2026-09-07; B, C, D and E all merged by 2026-09-09.** **F landed as [#891](https://github.com/tvofi/heatpump_optimizer/pull/891) `67a61fb`, which closed #558.** Read the delivered state from `.claude/workflows/wave-ux-groups.json`, not from a count here. Docket: the *Optimizer UX Docket* artifact. Independence is by **file**, not only by budget — see the collision table below |
| 5 | typing lane, and the coverage deficit #195 raised | #303 #195 | per tranche | **#303 CLOSED 2026-09-11: the census reads 0, from the 427 the issue records** — W5-G1 through W5-G4 all `done` (#596, #636, the W5-G3 batches #705/#758/#765, and #769 plus #770 for the last two modules). The two owner decisions that took the final four errors are `scipy-stubs` in the ruler's pinned third-party set and `max_cc` 48 → 50 for a narrowing. **Seam moves: W5-G9 `done` (#750), W5-G10 `done` (#771)** — `coordinator_loc` 9999 → **9093** across the two, `cross_seam_edges` 145 → 140, `classes_over_300` raised once per move on the owner's word. **#195 is what remains of this wave**: W5-G7 (`coordinator.py` to the 95 % bar) has merged tranches 1 and 2 — [#788](https://github.com/tvofi/heatpump_optimizer/pull/788) (`eb4d5b7`) and [#812](https://github.com/tvofi/heatpump_optimizer/pull/812) (`2684125`) — and has merged tranches 3 and 4, [#842](https://github.com/tvofi/heatpump_optimizer/pull/842) (`26105cb`) and [#858](https://github.com/tvofi/heatpump_optimizer/pull/858) (`cb424f9`), and tranche 5, [#867](https://github.com/tvofi/heatpump_optimizer/pull/867) (`c31beb5`), taking `coordinator.py` to **94.1 %**. **Tranche 6 is the last and stays with the `start-prompt-review-c8f8c2` seat**, which keeps #195; W5-G8 (the residual) is `pending`. **The owner raised the bar to 98 % on 2026-09-11**, from the plan's 95. Measured at `c31beb5`: 219 missed against 73 allowed, so **tranche 6 must cover 146**, spread over 89 methods whose top twenty hold only 100 — many small fixtures rather than a few deep ones, and splitting it across two or three pull requests is reasonable. At 98 % there is no room for a residual, so that tranche's body must name every statement it leaves and why it is unreachable. Its brief carries the five rules the mutation tables cost, the twenty-five subsumed guards, and the handover debt; it says to re-measure rather than carry a figure. No coverage figure is read from this table. |
| last | CI Node majors, then **UX lane F** | #412, then UX F1/F2 | after Wave 5 | **#412 CLOSED 2026-09-11** by [#767](https://github.com/tvofi/heatpump_optimizer/pull/767) (`c504e3a`): every action that still declared `node20` is on its lowest `node24` major, 48 occurrences over seven usages, and the set was larger than the three the deprecation warning names. **Lane F landed as [#891](https://github.com/tvofi/heatpump_optimizer/pull/891) `67a61fb` and closed #558.** #195 remains theirs — W5-G7 tranche 6 and W5-G8. |
| feat | seven product features from the 2026-09-09 ideation | #703 #701 #697 #698 #700 #699 #702 | after Wave 5 / own PRs | **Shipped on `main` as [#707](https://github.com/tvofi/heatpump_optimizer/pull/707) (`c2e9200`).** Pulse (#703), Nord Pool entity (#701), 15-min clock (#697), DSO catalog (#698), weekend/holiday profiles (#700), sensor-gap € (#699), wood-burn advisor (#702). Issues CLOSED completed. Not wave work. leaves #195 #303 open |

### The UX programme (#558) — what B1 measured, and what it binds

Lane B's first item asked a question this repository's own records left open
(`round2/D5/REPORT.md` at `d5d8c4a`, "Whether HACS's in-app README view renders
mermaid was not checked"). It is answered, by execution rather than argument,
and the answer constrains every later item that adds a figure.

**Mermaid does not render in HACS's in-app README view.** HACS reads `README.md`
as `additional_info` and passes it to `<ha-markdown>` with no `allow-svg`; that
is home-assistant/frontend's `markdown-worker`, which is plain `marked` plus
js-xss over a whitelist carrying no `svg`. A fence comes out as a literal
`<pre><code>` dump of its own source, and the `language-mermaid` class is
stripped with it, so nothing downstream can find it either. Control: rendering
the README through that exact pipeline (marked 15.0.4, xss 1.0.15 — the
versions hacs/frontend pins) yields zero `<svg>` elements, while a GFM table in
the same document is still wrapped by the worker's own `table` renderer, so the
pipeline is demonstrably running.

What this binds:

- **B6-B8 may not ship a diagram as mermaid alone.** A figure that must reach a
  Home Assistant user is an image. `docs/*.md` is not rendered by HACS at all,
  so a mermaid figure there is a GitHub-only figure — legitimate, but state
  which audience it serves.
- **A README image must survive HACS's rewriter, and the rule below is the
  rewriter's *behaviour*, not a list of the shapes that have broken so far.**
  This constraint has been carried three times and stated too narrowly twice;
  each restatement enumerated the shapes then known, and each time an ordinary
  construct obeying every listed rule still shipped blank. So read the
  mechanism and derive your own case, rather than matching your figure against
  the examples.

  Two lines of `markdownWithRepositoryContext` produce all of it. It matches
  `\[.*?\]\([^#](?!.*?:\/\/).*?\)` and then calls `x.replace("(", <prefix>)`,
  which rewrites **the first `(` of the matched span** — not the image's; and
  `showGitHubWeb` tests **the whole span** for `.md`. Whatever is left relative
  is then blanked by js-xss, which keeps a `src` only if it is absolute or
  `/`-, `./`-, `../`-rooted.

  **Read "the span" literally, because it is the part that keeps being got
  wrong.** The span is the rewriter's own match, and that regex is global and
  scans left to right from the start of the document, with `\[.*?\]` free to
  open at an unrelated `[` earlier on the line and run through the image's own
  `]`. So the span covering an image routinely **starts left of the image** —
  at a `> [!NOTE]` callout, a `- [ ]` task box, a `[1]` footnote marker, any
  bracketed word — and it is that text which then supplies the first `(`, or
  the `.md`. Every clause below is a property of **that** span, never of the
  `![…](…)` you are looking at. Reading them at the image is exactly what the
  #567 fix review found `tests/entities.py` doing, and it passed four ordinary
  constructs that ship blank or broken.

  A relative-src image therefore reaches a Home Assistant user only when
  **all** of the following hold:

  - **It is an inline `![alt](src)`.** The rewriter touches `](…)` and nothing
    else, so a reference-style `![alt][ref]` and an HTML `<img src=>` are never
    rewritten at all. Control: `![m][r]` with `[r]: docs/img/a.svg` → blank;
    the same with an absolute `[r]:` → renders.
  - **The `(` opening its `src` is the first `(` in the span.** A parenthetical
    caption takes the rewrite instead — and this is the case every earlier
    statement of this bullet permitted. Control, a minimal pair:
    `![Plan chart (24 hours)](docs/img/plan.svg)` → blank `src`, while
    `![Plan chart 24 hours](docs/img/plan.svg)` → rewritten and survives.

    **The parenthetical does not have to be in the alt text, or anywhere near
    the image.** Worked example, and the one to derive from, because the image
    here is faultless read on its own:

    ```
    > [!NOTE] The chart below (updated daily) ![Plan chart](docs/img/plan.svg)
    ```

    The scan opens at `[!NOTE]`, cannot close there (no `(` follows the `]`),
    and runs on to the image's `]` — so the span is
    `[!NOTE] … (updated daily) ![Plan chart](docs/img/plan.svg)`, its first `(`
    is `(updated daily)`, and the `src` is **left relative and blanked**.
    Control, the minimal pair: drop the parentheses —
    `> [!NOTE] The chart below updated daily ![Plan chart](docs/img/plan.svg)`
    → the image's own `(` is first in the span, and it survives. B3 adds a
    `> [!IMPORTANT]` callout to this README, so this is the live shape, not a
    contrived one. `- [ ] (optional) ![…](…)` and
    `See the plan [1] (figure 2) ![…](…)` fail identically, and
    `See [notes] in docs/arch.md ![…](…)` reaches the `.md` clause below by the
    same route.

    The same clause explains the linked-image case: in
    `[![License: MIT](https://img.shields.io/…)](LICENSE)` the span's first `(`
    *is* the image's own, so the badge collects the prefix and its `src`
    becomes `raw.githubusercontent.com/…/https://img.shields.io/…`. That badge
    is live and still unfixed; it needs its own lane-B item.
  - **The span carries no `.md`/`.markdown`.** The rewrite flips to
    `github.com/<repo>/blob/…`, which serves `content-type=text/html` inside an
    `<img src>` — broken rather than blank, and the lesser failure of the two.
    Control: `![Module map — see docs/architecture.md](docs/img/arch.svg)` →
    `github.com/…/blob/…`; the same alt without the `.md` →
    `raw.githubusercontent.com/…`. Scoped to the **span**, not the line: an
    image sharing its line with a `[docs/architecture.md](docs/architecture.md)`
    link is fine, because that link is a separate match.
  - **No `://` follows on the line.** The negative lookahead scans to the end
    of the line rather than to the end of the link, so a trailing "see `<url>`"
    — or an absolute link *target* wrapped around the image — leaves it
    un-rewritten. Control: `![x](docs/img/x.svg) see https://example.com` →
    blank; the identical image alone on its line → survives.
  - **The alt text does not wrap.** The regex is built without the `s` flag.

  None of these is visible on GitHub, which is where a figure is reviewed.
  `tests/entities.py` **runs the rewriter's regex over the README and judges
  each image in the match that covers it** — `_HACS_LINK`, a transcription of
  `\[.*?\]\([^#](?!.*?:\/\/).*?\)`, iterated globally so its left-to-right,
  non-overlapping consumption is reproduced rather than approximated. That is
  the correction the #567 review forced: the check previously built its span
  from the image's own `![`, which cannot see anything to the left of it, so
  the four constructs above passed. Two scope notes: the population is the
  image's own `src` being relative — which is why the `(LICENSE)` badge, whose
  `src` is absolute, falls outside it instead of needing an allowlist — and an
  image inside a fenced block or a `backtick span` is outside it too, since it
  renders as text and never becomes an `<img>`. Re-measure rather than quote:
  the pipeline is two upstream repositories, and this was measured on
  2026-09-07 against marked 15.0.4 + xss 1.0.15.
- **B12 should land after C1-C4.** A hero generated from the card's own renderer
  bakes in whatever the card looks like that day, and today that includes C2's
  colliding time-axis end labels and C1's low-contrast lane labels — both are
  visible in the interim asset at `docs/img/card-plan-chart.svg`.

Re-measure rather than quote: the pipeline is two upstream repositories that
move independently of this one, and the versions above are what they pinned on
2026-09-07.

### Wave 3L — leftovers, after Wave 3, before Wave 4

Every open issue that is not already in Waves 3–5 or #201, filed after the 2026-09-03 plan cut, plus #460 (monthly savings), #463 (wood furnace economics), and #465 (Plan-page away toggle). One burst so they are not lost again, and **before** Wave 4 because #400, #408, #463 and #465 are behaviour in the DHW/optimizer/config/card region a move PR would silently revert (principle 3). Wave 3 is released (`f0866c8`); 3L-G1–G5 and 3L-G7–G10 are done (`e4bc375`). **3L-G6** (#457) shipped nothing and #457 was closed `COMPLETED` by the owner on 2026-09-06 — discharged, not blocked. **W4-G6** (S5) merged #529 (`8281f54`); **W4-G7** (S6) merged #537 (`d04ed89`); **W4-G8** (S7) merged #551 (`0f9eb71`); **W4-G9** (S8) merged #555 (`52d38d9`); **W4-G11** (S10) merged #543 (`e072b2d`, closed #304). Next is W4-G10 (S9, #224). Do not stamp. #465 is closed. #412 stays last of the programme and is not in this burst.

| group | issues | model | after | scope |
|---|---|---|---|---|
| **3L-G1** | #400 | Grok 4.6 extra high | W3-G3 | DHW planner sees the wood-tank refill coil. Measured 5.394 SEK/day; plan is byte-identical coil-on/off today. Claims, never re-record goldens |
| **3L-G2** | #401 | Composer 2.5 | 3L-G1 | `closure.py` `_record_node()` strace availability guard. Unblocks a full derive on macOS. Before #404 |
| **3L-G3** | #404 | Composer 2.5 | 3L-G2 | Gate lock becomes a renewed lease + `flock`. Lives in `tests/`, needs the derive #401 unlocks |
| **3L-G4** | #405 | Composer 2.5 | 3L-G3 | `SolarIrradianceSensor` / `OptimizationScoreSensor` data-driven keys: state the bound in the holes list, no exact-set pin |
| **3L-G5** | #408 | Grok 4.6 extra high | 3L-G4 | Optional set-point entities + **consistency** repair issue only. Optimality / Fix-to-argmin half is refused (50→65 °C instability) |
| **3L-G6** | #457 | Composer 2.5 | 3L-G5 | Card setup-page button that opens the conflict flow. Card-only. **Not implemented** — no production `conflict` symbol; #457 closed `COMPLETED` by the owner 2026-09-06 |
| **3L-G7** | #460 | Grok 4.6 extra high | 3L-G6 | Monthly savings history card page. Realised thermostat-baseline ledger lines; calendar pro-rata for the open month. After #457 (or after #408 if #457 stays blocked). Spec/plan `docs/superpowers/{specs,plans}/2026-09-05-monthly-savings-history*.md` |
| **3L-G8** | #463 | Grok 4.6 extra high | 3L-G7 | Wood-furnace toggle, firewood price, `wood_fuel.py`, cheaper-than-pump sensor. Does not close #463. Spec/plan `docs/superpowers/{specs,plans}/2026-09-05-wood-furnace-economics*.md` |
| **3L-G9** | #463 | Grok 4.6 extra high | 3L-G8 | Plan banner, Wood lane, what-if wood slots. `Closes #463`. Same spec/plan |
| **3L-G10** | #465 | Grok 4.6 extra high | 3L-G9 | Plan-page Away toggle and return datetime. Service-backed store; published switch and datetime; optional person/calendar. `Closes #465`. Spec/plan `docs/superpowers/{specs,plans}/2026-09-05-away-plan-toggle*.md` |

Do not fold 3L into a closed Wave 3. 3L-G10 merged as #492 (`e4bc375`); #465 closed. W4-G1 #497 (`c197b01`), W4-G2 #500 (`67e1cf3`), W4-G3 #502 (`d979110`) and W4-G4 #506 (`5a4e6ff`) merged; #377 closed. W4-G5 (S4, fetch) recorded a halt with no production change, merged as `e46fb15` (#508). W4-G6 (S5) merged #529 (`8281f54`); W4-G7 (S6) merged #537 (`d04ed89`); W4-G8 (S7) merged #551 (`0f9eb71`); W4-G9 (S8) merged #555 (`52d38d9`); W4-G11 (S10) merged #543 (`e072b2d`). W4-G10 (S9) landed eight pull requests and #224 closed 2026-09-10; W4-G13 (S12) is a recorded halt (#637); Wave 4 is closed by W4-G14 (S13). Do not stamp or start #412 from this record.

### Wave 4 — #193 decomposition, S0–S13 (closed 2026-09-10 by W4-G14)

Roster: `.claude/workflows/wave-4-groups.json`. Serial, one group per stage. Worker briefs live out of tree under `/Users/timmalmstrom/wt/briefs/w4-gN-*.md` (same convention as 3L). **#223 issue text allows parallel with coordinator moves; this table does not authorize a second lane.** Plan numbers the registry as **S11**; #193 numbers it S10 — the issue number is the stable reference. **#304 is S11's precursor** (W4-G11), not Wave 5. **#225 is closed** (triage B1) — struck in the roster, do not reopen. **#412 is not in this wave.** **#457 / 3L-G6 is not Wave 4**, and #457 is closed `COMPLETED` (2026-09-06) with nothing shipped — do not go looking for that work. S2–S8 and plan S12 have no child issue: they track #193 and must not `Closes #193`. A survey stage **halts** (record only, no invented backend) when the named seam is not extractable at this merge-base, an open PR holds the region, or a ratchet metric would rise. The `model` column names Claude seats for groups not yet started and the model that actually ran for groups already delivered — see Model routing.

| group | stage | issues | model | after | scope |
|---|---|---|---|---|---|
| **W4-G1** | S0 | #377 | Grok 4.6 extra high | 3L-G10 merge | `CoordinatorContext` defined; nothing relocates. Do not close #377 |
| **W4-G2** | S1 | #377 | Grok 4.6 extra high | W4-G1 | Migrate hub refs; facade properties stay. `Closes #377` |
| **W4-G3** | S2 | #193 (tracking) | Grok 4.6 extra high | W4-G2 | Pure-function extractions. Survey-first; halt if not this seam |
| **W4-G4** | S3 | #193 (tracking) | Opus 5 | W4-G3 | views, thinned, stays the facade. Survey-first; halt if not this seam |
| **W4-G5** | S4 | #193 (tracking) | Opus 5 | W4-G4 | fetch/sources. Survey-first; halt if not this seam |
| **W4-G6** | S5 | #193 (tracking) | Opus 5 | W4-G5 | dhw. Survey-first; halt if not this seam |
| **W4-G7** | S6 | #193 (tracking) | Opus 5 | W4-G6 | grid/bookkeeping. Survey-first; halt if not this seam |
| **W4-G8** | S7 | #193 (tracking) | Opus 5 | W4-G7 | learning A (thermal). Survey-first; halt if not this seam |
| **W4-G9** | S8 | #193 (tracking) | Opus 5 | W4-G8 | learning B (curve/comfort/drift-watch). Survey-first; halt if not this seam |
| **W4-G10** | S9 | #224 | Opus 5 | W4-G9 | optimizer.py judge-corrected splits; `optimize` 30–50 verbatim halted at `30a202e`; #646 non-hot; `solve_space` lifted (hot loop); A-half `_dhw_window_floors` landed; 14-key `DhwPlan` return landed (#666, `da57a2a`); schedule/suppression halves refused by the seam perturbation; stage 5 delivered as a design brief; **#224 closed 2026-09-10 — done** |
| **W4-G11** | S10 | #304 | Sonnet 5 | W4-G10 | 21 named `config_flow.py` statements; test-only; before #223 |
| **W4-G12** | S11 | #223 | Opus 5 | W4-G11 | config_flow settings registry; serial after #304 |
| **W4-G13** | S12 | #193 (tracking) | Opus 5 | W4-G12 | Delegate seams / facade deletion (#193's S11) — **recorded halt, #637 (`30a202e`)**: no subsystem API to migrate tests to, the facades stay; re-confirmed at the close-out's merge base. #195 coordinator half is W5-G7; #374 already done |
| **W4-G14** | S13 | #193 | Sonnet 5 | W4-G13 | Close-out: Delivery-status, roster, audit register, #201. Do not stamp. **#740, this lane's close-out pull request, carries `Closes #193`** — S0–S12 done or recorded-halted and #377/#224/#223 closed; the roster flip to `done` follows in its own record pull request |

### Wave 5 — #303 typing (CLOSED) and #195 coverage (two groups left)

Roster: `.claude/workflows/wave-5-groups.json`. After Wave 4. Serial. **#304 is not here.** **#412 is not here.** #303 is four named tranches (parent may split G3 further). **The seam moves #193 sequenced to S12 are this wave's W5-G9 (dhw profile learner) and W5-G10 (legionella guard), approved by the owner 2026-09-10 from a simulation through `tests/structure.py`'s `seam_metrics`**; W5-G4 and W5-G7 run after W5-G9, W5-G7 in parallel with typing, and #195 closes in W5-G8. Models are the Claude seats of the 2026-09-06 routing.

| group | issues | model | after | scope |
|---|---|---|---|---|
| **W5-G1** | #303 | Sonnet 5 | Wave 4 S13 merge | Land the pinned stub-free ruler. Do not close #303 |
| **W5-G2** | #303 | Opus 5 | W5-G1 | `sensor.py` annotations (142 at filing) |
| **W5-G3** | #303 | Opus 5 | W5-G2 | Remaining modules except `coordinator.py`. Parent may split further |
| **W5-G4** | #303 | Opus 5 | W5-G3 | `coordinator.py` typing after Wave 4 seams. May `Closes #303` |
| **W5-G5** | #195 | Sonnet 5 | W5-G4 | `climate.py` / `open_meteo.py` / `frontend.py`. No coordinator |
| **W5-G6** | #195 | Sonnet 5 | W5-G5 | `diagnosis.py` / `curve_learning.py` / `grid_fee.py` / `switch.py`. Cleanup is not this tranche |
| **W5-G7** | #195 | Opus 5 | W5-G9, W5-G10 | `coordinator.py` coverage — the deficit is read from `tools/audit/w5-partition/partition.py` at the seat's merge base, never carried here — after the seam moves, in parallel with W5-G4 (owner, 2026-09-10). Four regional test-only tranches. Leaves #195 open; W5-G8 closes it |
| **W5-G8** | #195 | Opus 5 | W5-G7 | The residual: every below-bar module that is not `coordinator.py`, enumerated by `partition.py` at the seat's merge base. `Closes #195` on its last pull request |
| **W5-G9** | #193 follow-on | Opus 5 | — | The dhw profile/draws learner leaves the coordinator for one class in a new module: the only candidate under which every ratchet row falls, `cross_seam_fraction` included. `classes_over_300` rises by one (owner-approved). **Merged as #750 (`6978107`).** Leaves #193 closed; no closing keyword |
| **W5-G10** | #193 follow-on | Opus 5 | W5-G9, R1 | The legionella guard leaves the coordinator; gated on R1, which replaces `cross_seam_fraction` with the absolute cross-edge count because a cohesive extraction raises the ratio while the count falls. Policy-adjacent, owner approves R1's merge |

### Reliability, instruments and harness — delivered 2026-09-06 (not a wave)

The Delivery-status table above accounts for wave stages and their records.
It does not, on its own, account for the other kind of work this session
produced: hotfixes, an instrument repair and a harness gap, found while
doing something else rather than surveyed into a stage. It is not Wave 4 work
and is not forced into that table beyond the summary row above.

| PR | what | issue | state |
|---|---|---|---|
| #512 | `structure.py`'s cut walk matched only `ast.Attribute` on `ast.Name("self")`, so a reference through `getattr(self, "_ctx", self)` — an idiom S1 (#500) introduced 131 times — had a `Call` as its value and was invisible. The walk now resolves that idiom, the direct `self._ctx` form, and local aliases bound to either. The five cut budgets are re-recorded upward to their true values: `cut_views` 85→112, `cut_fetch` 115→132, `cut_dhw` 160→194, `cut_grid` 209→234, `cut_learning` 315→350 — they rise only because the true number was always higher; no coupling is added | #510 | merged `af47c96`, released **v6.3.16** |
| #515 | the process-solve worker could not unpickle its job on any Home Assistant install. A solve is shipped to the child by pickling a function, and pickle records it by qualified name; under Home Assistant that name begins `custom_components.`, a path the child's search path did not resolve, so every optimization on every v6.3.15 install failed, permanently and silently. Now an unloadable job is reported rather than killing the worker, and a worker fault falls back to an in-process solve | #511 | merged `98a7574`, released **v6.3.16** |
| #517 | `tests/deployment_shape.py` runs the integration under an installation's real module name and directory layout — the gap #513 named as the reason no test caught #511: the suite imports the package under a different name and runs with a `tests/` directory no installation has | #513 | merged `6cd2c28`, **unstamped** (lands after v6.3.16) |
| #519 | one living `docs/HANDOVER.md` replacing the dated handover series (`docs/handover-<date>.md`), with `tests/entities.py` refusing a second dated file from re-forming | #518 | merged `b6a21f1`, **unstamped** (lands after v6.3.16) |

#510, #511, #513 and #518 are closed by the fixes above, not by wave work.

**Every other open issue, with its disposition.** "Not mentioned" is not a
disposition, so each open issue is scheduled, deferred with a reason, or
refused with a reason — and the PR carrying it is named where one exists.

**The completeness check covers three sets, not two.** Open issues and open
pull requests are the obvious two, and checking only those is structurally
blind to the largest set: **merged** pull requests, which by definition stop
appearing in any "open" listing the moment they land. That blindness is not
hypothetical — it hid #491 and #498 among others, #498 being the pull request
that built `closures-autofix`, the job this repository makes load-bearing. **The
count is deliberately not stated here**: the first attempt at it said "twenty",
measured with `--limit 120`, and the re-derivation under the same rule gives a
different answer again. Run the check rather than reading a number off this
page. A **range in prose is not a disposition** either: `#470–#500` reads as
complete and absorbs thirty-one numbers while naming eight. The check is
therefore per-number over all three sets:

```
gh pr list --state merged --limit 300 --json number -q '.[].number' |
  while read n; do [ "$n" -ge 375 ] || continue
    grep -q "#$n\b" docs/plan-2026-09-open-issues.md ||
      echo "MERGED PR #$n has no disposition"; done
```

and the same loop, without the `375` guard, over `--state open` and over
`gh issue list --state open`. **Use a `--limit` that reaches past the oldest
number you are checking** — a truncated listing under-reports silently, and a
`--limit 120` run is what first reported this gap as twenty.

**The scope boundary, stated so the check terminates — and what it does not
claim.** This document is the plan of record for the #201 open-issues
programme, created by **#375** (`8e99ad1`), and it accounts for every pull
request merged **from #375 onward**. Run that check rather than reading its
answer here: every number it names is a row this document owes, and the
answer moves with every merge — which is why no answer is written down.
Without the boundary the loop demands this file account for the entire
repository history and can never come back clean, which is the failure mode
that makes a check get quietly dropped rather than fixed.

**The boundary is a limit on this document's scope. It is *not* a claim that
the earlier work is recorded elsewhere, and an earlier draft of this paragraph
said it was.** Measured against this file **as it stood on `origin/main` before
this paragraph existed**: of the merged pull requests below #375 with no
disposition here, **the great majority appear in none** of the three programme
documents this file cites. No figure is given, for a second reason on top of the
self-reference below: the check pages the listing with a `--limit`, which is a
**sliding window**, so the oldest rows fall out as new work merges and any count
decays by roughly one per merge. Two runs minutes apart disagree. Run it; do not
read it off this page. Those documents reach only into the low hundreds and the double
digits respectively, and `docs/audit-2026-08.md` carries no issue or
pull-request reference at all — so this is not an artifact of citation style.

**Why the baseline is named, and why two figures that used to be here are
gone.** The check is a bare `grep -q "#$n\b"`, which cannot tell a disposition
from an incidental mention. An earlier draft of this paragraph *cited the two
highest-numbered references in those documents by number* — and that sentence
put those tokens into this file, which handed both pull requests a
"disposition" and moved them out of the miss set. The paragraph's own
measurement of itself was destroyed by the act of recording it. So: measure
against a fixed baseline, not the live file, and read every count the check
produces as a **lower bound** on what is genuinely undispositioned.

That gap is real, it predates this programme, and it is **#575**. Naming it is
the point: a boundary that quietly reassigns unrecorded merges to a document
that does not contain them is the same defect as the prose range it replaced —
something that reads as complete while covering a fraction.

| issue | disposition | carried by |
|---|---|---|
| **#504** ruler will not install (Python 3.13.1 < 3.13.2) | **scheduled — W5-G1, as a precondition of it.** The choice between raising the box, re-pinning, or CI-only is made *in* that PR, with its reason | W5-G1 |
| ~~**#505**~~ #195 tranches no longer cover the below-bar tail | **DONE** — closed by [#728](https://github.com/tvofi/heatpump_optimizer/pull/728). The partition is no longer a list of module names, which is the defect rather than the symptom: `coordinator.py` is W5-G7 and **every other below-bar module is W5-G8**, the residual group this PR creates, whose scope a seat reads by running `tools/audit/w5-partition/partition.py` at its own merge base. No coverage figure is recorded here or in a brief — every one the roster carried was superseded before the seat holding it started, twice for `coordinator.py`. The pull-forward this issue asked about is spent: `process_worker.py` was untested when #505 measured it, #540 pinned it the next day and #654 lifted it again, so it is one ordinary member of the residual. leaves #195 open | [#728](https://github.com/tvofi/heatpump_optimizer/pull/728), then W5-G7 and W5-G8 |
| **#509** diagnostics publish home latitude/longitude unredacted | **CLOSED by [#535](https://github.com/tvofi/heatpump_optimizer/pull/535), merged `eda0236`.** Coordinates coarsened; `config.name` redacted. The "land it before #522" sequencing was void: #522's review measured that the lane never calls diagnostics. | shipped |
| ~~**#514**~~ Python floor undeclared, 3.14 untested | **DONE** — closed by #520, merged `36b71dd` | [#520](https://github.com/tvofi/heatpump_optimizer/pull/520) |
| ~~**#516**~~ config-flow options are ungrouped | **DONE** — closed by [#653](https://github.com/tvofi/heatpump_optimizer/pull/653), merged `7e830d6`. Capture landed first in #568, which is docket sequencing rule 4: a capture must see a change before the change is made. leaves #558 open | [#653](https://github.com/tvofi/heatpump_optimizer/pull/653) |
| ~~**#521**~~ no test runs the integration in a real HA install | **DONE** — closed by #522, merged `824fd84`. Residuals recorded, not swept: the lane reaches ~15 of the ~58 container-reachable escapes, and its incompleteness was silent → **#533** | [#522](https://github.com/tvofi/heatpump_optimizer/pull/522) |
| **#523** `closures-autofix` reported success without repairing | **CLOSED by [#528](https://github.com/tvofi/heatpump_optimizer/pull/528), merged `0265cdd`.** An autofix job that reported success without repairing now reddens. | shipped |
| **#524** an unpicklable solve result is returned as the plan | **CLOSED by [#540](https://github.com/tvofi/heatpump_optimizer/pull/540), merged `9da726a`.** An unpicklable solve result raises; it is not published as the plan. | shipped |
| **#525** two blocking calls in the event loop | **CLOSED by [#540](https://github.com/tvofi/heatpump_optimizer/pull/540), merged `9da726a`.** Setup no longer blocks the event loop. | shipped |
| **#527** a full `derive_closures.sh` silently shrinks the node lanes | **CLOSED by [#629](https://github.com/tvofi/heatpump_optimizer/pull/629), merged `92c1bd6`.** A full merge may not shrink a closure. | shipped |
| ~~**#533**~~ the nightly lane's incompleteness is silent | **DONE** — leftover named work is on main: [#751](https://github.com/tvofi/heatpump_optimizer/pull/751) `86c95c3`, [#755](https://github.com/tvofi/heatpump_optimizer/pull/755) `a325ebd`, [#754](https://github.com/tvofi/heatpump_optimizer/pull/754) `76977ee`, [#731](https://github.com/tvofi/heatpump_optimizer/pull/731) `d162b79`, [#763](https://github.com/tvofi/heatpump_optimizer/pull/763) `ba81d36`, `691f109`, `dc03619`. A6/A11/A12/A13 read `done` in the `tests/nightly_ha.py` lane table. Dispatch `34543635655` at `dc03619` is the container execution. The A14 pin and the #588 probe are that control, not leftover. `nightly-status` reports the last scheduled Tests run; it is not leftover. | [#766](https://github.com/tvofi/heatpump_optimizer/pull/766) |
| **#536** `tests/hastub` can diverge from Home Assistant | **CLOSED by [#578](https://github.com/tvofi/heatpump_optimizer/pull/578), merged `6ac7d83`.** `tests/hastub` is measured against Home Assistant rather than hoped. | shipped |
| **#542** saving the learning options page **wipes `external_heat_entity`** | **CLOSED by [#579](https://github.com/tvofi/heatpump_optimizer/pull/579), merged `52c83d1`.** Saving the learning page no longer wipes `external_heat_entity`. | shipped |
| **#559** B1, **#560** B2, **#561** B3, **#562** B4, **#563** B5 — UX lane B | **CLOSED by [#567](https://github.com/tvofi/heatpump_optimizer/pull/567), merged `f0042ad`.** UX lane B (B1–B5) is on `main`. leaves #558 open | shipped |
| **#564** UX lane C, item C1 — four contrast fixes in one PR | **CLOSED by [#569](https://github.com/tvofi/heatpump_optimizer/pull/569), merged `c609b91`.** C1 contrast defects. leaves #558 open | shipped |
| **#565** D2, **#566** D3 — UX lane D | **CLOSED by [#571](https://github.com/tvofi/heatpump_optimizer/pull/571), merged `7df2ce5`.** D2/D3. leaves #558 open | shipped |
| **#558** UX programme tracking — 34 items in five lanes | **CLOSED by [#891](https://github.com/tvofi/heatpump_optimizer/pull/891), merged `67a61fb`.** F1 added the device-registry configuration-URL field and a publisher manufacturer; F2 setdefaults the repair-notice documentation link. Device name unchanged. Packed so the coordinator class did not grow. leaves #201 open | shipped |
| **#550** the `apply_topology` set check pins the reverse direction against the module constant, not the schema | **CLOSED by [#554](https://github.com/tvofi/heatpump_optimizer/pull/554), merged `06ad947`.** The check probes the registered schema. | shipped |
| ~~**#544**~~ every branch conflicts in the two claim files | **DONE — closed by #545, merged `4f6a8b1`.** Prevented, not repaired — a `claimnotes` merge driver unions the note comments and **refuses** a claim list both sides rewrote, since union reinstates a deleted claim past the `#495` guard. Five branches, ten conflicts, in one session | [#545](https://github.com/tvofi/heatpump_optimizer/pull/545) |
| ~~**#546**~~ pressing **Tidy** made the setup page unsaveable | **DONE — closed by #548 (`137b6d5`), shipped in v6.3.17.** Released severity — `apply_topology` rejects `positions.outdoor`, which the card always emits. **Not drag-only**: the RCA ran the card's own `layoutArrange` and Tidy alone emits it on every configuration. **Shipped v3.16.0, 80 releases ago.** A stamp follows the merge | [#548](https://github.com/tvofi/heatpump_optimizer/pull/548) |
| **#547** four config-flow pages have a stored-value arm that is executed but unpinned | **CLOSED by [#553](https://github.com/tvofi/heatpump_optimizer/pull/553), merged `fde4f69`.** The golden seeds options so the stored-value arm is visible. | shipped |
| **#539** `tools/audit` *generates* the forbidden `mkdir` gate lock | **CLOSED by [#552](https://github.com/tvofi/heatpump_optimizer/pull/552), merged `c79b387`.** The generator no longer emits the forbidden `mkdir` gate lock. | shipped |
| **#590** upstream has drifted from the declared floor | **CLOSED by [#632](https://github.com/tvofi/heatpump_optimizer/pull/632), merged `5eec023`.** Floor kept; `_number` convention pinned. | shipped |
| **#577** nine measured divergences between `tests/hastub` and Home Assistant | **CLOSED completed.** Recorded in `tests/ha_contract.py` via [#578](https://github.com/tvofi/heatpump_optimizer/pull/578) `6ac7d83`. The issue was closed by hand after that mechanism landed. | shipped |
| **#584** nightly A3: the published-state sweep | **CLOSED by [#626](https://github.com/tvofi/heatpump_optimizer/pull/626), merged `6b6132e`.** Nightly A3. #533's abort precondition is **discharged by [#731](https://github.com/tvofi/heatpump_optimizer/pull/731)** — the cause was production code, not the harness. The rest of that precondition stands: the lane still discards a container's results on any abort, `log:no_integration_traceback` counts the A4 tranche's own injected fault, `log:blocking_positive_control` sees nothing inside its probe window, and `a3:roster` has no independent baseline. A later tranche may not expect a green lane. | shipped |
| **#585** nightly A10: the diagnostics privacy probe | **CLOSED by [#638](https://github.com/tvofi/heatpump_optimizer/pull/638), merged `76849a0`.** Nightly A10. #533's abort precondition is **discharged by [#731](https://github.com/tvofi/heatpump_optimizer/pull/731)** — the cause was production code, not the harness. The rest of that precondition stands: the lane still discards a container's results on any abort, `log:no_integration_traceback` counts the A4 tranche's own injected fault, `log:blocking_positive_control` sees nothing inside its probe window, and `a3:roster` has no independent baseline. A later tranche may not expect a green lane. | shipped |
| **#587** nightly A5/A8/A9: options round-trip, service registration, reload | **CLOSED by [#655](https://github.com/tvofi/heatpump_optimizer/pull/655), merged `e785757`.** Nightly A5/A8/A9. #533's abort precondition is **discharged by [#731](https://github.com/tvofi/heatpump_optimizer/pull/731)** — the cause was production code, not the harness. The rest of that precondition stands: the lane still discards a container's results on any abort, `log:no_integration_traceback` counts the A4 tranche's own injected fault, `log:blocking_positive_control` sees nothing inside its probe window, and `a3:roster` has no independent baseline. A later tranche may not expect a green lane. leaves #533 open | shipped |
| **#588** the loop detector cannot tell "no blocking call" from "no log" | **CLOSED by [#651](https://github.com/tvofi/heatpump_optimizer/pull/651), merged `02ff13f`.** Loop-detector positive control. #533's abort precondition is **discharged by [#731](https://github.com/tvofi/heatpump_optimizer/pull/731)** — the cause was production code, not the harness. The rest of that precondition stands: the lane still discards a container's results on any abort, `log:no_integration_traceback` counts the A4 tranche's own injected fault, `log:blocking_positive_control` sees nothing inside its probe window, and `a3:roster` has no independent baseline. A later tranche may not expect a green lane. | shipped |
| **#580** a check earns its place once and is never asked again | **CLOSED `not planned` by judge ruling, 2026-09-07, and merged into [#588](https://github.com/tvofi/heatpump_optimizer/issues/588).** The mechanism it asked for was already in the tree — 45 committed, executing null controls across six test files — and the example it argued from had been landed as a committed control by #571 on the day it was filed. **Two residuals survive the closure and are carried below**, because a ruling in a comment on a closed issue is not propagation | closed; residuals carried |
| **#581** `brief_lint` refuses a literal metric but not a literal anything-else | **ANSWERED IN BOTH DIRECTIONS by [#672](https://github.com/tvofi/heatpump_optimizer/pull/672).** Its own falsification test was executed rather than argued: the shape rule reports 20 figures on the live briefs at `244ea5f`, five of them the defect, and one `30-50 LOC` window accounts for five of the fifteen false ones — so shape matching is refused. **The rule that produced those figures is deliberately not in the tree, so read them as rule-dependent**: #672's reviewer rebuilt it from the description and got 12, 29 or 32 reports depending on the noun list, which brackets 20 rather than confirming it, and reproduced the sweep-window family at exactly five. The 5-in-20 split is one seat's classification against a stated rule and nobody has re-derived it. The derivation-backed `counts` check, which had never read a roster, now does | own PR |
| **#582** lanes B–F have no roster, so propagation has no destination | **CLOSED completed.** Destination `.claude/workflows/wave-ux-groups.json` landed as [#601](https://github.com/tvofi/heatpump_optimizer/pull/601) `ac84d86`. The leftover "under refutation" was the measurement of whether a linter extension was needed, not leftover work. | shipped |
| **#583** stopping a seat mid-mutation leaves a production file broken | **item 2 CLOSED by [#671](https://github.com/tvofi/heatpump_optimizer/pull/671), merged `19c85ac`; the issue stays open.** The Stop hook reports an uncommitted tracked file under `custom_components/`. Item 1, a `.mutation-active` marker the seat writes, is a **recorded decision not to build**: a guard whose accuracy depends on the cooperation of the process it guards against is not a guard | open for item 1 |
| **#692** the services catalogue says eleven where twelve are registered, and omits `set_away`'s fields | **CLOSED by [#710](https://github.com/tvofi/heatpump_optimizer/pull/710), merged `e50aa51`.** The README table is `services.yaml`'s keys and the count is a digit derived from that set; `docs/configuration.md` documents `set_away`'s `active` / `return_time`. | shipped |
| **#697** 15-minute DSO effekt clock | **shipped on `main` as [#707](https://github.com/tvofi/heatpump_optimizer/pull/707) (`c2e9200`).** Quarter-hour peak billing is the billed clock. Issue CLOSED completed. Outside the #201 programme | shipped |
| **#698** DSO tariff catalog | **shipped on `main` as [#707](https://github.com/tvofi/heatpump_optimizer/pull/707) (`c2e9200`).** Versioned in-tree Swedish DSO products. Issue CLOSED completed. Outside the #201 programme | shipped |
| **#699** sensor-gap euro advisor | **shipped on `main` as [#707](https://github.com/tvofi/heatpump_optimizer/pull/707) (`c2e9200`).** Ranks empty topology slots by estimated currency per month. Issue CLOSED completed. Outside the #201 programme | shipped |
| **#700** weekend and holiday comfort/DHW profiles | **shipped on `main` as [#707](https://github.com/tvofi/heatpump_optimizer/pull/707) (`c2e9200`).** Weekend comfort pair and optional holiday calendar profile. Issue CLOSED completed. Outside the #201 programme | shipped |
| **#701** Nord Pool / nordpool-entity prices | **shipped on `main` as [#707](https://github.com/tvofi/heatpump_optimizer/pull/707) (`c2e9200`).** Entity price source, no Tibber token. Issue CLOSED completed. Outside the #201 programme | shipped |
| **#702** wood-burn night advisor | **shipped on `main` as [#707](https://github.com/tvofi/heatpump_optimizer/pull/707) (`c2e9200`).** Diagnostic 48-hour wood advice. Issue CLOSED completed. Outside the #201 programme | shipped |
| **#703** Tibber Pulse auto-bind | **shipped on `main` as [#707](https://github.com/tvofi/heatpump_optimizer/pull/707) (`c2e9200`).** Suggests Pulse for an empty `house_power_entity`. Issue CLOSED completed. Outside the #201 programme | shipped |
| **#574** two residues of #572 | **CLOSED by [#602](https://github.com/tvofi/heatpump_optimizer/pull/602) `de0c01d` and [#603](https://github.com/tvofi/heatpump_optimizer/pull/603) `da3f7b0`.** Step 13 names the one meaningful claim-file conflict; the ratchet comment states the rule rather than a number. | shipped |
| **#575** merged PRs below #375 have no disposition anywhere | **DECLINED this session, with the size measured rather than estimated** (comment 5598754296): 195 merge subjects on `main` name a pull request below #375, and **184 of them are mentioned nowhere** in this file or the handover. Derived from `git log` over every merge subject, which enumerates completely; the earlier refusal to state a figure here was right about the instrument it had — `gh pr list --limit`, a sliding window whose answer decays by roughly one per merge — and wrong that no honest figure existed. Read 184 as a floor, not a defect count: the test is a bare grep and cannot tell a disposition from a passing mention, which moves the true number up. #531's scope boundary asserted that pre-#375 work "is recorded there, not here" in three cited documents; it is not, and `audit-2026-08.md` carries no pull-request reference at all. Whether these need dispositions is the owner's call | declined |
| **#570** GitHub cannot run the `claimnotes` merge driver | **CLOSED by [#572](https://github.com/tvofi/heatpump_optimizer/pull/572), merged `059881e`.** A merge driver's implementation is a `git config` entry and git never clones config, so GitHub — which computes `mergeStateStatus` — falls back to a plain text merge and calls every open PR `DIRTY` the moment `main` touches a claim file. GitHub then will not build a merge commit, so the `pull_request` workflows **never queue**: such a PR does not go red, it cannot run. Measured on #569 (CodeQL alone; `fast`, `closures`, `browser`, `briefs` absent). The fix is a subtraction — nothing requires a branch to write a note into a claim file, so a branch that claims nothing does not touch them | policy PR |
| **#541** verifiable proof that a PR followed the *process* | **NOT BUILT this session, mechanism 3 included** (comment 5598760607): the governance programme mechanised **class 1 only**. Class 2 has nothing — the mutation proof is still a paste nobody re-runs. Class 4 cannot become mechanical here at all while one identity authors and approves. The ranking below survives untouched, and its 94 sentences are now a floor: the corpus is nine rules and seven contracts, not five and four. Prior disposition, still the plan: **split three ways, not deferred wholesale** (comment 5562208736). **Mechanism 3** (GitHub as witness — 14 obligations, one API call, additive) **now**. **Mechanism 1** (replay the branch) at a **wave boundary**, since its value is concentrated in the fixer PRs of Wave 4 S7/S8/S12 and Wave 5 and a gate change is only cheap when nothing is in flight. **Mechanisms 2, 4, 5** as a new programme after #201, whose **first task is an independent re-derivation of the taxonomy** — 94 rows are one agent's judgement over a heuristic split, and if the class distribution moves the ranking moves with it. **Mechanism 1's precondition, carried here from [#732](https://github.com/tvofi/heatpump_optimizer/pull/732) before it merged, per `finding-propagation.md`** — this row is the destination because the stage has no brief yet, and creating one is part of the carry when it starts. Re-executing a figure's command and comparing its output to the value the body states is legitimate **only for a command over an in-tree corpus at a fixed head**, and **only where it is demonstrated per case that the command prints the same value twice at that head**. **Running it twice is the control**, and it is the whole test: a command that prints two different values at one head is time-varying and must never be compared to a literal. Never for a command over the GitHub API, where that control fails by construction. Two further preconditions the same measurement established. An allowlist must be argued on **what the allowed programs can do** — `python3 tests/structure.py --record` rewrites the ratchet's budget table — not on which programs they are; naming the instruments is the easy half and is not the decision. And `pr-contract` **was** an `actions/checkout` with no `fetch-depth`, so it had depth 1 and no `origin/main`: no merge-base figure could be re-executed there until that checkout changed — **which #818 did, setting `fetch-depth: 0` so the approval gate could derive the diff**, so this particular cost is no longer one mechanism 1 pays before it starts. **Re-measure, do not carry**: the shares of `gh`, `git` and in-tree-instrument commands are a sliding window over the open pull requests; the enumerator is `node .claude/workflows/figure_census.mjs`, it states its own counting rule, and it is run at your own merge base rather than read out of this row | own programme |
| **#677** the merge enumerator reads a free-text squash suffix | **CLOSED by [#720](https://github.com/tvofi/heatpump_optimizer/pull/720), merged `e49b2fb`.** The record job asks `/commits/{sha}/pulls` per first-parent commit; the trailing-`(#N)` regex is the offline fallback | shipped |
| **#678** `push.sh` — contract-check the body at `HEAD`, then push and set the body in one command | **filed as the countermeasure of a root-cause finding, process state (c)**: the instruction to run `prepr.sh` before pushing is read and obeyed and still loses, because the check that binds lives in a job that exists only after the push. The cost test is in the body, from today's merged heads' `pr-contract` check runs. One script, plus a one-sentence change to `fixer.md` step 5 and `orchestrator.md`, hence the owner's approval. **IN REVIEW as [#715](https://github.com/tvofi/heatpump_optimizer/pull/715)**, built after the defect recurred across 2026-09-09 and 2026-09-10. #678's own cost test measures the **closed** half and its literal stands, 9 red `pr-contract` runs at merged heads on 2026-09-09; the 09-10 half is an **open** window, so #715's body carries a runnable enumerator rather than a number, per `writing-for-agents.md` — and its first enumerator did not run, which the fix review caught and the body records; its `## Approval` section carries the two sentences verbatim for the owner | governance, in review |
| **#679** `pr-contract` re-executes `## Figures` against an allowlist | **open on branch `claude/figures-command-replay` as [#732](https://github.com/tvofi/heatpump_optimizer/pull/732), policy, awaiting the owner's approval under decision 0007; the filed form is REFUSED and a narrower one is built.** Re-execution is refused on **two load-bearing reasons plus one that binds a single arm**, each recorded in `.claude/workflows/figure_lint.mjs`'s header with the counting rule behind it rather than asserted here. An allowlist bounds the program, not what the program does — `python3 tests/structure.py --record` is on any list that admits the ratchet, and it rewrites the budget table; that one is decisive on its own. The API arm is not empty and every command in it reads a value that is time-varying by construction, so comparing one to a stated literal reddens an honest body, and one reddening is enough for a check to be routed around. And `pr-contract` **ran** `actions/checkout` with no `fetch-depth`, so at depth 1 with no `origin/main` every merge-base figure would print a wrong value or none — **withdrawn by #818, which set `fetch-depth: 0`**; the refusal stands on the reason `figure_lint.mjs`'s header marks decisive alone. **Two quantities a first draft argued this on do not measure out, and the correction is the point of the round that found them**: *most figures are over the GitHub API* is false, `gh` being about a fifth of recognised commands while in-tree instruments are the largest class; and *the corpus is not executable as written* is far weaker than it reads, the templated commands being a small minority overall and a smaller one among the in-tree instruments #679 actually targets — so that reason is withdrawn as a **cost** re-execution would have to pay, not a reason it is refused. Both are counted by `node .claude/workflows/figure_census.mjs`, the in-tree enumerator that imports the checker's own recogniser so the counting rule is the checker's; the corpus is out of the tree and its window is open, so no literal is carried into this row. What is built executes no character of the body: each figure's command is checked for RESOLVING — a `gh` long flag against the inventory `gh <subcommand> --help` prints, a `gh` or `git` subcommand against the installed client, a `node`/`python3`/`bash` script path against the tree at this head — and anything else is reported `unverified` per line rather than refused. The defect it answers is #715 round seven, `--arg` passed to `gh api`, which errored client-side and printed the same figure for every state of the world. The one confused-deputy route review found is **closed rather than disclosed**: `gh` expands its own shell aliases and `--help` does not short-circuit them, so a subcommand word from a body selected which program `gh` ran — local-only, since a pull-request author cannot write the runner's config — and every spawn now runs under a config directory the checker creates. What it does not catch is in the pull-request body, the first entry being a command that runs and prints a different number than the body states | governance, open |
| **#680** a seat identity distinct from the owner | **accepted by the owner 2026-09-10; the machinery is decision 0008 and `.github/CODEOWNERS`, the identity is the owner's step.** Order (0005's): machine account with write, the authorization switch, a seat verifies the login, then the code-owner rule on `main-protect` — never the rule first. Was: The live ruleset has no `pull_request` rule because one account cannot approve its own pull request, and there is no `CODEOWNERS`. A second identity — machine user or App — unlocks required approvals, code-owner review over the policy set so that decision 0007 becomes a check, and #541 class 4 | owner |
| **#681** measure merge throughput before deciding on a merge queue | **CLOSED `completed` at 2026-09-10T18:53:11Z by [#741](https://github.com/tvofi/heatpump_optimizer/pull/741)**, which landed the enumerator and refused the merge queue with its reasons. The disposition below is what the issue was filed as and is kept for the history; it is no longer forward-looking. **Filed as a measurement with a decision at the end, not as a request for a queue.** Today's merge cadence and the forced-full gate's duration are in the body with their commands; some merges landed inside the previous merge's gate window, counted there. Three assumptions a queue's rebase breaks — `## Head`, review at this SHA, the enumerator — each need an answer before one is turned on | governance, after a week of `main` |
| **#682** render both disposition documents in the record job | **CLOSED by [#721](https://github.com/tvofi/heatpump_optimizer/pull/721), merged `8db8abe`.** Rendered structure compared to source; markdown-it vendored. `governance.yml` untouched | shipped |
| **#683** mutate the record mode's three outputs | **CLOSED by [#695](https://github.com/tvofi/heatpump_optimizer/pull/695), merged `1684e62`.** A second enumeration is exported from production beside the first; the lane mutates the record-mode outputs and an emptied `CAP_RES`. | shipped |
| **#684** a worktree collector | **CLOSED by [#716](https://github.com/tvofi/heatpump_optimizer/pull/716), merged `a1f148a`.** `tools/audit/worktree_gc.sh`, dry-run by default. Deletes only when the four predicates in the issue hold; a branch worktree is never touched. `--self-test` drives each keep criterion and the issue's null control. | shipped |
| **#685** handover traps 16–18 render under different numbers than their source | **filed only because the owner asked for the whole list as issues.** A line-neutral reorder of three items in `docs/HANDOVER.md` — it sits at its cap, and a reorder adds no line — fixes every citation; a `counts`-class rule that an ordered list's source numbers run `1..n` keeps it fixed. Policy file, so decision 0007's per-PR approval | any seat |
| **#774** reload plan handover has no expiry | **CLOSED by [#886](https://github.com/tvofi/heatpump_optimizer/pull/886), merged `7d142c0`.** #880 expired the stash; #886 recomputes age on republish of a still-fresh handover, in place. | shipped |
| **#781** frequency map folded during reverse-cycle cooling | **CLOSED by [#887](https://github.com/tvofi/heatpump_optimizer/pull/887), merged `14a3833`.** The map is not folded while reverse-cycle cooling is the freeze reason, or while the power pin is stale. | shipped |
| **#783** in-process solve fallback holds the GIL | **CLOSED by [#888](https://github.com/tvofi/heatpump_optimizer/pull/888), merged `546b492`.** After the consecutive in-process fallback cap on the same hass, the GIL solve is skipped. Mutually exclusive with #784. | shipped |
| **#784** solve worker released only at Home Assistant shutdown | **CLOSED `not planned`.** Xor of #783: reaping the worker would put every install into #783's GIL-starvation state. Worker stays resident until Home Assistant stop. | closed not-doing |
| **#796** one default-on sensor renders Unknown | **done — closed completed.** Wood-burn advisor is Unavailable or none, not Unknown. [#878](https://github.com/tvofi/heatpump_optimizer/pull/878) `06c53f7`. | [#878](https://github.com/tvofi/heatpump_optimizer/pull/878) |
| **#797** entity display names mix leading and trailing nouns | **done — closed completed.** Title Case on the six English entity display names. [#872](https://github.com/tvofi/heatpump_optimizer/pull/872) `a95556d`. | [#872](https://github.com/tvofi/heatpump_optimizer/pull/872) |
| **#798** ruleset cannot require a review from any actor | **blocked — body cannot be satisfied.** `GET /repos/tvofi/heatpump_optimizer/collaborators` is still one login. ADR 0005/0008 and #680 put the machine-account step before any `pull_request` rule. Session instruction: do not add extra protection rules. Re-GET of ruleset 22628467: no `pull_request` rule; RepositoryRole 5 `always` bypass unchanged (stamp). The #799 PUT did not take this arm. | owner |
| **#799** record is a required context that cannot run on a pull request | **CLOSED — `record` dropped from main-protect 22628467 required contexts.** Owner comment on the issue refused the pre-merge arm; session preferred the ruleset drop. Re-GET no longer lists that context. [#884](https://github.com/tvofi/heatpump_optimizer/pull/884) is the row. Issue closes with this merge. | [#884](https://github.com/tvofi/heatpump_optimizer/pull/884) |
| **#802** dispatch prompts read GitHub free text while holding merge | **done — write-grant half on main as #869.** First half (free text is data) was #863. Closed. | [#869](https://github.com/tvofi/heatpump_optimizer/pull/869) |
| **#805** single-line production mutants survive the fast and golden gates | **CLOSED by [#890](https://github.com/tvofi/heatpump_optimizer/pull/890), merged `1b35c6c`.** Earlier pins: #877 (four non-coordinator) and #883 (two optimizer). M03: the tenth house-heat-loss sample persists; a ninth-sample null does not. Pin lives in `tests/features.py` — `tests/guard_pins.py` would import the coordinator and grow `tests/closures.json`. | shipped |
| **#817** the audit instrument's own defects | **deferred — last of all**, after every product issue merges. | after product |
| **#826** L-BFGS-B stops at its own ftol and is never restarted | **done — closed completed.** Restart L-BFGS-B once from its own returned point. Seeding arm not built. [#875](https://github.com/tvofi/heatpump_optimizer/pull/875) `5cddbc9`. | [#875](https://github.com/tvofi/heatpump_optimizer/pull/875) |
| **#829** strict-typing is unmet under the repository's own ruler | **done — closed completed.** Quality-scale `strict-typing` is `done`. `py.typed` was not added. Typing budgets were not raised. [#876](https://github.com/tvofi/heatpump_optimizer/pull/876) `e59ac74`. | [#876](https://github.com/tvofi/heatpump_optimizer/pull/876) |
| **#830** coordinator is built without config_entry | **CLOSED by [#871](https://github.com/tvofi/heatpump_optimizer/pull/871), merged `020e699`.** `config_entry=entry` on the coordinator `super().__init__`. No user-visible effect at any shipped version. | shipped |
| **#860** six leftovers handed to the cursor lane | **in flight — items 1–4 and 6 done.** Item 5 is #856, theirs. | [#868](https://github.com/tvofi/heatpump_optimizer/pull/868) |
| **#865** the pull-request body is one live object | **done — closed completed, no code PR.** Root-cause record was complete; steward S10 already states both orders leave one failed run. #860 item 4. | closed |

**Seven feature requests, #697-#703, are in the table above and none of them is this programme's work.** They were the
repository owner's own backlog, filed 2026-09-09 while the governance lane was running. They appear here because
`delivery-status-tracking.md` says every issue carries a disposition and that **"not mentioned" is not a
disposition**. Recording them as outside the programme is that disposition. They shipped on `main` as
[#707](https://github.com/tvofi/heatpump_optimizer/pull/707) (`c2e9200`); the issues are CLOSED completed.
They were never inside #201.


Policy and contract PRs this session opened, which close no issue and belong to
no wave:

- [#530](https://github.com/tvofi/heatpump_optimizer/pull/530) — **merged `f4ed26c`.** Tracking covers every PR and every open issue; and `finding-propagation.mdc`: a finding that changes how a later stage must work goes into that stage's own brief before the producing PR merges. Enforced at `fix-review.md`, verdict `blocked: finding not carried to <stage>`.
- [#526](https://github.com/tvofi/heatpump_optimizer/pull/526) — root-cause doctrine. Blocked once for having **no enforcement point**; now trigger *red on a check a cheaper detector could have run*, checked at `fix-review.md` step 11, verdict `blocked: root-cause trigger unanswered for <check>`.
- [#532](https://github.com/tvofi/heatpump_optimizer/pull/532) — the handoff to review freezes the branch. Blocked once for naming the **coordinator** where the tree means the **orchestrator** (`coordinator` is the production god-class Wave 4 is decomposing); verdict `blocked: head moved under review, measured <sha>`.
- [#534](https://github.com/tvofi/heatpump_optimizer/pull/534) — three permanent documents that contradicted the code: `fixer.md` step 5 mandated the `mkdir` gate lock two other permanent files forbid, and prescribed an unconditional local gate. Blocked once on a null control that reproduced at **neither** head, with the false form committed to a claim file. Cleared; `merge`.
- [#543](https://github.com/tvofi/heatpump_optimizer/pull/543) — **W4-G11 / S10, `Closes #304`.** `config_flow.py` 96.13 % → 99.26 %, all 21 named statements individually pinned. Blocked twice: a forward-carry that told S11 four pages were inert, and a body whose "Does not close #195" **parsed as a closing keyword**.
- [#545](https://github.com/tvofi/heatpump_optimizer/pull/545) — the `claimnotes` merge driver (#544). `merge`. The seat was asked for a third autofix job and **refused it with arithmetic**, which is the right outcome.
- [#548](https://github.com/tvofi/heatpump_optimizer/pull/548) — **`Closes #546`**, the released Tidy defect. **merged `137b6d5`, shipped in v6.3.17** — the stamp it said would follow has followed.
- [#549](https://github.com/tvofi/heatpump_optimizer/pull/549) — the policy text split verbatim out of #545, **merged `3f78703`**. Split so a working fix does not wait behind a 46-line docs diff.
- [#538](https://github.com/tvofi/heatpump_optimizer/pull/538) — **merged `17dc30a`.** `finding-propagation.mdc` routed cross-cutting findings to a destination `git grep` cannot find, *and made reaching it a merge blocker*. It also **deleted the clause deferring the in-tree carry to the record PR**, which retroactively bound #540 — a verdict correct when written stopped being correct without the code changing.
- [#552](https://github.com/tvofi/heatpump_optimizer/pull/552) — **merged, closed #539.** `tools/audit/prepare_baseline.sh` was *generating* the forbidden `mkdir` gate lock into every new auditor's text; the generator is fixed first, because correcting the prose alone leaves it re-emitting. Wider than filed: the same instruction also sat in agent prompt strings under `.claude/workflows/`.
- [#554](https://github.com/tvofi/heatpump_optimizer/pull/554) — `Closes #550`. Probes the registered schema instead of the module constant. Reviewed `merge`: fails on the junk-key reproduction that passed all 2002 shipped checks, and passes on **both** plausible fixes where the shipped check fails 4 of 7, because both directions became bounds rather than an equality.
- [#556](https://github.com/tvofi/heatpump_optimizer/pull/556) — the README section on AI use, its failure mode and what the gate costs a human contributor. Reviewed `merge`; contains no digits, by regex.
- [#557](https://github.com/tvofi/heatpump_optimizer/pull/557) — **W4-G10 / S9**, the first split of #224. Does not close it; five implementable pieces plus a design brief remain.
- [#375](https://github.com/tvofi/heatpump_optimizer/pull/375) — **merged `8e99ad1`**, this document and the workflows that run it. The programme's own first commit, and the boundary the completeness check above uses.
- [#379](https://github.com/tvofi/heatpump_optimizer/pull/379) / [#382](https://github.com/tvofi/heatpump_optimizer/pull/382) — **merged `db13fba` / `f7b5881`**, triage B1 and B2. B1 found the decomposition order **inverted** and its first stage overscoped, which is why Wave 4 runs S0→S13 in the order it does. B2 established the card residual is vertical and the coverage gap 21 statements.
- [#381](https://github.com/tvofi/heatpump_optimizer/pull/381) — **merged `a2c4982`**, a blocked tag push is *reported*, not raised over an already-public commit. One of `stamp.py`'s refusals.
- [#389](https://github.com/tvofi/heatpump_optimizer/pull/389) / [#390](https://github.com/tvofi/heatpump_optimizer/pull/390) — **merged `c06932a` / `81216e6`**. Everything a cold session needs is on `origin`, and the recorded resume state can be *executed* rather than only read. Together with #391–#393 these are why `resume` fields are machine-usable.
- [#467](https://github.com/tvofi/heatpump_optimizer/pull/467) — **merged `2ba8367`**, production: the heat-pump switch turns off on DHW-only idle.
- [#490](https://github.com/tvofi/heatpump_optimizer/pull/490) — **merged `62799e4`**, display-only DHW band: live probe σ(0) and an in-window lo floor.
- [#493](https://github.com/tvofi/heatpump_optimizer/pull/493) / [#494](https://github.com/tvofi/heatpump_optimizer/pull/494) — **merged `ae97a65` / `a26bb76`**, the Wave 4 and Wave 5 rosters prepared with no seat started, and the inherited DHW card claims emptied behind them.
- [#464](https://github.com/tvofi/heatpump_optimizer/pull/464) — **merged `7a233f7`**, seat 3L-G8/G9 wood furnace economics (#463). Seat work, not a record.
- [#466](https://github.com/tvofi/heatpump_optimizer/pull/466) — **merged `186be0c`**, seat 3L-G10 plan-page away toggle (#465). Seat work, not a record.
- [#498](https://github.com/tvofi/heatpump_optimizer/pull/498) — **merged `5234024`**, `closures-autofix`: the CI job that re-records `UNDER-SCOPED` closures from the failed job's own recordings. `CLAUDE.md` makes it load-bearing — *do not open a second PR, do not Darwin `--single`, wait for the bot commit.* Its successor #528 had a row; the job that introduced it did not.
- **The doctrine PRs that predate the wave rows** — [#391](https://github.com/tvofi/heatpump_optimizer/pull/391) (a cold session is oriented by the repository, not by a programme — the ancestor of this `CLAUDE.md`), [#392](https://github.com/tvofi/heatpump_optimizer/pull/392) (the handover says where the session *stopped*), [#393](https://github.com/tvofi/heatpump_optimizer/pull/393) (the wave-resume machinery). All merged. They are why a resuming session needs no briefing.
- **The record PRs — all of them, by rule.** A record PR carries one group's Delivery-status and roster update and closes nothing; its content is the rows above rather than a row of its own. Naming three of them and calling the enumeration complete is how #491 and #498 went 20 merges without a mention. The complete set, so the rule can be checked rather than trusted: waves 1–2 — [#422](https://github.com/tvofi/heatpump_optimizer/pull/422), [#423](https://github.com/tvofi/heatpump_optimizer/pull/423), [#425](https://github.com/tvofi/heatpump_optimizer/pull/425), [#429](https://github.com/tvofi/heatpump_optimizer/pull/429), [#430](https://github.com/tvofi/heatpump_optimizer/pull/430); wave 3L — [#471](https://github.com/tvofi/heatpump_optimizer/pull/471), [#473](https://github.com/tvofi/heatpump_optimizer/pull/473), [#476](https://github.com/tvofi/heatpump_optimizer/pull/476), [#478](https://github.com/tvofi/heatpump_optimizer/pull/478), [#482](https://github.com/tvofi/heatpump_optimizer/pull/482), [#484](https://github.com/tvofi/heatpump_optimizer/pull/484), [#486](https://github.com/tvofi/heatpump_optimizer/pull/486), [#488](https://github.com/tvofi/heatpump_optimizer/pull/488), [#491](https://github.com/tvofi/heatpump_optimizer/pull/491); wave 3L close-out — [#496](https://github.com/tvofi/heatpump_optimizer/pull/496), [#499](https://github.com/tvofi/heatpump_optimizer/pull/499); wave 1a — [#380](https://github.com/tvofi/heatpump_optimizer/pull/380); wave 4 — [#501](https://github.com/tvofi/heatpump_optimizer/pull/501), [#503](https://github.com/tvofi/heatpump_optimizer/pull/503), [#507](https://github.com/tvofi/heatpump_optimizer/pull/507).
- [#567](https://github.com/tvofi/heatpump_optimizer/pull/567) — **UX lane B, items B1–B5** (#559–#563). Establishes by execution that **mermaid does not render in HACS's in-app README view**: the chain is `hacs/integration` → `<ha-markdown>` with no `allow-svg` → `home-assistant/frontend`'s plain `marked` + `js-xss` worker, and this README run through HACS's own pinned versions yields zero `<svg>`. The entity count re-derives to **69, not the docketed 66** — the old pin compared the README against the literals it supplied, so it never saw `wood_cheaper` make a fifth binary sensor. **merged `f0042ad`**.
- [#568](https://github.com/tvofi/heatpump_optimizer/pull/568) — **teaches the config-flow golden's fingerprint to recurse into `section()`**, the hard precondition for #223's registry. Corrects #516's body: `section` is in `homeassistant/data_entry_flow.py`, not `helpers/selector.py`, and has existed since 2024.7.0. The sharp finding: grouping moves the fixture **once**, then goes silent — field removal, addition and selector-bound rewrites all left it byte-identical afterwards. **33 one-level schema walks remain in the assertion layer** (`entities.py` 28, `config_flow_steps.py` 4, `features.py` 1) and fail the same way. **merged `3c5b534`**.
- [#569](https://github.com/tvofi/heatpump_optimizer/pull/569) — **UX lane C, item C1** (#564): the chart's four contrast defects, measured in both stock Home Assistant themes with WCAG relative luminance and, for the two colours that share lightness, CIE Lab ΔE76 through a deuteranope model — because a contrast ratio cannot see that defect at all. **merged `c609b91`**.
- [#571](https://github.com/tvofi/heatpump_optimizer/pull/571) — **UX lane D, items D2/D3** (#565, #566): the English narrative priced in the instance currency rather than hardcoded Swedish, and `SensorDeviceClass.ENUM` with state translations for the string-state sensors. **merged `7df2ce5`**.
- [#572](https://github.com/tvofi/heatpump_optimizer/pull/572) — **merged `059881e`, closed #570.** Owner-approved and reviewed. GitHub cannot run the `claimnotes` driver, so a claim-file `DIRTY` blocks CI from queuing at all; a branch that claims nothing does not touch those files; the ratchet metric count is derived rather than stated (**24**, not the 22 the file had said); and `fix-review.md` gains step 13. Its own branch touched neither claim file, which is the rule it proposes. Residues in #574.
- [#573](https://github.com/tvofi/heatpump_optimizer/pull/573) — **#195 coverage tranche 1**, `climate.py` / `open_meteo.py` / `frontend.py` to 100 % statement coverage. Leaves #195 open; the brief's figures were 204 commits stale and were re-derived rather than carried. **Merged `9c1de0c`.**
- [#540](https://github.com/tvofi/heatpump_optimizer/pull/540) — **merged `9da726a`, closed #524 and #525.** Home Assistant's loop detector fired twice on every install, at setup and at worker shutdown, both warnings telling the user to file against this repository; invisible to every lane in `tests/` because the stub has no loop protection. Reviewed at the fourth attempt — the first three blocked on process grounds and never reached the code, because the branch was `DIRTY` and its gate lanes had therefore never run (#570).
- [#576](https://github.com/tvofi/heatpump_optimizer/pull/576) — **UX lane B, items B6–B11**: eight figures, none drawn by hand — B6/B7 from the shipped card, B9 reusing `setup_qa_render.mjs`, B8/B11 calling production. Establishes that **`docs/*.md` is not HACS-rendered at all**, so the image constraints are README-only. **Collides with #567**, and the shape is worse than "git will stop". It does stop — `merge-tree` exits 1 on `tests/entities.py` — **but the conflict hunk does not contain the colliding code.** #567's `_readme_table_rows` loop and `README.md` both auto-merge; the conflict is between two unrelated adjacent additions, so a resolver is never shown what breaks. Resolved the natural way (keep both sides), the check then fails: *table has 63 row(s), there are 56* — 63 = 56 + 8 tables − 1 header. **The merge instruction is explicit: remove `("sensors", "sensor", "Sensors")` from #567's row-count loop and keep this PR's name-set check.** Reviewed `merge`; **merged `5d73c38`**.
- [#578](https://github.com/tvofi/heatpump_optimizer/pull/578) — **#536, the hastub fidelity mechanism.** The highest blast radius in flight: every lane runs with `PYTHONPATH=tests/hastub`. **merged `6ac7d83`**.
- [#579](https://github.com/tvofi/heatpump_optimizer/pull/579) — **`Closes #542`**, the options-page data-loss bug. The defect class was derived by AST rather than taken from the issue body: nine option pages clean an entity key, eight clean only keys they present, and `learning` was **the only one** cleaning a key its schema never shows. All six named statements fixed. **merged `52c83d1`**.
- [#586](https://github.com/tvofi/heatpump_optimizer/pull/586) — **W4-G10 / S9 continued**: `optimize`'s comfort envelope and power ceiling leave. **merged `2406413`**.
- [#589](https://github.com/tvofi/heatpump_optimizer/pull/589) — **merged `df03771`**, W5-G6 / #195 tranche 2: `diagnosis.py`, `curve_learning.py`, `grid_fee.py` and `switch.py` driven directly, test-only. The disposition this row owed since the last sweep. It completes W5-G6, whose roster `resume` said `pending` for two days after it merged — the staleness this record exists to clear. leaves #195 open. leaves #505 open.
- [#591](https://github.com/tvofi/heatpump_optimizer/pull/591) — **#533's silent nightly pin.** At merge base a return of *either* #525 offender **passed** the lane — so a regression of the two bugs #540 fixed would have gone green in the only place that runs real Home Assistant. `Checks.check` blanked the detail on a pass, which is why nobody saw it: a stale pin *is* a pass. Also moves `tests/nightly_ha.py` off the INERT list, so the lane is gate-visible for the first time. **merged `f1c657a`** — the row said "In review" for two days after it landed, which is the staleness this record clears.
- [#592](https://github.com/tvofi/heatpump_optimizer/pull/592) — **policy, owner-approved**: `fixer.md` step 3's null control extends from "cost, gain or time" to **every quantified claim**. Written because twelve unmeasured claims were made in one day and **none was a cost, gain or time claim**, so the existing clause had no purchase on any of them. **merged `7c2c9d2`** — the row said "In review" for two days after it landed, which is the staleness this record clears.
- [#593](https://github.com/tvofi/heatpump_optimizer/pull/593) — **policy, merged**: `tools/audit/briefs/orchestrator.md` and `tools/audit/preflight.sh`, the latter pinned from `tests/entities.py` so the pre-flight cannot rot unnoticed. Leaves every issue open. **merged `f4b0113`**.
- [#594](https://github.com/tvofi/heatpump_optimizer/pull/594) — **merged `1cea960`.** Indexes every policy document in `CLAUDE.md` by who it binds. Merged into this branch before this record's own fix commit, which is how it reached the miss set: a record PR can absorb a merge and not record it, the failure mode #575 names.
- [#595](https://github.com/tvofi/heatpump_optimizer/pull/595) — **policy, merged**: the full-derive prohibition, fix→verify→file, and the symbol-citation remedy — three of the five rules the mining seat recommended promoting out of the out-of-tree seat block; the other two are in #592. Leaves every issue open. **merged `b7dbabc`** — the row said "In review" for two days after it landed, which is the staleness this record clears.
- [#596](https://github.com/tvofi/heatpump_optimizer/pull/596) — **Wave 5 / W5-G1, #303 tranche 1**: the pinned stub-free typing ruler and its ratchet, landing the instrument before any annotation. Annotates nothing; leaves #303 open. **merged `e803d83`** — the row said "In review" for two days after it landed, which is the staleness this record clears.
- [#597](https://github.com/tvofi/heatpump_optimizer/pull/597) — **W4-G12 / Plan S11, #223**: two tables replace the options flow's three hand-listed field rosters, and every page becomes a query over them. The group whose brief this record unions on merge. **Merged `0323c5b`.**
- [#598](https://github.com/tvofi/heatpump_optimizer/pull/598) — **policy, owner-approved**: `CLAUDE.md` gains a rule against filler prose, scoped to the development record rather than the product. Leaves every issue open. **merged `86647c4`**.
- [#599](https://github.com/tvofi/heatpump_optimizer/pull/599) — **UX lane D, items D4-D6**: icons follow state, services are translated, and the schedule sentence carries a number. Part of #558, which stays open at 34 items across five lanes. **merged `6ea0083`**.
- [#600](https://github.com/tvofi/heatpump_optimizer/pull/600) — **UX lane C, items C2-C3**: chip toggles, colliding axis labels, the band drawn as an envelope, savings typography. Two of lane C's nine; #558 stays open. **merged `6b389db`**.
- [#531](https://github.com/tvofi/heatpump_optimizer/pull/531) — this record. Blocked once: it claimed nine roster briefs had received a carried finding when only two had. The script used `str.replace`, which does not raise on no match, and printed success either way — the same shape as #523. The fix asserts the string changed and re-reads the file from disk.
- [#601](https://github.com/tvofi/heatpump_optimizer/pull/601) — **merged `ac84d86`**, the UX lanes' in-tree roster `.claude/workflows/wave-ux-groups.json`: 28 pull-request units over the docket's 34 items, each carrying a brief, `after` edges and a `resume.stage`. Discovered by `brief_lint.mjs`'s existing `wave-*-groups.json` glob with **zero** code changes, which is why the file carries the `wave-` prefix although the lanes are not a wave — so #582's "the linter extension is the larger half" is refuted, as its own judge measured. The linter half that is real is four shape rules: before them a group missing `resume` was accepted in silence, a missing `brief` or `groups` threw, and a malformed roster sorting first took every other roster's findings with it — **0 of 6 rosters linted before, 6 of 6 after**. Leaves #558 and #582 open.
- [#602](https://github.com/tvofi/heatpump_optimizer/pull/602) — **merged `de0c01d`**, part 2 of #574: the "22 metrics" comments in `tests/features.py` and `tests/structure.py` rewritten to state the rule rather than a number, and two historical clauses **dated once** rather than rewritten, because they also carry two other #374-era figures. The count is 24, derived as `tests/structure_budgets.json` keys less `recorded_at`. Its finding is that the occurrence count depends entirely on the sweep rule — **4 live occurrences under one pattern, 9 under a wider one**, both correct under their own rule — so a count is given with its rule or not at all. Left #574 open for #603.
- [#603](https://github.com/tvofi/heatpump_optimizer/pull/603) — **merged `da3f7b0`**, part 1 of #574, **owner-approved before the branch was pushed**. `fix-review.md` step 13 told a reviewer that a conflict confined to the two claim files is merge-prep, with no exception; `env_drift.py`'s `merge_claim_file` has one, returning `None` when **both** sides rewrote the bare claim list, because a union reinstates a claim the branch deliberately deleted where `inherited_claims_error` — which fires only on a list *exactly* equal to the baseline's — cannot see it. Written from the mechanism in source, **not from an observed failure**, and the body says so. Closes #574 together with #602.
- [#604](https://github.com/tvofi/heatpump_optimizer/pull/604) — **merged `3b5a318`**, the durable half of the 2026-09-07 session into `docs/HANDOVER.md`: three decisions (fix→verify→file; the orchestrator is bound by every contract it enforces; every sentence earns its place), two corrections (the ratchet's 24 metrics; the claim-file rule is conditional and the flat form was briefed to every seat for a whole session), and five traps. The sharpest is trap 12 — a fix is verified against the **instance demonstrated**, not the **property stated** — at **3.1 % of reviewed pull requests and 11.2 % of all review rounds**, with the countermeasure written against that very class, `tools/audit/preflight.sh`, catching **0 of 3** because all three spell the quantity as a word.
- [#605](https://github.com/tvofi/heatpump_optimizer/pull/605) — **merged `5a7c9e6`**, `orchestrator.md` §4 gains the instrument it was missing: the merge message is a second closing surface, and the hand-written grep used for a whole session of merges catches **2 of the 4 forms GitHub acts on** where `tools/audit/preflight.sh` catches 4. The more useful half is the invocation — the pre-flight reads the body on **stdin** and takes the issues you intend to close as arguments, so passing a filename leaves stdin empty, the script blocks, and a killed process reports success. That is how it was first "verified" clean over three bodies, one of them binding a closing keyword to an open number.
- [#606](https://github.com/tvofi/heatpump_optimizer/pull/606) — **merged `5a62b96`**, the repair for a red `main`, merged with **no review** because main was red and this was the repair. #601 landed a brief citing `configuration_url` and #531 deleted the tracked tree's only occurrence of that string; different files, no conflict, and only main's forced-`full` run could see the relation. Repaired by **re-anchoring the brief**, not by restoring the deleted sentence — restoring it would have greened the gate while leaving the citation pinned to a line of English, and **prose is not a pin**.
- [#607](https://github.com/tvofi/heatpump_optimizer/pull/607) — **merged `5018e31`**, the 2026-09-07 record: the Delivery-status table truthed in both waves (Wave 4 to S0–S11 with #224 open; Wave 5 to W5-G1 landed, and W5-G1's census correcting the plan in both directions), W4-G10's spent "do not open W4-G11 until #224 is closed" instruction removed, traps 17 and 18 added, and the eight pull requests merged without an independent verdict at their final head named. **It dispositioned neither its own merge nor #608 and #610** — the gap this record closes — and its 43-line addition to `docs/HANDOVER.md` carried that file past the cap #608 had recorded 56 minutes earlier, leaving `main` red on `Governance / policy-docs` at `5018e31`. That red is repaired here by cutting the lines back, never by raising the cap.
- [#608](https://github.com/tvofi/heatpump_optimizer/pull/608) — **merged `2b5e416`**, `.claude/workflows/policy_lint.mjs` and `.github/workflows/governance.yml` (job `policy-docs`, never scoped, on the `briefs` precedent). **Six check classes** over the policy corpus — citations, counts, `no-gh`, budgets, index, duplicates — reusing `brief_lint.mjs`'s resolvers by import rather than copying them, so there is one implementation of "does this resolve"; that needed `export` on 25 resolvers and a main guard, both proven behaviour-free by `brief_lint.mjs`'s output staying byte-identical. A **defect ledger**, `.claude/workflows/policy_known_bad.json`, records the 26 defects present in **41 occurrences**: more than recorded is an error, fewer is an error until re-recorded, an entry that no longer fires is an error, and **the list may only shrink**. The size caps are **one-sided** deliberately — a two-sided ratchet on prose would charge a seat for deleting a paragraph, and deletion is what this corpus needs. Three adversarial review rounds from a detached worktree at the head SHA by a seat that did not write the change; **rounds 1 and 2 returned `blocked`**, on nine defects between them, and round 3 returned `merge`. Merged under the grant #610 records.
- [#610](https://github.com/tvofi/heatpump_optimizer/pull/610) — **merged `d5d8c4a`**, `docs/decisions/0001-session-policy-merge-grant.md`: the session policy-merge grant written into the tree instead of cited from a chat transcript that does not survive the session. It records what the grant permits, what it **excludes** — release stamps, structural budget raises, pull requests authored outside the audit, and anything after this session — and that it replaces one precondition rather than the set: every merge under it still needs an adversarial `merge` verdict from a seat that is not the seat that wrote the change. The measurement behind it is that **no ruleset applies to `main`**, repository or inherited, both endpoints answering `200 []`; the decision also separates the two 403s it had first reported alike, one from GitHub's token scope and two from the agent proxy, because reading the second kind as the first sends a reader to change something that was never the obstacle. `docs/decisions/` is not a second handover — `closure.is_handover` is False for it, and the handover set over `docs/` is still exactly one file.
- [#611](https://github.com/tvofi/heatpump_optimizer/pull/611) — **merged `6438406`**, the stage vocabulary and the verdict grammar. `web-fix-wave.js` recognised four `resume.stage` values against the six the rosters use, so a group at `pending` or `blocked` fell through every branch and was silently skipped; the verdict line was parsed by a prefix test that accepted anything beginning `Fix review: merge`, including a blocked verdict whose reason began with that word. Both are now one `STAGES` definition and one grammar with a closed class vocabulary, dispatching the root-cause seat on `root-cause-unanswered`. Two adversarial rounds; round 1 returned `blocked` on two regressions the change itself introduced — a null reviewer dereferenced, which `parallel()` swallowed so the group lost its pull-request number rather than throwing, and a truncation guard added, described in the commit message as the repair, and **never called**. The harness went **8 to 26 assertions** and the control moves **15 passed, 11 failed** to all passing.
- [#612](https://github.com/tvofi/heatpump_optimizer/pull/612) — **merged `d5419fe`**, the repair for a `main` that had been red on `Governance / policy-docs` since `5018e31`. #608 recorded `docs/HANDOVER.md`'s cap at the length that file then had; #607, cut from the same base and already in review, added 43 lines to it and merged 56 minutes later. Both prefixes are INERT, so that workflow was the only thing measuring it and **each branch was green alone** — the relational shape of trap 17, on a budget rather than a citation. Repaired by cutting the file 319 → 276 against a cap of 278, never by raising the cap, with every cut line's content verified present at a named destination first. Also dispositioned the ten merges no record covered. Its own row is this one.
- [#613](https://github.com/tvofi/heatpump_optimizer/pull/613) — **merged `bcba123`**, `GATE_FILES` narrowed from the directory prefix `.github/workflows/` to `tests.yml` alone, with the other four workflows classified `INERT`. Only `tests.yml` can do what a gate file means — it sets the job matrix, the interpreter versions, the dependencies and `GATE_SCOPE`; measured, **no recorded closure reads any of the other four**, none sets a gate variable, none runs a gate script. The prefix was already wrong for three of them and #608 widened its reach by adding `governance.yml` beside them. Cost, from this repository's own runs: `fast (3.13)` **1426s** on a workflow-touching pull request against **48s** on one that scopes normally, about 30×, and `tests/stress.py` is inside that job. Four pins in `tests/entities.py`, 1105 → 1112, including an anti-regression check that no directory prefix in `GATE_FILES` can match `tests.yml`. **The review found a second effect the body understated:** under the prefix a *new* workflow was `gate=True` and therefore never orphaned, so it entered unclassified and forced FULL forever — which is exactly how `governance.yml` got in. `CLAUDE.md`'s standing sentence that a new tracked file must be deliberately classified or `tests/entities.py` fails **was not true for workflow files** before this and is true after.
- [#614](https://github.com/tvofi/heatpump_optimizer/pull/614) — **merged `118fcf2`**, the pre-PR self-check `tools/audit/prepr.sh`, the body contract `policy_lint --pr-body` with its required H2 set parsed **from** `.github/PULL_REQUEST_TEMPLATE.md` so the two cannot drift, the `pr-contract` job on `pull_request: [opened, edited, synchronize, reopened]`, the `coverage` check, and `.claude/skills/steward/SKILL.md`. **Seven `blocked` verdicts before `merge`, and five of the seven were defects in CHECKS rather than in production code** — a check that cannot refuse is worse than none, because it reads as enforcement. Round 1: the contract refused this pull request's own body, because no fixture had ever exercised its accept path, so backticked identifiers and wrapped evidence — the two things every policy file here does — were both false refusals. Round 2: `coverage` was **vacuous** (deleting its call site left `--self-test` 11/11 and `FIXTURE ok` green, because its probe tested the glob regexes and never invoked the function); `NEVER_SUPPRESSED` was claimed in the body and absent from the tree; a bare `n/a` satisfied the whole contract. Round 3: `CORPUS_CHECKS.length === 4` pins **arity, not membership** — a no-op arrow, a duplicate, or *removing the wrapper* all keep the count and disable the check, and the last is a one-token cleanup the comment itself invited. Round 4: the body claimed no existing cap moved while `CLAUDE.md`'s went 465 → 468 at the time, which decision 0001 disclaims unqualified — **paid by cutting three lines rather than raising it**; and the wrapper's name was pinned, its body was not. Round 5: the round-4 fix added **a line of production code nothing tested** — `coverageFileSource`'s default `() => []` disabled coverage entirely with every pin green, since `??` discards null and undefined but not an empty array. Round 6: the pin asserted **a spelling, not a property**, refusing `() => {}` — the canonical no-op idiom — while detection stayed correct. **Two attacks survive and are disclosed rather than papered over**: no assertion inside a program can pin its own last call site. The review also established what the author had not — that under the old gate prefix a *new* workflow was never orphaned, so `CLAUDE.md`'s standing sentence about deliberate classification **was not true for workflow files**; and it supplied the stopping rule that ends the regress, that a mutation of production code must be caught while a mutation of the acceptance is the floor. One measurement class bit three times here — #523's silent `str.replace`, a reviewer's `\n` crash, and an author's `$?` read through a pipe — each time **a harness that crashed was indistinguishable from one that passed**; the countermeasure is procedural, to report *how* a thing failed rather than whether a count moved.

- [#615](https://github.com/tvofi/heatpump_optimizer/pull/615) — **merged `e4a388a`**, `CLAUDE.md` becomes an index 464 → 197, the five `.cursor/rules/*.mdc` become nine `.claude/rules/*.md` the harness loads by `paths:`, `gh` leaves the role contracts, and one prose cap becomes three — because the always-loaded floor alone prices a session that opens nothing, so a split lowers it without deleting a line. **Eight adversarial rounds, and three of the eight blocks were introduced by the previous round's fix.** Rounds 1-5 each closed one named document extension and each shipped a body claiming the rest were covered; round 6's finding is that **an allowlist of document extensions cannot be completed**, so the list that must be complete is the other one — inverted to a blocklist of code and data bounded by `git ls-files`, where an extension nobody thought of defaults to *reported* rather than to silent. Round 7 found the axis beside it: a citation by **basename** left the corpus at rc=0, because `tracked.has` compares whole paths while `CLAUDE.md` cites all thirty documents it indexes by basename. Round 8 found that round 7's fix was witnessed at its seam and never at its call site — round 6's own block one level up — and is answered by a differential control over the live corpus. 45 → 50 pins. **Four things this body called "limits" were defects wearing a label**, each closed at zero or near-zero measured cost once a reviewer probed it, which is the argument for treating a stated limit as a claim to falsify first.

- [#616](https://github.com/tvofi/heatpump_optimizer/pull/616) — **merged `d7dc142`**, `policy_lint_mutants.mjs`: each corpus check's return emptied in turn, the acceptance required to redden. It **imports `CORPUS_CHECK_NAMES` from production** rather than copying it, runs a null control before any mutation, and prints the enumeration rather than a count — a count that fell from seven to six reads exactly like one that was always six. Plus `checkProvenance`: `--record-known-bad` stamped `recorded_at` from HEAD, and a branch head is deleted by the squash that lands it, so **every ledger in this repository's history named a commit that does not exist**; stamped from the merge base now. **The lane caught the defect its own commit introduced**, which is the argument for it: the provenance witness used `HEAD` as the unreachable commit and skipped the assertion when `HEAD == origin/main` — and `governance.yml` also runs on `push: branches: [main]`, where those are equal, so the witness never ran there, an emptied check passed, and the lane would have turned `policy-docs` red on `main` at this pull request's own merge. Reproduced at both heads in a clone with `origin/main` set to `HEAD`. The witness is now a parentless `git commit-tree` commit: unreachable by **construction** rather than by circumstance. Three more from that review: `--is-ancestor` exit 1 ("no") was conflated with exit 128 ("cannot look"), turning every shallow clone into a false refusal; `pins += 3` counted a drive that had skipped; and `docs/decisions/0002`'s standing cost was 0.35s on paper against 1.3s re-measured, because the figure was taken when the enumeration held four checks and the acceptance 43 pins.

- [#617](https://github.com/tvofi/heatpump_optimizer/pull/617) — **merged `6b71e85`**, two dead symbol citations and a judge nothing has ever seated. D1 cited `_async_save` and D8 cited `entity_registry_enabled_default`; neither is a symbol in the tree, and they are **mirror images**, which is why both read as correct — one is a *prefix* of five real methods, the other is the real symbol *minus* its `_attr_` prefix. The resolver passes `-w` to `git grep`, so each fails on a word boundary a plain grep does not see. The review checked the replacements are what the briefs *mean*: `async_save` is `async_load`'s pair and the Store API all twelve production writes go through, and `tests/hastub` defines no `entity_registry_enabled_default` property at all, so a D8 finder can only read the `_attr_` form. **`judge.md` put a judge on every fix pull request and no fix pipeline has ever dispatched one** — verified across all four, none has a judge phase — so the rule was violated by every fix pull request in this programme's history. Amended to round 3 or a disputed verdict, line-neutral against a live cap of 29. Ledger 17 → 15, `recorded_at` at the merge base.
- [#618](https://github.com/tvofi/heatpump_optimizer/pull/618) — **merged `785963e`**, the archive pass and the three defects it exposed by moving the ground under four hand-kept lists. **214 files and 5.34 MiB of write-once evidence leave the tree** (net −212; 16.09 → 10.77 MiB, 564 → 352 files), reachable at `d5d8c4a`, which is an **ancestor of `origin/main`** rather than a branch head, so it survives this branch's own squash — a SHA and not a tag, because tag creation is proxy-refused here and a citation to a tag that does not exist is the class this programme removes. **The ambiguous-basename limit was a ONE-FILE escape, not the two-file one #615 claimed**: the second file never has to be planted, because it is the policy file itself — a new tracked `docs/COMMON.md`, `docs/fixer.md` or `docs/gate-scoping.md` each left every cap in silence at 0 findings, with `docs/Zednotes.md` reporting as the control. An ambiguous basename now resolves to **all** its candidates and the caller's existing filter drops those already capped and measured. **Where "sixteen" came from is established by execution** rather than guessed: driven on `e4a388a`, an exact-case resolve-to-all reports 16 and the folded one 17, the single finding between them being `round2/JUDGE.md` — so it is the count from before the fold, which `e4a388a` itself carries, and an earlier draft blaming #616 was refuted by running both (#616 is not even an ancestor of `e4a388a`). **The sweep for stale behaviour walked past a stale number four lines below its own last deletion**, in the commit whose body claimed none of them was a stale number. And a root-cause seat running beside it found **two assertions that were correct and never ran**, both live at the head: `99dd454` — the commit that landed `decisions/0003` and its rule *"do not report a refusal you have not established"* — added an arm making `checkProvenance` decline in a shallow clone and, in the same diff, an acceptance arm demanding it refuse, so both lanes went rc=1 on any shallow seat with the message asserting *"this clone is not shallow"* two lines under its own output saying it is; and `check-wave-script.mjs` printed an identical `26 passed` at 7 rosters/84 groups, at 4/59 and at **zero**, while this very branch deleted three of the seven. Both fixed, with the control that matters — in a full clone, production conflating exit 128 again still refuses, so guarding the arm did not disable it.
- [#619](https://github.com/tvofi/heatpump_optimizer/pull/619) — **merged `24e1d2f`**, the three defects the archive created and the repair of a repair. **An exclusion list #618 emptied, and the list had no assertion**: `SYMBOL_GREP_EXCLUDE` in `brief_lint.mjs` carried `:!tools/audit/round2` beside `:!.claude`, and that tree is gone, so the entry has excluded nothing since. The entry is not the finding — `policy_lint.mjs` grew exactly that assertion for `CORPUS_EXCLUDED` two rounds earlier and `brief_lint.mjs` never got one, so a file written at `tools/audit/round2/anything.py` would have been invisible to `symbolInTree` with **no diff to `brief_lint.mjs`** for a reviewer to see. Bounded now in BOTH directions per `decisions/0003`, because a ceiling alone is half an answer: `[]` names nothing dead and passes every "this entry matches no file" test while making the check vacuous. The witness row is the one that matters — with the assertion neutered and the dead prefix restored, the run is rc=0 and silent, which is the state this branch found the repository in. **A citation repair that named the wrong commit**, caught by review and worse than what it replaced: four citations were repointed to `d5d8c4a`, which carries `round2/D10/` as reports and outputs and **zero** harnesses, the executable ones having left `main` at `72a03f8` for `757e164`. A dead citation fails loudly; one naming the wrong commit tells a reader the harness was deleted when it was archived. The review then cloned the real remote with no flags to confirm all four resolve, with a `--no-tags` clone as the null control. **Two READMEs cut** to what no docstring already carries, 800→459 and 250→215, every deferral spot-checked against the actual docstrings, the ledger shrinking 15/27 to 13/25 with both deletions proven earned. **One rule change named rather than buried**: `tools/audit/README.md` went from gating the judge on `load1 > 1.5` to "quoted, not gated", resolving a self-contradiction the file already carried. And **the body corrected itself three times**, each caught by review — two numbers carried from a neighbouring branch into the null control, a run count true only before a body edit, and a "no cap moves" credited to the wrong reason.
- [#620](https://github.com/tvofi/heatpump_optimizer/pull/620) — **merged `735519a`**, `fragments_sync.mjs`: the shared prompt block the `web-*.js` dispatch scripts each copy was never byte-identical, and for the whole life of the file nothing could tell. `web-fragments.md` said "Keep the copies in sync by hand" and nothing checked it. **The measured state is worse than drift and better than feared**: all copies agree with each other and disagree with the file calling itself canonical in exactly one character — an em-dash where the scripts have `--`, on line 31 of the `GATE` fragment, in all four scripts and nowhere else. `git log -S` on both spellings returns `8ea27d4`, so neither side drifted later; **the copy was not byte-identical in the commit that created it**. Eleven fragments otherwise match exactly, which is why this lands as a check rather than a rewrite. Both sides are split by the SAME parser deliberately — a canonical parsed one way and a copy parsed another would compare two different texts and call the difference drift, making the check measure its own parser — and where a declaration's boundary cannot be found the run refuses rather than comparing a truncation. Driven by the review rather than taken from the body: perturbing one fragment in the CANONICAL file reports **all four** carriers, not one, and perturbing a copy MID-fragment at line 31 is still detected, proving the banner heuristic does not truncate at the boundary. **A finding the review null-controlled instead of reporting**: unwiring this check from `governance.yml` and `prepr.sh` is caught by nothing — but unwiring the pre-existing `policy_lint.mjs` from the same two files gives the identical result, so that is a property of the whole governance layer and not of this change. Carried forward. Known and disclosed in the body before review found it: five prose sites still say "the five `web-*.js`" when #618 left four, while every count the check PRINTS is derived at run time and correct.
- [#621](https://github.com/tvofi/heatpump_optimizer/pull/621) — **merged `07ae2d8`**, `docs/plan-2026-09-open-issues.md`: the lane table was the only copy of its facts left after #612 cut the one that contradicted it, and those facts were stale. Three statements corrected and **nine** disposition rows added — derived from the diff, after the body claimed five. The reviewer established nine by mutation rather than by counting: removing all nine gives `RECORD: 26 merged pull request(s); 9 without a disposition`, rc=1, and the tree as landed is rc=0. It is now trap 25 in `docs/HANDOVER.md` — **a body's count of its own diff must come from the diff** — and it is the reason this row states nine with the derivation attached.
- [#622](https://github.com/tvofi/heatpump_optimizer/pull/622) — **merged `d8dccd1`**, `tests/env_drift.py`, `.github/workflows/release.yml` and `tests/entities.py`. `env_drift.three_dot_files` read `stdout` from three git commands without ever reading `returncode`, so an unanswerable comparison and a genuinely clean tree produced the same empty list and `check_claims_hygiene` returned its all-clear either way — a check that cannot tell "nothing moved" from "I could not look". `release.yml`'s dispatch path interpolated `${{ inputs.tag }}` straight into a `run:` line in a job holding `contents: write`. Three further reported defects from the same deferred list are recorded **refuted, each with the command that refutes it**, rather than filed: `run.sh` is guarded, `entities.py` does enforce `SLOW_GATED`, and end-anchoring `stamp.py`'s `PR_RE` would lose seven legitimate matches while gaining nothing. Three review rounds, two `blocked`, **both on claims rather than on code**.
- [#623](https://github.com/tvofi/heatpump_optimizer/pull/623) — **merged `03af74b`**, `docs/HANDOVER.md` truthed and `docs/plan-2026-09-open-issues.md` given the carry it owed. The handover was eleven merges stale, its machine section described a box no session in it was running on, and three new traps were numbered 8, 9 and 10 — numbers the list already used — which shipped green through `policy-docs`, `prepr` and a review, because **nothing measures a numbered list's numbering**. Renumbered to the end rather than monotonically, because six sites across four files cite traps by number and renumbering would have killed all six to fix a cosmetic defect. Two review rounds. Round 1 blocked on a `## Forward-carry` naming a **branch** rather than a file `git grep` can find, and on the body reporting its distance from `118fcf2` — a value the branch had written in its own first commit and superseded twice — where the truth against `origin/main` was eleven.
- [#624](https://github.com/tvofi/heatpump_optimizer/pull/624) — **merged `cc2efc9`**, `docs/decisions/0006-policy-merge-grant-regranted-to-the-local-session.md`. Decision 0001 scoped policy-merge authority to session `019DU5u9DvSdWdcqXQnEW3ga` and says in its own text that anything after it reverts to owner approval per pull request; that session ended with this queue built and unmerged, so the authority did not carry and was **re-granted by the owner before this session merged anything**. 0001's six preconditions carry forward unchanged, and 0006 does not supersede 0001 — a record of an authority that was held and is now spent does not become false when its session ends. It also corrects the outgoing handover's *"a sixth ADR costs a line"*: established by mutation, an ADR is free until a **policy document** cites it, and `docs/plan-2026-09-open-issues.md` is corpus-excluded, which is why ADR 0001 is already cited from this very list at #610's row and cost nothing. Branch deletion is measured in it rather than asserted — the four merged queue refs deleted, `ls-remote` as witness rather than the push's own output — and ruleset creation is deliberately left to last, because a required check absent from `main` blocks every merge permanently.
- [#625](https://github.com/tvofi/heatpump_optimizer/pull/625) — **merged `d08a56a`**, `.claude/settings.json` and three hooks, which did not exist: SessionStart, PreToolUse and Stop, each standing in for a rule whose cheapest detector was minutes of CI or a forty-minute release stamp. `policy_lint --hooks` is what keeps them from becoming the claim they replace. **Two review rounds, and round 1 found the same defect class the change's own commit message names as its lesson**: `stop-selfcheck.sh`'s thirteen cases all drove helpers, none drove the wrapper, so replacing its final `exit 2` with `exit 0` left 13 of 13 passing and `--hooks` at rc=0 with the hook completely inert in production. Fixed for `pre-edit.sh` in the first draft and not for the second hook. Four end-to-end cases now drive the wrapper against a scratch repository with a stub linter whose exit status the test chooses, and the reviewer drove **five further wrapper mutations, all five caught**. Round 1 also refuted the body's unconditional fail-open claim on one of its four items: `git branch --show-current` returns an empty string both on a detached HEAD and when it cannot answer at all, and collapsing the two made the hook fail **closed** on `VERSION`, the manifest and `RELEASE_NOTES.md` whenever git was absent — **the same shape as #622**, a git command's `stdout` read without its `returncode`. Also closes two settings-level holes the review reported without blocking: deleting a hook entry left `HOOKS ok: 2 wired hook(s)` and rc=0, and repointing `PreToolUse` at another script left it green at three, so `REQUIRED` now pins the roster by **membership — event and script, not a count**, because a count is satisfied by a duplicate and by a swap. The forward-carry answer of `none` was rejected and the reviewer was right: the vacuous-mutation finding went to `tools/audit/briefs/fixer.md` step 2, **paid by cutting** — 257 lines in, 257 out, equal-line at the cap then in force, every cut line's rule verified still stated.
- [#626](https://github.com/tvofi/heatpump_optimizer/pull/626) — adds nightly A3 published-state sweep.
- [#628](https://github.com/tvofi/heatpump_optimizer/pull/628) — **merged under decision 0006**, and deliberately **without a merge SHA**: GitHub creates the squash commit at merge time, so a row a pull request writes for itself cannot name one, and #612's row saying *"Its own row is this one"* was in fact written by #621 nine merges later. The rows `07-loop` needs before its `record` job can land — #621 through #625 — established by driving the detector rather than counting: **31** merged pull requests in `v6.3.18..main` at `d08a56a`, 3 without a disposition in a `07-loop` worktree's own tree, **0 with this branch's plan file, rc=0**. Two of the five already satisfied the check and should not have, which is the hole the same change designs the fix for: principle 6 sequences it after the queue closes and before the next release stamp, and the entry under `## Carried findings awaiting a stage` carries the anchor design, its two prohibitions and its honest limit. Briefly filed as #627 and closed as wrong — an issue is not the instrument for propagation. **Round 1 blocked this pull request and was right**: it had paid for three handover traps by compressing nine entries, and the compressions cut evidence — a path, a literal glob, a worked example, trap 17's control clause and half of trap 18's prescribed verification — which `writing-for-agents.md` forbids outright, *cutting evidence is never compliance*. `docs/HANDOVER.md` is now byte-identical to its merge base apart from `updated-for:`, and the traps landed in `## Standing rules` here instead. Two counts in round 1 also failed to re-derive, both stale rather than invented: 69 rows for what is 65 at the merge base and 71 at head, and 30 merges in a window that already held 31 when the sentence was written.
- [#633](https://github.com/tvofi/heatpump_optimizer/pull/633) — UX C4: dark-theme and graphics contrast witness. leaves #558 open.
- [#635](https://github.com/tvofi/heatpump_optimizer/pull/635) — UX B12: README hero from the Playwright lane. leaves #558 open.
- [#631](https://github.com/tvofi/heatpump_optimizer/pull/631) — **merged**, measured `_stash_price_horizon` extract, leaves #224 open.
- [#634](https://github.com/tvofi/heatpump_optimizer/pull/634) — **merged under decision 0006**, without a merge SHA it cannot know: `--record`, `--stats` and `--sunset`, and the `record` CI job that runs the first of them on push to `main` — the only one of the three that can fail a job. Its mutation proof: emptying `checkRecord`'s return gives `FIXTURE VACUOUS: check 'record' produced 0 error(s) on the rot fixtures, 2 required`, rc=1 on both `policy_lint` and `policy_lint_mutants`, restored rc=0 — the acceptance pins the sub-claim, not just the count. Driven against the live window before opening: 34 merged pull requests in `v6.3.18..main`, **0 without a disposition** — #629 and #632 record themselves on the status rows of the issues they close, which is the Delivery-status table's own form, so an earlier note calling them undispositioned was wrong and is withdrawn. Lands the **handover graduation rule** as the fourth programme-closing item, with the detector-mode distinction driven at `d08a56a`: `session-start.sh:31` really does run `git rev-parse --is-shallow-repository`, but it reports rather than refuses, which suffices for trap 11 and would not for a silently-wrong-answer trap. Body written against its SHA before the push, per `steward/SKILL.md` § S10, because #628 spent four rounds learning what the other order costs.
- [#637](https://github.com/tvofi/heatpump_optimizer/pull/637) — W4-G13 S12 recorded halt: no subsystem API to migrate tests to. leaves #193 open.
- [#740](https://github.com/tvofi/heatpump_optimizer/pull/740) — **row written before the merge**, and it is this pull request: W4-G14 / S13 close-out. W4-G13's recorded halt (#637) and W4-G10's closed #224 truthed in the roster, the halt re-surveyed at the merge base and reproducing, W5-G7's brief carrying the Wave-4-closed finding, the D7-01 and D7-05 register cells updated, the handover's seam-move bullet rewritten in place. Its body carries the closing keyword for #193; this row states that as a fact. leaves #195 open. leaves #201 open.
- [#741](https://github.com/tvofi/heatpump_optimizer/pull/741) — **merged `eacdc70`, and its row is written after the merge because nobody wrote one before it**: the enumerator #681 asked for, plus the cheaper of the two decisions it feeds. `tools/audit/merge_throughput.py --from-runs` counts the overlap that matters — a later Tests `push` run on `main` whose `createdAt` precedes the previous run's `completedAt` — and `--wait` exits 1 while the latest such run is `queued` or `in_progress`, because the forced-full run on a push to `main` is the serialising resource. **A merge queue is the decision it refuses**, and the reason is this repository's own contracts rather than taste: a queue's rebase breaks `## Head`, the review's at-this-SHA rule, and the record enumerator's assumption that the reviewed head is the commit that lands. **This row is the fourth `record` red on `main` today** — after #734, then #733 and #735 — and the disposition rule's cost still lands on whoever merges next rather than on the branch that skipped the row, which is the cause analysed on #541 and answered by #738. **`Closes #681`**, and the row that first stood here asserted the issue was still open — false when written: #681 was closed `completed` at 2026-09-10T18:53:11Z by this very merge, and a row about another seat's pull request is exactly where an unread issue state does the most damage. leaves #201 open.
- [#745](https://github.com/tvofi/heatpump_optimizer/pull/745) — **row written before the merge, and it is this pull request**: two disposition rows — #741's and its own, plus three later rows for merges nobody recorded. **Two earlier forms of this row were wrong in opposite directions**: the first said two, written before #749 merged without one; the second said three, written after I added #749's row — and then `main` wrote #749's row itself, so mine was withdrawn and the count went back to two. Measured rather than carried: `git diff $(git merge-base origin/main HEAD)...HEAD -- docs/plan-2026-09-open-issues.md | grep -cE '^\+- \[#'` returns the count, and `'^-- \[#'` returns the rows removed, which must be `0` — a row of another lane's dropped silently is the near-miss this branch hit twice. `main` was red on `record` at `e713ab4` — 31 merged pull requests in the window, 1 without a disposition. **The self-row is in a second commit and the split is forced, not chosen**: a disposition needs the pull request's number and the number does not exist until the pull request does. **The proof simulates the merge rather than measuring the branch head**, because at the branch head the merge has not happened, the window does not contain this pull request, and the check prints the same figure whether or not the self-row exists — a vacuous arm that has appeared twice on record branches already. leaves #201 open.
- [#742](https://github.com/tvofi/heatpump_optimizer/pull/742) — **row written before the merge**, and it is this pull request: W4-G14's own `resume` flipped to `done` with #740's squash SHA `e082136` and the roster `fork` re-pointed at it, because a `done` entry needs a SHA that exists only after the merge; every Wave 4 group now reads `done`. Roster only. leaves #195 open. leaves #201 open.
- [#744](https://github.com/tvofi/heatpump_optimizer/pull/744) — **row written before the merge**, and it is this pull request: W5-G9 (dhw profile learner) and W5-G10 (legionella guard) enter the Wave 5 roster with the simulation that chose them, W5-G4 and W5-G7 re-sequenced behind W5-G9, the D7-01 cell names the follow-on — and **`main` went red on `policy-docs` at `a07f435`**: #719 netted +3 lines on `docs/HANDOVER.md` on top of #740's +2 and the sum crossed the cap of 406 at the time (trap 19, both branches green, neither able to see the other). Repaired here by tightening three bullets in place to 405, never by raising the cap. leaves #193 closed. leaves #195 open. leaves #201 open.
- [#747](https://github.com/tvofi/heatpump_optimizer/pull/747) — **row written before the merge**, and it is this pull request: an instrument repair, in no wave. `tests/env_drift.py` applied the inherited-claims guard to both claim files once a branch moved anything claimable, so the first solver branch after #735's six card claims (W5-G9) was refused for a card list it could not have written and offered the deletion #662 forbids; the autofix would have made that deletion. Per file kind now — `claims_hygiene_verdict`, shared by the guard and the bot — pinned with the live case, its null control and the twin of each harm shape; two #662 pins that encoded the per-branch rule are rewritten with the reason. Found locally before any push; process state (c). leaves #193 closed. leaves #195 open. leaves #201 open.
- [#750](https://github.com/tvofi/heatpump_optimizer/pull/750) — **row written before the merge**, and it is this pull request: **W5-G9**, the dhw profile/draws learner leaves the coordinator for one class in a new module. Thirteen methods and nine constants move verbatim under a stated substitution table (provenance residual: the boundary edits only); thirteen call sites re-pointed; the pump map goes to the runtime init; about forty `features.py` sites migrate to the learner's API. Every ratchet row falls or holds except `classes_over_300`, raised 9 → 10 on the owner's decision of 2026-09-10; goldens byte-identical across 55 scenarios at the merge base. leaves #193 closed. leaves #195 open. leaves #201 open.
- [#753](https://github.com/tvofi/heatpump_optimizer/pull/753) — **row written before the merge**, and it is this pull request: R1, the seam programme's one policy-touching pull request. `cross_seam_fraction` leaves the budget table for the absolute count `cross_seam_edges`, an ordinary one-sided row (owner decision D2, 2026-09-10): a cohesive extraction removes more intra- than cross-seam edges, so the ratio rose past its band on the simulated legionella move while the count fell, at `e4f3436` when the plan was written and again at the head. `FRACTION_METRICS`, `NEVER_RERECORDED` and the tolerance leave `tests/structure.py` with it; the #350/#370/#374 pins drive the count; `CLAUDE.md` rule 2, `fixer.md`, `orchestrator.md`, `D7.md` and five Wave 5 briefs stop naming the fraction; W5-G9's roster entry flips to done (#750). Merges only on the owner's approval; W5-G10 is blocked on it. leaves #193 closed. leaves #195 open. leaves #201 open.
- [#756](https://github.com/tvofi/heatpump_optimizer/pull/756) — **row written before the merge**, and it is this pull request: #680 accepted by the owner on 2026-09-10. Decision 0008 records the machinery in 0005's order — machine account with write, the authorization switch, a seat's verified login, then the code-owner rule on `main-protect`, never the rule first — and `.github/CODEOWNERS` names the owner for the policy set, inert until that rule exists. 0005 carries a status note and stands until step 3(c). Policy; merges only on the owner's approval. leaves #680 open until the rule is live. leaves #541 open. leaves #201 open.
- [#758](https://github.com/tvofi/heatpump_optimizer/pull/758) — **row written before the merge**, and it is this pull request: **W5-G3**, the second application of the tail batching rule #705 landed. The Home Assistant object boundary in eleven modules — the coordinator-and-entry constructor on the entity platforms, the entity properties reading off the coordinator, setup and its lazy imports, and the defs taking `hass`, a service call or repair-flow data. Annotations and local narrowings only; three sites needed more than a signature and each says why in place. The census records 191 → 163: 24 of that is this batch and four were `main`'s own unrecorded improvement. The tail's other half, the value-conversion boundary, is the next batch, because the derived cap is 30 and a single 51-error sweep exceeds it. leaves #303 open. leaves #201 open.
- [#760](https://github.com/tvofi/heatpump_optimizer/pull/760) — **row written before the merge**, and it is this pull request: the record for R1's merge, plus one owner decision. W5-G10's `resume` leaves `blocked` for `pending`, since #753 (`d737ab0`) put `cross_seam_edges` on the table and the retired ratio no longer reads that extraction as a breach. **Owner, 2026-09-10: #558's lane F runs immediately after Wave 5 and #412**, carried into F1's and F2's briefs in `.claude/workflows/wave-ux-groups.json` with what the wait buys and the payment scan it still owes. `docs/HANDOVER.md` reads `updated-for: a801d7c`. leaves #558 open. leaves #201 open.
- [#763](https://github.com/tvofi/heatpump_optimizer/pull/763) — **row written before the merge**, and it is this pull request: the nightly lane was forced to run at the owner's instruction (runs 34537901814 and 34538569051) and failed 4 of 58 checks on both matrix arms. Two are one defect in `tests/nightly_ha.py`: the blocking probe's begin/end markers were appended to `home-assistant.log` behind Home Assistant's own handler, which overwrote them, so the window did not exist and the two checks reading its halves failed in opposite directions on the same provoked report. The markers are log records now. `run:exit_status` was their cascade. The fourth, `a5:byte_unchanged`, is a real finding this pull request makes legible rather than fixes: the detail now names the keys and the changed values, and the next run named eight weekend and holiday comfort keys plus `peak_tariff_window_minutes`. Verified after the fix: 4 failures → 2, run 34539632659. leaves #201 open.
- [#765](https://github.com/tvofi/heatpump_optimizer/pull/765) — **row written before the merge**, and it is this pull request: **W5-G3**, the third and last batch of the #303 tail: the value-conversion boundary in eleven modules — every def that turns an untyped or optional value into a float, a numpy array or a typed mapping, plus `dhw_learning.py`'s two bare `Store` generics, which postdate #705's persistence sweep. Census 163 → 135; the tail reads zero after this and only `optimizer.py` and `coordinator.py` carry errors. Two edits change an expression and each carries its control: the unbounded-age sentinel narrows by `isinstance`, and the `MODES` comprehension's `is not None` guard is shown to drop nothing by comparing the dict at both ends. leaves #303 open. leaves #201 open.
- [#767](https://github.com/tvofi/heatpump_optimizer/pull/767) — **row written before the merge**, and it is this pull request: **#412**, the programme's last scheduled task. Every action that still declared `node20` moves to its lowest `node24` major — 48 occurrences over seven usages in five workflow files, and the set is **not** the three the deprecation warning names, because a warning lists only the actions the printing job used. `actions/cache` needed it too, which #412 asked to be checked rather than assumed, and so did both artifact actions, which its inventory never mentions. The job graph is identical at both ends and the three-dot carries nothing but `uses:` lines. Closes #412. leaves #201 open.
- [#636](https://github.com/tvofi/heatpump_optimizer/pull/636) — W5-G2: sensor.py annotations, ruler 518→371. leaves #303 open.
- [#642](https://github.com/tvofi/heatpump_optimizer/pull/642) — W4-G10 S9 recorded halt: `optimize` 30–50 LOC verbatim has no remaining seam at `30a202e`. leaves #224 open.
- [#646](https://github.com/tvofi/heatpump_optimizer/pull/646) — W4-G10 S9: `_optimize_with_dhw` always-hot DHW baseline extract, max_method_loc 489→455. leaves #224 open.
- [#657](https://github.com/tvofi/heatpump_optimizer/pull/657) — W4-G10 S9: `_optimize_with_dhw` nested `solve_space` leaves (hot loop, stress lane). leaves #224 open.
- [#663](https://github.com/tvofi/heatpump_optimizer/pull/663) — W4-G10 S9: `_build_dhw_requirements` stage-4 A-half leaves as `_dhw_window_floors`. leaves #224 open.
- [#666](https://github.com/tvofi/heatpump_optimizer/pull/666) — W4-G10 S9: 14-key `DhwPlan` return. leaves #224 open.
- [#639](https://github.com/tvofi/heatpump_optimizer/pull/639) — **merged under decision 0006**, without a merge SHA it cannot know: `policy_lint_envmatrix.mjs`, the declared-environment matrix that builds five shapes of this repository and fails a row whose run does not produce what the row declares — or a shape it cannot build — plus the `env-matrix` job, decision 0004 (*an assertion can be correct and never run*), and the `prepr.sh` widening. Mutation proof against production, not the harness, and via a temporary commit because the matrix clones from git objects: disabling the shallow-clone disclosure in `policy_lint.mjs` takes it to 11 held / 2 not, rc=1, both in the `shallow` shape; restored 13/13. A vacuous first attempt — a shell-form search string against an array-form call, zero occurrences, an empty WIP commit, 13/13 against an unmutated tree — is disclosed, because it read exactly like a pass until the occurrence assertion caught it. Trap 8 (*one CI runner is not the fleet*) gains its detector with this merge, the fifth in the graduation rule's runway; the ruleset's `env-matrix` context now exists on `main`. Body written against its SHA before the push, per S10; `--claims-only` at the merge base `ok`, because `main`'s claim list is empty and an empty list inherits nothing.
- [#641](https://github.com/tvofi/heatpump_optimizer/pull/641) — **merged under decision 0006**, without a merge SHA it cannot know: `fix-review.md`'s verdict examples corrected to the grammar `web-fix-wave.js` actually parses — for a session the contract said `blocked: finding not carried to <stage>`, no SHA, no class, which `VERDICT_RE` rejects — plus `D7.md` truthed and decision 0005 recording why one identity authoring and approving makes a required-approval rule a lock. **The fix was unpinned and this branch pins it**: reversing the contract change left every detector green, so `check-wave-script.mjs` now extracts each backticked example beginning `blocked ` or `merge ` and runs it through the grammar rebuilt from the wave script's own text, with a floor of three so an empty extraction cannot pass — **37 passed at head**, the pin having since been widened to read every brief in `tools/audit/briefs/` rather than the contract alone. Driven, and stated as the assertions actually fire rather than as they did when this row was first written: **reversing one example is refused by the `blocked:` assertion**, 35/1 — the floor does NOT fire, because four examples across three files survive a floor of three; **deleting all three examples does fire the floor**, `found 2`, 33/1; a wrong class keeps its space and is refused by that file's own parse assertion, 36/1; and the negative control shows the grammar itself refuses the old form. The earlier reading of this row credited the floor with the reversal, which its own commit falsified two commits later — a row is a claim about the head it merges at, not about the head it was typed at. Body written against its SHA before the push, per S10; `--claims-only` at the merge base `ok`.
- [#638](https://github.com/tvofi/heatpump_optimizer/pull/638) — nightly A10 diagnostics privacy probe. leaves #533 open.
- [#645](https://github.com/tvofi/heatpump_optimizer/pull/645) — W5-G3: away.py annotations, ruler 371→354. leaves #303 open.
- [#647](https://github.com/tvofi/heatpump_optimizer/pull/647) — W5-G3: ledger.py annotations, ruler 371→360. leaves #303 open.
- [#648](https://github.com/tvofi/heatpump_optimizer/pull/648) — W5-G3: defrost.py annotations, ruler 371→355. leaves #303 open.
- [#655](https://github.com/tvofi/heatpump_optimizer/pull/655) — nightly A5/A8/A9 options, services, reload. leaves #533 open.
- [#651](https://github.com/tvofi/heatpump_optimizer/pull/651) — **merged**, the loop detector cannot tell "no blocking call" from "no log". leaves #533 open.
- [#654](https://github.com/tvofi/heatpump_optimizer/pull/654) — W5-G6: process_worker.py in-process pins, 0.0%→92%. leaves #505 open. leaves #195 open.
- [#640](https://github.com/tvofi/heatpump_optimizer/pull/640) — W5-G3 first cut: wood_fuel.py annotations, ruler 355→325. leaves #303 open.
- [#643](https://github.com/tvofi/heatpump_optimizer/pull/643) — W5-G3: config_flow.py annotations, ruler 297→271. leaves #303 open.
- [#661](https://github.com/tvofi/heatpump_optimizer/pull/661) — nightly A4 availability fault-injection. leaves #533 open.
- [#664](https://github.com/tvofi/heatpump_optimizer/pull/664) — UX E1: setup and reauth token fields use the same password selector as options. leaves #558 open.
- [#665](https://github.com/tvofi/heatpump_optimizer/pull/665) — UX E2: finish-setup-now after the second screen. leaves #558 open.
- [#667](https://github.com/tvofi/heatpump_optimizer/pull/667) — W5-G6 leftover: grid_fee.py lone-month refusal. leaves #505 open. leaves #195 open.
- [#668](https://github.com/tvofi/heatpump_optimizer/pull/668) — UX E3: setup overview as last config-flow step. leaves #558 open.
- [#656](https://github.com/tvofi/heatpump_optimizer/pull/656) — W5-G3: thermal_model.py annotations, ruler 271→248. leaves #303 open.
- [#649](https://github.com/tvofi/heatpump_optimizer/pull/649) — W5-G3: dhw_schedule.py annotations, ruler 247→239. leaves #303 open.
- [#650](https://github.com/tvofi/heatpump_optimizer/pull/650) — W5-G3: price_model.py annotations, ruler 239→232. leaves #303 open.
- [#687](https://github.com/tvofi/heatpump_optimizer/pull/687) — the record this session opened with, before any product cut: five roster `resume` fields and the Wave 5 Delivery-status cell truthed against measured `origin/main`. W5-G1 and W5-G2 said `in-review` and `pending` on work that had merged; W5-G6 said `pending` on a tranche #589 landed two days earlier; W5-G3 named `away.py` as next when it had already landed and `snapshots.py` is next; W4-G10 said `in-review` when its DhwPlan carrier (#666) was on `main` and nothing of that group was in review. The Wave 5 cell carried a census figure that has moved by more than half; it now names `tests/typing_budgets.json`, where the figure is re-read at a merge base. #589's own disposition, owed since the last sweep, is written. **Two controls in its body are worth more than the diff**: an unrecognised `resume.stage` this branch first introduced is refused by `check-wave-script.mjs`, and a bad path in `resume.note` is invisible to `brief_lint.mjs` while the same path in `brief` is an error — the fields a record truths are checked by nothing but a reader. leaves #303 open. leaves #195 open. leaves #224 open. leaves #505 open.
- [#652](https://github.com/tvofi/heatpump_optimizer/pull/652) — W5-G3: snapshots.py annotations, ruler 232→226. leaves #303 open.
- [#689](https://github.com/tvofi/heatpump_optimizer/pull/689) — the `hassfest` countermeasure the root-cause seat established on #201: a retrying warm-up `docker pull` in `.github/workflows/hassfest.yml`, so the pinned composite action's bare `docker run` finds the image already cached. It addresses process state **(a)**, the missing property being *a required context's third-party fetch retries* — `hassfest` was the one member of the 18-context required set that had none, which is why it was the one that failed. The reference warmed is byte-identical to the action's own `docker run` argument, read from `action.yml` at the pinned SHA rather than assumed; a reference differing by one character leaves the cache cold and the step doing nothing, which is the null control that arm carries. **No demonstration on the defect is offered and none is producible** — GHCR cannot be made to return `toomanyrequests` on demand, and this is a recovery step rather than a detector, so what is shown instead is the retry loop's own failure and success paths driven over the shipped `run:` text with a stubbed `docker`. The **relocation** is measured, and by a property rather than a duration: `Unable to find image … locally` appears once in the green `hassfest` job before this change and **zero** times in the green job on this branch, with the same 23 validations run, so the action's `docker run` consulted no registry. Standing cost: the added step's own non-pull overhead on every run, forever — **carried as an upper bound, because at n=2 it is not separated from runner noise**. Counting rule: the warm-up step's whole span in the raw job log (its own `##[group]Run` line to the next step's) less the registry transfer inside it (`latest: Pulling from` → `Status: Downloaded newer image`), never the jobs API's step span, which is rounded to whole seconds and so cannot resolve it. That gives **0.80 s and 1.80 s gross** in the branch's two green jobs (`102572589934`, `102574580941`), or **≈0.3 s and ≈1.3 s marginal** after netting off the 0.52 s the pre-change `docker run` spent on the same work before its own pull. So the figure carried forward is **≤ ~1.8 s**, not a point estimate; an earlier draft of this row said ≈0.2 s, which was derived from `Checkout`'s `##[endgroup]` rather than the warm-up step's and subtracted from a second-rounded span, and the fix reviewer refuted it. The cost test clears the bound by about an order of magnitude and does not turn on the sample: 696 s × 5 failures ÷ that day's attempt count stays above 1.8 s for any denominator below ~1,930, against 219 attempts when re-derived. The whole-job figure moved 22 s → 26 s and is deliberately *not* quoted as that cost, because both sides are n=1 and the pull time itself varied by 2.8 s between them. `hassfest.yml` is on `closure.py`'s `INERT` list, so the gate selects nothing on it. Closes nothing; leaves #201 open.
- [#690](https://github.com/tvofi/heatpump_optimizer/pull/690) — the record four merges owed and did not carry: `docs/HANDOVER.md` brought current from eleven merges back, net shorter, no cap raised. Its substance is three corrections rather than an update: **trap 26 was stale inside the trap about staleness** (it counted the count rules, and #676 added the ninth without touching the sentence — the one figure no derivation can check, since none counts the derivations); **W4-G10's roster note carried a premise the tree refutes** — the two remaining halves cannot read `DhwPlan`, which is a frozen dataclass built only at its method's return, so the judge's incremental-carrier reasoning and the delivered design disagree; and **the Delivery-status table asserted `In review` on work that had merged**. Three passes, because the count was wrong twice and a review refuted it each time -- round 1 the first count, round 2 the second. **No count is stated here, deliberately** — it decays with the next row and it was the part that kept being wrong. The rule is: a bullet whose *own verdict* asserts a review state while `gh pr view <n> --json state` says `MERGED`, with quoted prose excluded, since several repaired rows now quote the phrase they replaced. Sweep it with that rule rather than reading a number out of this row; at this head it returns the empty set. Two of the misses are worth naming because they were the same defect: #549 said *awaiting **the owner's** approval*, which a sweep for the other spelling missed, and #593 was half-repaired — the merge appended **beside** the false field instead of replacing it, which is exactly the shape trap 31 describes and the second thing in this pull request to exhibit it. The traps list is reordered into source order, which is #685 and is line-neutral. Carries the owner's model-routing ruling of 2026-09-09 and the fact a Fable trailer measures the session's model, not routing. leaves #303 open. leaves #195 open. leaves #224 open. leaves #505 open. leaves #685 open.
- [#691](https://github.com/tvofi/heatpump_optimizer/pull/691) — **the UX roster recorded a stage word with no referent.** Fourteen groups sat at `resume.stage: "in-review"` carrying only `stage` and `note`, and `web-fix-wave.js` maps that to `review`, whose branch reads `g.resume.pr ?? g.resume.open_pr` and `g.resume.head_sha` — so a wave over this roster dispatches fourteen adversarial reviewers at PR `undefined`, from a worktree detached at head `undefined`. Nine more were at `done` with no `merged_pr`/`merge_sha`; three — B12, C4, E1 — were at `pending`, *"Not started"*, on work merged as #635, #633 and #664, and `pending` normalises to the fresh-fixer path that re-opens merged work. `check-wave-script.mjs` was green throughout, because it asserted the stage VOCABULARY and never the REFERENT; that missing assertion is what this pull request builds, and the rule is read off the wave script rather than invented — a stage requires a key exactly where that script dereferences `g.resume.<key>` with no `?? null` fallback and then hands it to an agent or reports it as fact. **`blocked` is exempt on that same rule and the exemption is stated**: its branch spells both keys `?? null` and dispatches nobody, so requiring them would fail the one committed `blocked` group, whose roster is not defective. **Widening past `review` is what found the nine `done` groups**; a review-only check would have left them. Every group is established one at a time from the API and from `main`, never swept — a merged pull request is not a delivered item — and **B4 is the one that separates the two**: its item, a hero above the fold, is delivered, but the asset #567 committed is not in the tree, because B12 (#635) replaced the interim `card_rig` SVG with the Playwright PNG. All fourteen items landed. The lane cells above are truthed with it: B, C, D and E are complete on `main` and #516 is closed. **Read the delivered state from the roster's own `merged_pr`/`merge_sha`, never from a count in this row.** leaves #558 open
- [#693](https://github.com/tvofi/heatpump_optimizer/pull/693) — **merged `e3072ef`**, the two residuals #691's review named as follow-ups (the rule/map gap and the branch-scoping of the stale-key guard, not the two that review itself blocked on). `check-wave-script.mjs` now **derives** the stage-to-key map from `web-fix-wave.js`'s own branch source — the rows, the OR/AND structure, and the `blocked` exemption — and asserts the hand-written map equals it, so the stated rule and the executed map can no longer be edited apart. Its other half, which its reviewer called the arm that matters: the stale-key guard is now scoped to the branch that requires a key rather than accepting one read anywhere in the script, and the roster scan cannot see that class at all — only the guard discriminates it. The `fix` row keeps `pushed_sha` alone, justified from the script's second enumeration of resume keys rather than from taste: the Reconcile prompt names that key because it is the one `fix` key that is a claim about a fact at origin. Its review did not accept the author's demonstration arms as proof that a derivation derives — an arm the author chose only shows the check fires where they aimed — and perturbed the script in five directions of its own; splitting a `??` chain into two dereferences made the derived side report AND where the map says OR, which is the failure a second hand-encoding would produce. **Carried, not closed:** a false `pending` — a group whose work merged — stays invisible, because `pending` is unkeyed by design: a group that never started is indistinguishable from one delivered last week in every field the script reads, whatever their prose notes say. leaves #558 open. leaves #201 open.
- [#696](https://github.com/tvofi/heatpump_optimizer/pull/696) — **the record that cleared `main`**, and its own row is here because a record pull request that omits itself does not clear the red, it moves it: the post-merge `record` run would refuse #696 exactly as it refused #693. Its review established that by simulating the merge rather than reading the branch — `--record` resolves `origin/main`, so a run at the branch head measures a history the branch is not in. Carries #693's disposition, missing because four seats were told not to touch this file and #693 was merged before the record that was to carry them; and #692 plus #697-#703, filed while this lane was running and named nowhere. leaves #692 open. leaves #697 open. leaves #703 open.
- [#695](https://github.com/tvofi/heatpump_optimizer/pull/695) — **merged `1684e62`**, closing #683: the mutation lane covered the corpus checks and never the record mode's three outputs. A second enumeration is exported from production beside the first rather than copied — its review tested that by adding a real record-mode check to production only and running the lane untouched, where it was picked up and mutated. Two targets live in `counts.mjs`, so the lane mutates that module and rewrites the importing specifier, **asserting the rewrite**, with a control proving a cross-module mutation that never reaches the acceptance reports accepted rather than a false pin. The regex-list arm is distinct from the check arm, shown by weakening the witness until one passes and the other does not. The review verified every mutation at source level under a write hook, because a green arm can mean a mutation that never applied. It also repaired, rather than filed, a contradiction found while gating its own body: `prepr.sh` forwarded no intended-issue list to `preflight.sh`, so a body carrying the closing keyword `fixer.md` step 7 requires was refused, while `pr-contract` runs the same script with a fallback that binds nowhere. That forwarding has no committed regression test and its body says so. leaves #201 open.
- [#694](https://github.com/tvofi/heatpump_optimizer/pull/694) — **row written before the merge, deliberately** (see the note below): `prepr.sh` compared the body's `## Head` against the **local** head only, so a body naming a commit the remote does not yet carry passed locally and reddened `pr-contract`. It now derives `refs/remotes/<remote>/<branch>` from the branch and its configured remote — the pull request's own head ref by construction — and reads `@{u}` nowhere. Round 1 blocked it for over-firing: `@{u}` may name `origin/main` when a branch was cut with `checkout -b … origin/main`, which refuses a healthy branch, and branches in this clone were configured that way while it was open. **The count is not written here**: it read 2 of 10, then 1 of 10, then 0 of 11 within two hours as seats pushed with `-u`. Derive it — a branch whose `branch.<name>.merge` is not `refs/heads/<name>` — rather than reading a number, which is what #694's own body concluded and what this row nearly undid. Round 2 settled the design with a shape neither round had run — main-tracking **and** the branch's own remote ref ahead — where the shipped form refuses correctly and the alternative guard would have fallen through to skip. Seven fixtures now carry two assertions each, the ref and the verdict, because the blocking defect lived in the half that had none. Narrows #678; leaves #678 open. leaves #201 open.
- [#708](https://github.com/tvofi/heatpump_optimizer/pull/708) — **the record that cleared `main` the second time**, and the protocol change that stops a third. Twice this evening a pull request merged before its disposition existed — #693 and #695 — because four parallel seats had been told not to write plan rows, to avoid four rows colliding at one anchor. That was right about concurrent **writers** and wrong as applied to **merging**, which is serial. **The narrower true rule, which is what a later seat needs:** a row is added by a branch that must itself merge, so it *is* a concurrent writer at that anchor — two record pull requests open at once still collide. What makes this work is **one serialising writer**, not the ordering alone. `checkRecord` tests only that the number appears in a disposition document, so a row may precede its merge, and #694's above does. **That closes the window for the pull request whose row precedes it, and for no other.** Any pull request merging without a row reddens `record` the same way, whoever opened it — the check enumerates every merge on `main`, not this programme's. Its own row is here because a record pull request that omits itself moves the red rather than clearing it — established on #696 by simulating the merge rather than reading the branch. leaves #201 open.
- [#704](https://github.com/tvofi/heatpump_optimizer/pull/704) — **row written before the merge**, and not this programme's work: the repository owner's DHW-tank-only setup, opened while the governance lane was running. It is here because `checkRecord` enumerates every merge on `main` regardless of who opened it, so a merge without a row reddens `record` for everyone. Outside #201; no wave covers it and none is claimed to. leaves #201 open.
- [#706](https://github.com/tvofi/heatpump_optimizer/pull/706) — **row written before the merge**, same reason: the owner's typed setpoint for a dumb mixing valve. Outside #201. leaves #201 open.
- [#746](https://github.com/tvofi/heatpump_optimizer/pull/746) — **merged `2072fec`**: typed indoor °C setpoint for a mixing valve with no target entity. `describe_setup` publishes `manual_setpoint` on the valve-target slot; `assign_entity` persists `mixing_valve_target`; the Setup picker offers the number on that slot only. Successor of draft #706, which was not merged. Outside #201. leaves #201 open.
- [#748](https://github.com/tvofi/heatpump_optimizer/pull/748) — **row written before the merge, and it is this pull request**: leftover row for #746 `2072fec`. `main` was red on `record` at that squash — 32 merged, 2 without (#746 and #741). This dispositions #746. #741 stays #745's. leaves #201 open.
- [#707](https://github.com/tvofi/heatpump_optimizer/pull/707) — **merged `c2e9200`**, the owner's seven leftover product features: Pulse bind (#703), Nord Pool entity (#701), 15-minute clock (#697), DSO catalog (#698), weekend/holiday profiles (#700), sensor-gap € (#699), wood-burn advisor (#702). Outside #201. Issues CLOSED completed.
- [#705](https://github.com/tvofi/heatpump_optimizer/pull/705) — **row written before the merge**: W5-G3's tail, whose deliverable is a batching rule rather than a cut — whole modules grouped by the protocol they implement, with the size cap derived from the nine merged tranches rather than chosen. Its review refuted the premise under that rule with a one-line perturbation: a parameter type consumed elsewhere moves its error to the consumer, so a module is **not** closed by construction and the per-module control is mandatory rather than confirmatory. The rule survives; the reason under it did not. leaves #303 open.
- [#716](https://github.com/tvofi/heatpump_optimizer/pull/716) — **merged `a1f148a`**, closing #684: `tools/audit/worktree_gc.sh`, dry-run by default; `--apply` deletes only a detached, clean worktree whose HEAD is not an open pull request's head and whose directory mtime is older than 60 minutes. A branch worktree is never touched. The `--self-test` is the acceptance. leaves #201 open.
- [#717](https://github.com/tvofi/heatpump_optimizer/pull/717) — **row written before the merge**: leftover #684 still said in review after #716 landed. leaves #201 open.
- [#710](https://github.com/tvofi/heatpump_optimizer/pull/710) — **merged `e50aa51`**, closing #692: twelve registered services and a shipped catalog that said eleven and omitted `set_away`. The README table is `services.yaml`'s keys. leaves #201 open.
- [#711](https://github.com/tvofi/heatpump_optimizer/pull/711) — **row written before the merge**: leftover #692 still said in review after #710 landed. leaves #201 open.
- [#713](https://github.com/tvofi/heatpump_optimizer/pull/713) — **merged `4e28724`**: the nightly's conclusion reached nobody for two nights. `nightly-ha` and `slow` run on `schedule` alone, are skipped on every push- and pull-request-triggered commit, and are in none of `main-protect`'s required contexts, so a scheduled run's verdict attaches to whatever commit was `main`'s head when cron fired and the next merge strands it. `tests/nightly_status.py` reads the last **concluded** scheduled run and reports it as its own check on every pull request. A root-cause seat costed a notifier that files an issue and **refused** it, because it buys latency rather than prevention and needs a permissions widening against a `contents: read` floor the workflow states as deliberate. leaves #533 open.
- [#714](https://github.com/tvofi/heatpump_optimizer/pull/714) — **row written before the merge**, closing the blocking call the nightly lane caught at `coordinator.py:832`. The route was established as the `atexit` backstop rather than the executor offload, on three independent legs, the load-bearing one being that the loop-protection warning printed a single stack frame and so had no Python caller. The reap on that route now kills first and waits without a timeout, reaping through `os.waitpid`, which blocks in C instead of polling with `time.sleep`. The loop-side reap keeps its graceful terminate. A `KNOWN_BLOCKING` entry was rejected deliberately: its key carries no thread and no caller, so it would have masked the #525 class at the very site the pin watches. Both lane arms move from one offender to zero. Its review found the fix **understates** its own harm, since `time.sleep` is registered strict, so the old wait raised and the child was never reaped at all on that path. leaves #533 open.
- [#715](https://github.com/tvofi/heatpump_optimizer/pull/715) — **row written before the merge**: `tools/audit/push.sh`, the countermeasure #678 specified and nobody built, so that a branch cannot reach the remote before its body has passed the contract check. built after the defect recurred across 2026-09-09 and 2026-09-10. #678's own cost test measures the **closed** half and its literal stands, 9 red `pr-contract` runs at merged heads on 2026-09-09; the 09-10 half is an **open** window, so #715's body carries a runnable enumerator rather than a number, per `writing-for-agents.md` — and its first enumerator did not run, which the fix review caught and the body records. Its first review returned **blocked**: when the query for an existing pull request *failed*, the script read that as "no pull request exists", took the push-first arm, and pushed against an open pull request's stale body — the defect it exists to prevent, reached through itself. In a repair round with a self-test case for that path. **Its policy half needs the repository owner's approval before merge**, being one sentence each in `fixer.md` and `orchestrator.md`; both files were at zero line headroom and the seat paid by deleting prose rather than raising a cap. **Two departures from #678's own words, both argued in the body**: step 4's "atomically" cannot be delivered against GitHub, so the script guarantees the ordering instead and says so; and for the arm where a pull request already exists the issue's step order is inverted, because setting the body after the push is what makes the `synchronize` run read the stale body at the head a reviewer reads. leaves #678 open.
- [#718](https://github.com/tvofi/heatpump_optimizer/pull/718) — **row written before the merge**, and it is this pull request: #713, #714 and #715 had no disposition row, and #714's head is frozen under a `merge` verdict, so the rows could not be written into the branches they describe. The fourth record branch today, and the first of the four a frozen head forced: #708 was the serialising-writer protocol change, and #711 and #717 were leftover rows whose truth changed at a merge that had already landed. leaves #201 open.
- [#709](https://github.com/tvofi/heatpump_optimizer/pull/709) — **row written before the merge**: the `nightly-ha` runner installed nothing, so the driver's HOST half -- which imports the production package to stage the seed's `unique_id` and the A3 roster -- died in `_stage` on both matrix arms for two consecutive nights, before Docker was reached at all. It adds the same pinned dependency-install step four other jobs already run, and a `tests/entities.py` check that pins **this job's wiring** rather than the derived rule ("every job that runs a `tests/` script installs the requirements"), which was measured and over-fires on four jobs that legitimately install nothing. Necessary and **not sufficient**: with it the lane reaches Home Assistant for the first time since 2026-09-08 and is still red on both arms, for causes carried as **preconditions** into the #533, #584, #585, #587 and #588 rows above rather than fixed here -- a container abort that reaches the host as "never ran", an `a3:roster` expectation derived from the tree it checks, and `log:no_integration_traceback` counting the A4 lane's own injected fault. leaves #533 open. leaves #201 open.
- [#720](https://github.com/tvofi/heatpump_optimizer/pull/720) — **merged `e49b2fb`**, closing #677: the record job enumerates merges from `/commits/{sha}/pulls` per first-parent commit and keeps the trailing-`(#N)` regex as the offline fallback. `GITHUB_TOKEN` is on the record step only. leaves #201 open.
- [#721](https://github.com/tvofi/heatpump_optimizer/pull/721) — **merged `8db8abe`**, closing #682: both disposition documents are walked as rendered tokens and compared back to source — cell count vs header, table count vs source pipe-blocks, ordered-list source number vs rendered ordinal, and a `#NNN` link that is not an issue or pull. markdown-it is vendored; `governance.yml` is untouched. leaves #201 open.
- [#725](https://github.com/tvofi/heatpump_optimizer/pull/725) — **merged `52b9eb6`**: #720 and #721 had no disposition row, and both heads were frozen under decision 0007, so the rows were written here rather than into the branches they describe. leaves #201 open.
- [#726](https://github.com/tvofi/heatpump_optimizer/pull/726) — **merged `6baa0ce`**: leftover #677 and #682 still said in review after #720 and #721 landed. leaves #201 open.
- [#727](https://github.com/tvofi/heatpump_optimizer/pull/727) — **merged `6799ef4`**: leftover #683 still said filed after #695 landed, and leftover #697-#703 still said the issues were open after they were marked completed. leaves #201 open.
- [#729](https://github.com/tvofi/heatpump_optimizer/pull/729) — **merged `cd2e663`**: leftover #582 still said under refutation; #713 still said in review; #707 still said the issues were open; #724 still said do not merge. leaves #201 open.
- [#730](https://github.com/tvofi/heatpump_optimizer/pull/730) — **row written before the merge**: leftover #574 still said unclaimed; leftover issue-table cells still said scheduled, in flight, filed, or this PR after those issues closed. leaves #201 open.
- [#719](https://github.com/tvofi/heatpump_optimizer/pull/719) — **row written before the merge**: `docs/HANDOVER.md` stopped at `updated-for: a6e95ff`, which is #689's merge. **The staleness is named by its enumerator and by no number at all**: the first form said “nine merges”, which matched no rule the tree runs, and every rule that does run — `git log --format='%s' a6e95ff..HEAD | grep -cE '\(#[0-9]+\)$'`, the variant of it that excludes `record:` commits, and `policy_lint --record --since a6e95ff`, the tree's own record enumerator — answers a different question and answers it again at every merge, so a number here is stale before it is read. **No cap is raised and no budget re-recorded** — every addition is paid for by cutting, and the headroom is `policy_lint --budgets`'s to print rather than this row's. What was cut is stated by the test each line failed, not by volume: the preamble restated the rule the harness loads on this very path; the ratchet-raise order is `CLAUDE.md` rule 2 verbatim; “the orchestrator is bound by every contract it enforces” is `orchestrator.md` section 0's own heading; the `## Figures` format is `.github/PULL_REQUEST_TEMPLATE.md`'s. **The largest cut is this file's own rule turned on the handover**: the #575 and #541 declines, the cloud-seat identity (#680) and half the #510 correction were restated there while carrying Delivery-status rows here — the handover links this table and does not restate it, and it was breaking that in four places. Added: the verdict grammar, folded into the trap about the same defect rather than appended as a second one. **The finding is a set over a closed window, and every corpus total that once stood beside it is cut rather than corrected**: a total over issue comments is answered by a corpus that grows with every comment, which `brief-citations.md` names as an error, and it is why three review rounds on this branch blocked on a number and none on the substance. **Six `Fix review: revise` verdicts** — a class the closed `VERDICT_CLASSES` list does not carry — across **five** pull requests: #686, #687, #689, **#690 twice** and #708, between 2026-09-09T15:19:48Z and 2026-09-10T06:33:11Z. That window is closed and the multiset cannot move, so the sweeps are stated where the totals were. Repository-wide: `gh api --paginate '/repos/tvofi/heatpump_optimizer/issues/comments?per_page=100' --jq '.[]|.html_url+"\t"+((.body//"")|split("\n")[0])'`, then match the first-line field against `^Fix review:`. Per pull request: `gh api --paginate '/repos/tvofi/heatpump_optimizer/pulls?state=all&per_page=100' --jq '.[].number'`, then the same first-line extraction over `issues/<n>/comments`, `pulls/<n>/reviews` and `pulls/<n>/comments` for each number. **Two sweeps because each is blind where the other sees**: the repository-wide one reaches the `Fix review:` first lines on issue **#201**, which the per-pull-request sweep never visits, and misses the one `Fix review: merge` posted on #501 as a *review*, which the issue-comment endpoint cannot return. Controls, and they hold in both: **#531 carries no `revise`** — its `Fix review:` first lines are `Fix review: blocked — …`, a non-parsing shape with no SHA and no class, plus one bare `Fix review: merge`, and both sweeps return them — so its absence is a fact rather than a miss; a verdict class the repository has never used returns none; and each sweep counts its own API failures rather than reporting a total a swallowed 403 would silently have deflated. **An earlier form of this row named #531 and read the six as one per pull request**: the total was right for the wrong set, which is how the error survived — trap 29 in the handover says only “six verdicts” and was correct throughout. Also added: a worktree sharing the repository's config and refs, which is how `git remote remove origin` inside one repointed the main checkout and dropped every remote-tracking ref; `worktree_gc.sh`'s collection criteria, and that **`git worktree lock`** is the claim mechanism for a detached seat — `classify()` keeps a `locked` worktree ahead of every criterion, as it does the `main`, `current` and `missing` paths, none of which the script's header names, though no `--self-test` case pins that path. **An untracked marker file is not**, and an earlier form of this row recommended one: at this head `tests/closure.py select --diff origin/main` prints `MODE: SCOPED` with no marker and `MODE: FULL` with `reason: no recorded closure mentions .seat-claim-probe` when a marker is added at the repository root — three arms, the third being the same marker under `.claude/`, which stays `MODE: SCOPED`. Keyed on the mode line and not on the script count, which `CLAUDE.md` rule 1 requires and which is a figure the suite moves. The mechanism costs the gate its scoping; the scheduled-context half of the required-check trap; and **`--red` has never fired** — `governance.yml`'s body-contract step passes no `--red`, so the refusal that requires a body to name and answer a red check iterates an empty list on every pull request this repository has run, which makes `CLAUDE.md`'s “only the red-check trigger is enforced” an intent rather than a measurement. **No trap is renumbered**, so the citations #685 tracks are untouched. **Carried as owed, not claimed:** `fix-review.md` step 11 rests on an assumption the `--red` finding invalidates, and that file is policy. Also owed and undecidable by a seat: `finding-propagation.md` sends a finding that constrains every seat to one role contract before the producing pull request merges, which two concurrent branches owing a carry cannot both do. **Second repair round, both after a `claims` block.** Round two corrected three quantified claims and cut a fourth — `wave-ux-groups.json` was called “the only one a linter reads”, which `brief_lint.mjs`'s `main()` refutes, since with no arguments it lints every `wave-*-groups.json` in the workflows directory; the clause is **cut** rather than corrected because what would replace it is `brief-citations.md`, which the harness already loads on that path, so it fails the uniqueness half of `writing-for-agents.md`. Round three reproduced the set, the span, both asymmetries and every control exactly and blocked on the two enumeration totals alone, which re-derived to neither printed value under any of the nine counting rules it executed, at a constant offset in both. **The repair is removal, not a tenth rule**: both were counts of a growing corpus, so a corrected pair is wrong at the next comment. The record-excluding enumeration goes with them: round one printed one figure for it and round two a different one, and neither is a number this row should carry. Both sweeps were re-run whole at this head, each counting its own API failures and each reporting none, and both return the same multiset. **A new instrument fact fell out of doing it**: under GitHub's *secondary* rate limit `gh api rate_limit` reports `remaining: 5000` while every other call returns HTTP 403 *API rate limit exceeded*, so that endpoint is not a usable pre-flight for a sweep of this size, and a sweep that appends the response body on failure writes the 403 JSON into its own result file. Owed to the handover, which is at its cap. **The rule this repair applies landed on `main` while the repair was being written.** #724, from the root-cause seat on this same defect, moved *name the instrument, never the figure it prints* out of the handover's own paragraph into `writing-for-agents.md`'s criteria paragraph and extended it: where the corpus is out of the tree and its window still open, the artifact carries the **enumerator** — the command that, run alone, prints exactly that number — and the literal goes only in `## Figures`; a count over a *closed* window is carved out, which is why the multiset above stays. This row was already in that form, and it is now the rule rather than this seat's judgement. Two consequences here: the handover's copy of the moved sentence becomes a restatement of policy the harness loads on that path, so it is **cut and replaced by a pointer**, keeping only what `writing-for-agents.md` does not carry — the `coordinator_loc` measurement the rule was written from; and the re-flow is equal-line, so the file is still at its cap. **The branch was updated onto `main` repeatedly, and the count is given by an enumerator rather than stated**, because it moves at every update and the previous form of this sentence went stale twice before a reviewer caught it: `git log --merges --format='%h %p' origin/main..HEAD` lists them with the `main` commit each took. Main's rows are taken **verbatim** every time, this row re-applied after them, and each resolution is verified by a whole-file comparison rather than by reading the conflict region — `diff <(git show "$(sed -n 's/^updated-for:[[:space:]]*//p' docs/HANDOVER.md):docs/plan-2026-09-open-issues.md") docs/plan-2026-09-open-issues.md`, which must report one added line, this row, and none removed. **The command reads the SHA out of `updated-for:` instead of naming one**, so it cannot drift from the field it is checking, which is the exact defect that blocked this branch: the field named #727's merge while the head had merged #728's, and the quoted result was two commits old. **The comparison names the merged SHA and never `origin/main`**: that ref moved under this seat mid-round, on a fetch another worktree sharing these refs ran, so a claim pinned to the ref stops being reproducible the moment anyone else fetches. Taking *ours* at either point would have silently reverted #726's rewrite of two rows and #727's of eight, none of which this branch touched - no conflict marker, no failing test. `updated-for:` moves to that merge. The handover lands at its cap, the number being `policy_lint --budgets`'s to print. **One residue is deliberately not carried**: the review noted that “`pr-contract` is required by `main-protect`” now survives nowhere in the handover. It does not earn a line — the file already names ruleset `main-protect` id `22628467` and the enforcement it buys, and which contexts are in its required set is what that instrument prints, which is the same file's own companion rule. **A limit on #724's own carve-out, found while applying it, and recorded here because both of its proper destinations are shut.** #724 exempts a count over a *closed* window from the enumerator rule, on the ground that no future comment can move it. Closing the window bounds `created_at` and nothing else: comment bodies stay editable and deletions leave no trace, so a closed window is not an immutable corpus. It is not hypothetical - `Fix review:` first lines in this repository have been edited after posting, and the enumerator is `gh api --paginate '/repos/tvofi/heatpump_optimizer/issues/<n>/comments?per_page=100' --jq '.[]|[.id,.created_at,.updated_at,((.body//"")|split("\n")[0])]|@tsv'` over the threads a sweep reads, comparing the two timestamp fields; a deletion has no field to compare and no sweep can bound it. **The control is that this does not weaken the set above**: every one of the six `revise` comments has `updated_at` equal to `created_at` under that same enumerator. The limit belongs in `writing-for-agents.md` beside the carve-out - policy, needing the owner's approval before merging, and itself at zero headroom under `policy_lint --budgets` - and the handover's trap list is the other home and is at its cap. Neither is payable by this branch, so it is written where a later seat reading this table meets it, rather than filed as an issue. leaves #201 open. leaves #685 open.
- [#723](https://github.com/tvofi/heatpump_optimizer/pull/723) — **row written before the merge**: an orchestrator worktree 69 commits behind `main` dispatched a review seat into a `fix-review.md` predating `58aec5f` and `43d3e93`, so the seat would have written a verdict `web-fix-wave.js` cannot parse and read checks with a call that reports `pr-contract` green where it was red. `tools/audit/preflight.sh` gains a **stale policy corpus** check: a file `origin/main` moved since the merge base that this branch does not touch, three-dot on both sides, corpus read from `POLICY_GLOBS` through a new `policy_lint.mjs --corpus-filter` rather than copied. Not "differs from `origin/main`", which fires on exactly #715 and #722, the branches doing intentional policy work. It **warns**: every other refusal in that script is a property of the text on stdin, staleness is a property of the checkout, and the evidence is a local mirror nothing fetches. `preflight.sh` runs before a **push** and a fix reviewer never pushes, so the check does not reach the seat the defect hurt; the forward-carry that closes that is one sentence in `tools/audit/briefs/fix-review.md`'s detached-worktree step, **written into this branch**, which makes this a policy change needing the repository owner's approval before merge — that file was at zero line headroom and the seat paid by deleting a line rather than raising a cap. Its first review returned **blocked** for naming the carry and not making it. The first fixture did not pin the check — disjoint sets make `moved - authored` and `moved` agree, so the mutation that matters left all three arms green. leaves #201 open.
- [#733](https://github.com/tvofi/heatpump_optimizer/pull/733) — **merged `07bdc55`**. Two-hour DHW and space-heat boost switches. Overlay lives in `boost.py`; lookup is `held_for`. **Row written after the merge, not before** — the merge landed without one and `record` went red on `main`. leaves #201 open.
- [#735](https://github.com/tvofi/heatpump_optimizer/pull/735) — **merged `8dc7813`**. Setup can add and remove the DHW and wood tanks; return time shows on Setup when Away is on; collapsed card still has no away strip. **Row written after the merge, not before**. leaves #201 open.
- [#736](https://github.com/tvofi/heatpump_optimizer/pull/736) — **row written before the merge**, and it is this pull request: `tools/audit/briefs/fixer.md` step 14, the forward-carry #714 established and could not place because the file stood at its cap in `.claude/workflows/policy_budgets.json`. #714's reviewer judged the lane-side destination in `tests/nightly_ha.py` adequate and recorded the residual — the general lesson lived only in a lane-specific file. The step states what the instance illustrates: an allow-list entry silences everything its **key** matches, so the test before adding one is to key the occurrence the pin exists to catch and compare it with your own — `KNOWN_BLOCKING` is keyed on (call, file, source snippet) and #714's report was legitimate only because of its caller, which no field of that key carries; and a fix that changes the **route** rather than the snippet leaves the reported call, file and snippet in place, so a search for the offending text and a search for its absence mislead alike. The **line** is no help either and is not in the key: #714's own fix moved `worker.wait(timeout=2)` from 808 to 832 while the defect it reported was being fixed. The per-file cap was raised with the owner's confirmation obtained before the push (#201 comment 5616844489 item 2), the reason in the commit message per `CLAUDE.md` rule 2, and bounded by the step — one line less refuses. One line was paid out of the same file by cutting a sentence that fails `writing-for-agents.md` on uniqueness — an earlier form of this row said two, and the review established that half of that "payment" was a rewrap deferred: the cut paragraph had been left as a single 109-character line where no prose line in the file exceeds 82. Reflowed to the file's own convention, the honest bound is 278, which is the cap now recorded. No role cap and no `tests/structure.py` metric moved. The lane-side copy stays: it carries the mechanism, the step carries the rule. Also repairs the #625 row above, whose quoted cap this raise falsified. **The step's wording still needs the owner's approval; only the cap raise is already given.** Closes nothing; leaves #201 open.
- [#739](https://github.com/tvofi/heatpump_optimizer/pull/739) — **row written before the merge**, and it is this pull request: #733 and #735 merged without a disposition and `record` went red on `main`. `checkRecord` enumerates every merge regardless of author, so a record branch names itself or reddens on its own merge. leaves #201 open.
- [#743](https://github.com/tvofi/heatpump_optimizer/pull/743) — **row written before the merge**, and it is this pull request: an instrument repair, in no wave. #735's six card claims made `tests/card_drift.mjs` fail every branch for a list the branch did not author, reddening `fast (3.13)` and `fast (3.14)` — both required contexts. `tests/env_drift.py` already refuses to do this: #658 gave it `stale_claims_judged`, and on one tree `--claims-only` printed `ok` while `card_drift.mjs` failed the same branch seven times. The judgement is ported into `tests/card_rig.mjs`, where the other two mirrors of `env_drift.py`'s claim rules already live, and both claim failures are gated on it — reported either way, judged only against a branch whose three-dot could have caused them. Neither refused remedy was taken: no claim line is deleted (#569, #633) and no merge is reverted. **The finding it leaves open**: the two instruments now carry the judgement in two copies and nothing checks that they agree; a shared module and a parity check are both closure changes larger than the unblock, so neither was built. leaves #201 open.

**Why a disposition may precede its merge, and exactly how far that goes.**
`checkRecord` tests that `#N` appears in a disposition document; it does not require the merge to
have happened, and it enumerates every merge on `main` regardless of who opened the pull request.
Twice in one evening `main` went red because a pull request merged before its row existed — #693
and #695 — both times because four seats had been told not to write plan rows, to avoid four rows
colliding at one anchor.

That instruction was right about **concurrent writers**. It was wrong as applied to **merging** — but
the correction is narrower than it first reads, and three limits belong with it:

- **A row is added by a branch that must itself merge**, so it *is* a concurrent writer at that anchor.
  Two record pull requests open together still collide. What makes this work is **one serialising
  writer**, not the ordering alone.
- **Writing the row first closes the window for that pull request and for no other.** It is not a
  general fix. Any pull request merging without a row reddens `record` the same way.
- **The set is enumerated at writing time and decays.** Rows written here cover the pull requests open
  when this branch was written; the serialising writer re-enumerates immediately before merging rather
  than trusting this paragraph.

And one cost, stated because nothing detects it: **a pre-emptive row for a pull request that is closed
unmerged becomes a permanent false disposition**, and `checkRecord` cannot see it — the check asks
whether the number is mentioned, never whether the mention is true. #704 and #706 were drafts when
their rows were written. The trade is deliberate: a false row is a reader's problem, a missing row is
a red `main`, and the `record` job is post-merge only, so the cost of the second is never a refused
pull request and always a broken default branch.


**A pattern worth naming**, since most of these were blocked for it: every one of those blocks was a document asserting something that was not true of the tree — a stale head, a count, an actor, a carry that did not land. None was a disagreement about the change itself.

### Governance queue — where this lane's rows go from here

Both lanes appended their disposition rows to the end of one list, so every
merge on `main` conflicted the other lane's open branch at that seam: this pull
request was rebased five times for it and #639 three, each rebase costing a
fresh review round at a head whose code had not changed. The rows above stay
where they are; **from here this lane appends below and every other lane appends
there**, so the two insertion points are never adjacent and neither lane waits
on the other. No pull-request number is named as the boundary: one was drafted
into this sentence and taken by another lane four minutes later. **What reads this row, stated as it is
today and not as it will be:** `checkRecord` tests `#<pr>` against the whole
text of both disposition documents, so a row is read wherever it sits in either
of them — driven by moving #648's row clean out of `## Delivery status` into
`## Carried findings awaiting a stage`, which leaves `--record` at 47 merged, 0
undispositioned, with masking that number in both files as the null control that
does report it. The pull request after this one narrows that to the
`## Delivery status` section alone, which is why this subsection is placed
inside it rather than after it.

- [#644](https://github.com/tvofi/heatpump_optimizer/pull/644) — **merged under decision 0006**, without a merge SHA it cannot know: `docs/decisions/` leaves the measured corpus, named one by one so a seventh decision costs a line; 0006 added to that list; 0005's status line stops waiting on the question the same file answers. Closes the queue 05–10; the ruleset's `record` and `env-matrix` contexts both exist on `main` from here.
- [#658](https://github.com/tvofi/heatpump_optimizer/pull/658) — **merged under decision 0006**, without a merge SHA it cannot know: the record check's region narrows from both documents whole to `## Delivery status` plus the handover, so a pull request mentioned in passing is no longer dispositioned by that mention; the list-item anchor this plan proposed was refuted first (it refuses #629 and #632, dispositioned inside table cells); pinned by seven acceptance assertions over synthetic input, tip invariant 76 → **83** pins across the same 10 classes; the handover's `updated-for` catches up; and the backticked-verdict finding is carried.
- [#662](https://github.com/tvofi/heatpump_optimizer/pull/662) — **merged `2d06e06`**: a branch that moves no fixture was told to EMPTY the claim files, and a squash applies that deletion to `main` — #608 carried 33 of #569's claim lines off, #635 the same to #633's, #658 was stopped on the way to #653's. The rule is now *leave both files exactly as you found them*, which is the same rule whenever the baseline claims nothing. Three routes closed: the record check, the autofix bot, and the stale-claim judgement. This row is written by the pull request AFTER it, because #662 merged before its own row existed — which is the defect `record` is for, caught by `record` itself.
- [#659](https://github.com/tvofi/heatpump_optimizer/pull/659) — **merged under decision 0006**, without a merge SHA it cannot know: the environment matrix stops counting its shapes off the filesystem and counts what the run built, refuses a work directory it would otherwise reuse, and pins its thirteen outcomes by NAME and by COUNT — names catch a swap, the count catches a duplicate, and the first version had only the names, which round 1 measured. Null control: the previous script, with a shape deleted and a stale work directory, certifies five shapes and twelve outcomes at rc=0.
- [#660](https://github.com/tvofi/heatpump_optimizer/pull/660) — **merged under decision 0006**, without a merge SHA it cannot know: the handover's cap deadlock is resolved by a GRADUATION rule — a trap whose failure mode has acquired a mechanical detector becomes a one-line pointer to it, and each graduation owes a mutation proof that breaking the detector turns a check red. Four graduate (8, 9, 11, 19); trap 17 does not, because its only proof is a push to `main` with two branches arranged to collide, and a detector nobody drove is what the rule forbids trading prose for. 276 → 273 lines and the cap ratchets down with them.
- [#669](https://github.com/tvofi/heatpump_optimizer/pull/669) — **merged under decision 0006**, without a merge SHA it cannot know: the reporting hole that let #625 merge with a red `pr-contract` at its head and a body saying `## Red checks: none`. The listing that shows one run per check is refused in every file the corpus MEASURES — the plan of record is not one of them, so this entry may keep naming it while no document that instructs a seat can — in every policy file **including the MCP mapping table**, which is where a seat with no `gh` binary looks up what to run — an exemption there would have been the hole rather than an escape from it. The table and `fix-review.md` step 11 now name the commit's `check-runs` API. Three findings this queue closed are marked closed in the entries above.
- [#670](https://github.com/tvofi/heatpump_optimizer/pull/670) — **merged under decision 0006**, without a merge SHA it cannot know: **decision 0007** records the owner's O3 ruling — after this session a policy merge needs approval per pull request, with a per-session grant of the 0001/0006 shape as the option. It DATES what it says about the repository — the ruleset did not exist when the decision was taken — and does not wait on it; the first draft wrote that in the present tense, which would have gone false the hour the ruleset is created. 0006's sentence calling O3 an open question is corrected rather than left to age, and the seventh ADR pays its line in the exclusion list, which is what that list is for.
- [#671](https://github.com/tvofi/heatpump_optimizer/pull/671) — **merged under decision 0006**, without a merge SHA it cannot know: closes **item 2 of #583**, which stays open for item 1. A fixer proves a check by breaking the thing it checks and restoring it; a seat stopped between those steps leaves a production file altered, and the alteration reads as an edit. The Stop hook now names any uncommitted **tracked** production file under `custom_components/` at the moment the seat stops — **reported, never refused**, because a seat may legitimately be mid-edit and a Stop hook that blocks work in progress is a cage. Measured on this box while writing it: ten worktrees carried an uncommitted change at once, six of them a single production file in a mutation worktree. **What it does not watch**, named so nobody assumes otherwise: untracked files, deletions, and arms under `tests/`, `tools/` or `.claude/` — including the hook itself. Item 1 of the issue's cheap version, a `.mutation-active` marker written by the seat, is **not built**: it needs the seat to cooperate, and the whole point of a stopped seat is that it did not.
- [#672](https://github.com/tvofi/heatpump_optimizer/pull/672) — **merged under decision 0006**, without a merge SHA it cannot know: #581 asked for a literal figure of any kind to be refused in a brief; the rule that would do it was built, driven and **refused on its own issue's criterion** — 20 reports on the live briefs, five of them the defect, and the false ones are a sweep window repeated in prose and evidence from a completed measurement, which is what a brief is for. What lands is the resolving half: `policy_lint`'s eight derived counts had never read a `wave-*-groups.json`, and seven of them did from #672. `modules` is withheld because the brief genre uses that word for a subset; the shared enumeration moves to `counts.mjs`, a third module, because the linters' existing import direction makes any other arrangement a cycle.
- [#673](https://github.com/tvofi/heatpump_optimizer/pull/673) — **merged under decision 0006**, without a merge SHA it cannot know: the Delivery-status table outranks anything that disagrees with it, so a row that stopped being true is worse than a missing one. #580 was closed `not planned` by judge ruling on 2026-09-07 and its row still had three seats deliberating; **two residuals of that ruling lived only in a comment on the closed issue** and are carried into the tree here — `fix-review.md` has no step for an ABSENT check, where a pull request whose workflows never queued shows a reviewer no red checks at all, and the mutation proof is executed twice and lands in prose both times. #575 and #541's rows described plans that this session declined. #581's row now says which half of its figure is independently reproducible, because the rule that produced it is deliberately not in the tree. `--record` was clean throughout, including while #672's own entry sat in the wrong section, and the reason is narrower than it looks: #658 already cut `checkRecord`'s region to `## Delivery status` plus the handover, and line 84 is **inside** that region. So the check saw the number and was satisfied. Placement is invisible *within* the region, by design — the region says where a disposition may live, not where it must sit.
- [#674](https://github.com/tvofi/heatpump_optimizer/pull/674) — **merged under decision 0006**, without a merge SHA it cannot know: **26 of the Delivery-status table's 36 rows were not in a table.** A blank line ended it at 363, and everything below rendered as literal text with its pipes showing while the source still read as a table. Through GitHub's own `/markdown` endpoint at `7d8d271`: one table of 11 rows plus 104 loose pipe characters; without the blank line, one table of 37 rows and none. Found while reviewing #673, whose author and round-1 reviewer both explained a five-cell row's survival by saying GitHub truncates the extras — **the wrong explanation is what sent a seat looking for the real one**. The detector lives in the RECORD mode because `docs/` is not a policy directory and no corpus check has ever opened either disposition document; it tells a split apart from two adjacent tables by looking one line further for a delimiter row. Pinned in both directions, and the over-firing arm found that `table` was in the `silent` map but not in `REQUIRED_SILENT`, so that control was inert until this change. **Disclosed rather than papered over:** gutting the call site in `cmdRecordDispositions` leaves the acceptance green, which is the standing limit #614 recorded — no assertion inside a program pins its own last call site.
- [#675](https://github.com/tvofi/heatpump_optimizer/pull/675) — **merged under decision 0006**, without a merge SHA it cannot know: `docs/HANDOVER.md` stopped at `a9d117c` and could not take a line, so 24 merges of durable findings went to *Carried findings* instead — correct under the deadlock note, and not where a cold session looks first. **The owner raised the cap for this, explicitly, before the branch was pushed**, and it is recorded at **whatever `wc -l` answers at the head that lands**, with one below it turning `policy_lint` red. **No number is given here, deliberately.** The cap moved on every round of this pull request's review — each round's corrections added lines — and each time it went stale in this row before it went stale anywhere else. **A count of how many times is not given either**, for the same reason: the first draft of this sentence carried one, and reviewing the sentence moved it. A figure that is a function of the file it describes belongs in the file's own budget entry and nowhere else; `policy_lint --budgets` prints it. The floor and all three role caps are untouched, because `roleTokens` counts the always-loaded set and the scoped rules a role opens, never the opened file. Plus the staleness sweep: this plan said **`main` is unguarded** and that a ruleset *would* guard it, now rewritten as what was created and measured; the closing #201 obligation it recorded as owed is **discharged**; ADRs 0001, 0005 and 0006 carry **dated status notes rather than rewrites**, because a decision record states what was true when it was taken. **CLAUDE.md and `orchestrator.md` are left silent about the merge boundary on purpose** — both sit at their caps, and because the index is always-loaded, two lines there overflow **five** caps at once (floor 3195 → 3245 against 3228). That is the owner's call, not a seat's.
- [#676](https://github.com/tvofi/heatpump_optimizer/pull/676) — **merged under decision 0006**, without a merge SHA it cannot know: three rules from one recommendation, applying to author and orchestrator alike. **Name the instrument, never the figure it prints** — generalised in `writing-for-agents.md` from a sentence it already carried, and landed as a clause in `fixer.md` step 3 and `orchestrator.md` section 1, each in its own words because `duplicates` refuses a repeat. **A cap stated beside its file's name is checked** by `counts`, resolved by unique suffix against the budget file rather than guessed, in the corpus, over roster briefs, and alone in `--record` over both disposition documents — the other eight rules were driven over this plan first and reported four quotations of history, so they stay out. Measured before wiring: one figure across every genre, and true. **A body has a `## Figures` section**, required by the same contract as `## Red checks`, so the cost of enumerating figures sits with the author and a reviewer reads a list. Every capped file this touches stays at its cap by reflowing the same words; no raise. **Side effect, stated**: the other lane's open pull requests carry no `## Figures` and `pr-contract` refuses them at their next push until one is added. Two sentences in this plan were anchored, not deleted, because the new rule read them as live claims. The `#` guard's healthy control was inert in its first form and the mutation arm found it.
- [#686](https://github.com/tvofi/heatpump_optimizer/pull/686) — **merged, without a merge SHA it cannot know**: nine disposition rows for #677–#685, the issues filed on the owner's instruction from this session's closing recommendations, appended to the issues table after #541 so this list's insertion point is untouched. Its null control, as the review corrected it: a blank line before a row is reported by the `table` class at its line, and a row whose leading pipe is deleted is correctly not reported — GFM makes that pipe optional and the row still renders, checked against GitHub's own renderer rather than assumed.
- [#688](https://github.com/tvofi/heatpump_optimizer/pull/688) — **D11, a twelfth audit dimension: governance mechanisms and policy** — **policy, merged under decision 0007 with the owner's approval given on the pull request**: a twelfth dimension brief, `tools/audit/briefs/D11.md`, in the owner's words, auditing the governance mechanisms against public standards — OpenSSF Scorecard and Best Practices, SLSA, NIST AI 100-1 and AI 600-1, ISO/IEC 42001, the OWASP LLM Top 10, DORA's four keys — and measuring the structure's own health: detector controls, friction recurrence, sampled conformance, staleness outside the corpus, cost per merge. Threaded through every site that enumerates dimensions: the `CLAUDE.md` table, `COMMON.md`, the toolkit README, `finding.schema.json`, the dispatcher's lists (D11 isolated, since it needs `.git` and the API), and the budgets. The counts of auditors that the corpus carried in prose were removed rather than bumped, so the next dimension edits no sentence.
- [#722](https://github.com/tvofi/heatpump_optimizer/pull/722) — **open, policy; needs the owner's approval under decision 0007 before merging**: `finding-propagation.md` sends a carry to that stage's own brief and `delivery-status-tracking.md` makes this document the only valid destination for a stage with no roster group, which under concurrency cannot both be satisfied — #709 and #718 were in that position on 2026-09-10, and #708, #711, #717 and #718 each change this file and no other. A stage with no roster group now has `.claude/workflows/carry-<N>.json`, one file per destination issue, so two branches carrying to two stages write two files. `brief_lint.mjs` lints it — `from`, `effect` (one of the rule's three, never free text), `control`, `remeasure`, and a citation-checked `brief` — and refuses both an empty `carries` array and a carry filed at an issue a roster already covers, so no stage has two destinations. Fixtures pin it in both directions, and every mutation of a rule turns the acceptance red — including the over-fire direction, which only the clean fixture can catch. `rosterIssues`, the reader deciding whether a stage already has a destination, was reached by no acceptance and indexed only integers; it now takes a numeric string, still refuses a non-numeric one, and has its own probe. **What the tree scan cannot see, said plainly** — four cases, two of them checked: a carry file never created is not in the scan, so that arm is `policy_lint.mjs`'s `--pr-body` rule on `## Forward-carry`, which tests **existence, not authorship**. So a body naming a destination already in the tree that received nothing this round passes both layers, and that case — with a pull request that owed a carry and wrote `none` — is decidable by neither and stays with the fix reviewer. A diff-membership predicate for the third was measured and refused rather than argued away: the rule collects every path token in a prose section, so it tests the citations too, and of the open pull requests on 2026-09-10 whose `## Forward-carry` was not `none`, every one names a path absent from its own diff — a mechanism cited as context, or a destination named as owed but deliberately unwritten because it is policy the owner must approve. A round-two body carried the false form of this, "a body naming a carry it did not write is refused", and the review blocked on it. **The correction owed with it**: this rule said the record pull request carried the disposition "so it costs no extra PR"; `fixer.md`'s handoff freezes the branch at the head under review, so it cannot, and the same clause is corrected in `writing-for-agents.md` and `orchestrator.md` section 9 — which retired one `policy_known_bad.json` entry. **No cap moves**: an earlier revision raised `delivery-status-tracking.md`'s cap and cited an owner approval reachable from no record, and the review refused it; the correction is reflowed into the bullet it corrects instead, so `.claude/workflows/policy_budgets.json` is byte-identical to `main` and the role caps this pushed against are paid for by prose deleted from `finding-propagation.md`. Run `--budgets` for the figures rather than reading one here. **Dispositions this row also carries**: **#582** ("lanes B–F have no roster, so the finding-propagation policy has no destination for them") is **closed `completed`**, by the owner at 2026-09-10T10:12:56Z — twenty-nine minutes before this branch’s first commit, so the row that first said it stays open was false when written. Its closing comment names the destination it said did not exist, `.claude/workflows/wave-ux-groups.json`, landed as #601 (`ac84d86`). What that closure did not cover, and what this pull request answers, is the general form the issue also stated: any work organised outside the wave rosters inherits the same gap. No re-opening is asked for. Every issue status in this row was read from the API at the head that carries it, not from the session’s memory of it. **#681** is **scheduled unchanged** and receives the first forward-carry to the new destination, `.claude/workflows/carry-681.json`: merge throughput here has a second serialisation point besides the gate which costs no gate time at all, so measuring only against the forced-full gate would attribute those four pull requests' latency to the gate and find nothing there. **Not migrated**: the carries already sitting in `## Carried findings awaiting a stage` stay where they are — they have been delivered to their readers, and rewriting that section is the contended edit this change exists to avoid.
- [#724](https://github.com/tvofi/heatpump_optimizer/pull/724) — **merged `44f914a`**, with the owner's approval for its policy half: `## Figures` asks for *"the command that printed it"* and nothing executes that command, so the contract has grip only where an instrument in the tree prints the figure — and every figure refuted in this session was over the GitHub API or this repository's own review history, while every figure that re-derived was over an in-tree corpus. The root-cause seat (#201 comment `5618564043`) named process state **(c)** from a split inside one body, one section, one author: #719's `## Figures` bullet 1 gave a `gh api` command that prints the corpus and two literals it cannot print and was blocked, while bullet 2 stated a `git log` enumerator instead of its number and survived the same round untouched. **The seat refused to build a check and that refusal stands** — the narrowest predicate it could write is `preflight.sh` check 3, which is deliberately advisory, and `docs/HANDOVER.md` trap 12 records the sibling attempt's measured catch rate. What lands instead is a writing rule: where the corpus is not in the tree **and its window still open**, the artifact carries the enumerator — the command that, run alone, prints exactly that number — and the literal goes only in `## Figures`. The closed-window carve-out is deliberate: a count over a finished window is a fact no later event moves, and a clause that refused those would fire across the legitimate history already in this plan, the handover and the release notes, which is the false-fire surface that killed the check. Equal-line at the cap, no raise and no re-record; the three deleted sentences and the test each failed are in the body. It stays in one file — `brief-citations.md` covers the corpus a linter can open, `fixer.md` and `orchestrator.md` carry the warning half and are at their caps, and `duplicates` refuses a repeat. leaves #303 open. leaves #195 open. leaves #224 open. leaves #505 open.
- [#728](https://github.com/tvofi/heatpump_optimizer/pull/728) — **`Closes #505`**: the #195 tranche partition becomes a predicate with an enumerator, and gains the residual group W5-G8 that its complement needs to land in. The finding is not that the list was wrong but that a list cannot be right for long — the roster's own carry into W5-G6 quoted #505's figures, and `process_worker.py` had already been pinned by #540 before that seat read them. `tools/audit/w5-partition/coverage_tree.sh` measures the package over the default-gate script list **derived** from `tests/run.sh` and writes nothing inside the worktree; `partition.py` prints the partition and refuses a roster with no residual group and a done tranche's module that has fallen back below the bar, both demonstrated by its `--self-test` beside their null controls. **Friction worth keeping**: `brief_lint.mjs` returns zero errors for `wave-5-groups.json` at `44f914a` while two of its briefs carry coverage readings that later merges had already superseded — rule 4 reaches a count the tree can answer, and a coverage count is not one. leaves #195 open. leaves #303 open.
- [#734](https://github.com/tvofi/heatpump_optimizer/pull/734) — **merged `a94bbaf`**, the owner's lane, outside #201. The headline score was the **house time-constant grade**, not a judgment of when the tank ran: overall was the mean of whichever of envelope, machine and operation existed, and a fresh install has neither machine nor operation evidence, so overall *was* envelope — about 5 for a ~24 h house. Operation also skipped any day under 1 kWh, which is most summer DHW-only days. Overall is now the mean of machine and operation only; envelope stays in the breakdown. **Row written after the merge, not before** — the merge landed without one and `record` went red on `main` at 15:53:48Z. leaves #201 open.
- [#737](https://github.com/tvofi/heatpump_optimizer/pull/737) — **row written before the merge**, and it is this pull request: #734 merged without a disposition and `record` went red on `main`. `checkRecord` enumerates every merge regardless of author, so a record branch names itself or reddens on its own merge. leaves #201 open.
- [#738](https://github.com/tvofi/heatpump_optimizer/pull/738) — **row written before the merge**, and it is this pull request: **CM-2** of the root cause on #541 (comment `5622000848`), whose home for the record is **#678**, where process state **(c)** is already recorded for the identical cause on a different surface. `record` is one of `main-protect`'s 18 required contexts while reporting `skipped` on the only event a seat reads it at — 17 `success` and `record` alone `skipped` at #734's head `b63470b` — so the disposition rule is enforced only after a merge and the red lands on whoever pushes next. `tests/record_status.py` reports `main`'s current `record` conclusion as its own red check on every pull request: #713's construction pointed at `record`, with `skipped` refused as ABSENT rather than accepted as a pass the way the nightly correctly accepts it, and staleness measured in commits rather than nights. It does **not** prevent a merge without a row; it converts "`main` is red and nobody looks" into "every open pull request says so". CM-1, a pre-merge own-row check in `pr-contract`, was **refused** on #541 with a number — 5 false refusals per true one, because 5 of 6 rowless heads were dispositioned by a companion record pull request. **CM-3, taking `record` off `main-protect`'s required contexts, is a ruleset change and the owner's; this pull request does not make it and `record-status` is **not** added to the required contexts either.** leaves #678 open. leaves #201 open.
- [#749](https://github.com/tvofi/heatpump_optimizer/pull/749) — **merged `ef7599e`**: `.gitignore` was declared unread (`INERT`) while a gate script read it, so touching it forced the FULL suite. Classification only. leaves #201 open.
- [#751](https://github.com/tvofi/heatpump_optimizer/pull/751) — **merged `86c95c3`**: leftover #533 nightly-ha product/setup (A3(e) indoor/climate, A5 `option_resubmit`, A8 ConfigEntry fields, A14 ConfigEntry bind, A4 UpdateFailed pin). Left #533 open. Does not implement A6/A11/A12/A13. Dispatch `34529186389` on that squash still failed both arms inside HA (`a5:byte_unchanged`, `a8:already_configured`, A14 `_lazy`). leaves #533 open. leaves #201 open.
- [#754](https://github.com/tvofi/heatpump_optimizer/pull/754) — **merged `76977ee`**: leftover A5/A8/A14 nightly reds after #751 (`_live_option_defaults`, `a8_sensors_payload`, `_async_lazy` offloads `import_module`). Does not implement A6/A11/A12/A13. leaves #533 open. leaves #201 open.
- [#755](https://github.com/tvofi/heatpump_optimizer/pull/755) — **merged `a325ebd`**: leftover #533 **A6/A11/A12/A13**. Four corrupt stores must not raise or apply; a failing service raises; an older schema version migrates; the currency follows the EUR instance. Host pins demand the checks by name. Does not touch the nightly-ha production files #754 owns. leaves #533 open. leaves #201 open.
- [#766](https://github.com/tvofi/heatpump_optimizer/pull/766) — **row written before the merge**, and it is this pull request: leftover-row that truths the #533 cell after leftover named work landed on main. Closes #533. leaves #201 open.
- [#769](https://github.com/tvofi/heatpump_optimizer/pull/769) — **row written before the merge**, and it is this pull request: **#303, `optimizer.py` whole**: 52 errors to 4. The solver wrappers and their closures, the legionella helpers' keyword-only parameters, the bare generics on the horizon and the result assembler, and ten `Any` returns through numpy's stubs. Three closures renamed so a memo stops shadowing the objective it wraps; no value moves — 55 golden scenarios byte-identical at 6 dp. **The residual of 4 is refused by caps, not by code**: two `import-untyped` that are the pinned ruler's own third-party set, and two `index` whose narrowing takes `optimize` from `max_cc` 48, the recorded cap, to 50. Both are owner decisions, named in the body. leaves #303 open. leaves #201 open.
- [#770](https://github.com/tvofi/heatpump_optimizer/pull/770) — **row written before the merge**, and it is this pull request: **W5-G4, `coordinator.py` whole**: 83 errors to zero, and #303's census ends at 4. The annotations were **paid for, not raised** — `coordinator_loc` and `max_class_loc` end at 9599 against a cap of 9604, re-recorded, after the first pass cost 36 lines and one `functions_cc_over_15` row. One bug this branch wrote is in its own mutation proof: a scripted edit left the two-zone heat-loss branch without a `return`, and `tests/features.py` names it. W5-G3 and W5-G4 both flip to `done`. **#303 stays open on the residual of 4** with the two owner decisions that would close it. leaves #195 open. leaves #201 open.
- [#771](https://github.com/tvofi/heatpump_optimizer/pull/771) — **row written before the merge**, and it is this pull request: **W5-G4, `coordinator.py` whole**: 83 errors to zero, and #303's census ends at 4. The annotations were **paid for, not raised** — `coordinator_loc` and `max_class_loc` end at 9599 against a cap of 9604, re-recorded, after the first pass cost 36 lines and one `functions_cc_over_15` row. One bug this branch wrote is in its own mutation proof: a scripted edit left the two-zone heat-loss branch without a `return`, and `tests/features.py` names it. W5-G3 and W5-G4 both flip to `done`. **#303 stays open on the residual of 4** with the two owner decisions that would close it. leaves #195 open. leaves #201 open.
- [#772](https://github.com/tvofi/heatpump_optimizer/pull/772) — **row written before the merge**, and it is this pull request: the record for W5-G10's merge, and #195's map. W5-G10's `resume` flips to `done` (#771, `ec263d8`), which closes every Wave 5 group except the two #195 ones. The Wave 5 table row now records #303 **closed** with its census at 0 and both seam moves merged; the `last` row records #412 **closed**, so lane F waits on Wave 5 alone. W5-G7's and W5-G8's briefs carry the coverage map measured on 2026-09-11 with this group's own instrument — 91.8 % overall, 1,237 missed over 55 modules, `coordinator.py` holding 642 at 83.4 % and 24 other modules holding 407 — each with a re-measure instruction, because W5-G10 moved a module out of that file after the measurement. leaves #195 open. leaves #558 open. leaves #201 open.
- [#788](https://github.com/tvofi/heatpump_optimizer/pull/788) — **row written before the merge**, and it is this pull request: **W5-G7 tranche 1 of 4** (#195). Twenty-four checks over six methods of the coordinator's core seam — the ECL110 state handler's four payload shapes and its malformed arm, the live PV production reading, the away override, the accuracy store's two refusal paths, and the setpoint override that is the comfort learner's only evidence. `coordinator.py` 83.3 % → 85.4 %, 75 statements newly covered and 0 newly missed. Eighteen mutations, sixteen failing a check by name; the two that cannot are production findings recorded in the body — a redundant non-value guard in the PV reader and a redundant parse in `async_set_away`. Test-only. leaves #195 open. leaves #201 open.
- [#812](https://github.com/tvofi/heatpump_optimizer/pull/812) — **row written before the merge**, and it is this pull request: **W5-G7 tranche 2 of 4** (#195). Sixty checks over the five learners of the coordinator's learning seam — the buffer-cooling learner's nine rejecting arms and its alpha asymmetry, one check per `except` arm of the thermal-learning store loader against a well-formed payload as the null control, the price-shape learner's two seen-sets, the quiet-comfort recorder including 300 flat against 300 swinging periods for the flatness guard, and the two replay learners' rejecting arms. Test-only, plus this row, the roster and the handover. **Two production findings reported rather than tested into false coverage**: four unreachable lines in `_async_learn_price_shape`, whose keys cannot fail `fromisoformat`, and a warming guard in `_async_learn_buffer_cooling` that rejects nothing the volume-derived floor does not already reject. **A measurement discipline it corrected in itself**, carried into tranches 3 and 4: the mutation table ran three rounds, and every one of its nineteen first-round passes was answered rather than reported as a ratio — six inputs an earlier guard had already rejected, seven guards whose removal escaped as an exception and ended the script instead of failing the check named for it, three store arms writing the value their attribute already held, and seven guards that are genuinely subsumed and are reported as findings. W5-G4's roster `resume` is truthed from `in-review` to `done` in the same commit — #770 merged as `4da4cce` and the field had said `in-review` since. leaves #195 open. leaves #201 open.
- [#842](https://github.com/tvofi/heatpump_optimizer/pull/842) — **row written before the merge**, and it is this pull request: **W5-G7 tranche 3 of 4** (#195). Sixty-one checks over the nineteen methods holding the coordinator's fetch and grid seams — the solar coordinate's seven arms and the client's lifetime, the forecast view's window and interval-start anchor, the price-model and ledger stores, the live export-price entity, both #13 tariff masks, the realised-peak source order, the power listener's five refusals, the peak-guard transition with no plan, the outage detector's zone adoption, the headroom horizon and the price-tile rotation. `coordinator.py` 88.1 % → 90.9 %, 106 statements newly covered and 0 newly missed; the nineteen targets 112 → 6 while the rest of the file holds 328 at both ends. Sixty-four mutations over sixty-three arms in three rounds, 56 failing a check by name; the four that pass are subsumed guards reported as findings, and three more are refused by an earlier check that dies rather than failing. Test-only, plus this row and the roster. **It also corrects the plan**: four tranches do not reach the 95 % bar, because 334 missed against 184 allowed needs 150 more statements and the core seam alone holds 250. leaves #195 open. leaves #201 open.
- [#858](https://github.com/tvofi/heatpump_optimizer/pull/858) — **row written before the merge**, and it is this pull request: **W5-G7 tranche 4 of 5** (#195). Thirty-one checks over twelve methods of the core seam and the learning tail — the entity-state helper every configured-entity reader goes through, pinned by identity rather than equality because handing back the live mapping lets one reader's edit reach every other; the system-identification adopter's confidence-weighted blend and its two-zone base; the three service entry points; the defrost listener's three states; the compressor-frequency reader's refusal to fall back to an echoing setpoint; the learning tail's per-entry corruption barriers; and the options write-through's type coercions. `coordinator.py` 91.0 % → 92.7 %, 63 statements newly covered and 0 newly missed, **the twelve targets 63 → 0 with an empty residual** while the rest of the file holds 271 at both ends. Thirty-seven mutations, 31 failing a check by name; the six that pass are subsumed guards reported as findings, taking the running total across three tranches to twenty-two. Test-only, plus this row and the roster. leaves #195 open. leaves #201 open.
- [#867](https://github.com/tvofi/heatpump_optimizer/pull/867) — **row written before the merge**, and it is this pull request: **W5-G7 tranche 5** (#195). Thirty checks over the five large lifecycle methods the four earlier tranches left last, because each needs a whole update cycle *driven* rather than a method called — the pump driver's transition-only commanding and its refusal to remember a failed command, the update cycle's three wrapped accessory sub-steps and its `UpdateFailed` translation, the state reader's valve target and dropped-not-held wood tank, the what-if's rate-limit cache and deep copy, and both comfort-floor widenings. `coordinator.py` 92.7 % → 94.1 %, 52 newly covered and 0 newly missed; the five targets 70 → 18 while the rest of the file holds 201 at both ends. Twenty-eight mutations, 23 failing a check by name; three passes are subsumed guards, taking the running total to twenty-five. **Its table added a fifth rule**: assert a mutant leaves parseable code, because one that cannot run reports as a pass and a pass reads as a finding about production. Test-only, plus this row and the roster. leaves #195 open. leaves #201 open.
- [#873](https://github.com/tvofi/heatpump_optimizer/pull/873) — **W5-G7 record and the cursor split**, **row written before the merge**, and it is this pull request. Not a tranche: it truths W5-G7 after [#867](https://github.com/tvofi/heatpump_optimizer/pull/867) merged and writes tranche 6's brief, measured at `c31beb5` rather than carried. **The owner split the work on 2026-09-11: #195 stays with the `start-prompt-review-c8f8c2` seat, everything else goes to the cursor lane.** So the brief now says who owns what — tranche 6 and W5-G8 are this seat's; the twenty-five subsumed guards, the five unreachable and six deferred statements, the `docs/HANDOVER.md` debt and #558's lane F are the cursor lane's. It also states the five rules the mutation tables cost one round each, because a fresh seat would otherwise pay for them again. leaves #195 open. leaves #201 open. leaves #558 open.
- [#757](https://github.com/tvofi/heatpump_optimizer/pull/757) — **row written before the merge, and it is this pull request**: `3L-G6`'s roster `resume` note said *"#457 stays open"*; the owner closed #457 `completed` on **2026-09-06T03:40:23Z**, so the note was false for five days across three concurrent sessions. Two lines, edited textually rather than through a JSON round-trip, because re-serialising rewrites 59 lines of a file other sessions are reading. **The group does not reopen**: its brief said 3L-G7 sits after 3L-G5 if the conflict-flow spec was missing, and the spec never arrived — the issue was closed rather than specified. **`stage` is unchanged at `blocked` and the whole change is the note.** An earlier revision of this branch flipped it to `done` with a qualifying note; `done` in this roster **means merged** — `web-fix-wave.js` dereferences `resume.merged_pr` and `merge_sha` bare for it, `check-wave-script.mjs` derives its assertion from that source, and the flip turned `wave-script`, a required context, red. It also silently stopped `brief_lint` linting this group at all, because `STAGE_SKIP` is `done`. So the stage round-tripped `blocked → done → blocked` and the three-dot diff carries **no `"stage"` line**: one changed line in the roster, and it is the note. `blocked` here means spends no agent, recorded for the orchestrator — which is what a cancelled group is. **The finding, and it is why this went unnoticed**: no check reads a roster `resume` note against issue state — `brief_lint` and `policy_lint` are green before and after — which is #752's shape one artifact over. leaves #201 open.
- [#759](https://github.com/tvofi/heatpump_optimizer/pull/759) — **merged `1fd2487`, and its row is written here because nobody wrote one before it**: `.claude/workflows/gh_comment.py`, a comment poster that composes no field flag and **exits non-zero unless the posted comment reads back byte-identical**, and `.claude/rules/comment-readback.md`, the `paths:`-scoped rule that requires the read-back without naming the flag. Landed with the owner's approval for the policy half and for the `fixer.md` cap raise it carried. The defect it closes: a flag that posts the **literal path** instead of the file and exits `0`, which three reviewers reproduced in one day after being warned against it in their own prompts — which is also the evidence for the ruling that a prompt-stated warning closes a defect only when compliance produces an artifact another seat reads. leaves #201 open.
- [#761](https://github.com/tvofi/heatpump_optimizer/pull/761) — **merged `691f109`, row written after the merge**: nightly-ha A5 unstored computed defaults and A14 cached `__getattr__`, the container lane's leftovers after #755. Not this lane's work; recorded here because the Delivery-status table covers every merge, not every lane. leaves #533 open.
- [#764](https://github.com/tvofi/heatpump_optimizer/pull/764) — **merged `dc03619`, row written after the merge**: nightly-ha A5 keeps the stored type when a select retypes `'60'` to `60`. Same lane as the row above. **The scheduled `Tests` run failed on 2026-09-09 and 2026-09-10 on both `nightly-ha` matrix arms with `ModuleNotFoundError: No module named 'voluptuous'`** — the host half of the driver dying before Docker was reached — and the install step that answers it is on `main` but has not yet been exercised by a cron, so `nightly-status` stays red on every branch until one concludes green. leaves #533 open.
- [#762](https://github.com/tvofi/heatpump_optimizer/pull/762) — **row written before the merge, and it is this pull request**, `Closes #752`: `checkRecord` tested `#<pr>` against the whole region, so a sentence inside another pull request's row discharged the obligation — including one saying it is NOT dispositioning that number. A line anchoring a pull request now speaks for that pull request alone; table cells, rows anchored to an ISSUE number and the handover's prose bullets are untouched and each is pinned. The plainer predicates were measured over every first-parent head in a range before being rejected — `tools/audit/record-predicate/sweep.mjs` is that measurement and stays in the tree, with its own `--self-test` and an `API_REFUSALS=` line beside every figure. **#741's own row is not written here**: [#745](https://github.com/tvofi/heatpump_optimizer/pull/745) has owned it since #748's row said so, and this pull request does not take another lane's row — it merges after #745, which is the sequencing this change creates and the body measures. **The cost, stated:** a merge dispositioned ONLY from inside another row is now refused, and the remedy is the row the rule asks for anyway. leaves #201 open.
- [#785](https://github.com/tvofi/heatpump_optimizer/pull/785) — **merged `c4eefd3`, row written after the merge**: refuse a sysid fit whose shrunk drift landed in UA. Closed #778. `node .claude/workflows/policy_lint.mjs --record --since v6.3.20` at `origin/main` `4409e49` named this pull request among the three without a disposition. leaves #201 open.
- [#786](https://github.com/tvofi/heatpump_optimizer/pull/786) — **merged `a31bce4`, row written after the merge**: last_* prefix pin; unread last_dhw_refused dropped. Closed #780. Same `--record` run at `4409e49` named it. Not this leftover-row's implementation. leaves #201 open.
- [#787](https://github.com/tvofi/heatpump_optimizer/pull/787) — **merged `4409e49`, row written after the merge**: Carnot flow correction no longer inverts COP as outdoor rises. Closed #776. Same `--record` run at `4409e49` named it. Not this leftover-row's implementation. #745's #759/#761/#764 stay #745's. The Wave-5 table `[render]` at plan line 82 stays #768's. leaves #201 open.
- [#789](https://github.com/tvofi/heatpump_optimizer/pull/789) — **row written before the merge, and it is this pull request**: leftover-row for #785 `c4eefd3`, #786 `a31bce4`, #787 `4409e49`. `node .claude/workflows/policy_lint.mjs --record --since v6.3.20` at `origin/main` `4409e49` named those three. #745's #759/#761/#764 stay #745's. Wave-5 table `[render]` at plan line 82 stays #768's. leaves #201 open.
- [#790](https://github.com/tvofi/heatpump_optimizer/pull/790) — **row written before the merge**, and it is this pull request: the Wave 5 row above carried a duplicated trailing cell, so `main` rendered it with more cells than its header and `record` reported it. Not this lane's row; split out of [#768](https://github.com/tvofi/heatpump_optimizer/pull/768) so a one-line repair to a red required check does not wait behind a policy change. The removal is the duplicated cell and nothing else — the row's content is unchanged. leaves #201 open.
- [#792](https://github.com/tvofi/heatpump_optimizer/pull/792) — **merged `a1bdb11`, row written after the merge**: a stamp ahead of the host clock is stale, not age 0. Closed #775. `InputReader._age_minutes` no longer clamps a future stamp to 0.0; `_age_gate` treats that unknowable age as stale when a comparable stamp exists. Untimestamped stubs stay usable. `FakeState` no longer invents `datetime.now()`. `node .claude/workflows/policy_lint.mjs --record --since v6.3.20` at `origin/main` `a1bdb11` named this pull request. leaves #773 open. leaves #774 open. leaves #201 open.
- [#794](https://github.com/tvofi/heatpump_optimizer/pull/794) — **row written before the merge, and it is this pull request**: leftover-row for #792 `a1bdb11`. `node .claude/workflows/policy_lint.mjs --record --since v6.3.20` at `origin/main` `a1bdb11` named #792. leaves #201 open.
- [#793](https://github.com/tvofi/heatpump_optimizer/pull/793) — **row written before the merge**, and it is this pull request: `fixer.md` step 6's re-execution range widened to cover the pull-request body, so a figure that is a function of `origin/main`'s tip is re-taken after a rebase and not only the harness; and a section saying that past three review rounds the body is replaced rather than repaired. `fix-review.md` carries the reviewer's half and `CLAUDE.md`'s index tracks the range. **Policy: needs the owner's approval under decision 0007**, given before the branch was pushed together with the file-cap raises it needs; `tools/audit/briefs/fixer.md` is capped at 285. **The corpus cap is unchanged**: the added lines are paid for by compressing step 6's closing paragraphs. This is #768's tree on a fresh branch; #768 was closed rather than repaired, and why is in its own closing comment and in the pull-request body here. leaves #201 open.
- [#804](https://github.com/tvofi/heatpump_optimizer/pull/804) — **merged `ef0788f`, row written after the merge**: wood night advisor derives SOC from the tank probes. Closed #795. `_attach_night_advice` no longer reads unwritten `wood_tank_soc` or falls back to `0.5`; SOC is the probe span. No live temperature attaches no advice. `node .claude/workflows/policy_lint.mjs --record --since v6.3.20` at `origin/main` `ef0788f` named this pull request. leaves #796 open. leaves #201 open.
- [#811](https://github.com/tvofi/heatpump_optimizer/pull/811) — **row written before the merge, and it is this pull request**: leftover-row for #804 `ef0788f`. `node .claude/workflows/policy_lint.mjs --record --since v6.3.20` at `origin/main` `ef0788f` named #804. leaves #201 open.
- [#803](https://github.com/tvofi/heatpump_optimizer/pull/803) — **row written before the merge**, and it is this pull request: `delivery-status-tracking.md` concluded that a pull request carrying a merge cannot write its own row, reasoning from `fixer.md`'s handoff freeze; rows like this one are written before that freeze, not after, so the premise held and the inference did not. **Policy: needs the owner's approval under decision 0007**, which was given for this repair after a root-cause seat recorded the contradiction as one a seat cannot resolve. Surfaced on #201, not filed as an issue. The generated `.cursor` rule is regenerated by `rules_sync.mjs`. The replaced sentence is shorter than the one it replaces, and the saving is banked rather than left: `corpus_tokens` and the `record` role's cap are lowered by what this deletion freed, which `ratchet-budgets.md` makes free for a deletion. The pre-existing headroom that stood on `main` is **not** absorbed — the rationale earns only what the deletion freed. Figures and both refusal arms are in the pull-request body. leaves #201 open.
- [#791](https://github.com/tvofi/heatpump_optimizer/pull/791) — **merged `c7e2f81`, row written after the merge**: capacity-tariff billing mask walks UTC, not the wall clock. Closed #777. `node .claude/workflows/policy_lint.mjs --record --since v6.3.20` at `origin/main` `2684125` named this pull request. The squash subject ends `(#777)`, so a tokenless run names the issue instead. Not this leftover-row's implementation. #745's #759/#761/#764 stay #745's. leaves #201 open.
- [#813](https://github.com/tvofi/heatpump_optimizer/pull/813) — **merged `e2dd1a6`, row written after the merge**: JSON-string nan in thermal_learning no longer wedges every cycle. Closed #773. Load `isfinite` plus tolerant `int()` in `_learning_view`. Same `--record` run at `2684125` named this pull request. leaves #201 open.
- [#815](https://github.com/tvofi/heatpump_optimizer/pull/815) — **row written before the merge, and it is this pull request**: leftover-row for #813 `e2dd1a6`, #791 `c7e2f81`. `node .claude/workflows/policy_lint.mjs --record --since v6.3.20` at `origin/main` `2684125` named those two. #745's #759/#761/#764 stay #745's. leaves #201 open.
- [#814](https://github.com/tvofi/heatpump_optimizer/pull/814) — **merged `0bff000`, row written after the merge**: #525 reap waits for a readiness byte, not a wall-clock floor. Closed #810. `node .claude/workflows/policy_lint.mjs --record --since v6.3.20` at `origin/main` `c06250e` named this pull request. leaves #201 open.
- [#816](https://github.com/tvofi/heatpump_optimizer/pull/816) — **merged `c06250e`, row written after the merge**: a NaN hour is refused by `PriceShapeModel.observe_day`. Closed #807. Same `--record` run at `c06250e` named this pull request. leaves #201 open.
- [#820](https://github.com/tvofi/heatpump_optimizer/pull/820) — **row written before the merge, and it is this pull request**: leftover-row for #814 `0bff000`, #816 `c06250e`. `node .claude/workflows/policy_lint.mjs --record --since v6.3.20` at `origin/main` `c06250e` named those two. #745's #759/#761/#764 stay #745's. leaves #201 open.
- [#831](https://github.com/tvofi/heatpump_optimizer/pull/831) — **merged `cfed184`, row written after the merge**: coordinator goldens instantiate the sensor platform and record each sensor's `native_value` and `extra_state_attributes`. Closed #806. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `cfed184` named this pull request. leaves #201 open.
- [#838](https://github.com/tvofi/heatpump_optimizer/pull/838) — **row written before the merge, and it is this pull request**: leftover-row for #831 `cfed184`. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `cfed184` named #831. #745's #759/#761/#764 stay #745's. leaves #201 open.
- [#832](https://github.com/tvofi/heatpump_optimizer/pull/832) — **merged `be3a723`, row written after the merge**: sysid step sized on the two-state plant. Closed #779. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `be3a723` named this pull request. leaves #201 open.
- [#819](https://github.com/tvofi/heatpump_optimizer/pull/819) — **merged `5d60fc6`, row written after the merge**: `SECURITY.md` points at the enabled private advisory channel. Closed #801. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `98c57cf` named this pull request. leaves #201 open.
- [#821](https://github.com/tvofi/heatpump_optimizer/pull/821) — **merged `98c57cf`, row written after the merge**: `tests/solar_alignment.py` pins the no-pyranometer Open-Meteo current-irradiance fallback. Closed #808. Same `--record` run at `98c57cf` named this pull request. leaves #201 open.
- [#839](https://github.com/tvofi/heatpump_optimizer/pull/839) — **row written before the merge, and it is this pull request**: leftover-row for #832 `be3a723`, #819 `5d60fc6`, #821 `98c57cf`. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `98c57cf` named #819 and #821; the #832 line was already on this branch. #745's #759/#761/#764 stay #745's. leaves #201 open.
- [#825](https://github.com/tvofi/heatpump_optimizer/pull/825) — **merged `0420662`, row written after the merge**: the round-3 finder harnesses land under `tools/audit/round3/<D>/`, 63 instruments across all twelve dimensions, so a reviewer can run the finder's instrument per `fix-review.md` steps 2 and 9. Additive: four already-tracked round-3 files were skipped, `D1/store_fuzz.py` among them because `main`'s copy is the narrowed reproducer from #773 and the archive copy is the finder's original. `tools/audit/` is already INERT so the gate stayed `MODE: SCOPED`. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `f625e54` named this pull request. leaves #201 open.
- [#833](https://github.com/tvofi/heatpump_optimizer/pull/833) — **merged `f625e54`, row written after the merge**: four round-3 D5/D6 findings fixed rather than filed — the entity census in `docs/configuration.md` and `docs/architecture.md` (65 → 74, derived by perturbing README's pinned total and reading `tests/entities.py`'s own failure message), the `simulate_plan`/`assign_entity`/`apply_topology` field lists (11/3/3 → 16/4/5), a dead README anchor, and both halves of one supersession. The evidence register and backlog still say 65 deliberately: they record what was measured when written. Same `--record` run at `f625e54` named this pull request. leaves #201 open.
- [#841](https://github.com/tvofi/heatpump_optimizer/pull/841) — **row written before the merge, and it is this pull request**: leftover-row for #825 `0420662`, #833 `f625e54`. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `f625e54` named those two. #745's #759/#761/#764 stay #745's. leaves #201 open.
- [#840](https://github.com/tvofi/heatpump_optimizer/pull/840) — **merged `1cc2193`, row written after the merge**: persist the fuse advisor weekly guard across restart. Closed #782. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `1cc2193` named this pull request. leaves #201 open.
- [#845](https://github.com/tvofi/heatpump_optimizer/pull/845) — **merged `ba4687a`, row written after the merge**: three quality-scale rules the tree already satisfies, and the typing pointer retargeted to #829. Closed #827. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `45de8f4` named this pull request. leaves #201 open.
- [#846](https://github.com/tvofi/heatpump_optimizer/pull/846) — **merged `45de8f4`, row written after the merge**: wood-fuel economics in configuration.md and the real wood_cheaper gates in the README. Closed #835. Same `--record` run at `45de8f4` named this pull request. leaves #201 open.
- [#847](https://github.com/tvofi/heatpump_optimizer/pull/847) — **merged `0018579`, row written after the merge**: the options dialog's 21 pages named by their real labels; away options are the four fields; circulation pump on building. Closed #834. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `0018579` named this pull request. leaves #201 open.
- [#848](https://github.com/tvofi/heatpump_optimizer/pull/848) — **row written before the merge, and it is this pull request**: leftover-row for #840 `1cc2193`, #845 `ba4687a`, #846 `45de8f4`, #847 `0018579`. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `0018579` named #847; the earlier three were already on this branch. #843 is theirs (audit #822/#823). #745's #759/#761/#764 stay #745's. leaves #201 open.
- [#818](https://github.com/tvofi/heatpump_optimizer/pull/818) — **row written before the merge**, and it is this pull request: **closes #800 (R3-D11-03)**. The `## Approval` section was required only when the pull request's title began with `policy:` — a string the constrained seat writes — so a one-word title change switched the owner-approval gate off. It is keyed on the **diff** now: required when the change touches a `POLICY_GLOBS` path, with the title arm kept as a second trigger, and refusing rather than passing when the path list cannot be derived. **Policy: needs the owner's approval under decision 0007**, because it changes when a seat must obtain approval. **Not taken and surfaced instead**: `POLICY_GLOBS` excludes the enforcement programs themselves, so a change to them still does not demand approval; widening it is the owner's call. leaves #201 open.
- [#843](https://github.com/tvofi/heatpump_optimizer/pull/843) — **merged `9892160`, row written after the merge**: the card's no-data legend chips clear WCAG AA and the away strip joins the card's own 24px coarse-pointer floor. Closed #822 and #823. `.chip.nodata` lost `opacity: 0.3` (1.90:1 light / 2.36:1 dark → 16.10 / 13.03) and its lying `cursor: not-allowed`; `.away-strip` gained base rules and its controls joined `coarseHtmlTargets` (13px → 24px, visual gap 0 → 12px). 33 of 34 `card_drift` states claimed — `card_drift` refused an earlier list claiming all 34, because `editor_schema` renders no card stylesheet. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `b8731c3` named this pull request. leaves #201 open.
- [#849](https://github.com/tvofi/heatpump_optimizer/pull/849) — **merged `45da946`, row written after the merge**: the initial config flow groups `user_sensors`' fourteen pickers into indoor/solar/plant, the registry's own names. Closed #824. Nothing collapsed, because a collapsed section on a setup screen is a field the user never sees. Grouping is applied on a FRESH setup only: `add_suggested_values_to_schema` fills by top-level key, so a sectioned schema returned every sensor as `None` on reconfigure and would have silently dropped a user's pickers — the panel called that precondition theoretical and it was not. `tests/golden/config_flow.json` re-recorded and claimed, per #653. Same `--record` run at `b8731c3` named this pull request. leaves #201 open.
- [#850](https://github.com/tvofi/heatpump_optimizer/pull/850) — **merged `64e39e0`, row written after the merge**: `tests/README.md` records that line deletion is the wrong mutation operator for the end-to-end solver scripts — 0 of 8 killed on `validate.py` and `optimality.py`, against 2 of 2 on arithmetic mutants. Closed #809. The finding's cost half was cut to the issue rather than the tree: the policy corpus had 84 tokens of headroom and both halves measured 457 over, and raising a cap needs the owner's confirmation before the push. Same `--record` run at `b8731c3` named this pull request. leaves #201 open.
- [#851](https://github.com/tvofi/heatpump_optimizer/pull/851) — **merged `7f385f2`, row written after the merge, and not by its author**: the ledger-rider check was a second declaration of the payload, and `main` went red. This repaired a suite failure standing at `3654cb3`, `64e39e0` and `c06a92f`, which reached every open pull request as a red `fast` leg on a money-state check their diffs could not touch. Same `--record` run at `b8731c3` named this pull request. leaves #201 open.
- [#852](https://github.com/tvofi/heatpump_optimizer/pull/852) — **merged `b8731c3`, row written after the merge, and not by its author**: the away tick lives on Plan and expands the return time. Same `--record` run at `b8731c3` named this pull request. leaves #201 open.
- [#857](https://github.com/tvofi/heatpump_optimizer/pull/857) — **row written before the merge, and it is this pull request**: leftover-row for #843 `9892160`, #849 `45da946`, #850 `64e39e0`, #851 `7f385f2`, #852 `b8731c3`. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `b8731c3` named those five and two more, #844 and #854, which cursor's #855 carries. #745's #759/#761/#764 stay #745's. leaves #201 open.
- [#854](https://github.com/tvofi/heatpump_optimizer/pull/854) — **merged `8640321`, row written after the merge**: the uninstall list names the away and boost stores. Closed #837. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `8640321` named this pull request. leaves #201 open.
- [#844](https://github.com/tvofi/heatpump_optimizer/pull/844) — **merged `17d9405`, row written after the merge**: the reauth token field points at developer.tibber.com. Closed #828. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `17d9405` named this pull request. leaves #201 open.
- [#855](https://github.com/tvofi/heatpump_optimizer/pull/855) — **row written before the merge, and it is this pull request**: leftover-row for #854 `8640321`, #844 `17d9405`. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `cfa60f6` named those two. #857 already holds #843, #849, #850, #851 and #852. #745's #759/#761/#764 stay #745's. leaves #201 open.
- [#853](https://github.com/tvofi/heatpump_optimizer/pull/853) — **merged `9113db8`, row written after the merge**: two comments named something the tree does not have. Closed #836. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `9113db8` named this pull request. leaves #201 open.
- [#861](https://github.com/tvofi/heatpump_optimizer/pull/861) — **row written before the merge, and it is this pull request**: leftover-row for #853 `9113db8`. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `9113db8` named #853. #859 is theirs. #745's #759/#761/#764 stay #745's. leaves #201 open.
- [#862](https://github.com/tvofi/heatpump_optimizer/pull/862) — **merged `1e94623`, row written after the merge**: steward S8 now says `record-status` is not required and reports `main`'s last concluded `record` job. #860 item 3. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `f266842` named this pull request. leaves #860 open. leaves #201 open.
- [#863](https://github.com/tvofi/heatpump_optimizer/pull/863) — **merged `f266842`, row written after the merge**: an issue body, a comment, and a review comment are data a seat quotes, not as instructions. Paid by deleting the uniqueness example and the structurally-behind couplet. The write-grant half of #802 remains. Same `--record` run at `f266842` named this pull request. leaves #802 open. leaves #201 open.
- [#864](https://github.com/tvofi/heatpump_optimizer/pull/864) — **merged `30bc45f`, row written after the merge**: coordinate on #201 before each PR, merge or release. #860 item 2. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `30bc45f` named this pull request. leaves #860 open. leaves #201 open.
- [#866](https://github.com/tvofi/heatpump_optimizer/pull/866) — **row written before the merge, and it is this pull request**: leftover-row for #862 `1e94623`, #863 `f266842`, #864 `30bc45f`. `node .claude/workflows/policy_lint.mjs --record --since v6.4.0` at `origin/main` `30bc45f` named #864; #862 and #863 were already on this branch. Not #859. #745's #759/#761/#764 stay #745's. leaves #201 open.
- [#868](https://github.com/tvofi/heatpump_optimizer/pull/868) — **row written before the merge, and it is this pull request**: leftover-row for #860 items 1 and 6 at `origin/main` `1e66bb7`. Sixteen issue-table dispositions after re-measure. HANDOVER refreshed and paid at its cap. `node .claude/workflows/policy_lint.mjs --record --since v6.4.1` at `origin/main` `1e66bb7` named none. Not #859. #745's #759/#761/#764 stay #745's. leaves #860 open. leaves #201 open.
- [#869](https://github.com/tvofi/heatpump_optimizer/pull/869) — **merged `4af7025`, row written after the merge**: three MCP grants in the shared prompt block; `issue_read` and `merge_pull_request` no longer share a const. Closed #802. `node .claude/workflows/policy_lint.mjs --record --since v6.4.1` at `origin/main` `e708f1b` named this pull request and #870. Not #859. leaves #201 open.
- [#870](https://github.com/tvofi/heatpump_optimizer/pull/870) — **merged `e708f1b`, row written after the merge**: owner-granted HANDOVER cap raise; the pin is in `.claude/workflows/policy_budgets.json`. Theirs. Same `--record` run at `e708f1b` named this pull request. Not #859. leaves #201 open.
- [#874](https://github.com/tvofi/heatpump_optimizer/pull/874) — **merged `f9f54cf`, row written before the merge**: leftover-row for #869 `4af7025` and #870 `e708f1b`. `node .claude/workflows/policy_lint.mjs --record --since v6.4.1` at `origin/main` `7e84856` named those two. Not #859. Not #867. leaves #860 open. leaves #201 open.
- [#872](https://github.com/tvofi/heatpump_optimizer/pull/872) — **merged `a95556d`, row written after the merge**: Title Case on the six English entity display names. Closed #797. Theirs. `node .claude/workflows/policy_lint.mjs --record --since v6.4.1` at `origin/main` `e59ac74` named this pull request and #876. Not #859. Not #867. leaves #201 open.
- [#876](https://github.com/tvofi/heatpump_optimizer/pull/876) — **merged `e59ac74`, row written after the merge**: quality-scale `strict-typing` is `done`. Closed #829. `py.typed` was not added. Typing budgets were not raised. Same `--record` run at `e59ac74` named this pull request. Not #859. Not #867. leaves #201 open.
- [#879](https://github.com/tvofi/heatpump_optimizer/pull/879) — **row written before the merge, and it is this pull request**: leftover-row for #872 `a95556d`, #876 `e59ac74`. `node .claude/workflows/policy_lint.mjs --record --since v6.4.1` at `origin/main` `e59ac74` named those two. Not #859. Not #867. leaves #860 open. leaves #201 open.
- [#878](https://github.com/tvofi/heatpump_optimizer/pull/878) — **merged `06c53f7`, row written after the merge**: wood-burn advisor is Unavailable or none, not Unknown. Closed #796. `node .claude/workflows/policy_lint.mjs --record --since v6.4.1` at `origin/main` `06c53f7` named this pull request. Not #859. Not #867. leaves #201 open.
- [#880](https://github.com/tvofi/heatpump_optimizer/pull/880) — **merged `f46028b`, row written after the merge**: expire a reload handover older than one update interval. Leaves #774 open — the residual is the coordinator republish of a still-fresh handover. `node .claude/workflows/policy_lint.mjs --record --since v6.4.1` at `origin/main` `f46028b` named this pull request. Not #859. Not #867. leaves #774 open. leaves #201 open.
- [#875](https://github.com/tvofi/heatpump_optimizer/pull/875) — **merged `5cddbc9`, row written after the merge**: restart L-BFGS-B once from its own returned point. Closed #826. Seeding arm not built. `node .claude/workflows/policy_lint.mjs --record --since v6.4.1` at `origin/main` `5cddbc9` named this pull request and #877. Not #859. Not #867. leaves #201 open.
- [#877](https://github.com/tvofi/heatpump_optimizer/pull/877) — **merged `a70e8e9`, row written after the merge**: pin four non-coordinator surviving guards. Leaves #805 open — two optimizer residuals and the coordinator residual remain. Same `--record` run at `origin/main` `5cddbc9` named this pull request. Not #859. Not #867. leaves #805 open. leaves #201 open.
- [#881](https://github.com/tvofi/heatpump_optimizer/pull/881) — **row written before the merge, and it is this pull request**: leftover-row for #878 `06c53f7`, #880 `f46028b`, #875 `5cddbc9` and #877 `a70e8e9`. `node .claude/workflows/policy_lint.mjs --record --since v6.4.1` at `origin/main` `5cddbc9` named #875 and #877; #878 and #880 were already on this branch. Not #859. Not #867. leaves #860 open. leaves #774 open. leaves #805 open. leaves #201 open.
- [#884](https://github.com/tvofi/heatpump_optimizer/pull/884) — **row written before the merge, and it is this pull request**: dropped `record` from main-protect 22628467 required contexts. Closed #799. No pre-merge `--record` arm. #798 stays blocked. `node .claude/workflows/policy_lint.mjs --record --since v6.4.1` at `origin/main` `cf7ac15` named none. Not #859. Not #867. leaves #798 open. leaves #860 open. leaves #201 open.
- [#871](https://github.com/tvofi/heatpump_optimizer/pull/871) — **merged `020e699`, row written after the merge**: `config_entry` on the coordinator constructor. Closed #830. `node .claude/workflows/policy_lint.mjs --record --since v6.4.1` at `origin/main` `67a61fb` named this pull request. leaves #201 open.
- [#886](https://github.com/tvofi/heatpump_optimizer/pull/886) — **merged `7d142c0`, row written after the merge**: recompute handover age on republish. Closed #774. Same `--record` run named this pull request. leaves #201 open.
- [#887](https://github.com/tvofi/heatpump_optimizer/pull/887) — **merged `14a3833`, row written after the merge**: do not fold the frequency map during reverse-cycle cooling or a stale power pin. Closed #781. Same `--record` run named this pull request. leaves #201 open.
- [#888](https://github.com/tvofi/heatpump_optimizer/pull/888) — **merged `546b492`, row written after the merge**: cap consecutive in-process solve fallbacks. Closed #783. `--record` enumerates by a trailing `(#N)` on the squash subject; this subject's has none, so that run is blind to it. leaves #201 open.
- [#890](https://github.com/tvofi/heatpump_optimizer/pull/890) — **merged `1b35c6c`, row written after the merge**: pin house-heat-loss persist on the tenth sample. Closed #805. Same trailing-`(#N)` gap as #888. leaves #201 open.
- [#891](https://github.com/tvofi/heatpump_optimizer/pull/891) — **merged `67a61fb`, row written after the merge**: device configuration-URL field and repair-notice documentation links. Closed #558. Same `--record` run named this pull request. leaves #201 open.
- [#883](https://github.com/tvofi/heatpump_optimizer/pull/883) — **merged `4a42eab`, row written after the merge, and not by this leftover-row**: pin two optimizer surviving guards. Theirs. Same `--record` run named this pull request. #805's coordinator residual is #890. leaves #201 open.
- [#892](https://github.com/tvofi/heatpump_optimizer/pull/892) — **row written before the merge, and it is this pull request**: leftover-row for #871 `020e699`, #886 `7d142c0`, #887 `14a3833`, #888 `546b492`, #890 `1b35c6c`, #891 `67a61fb`, and #883 `4a42eab` (theirs). `node .claude/workflows/policy_lint.mjs --record --since v6.4.1` at `origin/main` `67a61fb` named #891 #887 #886 #871 #883; #888 and #890 are suffix-blind. F1/F2 resume is `done`. Not #889. Not #885. Not #882. leaves #195 open. leaves #860 open. leaves #817 open. leaves #798 open. leaves #201 open.

### The UX programme — 34 items, five lanes, tracking #558

Thirty-four graphics and interface changes the owner selected from a
forty-two item survey. **Tracking issue #558** carries every item; the
*Optimizer UX Docket* artifact is the source of record. Three items were
dropped and two reshaped so they stop being breaking changes — both recorded
there with reasons.

**The lanes run concurrently with the waves, and that is measured rather than
assumed.** `docs/` is an INERT prefix, so lane B selects zero test scripts.
`tests/structure.py` walks `*.py` only, so lane C moves no ratchet metric at
all — its only cost is a golden drift claim. Lane D is Python outside the
coordinator, so repo-wide budgets bind but `coordinator_loc` does not.

**Independence by budget is not independence by file.** The docket's original
claim was measured against the ratchet, which was true and incomplete: two
lanes share files with remaining wave stages.

| lane | items | collides with | on | sequence |
|---|---|---|---|---|
| **B** docs | 12 | — | — | **complete on `main`**: #567 (B1–B5), #576 (B6–B11), #635 (B12) |
| **C** card | 9 | — | — | **complete on `main`**: #569 (C1), #600 (C2–C3), #633 (C4) |
| **D** ha | 6 | W5-G2 | `sensor.py` | **complete on `main`**: #535 (D1), #571 (D2–D3), #599 (D4–D6). D landed before W5-G2 (#636), which re-measured against it |
| **E** flow | 4 | **W4 S11 (#223)**, W5-G3 | `config_flow.py` | **complete on `main`**: E1 #664, E2 #665, E3 #668, E4 #653 (`7e830d6`, closed #516). S11 landed as #597 (`0323c5b`) and shut #223; the capture #568 landed before E4 grouped anything |
| **F** post-W4 | 2 | S12/S13, W5-G4, W5-G7 | `coordinator.py` | **last work of the programme**, after #412 |

**Why E1–E3 waited, and no longer do.** S11 rewrote `config_flow.py` as a
settings registry, so landing the token masking, the finish-setup-now step and
the `setup_overview` move first would have had S11 restructure work that had
just landed. S11 is merged (#597, `0323c5b`), so each is now one row in the
registry rather than three separate edits — which was the point of waiting.

**Why F is last.** It is the only lane that adds lines to `coordinator.py`,
where `coordinator_loc` and `max_class_loc` sit at zero headroom — three added
lines would fail two budgets and eat the headroom the seam stages need. It
therefore follows Wave 4, Wave 5 **and** #412, which makes it the final work
of the whole programme rather than merely late.

**How HACS eats an image, measured — this binds every figure lane B ships.**
`hacs.json` sets `render_readme: true`, and HACS rewrites image sources before
`<ha-markdown>` sees them. Three constraints, each established by running HACS's
own pipeline rather than by reading its source:

1. **A relative `src` is blanked** unless HACS rewrites it to an absolute URL.
2. **The rewriter's regex has no `s` flag**, so an image whose alt text wraps
   across lines is skipped — and then blanked. This caught the lane's own hero,
   which was written wrapped and would have shipped broken in the one view B4
   exists for.
3. **The rewriter's lookahead `(?!.*?://)` scans the whole line, not the link.**
   So a relative image that *shares a line with any absolute URL* is never
   rewritten, and vanishes. The construct that matters is exactly the one a
   figure lane reaches for — a figure linked to a larger version:

   ```markdown
   [![alt](docs/img/fig.svg)](https://example.com/full.svg)
   ```

   This is the same mechanism as the `(LICENSE)` badge defect, whose target has
   no extension and which HACS therefore rewrites into a broken link. Rule 3 is
   **not covered by the pin B1 landed**: all three such constructs pass it.

Establish separately whether `docs/*.md` is subject to any of this. HACS renders
the README; `docs/` may reach the reader only through GitHub, and a constraint
applied where it does not hold costs quality for nothing.

**Three sequencing rules inside the lanes**, each of which costs a red main or
a wasted PR if ignored: **C4** (the contrast witness) runs **last** in its
lane, because extended today it fails immediately on four measured ratios;
**C1 is one pull request, not four**, since the four colour fixes claim drift
over the same state list; and **B5 needs B4 landed**, or the README opens with
nothing where the flowchart used to be.

**#516 (E4)**'s original blocker is discharged — #520 raised the Home
Assistant floor to 2025.2.0, where `section()` exists. The capture blocker
is discharged by #568: `golden.py`'s fingerprint recurses into `section()`.
The remaining cost is the assertion layer, which [#653](https://github.com/tvofi/heatpump_optimizer/pull/653) teaches to reuse
that same walker before grouping the ten wide pages.

### Wave 1b, half I delivered 2026-09-04

Twelve PRs merged in sequence, `main` green after each, ending at `841fe0f`: #383 (W1-G1, #369 #370), #385 (W1-G10, #247 #248 #249 #250 #251 #252), #396 (truth-up), #384 (W1-G4, #373), #386 (W1-G5, #334), #397 (W1-G3, #372 #357), #399 (the #387 coverage-floor backstop), #402 (W1-G11, #246 #251 #395), #407 (operational docs), #409 (the ratchet-raise policy), #410 (the claim priority), #406 (W1-G2, #350 #374). **Released**: `v6.3.12` is tagged at `84a27b6f21690edcd340c6d74ff303c8e0774180`, now `origin/main`.

Half II (`wave-1b-groups.json`, archived at `d5d8c4a`) started 2026-09-04 and completed 2026-09-05. **Released**: `v6.3.13` tagged at `f94ae13a75ed58ab53b70b5dbb13786c1c081a4c`, 2026-09-05. Eight fixer groups merged in sequence, `main` green after each; record PR #433 at `3bcea26`, inherited-card-claims fix `7044a27`, then stamp. Merge SHAs in the roster's `resume.merge_sha` fields. Record/tooling since v6.3.12: #414/#398, #415, #417, #418, #416/#411 (Wave 2 prerequisite), #420 (stress closure 64→22), #426 (W2-G2 citation re-anchor), #413 (brief corrections, W1-G16 added).

Wave 2 (`wave-2-groups.json`, archived at `d5d8c4a`) forked at `f94ae13` and completed 2026-09-05. **Released**: `v6.3.14` tagged at `ef539bec138392217bce7d51c96e4c49d0e456c2`, 2026-09-05. Seven fixer groups merged in sequence, `main` green after each; record PR #450 at `6cc3318`, then stamp. Merge SHAs in the roster's `resume.merge_sha` fields. Record/tooling since v6.3.13 stamp: #434, #435, #439, #442, #443, #446, #448, #450.

Wave 3 (`wave-3-groups.json`, archived at `d5d8c4a`) forked at `ef539be` and completed 2026-09-06. **Released**: `v6.3.15` tagged at `f0866c8e5600902276fd0fb32e3e1d5f64f0a0c2`, 2026-09-06. Three fixer groups merged in sequence, `main` green after each; record PR #468 at `7f5b674`, then stamp. Merge SHAs in the roster's `resume.merge_sha` fields. Record/tooling since v6.3.14 stamp: #452, #458, #459, #468, #469. Unstamped #451 from v6.3.14 included in this stamp.

### The #387 blocker, 2026-09-04

**Fixed 2026-09-04, merged as `32f309f` (PR #388), released under the v6.3.12 framing decision above.** The reasoning below is kept because it is what the fix rests on, including the "one CI runner is not the fleet" lesson.

`main` is red on roughly half of all merges and the v6.3.12 stamp is blocked
behind it, from a regression this programme itself introduced in #346 / PR #378
and released as v6.3.11. Every push to `main` forces `GATE_SCOPE=full`, so
`tests/stress.py` runs on every merge; its coverage check demands **≥ 40 of 51**
scenarios land in a *recorded* solver basin, and on a runner whose basins are not
the recorded set it gets **29**.

Exactly 22 entries in `tests/stress_budgets.json` carry an `alt_basins` list, and
exactly those 22 flip together — one cause (the CPU model and its BLAS kernels
choosing the multi-start basin), one cohort. The floor was sized on the
assumption in its own comment that "a third platform may hold a third basin *for
some scenario*", i.e. that the misses are per-scenario and independent, leaving
eleven scenarios of slack. They are not independent. Four full-scope pushes after
#378: two green, two red, on commits differing only in INERT paths.

The owner chose **the `env_drift` shape** — capture each scenario's solver work
twice in one run, tree and merge base, compare computed against computed, no
basin table — at an accepted **≈ +500 s** on full-scope runs, and chose to fix it
**alone before anything else merges**. Recording the observed basins was rejected
as a treadmill (the `ubuntu-latest` fleet is heterogeneous and not enumerable, so
each new runner model contributes another basin for all 22); lowering the floor
was rejected as discarding what #346 existed to buy.

The general lesson, which the remaining gate-instrument groups are now reviewed
against: **one CI runner is not the fleet.** #378's reviewer asked exactly the
right question — whether a 2× regression is still caught on a machine whose
basins are not the recorded set — and the answer was measured on a single runner
and generalised.

### What triage changed, 2026-09-04 (batch B2)

Three read-only judges, run on this idle box (`load1` 0.17–0.58, `thread_factor` 1.00) at
`291ae76`. Two of the three overturned a brief this plan had already written, so the
corrected version is recorded here as well as on the issues.

- **#258 is re-scoped, and W1-G13's brief was wrong.** #333 did fix the clipping half:
  `units_with_ink_on_top_row` **12/12 → 0/12**. But its `uy` clamp traded the clipping for a
  new ink collision — the value-axis unit and the top tick of its own axis overlap by
  **1.00–1.25 px vertically and 4.0–8.5 px horizontally** on every tile that engages the
  font floor, **9 of 13** measurable pairs, leave-one-out **9 of 9**. This plan's hypothesis
  (a horizontal right-axis unit at `ux = x + 5` running past the viewBox) is **refuted**:
  right-edge headroom is −21.5 to −80.7 viewBox units and `ink_at_right_col` is false in
  every arm. The residual is vertical, not horizontal, and W1-G13's brief has been rewritten
  to say so. The finder's `card_geometry.mjs` is **void** for this row — its
  `text_overlap_pairs` reads 941 before and 941 after a perturbation that takes the collision
  9 → 0. The measured fix is `plotT = Math.max(MARGIN.top * marginScale, font * 1.45)` plus
  the `uy` offset 4 → 5.2; raising `plotT` alone does not work because `uy` tracks it.
  **No committed check can see this defect**: the DOM stub returns a constant 900×400 rect so
  the font floor never engages, the browser lane measures fonts and hit targets and never
  label proximity, and CI run 33829697839 at `291ae76` is green with the defect present. The
  fixer's failing test must therefore be a real-Chromium proximity check in the committed
  browser lane, or the fix ships without a witness.
- **#304 is re-scoped to 21 named statements, and its mechanism is refuted.**
  `config_flow.py` measures **96.2 %** (547 statements, 21 missed) — the third independent
  measurement to land on that figure, across two Python versions and two coverage cores. The
  body's mechanism (“no test submits `async_step_user` with input”) is false:
  `tests/config_flow_steps.py` is unconditional in `run.sh` and drives all three token
  verdicts plus `create_entry` through the real validation path, 89 checks passing. What made
  the gap look open was the frozen `coverage_suite.sh`, whose hand-typed `SCRIPTS` list omits
  that script — the same instrument-rot class as #334. All 21 residual statements are
  reachable by extending the existing harness with **no production change**; the largest
  single bite is 6 of 21, one repeated `return vol.Optional(key, default=existing)` idiom
  across six options pages.
  **Sequencing consequence:** #304 lands *before* the #223 registry stage, not in
  Wave 5. (That stage is numbered S11 here and S10 in #193's own stage list; the
  issue number is the stable reference, not the stage number.) #223 rewrites
  exactly those six options pages into a registry, so the coverage extension is the witness
  S11 needs, and writing it afterwards would mean writing it against code that has already
  moved.
- **#242 is weakened to a structural zero, and W3-G4 is struck.** The derivation spike
  returned **no admissible candidate**, and the obstruction is analytic rather than a
  coefficient that needs tuning. The base curve's log-slope budget is **+0.03030/K at 0 °C
  and exactly 0 above +27 °C**, while any ratio anchored on `(T_ref − T_out)` contributes
  **−0.01429/K at 0 °C, −0.04667/K at 20 °C** and diverges as `T_out → 35 °C`. The 0.0000 SEK
  plan consequence is therefore structural, not a sampling artefact: **189,882 Carnot-branch
  calls** across all nine shipped cells, every one at `T_out ∈ [−16, −8] °C`, against a
  coldest turnover of **+9.96 °C** — a 17.96 K margin. Wave 3 loses its fourth group; the
  physics half of the issue stands as verified and documented.

### What triage changed, 2026-09-03

The judges overturned this plan three times, which is what they are for. Recorded here
because the corrected version is what the waves now execute; the full numbers are in the
judge comments on each issue and summarised on #201.

- **#195 was not superseded and is now fix work.** #304's judge comment is aggregates, not
  the per-module table #195 asked for, and the only committed table on main is the stale
  88.4 % artefact. Re-measured: **89.7 %, 23 of 48 modules under the 95 % bar, and
  `coordinator.py` alone is 789 of the 1,338 missed statements** — 59 % of the deficit, so
  its half sequences behind the #193 seams. The leave-one-out is the planning fact:
  `validate`, `edge`, `backtest`, `optimality` and `plan_view` each move the total **0.0
  points**, so coverage cannot be bought with end-to-end scripts.
- **#325 is not an accepted limit.** The settle hour buys the identifiability — discrimination
  0.036 (below its own null floor) to **0.288** — but only if the settle hour's real delivered
  power is recorded. `sysid.step()` hard-codes 0 kW, and admitting those rows unchanged makes
  it *worse*: 0.012, with a −0.064 UA bias on an honest install. Record the power first,
  widen the filter second.
- **#334's residue was inverted.** `D6/claims.py` is repaired; **`D9/d9lib.py` is the one still
  dead**, in ten files. The README has contradicted `HARNESSES.md` since #348, and no file on
  main names the SHAs the tag moved between.
- **#277, #244 and #325 are one group**, three views of one lead in `sysid.py`'s
  `step()`/`identify()`; splitting them would lose #325's ordering constraint.
- **The Wave 4 order was inverted, by the ratchet's own numbers.** The plan of
  record put DHW before fetch. The measured cut costs on main read
  **views 120 < fetch 132 < dhw 195 < grid 236 < learning 350**, so the stages
  now run in that order. A stage is never justified by cut cost alone: three
  tools give three different orderings of the same class, so cut cost is a
  property of the partition rule rather than of the code.
- **The context object separates nothing, and #377 says so.** The round-2
  comment justified extracting the six hub attributes by citing a separability
  result. Leave-one-out overturns that reading: drop **all six** and 200 of 254
  methods remain one connected component, with every other component a
  singleton. What it is actually worth is a cut discount — **189 of 1,033
  cross-seam references, 18.3 %, changing no rank** — plus the deletion of a
  coordinator back-reference every later stage would otherwise need. It goes
  first because it relocates no method body, so no open fix can be silently
  reverted by it.
- **`optimize` is the most decomposable of the five monoliths, not the least.**
  The plan assumed the opposite. It has five ratchet-clean verbatim blocks at
  6–11 interface cost, the first being 64 lines at 6 in / 0 out after the solve,
  where no hot-loop question arises. The real carrier case is only the DHW tail,
  and it wants a dataclass of the 14 keys the method already returns rather than
  a state object threaded through. Constraint that decides the cuts:
  `functions_cc_over_15` sits at 39 of 39 with zero headroom, so every extracted
  helper must come in at or under complexity 15 — the otherwise obvious cut is 18
  and fails the gate.
- **#225 is closed, not re-scoped.** Its two named targets measure worst-boundary
  37 and 30 live locals inside the batched objective the gradient solver
  evaluates, no cold target remains above the 150-line mark, and `ThermalModel`
  binds no ratchet metric at all — the class contributes 3 of 23 oversized
  methods, behind the coordinator's 8 and the optimizer's 7.
- **#303 now has a ruler that cannot be gamed**: with the stub excluded by
  construction rather than subtracted afterwards, main measures **427**
  production-only strict errors, against 743 with the test fake — so 42.5 % of
  the historical headline was an artefact of a fake class. One correction to the
  brief it was given: `--warn-unused-ignores` does **not** prevent
  ignore-stuffing, since four real annotations and four live ignores move the
  count identically, so the ignore count has to be its own hard metric.
- **#197 and #233 closed**, each with a sharper reason than the plan's: 160 mypy errors was a
  *different ruler* (non-strict) rather than a stale count, and #233's restart gap fails its
  own flat-price null at both 24 and 48 hours.

## Carried findings awaiting a stage

- **An input-side carrier for `_optimize_space_only`, from #224's stage-5 brief
  (comment 5615941654), awaits a stage.** #224 closed on that brief rather than
  on a cut: the method's cheapest tail is a pure consumer of computed locals, and
  the same name set recurs in `_optimize_with_dhw` and `optimize`, so one carrier
  might pay in three places — a name-set intersection, not a dataflow proof, and
  the brief says to test the shared-shape hypothesis before designing the
  carrier. `_plan_dhw_min_cost` carries a recorded decision not to split. No
  wave owns this: UX lane F is the only planned `coordinator.py` work after
  Wave 5, and this is `optimizer.py`. Re-measure at your own merge base.

- **Nothing measures a numbered list's numbering.** Carried to the corpus-loop
  work in `.claude/workflows/policy_lint.mjs`. #623 shipped `docs/HANDOVER.md`
  with two entries numbered 8, two numbered 9 and two numbered 10, green through
  `policy-docs`, `prepr.sh` and a review. **A numbering check must not
  renumber**: six tracked sites cite traps by number — `tests/env_drift.py`,
  `tools/audit/prepr.sh`, `tests/entities.py` and this file at three places,
  naming traps 11, 12, 17 and 18 — so it refuses duplicates and gaps while
  leaving existing numbers fixed, and the list is deliberately not ascending.
  Re-derive that citer set at your own merge base rather than quoting this one.

- **CLOSED by #658 (`ac423c8`).** The `record` check was satisfied by a bare token, not by a disposition — and
  the replacement is an anchor, not a row format. Scheduled by principle 6
  above: after `10-adr-corpus`, before the next release stamp. `checkRecord` is
  one line — `new RegExp("#"+pr+"(?![0-9])").test(text)` — over
  `docs/plan-2026-09-open-issues.md` and `docs/HANDOVER.md` concatenated, so any
  occurrence anywhere satisfies it. **The haystack is the same text as the
  subject matter**: it searches the two documents whose job is to discuss pull
  requests, so collisions are the expected behaviour rather than bad luck, and
  they cluster on the pull requests that edit these two files, because those are
  the ones that cite other pull requests. Measured at `cc2efc9`: #621 and #623
  read as dispositioned while the Delivery-status table held no row for either —
  one on a trap citation in the handover, one on a paragraph in this section —
  and **both mentions were written by a single commit, `03af74b`**, which
  described #621's defect and named itself.
  **The design that landed, and why it is not the one proposed here.** This
  entry proposed a LIST-ITEM anchor — the number must open a list item,
  `- [#NNN](…`, said to hold for 65 of 65 rows. Driven again before building it,
  against the 42 merged in the window at `e4f34c7`: **two fail** — #629 and #632
  are dispositioned inside Delivery-status TABLE CELLS, on the rows of the issues
  they close (`| **#527** … |`, `| **#590** … |`), which is a legitimate
  disposition this repository actually writes. Re-derived at this head, where the
  window is larger: **five fail**, and the two new kinds are worth naming. #653 is
  a further table-cell disposition. **#585 and #587 are not pull requests at
  all** — both are issues, and the merge subjects that name them end in an issue
  number, which `MERGE_SUBJECT_RE` takes for a pull-request number. A rule that
  pins a row shape would have had to refuse all five, and **two** of them have no
  row to write. (Checked against the API rather than inferred: #629, #632 and
  #653 are pull requests; #585 and #587 are not. An earlier draft of this
  sentence said one, and #658's round 2 counted them.) A rule that refuses it
  either loses those records or forces duplicate rows, and it pins a shape rather
  than a property, which this entry itself forbids two paragraphs down.
  **The anchor is the SECTION.** A disposition must appear under the plan's
  `## Delivery status` heading, or anywhere in the handover. Measured at the head
  that landed it, and at every head since: all of them
  are linked from that section and from nowhere else, and the mentions that made
  the old check pass on nothing — a carried finding naming a pull request in
  passing, a standing rule using one as an example — are all outside it. The
  handover is not demoted: it contributes all of itself, because carrying the
  record is its whole job. A renamed heading reports as its own error rather
  than as one error per merge in the window, so fail-closed does not read as a mass defect.
  Landed with seven acceptance pins over synthetic input — inside counts,
  outside does not, a plan with no such heading says so, the region CLOSES at the
  next section, and a disposition written only in the handover still counts —
  because the region is
  otherwise widenable back to the whole file with every other count unchanged;
  the tip invariant moves from 76 pins to **83** across the same 10 classes.
  **What it does not fix, stated so the next seat does not overclaim.** An
  anchored row can still say nothing — `- [#NNN](…) — merged, see above` passes.
  (Written `#NNN` deliberately: a real number here would itself satisfy the
  check for that pull request, which is the defect demonstrating itself.) This
  moves "any mention counts" to "any anchored line counts"; it does not reach
  "a statement about this merge", and nothing mechanical does.
  Re-derive the passing-by-accident set at your own merge base rather than
  quoting this one — it changes with every merge. **This is programme-closing work**,
  sequenced by principle 6 rather than filed: an issue is not the instrument for
  propagation. #627 was opened for it and closed. It is carried **here** and not
  in `docs/HANDOVER.md`: that file is at its cap, and `writing-for-agents.md`
  forbids paying for an addition by cutting evidence, so at its cap it can
  take nothing new. That is a real constraint on the living handover and is
  itself owed work — see `## Standing rules`.
- **A pull request cannot name its own squash-merge SHA.** GitHub creates the
  squash commit at merge time, so a row saying **merged `<sha>`** written in its
  own branch is either back-filled later or false: #612's row, which reads *"Its
  own row is this one"*, was in fact written by **#621** at `07ae2d8`, nine
  merges later. Rows for merges that have already happened carry their SHA; a
  row a pull request writes for itself names its number and claims no SHA. This
  is why the `record` job cannot be satisfied in advance and why each remaining
  queue branch carries its own row before merging.

- **CLOSED. `main` is guarded, and this was the programme's last act.** Ruleset
  **`main-protect`, id `22628467`**, active on the default branch: deletion,
  non-fast-forward, and **18 required status checks**. It replaces the two
  `200 []` answers this entry used to report, under which every check here was
  advisory at the merge boundary.
  **The ordering was the whole argument, and it held.** A required context that
  never reports blocks every merge permanently, so the set could not be created
  until `record` and `env-matrix` existed on `main`. Before creation all 18 were
  confirmed present on **every open pull-request head**, not on one convenient
  head: a required check is evaluated on the pull request's head, and that shape
  differs from a push — `CodeQL` reports on the first and not the second.
  **A skipped required check satisfies the rule**, which is why five jobs an
  earlier payload excluded for that reason are in the set. Driven on an isolated
  probe, `main` at zero rules throughout: a pull request whose required
  `closures` was `SKIPPED` and `policy-docs` `SUCCESS` read `MERGEABLE /
  UNSTABLE`. The **negative control** is what makes that a result — adding a
  context that never reports flipped the same pull request to `BLOCKED`, and
  removing it returned it to `UNSTABLE`. That control is also the direct
  evidence for the ordering above.
  **Unchanged from the operative payload, each for its stated reason**: the
  role bypass — recorded as `RepositoryRole` **5**, the admin role, not the
  maintain role an earlier draft named — so `tools/release/stamp.py`'s direct push to `main`
  still lands; `strict_required_status_checks_policy` **false**, because
  "require branches to be up to date" would force a merge commit onto every
  frozen review head whenever `main` advances; and **no required-approval or
  code-owner rule** (ADR 0005), because one identity authors and approves here,
  so such a rule is a lock rather than weak enforcement.
  **The bypass premise was tested rather than assumed, and the instrument that
  looked like it answered does not.** `GET /repos/.../rules/branches/main`
  returns the identical rule list with the bypass-actors list emptied, so it
  reports the branch's configured rules and says nothing about the caller —
  reading it as *"the bypass does not apply to me"* nearly produced a false
  alarm that the release stamp was about to break. Probed properly on a
  throwaway branch with its own ruleset: with the admin bypass the push lands,
  without it GitHub answers *push declined due to repository rule violations*.
  Two-sided, so it is a measurement. The probe ruleset and its branch are
  deleted.
  **What it did to the pull requests already open: nothing that was not already
  true.** Five needed a rebase because `main` moved six times that night. #656
  read `BLOCKED` on two required checks still running, and carried an earlier
  `pr-contract` failure behind a later success at the same head — which does not
  block, because required checks are evaluated on the latest run per name.
  **#609's permissions reading was a proxy artifact** — it recorded
  `{admin: false, maintain: false, push: false, triage: false, pull: false}`
  while pushes plainly worked, and suspected as much; this session reads
  `admin: true`, and create/update/delete of a ruleset all succeeded.
- **CLOSED by #670 as decision 0007.** O3 is decided: after this session, a policy merge needs the owner's
  approval per pull request, with a per-session grant as the option, recorded as
  ADR 0007. The governance-audit plan (archived on
  `audit/session-evidence-2026-09-08`, not on `main`) left O3 as its closing
  question: whether policy merges after the programme revert to owner approval
  per pull request or stand on the ruleset plus `pr-contract`. The owner ruled
  on 2026-09-09: **per-PR approval**, with the **option of a session grant**
  of the 0001/0006 shape — a decision record naming the session, the six
  preconditions, reverting at session end. The ruleset and `pr-contract` are
  the floor either way, not the substitute. **Landed as ADR 0007**, which does
  NOT wait on the ruleset: the decision dates what it says about the
  repository and stands whether or not a ruleset exists. An earlier draft of
  this entry said it lands beside the ruleset as the programme's last act;
  0007 says otherwise and 0007 is the record. **DISCHARGED**, and stated here
  because deleting that draft nearly deleted the obligation with it: the
  programme's closing #201 comment lists every pull request merged under the
  grant — 0001's and then 0006's — with its verdict and head SHA, which is what
  the governance-audit plan asked for. Fifteen of them, **every verdict a
  `merge` naming its own head exactly**, checked mechanically with a corrupted
  head through the same comparison as the null control.
- **The verdict-example pin has two residuals its own reviewer drove, and one
  is a hole rather than a limit.** #641 round 2 attacked the widened block in
  `check-wave-script.mjs` and found three properties, two of which are left
  standing deliberately. **(a) The `blocked:` refusal is backtick-anchored**:
  the rejected spelling inside a fenced code block passes, while the same
  spelling in inline backticks fails — so a brief can still document the old
  form in a fence, and a brief warning *against* it inline cannot. The escape
  hatch and the hole are the same hatch; closing it means deciding whether a
  fence is documentation or instruction, which is a question about briefs and
  not about this checker. **(b) The floor of three is directory-wide**, so
  deleting one brief outright still passes at 36/0 — the floor guards the
  empty extraction, not per-file coverage; a per-file floor would pin which
  briefs must carry examples, which is the row-format mistake in another
  costume. The third, a hard-wrapped example failing for the width of its
  column, was **fixed** in that pull request rather than carried. Whoever
  revisits (a) should note that the same fence question governs
  `policy_lint`'s own prose checks.
- **A verdict comment whose first line is wrapped in backticks does not parse,
  and every verdict this queue has received was wrapped.** Found by #644's
  round 5 while reading the grammar it was reviewing. `web-fix-wave.js` reads
  `body.split('\n')[0]` and anchors `VERDICT_RE` on `^Fix review:`, so a first
  line of `` `Fix review: merge <sha>` `` fails to match and degrades to no
  verdict — safely, never to a wrong merge, but silently. The queue's own
  comments were unaffected because no wave script consumed them in this
  session; a wave that did would have read every one of them as unparsed. The
  pin #641 landed compares the contract's backticked EXAMPLES against the
  grammar, which is the right thing to compare and not this: the examples are
  backticked because they are examples, and the rendered comment must not be.
  Two candidate fixes, neither obviously right: strip a single pair of
  wrapping backticks before matching, which forgives a real formatting error;
  or say in `fix-review.md` that the first line is unwrapped and pin THAT,
  which needs a fixture comment rather than a brief. Whoever takes it should
  decide which of those the contract means before writing either.
- **`env_drift.py` reads the baseline at the ref's TIP while it takes the diff
  at the merge base**, so a local run against `origin/main` and the same run
  against the merge base can disagree — and the disagreement is exactly the
  one #662 exists to prevent: `--claims-only <merge-base>` says `ok` while
  `--claims-only origin/main` says *"Empty the lists"*. Found by #662's round
  2, which hit it live because `main` moved twice during the review. **CI
  never reaches it** — every workflow passes the merge base — and it predates
  #662, so it was carried rather than folded in. The remedy is one line:
  default the local ref to the merge base rather than to `origin/main`'s tip,
  which is what every caller that matters already passes. Until then, a seat
  running the check by hand should pass `$(git merge-base origin/main HEAD)`
  and not `origin/main`; #662's own body says so.
- **CLOSED by this pull request.** `pr-contract` red runs were hidden by the listing that shows one run per check, and the ones on this
  queue's heads were process state (b), not a defect in the check. Two facts,
  and only the first is the check's.
  **The reporting hole is real.** `gh pr checks` shows only the **latest** run
  per check, so a check that fails and then succeeds reads as never-red. Read
  `/repos/.../commits/<sha>/check-runs` filtered on `conclusion`. **#625 was
  merged with a `pr-contract` failure at its head (`3b823f8`, 19:11:34Z) and a
  body saying `## Red checks: none`.** That body is wrong and this row is the
  correction; the merge stands.
  **The cause was misdiagnosed, and the record refutes the diagnosis.** An
  earlier draft of this row called the failure structural — *"a body cannot name
  a SHA before that SHA exists"* — and cited `docs/HANDOVER.md`. That file
  contains no `pr-contract` and no `relocat`; the sentence being remembered is
  in the **out-of-tree** programme handover on `audit/handover-2026-09-08`, and
  this is the **second** time in one session those two documents were conflated.
  The in-tree record is `.claude/skills/steward/SKILL.md` **§ S10**, and it
  denies the premise: a commit's SHA exists when the commit is *made*, so the
  body can always be written against it before the push. S10 also says **both
  orders leave exactly one failed run** — what the order controls is *where* it
  lands: push-then-edit puts it on the commit that is your review head, while
  edit-then-push fires the `edited` run against a head you are abandoning. S10
  line 134 names the first order **`EXAMPLE BAD: push, then update the body,
  then explain the red run on your head`** — which is what every head of #628
  did, explanation included.
  **So the generalisation was wrong too.** Measured across nine recent heads:
  five carry a `pr-contract` failure — **four of four inside #628, one of five
  outside it** — and the split tracks S10 compliance rather than a property of
  the check. It is not "almost every head push"; it is almost every push that
  used the order S10 marks bad.
  **And one of the two failures at #628's fourth head was a different defect
  entirely**: a body edit produced `## Forward-carry## Forward-carry`, and the
  contract correctly refused a body with no such section. A cheaper detector
  exists and was skipped — `policy_lint --pr-body <file> --head <sha>`, which is
  step 7 of `tools/audit/prepr.sh`, whose own `--self-test` already carries
  `missing-section` as a rot fixture. That one is not the check's fault in any
  sense.
  **CLOSED here.** What was owed was the reporting hole and not the
  contract: a seat writing `## Red checks` must read the check-runs API, and
  `gh pr checks` should not be the instrument. Whether the `pr-contract` job
  should additionally skip a run whose only difference is a stale head SHA is a
  separate question that this row no longer asserts an answer to, because the
  premise it rested on is denied by S10.

- **`docs/HANDOVER.md` cannot accept a new fact, and the fix is a graduation
  rule rather than a higher cap.** The deadlock is structural and is recorded
  under `## Standing rules`: the file is at its cap, the cap is one-sided by
  design, and `writing-for-agents.md` — which governs that file — says
  *precision outranks concision, always* and *cutting evidence is never
  compliance*. Reflowing reclaims **0 lines** at its own width, derived
  independently by a reviewer, so there is no formatting slack either. An
  attempt to pay for three traps by compressing nine entries was blocked for
  cutting evidence in five places, two of which inverted a trap's meaning.
  **The rule:** *a trap whose failure mode has acquired a mechanical detector is
  replaced by a one-line pointer to that detector.*
  **Why this is not the cutting `writing-for-agents.md` forbids.** A trap
  superseded by a working check has not lost its evidence; it has been
  **promoted** — out of prose a reader must remember and into something that
  fires on its own. That is this programme's whole thesis, stated in #625's own
  title: *three rules that fired only in CI now fire at the moment they are
  broken.* Retiring the prose copy completes the work rather than trading it
  away.
  **Runway, re-derived at this head — and re-derive it again at yours.** The
  handover holds **twenty-five** traps. **Four** have a mechanical detector on
  `main` today, each named with its file: trap 11 (a shallow clone answers "no
  common ancestor" silently) by `.claude/hooks/session-start.sh`; trap 9
  (orchestration scripts nobody runs) by `check-wave-script.mjs` and
  `policy_lint --hooks`; trap 19 (a one-sided cap colliding across branches) by
  the `policy-docs` job on `main`; trap 17 (a citation and its referent on two
  branches) by `CLAUDE.md` rule 1's forced `GATE_SCOPE=full`. A **fifth**, trap
  8 (one CI runner is not the fleet), gains `policy_lint_envmatrix.mjs` when
  `08-envmatrix` lands and not before — an earlier draft of this entry counted
  it as already present, and a reviewer refused that, correctly. Two more that
  the same draft counted do **not** qualify: trap 23's "tip pin-count
  invariant" is trap 23's own prose instruction, not a detector — nothing
  refuses a mis-rebase by itself; and trap 10's `tools/audit/preflight.sh`
  reads a pull-request *body* on stdin, never a commit message, so it does not
  fire in the mode that trap needs. Trap 11 goes from three lines to one. The
  set grows as the programme mechanises, so the document shrinks exactly as
  fast as the honour system is replaced — which is the behaviour a ratchet
  should have.
  **Not every detector is the same kind, and the rule must say which suffices.**
  Driven at `d08a56a`: trap 11's detector is real — `session-start.sh:31` runs
  `git rev-parse --is-shallow-repository` and its self-test asserts *"the
  shallow state is printed and is one of the three answers"* — but it **reports
  rather than refuses**. That is enough here, because trap 11's instruction is
  *check before believing a comparison*, and a report at session start fires at
  exactly the moment the trap would bite. It would **not** be enough for a trap
  whose failure is a silently wrong result with no reader present. So the test
  is not "a detector exists" but **"a detector fires at the moment the trap
  would bite, in the mode that trap needs"** — reporting for a trap that asks a
  reader to look, refusing for one that produces a wrong answer unattended.
  **Each graduation owes a mutation proof.** Break the detector, show the check
  going red, restore it. Deleting prose on the strength of a check nobody drove
  is the defect this corpus keeps finding, and it would be a bad way to lose a
  trap permanently.
  **The floor, and the only condition under which a raise is right.** Some traps
  are permanently unmechanisable and trap 12 says so in its own text — a check
  written against that very class catches **0 of 3**. Those stay forever. If the
  irreducible floor ever exceeds the cap, a raise **is** warranted, and the case
  writes itself because the irreducible entries can be named. That is a raise
  that buys architecture; raising it now, to fit, is the thing `CLAUDE.md`
  forbids and would move the wall by one session.
  **Two alternatives rejected, with reasons.** Raising the cap now is
  raise-to-fit. Splitting the traps into a second file under `docs/` is refused
  mechanically: `tests/entities.py` asserts *"exactly one handover, with no date
  in its name"*, checked rather than assumed.
  **Ordering:** programme-closing work, after `10-adr-corpus`, beside the
  record-check anchor rewrite and the ruleset. Not inside the queue — the
  mutation proofs are per-trap and would stall it.
- **CLOSED by #662 (`2d06e06`).** `claims-autofix` erases an earlier lane's claims from `main` at squash-merge
  time, and it has already done so once. Measured on #634. `inherited_claims_error`
  fires when a branch's parsed claim list equals its **merge-base's**; after a
  rebase onto `a684cce` (#633, which added 46 lines to that file — **33** of them claims, the rest header and reasons) that is exactly
  the state `claim-files.md:47` calls "cannot conflict" — byte-identical to
  `main`. Both `fast` legs refused it and the bot repaired the branch by
  **emptying** the list (`6e2dd81 ci: drop inherited claims`). A squash-merge
  then three-way-merges base=33 claims, branch=0 onto main=33 and applies the
  deletion: `git merge-tree --write-tree origin/main 6e2dd81` diffed against
  `origin/main` is `card_claimed_drift.txt | 33 ---`, and `comm -12` over #633's
  added lines and the bot's removed lines returns **33**. The `claimnotes`
  merge driver that unions claim lists locally is per-clone config GitHub
  cannot run. **Precedent, twice:** `2b5e416` (#608, a governance pull request that
  never touched the card) deleted 33 lines #569 had added, by the same path;
  and while this entry sat in review, `dda7193` (#635, rebased onto `a684cce`
  and autofixed) deleted all 33 of #633's — `main`'s claim list is now empty.
  The warning on #201 preceded it by 9 minutes. Same path,
  and `main` merged **21** more times between `2b5e416` and `a684cce` with no stamp
  between, every completed `Tests` run green — so the gate is unaffected. A
  push to `main` measures drift computed-vs-computed at
  its own head (the #387 shape), and `stamp.py` deletes every bare claim at
  release anyway, counting them as it goes. **What is damaged is the record**:
  main's claim file stops saying which fixtures a lane claimed and why, and the
  stamp's `deleted_claims` count under-reports. **The fix is not in any branch's
  hands** — `ci-autofix.md` forbids hand-restoring, and restoring would only be
  emptied again. And the first draft of this entry prescribed a remedy that is
  **not implementable as written**: "skip the file the branch did not touch"
  names a git state indistinguishable from "carried forward", and
  `inherited_claims_error`'s own docstring (`env_drift.py:1259–1271`) fires on
  exactly that state. The discriminator the fix stage needs is not git's file
  history but **the branch's own computed drift**: `env_drift.py --all` already
  measures every fixture tree-vs-merge-base, so a claimed fixture that does not
  move on this branch is a claim the branch is *carrying*, not *asserting*.
  Such a branch should keep `main`'s list **unchanged** rather than empty it —
  then the squash's three-way merge sees no change to the file and `main`'s
  claims survive — and the check should refuse only a claim the branch asserts
  for a fixture its own diff moves. "Excuses nothing" and "excuses by accident"
  are separable by drift; they are not separable by `git diff`. Three
  precisions for that stage, each from round 4 of #634: the remedy touches
  **two** guards, not one — `record_pr_claims_error` (`env_drift.py:1589`) is
  absolute-empty and fires next on exactly the docs-only branches both erasures
  came from; the **card** list's instrument is `card_drift.mjs`, since
  `env_drift.py --all`'s `capture_tree` has no card states, so the drift
  predicate for `card_claimed_drift.txt` lives there; and `--claims-only`
  cannot make the carried-versus-asserted judgment at all — it compares lists,
  not drift — so the pre-push check is a smoke test, not the fix. The predicate
  itself is already computed: `--all` reports `stale = judged - claimed_hits`
  (`env_drift.py:2007` — an earlier draft cited `:1981`, a number carried from a review comment rather than read from the file; the fix stage will follow this pointer, so it is read here), 55 per-scenario verdicts against a merge base. Carried rather
  than fixed here
  because `tests/env_drift.py` is shared with the parallel session's lane and
  the change needs its own mutation proof and rot fixture. Until then, every
  branch rebased onto a claim-carrying `main` will do this on merge. #635
  already did it to #633's; `main`'s list is empty now, an empty list inherits
  nothing, and the window stays closed until the next claiming merge.

- **CLOSED by #659 (`e7a5433`).** The environment matrix could lose a shape or a row without noticing. Found
  by #639's first review, reported rather than blocked on, carried here so the
  matrix's next maintainer inherits it. `policy_lint_envmatrix.mjs`'s
  `MATRIX VACUOUS` guard keys on the shape *directory* existing, so a shape
  whose builder is deleted still passes as "13 held across 5 shapes" against a
  reused work directory that holds the previous run's clone; and no declared
  row *count* or row *name set* exists, so a deleted row is never noticed — 12
  of 12 reads as fine. The precondition for the fix: pin the row set by
  **name**, not by count (#614 round 3: a count is satisfied by a duplicate and
  by a swap), and have `build` refuse a work directory that already holds the
  shape rather than reuse it. Cost measured by the reviewer: none of the five
  shapes as declared are affected today; the hole is in what the matrix would
  say if one went missing.

- **#580's two residuals outlive it, and neither is in any contract.** The judge
  closed #580 and merged it into #588, leaving two one-clause policy changes
  named only in a comment on a closed issue. First: **`fix-review.md` has no step
  for an ABSENT check.** Step 11 obliges an answer for a check that went *red*;
  `grep -icE "absent|never ran|did not run|missing check|queue"` over that
  contract returns **0**. A pull request whose workflows never queued — which
  `claim-files.md` records as the ordinary consequence of a `DIRTY` merge state —
  presents a reviewer with no red checks at all, and the contract tells them that
  is fine. This is #669's defect approached from the other side: that one was a
  red run hidden behind a later green, this one is no run at all. Second: **the
  mutation proof is executed twice and lands in prose both times** — `fixer.md`
  step 2 and `fix-review.md` step 1 — so a proof that a check can fail exists
  only in two pull-request bodies and never in the tree, where a later seat could
  re-run it. The remedy the ruling names is that a mutation proof terminates in a
  committed control wherever one is constructible. Both are policy edits at zero
  cap headroom, so both need either an owner-approved raise or a graduation to
  pay for the lines.

## Standing rules

Unchanged from the repository's own protocol; restated here because a fresh
session reads this file first.

- **Measurement, three ways a command answers a question you did not ask.**
  All three cost this session a wrong reading, and all three print a normal
  result. `git push origin <branch>` from a **detached** worktree pushes the
  branch ref rather than your HEAD — push `HEAD:refs/heads/<branch>` and read
  `git ls-remote`, never the push's own output. A check script run from another
  worktree measures **that** worktree, not the one you meant. And within
  `policy_lint.mjs` the read models differ: the corpus checks read **tracked
  files from git**, so moving a file aside leaves the error unchanged and reads
  as "not the cause", while `--record` reads the **working tree**, so copying a
  file in changes the answer — isolate with `git rm --cached`, and establish
  which model a check uses before believing a negative result. These belong in
  `docs/HANDOVER.md` and are here because that file is at its cap; see the
  carried finding below.
- **CLOSED by #660.** `docs/HANDOVER.md` was at its cap and could not accept a new fact.
  `writing-for-agents.md` governs it — *precision outranks concision, always*,
  and *cutting evidence is never compliance* — while the cap is one-sided and
  only moves down. Together those two rules mean the living handover can take
  nothing new once full. An attempt to pay for three traps by compressing nine
  entries was reviewed and **blocked**: it lost the path in trap 12, the literal
  vulnerable glob in trap 21, trap 25's worked example, trap 17's control clause
  *"and reproduced the defect"* — without which the trap's lesson inverts — and
  half of trap 18's prescribed verification. Reflowing the traps section
  reclaims **0 lines** at the file's own width of 80–81, independently derived
  by the reviewer, so there is no formatting slack either. **Resolving this is
  owed work and needs the owner**: either the cap rises with a stated case, or
  spent content graduates out of the file deliberately. Until then, a session's
  durable findings land here.
- **Fixer** (`tools/audit/briefs/fixer.md`): failing test first, importing the
  production symbol; mutation proof pasted into the PR body; the finding's own
  harness re-run before and after at the measured head SHA; a null control on
  every cost, gain or time claim; a learner or guard measured at both ends of
  its range; claims only for drift you measured; the scoped gate green locally
  through the gate lock; never `VERSION`, the manifest version or the
  `RELEASE_NOTES.md` heading. **After any rebase, steps 2–8 are re-executed** —
  the evidence describes one tree and a rebase makes a new one.
- **Reviewer** (`tools/audit/briefs/fix-review.md`): a fresh worktree at the
  head SHA, the mutation proof re-run, the measurement taken with the
  **finder's** harness rather than the fixer's, `env_drift.py --all` against
  the claims, and an attack at other configurations. Verdict `Fix review:
  merge` or `Fix review: blocked — <why>`. A reviewer never ranks below its
  fixer.
- **Claims.** A branch that moves fixtures claims them with a direction; the
  check is three-dot, never two-dot. A name cannot be both claimed and
  `may-drift`. Value-bearing fixtures are **never re-recorded on this box** —
  only an environment that records them all can honestly re-record one — so
  value drift is claimed and `golden.py --record --only` is for new key paths.
- **Stamps.** Only `tools/release/stamp.py --push`, only after the merge
  commit's own `fast` and `closures` are green, with a notes section naming
  every PR since the last tag. Never by hand, never in a branch. No new branch
  is cut between a fixture-mover's merge and its stamp.
- **Ratchet.** `python3 tests/structure.py` before every push. A change that
  adds coordinator lines pays for them elsewhere, re-records with the reason
  in the commit, or — for a genuine new production feature whose lines cannot
  honestly be paid for elsewhere — **raises** the budget because the capability
  is worth the structure it costs. All three are a decision, not bookkeeping,
  and all three carry their reason in the commit message. A raise additionally
  **requires the repository owner's explicit confirmation before the branch is
  pushed**: it is not a fixer's, a reviewer's or a judge's call, so an agent
  that wants one stops and asks. It is not a route for accommodating
  sloppiness, an unexamined refactor or an unmeasured feature — the first
  question is still whether the lines can be paid for elsewhere — but a metric
  at zero headroom is not a veto on new capability either (#398 read it as
  one). `cross_seam_fraction` carries a
  tolerance band and is never re-recorded: within the band there is nothing to
  record, outside it the gate fails, so a re-record can only loosen.
- **Ownership.** `owner:<session>` and a `claimed-by:` comment before a branch
  is cut. An unlabelled issue is *unknown*, not free.
- **Every fix PR body**: `Closes #N`, `Part of #201`, the head SHA measured,
  and every executed number.

## Model routing

Every seat in this programme — orchestrator, fixer, reviewer, judge, recorder —
runs as a **Claude Code subagent** inside one Claude Code session. `claude-web`
(label `owner:claude-web`, branch prefix `claude-web/`) is the session identity,
kept for continuity with the branches already on origin; since 2026-09-06 it is
also literally the runner.

The orchestrator seat is this session's parent (Opus 5), which executes
`web-fix-wave.js`'s control flow by hand. Workers are Claude Code subagents:

| seat | model | when |
|---|---|---|
| orchestrator | **Opus 5** | control flow, merges, reconciliation, all sequencing decisions |
| architectural fixer + its reviewer | **Opus 5** | W2-G1, W2-G2, every Wave 4 and Wave 5 move PR and its review |
| per-stage survey | **Opus 5** | the survey that precedes a move stage; the halt decision is the product |
| adversarial reviewer, `fix-review` with the **finder's** harness | **Opus 5** | every group whose brief carries a refuted or corrected claim; every fixture-moving group; every move review |
| judge | **Opus 5** | all triage judges, including the #291 and #232 timing judges (still solo on an idle box), and any decomposition judgement |
| fixer on production code, mutation proof required | **Opus 5** | groups the wave file marks `"fixerModel": "opus"` |
| fixer on tests, tooling or docs | **Sonnet 5** | groups the wave file marks `"fixerModel": "sonnet"` |
| record / roster / truth-up / citation-freshness PR | **Sonnet 5** | mechanical docs edits; no measured claim of their own |
| read-only reporting | **Sonnet 5** | Reconcile, post-merge gate watching, the pre-merge checklist, label hygiene, release-notes source material, issue digests, wave inventories, the #303 typing and #195 coverage inventories |
| stamp | scripted `stamp.py` via `web-stamp.js`, drafted by **Sonnet 5** under orchestrator oversight | rule 4 refuses notes omitting a merged PR, and the refusals are the product; the orchestrator reads every refusal |

**Routing moved to Claude models on 2026-09-06**, at the W4-G3 merge (`d979110`).
Delivery-status rows for groups delivered before that date name the model that
actually ran (Grok 4.6 extra high / Composer 2.5, under a Cursor Multitask
parent) and are left alone: the delivery record says what happened, not what the
routing is today. Rows for groups not yet started carry the table above.

**Fable 5.1 is deliberately routed nowhere.** No seat needs a tier above Opus 5,
and every seat that historically took Fable is an architectural fixer or
reviewer, which is Opus 5 already. The absence is a decision, not an oversight.

**The tier tokens in the wave files now map literally.** `web-fix-wave.js` ranks
`haiku < sonnet < opus` and throws if a reviewer ranks below its fixer, so the
tokens stay as they are: `opus` → Opus 5, `sonnet` → Sonnet 5, `haiku` →
Haiku 4.5 (unused today). `tierOk` still applies. The tokens do not need editing.

**`.cursor/rules/*.mdc` still hold three `alwaysApply: true` policies, and
nothing loads them for a Claude seat.** Cursor applied them automatically;
Claude Code loads `CLAUDE.md` and nothing else. The files and every pointer to
them stay — every seat is told to open all three at seat start, and `CLAUDE.md`'s
summaries are not a substitute.

**An architectural reviewer on the same model as its fixer is still a fresh
agent, not the fixer continuing.** Independence here is procedural, not
model-family: the reviewer works in a fresh worktree at the head SHA and
measures with the **finder's** harness, per `tools/audit/briefs/fix-review.md`.

## What the runner changes

This section was written for a 4-core cloud container with no `gh`. **Since
2026-09-06 the programme runs on the owner's 8-core M1 again, with `gh` 2.98
authenticated**, so the first two bullets are history rather than instruction:
`gh` is used directly, and the REST fallback is a shipped capability nobody has
to reach for. The rest still stands and is why it is kept.

- every GitHub action went through the GitHub MCP tools **on the container**;
  on the M1, `gh` is used directly;
- `tools/release/stamp.py`'s rule 2 gained a REST fallback (Phase 0), because
  it shells out to `gh` before any flag is read and would otherwise have made
  stamping impossible there. It is still in the script, and still correct;
- the drift baseline cache starts cold, so the first `env_drift --all` per
  fork pays a full baseline capture — hence one fork per wave;
- at most two agents run at once, and anything needing a quiet box (the
  stress ruler, the timing judges) runs alone;
- **the gate lock is scoped to the runs that need it.** `fixer.md` step 5
  mandates it for every local gate; that was written for a dedicated
  eight-core machine, and on a shared container it serialises every agent.
  The lock exists for one script — `tests/stress.py`, whose solve-time guard
  measures the machine while it solves — so the rule now asks
  `closure.py select` what the diff actually runs and takes the lock only
  when the answer includes `stress.py`, reports `MODE: FULL`, or fails.
  Measured on this tree: a test file selects one script, the card five, and
  none of them `stress.py`; `optimizer.py` and `coordinator.py` select
  sixteen and do. The trap the rule is written around is that a gate file or
  an unmapped file prints **zero** selected scripts while meaning *run
  everything* — so it keys on the mode line, never on the count. What is run
  locally regardless is the evidence CI cannot produce: the mutation proof,
  the failing test at the merge base, and the finder's harness;
- `tests/card_browser.mjs` runs locally against the pre-installed Chromium
  (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`) but CI's `browser` job is the
  authority, because the local Playwright is not CI's pinned version.

## When a merge turns main red

The programme has been in this state, so it gets a written answer rather than a
judgement call each time. `web-fix-wave.js` logs `MAIN IS RED after <group>` and
stops merging; `audit-merge.js` returns `{green:false}`. What follows:

1. **A behaviour change in the merged diff → revert first, diagnose after.** The
   revert is cheap and main being trustworthy is what every later merge is judged
   against. Re-land with the fix and the evidence.
2. **A failure the diff cannot reach → do not revert.** Establish it first, the
   way the register requires: an error naming a subsystem the diff does not
   touch, reproducing identically, or red on the base branch too. Then it is its
   own issue with its own number, and the wave holds until it lands. #387 is the
   worked example — a released gate instrument that was runner-dependent, found
   only because main went red on roughly half its merges.
3. **Never `--allow-red` to get a stamp out.** The flag exists for a human with a
   reason, not for an agent with a deadline.

A red main is work *now*, at every wake, whatever else is running: only a green,
mergeable head waits on reviewers.

## Documentation discipline

So that an aborted session loses nothing:

| When | Where |
|---|---|
| before a branch is cut | the issue: `owner:claude-web` + `claimed-by:` comment |
| after the failing-test commit, and after every commit | the branch is pushed |
| PR opened | the issue: PR link and head SHA |
| reviewer verdict | the PR: `Fix review: …` with RESULT lines |
| cannot finish | the issue: `state at stop:` naming branch, pushed SHA, last green check, what is missing |
| wave end | this file's Delivery status, `docs/audit-2026-09.md` status cells, a #201 comment |
| a merge that settles a decision, corrects the record or leaves work owed | `docs/HANDOVER.md`, in that merge's own PR |
| stand-down | a #201 comment — running seats, unpushed branches, next action. Durable state is already in `docs/HANDOVER.md` and is not repeated |

The per-group briefs are committed too, not only the wave tables above.
The Wave 1b, 2 and 3 rosters closed every group and were archived out of the
tree; they are at `d5d8c4a` (`git show
d5d8c4a:.claude/workflows/wave-1b-groups.json`), and they are
still worth reading before re-deriving anything, because several groups exist
only to stop a fixer redoing work a judge already refuted — W1-G13 names the
measured fix for #258 and the harness that must not be used to check it.
Wave 3L is `.claude/workflows/wave-3l-groups.json`.
Wave 4 is `.claude/workflows/wave-4-groups.json` and Wave 5 is
`.claude/workflows/wave-5-groups.json`. Each group's `resume.stage` says where that
group stands and carries the merge SHA when it has landed; read that field rather
than a progress note here, which is stale by the next merge.

## The UX programme (#558) — what lane B's figure items measured

Carried here because lanes B–F have no roster JSON, so a later figure seat has
no brief of its own to read. Every figure below re-measures at its own merge
base; the numbers are snapshots.

**`docs/*.md` is not rendered by HACS at all, so B1's three constraints are
README-only.** HACS's `async_get_info_file_contents` builds its candidate list
from one stem and returns the first match in the repository's root tree —
`README.md`, `readme.md`, `readme.MD`, `README.MD`, `README`, `readme`. A path
under `docs/` matches none of them, and nothing else in the panel fetches a
second file, so `docs/` reaches a reader only through GitHub. Relative image
paths, and alt text on more than one line, are therefore free in `docs/` and
still forbidden in `README.md`. Control, executed against the pipeline
(`marked@15.0.4` + `xss@1.0.15`) on the branch that added the figures: a
single-line markdown image is rewritten to `raw.githubusercontent.com` and
survives, while a wrapped alt and an HTML relative `src` both come out
`<img src>` with the attribute empty. **Do not spend quality on the README
constraints in a `docs/` figure** — but keep alt text on one line anyway, which
costs nothing and survives the text being moved into the README later.

**A card figure that needs the house's two zone dashes must ask for a two-zone
payload.** A one-zone house publishes `upper` and `lower` as step-by-step copies
of `room`, and the card drops a duplicate extra rather than labelling it — so
the dashes cannot be rendered at all from the default payload, and no amount of
configuration in the figure generator changes that. `tests/plan_view.py` takes
`HPO_PLAN_TWO_ZONE=1` for this; its default is off, so the gate's payload is
unchanged. Control: `docs/img/make_card_figures.mjs` exits non-zero when the
two-zone render carries no dashed `house_temp` path, which is what a payload
silently reverting to one zone would produce.

**Where a figure's caption is a claim, the generator checks it.** The
demand-window figure's caption says the tank is held above the minimum inside a
frame; `docs/img/make_model_figures.py` refuses to write the figure if the plan
it read dips below it, using `dhw_schedule.hour_in_windows` to decide what
"inside" means. The measured values are printed beside the curve rather than
left to the reader's eye, because the crossing sits within a few pixels of a
frame edge. A figure whose caption cannot fail is a drawing, not evidence.

**Figure generators live in `docs/img/`, beside their output.** `docs/` is on
`tests/closure.py`'s `INERT` list, so a generator there needs no closure entry
and editing one selects no gate script. Under `tools/` a generator is an orphan
until `closure.py` names it, and `closure.py` is a `GATE_FILE`: classifying it
would force `MODE: FULL` on every documentation branch that touched the list.

**Still unfixed, and outside every lane item so far:** the `[![License: MIT]…](LICENSE)`
badge. Its cause is the "first `(` of the matched span" clause above, not — as
this paragraph said until #567's second review — a rule about link targets and
`.md` extensions: the span the rewriter matches runs from the wrapping `[` to
the *image's* closing `)`, so the first `(` in it is the image's own, and the
badge comes out of the HACS pipeline as
`src="https://raw.githubusercontent.com/tvofi/heatpump_optimizer/6.3.17/https://img.shields.io/badge/License-MIT-green.svg"`
— so the badge image itself does not load, not merely its link. Control: the
same badge with an **absolute** target renders correctly, so it is the relative
target that pulls the whole construct into one span. Reproduced on 2026-09-07
by rendering `README.md` through the pipeline. It needs a lane-B item; it is
not one today. A relative target also leaves the `<a>` with no `href` at all
(measured), which is a second, smaller defect on the same construct.

**Also stale, and also nobody's item:** `docs/architecture.md`'s outputs node
still reads `65 entities / 55 sensors, 4 binary sensors, 4 buttons, 1 switch,
1 climate`. It predates this programme (v5.1.0, #69), it is wrong at
`origin/main` today, and no check reads it — `tests/entities.py`'s census
covers `README.md` only. Extending that census to the architecture figure is
the obvious repair and is a lane-B item, not a side-effect of one.

**Delivery-status row.** No longer this PR's to add: #531 landed a truthed
`| UX |` row on `main` while #567 was in review, and the merge that brought it
here dropped #567's older duplicate in its favour — the newer copy is the right
one, per `delivery-status-tracking.mdc`. This PR therefore adds **no** row, and
carries B1–B5 and B6–B11 under that single existing row; a second one would be
the duplication the merge just removed.
