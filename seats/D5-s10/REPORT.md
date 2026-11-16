# D5-s10 — round 11, baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (box B12)

Cells: `.claude/hooks/*.sh`, `.claude/workflows/*.js`, `dev/audit/harnesses/**`; steps D5.M1-M4.
`check_scopes.py --seat D5-s10` prints 329 files (267 .py, 37 .sh, 16 .mjs, 9 .js), all M1+M2+M3+M4.
The export has no `.git`, so every instrument ran with `--repo /home/user/heatpump_optimizer --ref <baseline>`
(the units are read from the export root).

## Method and denominators

| step | enumerator | universe | examined |
|---|---|---|---|
| D5.M1 | `bash dev/audit/rounds/round11/D5/s10/enumerate.sh M1` | 0 | 0 |
| D5.M2 | `... enumerate.sh M2` | 0 | 0 |
| D5.M3 | `... enumerate.sh M3` | 0 | 0 |
| D5.M4 | `... enumerate.sh M4` | 1794 | 1794 |

M1-M3 take their universe from `text_ledger.py outline`, which prints rows only for Markdown and HTML.
None of these cells is a document, so the outline prints 0 rows. As a null control, the same outline
over D5-s2 prints 9 documents, 207 headings and 175 links.

M4: `m4_ledger.py` rows every D5 unit (1137 comments, 657 docstrings). Each row carries an executed check:
- every repository path and `file:symbol` the unit names, resolved with `git ls-tree` / `git show` at the baseline;
- C5 sentence length within prose paragraphs;
- the number the comment cites against the numeric constant directly below it.

The 24 units whose paths did not resolve, plus 5 hook units whose C1 truth a harness tested, are ruled in
`m4_adjudicate.tsv`, each ruling by a command the harness runs. The command for `text_ledger.py check` is:
`check --dim D5 --seat D5-s10 --plant m4_ledger.tsv`. It reports rows=1794, true=1781, false=8,
unverifiable=5, unrowed=0, orphan=0, malformed=0 and plant_refused=1.

Redispatched: C1, C4, C5, C6 and C7 examined; C2 and C3 not reached. C2 and C3 cover docs/ paths in
D5-s1's and D5-s2's cells, so they went to the leads.

## Findings

| id | sev | file | number (perturbed) |
|---|---|---|---|
| D5-s10-01 | medium | .claude/hooks/pre-edit.sh | The source the refusal names loses the edit on regeneration: edit_reaches_cursor=0 (perturbed: 1). The hook lets the generated `.claude/rules/` through: unguarded_generated=1. |
| D5-s10-02 | medium | .claude/hooks/stop-selfcheck.sh | escaped=2 (AGENTS.md, dev/audit/README.md) of 65 policy_lint files; e2e rc 0 vs 2 for CLAUDE.md (perturbed: 0). The header's three-dot claim is false (threedot_only=0). |
| D5-s10-03 | low | .claude/hooks/session-start.sh | mismatches=3: the header says lines 5/6, the hook prints them on lines 4/5; it says three other items, the list has four (perturbed: 1). handover_trap_11_found=0. |
| D5-s10-04 | low | dev/audit/harnesses/k1725_blas_kernel_gap.py | cites tools/audit/README.md, absent: unresolved_paths=1 (perturbed: 0) |
| D5-s10-05 | low | dev/audit/harnesses/thermal_parity.py | same, unresolved_paths=1 (perturbed: 0) |
| D5-s10-06 | low | dev/audit/harnesses/cop_duty_floor.py | cites the discharged carry-2065.json: unresolved_paths=2 (perturbed: 1) |
| D5-s10-07 | low | 193 of 329 files | 339 sentences longer than 40 words, criterion C5 (perturbed: 275) |

Full blocks are in `findings/*.json` and `REPORT.json`.

## Non-findings (each with its command in REPORT.json)

- pre-bash.sh: all 21 header examples behave as stated (`pre_bash_claims.sh`: mismatches=0).
- The workflow comments hold (`workflow_claims.py`: 6 claims, mismatches=0):
  - the audit-fix and audit-wave prompts are byte-identical mirrors;
  - the batches are three, SHARD_SIZE is 15, and there is one verifier;
  - there is no sibling import;
  - the fragments are in sync.
- always-fails.sh: its self-test fails (rc 2). It is not wired in settings.json, and its fixture exists.
- The 4 cited-number-vs-constant candidates all hold (for example 0.4 x 4.19 = 1.676 ~ 1.68 kW/K).
- unresolved_symbols=0.
- 16 of the 24 unresolved-path units hold (placeholders, a hypothetical file, an external package, evidence at
  an archived ref), plus one record harness and one external path. 5 stay unverifiable: they cite seat-local
  evidence that is not present at its archived ref.

## Harnesses

`enumerate.sh`, `m4_ledger.py` (+ `m4_adjudicate.tsv`, `m4_ledger.tsv`, `m4_ledger.out`), `pre_edit_source.py`,
`stop_prefixes.py`, `session_start_lines.py`, `pre_bash_claims.sh`, `workflow_claims.py`. Each header carries:
- the metric;
- the command;
- the expected value;
- the perturbation.

All numbers are counts, so they are not provisional.

## Unfinished

D5.M4: C1 semantic truth was executed for the hooks, the workflows and the 29 adjudicated units. Three
things are not done:
- For the other harness docstrings, C1 is checked only for resolution and numeric constants.
- C3 and C4 are not judged for any unit.
- The C5 sentences are counted, not each re-read.

## Leads

- D11-s1: `tools/audit/seat/moved_paths.py` sees an empty tracked set with no `.git` and reports 557 false
  STALE? hits. The real count is 45.
- D5-s1: C2.
- D5-s2: C3 and C7 (README/docs).
- D5-s4: C7 (www/*.js).

## Exposure

See REPORT.json `exposure`. No docs/ file was read, and nothing on GitHub was read.
