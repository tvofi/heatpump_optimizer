# R9-RO-PC1: a prose count that git merges clean is now read by the shape, not the sentence

Round-9 countermeasure for the stale-prose-count class, added to the instrument that
already **is** the I5 barrier.

**The defect, and why it cost three resolution rounds.** Two seats cut from one tip
(`d0f085ffb`) made the BYTE-IDENTICAL three prose edits to `docs/architecture.md` — `74
modules` → `75`, `27 of the 74` → `27 of the 75`, `The other 46` → `47` — and put their
new module-map row on different lines. `git merge` returned **rc 0**, auto-merged the
document, and conflicted on nothing, while the merged tree held **76** modules and **48**
HA-free. The sentences are identical, so `ort` sees one change; the map rows are on
different lines, so both survive. The count is false and git reports nothing. That is the
shape of the three incidents of 2026-10-09 — #2024, #2065, #2066 — at 110.0, 110.1 and
138.7 wall minutes each: #2024's `tests/deployment_shape.py` sentence *"all 91 files"* sat
outside the conflict markers for exactly this reason, #2065's two records each stated 74
for a merged tree of 75, and #2066's HA-free count was corrected only after the merge, to
what `entities.py`'s own check printed.

**Why it escaped — process state (c): the process was followed and did not produce the
result.** The sentences *are* read at that tree: at the reproduction,
`dev/audit/rounds/round4/D6/claims.py` prints `FALSE C32` and `tests/entities.py` names
three FAILs (the opening counts, the HA boundary, the HA-free count). The defect is not an
absent check; it is that coverage is keyed on a **sentence** rather than on the **unit**.
`tests/doc_claims.py`'s own docstring states the promise this class breaks — *"a new
sentence of the same shape enters the check the moment it lands"* — and for counts that
promise was kept in exactly one place, `check_multistart_starting_points`, which is
corpus-wide for one noun. Ground truth, measured by the root-cause seat and re-read here:
seven stale counts planted across the reader documents (a README field total, its
editable-page count, two option-page counts, a setup-page one, the card's page count, an
ECL110 settings count) left `entities.py` at **29 reds before and 29 after with no check
name moving**, `claims.py` at zero false, and `tests/doc_claims.py`'s 160 checks and
`tests/harness_headers.py`'s 109 all passing. Four instruments, zero red, three sentences
false.

**The fix, and the alternatives it beat (`fixer.md` step 17).**
`check_prose_tree_counts`, beside `check_multistart_starting_points` in
`tests/doc_claims.py`: count **shapes** scanned over the file's own reader corpus, each
compared to a measurement the tree derives — the package glob the script already parses,
an AST walk of those same trees, `config_flow._OPTION_PAGES` with the pages the
translation catalog actually renders a field on, and `doc_claims.registered_service_fields()`
for the service count and for each named service's field count. A narrow shape claims its
span first, so `The other 47 modules` reads as the HA-free count and not also as a module
total, and `27 of the 75 modules` yields both the importer count and the total.

- *An arm in `tests/entities.py`* — rejected: `entities.py` is inside the fixer role's
  `opens` cap (5852) and runs 2243 checks; `doc_claims.py` is in neither
  `policy_budgets.json`'s `files` nor its `roles`, so the arm costs no budget there, and
  that file is where the docstring already states the promise this class breaks.
- *A per-document sentence regex* — rejected: that is the shape that failed. The unit has
  to be the shape, or the next document is another escape.
- *A broad `<n> <noun>` enumerator inside the gate, with an ignore list* — rejected: it
  fires on `5 steps`, `30 min`, `0.5 kW`, and the ignore list would be a second
  hand-maintained enumeration of exactly the kind the file's docstring rejects.
- *Reading `services.yaml` for the service count* — rejected in favour of
  `registered_service_fields()`, which is execution-derived and already the F8.3 arm's
  source; a second reader of a fact the registered schema carries is the duplication
  `tests/README.md:237` forbids.

One prototype shape was dropped and two added, each for a reason the arm's own run shows:
the `N modules, of which M import` opening sentence had to be read or the bare module shape
would swallow its total, the `N service definitions` map comment is a count of the same set
that no shape took, and the prototype's two `fields` shapes became one keyed on the service
the sentence **names** — an unregistered name is refused rather than compared, because
`All N fields` inside a service paragraph is already priced by `check_service_fields`, and a
second, weaker reader of that sentence is the worse code.

