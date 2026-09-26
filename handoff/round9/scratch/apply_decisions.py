"""Apply tvofi's 19:16Z card answers (TVOFI-ASKS DECISIONS) to fixplan/data.py. Every replacement must match exactly once."""
import sys
P = sys.argv[1]
s = open(P).read()

def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:120])
    s = s.replace(old, new)

TV = "tvofi 19:16Z, card "

# ---------------------------------------------------------------- D2: F6.1b merged back into F6.1
for k in ("P9-rca2", "P9-rca3", "P9-rca4"):
    rep(f'dict(id="{k}", cls="P9", pr="F6.1b"', f'dict(id="{k}", cls="P9", pr="F6.1"')
old_f61b_start = s.index(' dict(id="F6.1b"')
old_f61b_end = s.index(' dict(id="F6.2"')
s = s[:old_f61b_start] + s[old_f61b_end:]
rep('''          "P9-rca1 (the RCA's grid): the setup picker's armed clear button takes the fix D4-s1-01's confirm state takes; the RCA's fix emulation used a darker confirm fill. The grid's contrast rule is its failing test, run from the RCA prototype until F6.3 lands it."]),''',
    '''          "P9-rca1 (the RCA's grid): the setup picker's armed clear button takes the fix D4-s1-01's confirm state takes; the RCA's fix emulation used a darker confirm fill. The grid's contrast rule is its failing test, run from the RCA prototype until F6.3 lands it.",
          "Cap exception (''' + TV + '''D2, 'Enlarge F6.1'): F6.1b is merged back into this PR, so it carries four findings and four P9 instances, over fixer.md's five-item cap by tvofi's explicit choice. gen.py accepts it only through its recorded exception list. The 400-production-line bound still applies: if the eight items together pass it, stop and ask the orchestrator; do not trim a fix to fit.",
          "P9-rca2 and P9-rca3 share one label: the 'estimated prices' label fails contrast on the estimated band and prints over the now label. The RCA's fix emulation moved it two lines lower in the text token; measure both rules after whatever fix you choose.",
          "P9-rca4 is a candidate that needs a fix design: grow each slot target against its neighbours' grown targets, not their ink, or disposition it with the measurement. One attempt (half-gap growth) made 53 targets worse, so show the whole grid's target count at both ends.",
          "All four P9 instances take their failing test from the RCA prototype's grid, run at the merge base and the head; F6.3's zero-rule grid cannot go green until each is fixed or dispositioned here."]),''')
rep('''   notes=["The P9 class barrier (below), after F6.1 and F6.1b: the grid''', '''   notes=["The P9 class barrier (below), after F6.1 (which carries all four of the RCA's instances since tvofi's D2 answer): the grid''')
rep('''"F6.1": ("sonnet", ""), "F6.1b": ("sonnet", ""), "F6.2": ("sonnet", ""),''', '''"F6.1": ("sonnet", ""), "F6.2": ("sonnet", ""),''')

# ---------------------------------------------------------------- C15: F7.3 dropped, D8-s2-01 refused against A3(e)
a = s.index(' dict(id="F7.3"'); b = s.index(' # ---------------- F8 docs')
s = s[:a] + s[b:]
rep('''   after=["F10.3", "F1.11", "F7.3", "F11.3"],''', '''   after=["F10.3", "F1.11", "F11.3"],''')
rep(''' "F7.3": ("sonnet", "mechanical once tvofi rules on A3(e)"),\n''', '')
rep('''("F7.3", "P6", "The P6 solve-seed arm (F1.11) declares room, upper and lower under A3(e). Whichever way tvofi rules on D8-s2-01, update that declaration table in tests/entities.py in the same PR; the arm refuses a stale declaration."),''',
    '''("F1.11", "P6", "tvofi kept A3(e) (card C15): D8-s2-01 is refused and F7.3 is dropped, so the P6 solve-seed arm's declaration of room, upper and lower under A3(e) stands as written; cite the A3(e) pin in tests/entities.py beside it rather than re-deciding it."),''')

