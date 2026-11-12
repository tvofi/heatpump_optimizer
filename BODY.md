R10-HOTFIX-CARD-HEALTH-TEXT, live defect on v7.1.11: the Health and Advisor labels lose their layout box when a content blocker's generic hide rules `##.adv-text` and `##.adv-label` (EasyList general hide; AdGuard Base, chromium and uBlock flavours) apply inside the card's shadow root. This PR renames every `adv-*` class in the card to `fact-*`, adds a browser-lane cell that injects those rules into the shadow root (failing first), and adds a static check in `tests/card.mjs` that refuses ad-list-prone class and id names. It also carries the earlier darkMode-false ink fix from this ref (560d2c569, d76f4d056, 75839015c), because that fix was already done and is green on the resumed ref. The card's class and id reader is `cardNames` in `tests/card_rig.mjs`. It has two consumers, `tests/card.mjs` and the harness, because the agreement lane refused a second copy of that grammar.

## Root cause

The RCA body is `handoff-body/r10-rca-card-health-text` at 03be2c7fbc50aecd6c17ce7a2456b651e1757326. Its first pass found the darkMode-false ink defect: the Health and Advisor rows draw `--hpo-text` on the darkMode-literal `--hpo-surface-2`, from 906fee95e (v7.0.5) onward. The ink commits on this branch fix it. Its second pass showed that ink defect cannot produce the owner's screenshot: the screenshot shows box-less labels, with the value at x=11. The orchestrator's third pass (THIRD-PASS.md) reproduced the owner's state in WebKit and Chromium. EasyList's generic `##.adv-text` (easylist.txt:9291 = easylist_general_hide.txt:7904) and `##.adv-label` (:7887 in easylist_general_hide.txt) are applied inside the shadow root. They remove the box of all 19 Health labels and hit 3 Advisor elements. Process state is (c) for the ink defect (themeMismatch's selector unit; RCA section 2). For the blocker defect the state is (a): no check read the card's class names against ad-list-prone names, and no lane rendered the card under a blocker's rules. The countermeasures are `blockerHide` (rendered) and the static name check (fast lane). Whether each real blocker reaches shadow roots is still being verified by the RCA seat. The rename holds either way.

Prefix choice: I checked each candidate prefix's names against every generic `##` rule in EasyList general hide (13631 rules), AdGuard Base chromium and uBlock flavours (version 2.5.3.82; 14005 and 14008 rules) and uBlock filters (45 rules), all fetched 2026-11-11 around 23:45Z. `fact-` names no rule, either alone or in a compound. Its stem is not ad-related. It also does not collide with the card's `--hpo-*` custom properties, which a `hpo-` class prefix would have done (a `/hpo-text/` search in tests/card.mjs would then read both). `hint-`, `tip-` and `lbl-` were also clean. They lost on meaning: Health rows are not hints.

Alternatives considered for the barrier: vendoring a filter list into the tree is refused (GPLv3 / CC BY-SA; brief). A live-list gate would make CI depend on the network and on a list that changes daily. The deny-stem pattern reads the tree alone, and `dev/audit/harnesses/r10_card_blocker_names.py` is the re-runnable instrument against the live lists.

Not carried, and why:
- Whether each real blocker (uBlock Origin, AdGuard, Safari content blockers) reaches a shadow root is still open with the RCA seat's third pass. The rename and both checks hold either way.
- The harness lists compound generic rules that touch a card name: `.panel.ad`, `.grid > .container > #aside-promotion`, and `.contentmovie > div[class^="ad"]` on `advisor-page`. Each needs a second class or an ancestor that the card's shadow root never has.

## Head

2f6188444316a9df45c714e934892140a8838855, merge base and origin/main 61afd4f2db10341ab9b86583944402b206eb4c78 at 2026-11-12T00:06Z.

## Mutation proof

- Rename reverted: the card file at 75839015c (`adv-*`), with this head's tests. `node tests/card.mjs` fails `no class or id in the card is a name generic ad-blocker hide rules target` and reads `1723 names read; ad-list-prone: adv-, adv-act, adv-basis, adv-est, adv-head, adv-inbox-row, adv-label, adv-note, adv-row, adv-sub, adv-text, adv-title, adv-unpriced-head, adv-value`. `blockerHide` fails `R10 every text-bearing element on every dialog page keeps a layout box with ##.adv-text ##.adv-label injected into the shadow root`, with 49 box-less elements (Advisor and Health `span.adv-text` / `span.adv-sub`).
- Ink fix reverted: main 61afd4f2's card in a 75839015c worktree, `themeMismatch` alone. It fails `R10 every own-text run on every dialog page clears 4.5:1` in both arms: 67 runs under 4.5:1, among them `advisor span.adv-text 1.24:1` / `1.11:1` and `setup button.layout-edit-toggle.on 2.95:1` / `2.32:1`.
- The deny pattern is driven over a generated spelling corpus. It has 7 stems × 3 cases × (bare + 2 separators × 5 suffixes) = 231 names that must be refused, and 241 near misses that must pass (a stem glued to a letter or digit, a stem inside a word, `advice-text`, `address`, `promote`, `fact-text`, ...). The check `the ad-list-prone name pattern refuses every stem spelling and no near miss` is ok. The extractor's own probe (`the card-name extractor reads class, id, className, classList and selector names`) is ok.

## Null control

`blockerHide`'s first arm is the same sweep without the injected rules. It is ok at main 61afd4f2's card, at 75839015c's card and at this head. So the injected-arm red at the base comes from the rules and not from the sweep. Its reach floor (≥5 pages, ≥20 text elements on Health, ≥3 on Advisor) is met at both ends: plan=81 setup=10 savings=22 advisor=46 health=59. At this head the injected arm is ok because the rules now match nothing. The harness at 61afd4f2 reads `class adv-label, class adv-text` targeted by a rule naming them alone in EasyList and both AdGuard flavours. At this head it reads none in all four lists. The static check is red at 75839015c's card and green here, as shown above.

## Figures

- 49 box-less elements under the injected rules at main 61afd4f2's card, and 0 here. Instrument: `blockerHide` in `node tests/card_browser.mjs` (CI `tests / browser`), measured alone through a scratch driver that calls only that function.
- 1723 names read at 75839015c's card, 14 ad-list-prone. Instrument: `node tests/card.mjs`, check `no class or id in the card is a name generic ad-blocker hide rules target`.
- Generic rule counts, list versions and per-list hits. Instrument: `python3 -I dev/audit/harnesses/r10_card_blocker_names.py 61afd4f2` and `... HEAD` (network; lists fetched at run time).
- 67 runs under 4.5:1 at main's card, 0 at 75839015c and here. Instrument: `themeMismatch` in `node tests/card_browser.mjs`.
- Full browser lane, `node tests/card_browser.mjs` (P9 grid `MODE: FULL`): `ALL BROWSER CHECKS PASSED` rc 0 at 75839015c, and with `HPO_PAGES_OUT=docs/img/card` at 0b86aacd1's tree.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` printed `MODE: SCOPED -- 12 script(s) run, 21 scoped out`. `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` ran them.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

none

## Unpinned sites

n/a: the diff adds no `custom_components/` predicate beyond class-name strings, and the static check and `blockerHide` read those strings by value.

## Forward-carry

none

## Friction

none
