# R9-RC-Carry-Pins: a mutation-autofix pin commit may add rows, not rewrite one

`tools/pr/app_approve.sh --carry` must not accept a head whose only change over
the verdicted head is a `mutation-autofix` `ci: pin killed mutants` commit that
REWROTE or DELETED a ledger row the reviewer already measured. That is the live
hole this PR closes: at `origin/main` `7cd5a588c` (`git merge-base` of this
branch), `carry` carries such a commit -- the reviewer's A2/A3/A9 fixtures all
CARRY against main's own copy, and `bash tools/pr/app_approve.sh --self-test` at
this head's base proves it. The plain ADD a pin commit makes is already handled:
the refuse baseline for a bare added row is the pre-`#2059` base `b2b6acd64`,
not current main -- `#2059` landed the carry-whole-subtree mechanism in between,
so #2071/#2070 carry at `7cd5a588c` (verified: main's own copy answers
`CARRY: yes` on both, re-run in `## Null control`), #2066 likewise per the
round-1 review, and the round-1 brief's "refuses under main's copy" was a
provenance error against a base that predated `#2059`.

`#2059` (R9-CI-2b) landed on main while this branch sat at its base, adding
`bot_author`/`bot_paths` to the very same `carry()` loop: a bot's subject may
change main's merge-driver files and its own declared paths and nothing else,
authored as that subject's writer, and a claim-file subject may only remove
lines. That is the mechanism, and it already carries every plain
`ci: pin killed mutants` commit this PR was first cut to fix. The first cut's
value is not the carry itself -- it is the hole left open beside it, and this
re-cut now closes it inside main's own mechanism rather than beside it.

`bot_paths` for the pin subject names `tests/mutation_budgets.json` and
`tests/mutation_ledger` -- a whole subtree, since the ledger moved to one file
per pinned row. The exclusion that hides a carried bot commit's files from the
branch's-own-diff comparison was built from that whole declared subtree, so a
bot commit that REWROTE or DELETED a row the branch's own diff already carried
was hidden too: its change to reviewed content vanished from `norm()`'s
comparison, and the head carried. Measured on main's own current copy, the
reviewer's A2/A3/A9 fixtures, and now pinned in this file's own arms: main's
coarse exclusion carries all three, `carry` must refuse all three.

The exclusion is now built from what this very commit did, path by path. An
entry `bot_paths` names that IS a file the commit changed (its exact path
appears in the diff, as `tests/closures.json` or a claim file does for the
other two subjects, and as `tests/mutation_budgets.json` can here) is excluded
whole, as before. An entry that is a DIRECTORY (no single diff line ever equals
it, only paths under it) contributes only what the RANGE added that the verdict
head `$v` did NOT already hold -- never a rewrite or a deletion of reviewed
content, which stays visible to the comparison below and refuses. That
`git cat-file -e "$v:$p"` test is also what closes the round-4 seam: two `ci:
pin killed mutants` commits in one range, the first DELETING a reviewed row and
the second re-adding the SAME path, union their additions across `v..h`, and the
re-add would otherwise re-cover the path the deletion exposed -- so a path `$v`
already held is never excluded, and the pair refuses. `bot_paths`' confinement
check still decides what such a commit may touch at all; this only decides what
the comparison may stop seeing, now narrower than the subject's whole subtree.

That narrowing introduced one new way to hide content, and it is fixed in the
same breath: `carry` turns each excluded path into a git pathspec, and a
pathspec is a glob -- `*` matches across `/`. A bot commit adding a file it
names literally `*` would, as a plain `:(exclude)`, widen one file's exclusion
to the whole subtree, hiding the rewrite sitting beside it -- exactly the class
this line now refuses. So each narrowed path is excluded as
`":(exclude,literal)$p"`, a filename and not a pattern. (`x`, read from main's
`.gitattributes` never from a head, and the confinement `y` list, take their
paths from main's tracked files or `bot_paths`' own hand-written list, and
were never exposed to a commit choosing its own filenames.)

## Grounds from the round-1 review, and where each is addressed

