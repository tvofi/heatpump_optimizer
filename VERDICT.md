Fix review: blocked 094f2c0d2696b4bd04cd485b9e7fc3f144620053 architecture-unsound: main landed #2059's bot-subject carry on this same seam while this branch sat at its base, so this is now a second mechanism for one concern and it conflicts with origin/main on tools/pr/app_approve.sh
bus-nonce: 4e63f91d61505e76b2dbe3a9728e1d11
round: 1
seat: review-2075
Evidence: /Users/timmalmstrom/hpo-seats/review-2075/evidence/

Measured head `094f2c0d2696b4bd04cd485b9e7fc3f144620053`, re-read before this
verdict was written and still the live head of #2075 (`state=OPEN draft=true
mergeState=DIRTY`). Branch base `b2b6acd64cde652676a568e93c05f021571ebe5e`.
`origin/main` moved twice while I measured: `a8ce87571` at the start, then
`d8a4bd36f6384dde45486fff388f91ed4a3aa6df` (the merge of #2059) part way
through. The head never moved; main did, and that is grounds 1 and 3 below.

Four grounds. Ground 2 is a hard rule and is settled by CI; grounds 1 and 3 are
one measurement; ground 4 is a defect in the new lines with a one-token remedy.

## Ground 1 — a conflict on a path that is not a claim file (step 13)

```
$ git merge-tree --write-tree origin/main 094f2c0d2696b4bd04cd485b9e7fc3f144620053
159f08dc29ffbbf5557a32a058e568af8605037c
100755 d818e8e5a... 1  tools/pr/app_approve.sh
100755 a07be5570... 2  tools/pr/app_approve.sh
100755 75986eb14... 3  tools/pr/app_approve.sh
CONFLICT (content): Merge conflict in tools/pr/app_approve.sh
exit=1
```

stderr is empty and there are **0 `MERGE-CLAIM:` markers** in either stream, so
this is not the claim-file driver refusing and not a `DIRTY` I can dismiss as
GitHub's status field: it is a content conflict on `tools/pr/app_approve.sh`,
the file this PR is mostly made of. Step 13 makes a conflict on any path other
than the two claim files mine to block on, because I cannot know the merged
result is correct. Against the earlier `origin/main` (`a8ce87571`) and against
the branch base, the same command exits 0 — the conflict arrived with
`d8a4bd36f`, i.e. with #2059. Evidence: `mergetree2.txt`, `mergetree2.err`,
`conflict.txt`.

## Ground 2 — `fast (3.14)` went red at the head and the body answers nothing (step 11)

All 17 required contexts of ruleset 23698884 (`main-protect-checks`, active)
**RAN** at the head; the head is authored and committed by `tvofi`, not
bot-pushed, so this is settled rather than absent. 15 succeeded. Two are red:

```
fast (3.14)    status=completed  conclusion=failure   id=113892203905
pr-contract    status=completed  conclusion=failure   id=113894588362
```

`## Red checks` says `none` — "at the branch head as of this writing, before CI
first runs at it." CI has now run at it. Neither check is named, so by step 11
this is `root-cause-unanswered` on both, and it is not `UNDER-SCOPED` or
`INHERITED CLAIMS`, the two `ci-autofix.md` answers by naming.

The cause is this PR's own added line, and I measured it at both ends with the
same instrument rather than reading CI's word for it:

```
$ PYTHONPATH=tests:tests/hastub python3 tests/layout.py     # at the head
    new-reference: tools/pr/app_approve.sh cites retired path .claude/workflows/policy_lint.mjs:
      [ -f "$lint" ] || lint="$SELF_DIR/../../.claude/workflows/policy_lint.mjs"
layout: GUARD: 1 refusal(s) against b2b6acd64cde
RESULT layout.py (PYTHONPATH honoured): head rc=1  base rc=0
```

