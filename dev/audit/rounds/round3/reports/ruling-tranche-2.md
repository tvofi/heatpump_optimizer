# Judge — audit round 3, second tranche (D8, D11)

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`, judged in the worktree at
`.../audit-r3/judge2`. Box: 8-core Apple M1, 8 GB, python 3.11.5, numpy 2.4.6,
scipy 1.17.1, node v20.10.0, `gh` 2.98.0. Five BLAS thread variables pinned
before numpy on every run.

**`thread_factor` was `1.000` on every harness without exception; `load1` ran
8.50 – 12.79 across the session.** Every number below is a count, a set
comparison or a fraction of counts — no wall, CPU or RSS figure is claimed — so
contention reaches nothing here. `load1` is quoted, not gated, per
`tools/audit/README.md`.

No `tests/stress.py`, no `./tests/run.sh`, no gate lock, no artefact above a few
kB (disk was at 3.2 GB free and stayed there). GitHub was read **read-only**:
nothing created, edited, closed, commented on, merged, pushed, dispatched or
re-run; the ruleset was read and never modified. **`api_failures=0` beside every
GitHub figure**, printed by the harness rather than assumed — `gh api rate_limit`
read `core: 0 used of 5000` throughout, which proves nothing, so every census was
compared as a **set** and every loop printed its own failure count.

**Panel size.** D8 and D11 each had **two** verifier seats, not three. The kill
rule needs three counted votes, so **no finding in this tranche could have been
killed by majority refute** — a two-seat agreement is weaker evidence than a
three-seat one, and where the two agreed I am the only independent check. I
re-measured every finding rather than counting votes.

---

## Verdict table

| id | reproduced? | perturbation moved? | null control | LOO | verdict | severity | stop_rule_class | note |
|---|---|---|---|---|---|---|---|---|
| D8-01 | **yes, exact** — `advice_value_as_shipped=0`, `gate_productive_at_0_5=0`, `writers_of_wood_tank_soc=0`, `wood_fuel_ready=6`, `advice_available=6` | **yes** — `wood_tank_soc=0.2` → 3 cheap-wood arms publish `'light Thu 23:00'` (0→3, up); 3 dear-wood arms stay `None` in both columns | **passes** — explicit `soc=0.5` (the fallback's own value) → `advice_attached_soc_mid_null=0` of 4000, while `0.2`→1890 and `0.9`→3693. The move is a threshold crossing, not key presence | drop the most favourable arm → still 0 of 5 as shipped; the 4000-draw sweep is 0 of 4000 | **verified** | **medium** | **bug** | **Wrong-source, not a missing option — confirmed.** `battery.components[wood_tank].soc_percent = 61.5` is already in the payload, derived from the same tank probes `wood_fuel_ready` already requires. Narrowing I add below. |
| D8-02 | **yes, exact** — `--limit 2` baseline `available_unknown_default_install=2`, `available_but_unknown_everywhere=2` | **yes** — `--perturb wood-gate` 2→1 and 2→1 (finder's metric), 1→0 (v1's) | **passes** — `--perturb inert-gate` (an `available` property returning `super().available`) leaves it at **1→1**: the drop is caused by the condition, not by defining the property | population is 1 real case; dropping it takes both metrics to 0 | **weakened** | **low** | **hygiene** | **Votes NOT COMPARABLE on the count** (2 vs 1 vs 42-of-74): three different metric definitions. I adopt the platform-based one. **Value = 1.** Countermeasure incomplete, re-measured: `mute_on_wood_ready_after_gate=1`. |
| D8-03 | **yes, exact** — `family_splits=36`, `_entity_id=36`, `_sv=36`, `rank_moves_ge_5=33`, `key_not_slug_of_name=15`, `case_style_minority=6` | **yes** — `--perturb split-ecl110` → `family_splits_entity_id` 36→**37**, others unmoved; `--perturb prefix-one` → 26→**27**; `--perturb shuffle-order` → 36→**55**, `family_splits_id` unmoved at 36 | **passes, and it bounds the finding** — `leading_word_splits=0` over 13 groups; 5,000-draw random permutation **58.59 ± 2.29** (min 50), so 36 is **9.9 sd BETTER than chance**, 61 % of random | **`finder_family_leave_one_out_max=7`** (`temperature`) → 36 drops to **29**; 19 % of the total from one family | **weakened** | **low** | **hygiene** | One sub-claim **refuted** (below). 36 is materially list-dependent: **23** single-keyword, **26** mechanical partition, **38** device-page. The defensible defect slice is `case_style_minority=6`. |
| D11-01 | **yes** — my own live reads: 18 required contexts, **0 `pull_request` rules**, `bypass_actors=[RepositoryRole 5, always]`, `current_user_can_bypass='always'` | **yes** — `mechanisms.py --perturb` arm B (splice in a `pull_request` rule) → `has_pull_request_rule` 0→1, `required_approvals` 0→1, rule types 3→4 | **passes** — 21 of 39 carry a `Fix review: merge` **comment**, so review *activity* exists; what is absent is the platform **object**. The honest reading is "review is unprovable from the platform" | repo-wide census replaces the sample: **6 of 518** merged PRs carry any review object, **0 of 518** an approving review by another account | **verified** | **critical** | **bug** | **The seats SPLIT (v1 critical, v2 high) and I decide on the rubric, not the votes.** Arm 1 is unconditional; arm 2 is a capability, which is what the rubric asks. Finder's headline metric corrected below. |
| D11-02 | **yes** — `dora.py` reproduces 37 / `{"record":20,…}` / 11 exactly, **but from its own cache**; `record` confirmed in the live 18; `governance.yml:225` `if: github.event_name != 'pull_request'` | **yes** — `mechanisms.py --perturb` arm C (`record` `if: always()`) → `contexts_skipped_by_construction_on_pr` 1→**0**; strike `record` and re-aggregate → red heads fall by exactly `red_heads_only_record` | **passes** — at #738's head **17 of 18** required contexts concluded `success`, exactly **one** (`record`) `skipped`, 0 failures, 0 with no run: the skip is specific to `record`, not a property of the head | drop the head most favourable to `record` → 15 of 23 (0.652), still by far the largest (next: `fast (3.13)`/`(3.14)` at 7) | **verified** | **high** | **bug** | **State it as an ORDINAL claim with a dated count.** The absolute count does not survive a window change; the remedy's second half is wrong — I confirmed it myself. |
| D11-03 | **yes, exact** — `policy_globs_in_production=10`, `arm_policy_title_exit=1`, `arm_docs_title_exit=0`, 82 / 64 / 0.7805, 50 / 32 / 0.6400 | **yes** — identical body, identical head, title `policy:` → exit **1** naming `` no `## Approval` section ``; title `docs:` → exit **0**. Direction to_zero | **passes** — the `docs:` arm with a byte-identical body is the control: the gate is switched **off**, not broken | 32 of 50 → 31 of 49 (0.633) with the most favourable commit dropped | **verified** | **high** | **bug** | **Votes NOT COMPARABLE on the consequence figure**: 32 of 50 counts the hole, 4 of 11 counts what fell through it. Both true of different metrics; the register carries both. |
| D11-04 | **file half yes; second half NOT EXECUTED** — `sc_security_policy=0` reproduces; no `SECURITY*` anywhere in the baseline tree; `community/profile` carries **no security entry** (health 57 %); `tvofi/.github` → **404**; 0 vulnerability wording in `README.md`/`docs/*.md` | **yes** — `standards.py --perturb`: SECURITY.md under a temp root → `sc_security_policy` 0→**1**, restored to 0; the tree was never written | **passes** — the restore arm returns 0 | not an aggregate | **weakened** | **low** | **hygiene** | **I called the endpoint myself: `GET …/private-vulnerability-reporting` → HTTP 200 `{"enabled":true}`.** The claim was inferred from a key's absence in a block that never carries it. |
| D11-05 | **yes, exact** — `prompts_reading_github_text=6`, `read_and_write_prompts=5`, `corpus_files_scanned=35`, `boundary_files=1` (`tools/audit/briefs/D11.md`), `repo_is_public=1`, `distinct_issue_authors=1`, `collaborators=1` | **yes** — `agency.py --perturb` appends a boundary sentence to a corpus **copy** → `boundary_files` 1→**2**, up | **passes, twice** — my own grep of `.claude/rules/`, `CLAUDE.md` and the PR template for `not (as )?instructions\|untrusted\|prompt injection` returns **0 hits**; v2's deliberately wider 9-pattern net returns 2, the extra one matching a sentence that is the **opposite** of a boundary | not an aggregate; the authorship census is the LOO-equivalent and holds at 518 PRs | **verified** | **medium** | **hygiene** | `GET /interaction-limits` → **`{}`** (my read): the one setting that would close all five surfaces at once is not set. The door is open; nobody has walked through — measured, not inferred. |

