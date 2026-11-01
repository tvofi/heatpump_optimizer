R10-996-RUNNER-CLAIMS, third PR: carry 3 (P214, ruling `dev/programme/triage/s6-batch41.md#P214`, ACCEPT, V127) only. Closes nothing: the group has no issue wired (#3099 tracks the part).

When main's claim driver refuses a merge, the merge-main bot answered only `skip-driver-refused tests/golden/claimed_drift.txt`, as it did on #2872 at `fe964895e`. The driver's decision text was already on the merge's stderr: `tests/env_drift.py`'s `merge_claim_refusal`, printed by `run_merge_driver` after its `MERGE-CLAIM: refused <path>` line. `merge_tree` captured that stderr, and `decide` dropped it.

The fix is `claim_refusal(driver_err)` in `tools/pr/merge_main_bot.py`. When the stderr holds the claim driver's `MERGE-CLAIM: refused ` line, `decide` appends that stderr under today's status line, verbatim and indented four spaces. Otherwise it appends nothing.
- The bot writes no summary of its own, so the driver's message stays the one source and its wording lives in `env_drift.py` only.
- The one string the bot keys on is the driver's refusal-line prefix, `CLAIM_REFUSED`. The self-test arm drives the real `tests/env_drift.py --merge-claim-file`, so a change to that prefix turns the arm red rather than silently dropping the relay.

**File ownership.** `tools/pr/merge_main_bot.py` belongs to this group by the P214 ruling's `edit-brief`, which the orchestrator has queued as the roster's `edit-brief`/`set-files`. The roster's `files` at this base still lists only `tests/env_drift.py` and `tests/golden/claimed_drift.txt`.

**Code owners and policy.** `tools/pr/merge_main_bot.py` is not code-owned. `python3 dev/audit/rounds/round6/D11/fix/codeowners_gap.py` lists it as `NO-PR-JOB tools/pr/merge_main_bot.py` (on the enforcement surface, run by `merge-main.yml` on a push to `main`, with no owner pattern), and it is not a policy file named in `CLAUDE.md`. No claim file is touched and no claim is decided.

**One design choice, and the alternative that lost.** The relay carries the drivers' whole stderr for that merge, not only the claim driver's block. When a ledger driver resolved a file in the same merge, its `LEDGER-MERGE: resolved` lines appear too (see the #2872 replay under `## Figures`). The alternative was to cut out the claim block alone. That would mean parsing where the claim driver's text ends, keyed on wording of both drivers (the claim message's own lines also open with an uppercase `WORD:` prefix). That parsing is the second reader the ruling forbids. The extra lines are the drivers' own accurate output.

## Head

`1e1d346b206bdad37f63e38c83ea268f6c48e9c3`, measured against merge base `7f849a24911e9d52336bd79ea9ce63c67416a6ae`, `origin/main`'s tip at 2026-11-01T21:25:36Z.

This head merges `origin/main` into `30ce8f459` five times, as main moved during each `prepr.sh` run: `c88d552c7` (#3051, #3074), `ddf4bfd73` (#3073), `56630e7e6` (#3097), `f04b25a00` (#3047) and `7f849a249` (#3118, #3141, #3142). All five merges were clean, and none of main's new commits touches `tools/pr/merge_main_bot.py` or `tests/env_drift.py`. #3047 changed `tests/golden/claimed_drift.txt` on main. This branch never wrote that file, so its copy is main's, as the byte-identical check below shows. The authored commits are:
- `d8e19bf4e`: the self-test arms, red with the unchanged bot.
- `30ce8f459`: the fix.

After that last `prepr.sh` run, main moved once more, to `25c46e76e` (#3148, an autofix record). I did not merge it: every one of the five cycles above was overtaken the same way during its `prepr.sh` run. Before the push, `git merge-tree --write-tree origin/main HEAD >/dev/null && echo "MERGE-TREE CLEAN"` printed `MERGE-TREE CLEAN`, and `git diff --name-only 7f849a249 25c46e76e` names none of `tools/pr/merge_main_bot.py`, `tests/env_drift.py` or either claim file. The orchestrator or the merge-main bot can carry the head forward without a resolution.

I first measured at `30ce8f459` against `407eb0cb3`, where `prepr.sh` returned rc=0. After main moved, every figure below was re-taken at this head unless it names another: the self-test, the three mutants, the scoped gate, the architecture score, the structure ratchet, the claim and version checks, and `prepr.sh`.

## Mutation proof

**Failing first.** At `d8e19bf4e` (arms added, bot unchanged), `python3 tools/pr/merge_main_bot.py --self-test` printed `merge_main_bot self-test: 46 checks, 1 failed`. The failing arm was `FAIL a claim conflict the driver refuses relays the driver's own message under today's line, naming each scenario both sides rewrote with both sides' lines  [skip-driver-refused tests/golden/claimed_drift.txt]`: the #2872 line, exactly. At the head: `46 checks, 0 failed`.

One mutant per rule, each applied in the tree to the predicate and restored. `git diff --quiet && echo RESTORED` printed `RESTORED`, then the self-test printed `0 failed`.
- **M1, drop the relay.** `decide` no longer appends `claim_refusal(driver_err)`. Result: `1 failed`, `a claim conflict the driver refuses relays the driver's own message ...`.
- **M2, drop the fallback to the filename list.** I deleted `claim_refusal`'s `if not any(l.startswith(CLAIM_REFUSED) ...): return ""`, so any stderr is relayed. Result: `4 failed`:
  - `a claim driver that cannot be run leaves today's filename list, byte for byte`
  - `a merge with no claim conflict (a ledger driver refusing) prints exactly today's line`
  - `decide: a driver that refused is not pushed (skip-driver-refused led.json)`
  - `a ledger conflict its driver refuses is left for a human`
- **M3, key on any driver's refusal, not the claim driver's.** I replaced `l.startswith(CLAIM_REFUSED)` with `"refused" in l`. Result: `3 failed`: the same list less the cannot-run arm, whose stderr says `not found` and never `refused`.

## Null control

Three self-test arms pin today's output byte for byte, and each is green at both ends: `d8e19bf4e`, where the arms are new and the bot is unchanged, and the head.
- **Binding control 1, the driver cannot be run.** `merge.claimnotes.driver` is set to a command that does not exist. The status is `skip-driver-refused tests/golden/claimed_drift.txt`.
- **The driver is uninstalled.** `git config --unset merge.claimnotes.driver`, so git's text merge conflicts and no driver prints anything. The status is the same line.
- **Binding control 2, no claim conflict.** A ledger driver refuses while the claim driver is installed. The status is exactly `skip-driver-refused led.json`.

The pre-existing arms `decide: a driver that refused is not pushed (skip-driver-refused led.json)` and `a ledger conflict its driver refuses is left for a human` also stay green at the head.

Binding control 3: `git diff --quiet 7f849a24911e9d52336bd79ea9ce63c67416a6ae HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt && echo "CLAIM FILES BYTE-IDENTICAL"` printed `CLAIM FILES BYTE-IDENTICAL`. The same `git diff --quiet` over `VERSION`, `custom_components/heatpump_optimizer/manifest.json` and `RELEASE_NOTES.md`, with `&& echo`, printed `VERSION MANIFEST NOTES UNTOUCHED`.

## Figures

- **Binding control 4, the #2834 shape.** The new arm builds a throwaway repository in which both sides rewrote the claims of `coord_a` and `coord_b`. `.gitattributes` routes the claim file to `claimnotes`, which is configured as the real `tests/env_drift.py --merge-claim-file %O %A %B %L %P`.
  - The arm asserts that the first line is today's `skip-driver-refused tests/golden/claimed_drift.txt`.
  - It asserts that the indented rest contains `env_drift.merge_claim_refusal(base, ours, theirs)`, the production function's own text, not a copy of its wording.
  - It asserts that the rest names `coord_a: this branch ['ours a']; the merge brings in ['main a']` and the same for `coord_b`.
  - It runs inside `python3 tools/pr/merge_main_bot.py --self-test`, which reports `46 checks, 0 failed` at the head.
- **The finding's instance, replayed.** #2872's head `fe964895e628e0fc54762f9e80dc6098ff606e0b` was planned against main `34cd75bf1` (#2745's merge, which added `negative_prices` and `summer_dhw_only`). `plan_one(repo, head, main, mergeable=False, same_repo=True, pins=lambda: [])` was loaded from each end's copy of the bot. The repository was a worktree at `34cd75bf1`, so the driver and `.gitattributes` were main's at that time.
  - Base copy (`git show origin/main:tools/pr/merge_main_bot.py`): `skip-driver-refused tests/golden/claimed_drift.txt` and nothing else.
  - Head copy: the same first line, then the indented stderr. It includes `MERGE-CLAIM: refused tests/golden/claimed_drift.txt` and that driver's `CONFLICTING CLAIMS: both sides rewrote the claim list -- this branch claims ['config_flow', 'coord_all_features', 'coord_dhw', 'coord_grid_fee', 'coord_minimal', 'coord_two_zone'] and the merge brings in [... 'negative_prices', 'summer_dhw_only']`, together with the two `LEDGER-MERGE: resolved` blocks.
  - Null control: the same call against today's tree (`origin/main`'s driver, after #3066) prints `merge` at both ends. #2872's disjoint shape merges cleanly under the per-scenario driver, which is why the in-tree arm uses #2834's shape instead.
- **Class.** `git grep -n "driver_err" tools/pr/merge_main_bot.py` enumerates every place the bot reads the drivers' stderr. Each site's disposition:
  - `merge_tree`: returns it.
  - `plan_one`: passes it through.
  - `decide`'s refusal test: unchanged.
  - `decide`'s `skip-driver-refused` return: closed in this diff.

  `skip-driver-refused` is the bot's only status built from driver output, and no other status relays it.
- **Scoped gate.** `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` with `scope.run` empty. The `run_always` lines run inside `prepr.sh` below.
- **prepr.** `bash tools/pr/prepr.sh <this body>`, run with no closures skip. At `30ce8f459` it returned `PRE-PR: 30ce8f4592b887374c21ab58cdca455a9aad2b1d 0000000000000000000000000 rc=0`. Its `ci predict` step printed `CI PREDICT: no closures, fast, governance or instrument red predicted`, and its `unpinned sites` step printed `the diff adds no unpinned mutation site`. Its `closures` step printed `scoped recordings are covered; left to CI: tests/harness_headers.py`. I ran the same command at this head, on this final body, before the handoff push. It returned rc=0 with the same `ci predict` and `unpinned sites` lines, and its `PRE-PR:` line names `1e1d346b206bdad37f63e38c83ea268f6c48e9c3`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 7f849a24911e9d52336bd79ea9ce63c67416a6ae`: `Architecture score: dS +0.0000 NULL`. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

none: no CI has run on this branch yet. Locally, `prepr.sh` and its CI-predict step predict no red (see `## Figures`).

## Unpinned sites

`tools/pr/prepr.sh` step 6d: `skip     unpinned sites         the diff adds no unpinned mutation site`. The bot's own self-test pins the three new predicates, as the three mutants under `## Mutation proof` show.

## Forward-carry

- Carry 3 (P214), the group's carry in `dev/programme/rosters/wave-r10-groups.json` (R10-996-RUNNER-CLAIMS `carry[2]`): built in this PR. `claim_refusal` relays `merge_claim_refusal`'s text under `skip-driver-refused`, and the self-test pins it. Carry: dismissed: fixed in this PR
- Carry 1 (P196, per-scenario three-way merge, `dev/programme/rosters/wave-r10-groups.json` `carry[0]`): untouched here, built in #3066 (`07207ce30`). Carry: dismissed: fixed in #3066
- Carry 2 (P209, union of disjoint claim additions, `dev/programme/rosters/wave-r10-groups.json` `carry[1]`): untouched here, built in #3066 (`07207ce30`). Carry: dismissed: fixed in #3066

## Friction

none