`tests/layout.py`'s guard refuses a NEW citation of a retired path, and
`bot_commit`'s second-choice lookup cites `.claude/workflows/policy_lint.mjs`,
which `tests/layout.json` records as retired in favour of
`tools/policy/policy_lint.mjs`. CI agrees exactly:
`layout self-test: ok`, then `layout: GUARD: 1 refusal(s)`, then
`>>> FAILED: python3 tests/layout.py`. `pr-contract` is red for the same
silence and says so itself:

```
record   red-history   1 commit(s) between origin/main and this head, every
                       failure conclusion across them: fast (3.14)
ERROR [pr-body] check `fast (3.14)` is red and `## Red checks` does not name it.
```

One root cause, two reds. The fallback is also **dead in this tree**:
`.claude/workflows/policy_lint.mjs` does not exist at the head or at the base
(`git ls-tree HEAD .claude/workflows/` holds no `policy_lint.mjs`), and the
first-choice path `tools/policy/policy_lint.mjs` always resolves. Deleting the
line clears the red and removes dead code; nothing else needs to move.
`fast (3.14)` was **success** at `b2b6acd64`, so this is not main's red.
Evidence: `layout-head4.txt`, `layout-base4.txt`, `job-113892203905.log`,
`job-113894588362.log`, `checks.txt`.

## Ground 3 — #2059 landed on this seam, so the premise and the null control are both stale (step 17)

While this branch sat at `b2b6acd64`, main merged **#2059
`fix/r9-ci-2b-carry`** (`d8a4bd36f`), whose commits are
`3adb02cd4 fix(R9-CI-2b): verdicts carry over the bots' own commits; a
merge-main bot un-DIRTYs driver-only conflicts` and
`0ac45f641 fix(R9-CI-2b): #2059 round 1 -- bot merge on main only; bot
subjects need their writer`. It touches the same two files
(`tools/pr/app_approve.sh` +91/-11, `tools/policy/policy_lint.mjs`) and adds
`bot_paths`/`bot_author` plus a `bots` exclusion list in `carry` — the same
concern, a second mechanism.

Main's current copy already carries every head this PR exists to fix. Measured
read-only from `/private/tmp/r9-main`, `main ref = origin/main = d8a4bd36f`:

```
RESULT base-copy-b2b6acd64  #2071 6aaba97f->7843b799  REFUSE
RESULT main-copy-d8a4bd36f  #2071 6aaba97f->7843b799  CARRY
RESULT head-copy-094f2c0d2  #2071 6aaba97f->7843b799  CARRY
RESULT base-copy-b2b6acd64  #2070 3ecb86ad->a9ba0b88  REFUSE
RESULT main-copy-d8a4bd36f  #2070 3ecb86ad->a9ba0b88  CARRY
RESULT base-copy-b2b6acd64  #2066 b511f9dc->d1538a73  REFUSE
RESULT main-copy-d8a4bd36f  #2066 b511f9dc->d1538a73  CARRY
```

So the body's null control ("refuses at main's copy, carries at the fixed copy")
holds only against `b2b6acd64`, which is no longer main. Step 8: the body
quotes `main's copy (unmodified)` as its baseline and that baseline moved under
it. Main's own self-test at `d8a4bd36f` reports `153 checks, 0 failed` here, so
#2059 brought arms of its own for this seam.

**But #2075 is not worthless — main's landed mechanism is looser on exactly the
axis this PR tightened, and that is worth carrying into the re-cut.** Same
fixture, main's current copy:

```
RESULT main-now A2-modifies-reviewed-row   expect=REFUSE got=CARRY
RESULT main-now A3-modifies-main-row       expect=REFUSE got=CARRY
RESULT main-now A9-deletes-reviewed-row    expect=REFUSE got=CARRY
RESULT main-now A7-reaches-prod-code       expect=REFUSE got=REFUSE
RESULT main-now A6-forged-identity         expect=REFUSE got=REFUSE
```

