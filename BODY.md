`tests/card.mjs`'s link census (R10-DEEPLINK, #2283) checks that the card's
routes out go through `haLink` and `navigateTo`. One declared surface
(`NAV_SURFACE`) is read by two arms. The static arm refuses the spellings of
surface names that its rows name, anywhere in the card's code outside
`navigateTo`. The dynamic arm presses every element the shadow root wires to a
click, records each instrumented surface member by name, and reads
`href`/`action`/`formaction` off the markup after every press. A reach check
compares the census's `ACTS` with every `act` branch the source dispatches,
in both directions, and requires each one pressed.

This pull request is narrowed to what that census pins (the orchestrator's
split ruling on the round-8 review). It does not close every written
navigation. **Residual, exactly**, in two parts.

1. **Undriven handlers.** Navigation written in a handler the dynamic arm does
   not drive (keydown, pointer, wheel, focus) is covered only in the
   spellings the static rows name.
2. **A form outside the shadow root, in any press.** The dynamic arm reads
   markup in the card's shadow root only. A form appended outside it
   (`document.body`) and submitted by a button's `click()` therefore passes
   both arms even inside a press the census drives. The round-9 review's
   `RD4`, in the advisor:settings press, is that witness, green by design.
   `RD5`, the same form appended in the shadow root, is its red control.
   Closing this needs a document-level read or a form-submit instrument,
   which is R10-DEEPLINK-HANDLERS's brief.

For part 1: The round-8 review's RV1-RV7 are the
witnesses, and the driver now carries them green by design beside the red
controls RV1c and RV5c:

- `history["back"]()`;
- `history?.back()`;
- a destructured `back`;
- a `createElementNS` form, submitted by a button's `click()`;
- `.action = <variable>`;
- a quoted `"action"` key;
- a bare `createElementNS` form.

A name built at run time in such a handler passes too. So does a write through
a selector the stub DOM cannot resolve (`Y1`, green, beside `R7c`, red).
Closing those is R10-DEEPLINK-HANDLERS's job: drive those handlers the way
clicks are driven.

What lands:

- Static rows for `open` and its `.call`/`.apply`/computed-key/Reflect forms,
  `history.<member>`, `createElement("form")`, and an `action` written through
  `setAttribute`/`setAttributeNS`/`createAttribute`, `Reflect.set`,
  `Object.assign` with a bare key, a computed key or a literal member write.
  Also `.submit`, `.requestSubmit`, `["submit"]` and `.submit.call(`.
- The click-driven dynamic arm and the reach check.
- The driver's plants, including `T1c`/`T2c` (a press that throws or rejects
  only inside the census), and the `F2` control repaired so it no longer
  declares an act branch.
- Two card renames, both behaviour-neutral, so the census's `open` name no
  longer collides:
  - the setup fold's `b.open` is `b.foldOpen`;
  - `SlotModel.runsFrom`'s local accumulator `open` is `run` (`d3513acc8`).
  The card is a hot file outside this group's `files`; these renames are the
  only card changes.

Part of #2317.

## Head

`b7e2ee65400581ae7b7b87adb223f800fe853157` is the code head every figure below was measured at. Its merge base
with origin/main is `52f698905868c9140ed213ea542c44053fca7096`. It is the
round-8 reviewed head `ee409c81d` plus these commits, the round-9 reviewed
head `e9e6b99b3` among them:

- a merge of origin/main;
- `b678c7d16`: the Residual paragraph, the driver docstring and the RV plants,
  and the four carries;
- a merge of origin/main;
- `b7e2ee654`: the form-outside-the-shadow-root case in the Residual
  paragraph and the four carries, and `RD4`/`RD5` in the driver.

Both commits change comments, the driver and roster text only; no census
check changes.

The driver docstring previously said X3-X13 alone are red and X7K1b red as a
crash. Measured, only X1 and X2 alone are red, and X7K1b is red on `no press
throws`; the docstring now says so.

## Mutation proof

Every plant is one mutation applied by
`tools/audit/seat/r10_deeplink_mutants.py`, which restores the file byte for
byte and refuses to start on a dirty tree. At this head, the residual's
witnesses and their controls:

    python3 tools/audit/seat/r10_deeplink_mutants.py RV1_history_bracket_back_in_undriven_keydown RV2_history_optional_back_in_undriven_keydown RV3_history_destructure_in_undriven_keydown RV4_form_ns_action_member_button_click_in_undriven_keydown RV5_action_member_to_variable_in_undriven_keydown RV6_object_assign_quoted_action_key_in_undriven_keydown RV7_create_element_ns_form_in_undriven_keydown RV1c_history_dot_back_control RV5c_action_member_to_literal_control

`RV1`-`RV7` each `rc=0 fails=0`, the residual. `RV1c` and `RV5c` each
`rc=1 fails=1` on `no navigation token in the card's code outside
navigateTo`: the same position in the spelling a row names is red, so each
witness is one spelling away from a refusal. These were run in two detached
worktrees at this head, as two halves of the same list.

