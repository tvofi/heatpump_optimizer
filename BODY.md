R10-I18N-DE: German as a third UI language beside English and Swedish, through the two i18n mechanisms the tree already has: `translations/de.json` key-for-key with `en.json`, and a `de` dictionary in the card's `STRINGS` table key-for-key with `en`. No new mechanism. The per-language production tables that already had `sv` (`narrative.TEMPLATES`, `topology._TRANSLATIONS`, `config_flow.PRESET_WARNING`) gained `de`. Every check that pinned en/sv parity now iterates the shipped catalogues (`tests/harness.py`'s `SHIPPED_LANGS`, derived from the files under `translations/`) or `Object.keys(STRINGS)`. The docs that list UI languages name German.

This resumes the stopped fixer's work on `handoff-wip/r10-i18n-de` at `ddd0ce25`. That work was never handed off. This pass merged `origin/main` (one docstring conflict in `tests/deployment_shape.py`) and added only what the group still lacked:

- **Card strings.** The 18 `whynow.*` keys main added since the stopped fixer's base (R10-WHY-NOW-WIDGET) now have German text. Before this, `tests/card.mjs`'s every-language parity check was red on them.
- **Tests.** Four checks were widened.
  - The why-now key-twin check compared `en` with `sv` only. It now compares `en` with every card language.
  - The setup-text, narrative and `reasons.scheduled` language checks in `tests/features.py` were floors (`>= {"sv","de"}`, `>= 3`, `>= 2`). They now equal the shipped catalogue set.
  - A German why-now render check was added beside the Swedish one.
- **README claims.** The `title` option row in `docs/dashboard-card.md` now names `Wärmepumpenplan`. README.md, docs/how-it-works.md, docs/architecture.md and docs/index.html already named German at the merge base of this pass.
- **Terminology.** Each concept now has one German term across the catalogue and the card:
  - Flüstermodus for the pump's silent mode (it had been Silent-Modus, Flüstermodus and Leisebetrieb);
  - Ruhezeiten for its windows (it had been Ruhezeiten and Leisezeiten);
  - Feiertag for the calendar-driven holiday profile (it had been Urlaub beside Feiertag);
  - Mindestleistung / Maximale Leistung / Leistungsaufnahme for the power-limit fields, which the config and options flows had worded differently.
- **A red check this branch caused.** `tests/entities.py`'s `--anchor` fixture was pinned to `topology.py:_tr RETURN_DEL 25b21b2f`, a ledger row the stopped fixer's rewrite of `_tr` retired. The fixture now names the live row `86fae85d`. See `## Red checks`.

German address is the informal *du* that Home Assistant's own German UI uses. Every "Sie" left in the catalogue is the third-person pronoun. Wire values stay untranslated, as the card's i18n header states: entity ids, config keys, service and attribute names, reason codes and enums.

Terminology was spot-checked against Home Assistant core's shipped German strings: `homeassistant/components/{climate,water_heater}/translations/de.json` from the `homeassistant-2026.11.0` wheel (core's git tree holds only English `strings.json`). Core uses Abwesend, Komfort, Eco, Boost, Ist-/Soll-Temperatur, Sollwert and Wärmepumpe. The catalogue uses the same words. Core's `hvac_action` label for defrosting is "Enteisung". The catalogue uses Abtauen, which is the manufacturers' term the brief names. The catalogue has no Sperrzeit concept: `en.json` has no utility-lockout field.

**Left alone, by design.** `name_match.SYNONYMS` and `grid_fee`'s month and day parser accept English and Swedish input words. They parse user-typed input and entity names; they are not UI text. German examples in `de.json` keep the English input grammar (`Nov-Mar Mon-Fri`), which is what the parser accepts. `tests/card_browser.mjs`'s P9 layout grid stays `["en", "sv-SE"]`. It is a render-overflow sweep, not a parity check, and no scope selects it.

**Carry 1 (c7e2fe29).** This is the German label for r10-min-power-floor's new option. That group is unmerged (`handoff/r10-min-power-floor`), so its key is not in `en.json` at this base and cannot be translated here. The existing `heat_pump_min_power` labels were harmonized (see above). Whichever of the two pull requests merges second is refused until the German leaf exists. The refusal comes from `tests/entities.py`'s "de.json has exactly strings.json's keys" and `tests/card.mjs`'s every-language parity check.

## Head

f9db7d7a01dd9bf2877d3a0845562f2004ecbc8e, merge base 73365699a135fb813a43380096b6776d57f8ff4c. Per the owner ruling of 2026-11-07, `origin/main` was not re-merged after the first clean prepr. `git merge-tree --write-tree origin/main HEAD` reported no conflict at the handoff.

## Mutation proof

