Fix review: merge 2a579f5794bef0d817a077ad1603859c070c9931

bus-nonce: 95e6b95f8cf226176e251f4293e64798

Round 3 of #2452 (R10-DEEPLINK-HANDLERS). Measured head
`2a579f5794bef0d817a077ad1603859c070c9931` (unchanged when this verdict was
pushed). The fixer's handoff is `dd74b93f`; the reviewed head is the relay's
recarry of it onto main, and `git diff --stat dd74b93f HEAD -- tests/card.mjs
tools/audit/seat/r10_deeplink_mutants.py dev/programme/rosters/wave-r10-groups.json`
is empty, so the handoff's three authored files are byte-identical here.

## RESULT lines (my own runs)

Base worktree at `8b3ea42c`, head worktree at `2a579f57`, each with the head's
`tools/audit/seat/r10_deeplink_mutants.py` and its own `tests/plan_view.py`
payload written first (`rc=0` in both). Every driver process printed
`restored`; `git status --short` over the card and `tests/card.mjs` is empty
after the runs.

    RESULT null-control head   NULL_no_plant                                  rc=0 fails=0
    RESULT pair-1 base         REV_CAP1_location_captured_at_load             rc=0 fails=0
    RESULT pair-1 head         REV_CAP1_location_captured_at_load             rc=1 fails=1
    RESULT pair-2 base         TMX_history_back_eighty_timeouts_deep          rc=0 fails=0
    RESULT pair-2 head         TMX_history_back_eighty_timeouts_deep          rc=1 fails=1
    RESULT pair-3 base         REV_XL1_svg_xlink_href_markup                  rc=0 fails=0
    RESULT pair-3 head         REV_XL1_svg_xlink_href_markup                  rc=1 fails=1
    RESULT x-pair-1 alone      X34_card_loads_before_the_surface              rc=0 fails=0
    RESULT x-pair-1 paired     X34CAP4_load_order_is_what_closes_REV_CAP4     rc=0 fails=0
    RESULT x-pair-2 alone      X35_settle_cap_drops_silently                  rc=0 fails=0
    RESULT x-pair-2 paired     X35TMX_cap_refusal_is_what_closes_TMX          rc=0 fails=0
    RESULT class-probe base    PROBE_CAP_SI_set_interval_captured_at_load     rc=0 fails=0
    RESULT class-probe head    PROBE_CAP_SI_set_interval_captured_at_load     rc=1 fails=1

Three of the sixteen before/after pairs re-derive as the body states: green at
`8b3ea42c`, red at the head. Two X-pairs re-derive as "only closes paired":
the isolating X plant alone is green, and the pair with the plant its line
closes is green too, so the line, not the plant alone, is what catches it.
`X35TMX`'s head FAIL is `no press throws ... deferred work had not settled
after 64 rounds`; `X34` alone passes all 1,260 checks.

## Class rule (fixer.md step 8; fix-review.md step 6)

The body's round-3 rule: every global the census records through is one graph
installed before the card loads. Read at the diff (`8b3ea42c..HEAD`): the
graph is built above `vm.runInContext(cardSrc, ctx)`, and the census switches
it on through `navHook` rather than replacing members, so a reference the card
took at load is the recorder. `CAP5-CAP13` and `REV_CAP1-4` plant one member
kind each (document.write, the element factory, CustomEvent, setTimeout, the
registration method, the Navigation API, the History prototype, the location
descriptor, a window alias; history, open, location).

Five members of planted kinds are not individually planted: `setInterval` /
`clearTimeout` / `clearInterval`, the plain `Event` class,
`createElementNS`, the window and document `addEventListener` sites, and
`window.window` / `self` / `defaultView`. Each is in the diff, so none is
`class-open` under the contract's clause. **This probe is mine, not the body's**:
I planted a load-time `setInterval` capture whose callback calls
`history.back()`, and it is red at the head (`every link the census records
from a press is one haLink builds for this entry`, `history back` recorded
against the keydown drive) and green at the base. The mechanism closes the
kind, not only the planted member.

## Red checks (defect-root-cause.md's second trigger)

`nightly-status` is red at this head and is not this pull request's. The job's
report is `NIGHTLY FAILED: slow failed last night`, scheduled run
`39387919507` at head `0c298f6`, job `slow` failure. The diff touches none of
`tests/nightly_status.py`, `tests.yml`, `governance.yml`, the plan or
`HANDOVER.md`, and the only row it adds is its own
`dev/programme/delivery/2452.md`.

`pr-contract` is green at this head (runs 118644092804 and 118644343217). Its
earlier red at `b69ac5c16` (job 118349952504) is named and answered in the
body's `## Red checks`; I re-derived its figure:
`python3 -I tools/audit/carry_audit.py check --body BODY.md` prints
`9 finding item(s): 9 routed, 0 unrouted, 0 bad destination(s)`. CI's own
red-history walk over the 20 commits prints `every failure conclusion across
them: nightly-status`, and that walk excludes `pr-contract` itself.

