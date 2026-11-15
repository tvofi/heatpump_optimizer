R11-PRE-PLAN-RENDER (part 1): the plan page shows every phase of the round.
Group R11-PRE-PLAN-RENDER, roster lane IN, size M; owner directive (tvofi, 2026-11-15): "Make the plan html show all phases in the round".
The round's phases are drawn from a tracked, linted per-round file, never from round-specific code.

Until now the plan page drew roster groups only. Between a round's start and its fix roster, it showed nothing of the round. This change adds `tools/audit/seat/plan_phases.py`, which owns the phases file, its refusals and its section. `plan_page.py` draws that section above the group lanes. Round 11's own file, `dev/programme/round11/phases.json`, holds the round's state as of 2026-11-15 13:00Z.

- The file is `dev/programme/round<N>/phases.json`: the round, `as_of`, and one entry per playbook phase (`dev/audit/README.md`, "Running a round: the playbook" and "Round start"). The phases, in the playbook's order, are round start, finders, verify and judge, the architect plan, fix waves, stamps and closure. Each entry carries a status (not started, running, waiting on a named thing, done), started and finished dates, an optional forecast window with its basis, entry and exit text, and items.
- The schema refuses: an unknown status or phase; a phase out of the playbook's order or repeated; `waiting` with nothing named; a date that is not ISO-8601 UTC; a started or finished date on a not-started phase; a finished date on a phase not done; and a forecast with no basis. `plan_phases.py --check FILE` exits 1 on any of them.
- The page draws a phase the file does not list as "not started", never omits it. A date the file does not carry is a dash. The page prints no date or count the file does not carry. Items are drawn under every phase not done.
- One page: the phases section plus everything `plan_page.py` drew before, unchanged (owner, 2026-11-15: "The generic plan page should support showing fixer groups as per normal in addition to the phases"). The phases are drawn on the swimlanes' own time axis (`plan_page.time_axis`, the one axis function both use). A phase reaching past either end is cut there and labelled, for example "since Sun 15 Nov 05:22"; a phase or forecast wholly off the axis is named in its row, not drawn. The section says that the fix waves are the group lanes below; the round-start items name their groups and do not repeat their lanes. The page renders in three cases: groups and phases; phases only (a roster with no fix group yet, as at a round's start); and groups only (no phases file, drawn exactly as before).
- `plan_page.py --phases FILE` draws the named file. Without it, the page draws the checkout's highest-numbered `dev/programme/round<N>/phases.json`. An invalid file draws its section as PHASES UNAVAILABLE and the rest of the page still renders. A checkout with no phases file draws no section, so the page is unchanged.
- The page names the file by its checkout-relative path, never a host path, so `plan_public.py`'s privacy refusal still passes on a page with phases.
- `plan_phases.py --phases FILE --html OUT` draws the section alone as a page in the plan page's stylesheet, for a round with no plan.json at all. The published page is `plan_page.py`'s, with both halves.

What the plan beat needs to pick the file up: nothing new. The beat's `plan-beat` row runs `state_docs.py --plan`, which runs `plan_page.py --repo <its checkout>`. Discovery reads `dev/programme/round*/phases.json` from that checkout's working tree, so the round-11 phases appear once the beat's checkout is at a main that holds this merge. Keeping the phases current is an edit to that file on main: the orchestrator's record step, like the roster.

Roster carries of R11-PRE-PLAN-RENDER, each named. Carry 0 (round filter), Carry 1 (next-round tab with its own preliminary Gantt), Carry 2 (the two-tab prototype as the model), Carry 3 (description, strip and lede counts), Carry 4 (PC-1113-05) and Carry 5 (plan-beat items P753 and P794) are the group's later parts, and this change leaves their text and scope as written. Today's behaviour is byte-identical with no phases file (measured below), the phases section is self-contained so a tab can host it unchanged, and no beat change is needed.

