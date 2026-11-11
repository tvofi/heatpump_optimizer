policy: the standing seats' shared terms live once in standing.md; tick and roster retire into beat rows

Implements design/R10-STANDING-CONTRACTS-P2 at a249d7685e1e (design-verdict reads `Design review: approve a249d7685e1ed6e87588e37201ca8e09d711bbf0`), carries 0-20 of the group. Leaves #3115 open and leaves #3134 open: the orchestrator's two gate records below are owed before the stubs merge.

## Head

dd5faa50c0a87aec310975128c18b172e052af3a, the pull request head: it holds the earlier handoff tip 5a4161d57647ccdfc82f9cd0e6988abcb81bfaed, a merge of origin/main and the delivery-row record commit. This round changes no code; it routes the body's carry items (see Red checks and Friction). `tools/pr/prepr.sh` is clean at this head with the body, and `git merge-tree --write-tree origin/main HEAD` reports no conflict. The mutation figures below were measured at 5a4161d57647, whose production diff this head carries unchanged.

## What changed

- `dev/governance/roles/standing.md` (new): Wait, Reads, Autofix hold, Recycle, Alive files, written once. `standing-merge.md`, `standing-dispatch.md` and `proposal-triage.md` cite it.
- `standing-tick.md` and `standing-roster.md` are retirement stubs naming their rows of `tools/audit/seat/beatd.jobs.json`.
- `standing-merge.md`: a budget-file or policy head takes the train's serial route; `merge_pr.sh` is no longer named as a merge route.
- `standing-dispatch.md`: the hand-written `git ls-remote` block gives way to standing.md's Reads row.
- `orchestrator.md` section 5: two standing seats; state is read only from the plan page and the ledger's digest; the recycle routing clause. Section 10b names the `roster-drain` queue.
- `fixer.md`, `designer.md`, `design-review.md`: the grader-first split (triage P371 parts a and b). `designer.md` step 1: on a revise, the verdict the payload pins.
- `tools/audit/seat/cloud_dispatch.py`: `dispatch_group` reads the tip of `design-verdict/<group>` from origin for a designer and pins that commit and the first line of its verdict.md in the payload; with no ref the designer text is unchanged.
- `tools/audit/seat/pulse.py`: `STANDING` holds merge and dispatch; `RETIRED` holds tick and roster; `--seat-queue` refuses a retired seat.
- `tools/audit/seat/sweep_template.md`: the three tick placeholders and step (5)'s tick-seat restart are gone.
- `tests/entities.py`: one check, rows a-c. `tests/closures.json`: standing.md joins that script's closure (`tests/derive_closures.sh --single tests/entities.py --record-only`, then `tests/closure.py merge --partial --allow-failures`; the traced run's only failing checks were the two refusing the unclassified file).
- `dev/governance/config/policy_budgets.json`: a row for standing.md at its measure; the tick and roster rows lowered to the stubs' measure. No existing cap rises: `node tools/policy/policy_lint.mjs --budgets` exits 0.

Departures from the design note, each forced by a check:
- standing.md's PR-state row names `pull_request_read` (`web-fragments.md`), not the `gh` command carry 2 and the note quote: policy_lint's no-gh check refuses that command outside `web-fragments.md`. `tools/audit/seat/gh_read.py` offers no command-line PR-state read (design item 17).
- The handoff file is named `STATE-HANDOFF` without its extension: policy_lint's citations check refuses a path that is not in the tree.
- The stubs quote the owner's constraint in part and cite `dev/audit/README.md` for the rest: policy_lint's duplicates check refuses the whole sentence twice.
- `dev/governance/config/corpus_excluded.json` gains `tools/audit/round9/fixplan/standing.md`: the new basename collided in policy_lint's named-docs check.
- Row (c) of the entities check names fixer.md and does not read `tools/pr/ci_predict.py`: that file is INERT and `tests/closure.py merge` refuses an INERT file a test reads.
- The lines of fixer.md and orchestrator.md citing decisions 0010 and 0011 keep their text at the merge base: policy_lint's citation-presence fixture counts those two citations, and the layout guard refuses a touched line that keeps the retired path.