- Ground 1, `architecture-unsound` (a second mechanism beside the landed one,
  and a content conflict on `tools/pr/app_approve.sh`): this re-cut merges
  `origin/main` and resolves the conflict by DELETING the first cut's parallel
  `bot_commit` entirely (and with it the `tools/policy/policy_lint.mjs` reading
  it added, so `policy_lint.mjs` is now byte-identical to `origin/main` and is
  not in this diff at all) -- `bot_paths`/`bot_author` answer those questions
  already, and the whole change is now the one loop that tightens
  `bot_paths`' subtree accumulation, per `fixer.md` step 17's "the existing
  mechanism, never a parallel one".
- Ground 2, `root-cause-unanswered` on `fast (3.14)` and `pr-contract` (the
  dead retired-path fallback): the first cut's `bot_commit` carried
  `lint="$SELF_DIR/../policy/policy_lint.mjs"` with a fallback to
  `.claude/workflows/policy_lint.mjs`, a GENER copy retired by the same
  reorganisation this file's own layout guard (`tests/layout.py`) refuses a new
  citation of, and which exists at neither base nor head. Deleting `bot_commit`
  deletes that dead fallback too, rather than adding an allowance over it; see
  `## Red checks`.
- Ground 3 (main's landed mechanism is looser than this PR's on exactly the
  additions-vs-rewrites axis): addressed, it is now the whole body of this
  change -- `bot_paths`' subtree contributes only its commit's own additions to
  the exclusion, and `## Mutation proof`'s `no_narrow` shows main's coarse
  version carrying all three attacks this branch now refuses.
- Ground 4, `metric-gamed: carry:` (a pathspec is a pattern): addressed with
  `":(exclude,literal)$p"` and the planted `H_PINGLOB` arm, a file named `*`
  beside a rewritten row; `## Mutation proof`'s `no_literal` shows that one
  arm, and only that one, going red when the token is dropped.
- Round 4's `harness` seam (a delete-then-readd of the same reviewed path across
  two `ci: pin killed mutants` commits still carried): addressed with
  `git cat-file -e "$v:$p" && continue` -- a path the verdict head already held
  is reviewed content and is never excluded -- and the planted `H_DELREADD` arm
  beside `H_DELADD` (delete + add a different path, which refuses, isolating the
  seam to the same-path re-add). `## Mutation proof`'s `no_skippath` shows
  removing that one guard reddens exactly the two `H_DELREADD` checks. The
  reviewer's challenge -- is there a case where a path was on `$v` for a reason
  other than being reviewed -- has no false-refusal answer: a path is on `$v`
  because this branch reviewed it, or because main owns it and a bot rewriting
  main's row is interference; both should refuse, and only a path new at `$v` (a
  genuine fresh add) is excluded, which `H_OKADD` still carries.
- One seam is deliberately NOT closed here, carried to `R9-RO-13` in
  `dev/programme/carries/carry-2075.json`: the BUDGET residual (a bot rewrite of
  `tests/mutation_budgets.json`, the exact-file entry, still a carry -- main's
  existing behaviour, its only backstop `budget-raise-gate` re-running at the
  pushed head). The #2010 context-shift question that earlier rounds carried is
  no longer live: #2010 merged (`1b72ca19f`), so its pair is moot, and the carry
  file now records the rule to re-measure rather than a live instance.

## Head

Measured at `addd6f45758ff90ab862bcbe62357c1373ed7786` -- the fix, its arms, and
the round-1..4 review's closures, with `origin/main` merged in. `origin/main` ran
forward several times while this sat (`#2067`, `#2069`, then the `#2072`/`#2073`/
`#2063`/`#2010` batch through `7cd5a588c`); each was a clean automatic `git merge`
(merge-tree exit 0, no conflict, no reviewed line of `tools/pr/app_approve.sh` or
the carry file moved), so the fix, its arms and `carry`'s mechanism are identical
under the round-4 head and under this one -- only the head SHA and its merge base
moved. The merge base is `git merge-base origin/main HEAD` =
`7cd5a588cbbbef354c00148040da2d720b8a888c`, and the figures below are re-taken at
it.

## Mutation proof

