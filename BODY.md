The merge train's pre-flight (`queue_pre_flight.findings_gate`, which runs `carry_audit.audit`) parked three `Fix review: merge` verdicts. In each, `carry_audit.items()` read evidence as finding items with no `Carry:`: #2513 item 3b97e1aa (issue comment 6314156311), #2544 item aeeb9432 (6314170570) and #2547 item b579380b (6315224098). This change adds a barrier at the source, in two parts (owner-approved 2026-10-21: "do that").

1. **The prompt.** `tools/audit/seat/cloud_dispatch.py` now tells the reviewer to put a blocked verdict's block under `## Block`, and each finding the PR does not settle in its own bullet under `## Findings` with its own `Carry:`. Everything else goes under `## Evidence`. `fix-review.md` is unchanged: it defers the verdict's shape to the dispatch prompt ("in the exact shape your dispatch prompt gives"), so no policy file or role contract changes.
2. **The classification.** In `tools/audit/carry_audit.py`, an item under a verdict's `## Evidence` heading is a finding when it opens with `LEAD`, sits under a lead, says a `DEFERRED` word anywhere, or says a `NONBLOCK` word outside the one carve-out.

**The carve-out, narrowed in round 2.** Round 1's review blocked on the carve-out's scope. It dropped every *sentence* matching `NOT_REQUIRED` before reading `NONBLOCK`, so a nit or defect sharing a sentence with "not a required check" passed. Now `NOT_REQUIRED` matches only the check's own clause: `not (a) required context|check`, optionally followed by a block-state phrase (`does not block`, `is not blocking`, `not blocking`, `non-blocking`). That phrase may be joined to the clause only by `,`, `and` or `it`, and it may not lead a `:`. Only that match is removed (`claims = NOT_REQUIRED.sub(" ", t)`) before `NONBLOCK` reads the rest of the item. The `SENTENCE` splitter is gone. The prompt now says the same: "evidence only in the clause saying it is not a required check and does not block, never in the rest of its sentence". The round-1 wording ("only in a sentence saying it is not a required check") made the sentence the exempt unit.