---

## D8 — what I re-measured, and where I differ

Every finder harness and every verifier harness was re-run from its own header,
from the repository root with `PYTHONPATH=tests/hastub`.

```
d8_ordering.py                 74 / 36 / 36 / 36 / 33 / 15 / 6 / 0 / 0    exact   load1=8.50
d8_ordering.py --perturb split-ecl110    family_splits_entity_id 36 -> 37, others unmoved
d8_wood_advisor.py             6/4/0/6/0/6/6/0/3/0/0/3                    exact   load1=12.51
d8_matrix.py --limit 2         2 / 2 / 9   (the three per-install metrics)  exact   load1=10.03
d8_matrix.py --limit 2 --perturb wood-gate      2 -> 1 and 2 -> 1
d8_matrix.py --limit 2 --perturb same-inputs    frozen_while_input_moved 9 -> 0
v1_wood_reach.py               0/1/175/8/3/10/3/175/0/21/21/1/0/1 and 4000/4000/0/1890/3693/0   exact
v1_mute.py                     1 / 1 / 0 / 1 / 1                          exact
v1_mute.py --perturb wood-gate      mute_reporters 1 -> 0
v1_mute.py --perturb inert-gate     mute_reporters 1 -> 1   (null control holds)
v1_families.py                 26 / 0 / 8 / 36 / 23 / 7 / 24 / 38         exact
v1_families.py --perturb prefix-one 26 -> 27, leading_word_splits unmoved at 0
v2_consequence.py              59.7 / 0 / 175 / 0 / 1 / 1 / 10 / 74 / 32 / 42 / 413 / 58.59 +- 2.29 / 4 / 27 / 0   exact
v2_consequence.py --perturb shuffle-order   family_splits_en 36 -> 55, family_splits_id unmoved at 36
```

