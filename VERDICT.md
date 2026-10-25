Fix review: blocked 683dd52cbb938ad00b38857117710791f5581f4b class-open: a writer the before end refused now passes, a wrapped argv whose open bracket is on the program's line and whose subject is on a later line (subprocess.run(["gh",\n "pr", "merge", str(n), "--squash",\n "--subject", s], check=True)), refused=1 at d0d35231 and refused=0 at the head under the finder's harness

bus-nonce: c9f56678938c303f574685af35040d6a

## Block

This is review round 6. The fixer re-cut the guard as `fixer.md` owes from round 4 on: `MERGE_CALL` no longer reads the program, and the extent opens at `pr`.

The program class is closed (see Evidence). The re-cut also brought in a regression in the extent:
- `LEAD` cannot cross a bare line end (`LINE_GAP`, pinned by mutant L2).
- So when the program ends its line, as in `["gh",` followed by a newline, the match starts on the line of `pr`.
- `callExtent` looks for an open bracket only from the start of that line (`agreement.mjs:195`, `ls = text.lastIndexOf('\n', at - 1) + 1`).
- So it never sees the `[` on the program's line. The extent ends at the end of the `pr` line, and a subject flag on any later line goes unread.
- At the before end, `PROGRAM` matched `gh"` on line 1, so that line's `[` opened the extent and the same writer was refused.

Measured with the finder's harness, `python3 -I tools/policy/agreement_py.py --run`, by appending one `if False:` writer to `tools/audit/seat/merge_train.py` (`ev/regress_plant.sh`, output in `ev/regress_plant.txt`):
- at d0d35231: `57 merge call(s)`, `REFUSED merge-subject-pr writer tools/audit/seat/merge_train.py:4176`, refused=1;
- at 683dd52c: `62 merge call(s)`, refused=0;
- unperturbed, both ends: refused=0.

The self-test's probes do not cover this shape. The same shape through my own probe (`ev/own_probes_wrap.txt`, `w-gh-own-line2`) is `["tools/x.py:1"]` at d0d35231 and `[]` at the head. The nearest probe, `cmd = ["gh", "pr",\n "merge", n, "--subject", s]`, has its `[` on the line of `pr`.

This is the hand-wrapped style the tree itself uses: continuation-aligned lists, as at `tools/audit/seat/record_row.py:962`.

Remedy: read the open-bracket context before `pr` from before the line of `pr`. Scan from the start of the statement, or from the last blank line, with the quote tracker, and keep the innermost bracket still open at `pr`. Add these probes:
- this wrapped shape;
- the exploded argv in the Findings;
- a null control: a sibling argv in an enclosing table on earlier lines, which L4's probes already shape.

Add a mutant that restores the line-local scan.

## Findings

- The wrapped-argv regression above: a writer refused at d0d35231 passes unseen at 683dd52c (Block). Carry: R10-MERGE-SUBJECT-HARDEN
- An exploded argv is unread at both ends and not dispositioned in the body. This is one expression, one element per line, as black or prettier writes an over-long list, with the subject after `merge`: `run([\n "gh",\n "pr",\n "merge",\n str(n),\n "--subject",\n s,\n])`, and the same in JS with `execFileSync('gh', [\n 'pr',\n 'merge', ...`. Both return `[]` under `.py`, `.mjs` and `.sh` names, at both ends (`ev/own_probes_byext.txt`). The root is the Block's line-local bracket scan, so the same remedy settles it. Carry: R10-MERGE-SUBJECT-HARDEN
- An option value between `pr` and `merge` that is an expression rather than one bare run is unread at both ends. The body's `VALUE` list (a quoted run, a `SLOT`, one bare run) does not name these shapes and no disposition covers them. Each returns `[]` (`ev/own_probes_byext.txt`):
  - `"-R", cfg["repo"]`
  - `"--repo", os.environ["REPO"]`
  - `"-R", f"{owner}/{repo}"`
  - `"-R", REPOS[0]`
  - `"-R", join(o, r)`
  - JS `'-R', cfg['repo']`
  - the shell word `-R "$O"/"$R"`

  JS `` `${o}/${r}` `` is refused. This is the family that round 5's second finding opened (an option value in a gap). It is one expression, not one split across expressions. Fix it by code (a `VALUE` arm for a subscript, a call or an f-string, or a gap-tolerant value that runs to the next argv comma), or disposition it with its reason. Carry: R10-MERGE-SUBJECT-HARDEN
