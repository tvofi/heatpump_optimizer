# Design: R11-OWNER-FEATURES-SPLIT (revision 5: freeze in place)

Answers `Design review: revise c1f6ce2ecf cost` (daf6aa17e4) with a different shape. Base e84856520dc4de8d70b68d67a206c6f2278351ad; no predecessor handoff. Owner order, no finder harness: owner report. Owning seam: tests/features.py and its successors; tests/entities.py owns the check. **This revision replaces revisions 1-4.** Their partition, swap-run gate, reference rewrite and mutation re-key are not built.

## Decisions

- **Freeze, not split: pending owner confirmation.** Orchestrator decision under mandate 6893738184, taken under the mandate's 5-minute rule: "owner silent >5 min after being asked at 17:30Z: option B. tests/features.py stays frozen in place — no row re-keyed; new tests go in seam scripts." The owner reverses it by authorising the fork-drive re-key above its cap (Cost to reverse, below).
- **Why the split lost.** The re-key the split needs (C1: no row re-keyed without its kill re-driven in its part) cannot fit the 150000 CPU-s cap. On a stratified sample stopped early, the expected cost is at least 372156 CPU-s, servers excluded. The 340 rows first reached in spans 0-2 alone need at least 166731 for the find pass. The evidence is on the spike at `handoff-wip/r11-owner-features-split-spike` ef2d5cd716 (`git fetch origin handoff-wip/r11-owner-features-split-spike`; the command is in `## Figures`).

## 1. What freezing means

tests/features.py keeps all 252 spans, its text and every behaviour; it runs where it runs today (`tests/run.sh`, `case_select.SCRIPTS`, `tests/closures.json`, `tests/case_closures.json`). The 4314 `tests/mutation_ledger` rows naming it keep `killed_by: tests/features.py`, so the killed set is unchanged mutant by mutant and nothing is re-driven.

**Freeze manifest.** A new tracked file, `tests/features_frozen.json`, records `{"spans": [the span ids case_select.split yields, in order], "lines": the file's line count}` at the fixer's merge base. It is written once by the freeze instrument's `--record` and read by the check. It is a measured input of tests/entities.py, so it goes in that closure, never on INERT. The check refuses at any tree where tests/features.py:
1. has a span id absent from the manifest: a new section was added, whether appended or inserted;
2. has more lines than the manifest records, so no growth by edit.

Edits inside a span that keep or lower the line count pass. A deleted span passes: removal is a move down. It still needs its own PR's mutation pins re-measured, as today.

The manifest's `lines` value lowers only through `--record` at a smaller count, never by hand. A raise goes through `budget-raise-gate` like any budget (CLAUDE.md rule 2).

**Where the check runs.** In tests/entities.py. Its measured closure in tests/closures.json already holds tests/features.py, so `GATE_SCOPE=auto` selects it on any diff touching that file or the manifest. Linux re-records the closure for the manifest read (gate-scoping.md).

## 2. Where new tests go: seam scripts

A new section goes in `tests/features_<seam>.py`. The seam is one of inputs, model, plan, dhw, actuation, surface or cycle, chosen by revision 1's step-A rule:
- take the distinct production modules the span names;
- the seam with the most modules wins; a tie goes to the first of inputs, model, plan, dhw, actuation, surface;
- a span naming none goes to cycle.

The rule is deterministic, so a new test has exactly one home. The instrument (`--seam <file>`) prints it, and the check refuses a span whose step-A seam differs from its script's.

The rule's code is the spike's `rev3/swap_run.py` `partition`. In the tree it becomes the freeze instrument under `dev/audit/harnesses/`, with its module table in that file.

**A seam script is created by the first PR that needs it**, never empty in advance. That PR:
- adds the script with the shared header its spans need (imports, fixtures from `tests/harness.py`);
- adds `run "$PYTHON" tests/features_<seam>.py` to the lane `tests/run.sh` runs features.py in, which `tools/coverage/coverage_tree.sh`'s `DERIVED` line then picks up;
- gets its closure recorded by `tests/derive_closures.sh` on Linux;
- adds it to `case_select.SCRIPTS` with its spans recorded by `--cases`;
- carries its own `tests/ci_budgets.json` raise.

