## Root cause — r10-rca-raise-gate-grammar (budget-raise-gate refused #2633 once and #2647 twice)

Root-cause seat (`root-cause.md`, `defect-root-cause.md`), beside R10-POLICY-LINT-FAMILY (carry "Triage P-F, recurrence 2") and not inside it. Measured at origin/main `a6620c30adcdf0d9529ee66977694bfa2a06d5c3`, 2026-10-23T11:06Z (`date -u`). No code is pushed: the countermeasure is a check, and that check is the fix seat's to build (below).

**Result: state (c). Cost test: build, decisively. Countermeasure: the P-F shared check that R10-POLICY-LINT-FAMILY owns, with four requirements this RCA adds (C1-C4). The barrier question goes to the owner, because the rule does not say what counts as one instance.**

### 1. Cause, reproduced

**Which side moved.** The gate did not move. `git log -G'IMPROVES|Payments tried' -- tools/policy/budget_raise_gate.py` returns only `31db3dc60` (2026-10-14T20:32Z). That commit landed `JUSTIFICATION_PAID` / `JUSTIFICATION_SCORE` (lines 137-139) together with the self-tests that pin the exact shapes the bodies later used: `"Payments tried:\nmoved"` is refused (line 1107), and a score line with no `dS <n> <verdict>` figure is refused (line 1105, `Architecture score: worse`). What moved was the bodies. #2647's own earlier body `8f564875d` (00:14Z) passes. Its round-2 rewrite `84e2aaf66` changed `dS +0.0023 IMPROVES` to `dS +0.0105` and dropped the verdict word.

Each refusal was reproduced by calling the gate's own function on each body version on the orphan handoff-body refs. The script `just.py` (sha1 `9daf5eb3`) is `import budget_raise_gate as g; ok, why = g.justification(open(argv[1]).read())`, and it exits 1 on a refusal:

| PR | body commit (`handoff-body/…`) | `justification()` | shape |
|---|---|---|---|
| #2633 | `c6c8fee16` (10-22 23:12Z), `9b5742049` (10-23 01:51Z) | REFUSED: lacks a `Payments tried:` line | `- Payments tried:` written as a bare label, with the payments on sub-bullets; `JUSTIFICATION_PAID` needs `\S` on the same line |
| #2647 | `8f564875d` (00:14Z) | PASS | `Architecture score: dS +0.0023 IMPROVES` |
| #2647 | `84e2aaf66` (04:10Z) | REFUSED: lacks an `Architecture score: dS` line | the score line is `Architecture score: dS +0.0105`, with no verdict word; `IMPROVES` is in the section only in prose (payment (4)) |
| #2647 | `f2b98c1df` (06:32Z) | REFUSED: same | a "Round 3" paragraph adds a second prose `IMPROVES` inside the section, and the score line is still bare. The only complete score line in the body is line 272, under `## Figures` (outside the section) |
| #2647 | merged body (API read) | passes | `Architecture score: dS +0.0105 IMPROVES` |

Passing once fixed (the null control for the reproduction):
- `9b5742049` with only `- Payments tried:` changed to `- Payments tried: each below, …` gives PASS.
- `f2b98c1df` with only its score line given `IMPROVES` gives PASS.

**The named cause.** The grammar has exactly one executable reader, `budget_raise_gate.justification()`. That reader is only reached from inside `approval()`, at line 483, after a mandated approval has been found on the head. Every earlier run returns at line 467 with `no decisive review by tvofi`. The mandated approval is posted by the merge train's approve step, so the grammar is first evaluated at train time, and not one moment before.

The CI gate ran on every push of both PRs and never executed the arm:
- #2647's round-3 review: "The only red is `budget-raise-gate` (two runs): … `REFUSED: no decisive review by tvofi`".
- The expected red hides the second reason. #2647's body answered it: "It is the gate working as designed, not a defect … No cheaper detector applies."
- No pre-train path reads the grammar. A `grep -c` for `Raise justification|Payments tried|justification(` returns 0 in each of `tools/policy/policy_lint.mjs`, `tools/pr/prepr.sh`, `tools/pr/ci_predict.py`, `tools/audit/seat/body_patch.sh`, `tools/audit/seat/body_push.sh` and `.github/workflows/governance.yml`.

The reported cause is right but narrower than this. The brief said "pr-contract, body_patch and the reviewer passed the body". The wider cause is that the one check that *does* carry the grammar is ordered behind the approval.

### 2. Process state: (c)

**The process: a CI check carrying the grammar on every push.** It existed (`budget-raise-gate.yml`, since 31db3dc60), it ran, and it was followed. It could not produce the intended result, because its unit, the justification arm, is reachable only after the train's approval. This is the same shape as `root-cause.md`'s "existed in CI but in no local path", and one step worse: the arm is in no path at all before the train.

**The review process was obeyed, and it is not meant to catch this.** Decision 0013: "It checks the shape; the fix review judges whether the payments were real." #2647's round-3 reviewer quoted the bare line ("lists each payment with the `Architecture score: dS +0.0105` line") and judged the substance, as instructed.

