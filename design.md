# Design: R10-MACHINERY-RATCHETS

Base: origin/main 56630e7e6d229d960cf1b4db304d488ee20873e6 (round 2; round 1 read ddf4bfd73bc764d6daf44f508f67139521d45724, its first-parent ancestor). Roster: handoff/audit-r10-roster at 7e5e5866e1870ea9c5300d0c022eb79d1941950c. No predecessor, so the code was read at main. The finding is the owner's report (tvofi, 2026-11-01). No finder harness exists: the evidence is the owner's report. The enumerators in `## Figures` reproduce its 14-day count from main's first-parent history.

## Owning seam

One new program under tools/audit/, the machinery ratchet, owns the classification of a merge and both metrics. Its data is a new machinery-budgets JSON file under dev/governance/config/, beside dev/governance/config/policy_budgets.json. Callers only: a step in the `policy-docs` job of .github/workflows/governance.yml, and an entry in the `SCHEMA` registry of tools/policy/budget_raise_gate.py. Every budgets file was added to that registry the same way, so the entry is not a second owner. Nothing writes state that another module owns. tests/seam_map.json maps no tools/audit/ path.

## Shape

**Counting rule.** It is deterministic from one merge commit M, a first-parent two-parent commit on main, with first parent P. Read `git diff -M -w --numstat P M`. Product lines are the added plus deleted lines of paths under custom_components/ or blueprints/. Every other line is a nonproduct line. M is a **production** merge when its product lines are above 0. It is a **record** merge when every path it touches is under dev/programme/, RELEASE_NOTES.md or VERSION. Every other merge is **machinery**. Stamp commits are single-parent pushes, so they are not merges and they are outside the window. `-M` makes a pure move cost 0 lines on both sides. `-w` makes a reformat cost 0.

**Window.** The newest W first-parent merges, where W is a frozen key in the budgets file equal to the owner's 14-day count. The window counts merges, not hours. A time window gives the same commit a different value at a different wall-clock time, and an idle week would move it with no merge. **Push mode** is a `--check` run on a push to main: the window is the newest W first-parent merges ending at HEAD. **PR mode** is a run on a pull_request event: the window is the newest W−1 first-parent merges of the base plus the PR itself as one candidate merge, read from its three-dot diff (merge-base..head). In both modes every merged M is graded by its own P and M, never by the head's files, so one merge counts the same in a push run and in a PR run.

**Metrics.** Both caps are one-sided. Each is compared against its cap plus its band, in the shape policy_budgets.json uses:
- **nonproduction-merges** is the count of record and machinery merges in the window. It is the owner's measure.
- **churn ratio** is nonproduct lines per 1000 product lines over the same window. It is stored as an integer, so the budget gate's finite-number check applies.

**Bands.** Each band is the largest rise of its metric above its running minimum over the newest 150 window positions. This is the rule tests/ci_budgets.json used for critical_path_minutes_band: the measured spread, unpadded. The cap is re-recorded down when the measurement falls more than the band below it (dev/governance/rules/ratchet-budgets.md).