**One delta, and it is an artefact of my own tree.** `v2_consequence.py` printed
`soc_key_tree_mentions=2` here against the verifier's `1`. The extra mention is
`JUDGE-CARRY.md:912` — the orchestrator's carry file, which lives in the judge
tree and not in the verifier's. Production is unchanged at **1**: the read at
`custom_components/heatpump_optimizer/wood_fuel.py:463`. Not a defect in the
instrument; recorded so the next reader does not chase it.

### D8-01 — the fix scope, and a narrowing on the "already published" claim

Carry item 105 is confirmed by my own re-execution and by reading the source.
`v1_wood_reach.py` prints `wood_tank_soc_already_published=1` with
`WOODTANK wood_tank soc_percent=61.5`, and the source says why that matters:
`wood_fuel.py:86-109`'s `wood_fuel_ready` **already requires** a wood tank top or
bottom probe (`CONF_WOOD_TANK_TOP_ENTITY` / `CONF_WOOD_TANK_BOTTOM_ENTITY`)
before the advisor may speak at all, and `battery.py:353-371` builds the
`wood_tank` component's state of charge from those same readings. So the advisor
is reading the wrong source for a number the tree already has. **"Add a
`wood_tank_soc` config field" is the obvious wrong fix** and would cost a
ratchet-relevant schema page.

**The narrowing the fix brief needs:** the *published* component is gated on
`params.two_tank_modelled` (`battery.py:354-355`), which resolves only through a
throttling mixing-valve mode **and** two zones **and** a wood probe. On a
wood-furnace install that is not two-tank-modelled, `battery.components` carries
no `wood_tank` entry. So the fix scope is **"derive the state of charge from the
probes the readiness gate already requires"**, of which reading
`battery.components[wood_tank].soc_percent` is the two-tank case — not
"read `battery.components`" full stop.

Severity stays `medium`, as both seats had it: a documented, shipped, closed
feature (`README.md:469`) that has never produced output on any install that
ever existed, for every user who wired the hardware — against which the loss is
bounded at **one** payload key with **one** consumer, no plan, cost, setpoint,
control or statistic, and an `EntityCategory.DIAGNOSTIC` row.

Two corrections to the finder that stand and must travel with the issue:

* **`advice_value_soc_high=0` is a clock artefact, not a product property.** The
  optimizer's horizon is 24 h (`optimizer.py:966`, `horizon_hours: float = 24.0`)
  and `golden.START` is midnight, so all 96 stamps fall on one calendar date and
  `expensive_next` cannot fire. Re-frozen at 14:00 the same arm returns `skip`.
  Do not read that zero as evidence the skip branch is dead.
* **Propagated to D5/D6, not filed:** the sensor docstring and `README.md:469`
  both promise **"48 h"** advice over a **24 h** horizon. I confirmed both lines.

### D8-02 — the votes are not comparable, and the count is 1

Three metric definitions were used and they measure different populations:

| seat | definition | number |
|---|---|---|
| finder | enabled-by-default value entities, all six platforms, `available=True` with a `None` state | **2** |
| verifier 1 | the same restricted to the **read-only** platforms (`sensor`, `binary_sensor`) — controls excluded **by platform**, not by argument | **1** |
| verifier 2 | entities with no `available` of their own anywhere in the MRO | **42 of 74** (a different question) |

I mark the votes **not comparable** on the count and decide it myself.
`AwayReturnDateTime` is a `DateTimeEntity` with `async_set_value`: a **control**,
whose `None` correctly means "no away override set", and Home Assistant disables
a control whose entity is unavailable — so gating it would make it impossible to
set the very value whose absence triggered the gate. Excluding it by platform
puts the judgement in the metric definition rather than inside the count, which
is the right place. **Value = 1.**

`stop_rule_class` is `hygiene`, from what the number shows and not from what the
finder wrote: the entity publishes `None` with **no `state_class` and no
`device_class`**, so nothing enters long-term statistics, nothing is recorded and
no reading is wrong. The loss is one permanently-Unknown row in the collapsed
Diagnostic section. That is structure and presentation, not a wrong value.

**Do not ship the one-liner as the fix.** I re-measured
`mute_on_wood_ready_after_gate=1` under both perturbation arms: on an install
where `wood_fuel.ready` is True the **gated** sensor is still available-and-None.
The one-line `available` gate removes the Unknown only from installs that *lack*
the feature. And once D8-01 is fixed, `action == 'none'` is the **normal** branch,
so a wood-ready install publishes `None` most of the time regardless — at which
point Unavailable-versus-Unknown is a UX preference, and the sibling binary
sensor answers the analogous question with `False`, not with unavailable.