Carry 6 (the owner's directive to show every phase of the round) is built here, apart from two of its items that remain on the group for its next part. First, phase dates from the plan's duration model: this change takes dates only from the phases file, where a forecast must name its basis, and adds no constant and no duration. Second, the page for a round with no plan: this change renders a roster with no groups (the "phases only" arm), but `replan.py` refuses round 10's plan now that VERSION is 10.0.0, so the beat's page stays at its 06:19 snapshot until round 11's roster exists.

## No functionality of today's public page lost

Owner, 2026-11-15: "No functionality from the public plan version today should be lost". This is measured, not asserted.

- Today's public page is `git show origin/handoff/audit-r10-plan:handoff/round10/state/PLAN.html`, the newest state ref's page (state ref ef9c9068, snapshot 15 Nov 06:19 UTC, sha1 3d2752f7b784). It is what `plan_public.py stage` publishes now, because round 10's state ref is the newest.
- Its inputs: the plan.json the beat drew it from (generated.start 2026-11-15T06:19:00Z, roster blob 4b083262, sha1 edc40ce32bfd), the roster at commit 47364eb0 (the commit holding that blob), and one GitHub snapshot taken through `plan_page.fetch_github` (sha1 21875573ab86). The roster ref is a commit SHA, rendered with `--no-fetch` from a scratch clone that holds no phases file.
- The inventory instrument is `python3 dev/audit/harnesses/r11_plan_page_inventory.py BASE OTHER...`. It lists every heading, table header row, legend entry, filter control, element id, class name, data attribute, event listener, link shape and the chart-bar tooltip, with digit runs read as `#`. It then prints MISSING and ADDED per other page. Its null control is the public page against itself: `missing=0 added=0`.
- No phases file: origin/main's `plan_page.py` (b3831ff6) and this head's, on the same three inputs, give byte-identical pages. The check was `cmp mainx-nophases.html headx-nophases.html && echo BYTE-IDENTICAL`, which printed BYTE-IDENTICAL. Inventory, public page against this head with no phases file: `RESULT other=headx-nophases.html missing=0 added=0`.
- With `--phases dev/programme/round11/phases.json`: `diff` against main's page shows one hunk, `114a115,129`, which is the phases section inserted and nothing else changed. Inventory: `RESULT other=headx-phases.html missing=0 added=9`. The nine added items are the section's own: heading "Round # phases", the phases table header, `id: phases`, `data-phase`, and the classes forecast, items, nowline, open and phase.
- `plan_public.refusal` over the page with phases returns None, and `python3 -I tools/audit/seat/plan_public.py --self-test` prints "all checks passed".
- Self-test arm "groups and phases: the page is the groups-only page plus the phases section, every section, table and control of it kept" asserts `both.replace(section, "", 1) == groups_only`. Mutant `phases-keep-groups-page` drops the Flow section when phases are present, and is killed.

<details><summary>Today's public page, inventory (94 items, by kind)</summary>

- class: alerts; bar; barlab; blk; blocked; chip; chk; closed; closelab; closeline; closer; cpnote; d; done; end; filters; g; grid; grp; held; issarea; lane; lanec; lanelab; legend; live; mono; note; occ; pill; ready; scroll; slotcap; st; stamplab; stampline; stat; strip; sub; tick; tier; tip
- data attribute: data-eta; data-f; data-name; data-part; data-st; data-start; data-state; data-wave
- filter: all; blocked; done; held; live; partial; ready
- heading h1: Round # Fix Plan
- heading h2: Flow; Groups; How the ETAs are computed; Planned stamps; Projected open issues; Swimlanes; Waves
- heading h3: Bottlenecks (#); Critical-path lane (# groups, the plan's full set); Flow metrics (to #-#-# #:#:#+#:#); Merge-wait per PR, # h (merge verdict to merge); Train skips per batch (latest #)
- id: hide-done; rows; tip
- legend: critical path (◆ marks each link); fixer working; groups in flight above the #-slot cap line; held; part merged; planned stamp; ready; waiting
- link: https://fonts.googleapis.com/css#?family=Barlow+Condensed:wght@#;#;#&family=Source+Sans+#:wght@#;#&family=JetBrains+Mono:wght@#;#&display=swap
- listener: change; click; mouseenter; mouseleave; mousemove
- table: Batch (UTC) | Skipped | Why | State; Group | Description | Status | Tier | PR | Issues | Blocked by | ETA (UTC) | Wave; Group | Status | PR | ETA; PR | Kind | Wait | Verdict at merged head; Version | Projected (UTC) | Carries | Kind; wave | opens (UTC) | last merge (UTC) | groups | stamp it cuts
- tooltip: chart bar title
</details>

Classification: `plan_phases.py` joins `tests/entities.py`'s recorded closure beside `plan_page.py` (`tests/closure.py` INERT_EXCEPT and `tests/closures.json`). The reason: `state_docs.py`'s self-test runs `plan_page.py`, which imports it. The same route was taken for `topic_grammar.py`. The phases file is classified in `tests/layout.json` as `dev/programme/round*/phases.json`. It stays inert under the `dev/programme/` prefix, because no gate script reads a real phases file: the self-tests use fixtures in a throwaway checkout.

## Head

c0db6bce48c5c8bafc1f1b3bc6d8cf4d33397443, repair of the reviewed head 2aff0cc4fe (verdict/3622: class-open). Delta from the handed-off head 8f53d88d7a is the type-check below; `git merge-tree --write-tree origin/main HEAD` reported no conflict.

## Class repair: a file `--check` accepts is a file the page draws

Defect (reviewer): `plan_phases.violations` left text fields untyped, so a phases file `--check` accepts crashed `plan_phases.section` (reached from `plan_page.render`, `plan_page.py:710`). The instance was `entry: 5`. Measured at the prior head, driving the old validator over every node of a full file with junk values: `entry`, `exit`, `detail`, `note`, `basis` and `waiting_on`/`name` as numbers or lists crashed `html.escape` (AttributeError), and a list, dict or `{}` as `status` or `phase` crashed `violations` itself (TypeError: unhashable), as did `items` not a list (not iterable).

Fix, one owner: `plan_phases.violations` types every text field the section prints (`_TEXT_DOC`, `_TEXT_PHASE`, `_TEXT_ITEM`; a forecast's `basis` and an item's `name` with their presence checks), `items` as a list and `status` as a string before it is a dictionary key. Alternative not taken: `str()` or `html.escape(str(x))` at the draw sites. It would turn a number into text silently and leave `violations` crashing on an unhashable status; refusing at the file is the one place the contract lives.

Enumeration rule (fixer.md step 8): the census `_census` in `plan_phases.fixture_checks` takes every node of a fully populated phases file (`_nodes`, not a list of field names) and replaces it with each of the ten junk values `_JUNK`; each result either earns a violation or draws in `section` (with the plan page's axis and without), and `violations` never raises. It asserts that the fixture populates every field the section reads, so a field the section starts reading has to be in the fixture. Every node the rule returns is closed: the count is asserted equal to `len(_JUNK) * (nodes - 1)` in the check "phases census: null control" (the number it ran is in its `got`, not carried here).

`as_of` in `dev/programme/round11/phases.json` is not refreshed: it records the orchestrator's state as of 2026-11-15T13:00Z (items such as the pull request and card counts), and a seat refreshing the date without re-measuring each item would make the file say something unmeasured. Carry: dismissed: the phases file is the orchestrator's record step, as stated above.

## Mutation proof

Failing first: with the self-test arms written and `plan_page.py` not yet integrated, `python3 tools/audit/seat/plan_page.py --self-test` exited 2. The error was `plan_page.py: error: unrecognized arguments: --phases ...`: the check "--phases FILE: the page draws the round's phases above the group lanes" could not pass.

Driver `dev/audit/harnesses/r10_plan_page_mutants.py`: one mutant per new predicate (the `phases-*` entries), including the three-case predicates `phases-drawn`, `phases-keep-groups-page`, `phases-shared-axis` and `phases-discovered`. Each mutant applies one exact replacement, runs `plan_page.py --self-test`, and restores the file byte for byte:

```
RESULT mutant=M0 rc=0 fails=0 verdict=null
RESULT mutant=phases-unknown-status rc=1 fails=2 verdict=killed
RESULT mutant=phases-waiting-named rc=1 fails=2 verdict=killed
RESULT mutant=phases-unknown-phase rc=1 fails=1 verdict=killed
RESULT mutant=phases-order rc=1 fails=2 verdict=killed
RESULT mutant=phases-iso-date rc=1 fails=1 verdict=killed
RESULT mutant=phases-not-started-date rc=1 fails=1 verdict=killed
RESULT mutant=phases-finished-not-done rc=1 fails=1 verdict=killed
RESULT mutant=phases-forecast-basis rc=1 fails=1 verdict=killed
RESULT mutant=phases-unlisted-drawn rc=1 fails=3 verdict=killed
RESULT mutant=phases-items-under-open rc=1 fails=1 verdict=killed
RESULT mutant=phases-waiting-label rc=1 fails=2 verdict=killed
RESULT mutant=phases-forecast-basis-shown rc=1 fails=1 verdict=killed
RESULT mutant=phases-unavailable rc=1 fails=1 verdict=killed
RESULT mutant=phases-newest-round rc=1 fails=2 verdict=killed
RESULT mutant=phases-no-host-path rc=1 fails=2 verdict=killed
RESULT mutant=phases-drawn rc=1 fails=6 verdict=killed
RESULT mutant=phases-shared-axis rc=1 fails=1 verdict=killed
RESULT mutant=phases-keep-groups-page rc=1 fails=1 verdict=killed
RESULT mutant=phases-cut-off-axis rc=1 fails=1 verdict=killed
RESULT mutant=phases-cut-since rc=1 fails=1 verdict=killed
RESULT mutant=phases-forecast-past-axis rc=1 fails=1 verdict=killed
RESULT mutant=phases-now-on-axis rc=1 fails=1 verdict=killed
RESULT mutant=phases-discovered rc=1 fails=2 verdict=killed
RESULT survived=0
```

## Null control

- M0 in the same driver: nothing replaced, `rc=0 fails=0 verdict=null`.
- In `plan_page.py --self-test`, "null control: a checkout with no phases file draws no phases section" and "null control, groups only: no phases section, nothing of the phases drawn". A round whose file is absent renders the page as before; the byte comparison above measures the same thing against main.
- In `plan_page.py --self-test`, "null control, phases only: the same empty roster with no phases file draws none".
- In `plan_page.py --self-test`, "phases: null control, an axis holding every date cuts and omits nothing".
- In `plan_page.py --self-test`, "phases: the fixture is sound (null control)". The fixture covers every status on a phase and on an item, plus a forecast with its basis, and has no violation, so each refusal check is driven by its one mutation.
- In `plan_page.py --self-test`, "phases: null control, a checkout with no phases file discovers none".

## Figures

- `python3 tools/audit/seat/plan_page.py --self-test`: `plan_page self-test: 133 checks, 0 failed`
- `python3 tools/audit/seat/plan_phases.py --check dev/programme/round11/phases.json`: exit 0, nothing printed.
- `python3 -I tools/audit/seat/plan_public.py --self-test`: `plan_public self-test: all checks passed`
- `python3 tools/audit/seat/state_docs.py --self-test`: `state_docs self-test: all checks passed`
- `python3 dev/audit/harnesses/r10_plan_page_mutants.py M0 <the phases-* names>`: `RESULT survived=0`: 23 mutants killed, M0 null

Class-repair proofs, drivers in the same directory. Failing first: the census ran against the prior head's `violations` (new census, old validator, in place) and failed with `no accepted file crashes the section, no check crashes`, first cases `(('phases', 0, 'status'), [], 'TypeError')` and `(('phases', 0, 'entry'), 5, 'AttributeError')`; with the fix `plan_page self-test` reads 0 failed.

```
RESULT mutant=phases-unknown-status verdict=killed   (isinstance guard removed with the membership test)
RESULT mutant=phases-status-unhashable verdict=killed (the isinstance(st, str) guard alone)
RESULT mutant=phases-text-typed verdict=killed       (_text_violations predicate)
RESULT mutant=phases-items-list verdict=killed       (items not a list)
RESULT mutant=phases-item-name-text verdict=killed   (name typed)
```
The first run of `phases-item-name-text` SURVIVED because `name` was typed twice (in `_TEXT_ITEM` and in the presence check); `name` left `_TEXT_ITEM` and the mutant is then killed. `phases-waiting-named` and `phases-forecast-basis` were re-anchored to the new text and are killed.

<!-- figure-block: scope-line mb=26dbf7c43ec3742101398b098dbdcc61bbee8f19 head=c0db6bce48c5c8bafc1f1b3bc6d8cf4d33397443 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Red checks

- `governance / instrument-self-tests`, step "Show the self-tests outside tools/audit/seat/ refusing their own fixtures" (head job 132899024683, red at the prior head; the base job failed a different step).
  - Cause: this PR adds `dev/programme/round11/phases.json`, a tracked path that `python3 -I tools/audit/check_scopes.py --self-test --repo .` found in no scope universe and not in `_coverage_excluded` (`FAIL coverage ... unclassified=1`; its live-scopes arms then read False). The step's other fifteen commands pass at the prior head (run each locally).
  - Fix: `phases.json` is round-state data of the same kind as `round9/` and `round10/` state notes, so `round11` joins their glob in both lists; no self-test was changed.
  - Runs, `python3 -I tools/audit/check_scopes.py --repo .` (coverage line) and `--self-test --repo .`: prior head a0d587549a `FAIL coverage tracked=11256 ... unclassified=1`, `in no universe and not excluded: dev/programme/round11/phases.json`, self-test rc 1 (`SELF-TEST FAILED`); merge base 26dbf7c43e `ok coverage ... unclassified=0`, rc 0; head 8f53d88d7a `ok coverage tracked=11256 ... unclassified=0`, `SELF-TEST passed (every perturbed scope refused)`.
  - Process state: (c). The prior handoff's prepr and its `ci_predict` ran and passed, but `ci_predict` reads a data file only when a changed file's own self-test reads it (its own line says so), and `check_scopes.py` was not in this diff's closure. Cheaper detector: `check_scopes.py --repo .` runs in seconds and is not in prepr. Recording no countermeasure here: a prepr step is a policy-adjacent change owed an owner's decision, and one instance does not meet the class threshold.
- `tests / fast (3.14)`: named because the body lint lists it red among the PR's checks; the check run at the pull request's head 0b9f5cbf24 (job 132899195719, run 43742580872) concluded success, so no failure of it is attributable to this branch's commits. Cheaper detector: none needed; it is the gate itself (a pass is the standing result).

## Forward-carry

none

## Friction

none