# ---------------------------------------------------------------- C16, C17: F11.2
rep('''   findings=[("D11-s1-01", None), ("D11-s1-04", None), ("D11-s1-03", None), ("D13-s1-03", None)],
   edit=[".github/workflows/tests.yml", ".github/workflows/pr-contract.yml", ".github/CODEOWNERS",
         ".claude/workflows/budget_raise_gate.py", "docs/decisions/0008-a-seat-identity-distinct-from-the-owner.md"],''',
    '''   findings=[("D11-s1-04", None), ("D11-s1-03", None), ("D13-s1-03", None)],
   edit=[".github/workflows/tests.yml", ".github/workflows/pr-contract.yml", ".github/CODEOWNERS",
         ".claude/workflows/budget_raise_gate.py"],''')
rep('''   tvofi="workflows, CODEOWNERS, budget_raise_gate.py and docs/decisions are code-owned; D11-s1-01 and D11-s1-04 are owner decisions",
   notes=["D11-s1-01: the remedy is a ruleset setting tvofi changes (dismiss stale reviews on push, or require last-push approval); the PR records it in decision 0008.",
          "D11-s1-04 (merged D11-s2-03): owner's decision between a distinct delegated identity and a refusal in budget_raise_gate.py.",''',
    '''   tvofi="workflows, CODEOWNERS and budget_raise_gate.py are code-owned",
   notes=["D11-s1-01 is not in this PR: tvofi left the ruleset setting unchanged (card C16, 'Leave'), so it closes as refused by tvofi. Nothing here edits a ruleset, a decision record or policy for it.",
          "D11-s1-04 (merged D11-s2-03): tvofi chose the refusal (card C17): budget_raise_gate.py refuses an approval by an agent-driven identity rather than a new delegated identity being created. Its failing test is the finder's reproduction of an agent approval satisfying the gate.",''')

# ---------------------------------------------------------------- C10, C16, C18: F11.3, and the new F11.6
rep('''   findings=[("D11-s2-01", None), ("D11-s2-04", None), ("D13-s1-02", None)],
   edit=[".claude/workflows/policy_lint.mjs", ".claude/workflows/policy_budgets.json", ".claude/rules/ratchet-budgets.md",
         ".cursor/rules/ratchet-budgets.mdc", "CLAUDE.md", "tools/audit/briefs/fix-review.md",
         ".claude/workflows/web-fix-wave.js", "tools/audit/app_approve.sh", ".claude/workflows/counts.mjs",''',
    '''   findings=[("D11-s2-01", None), ("D11-s2-04", None)],
   edit=[".claude/workflows/policy_lint.mjs", ".claude/workflows/policy_budgets.json", ".claude/rules/ratchet-budgets.md",
         ".cursor/rules/ratchet-budgets.mdc", "CLAUDE.md", ".claude/workflows/counts.mjs",''')
rep('''   tvofi="policy (CLAUDE.md, .claude/rules, tools/audit/briefs) and web-fix-wave.js are code-owned",
   notes=["D11-s2-04 is weakened: only claim (a) stands; quote the literal the select command prints.",
          "D13-s1-02 is weakened: a diff-equivalence carry saves a few rounds, not most; the owner decides whether to build it.",''',
    '''   tvofi="policy (CLAUDE.md, .claude/rules) and governance.yml are code-owned",
   notes=["D11-s2-04 is weakened: only claim (a) stands; quote the literal the select command prints.",
          "D13-s1-02 moved to F11.6 (tvofi's card C18, 'Build'): with the I3 barrier, the C10 derivation and the I5 quoted-line pass, this PR has no room under the 400-line bound for the verdict carry too.",
          "Registration set derived, not registered (tvofi's card C10, 'Derive'): the field-coverage program's set of governance checks is derived from policy_lint.mjs's CHECKS table, codeowners_gap.py's pinned surface and stamp.py's rule 4, and every entry of that derived set either registers its input or declares none; a check in the derived set with neither is refused. This closes the I3 RCA's residual (a new check covered only once registered). Demonstrate it: add a check to CHECKS with no registration and show the program refusing it, then register it and show it green.",
          "Ruleset (tvofi's card C16, 'Leave'): the ruleset setting is unchanged and D11-s1-01 is refused, so the ruleset fixture records the ruleset as it stands; the field-coverage ruleset arm still perturbs every leaf, including the stale-approval ones.",''')