Main's `bot_paths` excludes the whole `tests/mutation_ledger` subtree for any
accepted pin commit and checks only `%ae`, so a bot-identity `ci: pin killed
mutants` commit that **rewrites or deletes a row the branch's own diff already
carried** now carries to approval with no reviewer turn. This PR's copy refuses
all three (below). That is a live hole on main today and this PR's
additions-only narrowing is its fix — so the honest re-cut is a **tightening of
main's `bot_paths`/`bot_author`**, not a parallel `bot_commit` beside it
(`fixer.md` step 17: "the existing mechanism, never a parallel one"). Reading
`autofixCommit` rather than a second hand-written table is the right instinct
and survives the re-cut; the shell-side duplication of the exclusion idea does
not. Evidence: `mainnow.txt`, `mainnow-attacks.txt`, `main-carry-d8a4bd3.txt`,
`main-botpaths.txt`.

## Ground 4 — `metric-gamed: carry:` the new exclusion pathspecs are not literal, so one added file named `*` excludes a whole subtree

`bot_commit` ends with `git diff --no-renames --diff-filter=A --name-only
"$parent" "$sha"`, and `carry` turns each line into `bx[..]=":(exclude)$p"`.
`$p` comes out of **the commit's own diff** — the branch side of the comparison
— and is used as a **pattern**, not a literal. git wildmatches `*` across `/`
in a default pathspec, so one added file whose name contains a metacharacter
widens the exclusion from one file to a subtree, and the branch's-own-diff
comparison then cannot see anything under it. The existing `x` list has no such
exposure because `carry` reads `.gitattributes` at `$main` and never at a head,
exactly as its own comment says; `bx` is the first exclusion list taken from the
side being checked.