**Not (a):** a check for the grammar existed. **Not (b):**
- The carry was accepted at 03:45Z and instance 2 was written at 04:10Z. A countermeasure 25 minutes old and not yet dispatched (`resume.stage: not-started` at roster `4b3ca5d6c`) is not a process that was disobeyed.
- The brief cites an interim hand rule ("run the section-scoped regex, require count 1"). I did not find it in the tree at `a6620c30a`, on the roster at `4b3ca5d6c`, or in #201's comments for 2026-10-22T09:28Z to 2026-10-23T09:29Z (page 50 at 40 per page). If it was given, it was in nothing the #2647 fixer seat reads, so (b) cannot be shown. A rule held only in an orchestrator's notes is the (c) shape again.

**What the state implies for the countermeasure:** move the existing reader in front of the approval. Do not write a firmer instruction.

### 3. Class search and cost test

**The class:** a predicate the merge train applies to pull-request text that no pre-train path applies.

**The rule that enumerates it:** every `gh pr view … --json body|title` read in `tools/audit/seat/merge_train.py` and `queue_pre_flight.py`, and the predicate applied to each. For each predicate, I grepped the pre-train paths (prepr.sh, policy_lint.mjs, body_patch.sh, body_push.sh, governance.yml pr-contract). The seams it returns:

| train read | predicate | earlier reader | disposition |
|---|---|---|---|
| body, `_body` (merge_train.py:1012) | `justification()` | none | **this defect**: closed by the countermeasure below |
| body, recarry `rb<pr>.md` (merge_train.py:1239) | prepr through `remerge_main` | prepr step 7 at open and at body_push | already guarded (same function) |
| queue_pre_flight `findings` | `carry_audit.py check --body` | body_patch.sh:98, pr-contract | already guarded |
| reviews, `MANDATE_CITE` (merge_train.py:968) | citation grammar | n/a | the train writes this text itself; no author can mis-shape it |
| **title** (merge_train.py:1382, merge_pr.sh:252) | `preflight.sh` on the title | none: prepr.sh:3132 runs preflight.sh on the **body** only | **a second member**, with no known instance. Carried below as a note and not built; the cost test has nothing to multiply |

**Cost test**, in wall-clock minutes:
- **Cost per refusal:** at least one CI cycle before the train can re-admit the car. Measured on #2647's merged head `64b3cb5`, from the check-runs read: the first job started at 09:24:08Z and the last required job (`mutation`) finished at 10:20:14Z, which is 56.1 min (`fast (3.14)` alone took 54.3 min). The brief's "about 50 min per parked run" is the same order. I did not measure the parked runs run40 and run41 themselves, or the orchestrator's time.
- **Raise PRs, measured:** 7 PR merges raised a budget. The census ran `raises_between(merge-base(m^1, m^2), m^2)`, the gate's own reader, over every first-parent PR merge in `31db3dc60..origin/main`, 341 merges in all. The script is `raise_census.py`, sha1 `a63ed04b`. The 7 are #2209, #2311, #2368, #2585, #2586, #2633 and #2647, over 8.58 days, which is 0.82 per day.
  - Agreement control: the census's #2647 leaf `seam_cut_total: 708 -> 714` matches the CI gate's own `RAISE` line, as the review quoted it.
  - Null control: the other 334 merges read no raise, e.g. #2648, a delivery-row-only PR.
- **Refusal rate:** 2 of the 7 raise PRs had a body refused, with 3 refusals in all. That is a lower bound: I did not read the bodies of the other 5.
- **Exposure ahead:** mandate 6175172275 runs until 2026-10-28T18:14Z, 5.30 days after this measurement, so about 4.3 raise PRs at the measured rate. Separately, 4 not-started roster groups name a raise justification in their brief or carry (rule: regex `Raise justification|budget-raise gate|budget_raise_gate|a raise only|Payments tried` over brief and carry): R10-POLICY-LINT-FAMILY, R10-ROUND-PLAYBOOK, R10-FLY-MANDATE-REVOKE-GUARD and R10-ORCH-ROSTER-SCHEMA.
- **Expected cost without the countermeasure:** 4.3 × (2/7 to 3/7) × 56.1 min, about 69 to 103 CI-minutes over the mandate window.
- **Standing cost of the countermeasure:** `justification()` on a real body takes 49, 52 and 59 ms per process (3 runs on `f2b98c1df`, including interpreter start). It is paid only on bodies that carry the heading or a raise: 7 of 341 merges in the window.

**Verdict:** about 0.06 s per raise body, against 69 to 103 min expected. Build it.

### 4. Countermeasure

**M1, the P-F design that R10-POLICY-LINT-FAMILY builds:** `budget_raise_gate.py --check-body <file>`, called from `policy_lint.mjs --pr-body`. It addresses state (c) by putting the existing reader in front of the approval, in every path that writes a body the train reads: open_pr/prepr step 7, body_push, body_patch and pr-contract. It calls the gate's function rather than a mirror, so a clause the gate gains later is covered without anyone having seen it fail.

