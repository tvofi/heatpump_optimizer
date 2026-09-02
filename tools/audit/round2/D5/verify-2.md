# D5 — verifier seat 2 of 3

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, read-only export
`audit-r2-baseline`. Apple M1, Python 3.13.1 (`tvofi-claude/.venv`), run
from the export root with `PYTHONPATH=tests/hastub`. Every number is a count;
no solver, no test suite, no timing was run. Scratch and my harness:
`/tmp/verify-D5-2/` (`v2_checks.py`, `linkgraph.py`, `run_*.log`,
`v2_checks.log`).

## Re-runs of the finder's harnesses (exactly as their headers say)

| harness | finder | mine | load1 | thread_factor |
|---|---|---|---|---|
| `links.py` | 46 / 3 / 0 / 0 / 6 / 0 / 0 / 0 | identical | 1.90 | 1.004 |
| `duplication.py` | 538 / 37454 / 0 / 1 / 237 / 237 / 0.043 | identical | 1.90 | 1.000 |
| `comment_symbols.py` | 872/3, 209/7, 248/0, 42/0; vetted 0 / 1; redundant 11; long 515 / 242 | identical | 1.90 | 1.000 |
| `comment_numbers.py` | 432 / 65 / 17 / 1 / 2 / 2 / 0 | identical | 1.90 | 1.000 |
| `reader_paths.py` | 36 / 15; per-doc 2,1,2,1,2,7; unreachable 3; drift 7; ecl110 1; content 5; dead ends 4/4/8 | identical | 1.90 | 1.000 |

All exact. Counts are contention-immune; load1 was under 1.5 for none of
them but that gate applies to timing and memory RESULTs only.

## My harness

`/tmp/verify-D5-2/v2_checks.py <export-root>` — one script, one RESULT per
finding, my own metric definitions (below), facts derived through `ast`,
`closures.json`, `run.sh`, `tests.yml` and regex; nothing executed from the
tree. Final run: `thread_factor=1.000 load1=1.81`.

```
RESULT v2_tests_readme_contradictions=7          (strict contradictions 6; T6 is an omission)
RESULT v2_ecl110_doc_vs_code_contradiction=1
RESULT v2_ecl110_error_logs_per_cycle_without_mqtt=2   (per 30-minute cycle, default interval)
RESULT v2_unreachable_from_readme=3
RESULT v2_content_defects_present=5
RESULT v2_content_defects_reader_visible_when_rendered=3
RESULT v2_comment_precision_defects=5
```

---

## D5-01 · tests/README.md drift — **verify, low** (executed 7: 6 contradictions + 1 omission)

**Metric (mine).** Statements in `tests/README.md` whose stated path, count
or roster is denied by the tree, each fact derived independently of the
finder's script: `closures.json` reader map, `run.sh:390` wiring
allow-list (the longest `continue ;;` list), `tests/golden/*.json` on disk
plus `golden.py:SCENARIOS` via ast, `plan_view.py:130`, top-level `run(`
calls in `validate.py`, `.github/workflows/tests.yml`.

**Each of the seven, checked by hand.**