rep('''          "The I3 barrier lands here, after F11.2, because its ruleset fixture records tvofi's D11-s1-01 decision, which F11.2 makes. Form''',
    '''          "The I3 barrier lands here, after F11.2 (lane order, and F11.2's workflow edits are fixtures the barrier reads). Form''')
rep('''          "D11-s2-01's fix is the per-file files_tokens cap in policy_budgets.json (a new cap at the measured value, not a raise); F11.3's own rule makes any budget change tvofi's before the push.",''',
    '''          "D11-s2-01's fix is the per-file files_tokens cap in policy_budgets.json, at the measured value: tvofi allowed the new cap (card B3). It still merges only on tvofi's approving review (budget-raise-gate).",''')
# F11.6, inserted after F11.3 and before F11.4 in the F11 lane (F11.4 already waits on the deeper F10.4)
rep(''' dict(id="F11.4", lane="F11",''',
    ''' dict(id="F11.6", lane="F11", title="Verdict carry across diff-equivalent moves from main (D13-s1-02)",
   findings=[("D13-s1-02", None)],
   edit=["tools/audit/briefs/fix-review.md", ".claude/workflows/web-fix-wave.js", "tools/audit/app_approve.sh",
         ".claude/workflows/policy_budgets.json"],
   borrows={}, after=["F11.3"],
   tvofi="tvofi chose to build it (card C18); fix-review.md is policy and web-fix-wave.js is code-owned",
   notes=["New at tvofi's answers (card C18, 'Build'; split from F11.3 for the 400-line bound). A review verdict carries across a head move only when the move is a merge from origin/main (or a ci: bot commit) and the branch's own diff against its merge base is byte-identical before and after the move; any other move, or any difference in that diff, keeps today's re-review.",
          "D13-s1-02 is weakened: the judge measured the saving at a few rounds, not most. Its failing test is the finder's yield harness (tools/audit/round9/D13/s1/yield_rounds.mjs at the evidence commit): count the rounds the carry would have skipped and, as the null control, show that a move that changes the branch's own diff by one byte is not carried.",
          "fix-review.md is policy: the carry rule's text is tvofi's to approve at merge. Pay for its prose inside the file's policy_budgets.json cap first; a raise is tvofi's, asked before the push (ratchet-budgets.md)."]),
 dict(id="F11.4", lane="F11",''')

# ---------------------------------------------------------------- A1-A9, B4: F11.5
rep('''   tvofi="policy: tools/audit/briefs, .claude/rules and tests/README.md are code-owned; each draft needs tvofi's approval before this merges",
   notes=["The RCA seats drafted policy changes and landed none (root-cause.md). This PR carries the drafts tvofi approves (TVOFI-ASKS, group a), each verbatim from its RCA write-up, each naming the process state it addresses; a draft tvofi declines is left out and recorded in the body. Last in the F11 lane, so nothing waits on it.",''',
    '''   tvofi="policy: tools/audit/briefs, .claude/rules and tests/README.md are code-owned; tvofi approved all nine drafts (cards A1-A9) and reviews the PR at its head before it merges",
   notes=["The RCA seats drafted policy changes and landed none (root-cause.md). tvofi approved all nine drafts (cards A1-A9, A9 included, over the recommendation to skip it; A2: A1 rides this PR, not F1.10). Each lands verbatim from its RCA write-up, one commit each, naming the process state it addresses. Last in the F11 lane, so nothing waits on it.",''')
rep('''(I3 RCA, optional).",''', '''(I3 RCA; approved by tvofi, card A9). With C10's derivation built in F11.3, the draft reads 'a governance check is in the derived set and registers its input or declares none'; take the wording from rca/i3 and adjust only that clause, and say so in the body.",''')
rep('''          "Regenerate .cursor/rules with rules_sync.mjs after editing a rule. Pay for added prose inside each file's policy_budgets.json cap first (ratchet-budgets.md); a raise is tvofi's, asked before the push, and TVOFI-ASKS lists it."]),''',
    '''          "Regenerate .cursor/rules with rules_sync.mjs after editing a rule. Pay for added prose inside each file's policy_budgets.json cap first (ratchet-budgets.md); tvofi allowed raising the caps of fixer.md, D1.md, root-cause.md and tests/README.md by exactly what each approved draft adds, if policy_lint says it must (card B4), to the measured value only."]),''')