Payments inside each capped file (wording tightened, no rule removed): fixer.md drops step 3's pointer to step 8, step 14's first #714 instance (its second paragraph keeps #714) and one "rather than assuming"; orchestrator.md drops the tail of section 1's heading, the quoted text of `judge.md`'s void rule (the pointer stays) and "four readers parse it" in section 11 (`standing-merge.md` carries it); design-review.md shortens the R10-SCORES instance to its three rounds; designer.md points step 7's carry grammar at `design-review.md`. The owner reviews these as policy.

## Mutation proof

Each mutant is applied by hand to a `git archive` copy of the head and the named self-test run there (driver: the fixer's scratch `mutants.py`, its replacements quoted below). An entities mutant is judged on the one check's own line, because an archive copy reddens unrelated checks.

    MUTANT NULL-pulse SURVIVED at 5a4161d57647 rc=0: pulse self-test: 60 checks, 0 failed
    MUTANT P1 KILLED at 5a4161d57647 rc=1: FAIL every standing seat pulse judges is a tracked contract, and every contract a seat || FAIL --seat-queue refuses the retired seat tick, a beat row now
    MUTANT P2 KILLED at 5a4161d57647 rc=1: FAIL every standing seat pulse judges is a tracked contract, and every contract a seat || FAIL --seat-queue refuses the retired seat roster, a beat row now
    MUTANT NULL-sweep SURVIVED at 5a4161d57647 rc=0: sweep_render self-test: 35 checks, 0 failed
    MUTANT S1 KILLED at 5a4161d57647 rc=1: FAIL the tick seat is retired: no tick_alive, tick_brief or tick_stale_min placeholder, declared or rendered
    MUTANT NULL-cloud SURVIVED at 5a4161d57647 rc=0: cloud_dispatch self-test: 155 checks, 0 failed
    MUTANT C1 KILLED at 5a4161d57647 rc=1: FAIL a designer's text names no design-verdict ref while none exists (null control)
    MUTANT C2 KILLED at 5a4161d57647 rc=1: FAIL a designer's text pins the revise verdict's own commit and first line
    MUTANT C3 KILLED at 5a4161d57647 rc=1: FAIL a designer's text pins the revise verdict's own commit and first line
    MUTANT NULL-entities SURVIVED at 5a4161d57647 rc=0: ok   the standing seats' shared terms are written once in standing.md, cited by each standing contract, and fixer.md carries the BOOTSTRAP remedy and decision 0013
    MUTANT E1 KILLED at 5a4161d57647 rc=1: FAIL the standing seats' shared terms are written once in standing.md, cited by each standing contract, and fixer.md carries the BOOTSTRAP remedy and decision 0013  [missing: ['b:## Recycle']]
    MUTANT E2 KILLED at 5a4161d57647 rc=1: FAIL the standing seats' shared terms are written once in standing.md, cited by each standing contract, and fixer.md carries the BOOTSTRAP remedy and decision 0013  [missing: ['b:mutation-autofix', 'b:closures-autofix', 'b:claims-
    MUTANT E3 KILLED at 5a4161d57647 rc=1: FAIL the standing seats' shared terms are written once in standing.md, cited by each standing contract, and fixer.md carries the BOOTSTRAP remedy and decision 0013  [missing: ['b:claims-autofix']]
    MUTANT E4 KILLED at 5a4161d57647 rc=1: FAIL the standing seats' shared terms are written once in standing.md, cited by each standing contract, and fixer.md carries the BOOTSTRAP remedy and decision 0013  [missing: ['c:fixer.md:BOOTSTRAP', 'c:fixer.md:0013']]
    MUTANT E5 KILLED at 5a4161d57647 rc=1: FAIL the standing seats' shared terms are written once in standing.md, cited by each standing contract, and fixer.md carries the BOOTSTRAP remedy and decision 0013  [missing: ['a:proposal-triage.md']]
    MUTANT E6 KILLED at 5a4161d57647 rc=1: FAIL the standing seats' shared terms are written once in standing.md, cited by each standing contract, and fixer.md carries the BOOTSTRAP remedy and decision 0013  [missing: ['a:standing-merge.md']]

- P1, P2: `STANDING` in pulse.py regains `"tick": 70` / `"roster": 60`.
- S1: sweep_template.md regains the three tick placeholder rows and a step (5) that restarts a tick seat from them.
- C1: `dispatch_group` passes a verdict pair unconditionally. C2: the verdict read is skipped (`if False:`). C3: the design tip is pinned in place of the verdict commit.
- E1: standing.md loses the `## Recycle` heading. E2: it loses the autofix-hold predicate sentence and keeps the heading. E3: it loses the one job name `claims-autofix`. E4: fixer.md loses the BOOTSTRAP paragraph. E5: proposal-triage.md loses its standing.md citation. E6: standing-merge.md loses its citation.

Failing first: on origin/main's fixer.md the new entities check prints `missing:` with `c:fixer.md:BOOTSTRAP` and `c:fixer.md:0013` (P371's dangling citation); the designer verdict-pin case, added before the production change, printed `FAIL a designer's text pins the revise verdict's own commit and first line`.

