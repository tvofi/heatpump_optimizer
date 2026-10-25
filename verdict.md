Fix review: blocked e73424f247781b8d5e55abe52f54d7005cb51f39 class-open: a shell case-arm writer (`  never) gh pr merge "$n" --squash --subject "..." ;;`) is counted as a merge call but its subject goes unread, refused=0 under the finder's harness at the head, 683dd52c and d0d35231, while the `(never)` spelling of the same arm is refused=1

bus-nonce: 35d25ade68c3515b5b869a097a3434bc

## Block

This is review round 7, a re-cut as `fixer.md` owes from round 4. The re-cut does settle round 6's regression (see Evidence). The extent class is still open on a shape the tree uses all the time, and nothing in the body names it.

The cause:
- `callExtent` starts the forward read at the line's start (`ls`) when no bracket is open at `pr`. That is `const start = open.length ? open[open.length - 1] : ls` in `tools/policy/agreement.mjs`, in `callExtent`.
- So the forward read reads the lead again. A closer in the lead that has no opener is the `)` of a shell `case` arm pattern (`never)`). It takes `depth` below zero, and the extent returns at that `)`, before `pr`.
- The backward read already dropped that same `)` as an empty pop. Only the forward read trips on it.
- Nothing after the arm pattern is read: `--subject`, `-t`, `--body` and the rest.

Measured with the finder's harness, `python3 -I tools/policy/agreement_py.py --run`, with each end's guard. One case-arm writer was appended to `tools/audit/seat/merge_pr.sh` (`ev/case_plant.sh`, output in `ev/case_plant.txt`):
- head e73424f2: unperturbed `63 merge call(s)`, refused=0. Case-arm plant: `64 merge call(s)`, refused=0.
- 683dd52c: 63, then 64, refused=0.
- d0d35231: 58, then 59, refused=0.
- Control: the POSIX `(never)` arm form gives refused=1 at all three ends (`merge_pr.sh:260`).

So the guard counts the call but does not read its subject. This is not a regression, since it misses at every end. It is reachable:
- `git grep -cE '^\s*[^ ()#"]+\)\s+\S'` over `tools/*.sh` and `.claude/workflows/*.sh` counts 282 case-arm lines that carry a command on the arm line.
- They include `tools/audit/seat/merge_pr.sh:81`, `:86` and `:187`, in one of the two files that merge.

The same root also misses a one-line `x) gh pr merge 9 -t s` (`ev/own_probes2.txt`).

