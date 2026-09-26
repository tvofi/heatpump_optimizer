# Class sweep: I5 — docs, comments or a compliance checklist drift stale against the code

Round 9, Phase D, thread S2. Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`
(v6.7.1). Also checked at `origin/main` = `db878b2` (has merged #1641, #1642,
#1643 since the baseline).

## Method

I5 is not one production seam; its 19 canonical findings are 8 different
shapes of the same property ("a prose claim, a help string, a comment or a
translation names a fact — a number, a list, a state, a data flow — that the
code no longer delivers"). Round 9's finders already built a per-shape
checker for each shape, and several of those checkers already enumerate
*every* claim of their shape across the whole package (not only the
demonstrated instance): `claims.py` checks all 82 README claims,
`services_claims.py` all 59 service-schema claims, `entity_counts.py` every
entity-count claim in README/architecture.md/configuration.md,
`comment_numbers.py` every numeric citation in the three files it names,
`card_comment_names.mjs` every private-member mention in the card's own
comments, `m3_translation.py` all 74 translated entity names.

The class-level enumerator (`enumerator.py`) is the `D14.md` step-3 wrapper:
it runs every one of those per-shape checkers, **plus their four siblings
that were built during finding but did not themselves surface a round-9
finding** (`architecture_claims.py`, `setup_claims.py`,
`scan_const_numbers.py`, `scan_qualified_refs.py`) so the sweep also covers
shapes the finders checked and found clean, not only the ones that flagged.
A nonzero `*_false`/`*_mismatch`/`*_wrong`/`*_unfindable`/`*_stale` count from
any of those 19 sub-checkers is a seam.

## Positive control

`enumerator.py` re-runs the harness each finding's `seam_rule` names and
reads the same `RESULT` line the finding cited. All 19 findings reproduce at
baseline, with the same counts the judge recorded:

```
$ PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/I5/enumerator.py
D4-s2-09                                      flagged=16.0   (8 en + 8 sv bare-unit help texts)
D5-s1-01                                      flagged=4.0    (stale_facts)
D5-s1-02                                      flagged=2.0    (unhonoured_promises)
D5-s1-03                                      flagged=1.0    (doc_claims_card_lags)
D5-s1-05                                      flagged=5.0    (unfindable_field_refs)
D6-s2-01/entity_counts                        flagged=1.0    (disagreeing_claims)
D5-s2-01                                      flagged=12.0   (card_stale_private_names)
D5-s2-02/03                                   flagged=4.0    (comment_number_mismatches)
D5-s2-51                                      flagged=0      (inspected by hand -- see below)
D6-s1-01/02/03                                flagged=4.0    (claims_false)
D6-s2-02                                      flagged=1.0    (doc_entity_counts_wrong)
D6-s2-03                                      flagged=1.0    (behaviour_claims_false)
D6-s2-04                                      flagged=1.0    (howitworks_claims_false)
D6-s2-05                                      flagged=1.0    (services_claims_false)
D8-s3-02                                      flagged=1.0    (concept_mismatch)
(widen) architecture_claims                   flagged=0.0
(widen) setup_claims                          flagged=0.0
(widen) scan_const_numbers                    flagged=0.0
(widen) scan_qualified_refs                   flagged=19.0   (docstring: expect 19, all false positives)
```

`D5-s2-51` (optimizer.py comments describing a warm-start/buffer-series data
flow the code does not have) has no single `RESULT` count to key on;
`dataflow_comments.py`'s own output (`model_sequence_writes=0`) is read by
hand against the two comments `grep` finds, confirming the described flow is
absent both at baseline and on main.

D11-s2-04 (CLAUDE.md rule 1 quoting a mode line `tests/closure.py` does not
print) is a grep over policy prose, not a runnable claims-checker; its own
`seam_rule` is re-run directly and still finds the same two backtick spans at
both baseline and main.

Checked against the ledger (`tools/audit/bugclasses.json`): I5 has no prior
round entry — this is the class's first round, so there are no pre-fix
historical instances to re-find beyond the 19 in-round findings.

**Both checked at `origin/main`: all 19 counts are unchanged (see the
`--base` run against the main worktree) — none of the 19 has been fixed by
#1641/#1642/#1643, and the four widening siblings still find nothing new.**

## Null control and perturbation

`null_and_perturb.py`, run against `entity_counts.py` as the representative
shape-checker (it already mixes a hold and a defect at baseline, so both
directions show in one file):

```
$ python3 tools/audit/round9/D14/sweep/I5/null_and_perturb.py
RESULT baseline_disagreeing_claims=1 count
RESULT null_control_disagreeing_claims=0 count  (doc fixed to match code)
RESULT perturbed_disagreeing_claims=1 count  (one-line re-introduction elsewhere)
RESULT null_and_perturbation_ok=1 bool
```

Patching the one disagreeing claim (`docs/configuration.md:196`, "All 74
entities" -> "All 75 entities") drops the count to zero with no other claim
moving (null control). Re-introducing a one-line stale count somewhere else
that currently holds (`README.md:417`, `75` -> `80`) moves the count back to
1 (perturbation). The script reverts both edits before exiting; the working
tree is unchanged.

`unit_typography.py`, `card_comment_names.mjs` and `comment_numbers.py` each
already print explicit `RESULT ..._bareC=0` / hold rows / `OK` lines
alongside their nonzero counts, which is the same null-control shape
(claims of the right kind that do *not* disagree, checked by the same code
path) — not re-demonstrated here to avoid re-running the heavier ones.

## Disposition

All 19 canonical findings: **`instance`**, each with the probe already named
by its `seam_rule` (the failing `RESULT`/`ROW`/`MISMATCH` line above), which
the class's fixer(s) reuse as the failing test. See `S2.json`.

The four widening siblings that returned zero (`architecture_claims`,
`setup_claims`, `scan_const_numbers`) are **non-findings**: every claim they
check holds at both baseline and main, so no additional I5 seam.

`scan_qualified_refs` (19 rows) is **`not applicable`**: its own docstring
states the expected shape (19 rows, all false positives — entity ids like
`sensor.hp_t4`, filenames like `services.yaml`, and `datetime.weekday`, none
of which is a `module.attr`/`Class.member` reference the class's rule is
about) and this sweep re-verified none of the 19 rows is a real stale
reference.

## Count

N = 19 verified findings + 0 sweep-confirmed instances beyond them = **19**.
N >= 3, so **`rca: true`** (also independently true: this is the class's
first round, so it is not yet `barriered`, but 19 >= 3 sets RCA on the count
alone). Root-cause and barrier proposal are for the RCA seat, per
`defect-root-cause.md` and `root-cause.md` — this sweep does not fix or
propose the fix, only enumerates and dispositions (per the brief).

## Barrier proposal (for the RCA seat to size, not built here)

The 19 instances share no single production seam, so a single CI check
cannot barrier the whole class. What they share is *procedure*: none of the
8 shapes has a standing check that runs docs/comments/strings against the
code they describe outside an audit round. A plausible barrier is a nightly
(not per-PR, to keep gate seconds down) lane that runs all 15 shape-checkers
above plus the 4 widening siblings and fails on any nonzero count, so a
future PR that changes one of the described facts (an entity count, a
service schema, a translation, a private member name) without updating its
prose is caught before the next audit round rather than by it. Sizing that
lane's gate-seconds cost and whether it belongs in CI vs. nightly is a
judgement call for the RCA seat, not this sweep.

## Exposure

None: no `docs/` read beyond what the brief's own inputs and the harnesses
already touch, no GitHub read.
