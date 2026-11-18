# Proposal triage, session s14, batch 185 (P607)

The bar and the denominators are batch 141's. This proposal is a root-cause countermeasure, so
`proposal-triage.md` judges it on whether benefit clearly outweighs cost, not on the 10%/20%
machinery thresholds. The 20% bar is still reported, because the proposal asks.

Sources:
- origin/main `cbd23f1c8b`. Every line number below is at that commit.
- The roster at `origin/handoff/audit-r10-roster` `9c8603012a`, read at 10:56Z.
- The mutation-vacuous investigation's evidence directory (`rca-mutvac`, out of tree): `verdicts.tsv`,
  `heads.tsv`, `sites.tsv`, `verdicts/`, `batch*.log`.

## P607: MUTVAC-REVERT-ARM

Verdict: ACCEPT, narrowed. The narrowed part is a statement-deletion operator, `STMT_DEL`, in the
existing driver's diff mode (`tools/audit/seat/mutant_run.py --diff`), report-only. It goes as a
carry on R10-MUTANT-RUN-FORKCAP, which is not-started, has no dispatch ref, and owns the same file.

REJECTED:
- a separate revert arm, or a second tool. Its copy-tree, process-group kill and fork cap would be
  a second copy of the driver's. The out-of-tree prototype that did this without a group kill is
  the P604 incident.
- running the reviewer's existing diff arm unchanged as the fixer's pre-handoff step, as the only
  countermeasure. It reaches 7 of 23 reviewer sites (see below).

ROUTED TO THE ORCHESTRATOR (policy, owner-class): the `fixer.md` step 2 change that would make a
pre-handoff run mandatory. Triage's data for that ruling is under "Bar".

Source: queue line 285, 2026-11-11T10:49:37Z, orchestrator s14, from the Fable mutation-vacuous
investigation.

Instances:
- **Window figures, recomputed.** Command: first row per PR in `verdicts.tsv` from
  2026-11-04T10:49Z, then count verdict `merge` and a mutation-class cause.
  - Result: 207 first verdicts, 85 first-pass (0.411), 29 mutation-class.
  - The investigation reports 208, 85 and 31. The two differ only on the window edge.
  - If the claim were false, the first-pass rate would differ by more than a point, or the
    mutation class would be under 10.
- **How the reviewer found each site.** Command: tally the `found` column of `sites.tsv`.
  - Result: 43 blocked rows, 113 sites.
  - 89 sites came from hand mutants, 14 from CI's mutation lane, 2 from `mutant_run.py`, and 8
    from other routes.
  - The body's own mutants reproduce as killed on 33 of 43 rows (`K`).
  - Kinds: 98 sites are Python (`prod` 21, `tpy` 69, `tests` 8). The rest are sh 15, js 3 and
    yml 3.
  - Pattern tags: L 22, W 14, A 14, F 2, CI 1.
- **Reach of the existing diff arm on the sites reviewers named.**
  - Command: `s14-15/cover.py`. For every `*.py:N` that a blocked verdict names, it checks
    whether the line is added in `base...head` (`heads.tsv` columns 3 and 4). It then checks
    whether `mutant_run.mutate_line` (`:245-271`) yields an operator for that line.
  - Result: 23 distinct resolvable sites over 14 blocked heads. 16 sites are added lines and 7
    are not; the reviewer mutated an unchanged caller or context line.
  - Of the 16 added sites, the 5 existing operators reach **7 of 23** (30%): GUARD_OFF 5,
    RETURN_DEL 1, CALL_DEL 1. 9 added sites have no operator, because they are assignments,
    expression statements and continuation lines.
  - If the claim "the reviewer's own diff arm is enough" were true, this would read about 20 of
    23.
- **Reach of statement deletion.**
  - Command: `s14-15/lr.py`. It replaces each added site's line with `pass` at its indent and
    compiles the file at the blocked head.
  - Result: 7 of the 9 operator-less sites compile, or would compile once a deleted
    continuation statement is taken whole (5 of these compile as a single line; the
    continuation ones are `coordinator.py:6032`, `orchestrator_tick.py:758` and
    `survivor_list.py:77`).
  - The union with the existing operators reaches about **14 to 16 of 23** (61-70%). The
    prototype's revert unit reached 13 of 23.
  - The 7 sites on lines that are not added stay out of reach of any diff-scoped arm.
- **The prototype's claim was spot-checked on #3425.** `batch*.log`, `orchestrator_tick.py`:
  SURVIVED=2 at the blocked head (r1), and the named site is killed at the merged head
  (SURVIVED=1, a different unit).

Cost:
- **The change.** It is one operator in one file, `mutant_run.py`, of about 30-50 lines with its
  self-test arm. There is no new file, CI check, hot file or dependency.
- **Budgets.** `mutant_run.py` is not in `tests/structure_budgets.json`.
- **Runtime.** The investigation measured 2-136 s per file where the self-test is under 16 s.
  The operator adds at most one mutant per added simple statement.
- **The limit.** Serial runs are infeasible for `cloud_relay.sh`, `bus.sh`, `prepr.sh` and
  `roster_edit.py`. That is why this card rides on FORKCAP's process cap and keeps
  `--max-mutants` and `--report-only`.