# ---------------------------------------------------------------- C11, C14: F11.4
rep('''   carry=["RESUME owed work that shares audit-find.js (fold only if tvofi agrees): the driver-fix PR''',
    '''   carry=["RESUME owed work that shares audit-find.js, folded in by tvofi (card C14, 'Fold in'): the driver-fix PR''')
rep('''          "Register the pairs F10.4 and F11.1 record in their bodies:''',
    '''          "tvofi accepted the residual (card C11): a second reader with a different grammar for an unregistered concept stays undetected beyond the A7 and A8 policy text (F11.5). Record it in the body as accepted; build nothing for it.",
          "Register the pairs F10.4 and F11.1 record in their bodies:''')

# ---------------------------------------------------------------- C13: F1.9
rep('''          "FI-sw3 (`_detect_outage`): no bound fixes it; implement tvofi's decision (TVOFI-ASKS, group c): treat a stored last_tick ahead of now as an outage and open the staggered window, or accept one masked recovery per clock-corrected restart. Its failing test is the RCA's outage row.",''',
    '''          "FI-sw3 (`_detect_outage`): no bound fixes it, and tvofi decided (card C13, 'Outage'; #775's rule): a stored last_tick ahead of now is treated as an outage, so the staggered-recovery window opens. Its failing test is the RCA's outage row, red at the merge base and green at the head; the null control is a stored last_tick at or before now, whose outage verdict must not change.",''')
rep(''' "F1.9": ("sonnet", "regression tests for instances F3.1 closes plus one branch whose rule tvofi decides (FI-sw3); stop and ask if unruled"),''',
    ''' "F1.9": ("sonnet", "regression tests for instances F3.1 closes plus one branch whose rule tvofi has decided (FI-sw3, card C13: outage)"),''')

# ---------------------------------------------------------------- C1: declared-domain barrier F9.3 (P1)
rep('''("F1.6", "P1", "Cherry-pick 0ade2456 only (99118d35 is demo instance fixes). Before merging, re-derive tests/closures.json for tests/finite_boundary.py with derive_closures.sh --single on Linux. The arm's out-of-scope residue (out-of-domain but bounded values, and a loader that discards a whole valid grid for one bad cell) stays per-seam in its instance PRs, pinned by their probes, unless tvofi commissions a declared-domain barrier (TVOFI-ASKS).''',
    '''("F1.6", "P1", "Cherry-pick 0ade2456 only (99118d35 is demo instance fixes). Before merging, re-derive tests/closures.json for tests/finite_boundary.py with derive_closures.sh --single on Linux. The arm's out-of-scope residue (out-of-domain but bounded values, and a loader that discards a whole valid grid for one bad cell) is fixed per seam in its instance PRs, and tvofi commissioned a declared-domain barrier for it (card C1), which lands in F9.3 after this PR; keep Arm 4's oracle as prototyped and leave the domain table to F9.3.''')
rep('''("F3.3", "P1", "D1-s4-01's duty''', '''("F3.3", "P1", "tvofi commissioned a declared-domain barrier for this PR's residue (card C1; it lands in F9.3, after F1.6): fix each seam here as planned, and record in the body each stored field you bound and the domain its own update path enforces, which F9.3's table declares. D1-s4-01's duty''')
rep('''          "D12-s2-02's fix creates the P2 owner F1.11's registry names for entity writes: route the mode write by the target entity's own domain, as `_on_off_service` does."]),''',
    '''          "D12-s2-02's fix creates the P2 owner F1.11's registry names for entity writes: route the mode write by the target entity's own domain, as `_on_off_service` does.",
          "D1-s3-06 is one of the four findings the declared-domain barrier (F9.3, tvofi's card C1) covers: fix the seam here, and record in the body the decile and ratio domains `FrequencyMap`'s own update path enforces, which F9.3's table declares."]),''')
