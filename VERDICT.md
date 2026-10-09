Fix review: blocked cfa0f3d00a6fa8bd3604f02a066088fc3f07aba2 head-moved: measured cfa0f3d00a6fa8bd3604f02a066088fc3f07aba2, the pull request carries 094f2c0d2696b4bd04cd485b9e7fc3f144620053 -- the re-cut is pushed to origin/handoff/rc-carry-pins only, 0 of the 17 required contexts have ever run at the head I measured, and the body is still round 1's, describing a different fix
bus-nonce: 517d6f09b163209ad111de22532bbd42
round: 2
seat: review-2075
Evidence: /Users/timmalmstrom/hpo-seats/review-2075/evidence2/

**The code is sound. All four of round 1's grounds are fixed on the branch, and
I say so with my own arms below.** What blocks is that the re-cut is not yet a
reviewable pull request: the branch the PR carries is still round 1's head, no
check has ever run at the head I measured, and the body describes a fix that is
no longer in the diff. Nothing here needs a new design. It needs the push to
land, the body re-taken whole against `cfa0f3d00`, and two one-line repairs in
the new lines.

This is **round 2**. Per `fixer.md`, round 4 owes a re-cut rather than a repair;
this round does not.

`head-moved` is the taught class whose grammar fits and it routes to a repair
round, which is what is owed. I do **not** use `root-cause-unanswered`, though
ground C below is literally its step-11 trigger: `web-fix-wave.js:494` returns
that class to a root-cause seat **without** dispatching a repair, and the debt
here is a body and a push, not a cause. And I am not alleging a freeze
violation — the dispatch anticipated this push as the orchestrator's ("if my
push has not landed yet, wait"), so the head never arrived rather than moving
under me.

## What I measured, and against what

Head measured `cfa0f3d00a6fa8bd3604f02a066088fc3f07aba2`, from a fresh detached
worktree (`wt2`), re-read before this verdict was written. Merge base with main
`d8a4bd36f6384dde45486fff388f91ed4a3aa6df`. **`origin/main` moved three times
while I measured** — `d0f085ffb`, then `a9baf164c`, then
`9224833839c4db5221471a04b6558b65102542f2` — so every main comparison below is
pinned to a SHA, and I re-ran `merge-tree` against the newest. Main's
`tools/pr/app_approve.sh` blob is `a07be55707b25185f65d2d89aac120ad498c5e5f` at
all three, so main's copy never moved under these measurements.

The re-cut's chain from round 1's head: `b95753f07` (call the canonical
policy_lint path) → `1c458409b` (merge `origin/main` `d8a4bd36f`) → `5238604de`
(the carry file) → `cfa0f3d00` (drop the closures.json fixture scaffolding).

The diff is **2 files, +127/-4**: `tools/pr/app_approve.sh` +100/-4 and a new
`dev/programme/carries/carry-2075.json` +31.

**The shape changed, and the dispatch's description of it is now stale.**
`tools/policy/policy_lint.mjs` is **byte-identical at the head and on main**
(`e5824f8dac92121f43b23736fe2d68c35b040231` at both). The re-cut dropped the
`autofixCommit` `root` parameter entirely, so **mutant `ME` is moot** — there is
no second half of the diff to mutate. The whole fix now lives in `carry()`.

## Ground 1 — re-based onto main, and a tightening of main's mechanism, not a parallel one

`git diff origin/main...HEAD -- tools/pr/app_approve.sh` is in
`diff-app_approve.txt`. There is **no `bot_commit()` function** and no second
bot-commit path. What the diff does to main's landed `carry()` is replace one
accumulation line inside main's own `else` branch:

```
-        bots="$bots$b"$'\n'
+        ba=$(git diff --no-renames --diff-filter=A --name-only "$c^" "$c")
+        bt=$(git diff --no-renames --name-only "$c^" "$c")
+        while IFS= read -r e; do ... done <<<"$b"
```

It reads main's own `bot_paths` and main's own `bots` accumulator, and narrows
what each entry may hide: an entry that **is** a file this commit changed is
excluded whole as before; an entry that is a **directory** excludes only the
rows this very commit ADDED under it. That is additions-only narrowing of the
mechanism #2059 landed, which is what `fixer.md` step 17's "the existing
mechanism, never a parallel one" asks for. **One owner per concern holds**:
`bot_paths`/`bot_author` remain the single table of which subject writes which
paths as which identity, and the new code consults it rather than restating it.

**The round-1 conflict is gone.** Pinned to the newest main:

```
$ git merge-tree --write-tree 9224833839c4db5221471a04b6558b65102542f2 cfa0f3d00a6fa8bd3604f02a066088fc3f07aba2
exit=0   tree=9b88069cc537e8d269adefdcdef5bedf8ec9ece0   stderr bytes=0
MERGE-CLAIM markers: 0
```

