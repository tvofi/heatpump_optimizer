Fix review: blocked 2e2b374cd982d0b4d3bc4853a0227239c28e4f76 brief-lint: P66 carry text cites carries/carry-N.json, which tools/policy/brief_lint.mjs reports as an unresolved path

bus-nonce: 127d3efbc4a38998d30eaf98d9eae335

## Block

- Round 1 for this seat. Reviewed head `2e2b374cd982d0b4d3bc4853a0227239c28e4f76`, which is still the PR head (base `73b69fe0a` = origin/main).
- The brief asks that every ACCEPT carries text `tools/policy/brief_lint.mjs` accepts. `brief_lint` reads a group's `brief` and never its `carry` array, so a roster with the seven texts appended lints clean whatever they say (ev/brief-lint.txt, base). To lint the texts themselves I folded each group's new carries into its `brief`. On that roster brief_lint prints `ERROR [R10-FLY-CARRY-DISPOSITION] path: carries/carry-N.json: not in the tree` (1 error; the unmodified roster prints 0). The error comes from P66's carry text (`dev/programme/triage/s6-batch8.md` line 22: "a `#N` item with `carries/carry-N.json` yield zero").
- Repair: write `dev/programme/carries/carry-<N>.json`, the form `brief-citations.md` itself uses. With that one substitution the same roster lints `TOTAL: 0 error(s)` (ev/brief-lint-fix.txt). The other six carry texts (P67, P70, P71, P72, P75, P76) lint clean.
- Sensitivity control: changing `tools/pr/prepr.sh` to a path that does not exist in JIDOKA's folded text adds exactly one path error (ev/brief-lint.txt, asbriefp). So the instrument reads the folded texts.

## Findings

- `tools/policy/brief_lint.mjs` lints a roster group's `brief` only (`lintFile`: `lintBrief(g.group, g.brief, ...)`), not its `carry` entries. `roster_edit.py --push`'s lint gate therefore accepts any carry text, including an unresolved citation like P66's. This is an instrument gap; this PR's diff does not touch it. Carry: O1
- The body's `## Head` section says `2e2b374c` "merges origin/main `73b69fe0a` ... into this PR's previous head". There is no merge commit: the parent chain is 2e2b374c -> 7b3b748d -> 1890ef70 -> 73b69fe0a. The code head and base it names are correct. Carry: dismissed: template wording from the orchestrator's script that misdescribes no figure or SHA

## Evidence

- Every ACCEPT names a live roster group (`handoff/audit-r10-roster` at 50c69075): P66 and P76 name R10-FLY-CARRY-DISPOSITION (not-started), P67 and P75 name R10-FLOW-JIDOKA (in-progress), P70, P71 and P72 name R10-FLY-OPENPR-ATOMIC (not-started). Each carry's append-carry target equals the group on its Verdict line. `roster_edit.ruling_verdict` returns ACCEPT for each ACCEPT, including the NARROWED ones. `triage_refusal` returns None for every text with its `triage:` citation (ev/carry-sim.txt). The DEFER targets are also live (R10-FLOW-BODY-ONLY not-started, R10-FLOW-JIDOKA).
- Figures re-derived at head (ev/figures.txt): 7 ACCEPT / 2 DEFER / 2 REJECT. Null control `ruling_verdict(P99)` returns None. P75: 0 files under the old briefs directory, 33 role and dimension .md files, `fbbd3e61` is a commit, and `prepr.sh` step 4 still lists `tools/audit/briefs/*.md` (line 3087). P67: `rides .--red` is at `prepr.sh:777`. P76: `bus.sh` guards the message and first line through `ref_privacy.py guard` (lines 264, 1084-1092).
- Pre-study counts that cite out-of-tree scripts (`verdict_classes.py`, `opener_refusals.sh`, `cards.json`) could not be re-derived from the tree. The file says so itself in its preamble. They are unverified by this seat.
- Mutation proof n/a: no production code line in the diff. VERSION, the manifest and RELEASE_NOTES.md are untouched. Both files are under INERT `dev/programme/` (`tests/closure.py:273`).
- `git merge-tree --write-tree origin/main 2e2b374cd982d0b4d3bc4853a0227239c28e4f76`: rc 0, tree 7775a74c. No conflict.
- CI on this head: all 6 check runs (`prelude`, `refresh`, `cancel-superseded` x2 workflows) were still queued when read. No conclusion yet, so no red-check answer is owed or assessed.