rep(''' dict(id="F9.2", lane="F9",''', ''' dict(id="F9.2", lane="F9",''')  # anchor check
rep('''   notes=["D7-s3-51: `_async_check_a4` must not return inside finally."]),''',
    '''   notes=["D7-s3-51: `_async_check_a4` must not return inside finally."]),
 dict(id="F9.3", lane="F9", title="P1 declared-domain barrier: stored fields held to their writers' domains",
   findings=[], covers=["D1-s3-06", "D1-s4-01", "D1-s5-02", "D1-s4-03"],
   edit=["tests/finite_boundary.py"], borrows={CC+"store.py": "F1"}, after=["F1.6"], tvofi=None,
   notes=["New at tvofi's answers (card C1, 'Domain table', over the recommendation to keep the residue per seam). The P1 RCA's residual section (rca/p1/RCA.md, 'What it does not cover') is the design basis: Arm 4 refuses poison and magnitude, not a value outside the domain only its writer knows, and not a loader discarding a whole valid grid for one bad cell. F1.6's cap was full (three findings and two latent seams), so this is its own PR, after F1.6, which follows every P1 instance PR.",
          "Form: a declared-domain table for the stored fields, one entry per (store, field path) giving the domain the field's own update path enforces, held at the store boundary in store.py (borrowed from F1), and Arm 6 in tests/finite_boundary.py: seed every store through its real saver, substitute each declared field with a value just outside its domain and one inside, run the real loaders, and refuse any out-of-domain value held live. Blast radius (D1-s4-03): the same arm substitutes one bad cell per grid and refuses a load that loses more than that cell. An undeclared stored field is refused (no allow-list, fixer.md step 14); a field a loader deliberately discards whole is declared so, with its reason.",
          "Covers D1-s3-06 (FrequencyMap decile and ratio), D1-s4-01 (defrost duty), D1-s5-02 (price-shape and peak-tracker domains) and D1-s4-03 (the defrost grid's blast radius), plus the fields the P1 RCA names: a decile of 12-99, window_factor at 1e12 and a duty of 1.5. The findings close in F3.2 and F3.3, which fix each seam; this PR is the class-level check and closes no finding. The RCA sized the table at about 150 stored fields: derive the field list from the Arm 4 seed (every leaf the real savers write), never carry the count.",
          "Demonstrate it failing on each of the four findings' seams re-introduced at the head, passing on the fixed tree, and silent on a healthy load (the populated seed round-trips unchanged); and a planted undeclared field refused. If the table cannot be held in store.py without editing a writer module another lane owns, stop and ask the orchestrator for the borrow rather than widening the scope.",
          "Cost: the arm multiplies Arm 4's mutant count by two per declared field; measure its wall time at the head and apply the RCA's optional cut (sample nested grid rows first and last) if it passes Arm 4's own. tests/closures.json for tests/finite_boundary.py is re-derived with derive_closures.sh --single on Linux, as F1.6's carry says."]),''')
rep(''' "F9.1": ("sonnet", ""), "F9.2": ("sonnet", ""),''',
    ''' "F9.1": ("sonnet", ""), "F9.2": ("sonnet", ""),
 "F9.3": ("opus", "a class barrier tvofi commissioned (P1 declared domain, card C1) with no prototype: the domain table's design is open"),''')

# ---------------------------------------------------------------- C8, C9, B1, B2: F10.2
rep('''   tvofi="tests/stress.py is code-owned; new stress_budgets.json entries and the loop_cpu_ratio budget go through budget-raise-gate",''',
    '''   tvofi="tests/stress.py is code-owned; the loop_cpu_ratio entry and the valve rows are allowed (cards B1, B2) and still merge only on tvofi's approving review (budget-raise-gate)",''')
rep('''          "Owed decisions, asked before the push (TVOFI-ASKS): the loop_cpu_ratio entry in COST_BUDGETS (the prototype's figure is this box's, not the canonical runner's), the valve scenarios' stress_budgets.json rows, whether the three throttling-valve plants are sampled at their full price or cheaper members are measured first, and the production-call channel's subset or full form.",''',
    '''          "tvofi's decisions (19:16Z): the loop_cpu_ratio entry in COST_BUDGETS is allowed (card B1), recorded on the canonical runner, not this box; the production-call channel is the subset form (card C8, one scenario per family); the valve axis is covered by cheaper members, not the three throttling-valve plants at their full price (card C9, 'Cheaper'): pick the cheapest member per valve mode the topology allows (summer, one zone, as the zero-range trio already is), and add stress_budgets.json rows only for those members (card B2).",
          "Residual blind spot, recorded (card C9): a CPU regression that only a throttling valve's winter, two-zone path exercises stays outside the sample; the plant-axis coverage check still refuses an unreached valve mode, but not an unreached valve-mode and season pair. Name it in the body and in the class's tools/audit/bugclasses.json entry as a known residual; it is not a finding.",''')