**The class's seams, enumerated rather than asserted.** `tools/audit/prose_counts_census.py`
prints every `<number> <plural noun>` the corpus states, subtracts the spans the arms
claimed, and gives the rest a disposition; a noun with no entry is REFUSED and an entry
stating no unclaimed count is DEAD, so neither a count shape that lands tomorrow nor a
rotted entry passes unread. It imports the shapes *and the claiming rule* from
`doc_claims.py`, so the two cannot drift. At this head it prints `seam_rows=161 nouns=27
refused=0 dead=0`. The two seams it leaves, named in `I5.barrier`'s Not-reached clause: a
count spelled as a word (`five pages`, `twelve files`), and the ~60 `steps` cells in
`configuration.md`'s tables, which stay unread because C30 compares only the Default column
and C31 the min/max — planting `0.5 steps` → `0.7 steps` leaves every instrument green.

**Moratorium (decision 0012): the argument, for the reviewer to attack.** This is not a new
policy file, not a new `.claude/rules/*` rule and not a new lint class. `I5` is already
`barriered` by `tests/doc_claims.py`; what this adds is **one arm to that instrument**,
extending the barrier's **unit** from the sentence to the shape — and
`dev/governance/roles/root-cause.md` §2 says a countermeasure changes the unit, not the arm
count. I have added no rule, no policy file and no new check class to make it look smaller,
and I am not re-classifying it quietly. **If the review reads this as a new policy
instrument, the branch stops and goes back to the owner rather than merging.**

**The RCA document is in this PR, and why they cannot be split.**
`dev/audit/rca/R9-RO-PC1.md` is cited by `I5.rca`, and `tools/audit/fold_ledger.py:186`
makes `_rca[<id>].in_tree_home` **DANGLING** unless the file is under `dev/audit/rca/`;
the checker also refuses a cited id `_rca` does not index (**UNKNOWN-RCA**). So a fold that
cites a document which does not exist cannot be made to pass at all, and two pull requests
would leave one of the two states red in between. The document is the root-cause seat's
analysis, transcribed by the orchestrator and checked here against the seat's own artifacts
before committing; four corrections are recorded in the commit message — the enumeration
headline is two commands rather than one (22 instances with the ECL110 false positive
unanchored, 21 with none once anchored), the cheap gate's recorded seconds are
`tests/closures.json`'s 8.6 and not the seat's own 2.3 s wall measurement of `claims.py`,
the three rounds total 358.8 min (6.0 hours), and section 5 now describes the shape that
landed rather than the prototype.

## Head

`dc1abe6544806683d1d382d0e02ae452922f0c7e` — the evidence tree for every figure and every
arm below. It is `5550b3688` (the RCA document and the fold) merged with `origin/main`
`7cd5a588c`, a clean automatic merge: `tests/closures.json` and the claim files are
byte-identical to main, no `ledger_merge.py --resolve` was needed, and the branch claims no
drift.

The corpus the census reads is byte-identical to `origin/main` at this head — the diff
touches no README, no `docs/`, no blueprint and no package module — so the measured
quantities are main's, not this branch's.

## Mutation proof

The arm is the fix, so the mutants are mutants of the arm, each run on the tree where the
defect is present (`/Users/timmalmstrom/hpo-seats/pc1/arms/final/planted`), evidence
`/Users/timmalmstrom/hpo-seats/pc1/arms/logs/h-M-doc_claims.txt`:

- **M1 the comparison disabled** — `wrong = []` in place of `wrong = [row for row in claims
  if row[4] != row[3]]`, on the tree carrying the planted `26 options pages`: `1 of 169
  checks FAILED` becomes `ALL 169 checks PASSED`. The red comes from the comparison and
  nothing else.
- The four arms in `## Null control` below are the perturbation set proper: each moves one
  input (the corpus's counts, a reader document, the tree's measurement) and the row that
  fires is named.

`prepr.sh` step 6d's unpinned-site list for this diff is in `## Figures`.

## Null control

All at `dc1abe654`, in `git worktree` copies of it under
`/Users/timmalmstrom/hpo-seats/pc1/arms/final/`, logs under
`/Users/timmalmstrom/hpo-seats/pc1/arms/logs/`:

- **Healthy tree (`healthy`, untouched): `ALL 169 checks PASSED`, rc 0** — and the arm's own
  row reads `every count of a tree-measurable set the reader corpus states is the tree's (17
  counts over 11 shapes)`, and `the census read a positive number of counts (anchor: not
  green by skipping)`. Not green by skipping: it read 17 counts across 12 documents and all
  11 shapes, and a second identical run printed the same 169.