## 3. Open branches at the freeze

Spans that open branches append to tests/features.py are refused once the freeze merges. Each branch moves its new spans, unchanged, to the seam script the instrument names. The mutation rows the branch pins for its new code are re-pinned against that script by its own `mutation_table.py --pin-killed` run: the normal per-PR cost, bounded by that branch's new rows. Rows already on main are untouched.

## 4. Budgets

- `tests/structure_budgets.json` and `tests/mutation_budgets.json`: unchanged.
- `tests/ci_budgets.json`: this group adds no script. Each seam script adds 2 to `script_runs_per_push` and 2 to `script_runs_full_case_pr`, once in the `closures` lane and once in the `coverage` lane (base: 56 and 68). That raise is asked by the PR that creates the script, and all seven reach 70 and 82.
- Payment tried: tests in an existing script instead of a seam script. Refused: it moves the append conflict to that script.

## 5. Null controls (the fixer's failing test first)

In tests/entities.py, each against a scratch copy of tests/features.py read by the same function the live check calls:
- the base tree passes, and the manifest's spans equal `case_select.split`'s, 252, derived and never carried;
- one planted `R.section` plus one `R.check` appended is refused, naming the new span id;
- the same block inserted mid-file is refused;
- one line added inside an existing span is refused on `lines`;
- one line removed passes, so the check does not refuse a move down;
- a span placed in the wrong seam script is refused, naming the instrument's home for it.

Each control is mutation-proven on the check's two conditions (`fixer.md`).

## 6. What this leaves undone against the ask

The owner's brief asked to split tests/features.py by feature seam into several scripts and re-key its mutation kills. This shape does not:
- tests/features.py stays one 104130-line, 252-span script, one CI unit, `wc -l` at the base;
- aim (1), append conflicts, is met for new tests only: conflicts move to seven seam tails, and the existing body is never split;
- aim (2), D5 units, is met by the freeze: s7 holds 4304 units against the 4500 cap at the base and can no longer grow;
- aims (3)-(5) hold trivially: no kill moves, no new closure class for the frozen file, no structure budget moves.

**Cost to reverse:** authorise the fork-drive re-key at its measured lower bound, at least 372156 CPU-s, the upper bound not driven. The spike's `forkdrive.py`/`moddrive.py` method then applies to the frozen file as revision 4 describes. A later split pays it once, whether or not new tests have meanwhile gone to seam scripts.

## Notes for the fixer

- The manifest is recorded at the fixer's merge base, never at e84856520d: late-round merges may still add spans before the freeze lands. Carry: R11-OWNER-FEATURES-SPLIT (item manifest-base)
- Late-round groups whose briefs say they append to tests/features.py receive this note's section 3 in their own brief at this group's merge (finding-propagation.md). Carry: R11-OWNER-FEATURES-SPLIT (item open-branch-port)
- A seam script's header must not import tests/features.py, or the two share a process and a kill path. Carry: R11-OWNER-FEATURES-SPLIT (item seam-header)

## Figures

From the repository root at the base:
- lines: `wc -l tests/features.py`
- spans: `PYTHONPATH=tests python3 -c "import ast,case_select as cs; s=open('tests/features.py').read(); print(len(cs.split(s, ast.parse(s))[2]))"`
- D5 s7 units: `python3 tools/audit/check_scopes.py --repo . --ref HEAD | grep '^ok D5'`
- entities.py's closure holds features.py: `python3 -c "import json; print('tests/features.py' in json.load(open('tests/closures.json'))['closures']['tests/entities.py'])"`
- ci counts: `tests/entities.py`'s every-script-once check (35 + 21 at the base), `tests/ci_budgets.json` for 56 and 68
- re-key lower bound, from the spike ref with `S=spike-r11-owner-features-split`: `python3 $S/stratlb.py $S/evidence/strata.json $S/evidence/strat_fork.jsonl $S/evidence/strat_mod.jsonl $S/evidence/strat_inflight_at_stop.txt E=80551,83654,26053 MOD=43546`