# ---------------------------------------------------------------- C7: F10.3; C12, B5: F10.4
rep('''          "Waits on F9.2 (the last I1 pin PR) because the I1 barrier lands here.''',
    '''          "Not now (tvofi's card C7): the single-line mutant format is not extended to multi-line tests, clamps or ternaries; record the 101 multi-line if tests, 99 clamps and the TERN gap as the barrier's residual in the body, re-derived at the head. The comparison-bound operator is F10.6 and the kill-ledger writer F10.5 (cards C6, C5), both after this PR.",
          "Waits on F9.2 (the last I1 pin PR) because the I1 barrier lands here.''')
rep('''   tvofi="D7-s1-01 prices coordinator state reached through module-level helpers, which likely raises coordinator budgets: ask before the push",''',
    '''   tvofi="D7-s1-01 prices coordinator state reached through module-level helpers; tvofi allowed raising the coordinator structure budgets if the honest re-record raises them (card B5), to the measured value, and the raise merges only on tvofi's approving review",''')
rep('''          "D7-s1-01: if the honest re-record raises a structure budget, stop and ask tvofi before the push (CLAUDE.md rule 2)."]),''',
    '''          "D7-s1-01: if the honest re-record raises a structure budget, tvofi has allowed it (card B5): re-record with --allow-regression and the reason in the commit message, to the measured value only, and name every moved metric in the body.",
          "I5 arms extended (tvofi's card C12, 'Extend checks', the RCA's option 3, about 60 test lines): the arms also reach the behaviour-prose findings no arm reached, which retires the separate D6-s1-02 check and the D6-s2-04 count; run them at the merge base and the head and list every FAIL line against its instance PR."]),
 dict(id="F10.5", lane="F10", title="Nightly mutation-kill ledger writer: drain the pre-ratchet stock (I1 residual)",
   findings=[], edit=["tests/mutation_table.py"],
   borrows={".github/workflows/tests.yml": "F11", "docs/decisions/0011-app-authored-identity.md": "F11"},
   after=["F10.4", "F11.2"],
   tvofi="tvofi chose to build it (card C5); it needs a new writer identity under decision 0011, whose App and credential are a Mac/tvofi action, and tests.yml, tests/mutation_table.py and the decision are code-owned",
   notes=["New at tvofi's answers (card C5, 'Build', over 'not now'). The I1 RCA's residual (a): the pre-ratchet unpinned stock has no path to a disposition because mutation-nightly drives --scope full --max 40 and records nothing. This PR records the nightly's kills as killed_by rows in the mutation ledger and pushes them to main, so the stock drains; survivors (the RCA's sample: about 11 percent) are listed for a human verdict, never auto-triaged (ci-autofix.md).",
          "Identity (decision 0011): the writer is a new App identity distinct from hpo-author, hpo-approver and hpo-runs, allowed to push only ledger rows under tests/mutation_ledger/ with a ci: subject the loop guards recognise. The decision's amendment names it and its write set. Creating the App, installing it and storing its credential are a Mac/tvofi action, not the fixer's: the fixer writes the workflow step fail-soft while the secret is absent (as the Actions-only approval App already is) and the amendment text, and stops there.",
          "tests/mutation_table.py gains a record mode that turns one run's kills into ledger rows; the nightly step in tests.yml calls it and pushes. Demonstrate on a scratch ref: one nightly-sized run writes rows for exactly the sites it killed and none for survivors, the per-site ratchet then reads those sites as pinned, and a second run over the same sites writes nothing (idempotent). Derive the stock's size and nights-to-drain at the head; never carry the RCA's figures.",
          "Borrows tests.yml and the decision record from F11 after F11.2, F11's last PR on tests.yml. After F10.4 in lane order, so no round-9 PR waits on the identity setup."]),
 dict(id="F10.6", lane="F10", title="Comparison-bound mutation operator (I1 residual), cost measured first",
   findings=[], edit=["tests/mutation_table.py", "tests/mutation_budgets.json"], borrows={}, after=["F10.5"],
   tvofi="tvofi commissioned it (card C6); tests/mutation_table.py is code-owned, and any mutation_budgets.json change merges only on tvofi's approving review",
   notes=["New at tvofi's answers (card C6, 'Commission', over 'no'). The I1 RCA's residual (b): no operator mutates an ordering comparison, so D3-s1-01's bound (-5.0 <= value to <) was marked accounted for while unpinned. This PR adds a comparison-bound operator (< to <=, <= to <, and the mirrored pair) to the deterministic inventory.",
          "Measure its cost first, before enabling it: with the operator in list mode only, derive at the merge base the number of new inventory sites, how many are unpinned, the per-PR pin burden (new comparisons per merged PR over the last round's merges) and the nightly minutes at the current --max. Report those to the orchestrator for tvofi before the operator joins the per-site ratchet; if tvofi declines at that cost, the PR lands the operator in list mode only and says so.",
          "Ordering hazard, as F10.3's: once enabled, every later PR that adds a comparison owes a pin. It is the last PR in F10, so no round-9 fix PR meets it. No local mutation pools: count with list mode, check one mutant in memory against D3-s1-01's line, and leave evaluation to CI's mutation lane."]),''')