Alternatives, and why each lost:
- **Exempt a `NOT_REQUIRED` sentence only when every `NONBLOCK` hit in it is a block-state phrase** (the review's second option). This keeps the sentence splitter and a second pass over the hits. It is also wider: "The floor is written 0.27 K low (not a required check) and is not blocking." has only block-state hits, so it would pass. Removing the clause catches it with one regex and no splitter.
- **Exempt `NONBLOCK` under `## Evidence` entirely.** This frees #2441's nit and #2465's defect, so it was refused in round 1. The self-test rows for both still stand.
- **Allow `;`, `so` or `)` as joiners.** Each of these frees one of the review's attack sentences, or its `semicolon` case, which is already a finding. Left out.

## Head

`795b8befd25a9dd542c982124d9c2277bb2e5de0`, pushed to `handoff/r10-verdict-item-barrier`. It is the PR head `90788b1e5ea8ce015e7ae6c432d308d7a5aab476` plus two commits:
- `50c452947`: carry_audit's carve-out, the self-test rows, the harness arm and the mutants;
- `795b8befd`: the prompt wording and its self-test row.

Merge base: `5d433771aa88bbfd49b8868a9b53ea1241ab85a3` (`git merge-base origin/main HEAD`). Every figure below was taken at `795b8befd` unless it names another revision. "Base" means 5d433771a, and "round 1" means 90788b1e5.

origin/main has since moved to `e7c664856` (read 2026-10-21T15:01Z). The delta touches two hashed lock files and a delivery row, none of them in this diff. `git merge-tree --write-tree origin/main HEAD` exits 0 with tree `13ab941b0`, so the branch was not merged.

## Mutation proof

Each mutant was applied to a clean worktree at the head, then `python3 -I tools/audit/carry_audit.py --self-test` (or cloud_dispatch's) was run, and the file was restored.
- **Failing first.** The self-test rows were added before the fix, at round 1's classification: `carry_audit self-test: 188 checks, 5 failed`. The failing rows:
  - `a nit beside a not-required check's clause is a finding`
  - `a minor defect beside ...`
  - `a defect beside ...`
  - `a parenthetical defect beside ...`
  - `a colon-led nit beside ...`

  The null-control row (`, and it is not blocking` is freed) passed.
- **M-C**: the claims line reverted to round 1's sentence carve-out. `189 checks, 5 failed`, the same five rows.
- **M-D**: the clause tail of `NOT_REQUIRED` deleted, so only the bare phrase is freed. `189 checks, 5 failed`:
  - `under the Evidence heading a check that is not a required context and does not block is no finding`
  - `` ... `not required check` reads too ``
  - `the Evidence heading reads in any case and with words after it`
  - `` the check's clause frees `, and it is not blocking` (null control) ``
  - `` ... and `, non-blocking` ``
- **M-E**: the `(?!\s*:)` lookahead deleted. `189 checks, 1 failed`: `a colon-led nit beside a not-required check's clause is a finding`.
- **M-A**: the whole `## Evidence` arm of `items()` deleted (4 lines). `189 checks, 37 failed`. Under M-A the replay prints `v2544_reshaped=1 v2544_planted=2 v2544_attack=2`, the base's figures.
- **M-B**: every new prompt sentence in `cloud_dispatch.py` deleted. `cloud_dispatch self-test: 32 checks, 2 failed`:
  - `the reviewer is told to separate findings, each with its own Carry:, from evidence`
  - `the reviewer is told the not-required carve-out is the check's clause, never its sentence`
- **M-B'**: only the carve-out sentence reverted to round 1's wording. `32 checks, 1 failed`, the second of those two.
- **Every predicate alone.** `python3 dev/audit/harnesses/r10_carry_parser_mutants.py` gives `RESULT sites=166 unmapped=0 mutants=232 survived=0`, with `M0 failed=0` (base: `sites=152 unmapped=0 mutants=190 survived=0`). It now carries:
  - the open form as its own mutant, `I-ev-sentence` (round 1's sentence carve-out): killed, failed=5;
  - `I-ev-carve` and `I-ev-claims` (no carve-out): killed;
  - one mutant per piece of the clause: `P-notreq-a`, `-clause`, `-comma`, `-and`, `-it`, `-colon`, all killed;
  - the generated `V-NOT_REQUIRED-*` alternatives (`context`, `check`, `does not block`, `is not blocking`, `not blocking`, `non-?blocking`), all killed.

  Round 1's `I-ev-split` and `P-sentence-semi` were removed with `SENTENCE`.

## Unpinned sites

n/a: `r10_carry_parser_mutants.py` pins every site the diff adds in `carry_audit.py` (unmapped=0, survived=0 above). `cloud_dispatch.py`'s new prompt text is pinned by the M-B and M-B' rows.

## Null control

- **The check's own clause is still freed.** `python3 dev/audit/harnesses/r10_verdict_item_barrier.py` prints `v2544_reshaped=0`: #2544's "it is not a required context and does not block the PR" reads as evidence at the head, as at round 1. The `--whatif` sweep flags #2544 aeeb9432 at the base and not at the head.
- **The fix adds no false positives.** Over the real corpus, the `--whatif` FLAGGED set at the head is identical to round 1's (`comm` of the id sets: empty both ways). No live verdict sentence relied on the wider carve-out.
- **The planted control** (a deferred defect under `## Evidence`) is refused for all three verdicts: `v*_planted=1`.

## Figures

- **Replay, both ends and round 1.** Instrument: `python3 dev/audit/harnesses/r10_verdict_item_barrier.py --fetch`. It prints `fetch_2513/2544/2547=identical` against the live comments. The harness header defines the forms. The new `attack` form adds one Evidence bullet whose defect shares its sentence with a not-required check ("composed-proof is not a required check, and the stale-head guard misses a deleted ref, not blocking."). Head and round 1 were run with this file; the base was run with this harness copied into a base worktree.

  | form (2513 / 2544 / 2547) | head 795b8befd | round 1 90788b1e5 | base 5d433771a |
  |---|---|---|---|
  | verbatim | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 1 / 1 |
  | evidence | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 1 / 1 |
  | reshaped | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 1 / 0 |
  | planted | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 2 / 1 |
  | attack | 1 / 1 / 1 | **0 / 0 / 0** | 1 / 2 / 1 |

  The attack row reads 0 only at round 1: the open class, now closed.
- **The review's attack, re-run.** The four same-sentence attack sentences from the review's class_attack.py (on the bus ref verdict/2571 at 378816bc, under evidence/) are self-test rows. Each is a finding at the head, as above. Its `semicolon` and `abbrev e.g. split` cases were already findings.
- **Corpus.** The last 80 merged PRs by update time over REST, plus #2513, #2544, #2547 and #2556: 83 distinct PRs, fetched 2026-10-21T14:43:11Z with `gh api --paginate --slurp repos/tvofi/heatpump_optimizer/issues/<N>/comments?per_page=100` and `pulls/<N>` bodies. It is a live corpus, so these counts describe that fetch only.
  - `python3 -I tools/audit/carry_audit.py sweep --prs <83> --from-dir DIR` prints `CARRY-AUDIT: 124 finding item(s): 83 routed, 38 unrouted, 3 bad destination(s)` at the head, round 1 and the base. The sorted UNROUTED/BAD lines hash identically: sha1 `b4c16a2a…` at all three.
  - `python3 dev/audit/harnesses/r10_verdict_item_barrier.py --whatif DIR` gives `whatif_verdicts=58`, and `whatif_flagged=33` at the head, 33 at round 1 and 17 at the base. `comm` of the FLAGGED ids:
    - head vs round 1: empty both ways;
    - flagged at the base and not at the head: only `#2544 6314170570 aeeb9432`.
- **The finder's instrument.** `python3 -I tools/audit/carry_audit.py pr N` prints the same line at the head and the base (read 2026-10-21T15:01Z):
  - #2513: `2 finding item(s): 2 routed, 0 unrouted`;
  - #2544: `1 ... 1 routed, 0 unrouted`;
  - #2547: `1 ... 0 routed, 1 unrouted`.

  It reads flat at both ends because posted verdicts are old-format text the fix rightly leaves alone. The replay above is the companion that moves.
- **The generator, run** (fixer.md step 10). `python3 -I tools/audit/seat/cloud_dispatch.py --role reviewer --head <40×a> --pr 7 --nonce n0nce --env-id e --model m --repo o/r`. `grep -c` on the rendered prompt:

  | revision | `never in the rest of its sentence` | `evidence only in a sentence saying` | `## Evidence` |
  |---|---|---|---|
  | head | 1 | 0 | 1 |
  | round 1 | 0 | 1 | 1 |
  | base | 0 | 0 | 0 |
- **The class, enumerated** (fixer.md step 8). Two rules enumerate the seams.
  - **Seams in the parser.** Every point in `items()` where a `NONBLOCK`/`DEFERRED` read sees less than the item's text: `awk '/^def items/,/^def carry_segments/' tools/audit/carry_audit.py | grep -nE "NONBLOCK\.search\(|NOT_REQUIRED\.|DEFERRED\.search\("`. It returns five lines:
    - `claims = NOT_REQUIRED.sub(" ", t)` and the `NONBLOCK.search(claims)` read: closed in this diff (the only subtraction);
    - `DEFERRED.search(t)` beside it: reads the whole item;
    - `BLOCK_HEADING ... NONBLOCK.search(sec)` and `note_sec = NONBLOCK.search(sec)`: they read the heading, not the item, and are unchanged from main;
    - `NONBLOCK.search(t)` in the other verdict arm: reads the whole item.

    The AST census in `r10_carry_parser_mutants.py` (`sites()`: 166 sites, 0 unmapped, 0 survived) covers the rest.
  - **Generators that teach the carve-out.** `git grep -nE "not (a )?required (check|context)" -- .claude tools dev/governance` returns:
    - `tools/audit/carry_audit.py`: its docstring, now "outside the clause", and its self-test rows;
    - `tools/audit/seat/cloud_dispatch.py`: closed in this diff;
    - `dev/governance/config/cfr_exclusions.json`: two hits in a citation about the `record` job, unrelated to verdicts.
- **Cheap checks at the head** (`PYTHONPATH=tests/hastub`):
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`
  - `python3 -I tools/audit/seat/tmp_paths.py --check`: `tmp_paths: 0 refused`
  - `python3 tools/audit/archscore/score.py --diff 5d433771a`: `Architecture score: dS +0.0000 NULL`
  - `python3 tests/closure.py select --diff 5d433771a`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names `tests/entities.py`
  - `/opt/hpo/venv-ci/bin/python tests/entities.py` (3.14.7): `ALL 2375 ENTITY CHECKS PASSED`
  - run_always:
    - `/opt/hpo/venv-ci/bin/python tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`
    - `python3 tests/env_drift.py --claims-only 5d433771a`: `claims hygiene: 5d433771a ok`
    - `python3 tests/closure.py selftest`: `ALL 124 closure shrink pins PASSED`
    - `python3 tests/layout.py`: `layout self-test: ok`
  - `git diff --stat 5d433771a...HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md tests/golden` is empty.

## Red checks

- `nightly-status` (red on 90788b1e5). It grades the last concluded scheduled run of `tests.yml` on main (`tests.yml` header: "Reads the last CONCLUDED scheduled run of this workflow"), not this diff. The diff touches `tools/audit/carry_audit.py`, `tools/audit/seat/cloud_dispatch.py`, two `dev/audit/harnesses/` files, its delivery row and `tests/closures.json`, none of which that run reads. The cheaper detector already exists: the check itself, on main. This PR owes nothing for it.

## Forward-carry

n/a: no finding here changes how a later stage must work; the code-owned local prompt `.claude/workflows/web-fix-wave.js` still asks only for RESULT lines and the pre-flight parks such a verdict (fail-closed), as round 1 recorded

## Friction

none