| id | verdict | what I found |
|---|---|---|
| T1 (l.129) | contradiction | `closures.json`: `entities.py` reads `README.md` and `RELEASE_NOTES.md`; `golden.py` and `env_drift.py` read `brand/icon.png`, `brand/logo.png`, `custom_components/…/icon.png`. `closure.py:INERT` lists none of them (only the root `icon.png`), and `closure.py:451-457` fails a re-derivation if an INERT file is read, so the list is "checked" exactly as the doc says — it just does not contain what the doc says. The document contradicts itself 27 lines earlier: l.102 says a `RELEASE_NOTES.md` change runs `entities.py`. Not phrasing. |
| T2 (l.285) | contradiction | 55 fixture files = 49 `SCENARIOS` + 5 `coord_*` + `config_flow.json`; doc says 53 = 47 + 5 + 1. The doc's arithmetic was right when SCENARIOS had 47 keys. |
| T3 (l.355) | contradiction | `--all` captures SCENARIOS + coordinator + config_flow (`env_drift.py:145-146`) = 55; doc says 53. `env_drift.py:186`'s own comment also says "all 53" — the same drift in a code comment (tests/, outside D5-05's production scope; for the fixer). |
| T4 (l.228, l.457) | contradiction | `plan_view.py:130` writes `/tmp/plandata-<sha256(tests dir)[:12]>.json`; `card.mjs:12-20` takes `/tmp/plandata.json` "only as a last resort, loudly". A developer looking for the named file does not find it. |
| T5 (l.487) | contradiction | The sentence is about the "every script must be wired into `run.sh`" accounting. That accounting (`run.sh:390`) excludes seven: `harness.py profiles.py dst_checks.py closure.py dom_stub.mjs card_rig.mjs card_browser.mjs`. The doc's four include `derive_closures.sh`, which the glob (`tests/*.py tests/*.mjs`) never sees, and omit four that are excluded. `closure.py:NOT_A_TEST` is a different seven (`setup_qa_render.mjs` in, `dst_checks.py` out). Phrasing defence: l.234-236 do describe `harness.py`/`profiles.py` as shared plumbing — but the count is wrong against both rosters. |
| T6 (l.505) | **omission** | "`card.mjs` does not lay anything out" is true. `tests.yml:208` `browser` job (`if: push or pull_request`) runs `node tests/card_browser.mjs`; tests/README.md mentions it 0 times and tells the reader to verify by hand what CI automates. Drift, not a contradiction; the finding's claim wording ("state a fact that the tree contradicts") is wrong for this one. |
| T7 (l.221) | contradiction | 22 top-level `run(` calls in `validate.py`; doc says 18. |

**Attacks.** Contention: n/a, counts. Export artefact: none of the seven
touches a removed file. Wrong gate mode: n/a. Severity: developer-facing
document, no behaviour, no published value — low/hygiene is right. Bug? No.

**Vote: verify, low.** Executed 7 (my strict count 6 + 1 omission). The
register should read "six statements the tree contradicts and one lane the
document omits", not seven contradictions.

---

## D5-02 · ECL110 topics: "leave blank" vs non-empty defaults published each cycle — **verify, low as scoped; the mechanism is a `bug` for D10** (executed 1; 2 ERROR logs per 30-minute cycle)

**Metric (mine).** 1 if `docs/configuration.md` tells a non-owner the ECL110
topics can be left at their defaults AND, by ast over `coordinator.py`,
both `DEFAULT_ECL110_*_TOPIC` are non-empty, the publish call is a
top-level statement of `_apply_action`, `_async_update_data` awaits
`_apply_action`, the only early return is the conjunction "both topics
empty", and no `has_service("mqtt", …)` / `"mqtt" in hass.config.components`
gate exists; else 0. → 1. Second number: `_LOGGER.error` sites in
`async_publish_ecl110_command` → 2.