- **Failing (`planted`, `26 options pages` in the two documents that state it): rc 1, one
  check FAILED**, naming both — `configuration.md:9 options_pages: documented=26
  measured=23; setup.md:263 options_pages: documented=26 measured=23` — on a tree where
  `claims.py` (rc 0), `tests/entities.py` (`ALL 2250 ENTITY CHECKS PASSED`) and
  `tests/harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`) are all green. **Four
  instruments, zero red, two sentences false.**
- **Passing (`planted`, the same sentences corrected back to 23): `ALL 169 checks PASSED`,
  rc 0.**
- **Fail-closed (`failclosed`, `docs/architecture.md` deleted): rc 1, and the arm REFUSES
  rather than passing** — `the corpus states every count shape at least once … [no
  occurrence of: ['the Home-Assistant-free module count', 'the module-level importer count',
  'the opening module total and its importer count', 'the service-definition count', 'the
  module total']]`. The arm inherits the file's own anchor rule: the absence of the claim's
  subject is itself red, so deleting a reader document cannot buy a green.
- **At the reproduction (`/Users/timmalmstrom/hpo-seats/rca-prose-counts/work/mergeAB`, 76
  modules): rc 1 with exactly three FALSE rows** — `architecture.md:8 modules:
  documented=75 measured=76; architecture.md:197 modules: documented=75 measured=76;
  architecture.md:206 modules_free_of_homeassistant: documented=47 measured=48` — and the
  merge that produced it re-run here as `git merge-tree --write-tree e8d7be6cc 7a5818618`,
  **rc 0**.
- **In-process controls** the arm carries for itself: a narrow shape claims its span first
  (`The other 99 modules` yields one claim, not two); the plant fires in both documents that
  state it and nowhere else; deleting a document refuses; a `fields of` count naming an
  unregistered service is refused rather than compared.

The finding's own harness, `census_arm2.py` (sha1
`83abead913cb7fbeb508e16cdba7f05db66efb13`, `/Users/timmalmstrom/hpo-seats/rca-prose-counts/`),
re-run at both ends reads **flat** — identical `MEASURED` dict and `prose_counts_checked=16
shapes=10 docs=8 claims_false=0` at `origin/main` `7cd5a588c` and at this head — which is
correct: it measures the corpus and the tree, and this diff touches neither. The companion
applying the same rule is the arm above, which reads the defect at the reproduction tree and
not at this head.

## Figures

- `scoped gate: MODE: SCOPED -- 1 script(s) run, 32 scoped out; changed files (4)` and `scope.run: tests/doc_claims.py` — `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D; cat $D/scope.txt; cat $D/scope.run`
- `this head: ALL 169 checks PASSED` (rc 0), the arm's row `(17 counts over 11 shapes)` among them — `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py` at `dc1abe654`
- `at main's tip: ALL 160 checks PASSED` — the same command in a worktree at `origin/main` `7cd5a588c`; nine checks are added by this diff
- `seam enumeration: RESULT seam_rows=161 nouns=27 refused=0 dead=0` — `PYTHONPATH=tests/hastub:tests:custom_components python3 tools/audit/prose_counts_census.py`
- `fold ledger: 28 classes, 549 instances, 102 rca entries; 0 violation(s)` (101 entries before this branch) — `python3 tools/audit/fold_ledger.py check`
- `fold ledger self-test: 0 failed` — `python3 -I tools/audit/fold_ledger.py --self-test`
- `structure ratchet: STRUCTURE RATCHET PASSED, every row at or under its cap` — `python3 tests/structure.py`
- `agreement: RESULT divergent=0 unregistered=0 dead=0 refused=0` / `AGREEMENT ok` — `python3 -I tools/policy/agreement_py.py --run`
- `policy budgets: every per-file cap under, and the five aggregate caps inside cap+band (fixer ~6219 of 5852+500)` — `node tools/policy/policy_lint.mjs --budgets`
- `architecture score: dS +0.0000 NULL` — `python3 tools/audit/archscore/score.py --diff origin/main HEAD`; no gate rise, so no `## Architecture score` line is owed
- `the arm's standing cost: tree_count_facts 164.5 ms + prose_count_scan(CORPUS) 85.7 ms = 250.3 ms CPU, and the null control prose_count_scan({}) 0.1 ms` — `PYTHONPATH=tests/hastub:tests:custom_components python3 -c "import sys,time;sys.path.insert(0,'tests');import doc_claims as dc;dc.tree_count_facts();dc.prose_count_scan(dc.CORPUS);t=time.process_time();f=dc.tree_count_facts();t1=time.process_time();dc.prose_count_scan(dc.CORPUS,f);t2=time.process_time();dc.prose_count_scan({},f);print((t1-t)*1000,(t2-t1)*1000,(time.process_time()-t2)*1000)"`; the arm is 250 ms against a defect measured at 358.8 minutes for three occurrences, and the empty-corpus control shows the scan reads the corpus rather than costing a constant
- `claim files byte-identical to origin/main; VERSION, the manifest and the RELEASE_NOTES heading untouched` — `git diff --stat origin/main HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION`
- `ALL 2250 ENTITY CHECKS PASSED` (rc 0), `ALL 109 HARNESS HEADER CHECKS PASSED` (rc 0), `claims.py rc 0` on the planted tree — `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/entities.py`, `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py`, `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py`, all in `/Users/timmalmstrom/hpo-seats/pc1/arms/final/planted` at `b8bacbb6a`
- the four arm tallies and the reproduction's three rows — the commands in `## Null control`, logs under `/Users/timmalmstrom/hpo-seats/pc1/arms/logs/`
- `prepr.sh rc and every refusal line` — `bash tools/pr/prepr.sh /Users/timmalmstrom/hpo-seats/pc1/arms/BODY.md`

