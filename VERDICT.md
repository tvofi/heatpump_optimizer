Fix review: blocked 4aad9c1175318dec0b90da4113259c3ddb38309f class-open: the head regresses main on every line whose lead holds an unmatched closer, not only the case arm the body names; a wrapped Markdown parenthetical closing on the merge line (`down) with gh pr merge 9 --subject x`) is refused=1 at main 880b667aa and refused=0 at the head under the finder's harness, and neither the body nor R10-MERGE-SUBJECT-CASEARM's class text covers it

bus-nonce: 8c5003d6861fc4309716aaa71264dbbe

## Block

Review round 8. This is the owner's three-round split, so a narrowed class is legitimate. The narrowed class itself holds (Evidence). What does not hold is the body's account of the regression it accepts.

The body says the regression against main is "that one spelling", the case arm, and carries it to R10-MERGE-SUBJECT-CASEARM, whose class text is "every shell case-arm spelling". The cause the body itself quotes is wider than a case arm:
- When no bracket is open at `pr`, `callExtent` starts the forward read at the line's start.
- Any `)` in the lead with no `(` before it on that line ends the extent before `pr`.
- main's line guard reads the whole line, so it refuses all of these.

So the head lets through, and main refuses, spellings that are not case arms. Every one below is in the guard's scan surface (`tools/`, `.claude/workflows/`, `.md` included):
- **Markdown prose wrapped inside a parenthetical**, e.g. `Merge it by hand (the train is` / `down) with \`gh pr merge 9 --subject x\`.`.
  - The finder's harness `python3 -I tools/policy/agreement_py.py --run`, with this plant appended to `.claude/workflows/web-fragments.md` (`ev/md_plant.sh`, `ev/md_plant.txt`):
    - head: 64 merge calls, refused=0;
    - main 880b667aa: 54 merge calls, refused=1 at `web-fragments.md:157`.
  - Control, the same prose with no parenthetical: refused=1 at both ends.
  - It also misses at 683dd52c and d0d35231 (`ev/own_probes3.txt`). It is still a regression against main, which is what merging changes.
- **Markdown `1)` and `a)` list items, `- step 2) ...` and `:)`**: refused at main and missed at the head and 683dd52c (`ev/own_probes2.txt`).
- **A shell array closed on the merge line**, `x=(` / ` a` / `); gh pr merge 9 --subject x`: same result.

The shape is common in the scanned files. 134 of 1639 lines in the five scanned `.md` files hold a `)` with no `(` before it on the line (`ev/lead_closer_count.py`, `ev/reach.txt`). No such line holds a merge writer today: the finder's harness reads refused=0 unperturbed at the head. So this is a reachable domain the guard stops reading, not a live writer.

Remedy, either of:
- widen the carried class and the body to "a closer in the line's lead that has no opener on the line", with these probes added to the expected-fail and the body's regression paragraph corrected; or
- the root fix round 7 named: start the forward read at the lead's start, or skip a closer the backward read already found unmatched.

Either way, R10-MERGE-SUBJECT-CASEARM's roster brief must state the regression against main and its control before this merges (Findings).

## Findings

- The lead-closer regression above. It sits outside the stated class and outside the case-arm class text, and the body does not disposition it. Carry: R10-MERGE-SUBJECT-HARDEN
- R10-MERGE-SUBJECT-CASEARM's roster brief does not carry two things this PR established.
  - It states the miss as `refused=0 at e73424f2, 683dd52c, d0d35231` and never says main refuses the same spelling today. Merging #2697 turns that group from closing an open seam into repairing a regression on main. That changes the stage's urgency and its control: the control is main's own refused=1, measured at the stage's merge base.
  - It omits the three `routed` spellings, which the body routes to the group "for the roster seat to add". They are a blank line in a Python or JS argv, and a `)` in a JS `/* */` after `merge`.

  Both are in this PR's body only, at `origin/main` and at `handoff/audit-r10-roster` e78d7ded. The body also says "the roster has no brief field for it". The group has a `brief` string. Carry: R10-MERGE-SUBJECT-CASEARM