- **Card strings.** On the merged tree without the 18 German `whynow.*` keys (commit `763820d8a` reverted in a stash), `node tests/card.mjs` failed two checks: "every card language is key-for-key with en and keeps en's placeholders" and "and a planted missing key, dropped or unlisted extra placeholder, or extra key in any language fails it (null controls)". The run printed `2 CARD CHECK(S) FAILED`. With the keys restored it printed `ALL CARD CHECKS PASSED`.
- **Widened why-now check.** I deleted `"whynow.no_data"` from the `de` block and ran `node tests/card.mjs`. It failed three checks: the two above and "why-now: every en string has its twin in every card language, and every driver code has a label and an explanation". The run printed `3 CARD CHECK(S) FAILED`. The old `en`-vs-`sv` form of that check could not see a German gap.
- **Widened features.py checks.** I planted a fourth catalogue, `translations/fr.json` (a copy of `en.json`), and ran `python3 tests/features.py`. Exactly the three widened checks failed: "setup text ships every translated catalogue's language, and no other", "every template language uses en's placeholders per key, one per shipped catalogue" and "and a card label in every card language, wired to the code". The run printed `3 of 4983 FEATURE CHECKS FAILED`. Under the old floors (`>= {"sv","de"}`, `>= 3`, `>= 2`) all three would have passed.
- **Anchor fixture.** With `_MUT_AN` naming the retired `25b21b2f`, `python3 tests/entities.py` failed three checks, each reading `has pin=False` or `-> None`: "--anchor re-drives one site: …", "a re-driven pin is not reproduced by a driver that only sees the row the mutant made stale …" and "invalidated_rows names exactly the rows pinned to a rewritten line …". The run printed `5 of 2699 ENTITY CHECKS FAILED`, the 5 including the two environment reds below. With `86fae85d` it printed `2 of 2699`.

## Null control

- The unmodified head passes every widened check. Gate run at f9db7d7a0: `node tests/card.mjs` ok and `python3 tests/features.py` ok (`ALL 4978 FEATURE CHECKS PASSED`).
- With `fr.json` absent, the same features.py run is green on those three checks.
- `tests/entities.py` at unmodified `origin/main` (73365699a, a separate worktree, same container) printed `2 of 2665 ENTITY CHECKS FAILED`. Those are the same two checks that stay red at this head, so neither is this branch's.

## Figures

- **Catalogue parity: 1437 leaves in `de.json`, 1437 in `en.json`.** Missing 0, extra 0, placeholder differences 0. The enumerator is every leaf of the flattened JSON tree, and a placeholder is a `{…}` token. The instrument is `python3 tests/entities.py`'s "de.json has exactly strings.json's keys" and "every translation names exactly the placeholders strings.json names". Its null control is the sv.json plant at `tests/entities.py`'s catalogue block.
- **Card parity: 637 keys in `STRINGS.de`, 637 in `STRINGS.en`.** Missing 0, extra 0, placeholder differences 0, measured at this head. Before `763820d8a` it was 619 keys, 18 missing. The instrument is `node tests/card.mjs`'s "every card language is key-for-key with en and keeps en's placeholders", which has its own planted null controls.
- **Closure-pair census in `tests/deployment_shape.py`'s docstring.** It stays 145 of 406 comparable pairs at a Jaccard index of 0.80 or more over production files. The largest closure is 105 files, which equals `git ls-files custom_components/heatpump_optimizer/ | wc -l` = 105. The command is `python3 -c 'import json,itertools as I;d=json.load(open("tests/closures.json"))["closures"];P="custom_components/heatpump_optimizer/";c={k:{f for f in v if f.startswith(P)} for k,v in d.items()};c={k:v for k,v in c.items() if v};p=list(I.combinations(sorted(c),2));print(len(d),len(p),sum(len(c[a]&c[b])>=0.8*len(c[a]|c[b]) for a,b in p),max(map(len,c.values())))'`. It printed `33 406 145 105` at the head and `33 406 145 104` at the base. `de.json` moved card.mjs/config_flow_steps.py from 0.800 to 0.802, which was already at the floor on main, so the count did not move.
- **Diff mutants: 2 sites, 0 survivors, about 7 s wall.** The sites are `topology.py:377` CONST_SWAP and `topology.py:378` RETURN_DEL. The command was `PYTHONPATH=tests/hastub python3 -I tools/audit/seat/mutant_run.py --diff 73365699a135fb813a43380096b6776d57f8ff4c...HEAD --cmd "python3 tests/guard_pins.py" --max-mutants 40 --report-only`, enumerated by the same command with `--list`. In-tree prepr runs `MUTANT_CMD` as one argv, so the `PYTHONPATH=` prefix must come from the environment.
- **Scoped gate at f9db7d7a0.** The mode line read `MODE: SCOPED -- 27 script(s) run, 6 scoped out` (`GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=73365699a135fb813a43380096b6776d57f8ff4c ./tests/run.sh`). The two reds are answered under `## Red checks`.
- **`tools/pr/prepr.sh` at f9db7d7a0, with this body:** `PRE-PR: f9db7d7a01dd9bf2877d3a0845562f2004ecbc8e … rc=0`, with `MUTANT_CMD="python3 tests/guard_pins.py"` and `PYTHONPATH=tests/hastub` exported. Wall time was 828 s.
- **Terminology sample.** Taken with `random.seed(7)` over the flattened `de.json`, 7 strings per section from config, options, issues, entity, exceptions and services. Two pairs of inconsistent terms in that sample led to the terminology commits above.