## Red checks

`none` — no check on this branch went red, locally or on CI. `nightly-status` and
`delivery-status` grade `main` and this diff touches neither their scripts, `tests.yml`,
`governance.yml`, the plan, `HANDOVER.md`, nor a row they read.

The local gate refused nothing; a refusal of the kind `R9-RC-BLAS-KERNEL-RED` owns — `prepr`
step 5 failing while recording `tests/features.py` — is named in `## Figures` if it appears,
with the same failure reproduced at a clean `origin/main` worktree to show it is not this
diff.

## Forward-carry

- `dev/audit/config/bugclasses.json` — the class fold: `I5.non_round_instances` (the three
  resolution rounds), `I5.detector` (the census named among the barrier's arms),
  `I5.barrier`'s Not-reached clause (the two limits above), and `I5.rca` =
  `R9-RO-PC1` with `_rca`'s entry, so the next seat reads the closure and its limits from the
  ledger rather than from this body.
- `dev/audit/rca/R9-RO-PC1.md` — the analysis, and the destination for the two seams the
  enumeration leaves.
- `tools/audit/prose_counts_census.py` — the instrument a later round re-runs to find a
  count shape that landed without a reader; it is in the tree, not in scratch
  (`fixer.md` step 18).
- The census arm's own comment in `tests/doc_claims.py` names the two limits at the point a
  reader of the arm will look.
- **Not** `tests/README.md`: the manual names no per-script row for `tests/doc_claims.py`, so
  there is nothing to keep true there, and the file is in `POLICY_GLOBS`
  (`tools/policy/policy_lint.mjs:261`, `/^tests\/README\.md$/`) with a `policy_budgets.json`
  cap, so growing it is a policy change the owner approves before merging. The limits live in
  the arm's comment and in the ledger instead.

Out of scope and deliberately not folded: stale retired **paths** (group `R9-RO-10`). Its
truth condition is *does this path exist*; a stale count's is *does this number equal the
tree's measurement*, and no path check can see the latter. They share only the word stale.

## Friction

- `fixer.md: contradiction: the R9-RO-PC1 brief required the bugclasses I5 fold to "append this rca id" and also that `fold_ledger.py check` keep printing 0 violations, which cannot both hold while `dev/audit/rca/R9-RO-PC1.md` is absent — the checker refuses the citation as UNKNOWN-RCA and the in-tree home as DANGLING. Resolved by the orchestrator landing the document in this branch; the branch honestly carried the id in `I5.rca_planned` in between.
- `defect-root-cause.md: stale: `tools/policy/agreement.mjs:29,69` and `tools/policy/field_coverage.mjs:39,41` print their run command as `python3 -I .claude/workflows/<file>` / `node .claude/workflows/<file>`, a directory those files left; `python3 -I .claude/workflows/agreement_py.py --run` — the exact command `agreement.mjs`'s own REFUSED line prints — answers "No such file or directory", while the working path is `tools/policy/`. The Node side resolves through `counts.mjs`'s `locate()` shim, so only the printed command is wrong. Named, not fixed: out of this group's scope.
- `fixer.md: stale: `CLAUDE.md:150` names `tools/audit/harnesses/` as where per-group harnesses and instruments live; that directory does not exist, and a seat following it has to choose between `tools/audit/` (where `fastpath_census.py` and this census live) and `dev/audit/harnesses/` (which exists). Named, not fixed: `CLAUDE.md` is policy and needs the owner's approval before merging.