## Null control

The `NULL-*` lines above: the unmutated archive copy passes each self-test and the entities check prints `ok`. Carry 5's control: `git grep -n merge_pr.sh -- 'dev/governance/roles/standing-*.md'` prints nothing at the head and prints a `standing-merge.md` line at 8f97247fc1a6, the branch's first base.

## Figures

none

## Unpinned sites

n/a: the diff adds no site under `custom_components/`; the `tools/` sites are pinned by the self-test mutants above.

## Red checks

- `budget-raise-gate / budget-raise-gate`: red by design until the owner approves at the head or the mandate signs it. The diff changes three pinned token-cap rows of `policy_budgets.json`: standing.md's first row at its measure, and the standing-tick.md and standing-roster.md rows lowered to the stubs' measure. policy_lint's budgets check refuses a new policy file without both caps, so no edit that adds standing.md avoids the gate. The cheaper detector exists and ran: `tools/pr/prepr.sh` with the body predicts it in seconds; without a body it prints no raise line, which is where this seat first read it as no raise. The prepr.sh seam is not this group's; its live owner is R10-PREPR-RESIDUE (files `tools/pr/prepr.sh`, stage in-progress, on `origin/handoff/audit-r10-roster`), which receives the finding that step 6d's raise prediction prints no line when no body is supplied. Carry: R10-PREPR-RESIDUE

## Raise justification

No cap loosens: one row is new at the file's measure and two fall. The gate reads all three as pinned values it cannot sign as routine.

- Payments tried: (1) no standing.md, each term copied into the four standing contracts (carries 1-4 as written): four files within 4 tokens of their caps each need a raise, and the rule is then written four times. (2) the terms folded into orchestrator.md: at its cap, and the standing seats do not read it. (3) the corpus cost of standing.md paid by the two stubs and standing-dispatch.md's removed block: taken; `--budgets` exits 0 and no corpus or role cap is touched (after the merge of main the corpus line reads over its cap inside its band, as main's own tree does). (4) leaving the tick and roster token caps at their old values to avoid two of the three rows: refused, it leaves two retired stubs with unused headroom of several hundred tokens.
- Architecture score: dS +0.0000 NULL

Measured by `python3 tools/audit/archscore/score.py --diff origin/main` at the head.

## Approval

Policy: every edited role contract, `CLAUDE.md`, decision 0015 and `policy_budgets.json`. The owner's approving review at merge, or the mandate: tvofi's comment 6624093439 on #201 reads `MANDATE: agents may approve as tvofi, scope all, from 2026-11-04T06:18Z until 2026-11-14T18:14Z`, unedited, read 2026-11-11T08:27Z; this seat read no later comment revoking it and could not page #201 past its first page, so the gate's own reader is the authority. Routed by the design verdict, still open:
- decision: owner: carries 1-4 ask for the Wait, Reads, autofix-hold and Recycle text in each standing contract; this writes them once in standing.md.
- decision: owner: standing.md's new cap rows and the two lowered token caps; `## Raise justification` above.
- decision: orchestrator: the two gate records owed before the stubs merge: `beatd status` with every P1 row `ok` from main for one cycle beside the live seats; and roster-drain landing a seeded no-op-safe op on a scratch roster branch and refusing a seeded lint failure.
- decision: orchestrator: carries 21, 22 and 23 are outside the approved design (verdict item 22) and are not built here.