`mutation` is green with an empty scope:
`MUTATION TABLE -- scope changed: no production code line added or modified
against the base`. It draws no mutant, so the green says nothing about this
fix; the plant sweep is the proof and is re-derived above.

## Gate and claims, from CI at this head

`MODE: SCOPED -- 3 script(s) run, 30 scoped out`, naming `tests/plan_view.py`,
`tests/card.mjs` and `tests/card_drift.mjs`; `7 TEST SCRIPT(S) PASSED`, with
`ALL CARD CHECKS PASSED`, `ALL 124 closure shrink pins PASSED`, `ALL 109
HARNESS HEADER CHECKS PASSED`, `env_drift.py --claims-only` ok. `coverage`,
`coverage-ratchet`, `closures` and `fast (3.14)` are the lanes that conclude
the same. `node tests/card_drift.mjs a2b25bbc5` here, and CI's run against
`76bb4562`, both print `identical in all 40 states`. `VERSION`, the manifest
version, the notes heading, both claim files, `tests/dom_stub.mjs` and the card
are untouched by the three-dot diff. `git merge-tree --write-tree origin/main
HEAD` exits 0 with no conflicting path.

## Carries

`dev/programme/rosters/wave-r10-groups.json` is in this diff, and at this head
the three briefs R10-ADVISOR, R10-SCORES and R10-UX-HEALTH carry the census
terms with the control stated as a precondition: `Control, re-measured at your
merge base: ... RV1_history_bracket_back_in_undriven_keydown
RD8_insert_adjacent_html_built_href_driven_residual reads RV1 red and RD8
green`. `carry_audit.py` reads 9 items, 9 routed, 0 bad destinations.

## Notes (non-blocking)

- The body's `## Figures` says the three-dot diff is 3 files, 928 insertions,
  335 deletions and that `git diff --name-only origin/main HEAD` names the same
  three. At the measured head the three-dot is 4 files, 929 insertions, 335
  deletions: the fourth is `dev/programme/delivery/2452.md` (one line), and the
  two-dot names 84 paths because main has since taken #2465. The body also says
  `a01006c1b` is not in the head's ancestry; it is. The substantive claim -- the
  recarry reverted no authored file -- is true and I re-derived it directly.
  Carry: dismissed: the head the body's `## Head` names is the head reviewed,
  the extra path is the orchestrator's own delivery row, and round 4 owes the
  re-cut regardless.
- `Carry: R10-ADVISOR (roster 04a641598)` names a SHA that does not carry the
  text: at `04a641598` none of the three briefs contains the census carry (it
  is an ancestor; the text lands through the roster commits this branch
  merges). Carry: dismissed: the destination finding-propagation.md names, the
  roster file in this diff at the reviewed head, does carry it.

## Not verified

I re-derived 3 of the 16 before/after pairs end to end and 2 X-pairs; I did not
re-run the full 228-plant sweep (the brief scoped me to a subset), nor the
1,260-ok-line count. The finder's original plant scripts (`rev_plants.py`,
`mut*.py`, `review_plants*.py`, `own_plants.py`) are not in the tree, so the
driver's "verbatim" is its own label: `tools/audit/seat/r10_deeplink_mutants.py`
is committed and names each round's provenance, but I did not diff it against
the out-of-tree originals. `closures` was the last run at this head; it
concluded `success` at 13:49:13, so every run had concluded when this verdict
was pushed.

Round 3, so `fixer.md`'s re-cut rule does not yet bind. The body is cumulative
(rounds 1-3) and each round section states its change and its measurement; I
did not find it repairing rather than describing.
