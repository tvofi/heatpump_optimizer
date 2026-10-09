# R9-RC-Carry-Pins: a mutation-autofix pin commit may add rows, not rewrite one

`tools/pr/app_approve.sh --carry` must accept a head whose only change over the
verdicted head is `mutation-autofix`'s own `ci: pin killed mutants` commit, and
must not accept one that also rewrote or deleted something the reviewer already
measured. Measured 2026-10-09 on #2065 at head `3c9fe53fa`, and independently
confirmed on two still-open heads today: #2071 (`6aaba97f` -> `7843b799`, exactly
one commit between them, that commit) and #2070 (`3ecb86ad` -> `a9ba0b88`, same
shape).

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
it, only paths under it) contributes only what the commit ADDED beneath it --
never a rewrite or a deletion, which stays visible to the comparison below and
refuses. `bot_paths`' confinement check still decides what such a commit may
touch at all; this only decides what the comparison may stop seeing, and now
narrower than the subject's whole subtree.

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
  `origin/main` (`d8a4bd36f`) and resolves the conflict by DELETING the first
  cut's parallel `bot_commit` and its `autofixCommit` reading from
  `tools/policy/policy_lint.mjs` -- `bot_paths`/`bot_author` answer those
  questions already and are the mechanism now tightened, per `fixer.md` step
  17's "the existing mechanism, never a parallel one".
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

## Head

Measured at `cfa0f3d00a6fa8bd3604f02a066088fc3f07aba2`
(`chore(R9-RC-Carry-Pins): drop the closures.json fixture scaffolding`), after
`5238604de` (the `## Forward-carry` destination) and `1c458409b` (the merge of
`origin/main` `d8a4bd36f` resolving ground 1) over the first cut's two commits.
The merge base is `git merge-base origin/main HEAD` = `d8a4bd36f6384dde45486fff388f91ed4a3aa6df`,
the same base the round-1 reviewer measured against, which is why the
before/after figures below are all re-taken at it.

## Mutation proof

Two mutations, each a deletion of the one mechanism this branch changed, run
against the whole `--self-test` (161 checks). Each red name fails ONLY while the
mutant is present, and is green again on restore.

```
no_narrow    # the accumulation reverts to bot_paths' whole declared subtree, as main's copy does
  FAIL NO CARRY: the bot's pin commit over a row the branch's own diff already carried  (x2: rewrite, delete)
  FAIL refused by the branch's own comparison, not the confinement check  (x2)
  FAIL NO CARRY: a path named `*` is not a wildcard, it is one added file
  FAIL refused by the branch's own comparison, literal pathspec holding
no_literal   # the narrowed path is excluded as a glob again, plain ":(exclude)"
  FAIL NO CARRY: a path named `*` is not a wildcard, it is one added file
  FAIL refused by the branch's own comparison, literal pathspec holding
```

`no_narrow` reproduces the reviewer's A2/A3/A9 exactly (main's own live hole,
here caught by the four arms this branch adds: `H_PINMOD` rewrites a row,
`H_PINDEL` deletes one, `H_PINGLOB` adds a file named `*` beside a rewritten
row, and all three must refuse); `no_literal` separates the glob defect from
the narrowing, and reds only the one arm the glob can poison.

## Null control

`bash tools/pr/app_approve.sh --self-test` at `origin/main`'s own copy, with
this branch's test-only hunks added and NOTHING of the mechanism changed (the
test-only hunks of `git diff origin/main HEAD`, spliced onto
`git show origin/main:tools/pr/app_approve.sh`), is the failing-test-first run:
161 checks, 6 failed -- exactly the arms `no_narrow` also reddens, since the
unmodified subtree exclusion carries all three attacks. The fourth new arm,
`H_PIN_BADMSG`, is green here already: it tests the generic `ci:` guard that
main's mechanism already owns and this branch does not change.

The same narrowing, measured live: at `origin/main` (`d8a4bd36f`) `#2071`'s
`6aaba97f` -> `7843b799` pair already CARRIES (main's landed mechanism, not this
branch), and so does `#2070`'s `3ecb86ad` -> `a9ba0b88` pair; this branch's
copy answers identically on both (re-read at `cd /private/tmp/r9-main`,
read-only, both shas already present). This is the null control that replaces
the first cut's, which had to be re-taken once main moved: it can no longer say
"refuses at main's copy" for a plain added row, because main's copy now carries
it too.

Negative control, that the narrowing does not over-reach: `#2065`'s own verdict
head `3c9fe53fa` to its current head `90b9e87f...` is a 74-commit range, not a
bare pin commit (two human `test(...)`/`ledger(...)` commits and a merge of a
commit not yet on `origin/main`). It still refuses, at this head and at main's,
for the same unrelated reason (`... merges a456c5ed..., which is not on
origin/main`).