Three mutations, each a deletion of one mechanism this branch changed, run
against the whole `--self-test` (166 checks). Each red name fails ONLY while the
mutant is present, and is green again on restore.

```
no_narrow    # the accumulation reverts to bot_paths' whole declared subtree, as main's copy does
  FAIL NO CARRY: the bot's pin commit over a row the branch's own diff already carried  (x4: rewrite, delete, delete+add, delete+readd)
  FAIL refused by the branch's own comparison, not the confinement check  (x4)
  FAIL NO CARRY: a path named '*' is not a wildcard, it is one added file
  FAIL refused by the branch's own comparison, literal pathspec holding
no_literal   # the narrowed path is excluded as a glob again, plain ":(exclude)"
  FAIL NO CARRY: a path named '*' is not a wildcard, it is one added file
  FAIL refused by the branch's own comparison, literal pathspec holding
no_skippath  # drop `git cat-file -e "$v:$p"`: an added path the verdict head already held is not skipped
  FAIL NO CARRY: the bot's pin commit over a row the branch's own diff already carried  (x2)
  FAIL refused by the branch's own comparison, not the confinement check  (x2)
```

`no_narrow` reproduces the reviewer's A2/A3/A9 exactly, and the delete-then-readd
pair on top of them (the subtree exclusion carries all five shapes); `no_literal`
separates the glob defect and reds only the `*` arm; `no_skippath` removes the
`git cat-file -e "$v:$p"` guard and reds only the two `H_DELREADD` checks, so the
re-add guard is shown load-bearing for the delete-then-readd pair alone, and
nothing else in the 166 moves.

## Null control

`bash tools/pr/app_approve.sh --self-test` at `origin/main`'s own copy, with
this branch's test-only hunks added and NOTHING of the mechanism changed (the
test-only hunks of `git diff origin/main HEAD`, spliced onto
`git show origin/main:tools/pr/app_approve.sh`), is the failing-test-first run:
166 checks, 10 failed -- the five fixtures `no_narrow` also reddens (rewrite,
delete, delete-then-add, delete-then-readd, glob), each x2, since the unmodified
subtree exclusion carries all of them. Two new arms are green at the base already:
`H_PIN_BADMSG` tests the generic `ci:` guard main already owns, and `H_OKADD`
adds a fresh row main carries too -- neither is a hole this branch closes.

