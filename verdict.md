Fix review: blocked 455d7c2001fc7b94d39f9a0feb933894d9ca704d class-open: MERGE_CALL spellings gh and Python accept still pass unseen, and the gh-to-pr continuation arm survives deletion

bus-nonce: d80279e66a77e018eb1e327c348ac4ee

## Round

This is the third review of #2697 by the body's numbering (round-1 and round-2 verdicts are answered in the body). The dispatch brief calls it round 2. A fourth review would owe a re-cut, not a repair (fix-review.md).

## Block

The brief asked me to judge whether the shell arm's class is closed. It is not closed. The class is the spellings of one merge call that `MERGE_CALL` must read. The body says the continuation finding is "Closed, not dispositioned" and that the table's three survivors are the only unpinned sites. Neither statement holds at this head.

1. **Surviving mutant on the line this round repaired (fix-review.md step 1).** `MERGE_CALL`'s shell arm has two gaps, `gh`→`pr` and `pr`→`merge`. The new continuation probe drives only the second. Mutant R-first-gap is `\bgh(?:\s|\\\r?\n)+pr` → `\bgh\s+pr`, with the second gap left as is. Under it the self-test prints `SELF-TEST 41 of 41 probes held` (ev/own_mutants.txt). It is a real writer miss. `gh \`, newline, `  pr merge 9 --merge --subject "Merge pull request #9 (x)"` gives `bad ["f:1"]` at head and `calls [] bad []` under the mutant (ev/first_gap_probe.txt). The 33-row table in `r10_merge_subject_mutants.py` has no row for this. So the body's "Every other mutant ... is killed" holds for the table, not for the repaired line. The fix: add one probe with the continuation between `gh` and `pr`.
2. **Spellings of the same call that gh accepts pass unseen. The body neither closes nor dispositions them.** With the head's own `subjectWriters` (ev/shell_arm_shapes.txt, `ev/probe.mjs`), each of these gives `calls 0 bad []`:
   - `gh pr "merge" ...`, `gh pr 'merge' ...` and `gh "pr" merge ...` (quoted words);
   - `gh pr -R o/r merge ...` and `gh --repo o/r pr merge ...` (a flag between the words). gh 2.89.0 accepts all three spellings checked (ev/gh_spellings.txt);
   - the argv arm written with single quotes, `run(['gh', 'pr', 'merge', n, '--subject', s])`, and the same split over lines;
   - `"pr" , "merge"` (whitespace before the comma).
   This is the finder's harness with a perturbation (ev/harness_perturbed.txt, `python3 -I tools/policy/agreement_py.py --run`). The tree's own merge call at `tools/audit/seat/merge_train.py:864`, rewritten in single quotes with a `--subject`, drops the call count to `54` and prints `refused=0`. The call is no longer even counted. `gh pr "merge"` and `gh pr -R o/r merge`, planted in `merge_pr.sh`, print `refused=0` at both base `73b69fe0a` and this head. The single-quoted argv is an ordinary Python spelling, and the argv arm is a literal `"pr",\s*"merge"`, the same shape as Y8. The body's class rule 2 (`git grep -E 'gh pr merge|merge_pull_request'`) is itself a literal-spelling grep, so it cannot return a spelling it does not match. It enumerates scan sites, not call spellings. The body names no rule for the spellings. No site of these shapes is on the tree today (ev/tree_census.txt), so this is a seam of the guard, not a live writer. The cost of closing it is about one regex arm (`["']pr["']\s*,\s*["']merge["']`, and optional quotes around `pr` and `merge` in the shell arm) plus probes. Alternatively, the body can disposition each member with its reason the way it does the argv-across-expressions seam. Either one settles it. Silence does not.

## Findings

- `MERGE_CALL`'s `\\\r?\n` accepts a backslash-CRLF as a continuation, and bash does not: there the backslash escapes the `\r` and the newline ends the command. `callExtent` also tests `text[i - 1] !== '\\'`, so a CRLF continuation's extent ends at the call line anyway. The `\r?` is dead weight that can only add a call, never miss one. The R-crlf mutant (the `\r?` removed) holds 41 of 41 (ev/own_mutants.txt). Carry: dismissed: widening only; no writer miss on any shell input
- Y9 (close bracket excluded from the extent): I agree with the body's disposition. I re-ran it myself (R-Y9-own, 41 of 41). `SUBJECT_ARG`'s lookahead already accepts `]`, and `"` precedes any quoted closing `)`. Removing the close can only let `$` match a bare flag right before `)` or `}`, which is a refusal the head does not make. It is never a miss. Carry: dismissed: near-equivalent mutant that only widens refusal; no writer miss
- Y10 (end-of-file tail of the blank-line test): I agree with the body's disposition. R-Y10-own holds 41 of 41. The mutant only changes a file's single-character last line. That line cannot hold a subject flag, and every earlier line of the extent is already read when it returns. Carry: dismissed: equivalent for writer detection; end-of-file single-character line only

## Evidence

- Head measured: `455d7c2001fc7b94d39f9a0feb933894d9ca704d` (ev/HEAD.txt). It is still the PR head at verdict time (PR commits list), so the head did not move. It matches the body's `## Head`.
- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 against origin/main `4a00a3f05` (ev/merge_tree.txt). No conflict.
- Self-test at head: `SELF-TEST 41 of 41 probes held` (ev/selftest.txt).
- Mutation table: `python3 dev/audit/harnesses/r10_merge_subject_mutants.py` at head runs 33 mutants. Exactly X5, Y9 and Y10 print `41 of 41`, and every other row names a FAIL (ev/mutants.txt). This matches the body's table. The working tree is clean afterwards.
- Own targeted mutants (ev/own_mutants.txt): R-second-gap (continuation dropped between `pr` and `merge`) is killed, 40 of 41. R-first-gap survives, 41 of 41 (Block 1). R-crlf survives, 41 of 41 (Findings).
- Finder's harness, unperturbed (ev/harness_unperturbed.txt). Base `73b69fe0a`: `52 merge call(s) in 11 file(s)`, `RESULT divergent=0 unregistered=0 dead=0 refused=0`. Head: `270 first-parent commit(s)`, `55 merge call(s) in 11 file(s)`, `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`. The body's 52→55 and refused=0 reproduce. The body's `265 first-parent commit(s)` at this head reads 270 now, because the first-parent count grows with origin/main. Only the 265 is not re-derivable here.
- Finder's harness, perturbed (ev/harness_perturbed.txt). A first-gap continuation plant in `merge_pr.sh` gives `refused=0` at base and `refused=1` (56 calls) at head, so the repair works on that shape even though no probe pins it. The quoted-word and `-R`-between plants give `refused=0` at both ends. The single-quoted rewrite of `merge_train.py:864` gives `54 merge call(s)`, `refused=0` at head.
- Census of the missed shapes on the scan's surface (`tools/`, `.claude/workflows/`): no site (ev/tree_census.txt). The census rules are my own, written for this review, and are not the body's.
- Instruments built for this review and disclosed as my own (fix-review.md step 9): `ev/probe.mjs` and `ev/p2.mjs`. They use the same guard-block extraction as `dev/audit/harnesses/r10_merge_subject_argv_seam.mjs`.
- CI on this head (ev/ci.txt): `pr-contract` completed failure, and `gate` and one `prelude` are still queued. The head's workflows have not all concluded, so I do not judge step 11 (red-check answer) in this verdict. The body's `## Red checks: none` is to be re-checked once they conclude.
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched by the three-dot diff. The diff's fifth file, `dev/programme/delivery/2697.md`, is the record row (commit `b4dd11917`).