**The publish path, traced.** `_async_update_data` (4342) → solve sets
`_current_action` (4785; the three degraded branches at 4372/4382/4392 set
it too, with `displace_value = displace_min`) → `await self._apply_action()`
(4403, unconditional inside the cycle's `try`) → `_apply_action` (6519)
returns early only if `_current_action` is empty or the plan is stale in
auto/economy → step 2 (6584) `await self.async_publish_current_action(
reason="scheduled_update")` → `async_publish_ecl110_command` (6337) returns
at 6378 only when *both* topics are falsy; otherwise two
`hass.services.async_call("mqtt", "publish", …, blocking=True)`, each in
`try/except Exception → _LOGGER.error`. `grep has_service|"mqtt" in` over
coordinator.py and `__init__.py`: 0. `manifest.json` lists `mqtt` under
`after_dependencies`, not `dependencies`, so nothing requires it to be
loaded. Yes: with the shipped defaults every cycle attempts two publishes.

**What real Home Assistant does.** `ServiceRegistry.async_call` looks the
handler up in `self._services[domain][service]` before dispatch and raises
`ServiceNotFound` (a `HomeAssistantError`, so an `Exception`) when the
domain or service is not registered, `blocking` or not. `mqtt.publish` is
registered only when the MQTT integration is set up. So a default install
without MQTT logs "Error publishing ECL110 direct displace MQTT command:
…" and its legacy twin — two ERROR lines — every 30 minutes
(`DEFAULT_OPTIMIZATION_INTERVAL = 30`) from the first successful solve,
forever. With MQTT set up but no ECL110: two silent publishes per cycle to
topics nobody subscribes. Not executed here: no HA core on this box.
The stub cannot show it: `tests/harness.py:146-148` `FakeServices.async_call`
returns `None` for an unregistered service and the hastub `exceptions.py`
defines no `ServiceNotFound`. `grep` for the default topics, `"mqtt"` or
the error string across `tests/*.py`: 0 hits — nothing pins this either
way. The finder's D6/D10 note is correct.

**The documents.** `configuration.md:457` "Leave blank if you do not have
one" — the fields are not blank, so there is nothing to leave;
`configuration.md:70` "default sensibly when absent"; `ecl110.md:77-82`
says the opposite and `ecl110.md:8-9` opens by telling non-owners the page
is not for them; `README.md:599-606` points everyone at ecl110.md without
mentioning the defaults. Contradiction confirmed.

**Attacks.** Reachable in real HA: yes (above). Export artefact: no. Null
control: n/a. Severity: as a documentation row, low/hygiene is right — it
changes no plan or value. But the consequence of following the page is
user-visible in every default install without MQTT, and the finder's
proposed docs-only fix (make configuration.md tell every non-owner to go
and clear two topics) points the wrong way: the honest fix is the code
default (empty topics, or a `hass.services.has_service("mqtt", "publish")`
gate) with the docs following. I would record the mechanism as a `bug`
(ERROR-level log noise in the default configuration) under D10 and keep
D5-02 as the docs row that led to it; the fix should not land docs-only.

**Vote: verify, low** (docs scope). Executed 1; 2 ERROR logs / 30 min.

---

## D5-03 · Three documents unreachable from README.md — **verify, low** (executed 3)

**Metric (mine).** Documents in {README.md, DISCLAIMER.md, tests/README.md,
docs/*.md} not reachable from README.md by following relative links of any
of three syntaxes: inline `[t](p)`, reference `[t]: p`, HTML `href=`.
`/tmp/verify-D5-2/linkgraph.py` → 3: `docs/plan-card-decomposition.md`,
`docs/plan-open-issues.md`, `tests/README.md`. No reference-style or HTML
links exist in the set, so the finder's inline-only regex loses nothing.

**Graph.** README → DISCLAIMER, architecture, configuration, dashboard-card,
ecl110, how-it-works, plan-v4.0.0-program. architecture → how-it-works only
(it names `tests/features.py` and `tests/entities.py` as text). Inbound
links to `tests/README.md`: **none** — the two plan documents mention it in
backticks (plan-card-decomposition.md:252,267; plan-open-issues.md:113,220),
not as links. The finder's "the only inbound links … are from the two plan
documents" is wrong in wording, not in the count.

**Attacks.** *Export artefact:* README links `docs/backlog.md`, which the
export removed; if that file linked tests/README.md the count would be an
artefact. At the baseline commit (via the tvofi-claude object store, link
targets only through `grep -o`, no content read): `docs/backlog.md` has 0
markdown links, `docs/audit-2026-08.md` 0, `RELEASE_NOTES.md` 1 (external,
strutsfarm GitHub). Restoring them adds no edge; 3 stands. *Consequence:*
GitHub renders `tests/README.md` automatically when anyone browses
`tests/`, and architecture.md sends the developer to files in that
directory — "strands the developer" overstates it. The two plan documents
are the ones only a directory listing finds. Severity: low/hygiene right;
one table row and one bullet.

**Vote: verify, low.** Executed 3.

---

## D5-04 · Five content defects — **verify, low** (executed 5 present; 3 reader-visible when rendered)

**Metric (mine).** (a) Present: my own regexes for each of the five, over
the same documents. (b) Reader-visible: of those, the ones a reader of the
rendered page (GitHub or HACS) would notice without the source.

| id | present | reader-visible | judgement |
|---|---|---|---|
| H2 how-it-works.md:564 | yes | yes | "both that prior and the range learning may move within follow the tank's **surface area**" — two drafts merged; unparseable. Defect. |
| H1 how-it-works.md:1189 | yes | half | 134 chars; prose p95 = 80, the sole line over p95 + 20. Markdown reflows, so the wrap is invisible; what survives is "Without it, an unexpected slot is indistinguishable from a bug" now following the inserted v5.1.7 sentence, so "it" reads as the old `preheat_weather` fall-through. The dangling pronoun is a defect; the wrap is source hygiene. |
| S1 README.md:610-617 | yes | yes | Newest release named v5.0.0 ("have been an audit train"); VERSION 6.2.14. Stale rather than false — it narrates history — but a reader on 6.x notices the status stops a major version back. |
| C6 configuration.md ×8 | yes | no | No defining sentence anywhere in the user-facing set. But the three bullets at 482-484 ("no throttling mixing valve → No mixing valve; a throttling valve, two zones and a wood tank top sensor → Two tanks…; any other throttling valve → One tank behind a valve") define it by exhaustion, and how-it-works.md:386-392 explains the mechanism without the word. `mixing_valve.py:56`: "Modes in which a valve exists at all, and delivery is therefore throttled." A reader is not stopped. Clarity, not defect. |
| ST1 dashboard-card.md:31-133 | yes | no | Six h3 under the h1, first h2 at 134. Visible only in GitHub's outline; the page reads normally. Trivial. |

**Attacks.** Contention/export: n/a (S1's link to docs/backlog.md resolves
in the repository, links.py header says so). Severity: docs-only, low is
the floor and correct. Bug? No.

**Vote: verify, low.** Executed 5 present / 3 reader-visible; the register
entry should carry "5 (3 reader-visible)".

---

## D5-05 · Five comment-precision nits — **verify, low** (executed 5 = 1 + 1 + 3)

**Metric (mine).** Among the five named comments, those whose claim I can
falsify against the code beside them or the tree: number cited vs constant
value; service name vs `services.yaml`; content words of the comment (after
stemming) all present in the identifiers of the next code line.

- `open_meteo.py:66-69` "surface GHI cannot exceed [~1361]" beside
  `_MAX_PLAUSIBLE_GHI = 1400.0`, used as the reject threshold at l.167: the
  constant admits 1362–1400 W/m² that the comment says cannot occur. Nit;
  harmless (an Open-Meteo hourly value never approaches it). 1.
- `thermal_model.py:191` "(the set_thermal_params service)": services.yaml
  has `set_thermal_parameters`; `set_thermal_params` is the stem of the
  handler `handle_set_thermal_params` (`__init__.py:443`), so a grep lands
  on the handler, not nowhere. Nit. 1.
- `coordinator.py:4353` "# Fetch prices from Tibber" → `_fetch_tibber_prices()`
  (Tibber-only per its docstring: accurate, restating; one of four step
  labels in `_async_update_data`, house style); `optimizer.py:671`
  "# savings as percentage" on `savings_percentage: float`;
  `thermal_model.py:1830` "# Solar gains per zone" →
  `solar_gain_per_zone(...)` ("gains" matched only after stemming). By
  reading, all three restate. 3.

**Vetting attack.** `comment_numbers.py` ALLOW has 16 reasoned entries;
`comment_symbols.py` ALLOW 6. I read the raw lists in my run logs: the two
prose roundings (`defrost.py:93` "less than half" for 0.55, `:120` "a
third" for 0.30) are correctly vetted out; the eight non-counted redundancy
hits are section labels or `#:` attribute docs. The vetting holds.
Met on the way: `tests/env_drift.py:186` "over all 53 scenarios" is stale
(see D5-01 T3) — tests/ is outside this finding's production scope.

**Severity.** Five nits across 1,120 strict + 251 loose references and
5,825 comments; each is a real one-line fix and none is a bug. Borderline
register-worthy, but the claim is exactly what the tree shows.

**Vote: verify, low.** Executed 5.

---

## Summary

| finding | re-run | my number | vote | severity | class |
|---|---|---|---|---|---|
| D5-01 | 7 | 7 (6 contradictions + 1 omission) | verify | low | hygiene |
| D5-02 | 1 | 1; 2 ERROR logs / 30-min cycle without MQTT | verify (docs scope); mechanism → D10 `bug` | low | hygiene (docs) |
| D5-03 | 3 | 3 | verify | low | hygiene |
| D5-04 | 5 | 5 present / 3 reader-visible | verify | low | hygiene |
| D5-05 | 1+1+11 raw | 5 | verify | low | hygiene |

**Exposure.** To test D5-03's export-artefact hypothesis I extracted link
targets only (`grep -o '\](…)'`) from the export-removed `docs/backlog.md`,
`docs/audit-2026-08.md` and `RELEASE_NOTES.md` at the baseline commit via
the tvofi-claude object store; no content of those files was read. Neither
other verifiers' output, the register, nor GitHub was read.