The narrowing does not over-tighten the legitimate case, measured live: at the
merge base (`origin/main` = `7cd5a588c`) `#2071`'s `6aaba97f` -> `7843b799`
pair already CARRIES (main's landed mechanism), and so does `#2070`'s
`3ecb86ad` -> `a9ba0b88` pair; this branch's copy answers identically on both
(re-read at `cd /private/tmp/r9-main`, read-only, both shas already present).
What this branch changes is the rewrite/delete/re-add/glob rows
(`## Mutation proof`'s five fixtures), which main carries today and this branch
refuses -- that is the hole, and it is closed here. The round-1 brief's "refuses
at main's copy" for a plain added row was a provenance error (its baseline
predated `#2059`); this section states the live answer by SHA instead.

Negative control, that the narrowing does not over-reach: `#2065`'s own verdict
head `3c9fe53fa` to its current head `90b9e87f...` is a range that is not a bare
pin commit (two human `test(...)`/`ledger(...)` commits and a merge). It still
refuses, at this head and at main's, for an unrelated reason
(`90b9e87f... is not the automatic merge of its parents` -- the reason the
round-3 body quoted, `merges a456c5ed..., which is not on origin/main`, has
drifted as main advanced past `a456c5ed`; the conclusion is unchanged).

The #2010 case this branch does NOT fix: `--carry d67d8a44... 87849cd2...
origin/main` REFUSED at `origin/main` and at this head while #2010 was a live
pull request (the branch's own diff differed, one pure-context line of 16,965,
a hunk the branch never touched), and both round-1 and round-4 measured that.
But **#2010 has since merged** (`1b72ca19f Merge pull request #2010`), so both
its heads are now ancestors of `origin/main`, `carry`'s two diffs are empty at
both ends, and the pair trivially carries -- the live instance is gone and the
refusal is no longer reproducible against an advanced main. The strict
context-equal rule in `carry` is unchanged by this PR either way; the class
question (should a pure context shift carry?) is carried for R9-RO-13 without a
live instance, and re-measuring it means planting the shape fresh, not replaying
this now-merged pair -- see `## Forward-carry`.

## Figures

Every command re-runnable at the head above; the count each prints is named with
its instrument, since two of them are platform-dependent.

- `bash tools/pr/app_approve.sh --self-test` at `addd6f457` -- 166 checks, 0
  failed (macOS, this seat's own `--self-test`). At `origin/main`
  (`7cd5a588c`, the merge base) the same command reports 153 checks, 0 failed;
  the 13-check difference is the new arms and their paired reason-greps. CI's
  `instrument-self-tests` prints 2 more than this seat's own `--self-test`
  (157 macOS against 159 CI at the first cut, the delta the +2 arms for
  `/proc`/`/sys` conditional checks), so the CI number here is expected to be 168
  -- derived, not measured, since `--self-test` at a handoff ref is not what CI's
  required context runs against, and the failing-test-first run in
  `## Null control` (10 failed at 166 macOS) will read the same delta wherever it
  is re-run.
- `python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED`, rc 0. No metric
  moved: the caps are Python-production metrics and this diff touches only a
  `.sh` and a `.json` file, neither of which `tests/structure.py` measures.
- `PYTHONPATH=tests/hastub python3 tests/layout.py` -- `layout: GUARD: 0
  refusal(s) against 7cd5a588cbbb`, rc 0, at the current head (the guard now
  reports against the advanced merge base). At the first cut (`094f2c0d2`) the
  same command reported `GUARD: 1 refusal(s)` against `b2b6acd64`, rc 1 -- the
  dead retired-path fallback, ground 2, now deleted with `bot_commit` itself.
- `python3 tools/audit/seat/merge_train.py --self-test` -- passes, 0 failed, at
  this head; its check count tracks `origin/main` and moved several times since
  the round-1 body, so it is not quoted as a fixed figure (the round-1 `81`
  reproduces at neither the round-3 nor this head). The load-bearing claim is
  checked directly instead: `merge_train.py` resolves `app_approve`
  old-path-first (`tools/audit/app_approve.sh` then `tools/pr/app_approve.sh`)
  and all three of its `TOOLS` first candidates are gone from the tree (`find
  tools/audit -maxdepth 2 \( -name app_approve.sh -o -name app_push.sh -o -name
  preflight.sh \)` returns nothing, and `ls` names each as `No such file or
  directory`) -- a dead arm of exactly ground 2's class, and NOT touched here:
  it is R9-RO-10's pre-existing debt (R9-RO-6 moved the scripts), and this PR
  stays scoped to the mechanism it exists to fix.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
  --workdir "$D"` -- `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` (keyed
  on the mode line, not the count, per `CLAUDE.md` rule 1), taken on a fresh
  `mktemp -d` workdir with `git status` clean -- a second run in a reused dir
  reads the four `scope.*` files it wrote as changed and prints `MODE: FULL`.
  `tools/pr/app_approve.sh` and `dev/programme/carries/` are in no measured
  closure, so the scoped gate runs nothing for this diff; CI's required
  `instrument-self-tests` job runs `--self-test` directly regardless.
- `git diff --stat $(git merge-base origin/main HEAD) HEAD` -- 2 files changed,
  169 insertions(+), 4 deletions(-). `git diff --numstat` of the same range
  splits it: `tools/pr/app_approve.sh` +138/-4, `dev/programme/carries/carry-2075.json`
  +31/-0. Two-dot against `origin/main` is the wrong frame (main advanced to
  `7cd5a588c` through the `#2072`/`#2073`/`#2063`/`#2010` batch since the first
  cut's base `b2b6acd64`, and the merge-base is `7cd5a588c` too now, so both
  agree -- `CLAUDE.md` rule 3's three-dot discipline still names the merge-base
  as the frame, and `tests/layout.py`'s guard reports against it).
- The #2010 measurement is now moot and is recorded, not re-quoted: while #2010
  was live, `carry`'s own `norm()` pipeline for `mv=git merge-base origin/main
  d67d8a44` and `mh=git merge-base origin/main 87849cd2` gave 16965 lines a side
  with a two-line diff (one `<`, one `>`, both leading-space context, zero
  added-or-removed), the round-1 and round-4 reviews both measured it. #2010 has
  since merged (`1b72ca19f`), so both heads are ancestors of `origin/main` and
  the pipeline is now empty at both ends; the figure is a function of main's tip
  and is not restated as current. The #2065 range still re-derives at 74 commits,
  4 first-parent (two human `test(...)`/`ledger(...)` commits and two merges) --
  the two shas are fixed, so this one does not move with main.

## Red checks

`fast (3.14)` and `pr-contract` -- check-run ids 113892203905 and
113894588362, both red at this branch's first head `094f2c0d2` and reported by
the round-1 review. The cheaper detector that already stands here is the very
instrument `fast (3.14)` runs: `PYTHONPATH=tests/hastub python3 tests/layout.py`,
whose retired-path guard refuses a NEW citation of a landed path at any head, and
whose standing cost is nothing further -- it runs on every pull request already.
It fired exactly as designed and named its own reason (the `||
lint="$SELF_DIR/../../.claude/workflows/policy_lint.mjs"` fallback, which cited
a GENER copy present at neither base nor head). The fix is deletion, not an
allowance: with `bot_commit` gone, the fallback line does not exist to answer
for, and `tests/layout.py` at this head reports `GUARD: 0 refusal(s)` (in
`## Figures`); `pr-contract` was red only because the body did not yet name a
red it read at an earlier head of this same branch, which this section now does.
No red is left unanswered at the current head.

## Forward-carry

`dev/programme/carries/carry-2075.json`. The live entry is the BUDGET residual
the round-4 review raised: a bot rewrite of `tests/mutation_budgets.json` -- the
single FILE entry `bot_paths` names -- still carries, at this head and at main,
because the file branch excludes that exact path whole. It is main's existing
behaviour, unchanged by this diff, and `budget-raise-gate` re-runs at the pushed
head as its backstop, so it is recorded rather than closed here. The other entry
is the #2010 context-shift rule, now MOOT: #2010 merged (`1b72ca19f`), so its
pair trivially carries and the record is a rule to re-measure (plant the shape
fresh) rather than a live instance. The round-9 roster is not on main, so the
carry file named here is its in-tree destination, per
`dev/governance/rules/finding-propagation.md`.

## Friction

brief-citations: unclear: the seat brief named `tests/mutation_table.py`'s
`drain_write_set_problems`/`DRAIN_ROWS` as "the ledger writer's own guarded
write set" to extend. Verified rather than inherited: that guard bounds a
DIFFERENT job (`mutation-ledger-push`, DRAIN_SUBJECT `ci: record nightly kills`,
pushing straight to `main`), and the live bound for THIS bot's write set is now
`bot_paths`/`bot_author` in `tools/pr/app_approve.sh` itself, landed by #2059
while this branch sat at its base -- so the re-cut reads main's own mechanism,
not `DRAIN_ROWS`, not `AUTOFIX_BOT_COMMITS`, and not a hand-written table of its
own.

gate-scoping: cost: `python3 tools/audit/seat/merge_train.py --self-test` and
`bash tools/pr/app_approve.sh --self-test` both queued behind another process's
`tests/gate_lock.py` lease before running; per `gate-scoping.md` the correct
behavior is to wait, which they did.

gate-scoping: stale: `tools/pr/app_approve.sh`'s three source-pin assertions
("boundary class", `pwd -P`, "filesystem root") grep the file with a positional
`sed` window (`sed -n '1,340p'`), which a production edit above the evidence
gate silently shifts. This branch does not move that window: #2059 landed a
content-anchored form (`sed '/^if \[ "${1:-}" = "--carry" \]; then$/q'`) while
this branch sat at its base, so the re-cut took main's anchor and the fragility
class closed here on its own.

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