The round-9 driven-press pair, at this head: `python3
tools/audit/seat/r10_deeplink_mutants.py
RD4_form_ns_action_member_button_click_driven
RD5_action_member_to_variable_on_rendered_form_driven` prints `RD4` `rc=0
fails=0`, the residual's second part, and `RD5` `rc=1 fails=1` on `every link
the census records from a press is one haLink builds for this entry`.

The rows this pull request pins are the review's sample at `ee409c81d`, whose
card, census and driver plants are this head's apart from the comments and
added plants in `b678c7d16` and `b7e2ee654`:

- red: `V3`, `V8`, `V13`, `K1`, `K2`, `K3t`, `K5`, `Z2`, `Z3`, `T1c`, `T2c`,
  `R7c`, `X7K1b`, `X1K5b` and `X2`;
- green: `F1`-`F4`, `X12V8`, `X10V2`, `Y1`, `X3`, `X7` and `X8`.

This seat's full 109-plant sweep at `778ae2565`, an ancestor whose card and
census checks are this head's, read 76 red with a FAIL line and 33 green, with
0 crashes. The 33 green are the X* deletions alone, the X* pairs, `F1`, `F3`,
`F4` and `Y1`. `F2` read red there, and its repaired form is green in the
review's sample.

## Null control

`python3 tools/audit/seat/r10_deeplink_mutants.py --null` prints `RESULT mutant=NULL_no_plant rc=0 fails=0` at this head.
`node tests/card.mjs` prints `ALL CARD CHECKS PASSED` with 1257 `ok` lines
and 0 `FAIL` lines.

## Figures

- `node tests/card.mjs` at this head, after `PYTHONPATH=tests/hastub python3
  tests/plan_view.py`: `ALL CARD CHECKS PASSED`, 1257 `ok`, 0 `FAIL`.
- `node tests/card_drift.mjs 52f698905868c9140ed213ea542c44053fca7096`: `card_drift: identical in all 40 states`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff 52f698905 --workdir <dir>`:
  `MODE: SCOPED -- 9 script(s) run, 24 scoped out`, which names `tests/card.mjs`,
  `tests/card_drift.mjs` and `tests/plan_view.py` (run here) among its nine. The other scripts it names are left to CI's required runs on
  this head.
- Claim files, `VERSION`, the manifest version and the `RELEASE_NOTES.md`
  heading are untouched: `git diff --stat 52f698905...HEAD --
  tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION
  custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md` prints
  nothing.

## Red checks

These are the latest run per name at each earlier branch head, from the
check-runs API.

- `fast (3.14)`, red at `e59b1fb54` (job 117464541848).
  - **Failure:** `tests/card.mjs` failed on the `b.open` lines that an
    origin/main merge brought in.
  - **Fix:** closed by the `b.foldOpen` rename.
  - **Cheaper detector:** the scoped gate, re-run after each main merge before
    the push (`fixer.md` step 6). It costs one `card.mjs` run, about 30 s on
    CI.
- `pr-contract`, red at `e59b1fb54`, `485d0aa81` and `1d45350ba`.
  - **Failure:** at `e59b1fb54` it refused a body that did not name `fast
    (3.14)`.
  - **Cheaper detector:** `tools/pr/prepr.sh`, which this body passes.
- `wave-script`, red at `1d45350ba` (job 117250605987).
  - **Failure:** `AGREEMENT REFUSED`. The census had copied
    `tests/doc_claims.py`'s identifier grammar `[A-Za-z_$][\w$]*` unregistered.
  - **Fix:** `1fc6ce693` replaced it.
  - **Cheaper detector:** `node tools/policy/agreement.mjs --only discovery`,
    0.3 s, before each push that touches a governance code file. It was not
    run before that push.
- `coverage-ratchet`, red at `485d0aa81` (job 117397081517).
  - **Failure:** module floors on `coordinator.py`, `early_cutoff.py`,
    `sysid.py` and `price_model.py`. None of these is in this branch's diff,
    which at that head was the roster, `tests/card.mjs` and the driver. The
    red came from CI reusing a stale coverage base.
  - **Cheaper detector:** none at the branch's level. #2349 (`1138a4ef5`) is
    that class's root cause and backstop, and it is an ancestor of this head.
- `delivery-status`, red at `e59b1fb54` (job 117464452564).
  - **Failure:** not a required context. It listed other pull requests'
    overdue record rows.
  - **Finding:** none for this branch.

## Forward-carry

- **`dev/programme/rosters/wave-r10-groups.json`, in this diff.** R10-UX-SETUP,
  R10-ADVISOR, R10-SCORES and R10-UX-HEALTH each carry the census's refusals
  at their exact scope. They name the spellings the rows refuse, and say that
  navigation in a handler the dynamic arm does not drive is not covered
  (RV1-RV7). They also say to write none there until R10-DEEPLINK-HANDLERS
  drives it. In any press, they say a form appended outside the shadow root
  and submitted by `click()` is not covered either (RD4 green beside RD5
  red): append no form there. Each points to R10-DEEPLINK-HANDLERS's brief.
- **R10-DEEPLINK-HANDLERS's brief**, on the orchestrator's roster branch
  (`f51fe8a30`, which already names RV4's document-level read or form-submit
  instrument). The constraint it carries:
  - Drive every keydown, pointer, wheel and focus handler the card registers,
    through the instrumented surface, as clicks are driven.
  - Its controls are the driver's RV1-RV7 and `Y1`, green at this head. Each
    of RV1-RV7 must go red when its handler is driven. RV1c and RV5c stay red.
  - `RD4` must go red under the document-level read or form-submit
    instrument. `RD5` stays red.
  - Then the static arm can drop to bare-name rows only, with no spelling
    list (fixer.md step 17, #1874).

## Friction

- `fixer.md: cost: three review rounds each found a written spelling the static arm missed (open.call, the programmatic form, history["back"]); the spelling-row design was the step-17 shape the contract warns against, and only the split ruling stopped it.`
