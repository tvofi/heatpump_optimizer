Fix review: blocked d581d4e0b2e5fab662a2eb70b47b77b82ee5cc6e doc-claim-false: dev/README.md draws and states that the plan beat runs roster_sync.py and so writes the roster branch, and the plan beat never reaches it; three more sentences the diff adds are contradicted by the tree

bus-nonce: 92403cb174b38e04003d1fd1c5eaa5f4

Round 1 (first review). Measured at d581d4e0b2e5fab662a2eb70b47b77b82ee5cc6e, merge base 63bcdcaad827ad3d98f914bc2e5b6110f9bb9444, from a detached worktree.

## Block

The body's claim is that both pages are verified against the tree and that every arrow of the machinery figure is closed by its table row. Each item below is a statement this diff adds that the tree at the head contradicts. Reads are in `ev/tree_reads.txt`.

1. **The beat does not run `roster_sync.py`, so the drawn path beat -> docs -> roster branch is not performed.** `dev/README.md:406-408` says `roster_sync.py` is "run by the plan beat". `beat_jobs.py:424` runs `state_docs.py --push --mirror ... --plan ...`. `state_docs.py:574` enters the roster-sync step only under the `beat` subcommand with `--apply` (`state_docs.py:63`), and `state_docs.py:46` says that path never passes `--plan`. `roster_sync` is named in neither `beat_jobs.py` nor `beatd.jobs.json` (0 hits each). What runs it is `postmerge.py:47` (`roster_sync.py --repo ... --apply`). The figure's `beat -->|"runs"| docs` and `docs -->|"writes"| roster` therefore draw a write the beat's job does not make. The row passes `machinery_edge_findings` because the node groups three files and the actor-file rule accepts a citation from any basename in the label: the cited `roster_edit.write_roster(` is in `roster_sync.py`, which the cited runner never starts. Redraw from who starts `roster_sync.py`, and correct the sentence.
2. **`dev/README.md:194` "the only file a pull-request event starts".** `.github/workflows/dependabot-automerge.yml:38-40` starts on `pull_request_target`; the same list says so eight lines later ("starts on a Dependabot pull request").
3. **`dev/README.md:184` "three housekeeping jobs outside this chain".** `sweep-self` has `needs: gate` (`ci.yml:365-366`); it hangs off the chain's last job.
4. **`dev/README.md:380-382` "the figure shows the four that write a store".** The figure draws four `runs` targets of the beat. `replan.py` has no `writes` arrow and writes a local plan file; it and `state_docs.py` are one job (`plan_beat`). Three jobs write a store: roster-drain, plan-beat, opener.
5. **The entry predicate's second half is unpinned.** `if len(entries) != 1 or kind[entries[0]][0] != "seat":` mutated to `if len(entries) != 1:` leaves `tests/doc_claims.py` green (`ev/rev_mutants.txt`, P4). The fixer's `one entry` mutant replaces the whole test, so the harness's rule "one mutant per predicate test" does not see it. A red fixture whose single entry is a script closes it.
6. **Not re-read by me, reported by my locate pass; check and fix or disposition in the body.** `docs/architecture.md:90-92` lists the coordinator, `pump_arbiter` and `early_cutoff.py` as the direct readers of the pump's control entities; `pump_signals.py:457`, `services.py:834` and `config_flow.py:2232` also call `hass.states.get`.

## Findings

- Instrument: a node whose label names several files satisfies the actor-file rule with a citation from any of them, so a grouped node can carry an edge only one member performs, started by a path the figure does not draw (item 1 is the live case). Planting it needs no reversed arrow, so the reversal anchor does not see it. Carry: dismissed: owed in this pull request under Block item 1, the fixer's own round

## Evidence

- Fixer's harness at the head, `ev/mutants_head.txt`: `RESULT baseline_fails=0`, `RESULT mutants=12`, `RESULT killed=12`; two of the twelve die by crash, as the body says. The harness is the fixer's, not a finder's: the group has no committed finder harness.
- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` at the head: `ALL 318 checks PASSED` (`ev/doc_claims_head.txt`).
- Markers: head, in-tree roster and roster branch add34472b2 both `0 of 0 marker(s) due`, exit 0. Base with the roster branch's file: `28 of 28 marker(s) due`, two `UNRESOLVED`, exit 1. The body's roster SHA 39a92af760 is no longer the branch tip; the figure holds at the tip.
- My mutants, `ev/rev_mutants.py` and `ev/rev_mutants.txt`, builder the reviewer: `RESULT rev_mutants=21`, `RESULT rev_survivors=4`. P4 is Block item 5. P7 and P8 drop the live page's own check call and are the control for D1-D8 and S1-S2, which all die on the live page. P3 makes the entry rule stricter, not weaker. A due marker planted on either page is refused (D4, D5); a cited line removed from `tick_loop.sh` or `beat_jobs.py` is refused (S1, S2); an arrow reversed with its row and re-cited to a real line of the other script is refused (D6).
- Step 14, `tests/closures.json`: the recorded `tests/entities.py` `rc` moves 1 -> 0 at c4c28b4cef with `seconds` unchanged; main still records 1. I did not re-run the 868 s script; CI's `tests / closures` and `tests / fast (3.14)` at this head are the evidence, see CI below.
- Steps 4, 5: no golden or claim file, `VERSION`, manifest version or notes heading in the three-dot diff. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Step 10: the three forward-carries are on `handoff/audit-r10-roster` at add34472b2, each with its control command: R10-ARCH-DOCS-DELTA (items 6bc4f4e1, d5ef2398) and R10-USER-DOCS-VERIFY (item a44d0012).
- Step 13: `git merge-tree --write-tree origin/main` (444cf62fab) exits 0; `LEDGER-MERGE: resolved tests/closures.json`.
- Step 6: the enumeration rule (the `-->` lines under `### Its components`) returns arrows that all have rows; the open seam is not an unlisted arrow but item 1's grouped node.
- Not re-derived: the mermaid render figure (`5 block(s), 0 failure(s)`), the dark-theme look, the `prepr.sh` and `derive_closures.sh` history lines, `ALL 112 HARNESS HEADER CHECKS PASSED` (no `homeassistant` on this seat's bare path).
- The remaining machinery rows and CI-shape statements read true in my locate pass: nine units called and needed by `pr-contract`, `gate` needs `pr-contract`, the 18 workflow files all listed, `KINDS` holds the six listed event kinds, no script opens `train-stop`, `merge_train.py` has no pitch.
- CI at this head: `python3 tools/audit/seat/merge_train.py classify d581d4e0b2e5fab662a2eb70b47b77b82ee5cc6e --pr 3430` exits 0, `GREEN ... pending: none red: none` (03:22Z, `ev/classify.txt`). `tests / closures`, `tests / fast (3.14)` and `tests / mutation` are success in the packet digest; the diff writes no production code line, so `mutation` drew no mutant from it. A first `gate` run (id 130285221032) had concluded failure while the units were still running; the gate at id 130298435582 is success and the re-rendered packet carries no refusal, so no `## Red checks` answer is owed by `owed-reds` (`ev/owed-reds.txt`).
- Step 12: `git ls-remote` at 03:22Z reads `refs/pull/3430/head` at d581d4e0b2e5fab662a2eb70b47b77b82ee5cc6e, the head measured. Step 7: the body's `## Head` names it.