The #2010 case this branch does NOT fix, and the null control that proves it
still refuses exactly as designed: `--carry d67d8a44... 87849cd2...
origin/main` refuses at `origin/main` and at this head for the same reason
(`the branch's own diff differs`); the narrowed subtree exclusion changed
nothing there, because that pair has no added row at all, only a shifted context
line in a hunk the branch never touched -- see `## Forward-carry`.

## Figures

Every command re-runnable at the head above; the count each prints is named with
its instrument, since two of them are platform-dependent.

- `bash tools/pr/app_approve.sh --self-test` at `cfa0f3d00` -- 161 checks, 0
  failed (macOS, this seat's own `--self-test`). At `origin/main`
  (`d8a4bd36f`) the same command reports 153 checks, 0 failed; the 8-check
  difference is the four new arms and their paired reason-greps. CI's
  `instrument-self-tests` prints 2 more than this seat's own
  `--self-test` did at the first cut (157 macOS against 159 CI, and 145 against
  147, both already measured, the delta the +2 arms for `/proc`/`/sys`
  conditional checks), so the expected CI number here is 163 and 155 -- not
  measured yet, since `--self-test` at a handoff ref is not what CI's required
  context runs against, and the failing-test-first run quoted in `## Null
  control` (6 failed at 161 macOS) will read the same delta wherever it is
  re-run.
- `python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED`, rc 0. No metric
  moved: the caps are Python-production metrics and this diff touches only a
  `.sh` and a `.json` file, neither of which `tests/structure.py` measures.
- `PYTHONPATH=tests/hastub python3 tests/layout.py` -- `layout: GUARD: 0
  refusal(s) against d8a4bd36f638`, rc 0, at the current head. At the first cut
  (`094f2c0d2`) the same command reported `GUARD: 1 refusal(s)` against
  `b2b6acd64`, rc 1 -- the dead retired-path fallback, ground 2, now deleted
  with `bot_commit` itself.
- `python3 tools/audit/seat/merge_train.py --self-test` -- 81 checks, 0 failed.
  `merge_train.py` resolves `app_approve` old-path-first
  (`tools/audit/app_approve.sh` then `tools/pr/app_approve.sh`) and all three
  of its `TOOLS` first candidates are gone from the tree (`find tools/audit
  -maxdepth 2 -name 'app_approve.sh' -o -name 'app_push.sh' -o -name
  'preflight.sh'` returns nothing, and `ls` names each as `No such file or
  directory`) -- a dead arm of exactly ground 2's class, and NOT touched here:
  it is R9-RO-10's pre-existing debt (R9-RO-6 moved the scripts), and this PR
  stays scoped to the mechanism it exists to fix.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
  --workdir "$D"` -- `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` (keyed
  on the mode line, not the count, per `CLAUDE.md` rule 1). `tools/pr/app_approve.sh`
  and `dev/programme/carries/` are in no measured closure, so the scoped gate
  runs nothing for this diff; CI's required `instrument-self-tests` job runs
  `--self-test` directly regardless of that scoping.
- `git diff --stat $(git merge-base origin/main HEAD) HEAD` -- 2 files changed,
  127 insertions(+), 4 deletions(-). `git diff --numstat` of the same range
  splits it: `tools/pr/app_approve.sh` +96/-4, `dev/programme/carries/carry-2075.json`
  +31/-0. Two-dot against `origin/main` is the wrong frame (main advanced to
  `d8a4bd36f` and the merge-base is `d8a4bd36f` too now, so both agree --
  `CLAUDE.md` rule 3's three-dot discipline still names the merge-base as the
  frame, and `tests/layout.py`'s guard reports against it).
- The #2010 measurement, run from `/private/tmp/r9-main` with `carry`'s own
  `norm()` pipeline for `mv=git merge-base origin/main d67d8a44` and
  `mh=git merge-base origin/main 87849cd2`: each side `wc -l` is 16965, and
  `diff` prints exactly two output lines, one `<` and one `>`, both leading-space
  context (main's own history rewrote the text between the two merge bases),
  with zero added-or-removed lines of the branch's own. The #2065 range
  re-derives at 74 commits, 4 first-parent, two human `test(...)`/`ledger(...)`
  commits and a merge of a commit not on `origin/main` -- as the round-1 review
  re-derived it too.

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

`dev/programme/carries/carry-2075.json`. The round-1 review's ground 4 stands:
this branch's narrowed subtree exclusion admits, for `tests/mutation_ledger/**`,
the pure-context-shift class the body elsewhere refuses to fix -- a rewrite or
deletion is now visible again, but a context line that only MOVED, as in #2010,
still refuses on `the branch's own diff differs` by design. Whether `carry`
should tolerate that shift is a question for the round-9 roster group R9-RO-13
(mandate-gated batch policy), which is not on main, so the carry file named here
is its in-tree destination, per `dev/governance/rules/finding-propagation.md`.

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