**The systematic half is worth more than the instance**, and it is the round-2
precedent repeating: `tests/entities.py:1863-2219` records a round-2 finding on
exactly this principle whose countermeasure was a hard-coded roster of 13 named
entities (`_D801_IN_SCOPE`). `WoodBurnAdvisorSensor` (#702) was added later, is
not on the roster, and nothing noticed. 42 of 74 entities are ungated and there
is no base-class default. **The fix should be a rule, not a fourteenth roster
entry.**

### D8-03 — the count is right, one sub-claim is refuted, and most of it is a preference

The arithmetic reproduces in three independent implementations (36 / 36 / 36),
the perturbation moves by exactly 1, and the two controls I re-ran both hold. So
nothing here is unreproduced. What it is *worth* is a different question, and
three measurements bound it:

1. **The null control the finder did not run.** 5,000 uniform random
   permutations of the same 74 entities and the same family sets score
   **58.59 ± 2.29** (min 50). The shipped 36 is **9.9 standard deviations better
   than chance** and 61 % of it, with a floor of 0. "36 splits" reads as chaos
   and is not: the convention that exists buys about 39 % of the available
   grouping and stops — which is the finding's **own title**, "applies it to
   half the families".
2. **The number is materially list-dependent.** Cutting every multi-keyword
   bundle in `FAMILIES` to its first keyword gives **23**, so 13 of the 36
   (36 %) come from bundling choices — worst a `tariff_peak` family bundling
   peak / headroom / contract / price / savings, five topics as one. Under a
   mechanical last-word partition nobody chose it is **26**, with the same worst
   offenders. **Leave-one-out: 7 (`temperature`), so 36 → 29.** Quote 36 only
   with its definition.
3. **The remedy is blocked and the guidance runs the other way.** `entity_id`
   derives from `translation_key` and is used verbatim only at first
   registration, so a rename splits the installed base into two id conventions;
   the card resolves 4 headline stat sensors purely by id suffix, its own comment
   calling that "the discovery contract"; 27 distinct ids are pinned across
   `docs/` and `tests/`. And Home Assistant's own naming guidance makes the
   entity name the *measurement* with the device name prepended — i.e. exactly
   the trailing noun the finding objects to. An alphabetical sort clustering by
   leading token is a property of alphabetical sorting, not of this integration.

**One sub-claim is REFUTED.** "Swedish scatters the same total differently, so
this is not an artefact of English": under a mechanical trailing-noun partition
Swedish is **8** against English's **26**, because Swedish compounds the noun
(`Utomhustemperatur`) and there is no trailing-noun family left to scatter. The
finder's Swedish 36 came from its keyword list matching substrings *inside*
compounds — a different phenomenon. The scattering is substantially a property of
English multi-word naming.

**Two attacks on the finding FAILED and it survives them.** The three 36s are not
the same 36 (en/id agree on 12 of 16 families, sv on 7), so the metric does
respond to the sort and only the aggregate hides that; and under the device-page
order a user actually sees, splits go **up** to 38 — the flat sort understates
rather than invents.

**What is a defect, decided:** the ordering itself is a preference and I would
not file it. **The defensible slice is `case_style_minority = 6`** — six
sentence-case display names against 68 Title Case, in one file, with no rule
distinguishing them, and it is free: display names only, with `strings_vs_en` and
`strings_vs_sv` both 0. `weakened` to that, `low`, `hygiene`.

**Incidental correction that must not be lost:** the finder's non-findings row
"6 README ids" has **no referent** — `readme_entity_ids=0`. `README.md` contains
zero entity ids; the strings at `README.md:238-247` are `.storage` keys.

---

## D11 — what I re-measured, and where I differ

My own instrument (`j2gov.py`, `j2reviews.py`) shares no code with the finder's
or either verifier's. It resolves PRs through **REST** `/commits/{sha}/pulls`,
reviews through **REST** `/pulls/{n}/reviews`, and check runs through each head's
own `/commits/{sha}/check-runs?filter=all` paginated — a third route in each
case. **`api_failures=0` on every figure.**

**The `startedAt`-tie trap, handled.** Every "latest per context" here is ordered
on **`(started_at, check-run id)`** — GitHub's own ordering. I verified the
mechanism on #738's head, where `pr-contract` ran `failure 20:36:20Z` →
`success 20:36:53Z` → `success 20:38:20Z`; ordering on `startedAt` alone would
have scored that merge red.

```
RESULT j_required_contexts=18                       RESULT j_pr_rules=0
RESULT j_bypass_actors=[{RepositoryRole, 5, always}]  RESULT j_current_user_can_bypass='always'
RESULT j_sample_commits=40   j_commits_with_no_merged_pr=1 ['18d67a2']   j_sample_merged_prs=39
RESULT j_heads_red_required_at_merge=0 of 39 []
RESULT j_heads_pr_contract_first_red=5 of 39 [738, 743, 727, 711, 710]
RESULT j_record_conclusions_on_pr_heads={'skipped': 61}
RESULT j_sample_prs_with_a_review_object=0 of 39
RESULT j_sample_prs_with_an_approving_review_by_other=0 of 39
RESULT j_main_window_heads=60   j_main_heads_measured=60 of 60
RESULT j_red_main_heads=24 of 60   j_change_failure_rate=0.4000
RESULT j_red_heads_by_context={"closures":6,"env-matrix":4,"fast (3.13)":7,"fast (3.14)":7,
                               "nightly-ha (2025.2.0)":5,"nightly-ha (stable)":5,
                               "policy-docs":4,"record":16,"slow":1}
RESULT j_red_heads_only_record=8            RESULT api_failures=0
RESULT j_merged_prs_ever=518 (graphql totalCount=518)
RESULT j_prs_with_any_review_object=6 [230, 419, 424, 501, 522, 600]
RESULT j_review_states={"COMMENTED": 7}     RESULT j_prs_with_an_approving_review_by_other=0
RESULT j_merged_by={"tvofi": 518}           RESULT j_pr_authors={"claude": 3, "tvofi": 515}
```

### D11-01 — the split decided on the rubric, arm by arm

The two seats split, `critical` (v1) against `high` (v2), both honestly argued,
and with only two seats no majority could settle it. I re-measured both arms.

The rubric is `tools/audit/briefs/D11.md:87-88`, verbatim: *"`critical` — a merge
to `main` **can happen** with no review or with a red required check, or a job
executes text a seat did not write"*. **It is a modal bar — a capability bar —
not an event bar.** That decides the split.

**Arm 1, no review. Met unconditionally; not a sampling claim.** `0
pull_request` rules means the live ruleset **cannot ask any actor for a review**,
bypassing or not, and `ruleset_required_approvals=0` follows from the rule's
absence rather than from a setting. The consequence is measured at repository
scale, not in a window: **0 of 518** merged pull requests carry an approving
review by another account, **518 of 518** were merged by `tvofi`, and the author
set is `{tvofi: 515, claude Bot: 3}`.

**Arm 2, a red required check. Met as a capability, which is what the rubric
asks — and *not* as an event, which both seats correctly said.**
`current_user_can_bypass: "always"` is GitHub's own answer for the identity that
performed all 518 merges, and `bypass_mode: always` exempts it from **every**
rule in the ruleset including `required_status_checks`. Behaviourally:
**`j_heads_red_required_at_merge = 0 of 39`** — no merge in the sample landed
with a red required check. The five heads that fail the first-green test are
exactly #710, #711, #727, #738, #743, and every one went **red then green at the
same head before merging**; required contexts take the latest conclusion. The one
genuinely unchecked landing is `18d67a2`, **1 of 60** first-parent commits since
the ruleset activated — a direct push with no pull request at all, where 17 of
18 required contexts produced a run only *after* it landed — and it is the `v*`
release stamp `CLAUDE.md` itself assigns to `stamp.py` post-merge.

**Neither `high` nor `medium` fits.** `high` is "an obligation the record calls
enforced that nothing enforces" — but `docs/decisions/0005` records the *absence*
of review enforcement as deliberate and argued, so review is not an obligation
the record calls enforced. `medium` is "a detector with no live control", which
this is not. The rubric's own structure leaves `critical` or nothing.

**Verdict: `verified`, `critical`** — carried by arm 1 alone, with arm 2 met as
a capability plus one direct push.

**The metric correction v2 found is right and must travel with the finding.**
`C_github_review_object = 0/39` conflates two different objects. A review object
**is** reachable here — **6 of 518** merged pull requests carry one (#230, #419,
#424, #501, #522, #600; my set is identical to v2's), all 7 reviews `COMMENTED`,
four written by the author on his own pull request. So `0 of 39` is a property of
that 40-merge window, not a law. What is structurally unreachable is an
**approving** review — GitHub refuses self-approval and one account holds push —
so **0 of 518**, unreachable on 515 of them. The register must carry the
**arm-1 / arm-2 split** rather than one severity word, and must not quote
`0 of 39` as if it were repository-wide.

### D11-02 — verified as an ORDINAL claim with a dated count

The mechanism is unambiguous and I confirmed each half myself: `record` is one of
the live ruleset's 18 required contexts; `governance.yml:225` carries
`if: github.event_name != 'pull_request'`; and **`record` concluded `skipped` on
61 of 61 check runs across 39 merged pull-request heads** — not one reached any
other conclusion. A required check that reports `skipped` is satisfied for merge
purposes, so the disposition rule discharges **zero times before a merge**.

**Null control, mine:** at #738's head, **17 of 18** required contexts concluded
`success` and exactly one — `record` — `skipped`, with 0 failures and 0 contexts
producing no run. The skip is specific to `record`, not to the head or the
endpoint.

**The absolute count does not survive a window change.** Four windows, three
instruments:

| window | instrument | red heads | `record` | record-only | share |
|---|---|---|---|---|---|
| finder, 215 heads (Actions listing, capped at 1000) | `dora.py` | 37 | **20** | 11 | 0.5405 |
| verifier 1, 72 h to the pin, 136 heads | per-commit check-runs | 49 | **36** | 25 | 0.7347 |
| verifier 2, 60 post-ruleset heads | per-commit check-runs | 24 | **16** | 8 | 0.6667 |
| **mine**, 60 post-ruleset first-parent commits to the baseline | per-commit check-runs, `api_failures=0` | **24** | **16** | **8** | **0.6667** |

So: **file it as an ordinal claim — `record` is the single largest cause of a red
`main` — with a dated count beside it, never as a bare "20 of 37".** The ordinal
claim reproduces in all four windows and grows; in mine the runner-up is
`fast (3.13)`/`(3.14)` at 7 each against `record`'s 16, and leave-one-out (15 of
23) does not change the ranking. The finder's own denominator is 38, not 37 — its
disclosed 1000-run cap dropped one `nightly-ha`-only red head — and both
load-bearing numerators (20, 11) are exact.

**The remedy's second half is wrong, and I confirmed it directly.** Ranked change
#3 offers "require `record-status` instead". At #738's head `record-status` ran
**three times and concluded `failure` all three**. Requiring it would have refused
**#738's own merge**, for a main-side condition its author neither caused nor
could fix from the branch — exactly what the workflow's own comment argues. **The
first half (give `record` a pull-request arm over `merge-base..HEAD`) is
untouched and is the one to build.**

**Wording narrowing both seats owe the fixer.** Because the only merging identity
bypasses every rule (D11-01), *skipped-satisfies is not what lets these merges
through — the bypass is*. The mechanism sentence overstates for **this**
repository while being correct about GitHub. The measured consequence
(post-merge-only enforcement; `main` red at the baseline itself, where `record`
is the only `failure`) does not depend on it.

**Instrument caveat for the register:** `dora.py` **replays its own
`dora_runs.json` cache** when re-run from its header, as does `conformance.py`
with `conformance_raw.json`. A judge re-running "as the header says" is reading a
file, not the API. Both caches were shown genuine by a forced live re-fetch
(identical sets), and my window above was measured against GitHub directly.

### D11-03 — verified; both consequence metrics belong in the register

Reproduced exactly, and I read the predicate myself:
`.claude/workflows/policy_lint.mjs:3135`,
`const isPolicy = /^policy:/.test(title.trim())` — keyed on the **author's own
title**. Against `docs/decisions/0007:34-35`, which says `pr-contract` refuses a
body without an `## Approval` section *"mechanically, on every pull request"*.
That is the `high` anchor exactly: an obligation the record calls enforced that
nothing enforces as described.

The two consequence figures measure different things and the votes are **not
comparable** on them:

* **64 of 82** (0.7805) policy-touching merges, and **32 of 50** (0.6400) on the
  rule-text subset, merged under a title that switched the requirement **off** —
  this counts the size of the hole. Re-derived by v2 with production's ten globs
  **evaluated by node** and production `checkPrBody` **executed 82 times**
  (`exit codes {0: 64, 1: 18}`), set-for-set identical to the finder's
  (`F_only=[] V_only=[]`).
* **4 of 11** window commits merged with the gate off **and** no `## Approval`
  text at all — this counts what fell through it, and **#756, the pull request
  that added CODEOWNERS and decision 0008, is one of the four.**

Both are true; the register carries both. Leave-one-out on the headline gives 31
of 49 (0.633).

**CODEOWNERS cannot rescue it, and at the baseline it does not exist at all** —
I checked: there is no `.github/CODEOWNERS` at `ae36eff`. It was added
post-baseline in #756 and refutes itself in its own header ("Until that rule
exists this file claims nothing"), with the live ruleset confirming 0
`pull_request` rules. **0 of 5 candidate mechanisms can refuse an unapproved
policy change**, at the baseline and at the live head alike.

**Instrument trap to fix before this harness is reused** (it has not bitten —
both lists were re-derived from production and are right today):
`approval_gate.py`'s `POLICY_GLOBS` guard compares **cardinality only**. One glob
removed → `REFUSED: POLICY_GLOBS moved`; one glob **swapped** for a non-existent
path with the count unchanged → **passes silently** while the census shifts 16 %
(64 → 51). And the `RULE_RE` transcription that produces `32 of 50` is a second
transcription the guard does not cover **at all**. Separately: 20 of 82 squash
subjects are not the pull request's title, and the classification changes in none
of the twenty — so the shortcut is safe here and **not safe by construction**.

### D11-04 — the second half refuted by my own call

**I made the call the dispatch asked for, read-only:**

```
$ gh api repos/tvofi/heatpump_optimizer/private-vulnerability-reporting -i
HTTP/2.0 200 OK
{"enabled":true}
```

Private vulnerability reporting is **on**. The finder's evidence — *"the
repository's `security_and_analysis` block lists secret scanning and Dependabot,
not `private_vulnerability_reporting`"* — is an inference from a key's **absence**
in a block that never carries that key. **It was never executed:** the string
appears in the finder's `REPORT.md` prose only (3 occurrences, none a RESULT) and
in **none of the six harnesses**; `standards.py` computes
`bp_vulnerability_report_process = int(sec)` where `sec` is the SECURITY.md
existence sweep at `:125`. This is "a claim you checked by reading a payload is
not checked", landing on a governance seat.

**What survives, measured three ways at the baseline and live:** no `SECURITY*`
file anywhere in the tree; GitHub's own `community/profile` `files` block carries
**no security entry** (health 57 %); the org fallback `tvofi/.github` is **404**;
and `grep -rniE "report a vulnerability|security policy|vulnerabilit"` over
`README.md` and `docs/*.md` returns **0 hits**. So Scorecard's `Security-Policy`
really is 0/10 and `sc_security_policy=0` is correct.

**The consequence sentence that carried the `medium` is false.** "A reporter
today has no non-public channel" — there is one, and GitHub renders a *Report a
vulnerability* control for it. **The remedy shrinks from "there is nowhere to
report" to "add the file that points at the channel that already exists", and
ranked change #4's settings toggle is already on.** `low`, `hygiene` — a public
HACS integration that drives a heat pump has a working private channel that
nothing advertises: no file, no pointer, no response-time expectation.

### D11-05 — verified at `medium`, on the counts

Every figure reproduced and the perturbation moves (`boundary_files` 1 → 2 on a
corpus copy). The detector counts to 1, which is the kind that under-fires, so I
ran the over-fire check **twice** and it survived both:

* my own grep of `.claude/rules/`, `CLAUDE.md` and `.github/PULL_REQUEST_TEMPLATE.md`
  for `not (as )?instructions|untrusted|prompt injection` returns **0 hits**;
* v2's deliberately wider 9-pattern net returns **2** files, the extra one being
  `tools/audit/briefs/orchestrator.md`, whose matching sentence is the
  **opposite** of a boundary ("…are not instructions you relay. They are
  instructions you follow.").

The only corpus file that matches at all is `tools/audit/briefs/D11.md:47` — this
audit's own brief, naming OWASP as something to score against, binding no seat
afterwards. So the finder's `boundary_files=1` and v1's `binding=0, brief-only=1`
are the same fact under two definitions; they are not a disagreement.

**The door is open, measured rather than inferred:** `GET
/repos/tvofi/heatpump_optimizer/interaction-limits` returns **`{}`** — the one
setting that would close all five untrusted authoring surfaces at once is not
set. 5 of 6 surfaces are writable by a non-collaborator (discussions are
disabled). **Nobody has walked through:** my own repo-wide census
(`{tvofi: 515, claude Bot: 3}` over 518 merged pull requests) agrees with v1's
larger one (526 PRs, 246 issues, 737 comments, all owner-authored). That is
exactly the finder's own hedge and it is the right reason for `medium` and not
higher.

`stop_rule_class` is `hygiene` from what the number shows: **no job has executed
text a seat did not write** — the rubric's third `critical` arm is measured and
not met — so what is missing is a policy sentence and a narrower write grant,
which is wording and structure. If any non-owner text ever enters a seat's
context, the class becomes `bug` and the severity moves.

---

## Nothing was `unreproduced`

All eight findings reproduced from their own harness headers, and **all eight
perturbations moved in the stated direction**. No harness is void. The four
verdicts that are not `verified` are `weakened` on severity, metric definition or
a refuted sub-claim, never on a number that failed to reproduce.

## Exposure

Read-only, as this panel's exception permits and requires be recorded.
`gh api`: `repos/tvofi/heatpump_optimizer/rulesets/22628467`,
`/private-vulnerability-reporting`, `/community/profile`, `/interaction-limits`,
`/commits/{sha}/pulls`, `/commits/{sha}/check-runs?filter=all`, `/pulls/{n}`,
`/pulls/{n}/reviews`, `repos/tvofi/.github` (404); `gh api graphql` for the
merged-pull-request / review / merger census, paginated to exhaustion.
The repository's own git history at and before the baseline. **Nothing was
created, edited, closed, commented on, merged, pushed, dispatched or re-run; no
workflow was run; the ruleset was read and never modified; no branch, tag,
worktree or remote was created.** `tests/stress.py`, `./tests/run.sh` and the
gate lock were not touched.