- Two gaps inside one expression are unread at both ends and not dispositioned. Each returns `[]`:
  - a comment between `"pr",` and `"merge"` (Python `# ...` + newline, JS `/* ... */`);
  - Python implicit string concatenation, `os.system("gh pr " "merge 9 --subject x")`.

  Read them by code (comment and adjacent-literal arms in `GAP`), or name them under Unpinned sites. Carry: R10-MERGE-SUBJECT-HARDEN
- The census rule is line-scoped: it lists lines that hold both words. It cannot list a call whose `pr` and `merge` sit on different lines, or a call whose subject is on a later line than both words, and those are the shapes in the first two findings. So "no seam is open" holds only for one-line calls. Extend the census with a rule that reads `pr` and `merge` within one bracket group across lines, or state the bound in the body. Carry: R10-MERGE-SUBJECT-HARDEN

## Evidence

Head, CI and merge:
- Round 6. Head measured: `683dd52cbb938ad00b38857117710791f5581f4b` (`ev/HEAD.txt`). It was still the PR's head when I re-read it before writing this verdict. The body names it as the head.
- The role files are read from origin/main (`dev/governance/roles/fix-review.md`).
- `git merge-tree --write-tree origin/main 683dd52c` exits 0 with tree `99e75e11`, against origin/main `12b22200`, with no conflict (`ev/merge_tree.txt`).
- VERSION, the manifest and RELEASE_NOTES.md are untouched, checked three-dot against the merge base.
- CI on this head, from the check-runs API at my read: no check concluded red. These were success: `tests / mutation`, `arch-score`, `budget-raise-gate`, `governance / policy-docs`, `hassfest`, `validate-hacs`, and `codeql` actions and javascript.
- These were still queued or in progress: `pr-contract`, `governance / env-matrix`, `wave-script`, `instrument-self-tests`, `delivery-status`, `tests / closure-scope`, `tests / briefs`, `tests / nightly-status`, and `codeql` python.
- So step 11 has nothing to answer at this read.