## Carries of the brief

- Carry 0: parts (a) and (b) built in fixer.md, designer.md and design-review.md; part (c) was already on main.
- Carry 1: built, once, in standing.md (Wait).
- Carry 2: built in standing.md (Reads), with the PR-state departure above.
- Carry 3: built in standing.md (Autofix hold); its control is rows a-b of the entities check and mutants E2, E3.
- Carry 4: built in standing.md (Recycle) and orchestrator.md section 5; the field figures stay in the triage record.
- Carry 5: built in standing-merge.md.
- Carry 6: already on main in standing-merge.md's Instruments paragraph.
- Carry 7: built in orchestrator.md section 5.
- Carry 8: built in orchestrator.md section 5.
- Carry 9: left for a later part; it stays on the roster.
- Carry 10: built as standing-roster.md's stub, behind the orchestrator's gate record.
- Carry 11: built as standing-roster.md's stub, behind the orchestrator's gate record.
- Carry 12: left for a later part; it stays on the roster.
- Carry 13: left for a later part; it stays on the roster.
- Carry 14: left for a later part; it stays on the roster.
- Carry 15: built by #3197; sweep_template.md's remaining tick-seat text goes here.
- Carry 16: part (1) built by #3197, part (2) by #3294.
- Carry 17: the job was built by #3197; standing-tick.md's stub and the placeholder removal are built here.
- Carry 18: the jobs were built by #3197; the tick and roster seats leave the contracts here.
- Carry 19: built in standing.md (Alive files).
- Carry 20: built in cloud_dispatch.py and designer.md step 1.
- Carry 21: left for a later part; it stays on the roster.
- Carry 22: left for a later part; it stays on the roster.
- Carry 23: left for a later part; it stays on the roster.
- Carry 24: no further carry; the list above numbers from 0 as the brief does, and `review_packet.py` counts the same entries from 1, so its last is the brief's Carry 23.
- Carry 25: left for a later part; it stays on the roster.
- Carry 26: left for a later part; it stays on the roster.
- Carry 27: left for a later part; it stays on the roster.
- Carry 28: left for a later part; it stays on the roster.

## Forward-carry

- Carries 9, 12, 13 and 14 (the merge-seat retirement and the dispatch beat job) have no live owner: the design named R10-ORCH-LEDGER, which is not among this group's valid targets. They stay on this group's roster entry in `dev/programme/rosters/wave-r10-groups.json` pending the orchestrator's routing. Carry: R10-STANDING-CONTRACTS-P2 (item scp2-unbuilt-seats)
- Carries 21, 22 and 23 (the liveness hook's three arms with their constraints, and pulse.py reading the merge train) are outside the approved design; the verdict proposes a liveness-hook group and a pulse.py group ordered after this one. They stay on this group's roster entry in `dev/programme/rosters/wave-r10-groups.json` pending the orchestrator's ruling. Carry: R10-STANDING-CONTRACTS-P2 (item scp2-carries-21-23)
- `dev/programme/HANDOVER.md` names four standing seats in its standing-seats bullet; it is updated with the merge it records (verdict item 27). Carry: R10-STANDING-CONTRACTS-P2 (item scp2-handover-seats), the owner-routed ruling of the design verdict's item 27

## Friction

- standing.md: contradiction: carry 2 orders the `gh` PR-state command into a role contract that policy_lint's no-gh check refuses outside `web-fragments.md`. Carry: dismissed: resolved here by citing web-fragments.md
- fixer.md: cost: the layout guard refuses a re-wrapped line that keeps a retired `docs/decisions/` citation while policy_lint's citation-presence fixture needs that citation present, so the only passing edit leaves the line untouched; one prepr round and one closure re-record were spent finding it. Carry: dismissed: first instance, resolved here by leaving the line untouched; no mechanism change is asked, and a second instance goes to root-cause.md