This seat builds nothing in parallel, because a second copy would be the parallel mechanism `fixer.md` step 17 forbids. Four requirements follow from the cause, and each goes to the fix's brief:

- **C1. Demonstrate on the recorded bodies, not only on synthetic rows.**
  - Failing: the `## Raise justification` sections of `c6c8fee16`, `84e2aaf66` and `f2b98c1df` (on `handoff-body/r10-flow-arch-planner` and `handoff-body/r10-scores`).
  - Passing: `8f564875d`, and the two one-line repairs in section 1.
  - `f2b98c1df` is the case a mirrored "verdict word in the section" regex passes: `IMPROVES` appears twice inside the section in prose.
  - Carry: R10-POLICY-LINT-FAMILY
- **C2. Trigger on the diff, not only on the heading.**
  - A raise (`raises_between`) whose body has no section is refused by the train under any mandate, identically. A trigger keyed only on "the body has the heading" misses that case.
  - The owner's own review owes no section. So this case is the fixer's to design: refuse, or print a named warning that pr-contract surfaces, but never skip it in silence. The design review judges the choice.
  - Carry: R10-POLICY-LINT-FAMILY
- **C3. Run on the text the train reads.**
  - `body_patch.sh` rewrites the GitHub body after the handoff, and #2633 merged under the mandate train, while both of its handoff-body versions still refuse. So the body the train passed was a patched one that no ref holds (an inference: I did not read #2633's final body).
  - So the check belongs on the patch path and on pr-contract's run on body edits, not only at body_push.
  - Carry: R10-POLICY-LINT-FAMILY
- **C4. Register the class.**
  - An entry in `bugclasses.json` citing `dev/audit/rca/R10-RCA-RAISE-GATE-GRAMMAR.md`, so `fold_ledger.py check` sees a barrier once one is required.
  - This section is that document's text. It is a development-record file, which this seat's return instructions do not let it push, so it lands with the fix PR or the orchestrator's record beat.
  - Carry: R10-POLICY-LINT-FAMILY

**The title seam (preflight.sh at merge time only)** goes to the same family as a note, not a requirement:
- `prepr.sh`'s `body_check` already passes `--title` to policy_lint, so the change is small if an instance ever appears.
- There are zero known instances today, so nothing is built.
- Carry: R10-POLICY-LINT-FAMILY

**Refused: M2,** printing the justification verdict on every pre-approval run of the CI gate. The check is red by design at that point and seats read it as expected, so a new log line under that red changes nothing anyone keys on. M1 makes pr-contract red, which seats do read.

**No policy change is proposed.** 0013's prose ("a `Payments tried:` line naming each payment") admits the #2633 shape. But once M1 lands, the gate's own `why` is printed at writing time, which makes the grammar self-describing. Tightening the prose would be a firmer instruction for a state-(c) failure.

### The audit-class barrier

`defect-root-cause.md`: "three or more instances in one round … owes a class-eliminating barrier". The rule does not say what one instance is:
- **Counted per PR** (the triage's reading), round 10 has 2, and the next refusal is the third.
- **Counted per refusal**, it has 3 already, and the barrier is owed now.

That reading is the owner's to settle, and it is surfaced here rather than filed. Whichever count applies, M1 is class-eliminating for the enumerated class only if all four hold:
- it is the gate's function, not a mirror (C1);
- it runs on every path that writes the text the train reads (C3);
- nothing it depends on is supplied later by the train, such as the approval or the mandate (C2);
- it is registered in `bugclasses.json` (C4).

The title seam is the class's other member. A barrier that claims the whole class must disposition it: closed in the same PR, or recorded with its zero instances.

## Figures

All taken at `a6620c30a` unless the row names another commit. Body files come from `git show <commit>:BODY.md` after `git fetch origin handoff-body/r10-scores handoff-body/r10-flow-arch-planner`.

- **Refusals:** `python3 just.py <body>` for each row of the table in section 1.
- **Gate history:**
  - `git log -G'IMPROVES\|Payments tried' -- tools/policy/budget_raise_gate.py` returns `31db3dc60` alone.
  - The arm's position: `approval()` line 483 against the line 467 early return.
- **Pre-train readers:** `grep -c "Raise justification\|Payments tried\|justification("` returns 0 on each of the six files in section 1.
- **Raise census:** `python3 raise_census.py 31db3dc60` prints `RESULT pr_merges=341` and 7 `RAISE` rows. Per merge it reads `git log --first-parent --merges 31db3dc60..origin/main`, then `raises_between(merge-base(m^1,m^2), m^2, ls-tree, show)`.
- **CI cycle:** check runs on `64b3cb5` (43 runs): earliest `started_at` 09:24:08Z, `mutation` `completed_at` 10:20:14Z.
- **Detector cost:** wall clock from `date +%s%N` around `python3 just.py f2b98c1df.md`, 3 runs: 52, 49 and 59 ms.

## Friction

- `body_push.sh` refuses a result body from a checkout that has no `tools/pr/ci_predict.py`, so a root-cause seat must run it from a full worktree even when it pushes no code. That is not a defect, and this seat ran from an origin/main worktree.