The program class (the brief's main question) is closed at the head:
- The six round-5 probes are each refused at the head (`["f:1"]`) and return `[]` at d0d35231, the null control (`ev/own_probes.txt`, `ev/own_probes_byext.txt`; probe source `ev/probe.mjs`, `ev/probes.json`):
  - f-string `{GH}`;
  - `{gh_bin}`;
  - `{self.gh}` under shell=True;
  - `%s`;
  - `{}`.format;
  - JS `${cfg.gh}`.
- The control `${GH}` is refused at both ends.
- Round 5's second finding, `gh pr -R $(cat r) merge 9 -t x`, is refused at the head and `[]` at the before end.
- The PR's argv-seam generator, run from a pristine copy of each end's `agreement.mjs`, gives:
  - at the head: `PROGRAM-CLASS merge refused=144 of 144; view refused=0 of 144`;
  - at the before end: `merge refused=44 of 144; view refused=0 of 144`;
  - its first three lines are `[]`, `[]`, `["f:1"]` at both ends (`ev/argv_seam_head.txt`, `ev/argv_seam_before.txt`).
- I did not write a separate generator of interpolation shapes over program names. The program is no longer read, so a program generator tests only `LEAD`'s optionality. Instead, my own probes vary what the structural reader still reads: gaps, values and extents. Those probes found the four findings above.

Over-fire, benign plants at the head:
- These return `[]`: `gh xpr merge`, `gh pr merged`, `echo $pr merge`, and `f"{GH} pr view {n} -t x"`.
- `# we used to pr merge here --subject x`, a comment, is refused. That is the body's stated design choice: prose that names the two words is read as a call and can only add a refusal.
- The census of tools/ and .claude/workflows/, `r10_merge_subject_census.mjs` against the before end's guard (`ev/census.txt`), gives:
  - `TOTAL old=56 new=61 over 290 file(s)`;
  - five `DIFF` lines, at `merge_pr.sh:152`, `:186`, `:200` and `merge_train.py:3119`, `:3121`;
  - `UNCOVERED 55 of 95 line(s)`.

  All of these match the body. The finder's harness gives refused=0 unperturbed at the head, so the census reads no new writer.
- `CMD="pr merge"; gh $CMD 9 --subject x` on one line is refused at the head and `[]` at the before end, which is a gain.

Finder's harness at both ends under the PR's plants (`ev/plants_head.txt`, `ev/plants_before.txt`):
- Unperturbed: `61 merge call(s) in 11 file(s)` at the head and `56` at the before end, both `RESULT divergent=0 unregistered=0 dead=0 refused=0`.
- These five plants give refused=0 at the before end and refused=1 at the head:
  - the f-string program;
  - the `%`-format program;
  - the `.format` program;
  - `${cfg.gh}`;
  - `gh pr -R $(cat r) merge`.
- The other ten plants give refused=1 at both ends.
- The two null plants give refused=0 at both ends.
- All of this matches the body. The first-parent count is 305 at my run.

Self-test and mutants:
- `node tools/policy/agreement.mjs --self-test` gives `SELF-TEST 141 of 141 probes held` (`ev/selftest.txt`).
- With the before end's guard block (`// WHAT A MERGE CALL IS` up to `function nonTemplateMerges`) put into the head's file, the self-test gives `SELF-TEST 119 of 141 probes held` with 22 FAIL lines (`ev/old_guard_selftest.txt`):
  - the ten `spelling:` probes the body lists;
  - twelve `program class:` probes, all but the list join, the argv and the JS argv.

  This matches the body.
- `python3 dev/audit/harnesses/r10_merge_subject_mutants.py` gives 67 rows and no `NOT APPLIED` (`ev/mutants.txt`). Exactly X5, Y9 and Y10 print `141 of 141`. Each named row matches the body: L1 139, L2 139, L3 139, L4 133, L5 94, R4a 140, R11d 138, R11e 139, R11f 140, RV2 117, RV5 128.
- I read X5, Y9 and Y10:
  - X5 can only widen the extent;
  - Y9 drops only the closing bracket character;
  - Y10 touches only a one-character last line.

  I concur with their `Carry: dismissed`.

The body's other `Carry: dismissed` (words split across expressions, in-word quoting, gh aliases, eval) is concurred:
- A lexical scan cannot read any of these shapes. The two words in different expressions, `m"erge"`, an alias resolved in gh's config, and `eval` of a built string each need evaluation.
- `git grep -n -e '--subject' tools/audit/seat/merge_pr.sh tools/audit/seat/merge_train.py` prints nothing at the head.
- The shapes in my Findings are not of that kind. Each is one expression with both words adjacent in it, and each is readable by a lexical scan.

Figures I did not re-take:
- `MODE: SCOPED`, entities `2 of 2429`, structure, policy_lint, rules_sync, ci_predict, archscore `dS +0.0000 NULL`, and the run_always lines.
- These are the body's own, at code head 46d41ddc. CI's runs on this head are the authority for them, and they were still running at my read.

Instruments are my own and disclosed: `ev/probe.mjs` loads the head's or the before end's guard block the way the argv-seam harness does, `ev/probes.json` and `ev/probes2.json` are my probe sets, and `ev/regress_plant.sh` is my plant under the finder's harness.