Remedy: start the forward read at `pr` (or at the lead's start), not at `ls`, when no bracket is open. Or have the forward read skip a closer that the backward read already found unmatched. Add a probe for the case arm in `.sh` and `.md`, plus a `(a)` null twin. Add a mutant that restores `ls`.

## Findings

- The shell case-arm writer above. It is counted as a merge call, its subject is unread at all three ends, and the body does not disposition it (Block). Carry: R10-MERGE-SUBJECT-HARDEN
- The body's `Carry: dismissed` for a blank line between an argv's open bracket and `pr` is a deferral of a reachable spelling, not a shape a lexical scan cannot read. I do not concur.
  - The reason given is "the same bound the forward read already sets in a shell or prose file". But the plant is a Python or JS file.
  - In a Python or JS file, `callExtent`'s own forward read already reads across a blank line inside a bracket ("except in a Python or JS file, where the language reads a blank line inside a bracket as nothing"). So the backward read could do the same for `kind !== 'sh'`.
  - Both of these return `[]` at all three ends (`ev/own_probes.txt` `py-blank-in-bracket`, `ev/own_probes2.txt`): `run([\n "gh",\n\n "pr", "merge", n,\n "--subject", s])` and the JS `execFileSync('gh', [\n\n 'pr', 'merge', n,\n '--subject', s])`.
  - I could not re-derive "black never writes a blank line inside a bracket" (no black run here). As far as I know, black keeps blank lines a user puts between elements, so I treat that clause as unverified.

  Read it by code, or re-state the disposition with a reason a lexical scan cannot meet. Carry: R10-MERGE-SUBJECT-HARDEN
- A JS `/* */` comment that holds a closer after `merge` ends the extent early. `execFileSync('gh', ['pr', 'merge', n, /* ) */ '--subject', s])` returns `[]` at all three ends. The control with `/* x */` is refused.
  - `GAP` already reads `/* */` (G arms), but `commentAt` reads only `#` and `//`. So the two reads of one call disagree on what a comment is.
  - The body does not disposition this.

  Extend `commentAt` to `/* */` for `kind === 'js'`, with a probe. Carry: R10-MERGE-SUBJECT-HARDEN
- A JS regex literal holding an escaped closer, `String(n).replace(/\)/g, '')`, between `merge` and the subject ends the extent early. It returns `[]` at all three ends. A regex literal is hard to tell from division by a lexical scan, so dispositioning it with that reason is acceptable, but the body does not name it. Name it under Unpinned sites, or read it. Carry: R10-MERGE-SUBJECT-HARDEN

## Evidence

Head, CI and merge:
- Round 7. Head measured: `e73424f247781b8d5e55abe52f54d7005cb51f39` (`ev/HEAD.txt`). It was still `refs/pull/2697/head` at 2026-10-25T05:35:12Z, after the last measurement. The body names it as the head.
- Roles: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- `git merge-tree --write-tree origin/main e73424f2` exits 0 with tree `5db207f5` against origin/main `8a11b8bd` (`ev/merge_tree.txt`).
- VERSION, the manifest and RELEASE_NOTES.md are untouched, three-dot (`ev/version.txt`).
- CI on this head, from the check-runs API at my read (37 runs): none concluded failure.
  - Success: `tests / mutation`, `tests / typing`, `tests / browser`, `tests / arch-instrument`, `tests / closure-scope`, `tests / briefs`, `tests / nightly-status`, `arch-score`, `budget-raise-gate`, `governance / env-matrix`, `governance / policy-docs`, `governance / delivery-status`, `governance / wave-script`, `hassfest`, `validate-hacs`, and `codeql` actions and javascript.
  - Still in progress: `tests / closures`, `tests / coverage`, `tests / fast (3.14)`, `governance / instrument-self-tests` and `codeql` python.
  - Step 11 has nothing to answer at this read.

Round 6's regression is settled:
- The finder's argv-seam generator, `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs <each end's agreement.mjs>` (`ev/argv_seam.txt`):
  - head: `WRAPPED merge refused=12 of 12; null refused=0 of 12` and `PROGRAM-CLASS merge refused=144 of 144; view refused=0 of 144`;
  - 683dd52c (null control): `WRAPPED merge refused=0 of 12`, PROGRAM-CLASS 144 of 144, view 0;
  - d0d35231: `WRAPPED merge refused=3 of 12`, PROGRAM-CLASS 44 of 144, view 0.

  The first three seam lines are `[]`, `[]`, `["f:1"]` at all ends. All of this matches the body.
- My own extent-class generator (`ev/probe.mjs`, output in `ev/own_probes.txt`) has 46 probes. They cover wrapping after the program, after `pr` and after `merge`; nested brackets and an outer call; a dict holding the argv; a closed group on earlier lines; quotes holding brackets across line ends; Python and JS comments with an opener or a closer; a triple quote before the call; a black-style exploded argv with trailing commas; JS backtick strings; shell continuation, arrays and comments; and six over-fire nulls.
  - At the head, 42 of 46 hold.
  - The four misses also miss at both earlier ends. They are the Findings: the blank line in the bracket, the JS block comment, the regex and the case arm.
  - No probe that holds at either earlier end misses at the head, so there is no regression.
  - 683dd52c misses 26 probes and d0d35231 misses 19. So the re-cut is a strict gain over both ends.
- Over-fire: every null probe gives `[]` at the head. These are a wrapped `pr view`, a later sibling `pr edit --title` in a table, Markdown prose, an earlier statement's flag, an earlier open bracket's flag and an enclosing call's earlier flag.
- The census `node dev/audit/harnesses/r10_merge_subject_census.mjs <683dd52c's agreement.mjs>` (`ev/census.txt`) gives:
  - `TOTAL old=63 new=63 over 290 file(s)` and no DIFF line;
  - `UNCOVERED 57 of 98`, `EXTENT 11 of 63`, `SPLIT 1 of 1`.

  This matches the body, and the finder's harness reads refused=0 unperturbed at the head. So the census reads no new writer.

Self-test and mutants:
- `node tools/policy/agreement.mjs --self-test` gives `SELF-TEST 177 of 177 probes held` (`ev/selftest.txt`).
- `python3 dev/audit/harnesses/r10_merge_subject_mutants.py` gives 84 rows, no `NOT APPLIED`, exit 0 (`ev/mutants.txt`). Exactly Y9 and Y10 print `177 of 177`.
  - X5 is now killed (176), by the enclosing-table null.
  - P1 170, P2 170, P3 176, P4 176. All match the body.
- I concur with Y9 (it drops only the closing bracket character) and Y10 (it changes only a one-character last line) as near-equivalent.
- I concur with the `Carry: dismissed` for words split across expressions, in-word quoting, gh aliases and eval. A lexical scan cannot read any of these; each needs evaluation.

`python3 tests/structure.py` gives `STRUCTURE RATCHET PASSED`, exit 0 (`ev/structure.txt`).

Instruments: `ev/probe.mjs`, `ev/probe2.mjs` and `ev/case_plant.sh` are my own, not the finder's. The finder's harnesses are `agreement_py.py --run` and the PR's argv-seam, census and plants scripts. I used them at both ends as above.