- The case-arm expected-fail enumerates only `never)`, `(never)`, `a|b)` and `(a|b)`, plus the one-line `x)`. It has no `*)` default arm and no glob pattern arm (`[0-9]*)`).
  - Both miss at the head and are refused at main (`ev/own_probes.txt`, 24 rows each).
  - The `*)` default arm opens 94 of the 331 arm lines in the tree's `*.sh` (`git grep -hE '^\s*\*\)'` against `'^\s*\(?[^ ()#"]+\)\s'`, at the head).
  - The class text, "every shell case-arm spelling", covers them, but the marked test that the group's fixer will run does not. Add them to the expected-fail. Carry: R10-MERGE-SUBJECT-CASEARM

## Evidence

Head, CI and merge:
- Round 8. Measured head: `4aad9c1175318dec0b90da4113259c3ddb38309f` (`ev/HEAD.txt`). It was still `refs/pull/2697/head` at 2026-10-25T08:18:12Z, after the last measurement. The body names it as the head.
- `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- `git merge-tree --write-tree origin/main HEAD` exits 0, tree `fb636299`, against origin/main 880b667aa (`ev/merge_tree.txt`).
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched, three-dot.
- CI on this head, from the check-runs API at my read (37 runs): none concluded failure.
  - Success: `tests / mutation`, `typing`, `browser`, `arch-instrument`, `closure-scope`, `briefs` and `nightly-status`; `governance / delivery-status`, `env-matrix`, `policy-docs` and `wave-script`; `arch-score`, `budget-raise-gate`, `hassfest`, `validate-hacs`, and `codeql` actions and javascript.
  - Still in progress: `tests / closures`, `tests / coverage`, `tests / fast (3.14)`, `governance / instrument-self-tests` and `codeql` python.
  - Step 11 has nothing to answer at this read.

Structure and mutants:
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`, `exit=0` (`ev/structure.txt`). No budget file is in the diff, so there is no re-record.
- `node tools/policy/agreement.mjs --self-test` → `SELF-TEST 177 of 177 probes held`.
- `python3 dev/audit/harnesses/r10_merge_subject_mutants.py` → 84 rows, 0 `NOT APPLIED`, exit 0. Exactly Y9 and Y10 print `177 of 177` (`ev/mutants.txt`), matching the body.

The narrowed class is closed under its own rule. `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs <guard>` at four ends (`ev/argv_seam.txt`):

| row family | head | 683dd52c | d0d35231 | main 880b667aa |
|---|---|---|---|---|
| PROGRAM-CLASS | 144/144 | 144 | 44 | 12 |
| WRAPPED | 12/12 | 0 | 3 | 0 |
| CLASS | 43/43 | 31 | 30 | 13 |
| every null twin | 0 refused | 0 | 0 | 0 |

- Every figure matches the body's table.
- The 12 `CLASS` rows that 683dd52c passes are exactly the body's list: three comment gaps, the literal join, `"$O"/"$R"`, six values and the exploded call.

The case arm is pinned open, with the group id in the harness:
- `OPEN R10-MERGE-SUBJECT-CASEARM expected-fail: held=16 of 33; null refused=0 of 33` at the head, 683dd52c and d0d35231. It is `held=33 of 33` at main.
- 17 lines print `XFAIL`. All are no-paren spellings at indentation 0, 2 and 8 spaces and a tab, in `.sh` and `.md`, plus the one-line `x)`.
- `routed: held=0 of 3` at all four ends.
- The body's Forward-carry states the class rule: with and without the paren, any indentation, multi-pattern arms.

My own generators are mine, not the finder's or the fixer's (`ev/probe.mjs`, `ev/probe2.mjs`, `ev/probe3.mjs`):
- `ev/probe.mjs` puts 19 leads before three subject writers, in `.sh` and `.md`, with and without `;;`:
  - head: `PROBE refused=180 of 228; null refused=0 of 8`;
  - main: 228 of 228;
  - 683dd52c: 180.
  - All 48 head misses are case arms: `never)`, `a|b)`, `*)` and `[0-9]*)`.
  - Leads that close their own bracket on the line are refused at the head: `( cd x ) &&`, `r=$(cat f) &&`, `[[ ]] &&`, `{ ...; } &&`, `a=(1 2);`, `$(( ))`, `if (( ))` and `echo ")"`.
  - Over-fire nulls are 0 of 8 at all ends: a `pr view` in an arm, an arm merge with no subject, a later sibling `pr edit --title`, and prose.
- `ev/probe2.mjs` and `ev/probe3.mjs` are the lead-closer probes in the Block. JS and Python statement tails that close an earlier line's bracket (`}); execSync(...)`, `]; os.system(...)`) are refused at the head.

Over-fire: the census reads no new writer. `node dev/audit/harnesses/r10_merge_subject_census.mjs <683dd52c's guard>` at the head (`ev/census.txt`):
- `TOTAL old=63 new=63 over 290 file(s)`, with no `DIFF` line.
- `UNCOVERED 62 of 103`, `EXTENT 11 of 63`, `SPLIT 2 of 2`.

The body's `UNCOVERED 58 of 99` and `SPLIT 1 of 1` were taken at 43940f75 against main 1aa765fd. The difference comes in with the 880b667aa merge. The new SPLIT is `tools/audit/seat/cloud_relay.sh:44`, which is a comment, not a call.

The body's other brief item, the `(#N)` title laxity, is in the diff as `TEMPLATE_SUBJECT` with its probe and null control.

UNCERTAINTIES:
- I did not re-run the body's `r10_merge_subject_plants.sh` table. My finder's-harness plant covers the new spelling only. The 18 spelling plants are taken from the body and from the argv-seam table, which I did re-run.
- I used `python3` from PATH. There is no `seat-python3` in this container.
- The figure of 134 lead-closer lines is my own definition: a `)` with no `(` before it on the line, over the guard's scanned `.md` files. It is not the guard's grammar.
- I did not judge whether the owner's split ruling meant to accept a regression against main at all. The block is on the body's under-statement of the regression, not on the split.