Demonstrated with a one-name-difference null control on my own fixture (built
by me, not the fixer's, and using main's **real** `.gitattributes` so the
driver set is production's). Both heads sit on the same merge of main, whose
rewrite of a ledger context line shifts the `-U3` context of a hunk the branch
owns — the #2010 class in miniature. Their trees hold the same row content; the
added file is named differently:

```
RESULT N1-ordinary-pin-over-same-merge main-copy=REFUSE fixed-copy=REFUSE
       (fixed-copy: the branch's own diff differs: 42bd7175..6a1bceb8 against 2bfc4bde..65800af4)
RESULT N2-glob-pin-over-same-merge     main-copy=REFUSE fixed-copy=CARRY
  N1 added tests/mutation_ledger/killed_by/n1.json
  N2 added tests/mutation_ledger/*          <- same content, name differs
  git diff N1 N2 = A tests/mutation_ledger/* , D tests/mutation_ledger/killed_by/n1.json

RESULT literal-pathspec: plain hides 2 -> 0; literal hides 2 -> 1
  changed paths, no exclusion                     : [tests/mutation_ledger/* tests/mutation_ledger/ctx.json]
  with :(exclude)tests/mutation_ledger/*          : []
  with :(exclude,literal)tests/mutation_ledger/*  : [tests/mutation_ledger/ctx.json]
```

So the same head that must refuse for "the branch's own diff differs" carries
once a pin commit adds a file named `*`, and the remedy is one token:
`":(exclude,literal)$p"`, verified working on this git (2.38.1) and leaving the
intended single-file exclusion intact. This is also the answer to the boundary
the body deliberately left out: the body says the context-shift case is filed as
a separate owner question and that "this PR touches neither the docstring nor
that arm" — true as far as it goes, but **one new code path does admit that
class for `tests/mutation_ledger/**`**, and #2010 itself still refuses
(`RESULT fixed-copy-#2010 ... REFUSE`, identical reason to main's copy, at both
main refs). Threat model is the code's own, not mine: the comment above
`bot_commit` says "Anyone who can push can write the subject", so identity and
subject are assumed forgeable and the path set carries the weight — here the
path set does not, because its paths are patterns. Evidence: `globctl.txt`,
`attacks.txt`.

## RESULT lines

```
RESULT self-test head 094f2c0d  157 checks, 0 failed (macOS, bash 3.2.57, node v20.10.0)
RESULT self-test base b2b6acd64 145 checks, 0 failed
RESULT self-test CI Ubuntu head 159 checks, 0 failed (instrument-self-tests id=113892207189)
RESULT self-test CI Ubuntu base 147 checks, 0 failed (instrument-self-tests id=113754752946)
RESULT new-arms delta = 12 on both platforms; the absolute counts are platform-dependent and the body quotes only the macOS pair
RESULT twelve new arms present and consecutive at output lines 128-139, the six pairs claimed
RESULT red-first 157 checks, 6 failed -- test-only hunks spliced onto main's copy, 83 insertions 0 deletions, no production change
RESULT red-first failing arms are exactly the six claimed (positive CARRY arm, its null control, and the identity/subject/message/branch-diff reason greps)
RESULT mutant MA any-autofix-message      1 red arm  (matches the body's no_msg_narrow)
RESULT mutant MB exclusion-covers-mods    2 red arms (matches the body's no_afilter)
RESULT mutant MC skip-autofixCommit       10 red arms, two of them pre-existing ci: arms -- the new predicate is strongly guarded
RESULT mutant ME drop policy_lint root=   5 red arms -- the body's four mutants never touch this half of the diff; it is load-bearing and now proven
RESULT nullctl #2071 6aaba97f->7843b799 base-copy REFUSE / head-copy CARRY at both main refs
RESULT nullctl #2070 3ecb86ad->a9ba0b88 base-copy REFUSE / head-copy CARRY at both main refs
RESULT nullctl #2066 b511f9dc->d1538a73 base-copy REFUSE / head-copy CARRY at both main refs
RESULT nullctl #2065 3c9fe53f->90b9e87f REFUSE at both copies, same reason (merges a456c5ed, not on main)
RESULT figure #2065 range re-derived: 74 commits, 4 first-parent, two human test()/ledger() commits and a merge of a commit not on main -- as the body says
RESULT figure #2010 re-derived with carry's own norm(): 16965 and 16965 lines, diff 4 output lines, 2 payload lines both leading-space context, 0 branch-own +/- lines -- as the body says
RESULT attack A1 adds-fresh-row            main-copy REFUSE / fixed-copy CARRY   (the fix, working)
RESULT attack A2 modifies-reviewed-row     main-copy REFUSE / fixed-copy REFUSE  (the narrowing holds)
RESULT attack A3 modifies-main-row         main-copy REFUSE / fixed-copy REFUSE
RESULT attack A13 adds-one-and-rewrites-one main-copy REFUSE / fixed-copy REFUSE (holds in the composite too)
RESULT attack A6 forged-identity           fixed-copy REFUSE (not authored and committed as github-actions[bot])
RESULT attack A7 reaches-prod-code         fixed-copy REFUSE (changes custom_components/..., outside what "ci: pin killed mutants" stages)
RESULT attack A9 deletes-reviewed-row      fixed-copy REFUSE (does not only modify its files)
RESULT attack A11 two-chained-pins         fixed-copy CARRY
RESULT attack A8 other-autofix-message     main-copy CARRY / fixed-copy CARRY -- see the note below, this does not test the narrowing
RESULT attack A4 adds-row-bogus-killed_by  fixed-copy CARRY  (carried finding, not a block; see below)
RESULT attack A12 adds-nonrow-content      fixed-copy CARRY  (same)
RESULT attack A5/A5c glob-named added file fixed-copy CARRY where it must REFUSE -- ground 4
RESULT main-now A2/A3/A9 CARRY -- main's landed #2059 mechanism is looser than this PR on the reviewed-row axis
RESULT required-contexts 17 of 17 RAN at the head; 15 success; fast (3.14) failure; pr-contract failure
RESULT merge-tree origin/main(d8a4bd36f) head -> exit 1, CONFLICT (content) tools/pr/app_approve.sh, 0 MERGE-CLAIM markers
RESULT merge-tree origin/main(a8ce87571) head -> exit 0; merge-tree base head -> exit 0
RESULT claim files IDENTICAL to the branch base b2b6acd64 (both); they differ from current origin/main only by main's own 13-line movement
RESULT VERSION untouched; manifest.json untouched; RELEASE_NOTES.md untouched; files changed = 2
RESULT structure.py head rc=0 base rc=0, outputs byte-identical -- no metric moved
RESULT policy_lint --budgets head rc=0 base rc=0, outputs byte-identical -- no cap moved, so no raise is the owner's here
RESULT policy_lint plain head rc=0 base rc=0: TOTAL 0 errors across 40 policy files, FIXTURE ok 92 errors / 243 pins / 12 classes, KNOWN-BAD 7 of 7 in 15 -- identical at both ends
RESULT archscore --diff b2b6acd64: dS +0.0000 NULL -- not regressed
RESULT bot_commit cost: one node import of policy_lint.mjs 0.42-0.47s; a full --carry 1.20s at the head vs 0.19s at the base -- no merge-queue hazard
RESULT delivery row docs/delivery/2075.md absent from the diff, correctly: delivery-status-tracking.md makes the row the orchestrator's, "a fixer writes none"
```

## What I confirmed of the body's claims, and what I could not

**Confirmed by my own commands:** the 157/0 vs 145/0 pair and the twelve new
arms; the red-first at exactly 6 failed with the test-only splice (83
insertions, 0 deletions — no production change, so the arms are not vacuous);
both quoted figures re-derived to the digit (#2065's 74 commits and #2010's
16965/16965 with 2 pure-context payload lines); `structure.py` PASSED with no
metric moved; `VERSION`/manifest/notes untouched; the claim files byte-identical
to the branch base; `autofixCommit`'s only pre-existing call site
(`autofixChain`, line 5981) still passes one argument, so the new `root`
parameter defaults and every existing caller is unchanged, and the plain and
`--budgets` runs are byte-identical at both ends.

**Not confirmed, and I say so rather than reporting it as verified:**

- The body's `157 checks` is the **macOS** count. CI's `instrument-self-tests`,
  which is the required context, prints **159** at this head and **147** at the
  base. The delta is 12 on both platforms, so "12 new arms" is sound; the
  absolute number the body offers as re-runnable is not the number the lane
  prints, and the body does not say it is platform-dependent.
- The body says the #2010 context-shift question "is filed as a separate owner
  question". It names no issue number and no destination, and `##
  Forward-carry` says `none`, so there is nothing I can open. Step 8: not
  verified. Since ground 4 shows a new path here *does* admit that class for one
  subtree, this needs a real destination before the re-cut merges.
- I did not re-run the mutation table or the gate: step 11 cites CI's heavy
  runs, and `mutation` is green at the head. Per step 11 a green `mutation` does
  not establish a green baseline, but the body's mutation proof is the script's
  own `--self-test` mutants, which I re-planted myself (MA/MB/MC/ME above), so
  nothing here turns on that lane's log. `tests/arch_score.py` and
  `tests/structure.py` were both scoped out of CI's gate at this head; I ran
  `structure.py` at both ends anyway (identical) and `score.py --diff` (NULL).
- The fixer's disclosed ~2-minute wait on `tests/gate_lock.py`'s lease: I never
  held the lease by hand and cannot corroborate the wait from here. What I can
  say is that `tests/entities.py` — the one script CI's scoped gate ran — is
  green in CI's own `fast (3.14)` log at 84s, so the lease wait cost nothing
  that landed red.
- The body's third friction item (the positional `sed -n '1,340p'` window) is
  real and I verified the new bound is sound rather than merely larger: at the
  head the three pinned strings sit at lines 370, 387 and 398, the `--self-test`
  guard at 488 and `SELF=` at 497, so `1,472p` still stops before the self-test
  section and no pin can be satisfied by a copy of itself in the fixtures. At
  the base they sit at 279, 296 and 307 under `1,340p`. Not a metric moved: the
  window is a bound the diff had to pay for, and the self-test count is the only
  figure it moves.

**One arm that tests less than it looks like.** `A8`/`H_OTHERBOT` — "the bot's
identity and a real autofix shape, but not the ledger's pin message" — refuses
in the self-test only because that fixture's `.gitattributes` names a single
driver (`led.json`). Against main's **real** `.gitattributes`, `tests/closures.json`
and both claim files are merge-driver files, so a `ci: re-record closures`
commit passes `carry`'s pre-existing `git diff --quiet` check and never reaches
`bot_commit` at all: `RESULT attack A8 main-copy CARRY / fixed-copy CARRY`. That
is what the body itself says ("the other two autofix jobs stage merge-driver
files already, so their commits pass `carry`'s existing `git diff` check and
never reach here"), and my mutant `MA` shows the narrowing is load-bearing given
the fixture. So the arm is a legitimate isolation of the gate, not a false
claim — but the message narrowing is defence in depth that production does not
currently reach, and a later seat should not read it as the thing standing
between `carry` and the other two autofix jobs.

**A carried finding, deliberately not a block.** A bot-identity `ci: pin killed
mutants` commit may add a file under `tests/mutation_ledger/` with arbitrary
content and `carry` accepts it: `A4` adds a row whose `killed_by` names
`tests/THIS_SCRIPT_DOES_NOT_EXIST.py`, `A12` adds a non-JSON `exec.sh`. I did
not block on this because it is not new semantics this PR invented: it is
`autofixCommit`'s documented rule, which `checkPrBody` already trusts on the
head a body names, and `policy_lint.mjs` states the residual risk and its
reason in terms ("A forged pin commit is not re-checked: it can add a
`killed_by` entry no run measured... every other required context still runs at
the real head"). I read the downstream bound rather than assuming it:
`completeness_problems` refuses a disposition whose `(anchor, old)` names no
site the deterministic inventory generates, so a wholly invented row reddens
`mutation` at the head; a row naming a REAL site with a bogus script does not —
`pinned_script` only reorders drivers that exist, and `pin_reverification` is
report-only on the nightly. So the surviving exposure is "a well-formed pin for
a real site, unreviewed". That is worth a destination in the re-cut's body, not
a fourth ground here, and ground 3's measurement says the same exposure is
already live on main through #2059 with a wider path set.

## What the re-cut owes

1. Rebase onto `d8a4bd36f` and resolve `tools/pr/app_approve.sh` by
   **tightening main's `bot_paths`/`bot_author` mechanism**, not by landing a
   second `bot_commit` beside it. The measured value to carry over is
   additions-only: main's copy currently CARRIES a bot pin commit that rewrites
   or deletes an already-reviewed row (`A2`, `A3`, `A9` above), and this PR's
   copy refuses all three.
2. Delete the `.claude/workflows/policy_lint.mjs` fallback line. It is dead and
   it is the whole of the `fast (3.14)` red.
3. `":(exclude,literal)$p"` in the new exclusion list, with an arm that plants a
   metacharacter in an added path — the arm my `N1`/`N2` pair above is, already
   written and reproducible from `scripts/globctl.sh`.
4. Name `fast (3.14)` and `pr-contract` in `## Red checks` with their answer,
   and give the #2010 context-shift question a real destination, since a path in
   this diff admits that class for one subtree.
5. Re-take every figure in the body at the new head — including the self-test
   counts, which are platform-dependent and should be quoted as CI's (147 -> 159)
   rather than this seat's (145 -> 157). Steps 2-8 of `fixer.md` re-execute
   after a rebase; ground 3 is exactly the case that rule exists for.

Nothing here is a defect I could fix inside this review: grounds 1, 3 and 5 need
the fixer's branch to move, and ground 2 needs the body to answer its own red.