**Exemption, the owner's: a change proving a >10% improvement.** It lives in an `exemptions` list in the machinery-budgets file. Each entry gives the PR number, the measure (CI time, programme completion time, right-first-time or token usage), before, after, the command that produced each value, and an evidence path. The instrument reads an entry only when three conditions hold:
- the improvement is strictly above 0.10. For a cost it is (before−after)/before; for right-first-time it is (after−before)/before.
- the evidence path resolves at the head.
- the PR number is the merge subject's number for a merged M, or the event's PR number for the candidate.
- the entry was added by the merge it exempts. For a merged M (on a push, and for each of the base's W−1 merges in PR mode) the entry is absent from the budgets file at P and present at M. For the candidate it is absent at the merge base and present at the head. An entry added by any other merge exempts nothing, so an entry appended later for an already-merged PR cannot drop that merge from the window.

A matching merge leaves the window, and the next older merge fills it. A merge with no entry is counted, so an unrecorded raise is refused by the cap. Proposal-triage's bar takes the same record: an ACCEPT that skips the bar cites the entry (one line in dev/governance/roles/proposal-triage.md). `SCHEMA` classes the leaves as follows:
- caps and bands: `max`
- W: `frozen`
- `exemptions`: `superset`. Appending an entry records it and asks nobody; removing one is a raise.

The added-by-its-own-merge condition is the instrument's, not `SCHEMA`'s, so it holds under `superset` or `override` alike. Decisions, as ruled under mandate 6329234399:
- decided: `exemptions` is a superset. The base caps always apply, and an exemption only adds headroom for its named merge.
- decided: record merges get no carve-out. Records merge only inside a stamp batch, so the cap counts them there; a capped main holds owed records for that batch rather than merging them one by one.
- decided: R10-FLY-STANDING-CONTRACTS lands first (design/r10-fly-standing-contracts f214494449b9291146424f97ae3477e1089e4ea5 also edits dev/governance/roles/proposal-triage.md and dev/governance/config/policy_budgets.json). This group is set after it and re-measures on rebase.

**Flow.** governance.yml `policy-docs` runs these steps in order:
1. It restores the program from the base. The fixer adds the program's path to that step's pathspec. The PR that lands the program is graded by its own copy, which is the stated hole for a new file.
2. The program runs `--check` with the base, the head and the PR number.
3. On exit 1 it prints each metric, its cap and its band.

There is no network and no roster read. The `instrument-self-tests` job greps the `--self-test` count line, in the same way as for budget_raise_gate.

**Gaming.** The table shows how M1 (nonproduction-merges) and M2 (churn ratio) each respond to every move.

| move | M1 | M2 |
|---|---|---|
| split a machinery PR in two | rises by 1 | flat |
| split a production PR in two | falls: this is the hole | flat, so the machinery merges the split buys still add M2 churn |
| fold machinery into a production PR | counts production: this is the hole | flat: the lines count as nonproduct wherever they land |
| fold a record into a production PR | falls, a real merge saved | flat |
| move a file across the boundary | 0 lines under -M | 0 lines under -M |
| append an exemption for an already-merged PR | flat: the entry was absent at that merge's M | flat |
| write machinery as product code | counts production | that code ships, and the dead-symbol metrics in tests/structure_budgets.json read it |

Each metric closes the other's hole. The one residual left is product churn that changes no behaviour, and it is visible in the shipped diff.

## Rejected candidates, by the data

- **(2) Record merges per production merge.** Record merges are already in M1's numerator, so a separate cap refuses nothing that M1 does not. It is also lowered by splitting production.
- **(3) Open machinery groups.** Main holds only the stamp-time copy of the roster, which disagrees with the handoff copy (Figures). A gate on main would therefore grade a file the PR does not change, and folding two groups into one lowers the count with no work removed.
- **(4) Carries per machinery PR.** The markers live in PR bodies and on the handoff branch, so the merge commit gives no source.
- **(5) Accepted proposals per round.** dev/programme/triage/ counts ACCEPT verdicts, but main has no round boundary until the v10.0.0 stamp that this group precedes. Writing two proposals as one `P` entry also lowers the count.
- **(6) CI minutes.** These are already capped per push run as critical_path_minutes in tests/ci_budgets.json, from the API rather than from git. Per production PR, that cost is bounded by M1.
- **(6) Tokens.** No source in the tree measures them.

## Alternatives

- **Extend the `flow` board in tools/audit/merge_throughput.py.** Lost because `move_kind` classifies by branch name (a production change on a record branch counts as record), reads bus refs and the roster, and prints UNAVAILABLE rather than failing. A required check cannot degrade.
- **Add the metrics to tests/ci_ratchet.py.** Lost because its inputs are CI emitter lines, its file lies outside dev/governance/config/, and budget_raise_gate's governance of that directory is the reason the brief puts the caps there.
- **Use a 14-day time window.** Lost because it is not deterministic per commit (see Shape).

## Sibling sites

`git grep -ln "budgets.json" -- '*.py' '*.mjs' '*.yml'` lists every reader of a budgets file. Of those, only budget_raise_gate.py needs the new file, through its `SCHEMA`. `git grep -n "def move_kind"` finds the only other merge classifier, item N2.

## Evidence plan, by file, in order

1. **Failing test first.** The program's `--self-test` builds a temporary repository, as `flow_self_test` in merge_throughput.py does. It is written before the measuring code and run red. Its arms:
   - k production merges in N give N−k.
   - A candidate machinery merge at cap+band refuses (exit 1).
   - **Null control:** a rename-only move of a tools file into custom_components/ leaves M1 and M2 byte-identical.
   - Splitting a machinery merge raises M1 by exactly 1. Splitting a production merge leaves M2 flat.
   - Exemption arms: no entry refuses; exactly 10% refuses; 11% with evidence passes; 11% with a missing evidence path refuses; an entry appended later for an already-merged PR leaves M1 and M2 unchanged.
2. **Detector shown to detect.** At the fixer's merge base, `--check` exits 1 with a cap one below the measurement and exits 0 at the measurement. Both runs go in the body.
3. **The budgets file.** Recorded at the merge base's measurement; re-measure, never copy `## Figures`.
4. **budget_raise_gate.py.** Its `SCHEMA` entry plus self-test arms: raising a cap is a raise, lowering one is free, removing an exemption is a raise, and changing W is a raise.
5. **governance.yml.** The step, the pathspec line and the self-test grep.
6. **Instrument doc.** tools/audit/seat/INSTRUMENTS.md gets one line and tools/audit/seat/instruments/ gets the program's page.
7. **Closure.** The program enters a measured closure, as merge_throughput.py sits in tests/entities.py's. That closure is recorded by the Linux derive or the UNDER-SCOPED autofix, never by hand and never off Linux. It is not added to tests/closure.py `INERT`.
8. **Policy text.** A section in ratchet-budgets.md. It is policy, so the owner approves before merge. Its per-file cap in policy_budgets.json has zero headroom, so it is paid by cuts, or the fixer asks before the push.

**Mutation proof targets.** The fixer names their lines:
- the product-prefix test
- the `> 0` production test
- the record all-paths test
- `measured > cap + band`
- the window's drop-oldest in PR mode
- the strict `> 0.10`
- the evidence-exists check

No golden files and no claim files are involved.

## Hot files, serial position, carries

- hot_files: dev/governance/roles/proposal-triage.md and dev/governance/config/policy_budgets.json, shared with R10-FLY-STANDING-CONTRACTS.
- after: R10-FLY-STANDING-CONTRACTS (decided above). On rebase, re-measure `## Figures` and the policy_budgets.json headroom for ratchet-budgets.md and proposal-triage.md.
- R10-FLY-CLOSURE-MAJOR waits on this group.
- .github/workflows/governance.yml is also in R10-DEPS-ACTIONS-BUMP's files, with no edge between the two groups. Whichever group lands second rebases.
- decision: orchestrator — add tools/policy/budget_raise_gate.py, dev/governance/roles/proposal-triage.md and the new budgets file to the group's files.
- Seat token count: the harness reports none.

## Notes for the fixer

- Splitting a PR doubles the push runs while the per-run cost stays under its cap: the critical_path_minutes cap in tests/ci_ratchet.py is per run. The ratchet's merge count bounds those runs. Carry: dismissed: bounded by nonproduction-merges cap (item N1)
- The flow board's `move_kind` reads the branch prefix, so a branch name moves a merge across kinds. Carry: dismissed: flow board grades no merge (item N2)
- policy_budgets.json `corpus_tokens` against prose moved between files: the glob rule in ratchet-budgets.md already closes it. Carry: dismissed: already closed in tree (item N3)
- structure.py counts fall when a long method is split. Carry: dismissed: decomposition is the improvement (item N4)
- governance.yml overlaps R10-DEPS-ACTIONS-BUMP. Rebase onto whichever group lands first, and re-run step 2 after the rebase. Carry: R10-MACHINERY-RATCHETS (item N5)
- Measured cost of the full window: 13 s on this seat (`time` around the M1/M2 enumerator). That is the standing cost per governance run. Carry: R10-MACHINERY-RATCHETS (item N6)

## Figures

Each figure below is at 56630e7e6d229d960cf1b4db304d488ee20873e6, with its enumerator. The fixer re-measures at its own merge base.

- **M1 / window / M2: 521 580 13624.** Enumerator: `git log --first-parent --format='%H %P' 56630e7e6d229d960cf1b4db304d488ee20873e6 | awk 'NF==3' | head -580 | while read h p q; do git diff -M -w --numstat $p $h | awk -F'\t' '{n=($1=="-"?0:$1)+($2=="-"?0:$2); if($3 ~ /^(custom_components|blueprints)\//) P+=n; else N+=n} END{print P+0, N+0}'; done | awk '{if($1==0)m++; P+=$1; N+=$2} END{print m, NR, int(1000*N/P+0.5)}'`
- **Kind split: 213 machinery, 59 production, 308 record.** This reproduces the owner's 59 of the 14 days. Enumerator: the same loop with `git diff --name-only $p $h | awk '/^(custom_components|blueprints)\//{x=1} !/^(dev\/programme\/|RELEASE_NOTES.md$|VERSION$)/{o=1} END{print x?"production":(o?"machinery":"record")}' | sort | uniq -c`
- **Bands: M1 5 merges, M2 2436.** Range over the newest 150 positions: M1 516..526, M2 11188..18162. Enumerator: the M1/M2 loop over `head -730`, then sliding windows of 580 and the largest rise above the running minimum.
- **ACCEPT verdicts: 218, in 87 files since 2026-10-22.** Enumerator: `git grep -c '^Verdict: ACCEPT' 56630e7e6d229d960cf1b4db304d488ee20873e6 -- dev/programme/triage | awk -F: '{s+=$NF} END{print s, NR}'`
- **Open groups: 75 at the roster SHA (61 with no product file) and 50 on main.** Enumerator: the open-group count over `groups[].files` of dev/programme/rosters/wave-r10-groups.json, at each ref.