I read the driver's verdict from stderr rather than inferring it from paths
(step 13): stderr is empty and there are no markers, so nothing refused and
nothing conflicted. For contrast, round 1's head against the same main still
exits 1 with `CONFLICT (content): Merge conflict in tools/pr/app_approve.sh`
(`mergetree-r1head.out`). Evidence: `mergetree-final.out`, `mergetree-final.err`.

## Ground 2 — the pathspec hole is closed, and an arm now plants exactly that filename

`:(exclude,literal)$p` landed, in place of `:(exclude)$p`, with the reason in a
comment beside it. I re-ran **my own** round-1 `N1`/`N2` pair — the fixture built
by me, not the fixer's, using main's real `.gitattributes` (identical at
`b2b6acd64` and `d0f085ffb`, verified) so the driver set is production's:

```
RESULT N1-ordinary-pin-over-same-merge main-copy=CARRY fixed-copy=REFUSE
RESULT N2-glob-pin-over-same-merge     main-copy=CARRY fixed-copy=REFUSE
  N1 added tests/mutation_ledger/killed_by/n1.json
  N2 added tests/mutation_ledger/*        <- same content, name differs
  git diff N1 N2 = A tests/mutation_ledger/* , D tests/mutation_ledger/killed_by/n1.json
```

**The file named `*` no longer carries.** At round 1 this pair was
`N1 fixed-copy=REFUSE / N2 fixed-copy=CARRY` — the metacharacter alone flipped
the verdict. Now both arms refuse identically, on `the branch's own diff
differs`, so the perturbation no longer moves the outcome. That is the null
control passing.

My independent `A5c` (merge main, then a glob-named pin commit) agrees:
`main-copy=CARRY / fixed-copy=REFUSE`. The remedy probe still separates the two
pathspec forms on this git (2.38.1):

```
plain   :(exclude)tests/mutation_ledger/*          -> visible: []
literal :(exclude,literal)tests/mutation_ledger/*  -> visible: [tests/mutation_ledger/ctx.json]
```

The fixer's own self-test also plants the filename (`H_PINGLOB`, added by this
diff). Evidence: `globctl2.txt`, `attacks2.txt`.

*One correction to round 1's numbers, so the record is not read backwards:*
round 1 reported `N1/N2 main-copy=REFUSE`. That was my error of provenance, not
a change in main — round 1's `MAINCOPY` was `/private/tmp/r9-main`'s working
tree, which at that moment predated #2059, so `bot_paths` was absent and the
generic `ci:` guard refused (its printed reason was `is a ci: commit that
changes files outside main's merge-driver files`). Against **main's actual
current copy** both N1 and N2 carry, which is the coarse-subtree behaviour this
PR narrows. Round 2 pins the copy by blob (`a07be5570`) instead of by directory.

## Ground 3 — the retired path is gone, and the guard prints 0

```
$ PYTHONPATH-free python3 tests/layout.py       # at the head
layout: GUARD: 0 refusal(s) against d8a4bd36f638
layout self-test: ok                            # rc=0

$ git grep -n '\.claude/workflows/policy_lint' tools/pr/app_approve.sh
(no output; rc=1)
```

That is the exact string the dispatch asked for. At round 1's head the same
command printed `GUARD: 1 refusal(s)` naming the fallback, and that one refusal
was why `fast (3.14)` and `pr-contract` were red. `.claude/workflows/policy_lint.mjs`
is absent at the head **and** on `origin/main` (`git ls-tree` count 0), so the
deleted fallback was dead at both ends, as round 1 found.

**For R9-RO-10's record, since you asked me to say what I can see:** the line
you name in `merge_train.py` is **not there at this head** — `git grep
'\.claude/workflows/policy_lint' -- tools/pr/merge_train.py` returns nothing.
The surviving citations of the retired path are `.claude/hooks/stop-selfcheck.sh`
(3, all inside `test -f` guards), `.claude/rules/defect-root-cause.md:145` and
its generated `.cursor` twin (prose), `.github/CODEOWNERS` (2 comments) and
`.github/workflows/governance.yml` (3, all `if test -f A; then node A; else node
B; fi`). None is in `merge_train.py`, and none is a bare unconditional
reference, so I cannot call any of them dead code from here — the guard form
always takes the `tools/policy/` arm, which is live-but-unreachable-first-arm
rather than dead. `layout.py`'s guard refuses only NEW citations, and it prints
0, so none of these is this PR's debt.

**Not a coverage loss, which I checked rather than assumed.** Round 1's head
carried three positional source pins under `sed -n '1,472p'`; the re-cut has
none, at *every* commit of its chain. That is not deleted coverage: **main
itself removed them in #2059** — window pins count 3 at `b2b6acd64`, **0 at
`d0f085ffb`**, 0 at the head. The re-cut rebased and correctly inherits main's
removal. The pinned strings still exist as production code (`pwd -P` 12×,
`the filesystem root -- refused as evidence` 3×, identical counts at main and
head).

## Ground 4 — the destination exists in the tree, but the body does not name it

`dev/programme/carries/carry-2075.json` is real, in the diff, and linted clean:

```
$ node tools/policy/brief_lint.mjs
== dev/programme/carries/carry-2075.json ==
  -- 0 error(s), 0 warning(s)
CARRY: 44 carry file(s)     TOTAL: 0 error(s) across 45 file(s)     rc=0
```

It is also the **correct instrument**, which I verified rather than accepted.
`finding-propagation.md` routes to a carry file only where "the stage has no
live roster group", and `brief_lint.mjs` "refuses a carry at an issue a live
group covers". At this head the only roster file in the tree is
`.claude/workflows/wave-3l-groups.json`, which names neither `R9-RO-13` nor
`2075` — so there is no live group to carry to and the file is right, exactly as
its own `_comment` says ("The roster is not on main, so this file is the in-tree
destination"). I confirmed `brief_lint` really does examine it (line 122 of its
output) rather than passing it by.

I re-read the comment id before trusting it, as instructed:
`gh api repos/tvofi/heatpump_optimizer/issues/comments/6083743563` **returns
it** — id 6083743563, issue #201, author `tvofi`, created 2026-10-09T15:15:00Z,
1929 bytes, first line `## New exceptional mandate: batch merging of policy
changes is allowed (until 2026-10-12)`, and it names R9-RO-13 as the instrument
catch-up. So the id is not fabricated. Note that by `finding-propagation.md`
that comment **cannot itself be the destination** ("A comment is not
propagation"), and neither can #2078; the tree file is what survives, and the
carry's `stage` field points a reader at R9-RO-13.

I re-derived the figure the carry quotes, at the **re-cut's** merge base rather
than round 1's, since it says "At your merge base":

```
mv=af79f2114  mh=b2b6acd64   (origin/main at the time of the run)
wc -l A=16965  B=16965      diff output lines: 4      payload (+/-) lines differing: 0
16269c16269
<      coord._config[_r9egb1_const.CONF_PRICE_TILES_ENABLED] = True
>      with_config(coord, {_r9egb1_const.CONF_PRICE_TILES_ENABLED: True})
```

**"one line of 16,965 differs and it is pure context" reproduces exactly**, both
differing lines leading-space context. Step 8 satisfied. And `#2010` still
refuses at the head:

```
RESULT base-copy-#2010 origin/main REFUSE
RESULT head-copy-#2010 origin/main REFUSE
```

## A — the pull request does not carry the head I measured

15 polls at 300 s over 75 minutes (`poll-head.log`), every one answering:

```
head=094f2c0d2696b4bd04cd485b9e7fc3f144620053  mergeable=CONFLICTING  updatedAt=2026-10-09T16:43:31Z
state=OPEN  draft=true  mergeState=DIRTY
```

`cfa0f3d00` is reachable only from `refs/remotes/origin/handoff/rc-carry-pins`;
`git for-each-ref --contains` names no other ref, and the fixer's local
`fix/rc-carry-pins` (`82e9fb963`) has diverged from it rather than containing
it. Step 7 fails and I measured it rather than assumed it — the amended step 7
allows a valid `--carry`, and this one is not valid:

```
$ bash <head-copy> --carry 094f2c0d2696b4bd04cd485b9e7fc3f144620053 cfa0f3d00a6fa8bd3604f02a066088fc3f07aba2 origin/main
rc=1
CARRY: no ...: cfa0f3d00... is a commit of the branch's own (chore(R9-RC-Carry-Pins): drop the closures.json fixture scaffolding)
```

So the body's head does not carry to the head I measured. This is the ordinary
consequence of a re-cut, not an accusation — but it is why no verdict I write
can act: `app_approve.sh` requires a `merge` verdict's SHA to equal the head
exactly (#1106, and the parser comment at `web-fix-wave.js:207` says the same),
so a `merge cfa0f3d00…` verdict posted against a PR carrying `094f2c0d2…` would
be inert at the gate.

## B — 0 of the 17 required contexts have run at the measured head

```
$ gh api repos/tvofi/heatpump_optimizer/commits/cfa0f3d00a6fa8bd3604f02a066088fc3f07aba2/check-runs
total_count=0
```

Step 11 requires all 17 required contexts of ruleset 23698884 to have RUN at the
live head. None has, at `cfa0f3d00`. And per `claim-files.md` the PR cannot start
them while it is `DIRTY` at its live head: "such a pull request does not go red,
it **cannot run**." Its `mergeable: CONFLICTING` is GitHub's own field, computed
where the `claimnotes` driver cannot run — and here it is honest, because
`094f2c0d2` genuinely content-conflicts with main on `app_approve.sh`
(`mergetree-r1head.out`, exit 1). The re-cut does not. So CI begins only once the
branch moves.

I did not re-run the gate or the mutation table (step 11 cites CI's heavy runs),
and I cannot substitute a local run for the 17 contexts.

## C — the body is round 1's and describes a different fix

`## Red checks` still says `none` "at the branch head as of this writing, before
CI first runs at it." CI has run. At `094f2c0d2` — a first-parent ancestor of
the measured head, so inside the range — 40 check-runs over 38 distinct names,
latest-per-name, are non-green:

```
fast (3.14)    conclusion=failure   id=113892203905
pr-contract    conclusion=failure   id=113894588362
```

Step 11 is explicit that "the head's runs are not the range's" and that silence
is the block; `pr-contract` itself prints `record red-history` across the range,
so it will name `fast (3.14)` again at the re-cut. The **cause** is fixed
(ground 3: `GUARD: 0 refusal(s)`), which is the substantive half — but the body
still answers nothing, and a re-take must name both and answer them.

Every figure in the body is stale against the head I measured. Each line below
is a measurement, not a reading:

| the body says | measured at `cfa0f3d00` |
|---|---|
| `## Head` = `094f2c0d2…`, branched from `b2b6acd64…` | head `cfa0f3d00…`, merge base `d8a4bd36f…` |
| "judged by the same `autofixCommit` in `tools/policy/policy_lint.mjs`" | that file is **byte-identical to main** (`e5824f8da` both); the diff never touches it |
| "2 files changed, 201 insertions(+), 17 deletions(-); `app_approve.sh` +192/-12, `policy_lint.mjs` +26/-5" | **2 files, +127/-4**; `app_approve.sh` +100/-4, `carry-2075.json` +31/-0 — a file the body never mentions |
| "`--self-test` — 157 checks, 0 failed" | **161 checks, 0 failed** (main's copy 153/0) |
| "The 12 new checks are the 6 fixture pairs added under `## Mutation proof`'s four mutant names" | **+8 checks from 4 fixtures**; the four named mutants `no_bx`/`no_botcheck`/`no_msg_narrow`/`no_afilter` do not exist at this head, and two of their anchors (`bot_commit()`, the `root` parameter) are gone from the tree |
| `## Forward-carry` = `none` | the diff **adds** `dev/programme/carries/carry-2075.json`; `finding-propagation.md` requires "its body names the file and the stage that received it, so a reviewer opens the destination rather than taking the claim" |
| friction: "The bound moved `1,340p` -> `1,472p` here … it is not new debt this PR creates, only inherits" | neither bound exists at this head; #2059 removed all three window pins on main, and this diff contains no `sed -n '1,Np'` line at all (0 occurrences in `diff-app_approve.txt`) |
| `## Figures`: `MODE: SCOPED -- 1 script(s) run` naming `tests/entities.py`, and "ALL 2234 ENTITY CHECKS PASSED" | not re-derivable here — the diff now also adds a tracked file, and `entities.py` needs `homeassistant`, which this machine cannot install (my notes: the container lane is CI-only since 2026-10-04). See below for what I could verify instead. |

The body's `## Friction` first item is also stale in a way that matters: it
argues the fix reads `AUTOFIX_BOT_COMMITS`/`autofixCommit` rather than
`DRAIN_ROWS`. The re-cut reads neither — it reads `bot_paths`, main's own table.
The argument is now about code that is not in the diff.

Per my notes on body staleness (17 of 31 blocks in one window were stale body
figures), the remedy is to **re-take the whole body** against `cfa0f3d00`, not
to patch the named subset.

## D — two defects in the new lines, for the same re-take

**D1. An unintended command substitution in a new self-test arm, at line 1024.**

```
st $? 1 "NO CARRY: a path named `*` is not a wildcard, it is one added file"
```

Backticks inside a double-quoted string are command substitution, so bash
expands the glob `*` in the current directory and **tries to execute the
alphabetically-first entry**. Measured from the repo root, on every run:

```
$ bash tools/pr/app_approve.sh --self-test
tools/pr/app_approve.sh: line 1024: AGENTS.md: command not found     <- stderr, 65 bytes, 1 line
app_approve self-test: 161 checks, 0 failed                          <- rc=0
ok   NO CARRY: a path named  is not a wildcard, it is one added file <- the '*' is GONE
```

Three effects. (a) The arm's printed name loses the one character the arm is
about, in the CI log a later seat reads to find it — and the carry file points a
re-measurer at "the glob-named arm". (b) Every self-test run writes a spurious
`command not found` naming an unrelated file into `instrument-self-tests`.
(c) It is an execution primitive gated only by `.` not being on `PATH`: I proved
the attempt in an isolated directory (`/tmp/btick.*/probe`), where bash reported
`aaa_proof.sh: command not found` for an executable I planted as the first glob
entry. Single-quoting the label fixes all three, and I confirmed the quoted form
prints the name intact.

The **assertion itself is unaffected** — bash expands `$?` before the label's
substitution, so `st` still receives the true rc. That is why my `MNL` mutant
still reddens this arm (below) and why the self-test still reports 0 failed. So
this is a defect in an added line, not a weakened gate. No instrument pins these
labels (`git grep` finds the string only in `app_approve.sh` itself).

**D2. The carry file's `control` overstates its own null control, and names a
mutation that does not exist.**

It says: "Against main's coarse whole-subtree exclusion **all four** carry (the
planted regression, **6 failed arms** …)". I planted exactly that reversion
(`MCO`: the whole additions-only block replaced by main's `bots="$bots$b"`) and
read the arms one by one:

```
128:ok   NO CARRY: the bot's confined additions, under a ci: subject no writer uses
129:ok   refused by the generic ci: guard, not the bot one
130:FAIL NO CARRY: the bot's pin commit over a row the branch's own diff already carried
131:FAIL refused by the branch's own comparison, not the confinement check
132:FAIL (same, H_PINDEL)     133:FAIL (same)
135:FAIL NO CARRY: a path named  is not a wildcard, it is one added file
136:FAIL refused by the branch's own comparison, literal pathspec holding
```

**6 failed checks — that number is right and I reproduced it** — but from
**three** of the four fixtures, not four. `H_PIN_BADMSG` stays green under the
reversion because it refuses through the *generic* `ci:` guard, which the
narrowing never touches (and its own second check says so: "refused by the
generic ci: guard, not the bot one"). A re-measurer following the control as
written looks for four moving arms and finds three. `finding-propagation.md`
exists for precisely this: "Carry the control, not only the claim … A
conclusion without its control cannot be checked."

The same field names "the mutation `no_literal`". **No such mutation exists in
the tree** — the only `no_literal` anywhere is an unrelated local variable at
`tests/structure.py:2399`. The description is precise enough to plant, so I
planted it, and **its substance reproduces exactly**:

```
RESULT mutant MNL: 2 red arm(s)
  FAIL NO CARRY: a path named  is not a wildcard, it is one added file
  FAIL refused by the branch's own comparison, literal pathspec holding
```

Exactly the glob arm and nothing else, as claimed. So the control is sound and
its name is unresolvable — a reader who greps for `no_literal` finds a false
friend in `structure.py`. Name the plant instead of a mutation id, or land the
mutation.

## What still holds — re-measured, not inherited

Round 1's live hole on main, which is this PR's reason to exist. My own fixture,
main's real `.gitattributes`, main's copy pinned by blob:

```
RESULT A1-adds-fresh-row            expect=CARRY  main-copy=CARRY  fixed-copy=CARRY
RESULT A2-modifies-reviewed-row     expect=REFUSE main-copy=CARRY  fixed-copy=REFUSE
RESULT A3-modifies-main-row         expect=REFUSE main-copy=CARRY  fixed-copy=REFUSE
RESULT A9-deletes-reviewed-row      expect=REFUSE main-copy=CARRY  fixed-copy=REFUSE
RESULT A6-forged-identity           expect=REFUSE main-copy=REFUSE fixed-copy=REFUSE
RESULT A7-reaches-prod-code         expect=REFUSE main-copy=REFUSE fixed-copy=REFUSE
RESULT A11-two-chained-pins         expect=CARRY  main-copy=CARRY  fixed-copy=CARRY
RESULT A5c-merge-then-glob-pin      expect=MEASURE main-copy=CARRY fixed-copy=REFUSE
RESULT A10-pin-commit-as-merge      expect=MEASURE main-copy=CARRY fixed-copy=REFUSE
RESULT A8-other-autofix-message     expect=REFUSE main-copy=CARRY  fixed-copy=CARRY
RESULT A4-adds-row-bogus-killed_by  expect=MEASURE main-copy=CARRY fixed-copy=CARRY
RESULT A12-adds-nonrow-content      expect=MEASURE main-copy=CARRY fixed-copy=CARRY
```

**Main still carries A2, A3 and A9** — a bot-identity `ci: pin killed mutants`
commit that rewrites or deletes a row the branch's own diff already carried
reaches approval on main today with no reviewer turn. Each refusal at the fixed
copy is on the right reason, `the branch's own diff differs`, not the
confinement check. So the record shows the hole is real on current main and this
PR closes it. Round 1 measured the same three as `main-copy REFUSE` only
because its main copy predated #2059; see ground 2's correction.

`A10` deserves a note since it moves against round 1: the fixture's
`--amend --reset-author` collapses it to a single-parent commit whose diff is
`M tests/mutation_ledger/ctx.json`, so it is the A2 class (a modification of an
existing ledger file), not a merge. Its refusal is correct, not a regression.

`A8` is unchanged from round 1 and still tests less than it looks like: a
`ci: re-record closures` commit touches only merge-driver files, so it passes
`carry`'s pre-existing `git diff --quiet` check and never reaches the narrowed
branch. `A4`/`A12` are the carried findings I deliberately did not block on in
round 1 — a bot pin commit may add arbitrary content under the ledger subtree;
that is `autofixCommit`'s documented rule, not new semantics here, and it is
already live on main through #2059 with a wider path set.

Live pairs and the negative control, three copies of the instrument (base
`d818e8e5a` at `b2b6acd64`, main `a07be5570` at `d0f085ffb`, head `e4d264407` at
`cfa0f3d00`), run read-only from `/private/tmp/r9-main`:

```
RESULT base-copy-#2071 origin/main REFUSE      RESULT main-copy-#2071 origin/main CARRY   RESULT head-copy-#2071 origin/main CARRY
RESULT base-copy-#2070 origin/main REFUSE      RESULT main-copy-#2070 origin/main CARRY   RESULT head-copy-#2070 origin/main CARRY
RESULT base-copy-#2066 origin/main REFUSE      RESULT main-copy-#2066 origin/main CARRY   RESULT head-copy-#2066 origin/main CARRY
RESULT base-copy-#2065 origin/main REFUSE      RESULT main-copy-#2065 origin/main REFUSE  RESULT head-copy-#2065 origin/main REFUSE
```

**All three live pairs CARRY under the fixed code, including #2066
(`b511f9dc5`→`d1538a73b`), and #2065's range still REFUSEs at all three copies.**
One correction to the dispatch's expectation, measured rather than assumed: the
pairs do **not** refuse "under main's copy" — main's current copy **carries** all
three, because #2059 landed `bot_paths` there. The REFUSE baseline is the
**pre-#2059 base copy**. Round 1 established exactly this (its
`base-copy REFUSE / main-copy CARRY / head-copy CARRY`), and round 2 reproduces
it with the copies pinned by blob. Raw output with each run's reason line is in
`nullctl3.txt`; the same pairs against `d8a4bd36f` as the main ref are in
`nullctl2.txt`.

#2065's range re-derived at the new main: 74 commits, 4 first-parent, refusing
on `merges a456c5ed…, which is not on origin/main` — its own unrelated reason,
identical at all three copies.

## Mutation proof, re-run against the new production lines

Round 1's `MA`/`MB`/`MC`/`ME` anchored on `bot_commit()` and the `root`
parameter; neither exists at this head, so I wrote four new mutants for the two
production changes that do. Each is a one-file, production-only plant, verified
by diff before running, restored between plants, worktree clean after
(`mutants2.sh`, `mutant-*.txt`):

```
RESULT mutant MNL: 2 red arm(s)   drop `literal` from :(exclude,literal)$p     -- exactly the glob arm pair, nothing else
RESULT mutant MAF: 6 red arm(s)   drop --diff-filter=A from the ba= read       -- PINMOD x2, PINDEL x2, PINGLOB x2
RESULT mutant MCO: 6 red arm(s)   revert the block to main's bots="$bots$b"    -- the coarse regression, matches the carry's "6"
RESULT mutant MEX: 1 red arm(s)   force the exact-file branch false            -- "CARRY: remerge_main.sh's inherited-claims commit, only dropping a claim line"
RESULT worktree clean after all mutants: []
```

All four die, and each dies on the arms its own mechanism owns — so both halves
of the new conditional are load-bearing, not only the `else`. `MEX` is the one
worth naming: it shows the exact-file arm matters for `bot_paths`' FILE entries
(the claim files), which a reader of the diff might assume was dead weight.
`ME` is moot and I say so rather than reporting it as run.

The `MCO` count is also this PR's failing-test-first proof, and it substitutes
for a red-first splice: reverting the narrowing reddens 6 arms with no other
change, so the arms are not vacuous.

## Steps 14 and 15 — no metric moved, nothing to raise

```
RESULT structure.py: main rc=0, head rc=0, outputs byte-identical -- no metric moved (STRUCTURE RATCHET PASSED)
RESULT archscore score.py --diff <merge-base>: dS +0.0000 NULL -- not regressed
RESULT policy_lint.mjs --budgets: head rc=0, main rc=0, outputs byte-identical -- no cap moved, so no raise is the owner's here
RESULT policy_lint.mjs plain: head rc=0, main rc=0, byte-identical -- TOTAL 0 errors across 40 policy files; FIXTURE ok 92 errors / 243 pins / 12 classes
RESULT brief_lint.mjs: rc=0, TOTAL 0 errors across 45 files, CARRY 44 files, ROSTER ok, carry-2075.json 0 errors 0 warnings
RESULT rule 4: VERSION, manifest.json and RELEASE_NOTES.md absent from the diff
RESULT budgets: no *_budgets.json in the diff, so budget-raise-gate has no raise to grade
RESULT claim files: claimed_drift.txt eda8856b9 and card_claimed_drift.txt c683379da -- identical at head, merge base AND current main, so this branch claims nothing and neither file can conflict
RESULT diff file list: A dev/programme/carries/carry-2075.json, M tools/pr/app_approve.sh -- 2 files
RESULT self-test at head in its own worktree: 161 checks, 0 failed, rc=0
RESULT self-test at main d0f085ffb in its own worktree: 153 checks, 0 failed -- delta +8 checks from 4 new fixtures
```

The new tracked file **is** deliberately classified, which `CLAUDE.md` requires
of any new tracked file: `tests/closure.py`'s `INERT` list carries the prefix
`"dev/programme/"` (line 250, added by R9-RO-5), and its four siblings
(`carry-1645/1774/1795/1922/201.json`) are already tracked under it. **I could
not run `tests/entities.py` to confirm this** — it imports `harness`, which
imports `homeassistant`, absent from the 3.14.7 venv and not installable here.
So that one is verified by reading the INERT prefix and the precedent, not by
the instrument; CI's `fast` lane is what actually runs it, and it has not run at
this head. Flagging it as unverified rather than reporting it as confirmed
(step 8).

**Self-test honesty, which the dispatch asked about specifically.** The body
quotes 157 and does not name the instrument that printed it; the true pair at
the re-cut is **161 (macOS, this machine, `bash tools/pr/app_approve.sh
--self-test` in its worktree)** against **153** for main's copy. Round 1's
platform split still applies and I could not re-measure CI's side, because
`instrument-self-tests` has never run at `cfa0f3d00` (`total_count=0`); at round
1's head CI printed 159 where macOS printed 157. So the body must state, per
`writing-for-agents`, which instrument printed which number — and at this head
the CI number does not yet exist. One trap I hit and discarded rather than
reporting: running an extracted *copy* of the script outside its tree prints
`145/100 failed`, `153/17`, `161/21`. Those are artefacts of the extraction, not
measurements; every count above comes from a script run inside its own worktree.

Step 17 on added lines: one owner per concern holds (ground 1); no concept is
duplicated — the new `BOT_NAME`/`BOT_EMAIL` constants sit in the self-test
section and *consolidate* a hardcode main already had inline at line 588, and
hardcoding them independently of production `bot_author()` is what lets the
forged-identity arms detect `bot_author` changing wrongly. The bot email now
appears at 9 sites tree-wide, 8 of them pre-existing on main; `entities.py:25968`
pins the workflows' copies and pins neither `app_approve.sh` copy — true at main
too, so not new debt, but worth a line in the record if anyone later relies on
that pin.

## What I did not re-run, and why

The gate and the mutation table (step 11 cites CI's heavy runs, and nothing here
turns on them: my four mutants are planted and read directly). `env_drift.py
--all` (step 4): the diff moves no fixture and both claim files are
byte-identical at head, base and main, so there is no drift to declare and
neither file may be touched. `card_drift.mjs`: no card change. The
`delivery-status` row: `docs/delivery/2075.md` is correctly absent from the
diff, since `delivery-status-tracking.md` makes the row the orchestrator's.
`nightly-status`: its non-exempt arm does not apply — the diff touches neither
the mutation ledger nor a workflow file.

## RESULT lines

```
RESULT round 2, measured head cfa0f3d00a6fa8bd3604f02a066088fc3f07aba2, PR live head 094f2c0d2696b4bd04cd485b9e7fc3f144620053
RESULT poll 15 passes / 75 min at 300 s: head never moved off 094f2c0d2; mergeable=CONFLICTING, mergeState=DIRTY, draft=true throughout
RESULT ground1 diff is additions-only narrowing of main's own carry(); no bot_commit, no second bot path; one owner per concern holds
RESULT ground1 merge-tree 92248338 cfa0f3d00 -> exit 0, tree 9b88069cc, stderr empty, 0 MERGE-CLAIM markers (round-1 head: exit 1, CONFLICT tools/pr/app_approve.sh)
RESULT ground2 :(exclude,literal)$p landed; N1 fixed-copy=REFUSE and N2 fixed-copy=REFUSE -- the file named '*' no longer carries
RESULT ground2 remedy probe: plain exclude hides 2 -> 0 visible; literal hides 2 -> 1
RESULT ground3 layout.py PYTHONPATH-free at head: layout: GUARD: 0 refusal(s) against d8a4bd36f638, rc=0 (round-1 head: 1)
RESULT ground3 git grep '.claude/workflows/policy_lint' tools/pr/app_approve.sh -> empty, rc=1
RESULT ground3 merge_train.py holds NO such line at this head; .claude/workflows/policy_lint.mjs absent at head and on origin/main, so the deleted fallback was dead at both ends
RESULT ground3 window pins 3 at b2b6acd64, 0 at d0f085ffb, 0 at head -- main removed them in #2059, so the re-cut loses no coverage
RESULT ground4 carry-2075.json linted by brief_lint: 0 errors 0 warnings; CARRY 44 files; TOTAL 0 errors across 45 files
RESULT ground4 R9-RO-13 is not a live roster group in this tree (only wave-3l-groups.json, naming neither R9-RO-13 nor 2075), so the carry file is the correct instrument
RESULT ground4 comment 6083743563 re-read from the API and exists: issue #201, author tvofi, 2026-10-09T15:15:00Z, 1929 bytes, names R9-RO-13
RESULT ground4 #2010 figure re-derived at the re-cut's merge base: 16965/16965, 4 diff output lines, 0 payload lines differing -- "one line of 16,965, pure context" reproduces
RESULT A step7 --carry 094f2c0d2 cfa0f3d00 origin/main -> rc=1, "cfa0f3d00 is a commit of the branch's own"; the body's head does not carry to the measured head
RESULT B check-runs at cfa0f3d00: total_count=0 -- 0 of the 17 required contexts of ruleset 23698884 have RUN at the measured head
RESULT C check-runs at 094f2c0d2: 40 runs / 38 names; latest-per-name non-green = fast (3.14) id 113892203905, pr-contract id 113894588362; ## Red checks says none
RESULT C body stale on 8 measured points: head sha, merge base, autofixCommit narrative, diffstat, self-test count, new-check count, four mutant names, Forward-carry, and the 1,472p friction item
RESULT D1 line 1024 backtick is command substitution: stderr "line 1024: AGENTS.md: command not found" on every run; the arm's printed name loses its '*'; isolated probe confirms bash attempts the first glob entry
RESULT D1 the assertion is unaffected ($? expands before the label); MNL still reddens the arm; no instrument pins these labels
RESULT D2 carry control says "all four carry"; planted reversion MCO reddens 6 checks from THREE fixtures -- H_PIN_BADMSG stays green via the generic ci: guard
RESULT D2 the mutation 'no_literal' does not exist in the tree (only an unrelated local at tests/structure.py:2399); planted from its description it reproduces exactly, 2 red arms
RESULT attacks A2/A3/A9 main-copy=CARRY fixed-copy=REFUSE -- the live hole on current main, and this PR closes it; each refusal on "the branch's own diff differs"
RESULT attacks A1/A11 CARRY at both copies; A6/A7 REFUSE at both; A10 REFUSE at fixed (the A2 class, not a merge); A5c main CARRY / fixed REFUSE
RESULT attacks A8 main CARRY / fixed CARRY -- unchanged from round 1, never reaches the narrowed branch; A4/A12 CARRY, the carried findings round 1 did not block on
RESULT nullctl #2071 6aaba97f->7843b799 base-copy REFUSE / main-copy CARRY / head-copy CARRY
RESULT nullctl #2070 3ecb86ad->a9ba0b88 base-copy REFUSE / main-copy CARRY / head-copy CARRY
RESULT nullctl #2066 b511f9dc->d1538a73 base-copy REFUSE / main-copy CARRY / head-copy CARRY
RESULT nullctl correction: the live pairs CARRY under main's current copy (#2059 landed bot_paths there); the REFUSE baseline is the pre-#2059 base copy, as round 1 established
RESULT nullctl #2065 3c9fe53f->90b9e87f REFUSE at all three copies -- 74 commits, 4 first-parent, "merges a456c5ed, which is not on origin/main"
RESULT nullctl #2010 d67d8a44->87849cd2 REFUSE at base-copy and head-copy
RESULT mutants MNL 2 red / MAF 6 red / MCO 6 red / MEX 1 red; every plant one file, production-only, verified by diff, restored; worktree clean after
RESULT mutant ME is moot: policy_lint.mjs is byte-identical at head and main (e5824f8da), the root parameter is not in the diff
RESULT self-test head cfa0f3d00: 161 checks 0 failed rc=0, in its own worktree; main d0f085ffb: 153 checks 0 failed; delta +8 checks from 4 fixtures
RESULT self-test trap discarded: extracted script copies outside their tree print 145/100, 153/17, 161/21 failed -- artefacts of extraction, not measurements
RESULT structure.py main rc=0 head rc=0 outputs byte-identical -- no metric moved
RESULT archscore --diff: dS +0.0000 NULL -- not regressed
RESULT policy_lint --budgets head vs main byte-identical -- no cap moved, no raise is the owner's
RESULT policy_lint plain head vs main byte-identical -- TOTAL 0 errors across 40 policy files
RESULT VERSION, manifest.json, RELEASE_NOTES.md and every *_budgets.json absent from the diff
RESULT claim files eda8856b9 / c683379da identical at head, merge base and current main -- the branch claims nothing
RESULT new tracked file classified: dev/programme/ is on tests/closure.py's INERT list (line 250), with four tracked siblings; entities.py NOT run locally (needs homeassistant), so this one is read, not measured
RESULT origin/main moved three times while I measured: d0f085ffb -> a9baf164c -> 92248338; main's app_approve.sh blob a07be5570 at all three, so no main-copy measurement shifted
```

## What the repair owes

1. Land the push so the PR carries `cfa0f3d00`, and let CI run — all 17 required
   contexts must RUN at it, since `total_count=0` today.
2. Re-take the **whole** body against `cfa0f3d00`, not the named subset: head
   and merge base, the `autofixCommit` narrative (that file is untouched now),
   the diffstat, 161 not 157 and which instrument prints it, the four mutant
   names that no longer exist, `## Forward-carry` naming
   `dev/programme/carries/carry-2075.json` and R9-RO-13, the `1,472p` friction
   item, and `## Red checks` naming `fast (3.14)` and `pr-contract` with their
   answer (ground 3's fix is the answer; step 11 still requires it written).
3. Single-quote the arm label at line 1024.
4. Correct the carry file's `control`: three of the four fixtures re-carry under
   the coarse reversion (6 checks), and either name the `no_literal` plant
   descriptively or land it as a mutation a reader can find.

Items 3 and 4 are one line each. Nothing in this verdict asks for a different
design — the narrowing is the right fix and my mutants show it is load-bearing
on both of its branches.