Binding:
- **Bar.** The class ceiling is +19% to +36% relative to first-pass. The revert unit's estimate is
  0.409 to about 0.436 (+6.7%, range +3% to +17%). Scaled to 14-16 of 23 sites, it is about
  +7% to +9%. That is **below the 20% bar** for a permanent mandatory step.
- **What carries the ACCEPT.** The narrowed part is a root-cause countermeasure with a small,
  one-file, opt-in cost.
  - Reviewers already drive `mutant_run.py --diff`, and `survivor_list.py` reads its
    `SURVIVED` lines (#3262: four blocks in one class). So the operator first replaces hand
    mutants on the W and L patterns, at no standing cost.
  - At 207 first verdicts a week, +7% means about 6 first-pass merges, so about 6 fewer
    repair-and-re-review rounds a week. The cost is CPU seconds on an opt-in run.
- **Why the mandatory step is not ruled here.** It is policy, and its own gain (under 20%) is
  unproven.
  - Triage's recommendation is to DEFER it until this operator lands. Then re-run the card's
    acceptance harness and the next 10 mutation-vacuous blocks against STMT_DEL output.
  - If the operator's survivors cover 12 or more of the reviewer-named sites in those 10 blocks,
    a mandatory report-only run in step 2 is the stronger form, for files whose self-test is
    under 16 s.

### Card (carry on R10-MUTANT-RUN-FORKCAP)

**`tools/audit/seat/mutant_run.py` `mutate_line` / `diff_mutants` (`:245-297`), and the operator
list in the module docstring (`:25-45`).**

- **The operator.** Add `STMT_DEL`, from the `ast` of the file at the diff's head end. For each
  simple statement whose line span intersects the added lines:
  - Replace the whole span with `pass` at the statement's indent. Skip compound headers
    (`if`/`for`/`while`/`with`/`try`/`def`/`class`, which `GUARD_OFF` already covers), docstrings,
    `import`s, `print` and `_LOGGER` calls.
  - Keep the existing compile check and dedupe: a statement that `CALL_DEL` or `RETURN_DEL`
    already turns into `pass` is not a second mutant.
- **Output.** `SURVIVED <file>:<first line> STMT_DEL  pass`, which `survivor_list.py` already
  keys on `file:line`.
- **Acceptance (the finder's harness).** These 23 sites (block, head, base, site) are re-run with
  `--list`.
  - **What must pass.** The listed mutants must reach 14 or more (today 7). The five sites below
    marked + must each gain a STMT_DEL mutant.
  - **Null control.** A diff that adds only a comment or a docstring lists zero STMT_DEL mutants.
  - **Mutation proof.** Removing the operator's dispatch line drops the count back to 7.
- **Self-test.**
  - A fixture adds a bare assignment that no check reads: it is reported as SURVIVED STMT_DEL.
  - The same assignment pinned by the check is reported as KILLED.
  - A three-line continuation statement yields exactly one mutant.

Sites (head..base short ids from `heads.tsv`; `+` = needs STMT_DEL, `=` = already reached):
- 3184-r1 `freq_control.py:228` =; 3193-r1 `coordinator.py:2235` =, `:6032` + (continuation)
- 3231-r1 `inputs.py:467` +, `inputs.py:478` =, `config_flow.py:1667` (list element; a deletion,
  not `pass`)
- 3232-r3 `coordinator.py:1957` +; 3241-r1 `orchestrator_tick.py:758` (continuation)
- 3260-r1 `carry_audit.py:927` =, `:929` +, `:956` =; 3264-r1 `replan.py:2041`
- 3297-r1 `coordinator.py:4575` +, `:5400` =; 3341-r1 `survivor_list.py:77` (continuation)
- 3425-r1 `orchestrator_tick.py:1220` =
- Not-added (out of reach, listed so the count is honest): 3184 `tests/features.py:24969`,
  3193 `coordinator.py:11057`, 3231 `config_flow.py:1590`, 3262-r6 `beat_jobs.py:392`,
  3405 `config_flow.py:1562`, 3428-r3 `plan_page.py:212`, `replan.py:3290`.

**Size.** FORKCAP was S. With this carry it is an S/M edge in one file; the fixer stays sonnet. It
runs after the fork cap inside the same PR, because a statement deletion that removes a re-entry
guard is exactly the P604 shape.

### Owner-class answer (recorded after the ruling)

The orchestrator ruled on the routed `fixer.md` step 2 arm under mandate 6715477401 (scope `all`),
2026-11-11. This is not tvofi in person.

- **DEFERRED, as triage recommended.** There is no policy pull request now.
- **Re-open trigger.** It returns as a triage-queue line once two things hold:
  - STMT_DEL has merged;
  - 10 further `mutation-vacuous` blocks exist after that merge to measure against.
- **Threshold.** STMT_DEL survivors must cover 12 or more reviewer-named sites in those 10
  blocks. If they do, the stronger form is a mandatory report-only run in step 2, for files whose
  self-test is under 16 s.