## Unpinned sites

none: `mutant_run.py --diff` drove both added sites and `tests/guard_pins.py` killed both. The added German strings are data, which the parity checks above pin.

## Red checks

- **`tests/entities.py`, the three `--anchor` checks.** The branch turned them red. The fixture names a ledger row by anchor, and the stopped fixer's `ddd0ce25` retired that row without updating the fixture. The detector that caught it is the scoped gate, which selects `tests/entities.py` for any `topology.py` edit, and it caught it before the handoff. A cheaper detector would be a lint for literal ledger anchors in tests. Its standing cost: one more tree scan per push, to save an `entities.py` run that already runs for every production diff. No such lint is worth building. The stopped fixer never ran `entities.py` at its final head; prepr does not run the gate.
- **`tests/entities.py`, two checks red in this container at unmodified main as well:** "the coverage job reuses only an entry main's push run saved, keyed on the runner's OS" and "the release ZIP holds the integration folder at its root, and its check refuses a hacs.json naming another file". Both fail identically in a worktree of unmodified `origin/main` (73365699a) in this container, so neither comes from this diff. I did not establish their cause. Neither check is in the merge train's required set (owner ruling 2026-11-07).
- **`tests/arch_score.py`, "arch-score.yml: a head edit to tests/structure.py is not what the gate loads (the #2068 plant)".** It failed with `fatal: '/opt/hpo/runner-temp/base' already exists`. That directory was this seat's first gate run's leftover: the plant ran `git worktree add` into the environment's real `$RUNNER_TEMP/base`, and its own temp repo was then deleted. I removed the orphan and re-ran `python3 tests/arch_score.py`. It printed `ALL 279 ARCHITECTURE SCORE CHECKS PASSED` at f9db7d7a0, and it left `$RUNNER_TEMP/base` behind again, which confirms the leak (see `## Friction`). The check is not this diff's.

## Forward-carry

none. Carry 1 (the roster brief's "Carry 0", item c7e2fe29) needs no carry of its own. The mechanism is stated above: the every-catalogue parity checks refuse whichever of R10-I18N-DE and R10-MIN-POWER-FLOOR merges second until its German leaf exists. The terms for that field family are Mindestleistung, Maximale Leistung, Leistungsaufnahme and takten. An earlier draft of this body routed it to R10-MIN-POWER-FLOOR. `body_push.sh` then refused the draft with CARRY-MISSING, asking for a roster-branch write (`carry_audit.py land-ops`), which this seat's brief forbids ("Never write to any branch except your return refs"). The orchestrator may land that route if it wants the brief to name the terms.

## Friction

- fixer.md-step5: cost: the #2068 plant in `tests/arch_score.py` runs `git worktree add` into the inherited `RUNNER_TEMP=/opt/hpo/runner-temp/base` and leaves it behind. Its temp repo is then deleted, so the next `arch_score.py` run in the same container fails with `'/opt/hpo/runner-temp/base' already exists` until the orphan is removed by hand. Observed twice on this seat, at 08:03 and at 09:25. The proposed owner is R10-SUITE-HOST-DETERMINISM, but routing it there needs a roster write this seat may not make. Carry: dismissed: not routed by this seat; the orchestrator routes it from this body
- prepr.sh-6d: unclear: `MUTANT_CMD` is split into an argv and not run by a shell. `MUTANT_CMD="PYTHONPATH=tests/hastub python3 …"` therefore printed `ok diff mutants no survivor: FileNotFoundError …`, so a broken command reads as a clean mutant run. The proposed owner is R10-PREPR-CAP, with the same constraint. Carry: dismissed: not routed by this seat; the orchestrator routes it from this body
- body_push.sh: contradiction: CARRY-LANDED requires a fixer to land its carries on the round's roster branch, and the fixer dispatch brief forbids any write outside the return refs. Carry: dismissed: owner ruling needed; reported in this seat's result