rep(''' "F10.4": ("opus", _BAR + " (I5) plus ratchet truth"),''',
    ''' "F10.4": ("opus", _BAR + " (I5) plus ratchet truth"),
 "F10.5": ("opus", "a new writer identity pushing to main from CI (decision 0011): a wrong write set or loop guard corrupts the ledger or loops"),
 "F10.6": ("opus", "a new mutation operator in a code-owned gate script, whose cost must be measured and priced before it is enabled"),''')
rep(''' "F11.5": ("sonnet", "lands RCA drafts tvofi has approved, verbatim, and syncs the Cursor mirror"),''',
    ''' "F11.5": ("sonnet", "lands RCA drafts tvofi has approved, verbatim, and syncs the Cursor mirror"),
 "F11.6": ("opus", "a verdict carry decides when a review stops being re-run; a wrong equivalence silently approves a changed tree"),''')

# ---------------------------------------------------------------- C3: F1.11; C4: F8.3
rep('''          "P2 census precondition (P2 RCA, state d):''',
    '''          "The P6 arm S solve (about 1 to 2 s) runs in the per-PR gate, not nightly (tvofi's card C3, 'Per PR').",
          "P2 census precondition (P2 RCA, state d):''')
rep('''          "D5-s1-03: docs/dashboard-card.md changed in #1643 after the baseline; re-measure first.",''',
    '''          "D5-s1-03: docs/dashboard-card.md changed in #1643 after the baseline; re-measure first.",
          "D6-s1-81 (a P11 residual): tvofi accepted per-instance contracts for hass doubles outside tests/hastub (card C4, 'Per case'), not the harness-double refactor; this PR fixes the claim and names the per-instance pin.",''')

# ---------------------------------------------------------------- refusals, cap exceptions, decisions record
s += '''

# ---------------------------------------------------------------- tvofi's answers (2026-09-26 19:16Z)
# cmsg_01EL5jLi4rokGBbkaevYXSJV6CQVMDN96YfVMTcN5QGSx2: tvofi answered all 35 cards (TVOFI-ASKS.md, DECISIONS).
# Findings closed as refused by tvofi, with no PR: gen.py counts them placed and prints them.
REFUSED = {
 "D8-s2-01": "refused by tvofi (card C15, 'Keep'): the A3(e) ruling stands, the climate entity stays unavailable without an indoor thermometer as recorded, and F7.3 is dropped; the refusal is recorded against A3(e)",
 "D11-s1-01": "refused by tvofi (card C16, 'Leave'): the ruleset setting is unchanged; no ruleset, decision or policy edit",
}
# PRs allowed over fixer.md's five-item cap, each by tvofi's explicit choice. gen.py refuses any other.
CAP_EXCEPTIONS = {
 "F6.1": "tvofi, card D2 'Enlarge F6.1' (19:16Z): F6.1b merged back, four findings and four P9 instances",
}
'''
open(P, "w").write(s)
print("data.py patched")
