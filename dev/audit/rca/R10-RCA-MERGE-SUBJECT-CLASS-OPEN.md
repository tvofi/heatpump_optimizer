# R10-RCA-MERGE-SUBJECT-CLASS-OPEN: #2697 blocked class-open for eight rounds

Root-cause seat, `root-cause.md`, 2026-10-25. Measured at `origin/main` `102f74975`.
Nothing was fixed. The PR's branch, `tools/policy/agreement.mjs` and its harness were
not touched. The round-9 fixer (topic `r10-merge-subject-harden-r9`) was running while
this was written, so round 9 is not counted anywhere below.

The one instrument this record adds is the seat's own, not the finder's, a fixer's or a
reviewer's: `dev/audit/rca/merge-subject-class-open/differential.mjs`. It loads
`subjectWriters` out of `tools/policy/agreement.mjs` at any ref, using the same block
cut as the PR's argv-seam harness, and compares refused sets. Its three modes are
described in its header. Every figure below names the command that printed it.

## 1. What happened, reproduced

#2697 (R10-MERGE-SUBJECT-HARDEN, size S, severity low) changes the merge-subject guard.
Round 1's brief asked for two things. The second was: "The scan that detects a
`--subject` writer is line-based ... measure a writer it misses, for example a
`--subject` split across a continuation line, then make the scan read the whole
command, not a line." The round-1 head, `09b1d002c`, met that by replacing the line
test with `callExtent`. In the round-1 body's own words, the extent "starts at the
innermost bracket left open before the match on its line, or at the line's start if
none is open".

Eight fix reviews followed, and each one blocked:
`git log --reverse --format='%cI %s' origin/review/2697`. Two blocks were
`mutation-vacuous` and six were `class-open`. Each example spelling a verdict named
was run under main's guard and under that round's head:
`node dev/audit/rca/merge-subject-class-open/differential.mjs named origin/main`.

| review | head | block | named spelling | main | head |
|---|---|---|---|---|---|
| 1 | `b4dd11917` | mutation-vacuous | `(cd repo) && gh pr merge ...` (a mutant only) | refused | refused |
| 2 | `96ad30e87` | mutation-vacuous | `gh pr \` newline `merge ... --subject` | missed | missed |
| 3 | `455d7c200` | class-open | `gh pr "merge"`, `gh pr -R o/r merge`, single-quoted argv | missed | missed |
| 4 | `5d79db511` | class-open | `--subject "x y"` in a gap, `${GH:-gh}`, `$(command -v gh)` | missed | missed |
| 5 | `d0d35231c` | class-open | `f"{GH} pr merge"`, `"%s pr merge" % GH`, `${cfg.gh}` | missed | missed |
| 6 | `683dd52cb` | class-open | wrapped argv, bracket on the program's line | missed | missed (refused at `d0d35231c`) |
| 7 | `e73424f24` | class-open | `  never) gh pr merge ... --subject ... ;;` | **refused** | missed |
| 8 | `4aad9c117` | class-open | `down) with \`gh pr merge 9 --subject x\``, `1) gh pr merge ...` | **refused** | missed |

So there are two populations, and they are different defects.

- **Reviews 2 to 6: OPEN-AT-BOTH, 11 of 11 named spellings.** Main misses each one as
  well. These are not regressions. They are members of the class the bodies claimed
  to close. The claim grew past the brief: the round-4 body said "the class is
  closed by construction for everything a lexical scan can read", and the round-5
  body said "`MERGE_CALL` reads every spelling of one call that gh's argv and the
  Python, JS and shell call forms accept"
  (`git show <commit>:BODY.md` over `git log origin/handoff-body/r10-merge-subject-harden`).
  Each reviewer then disproved that claim with a fresh sample, as `fix-review.md`
  step 6 requires. Review 6's spelling was a regression against the previous head
  (`differential.mjs named d0d35231c` prints `REGRESSION`), not against main.
- **Reviews 7 and 8: REGRESSION, 3 of 3 named spellings.** Main refuses each one and
  the head does not.

### The regression was in round 1's head, not round 7's

The corpus mode generates 192 lines whose lead closes a bracket it did not open on
that line. They come from 16 leads, 3 subject writers and 4 file kinds. Alongside
them it generates 96 control lines and 8 over-fire nulls:
`node dev/audit/rca/merge-subject-class-open/differential.mjs corpus origin/main origin/main 09b1d002c b4dd11917 96ad30e87 455d7c200 5d79db511 d0d35231c 683dd52cb e73424f24 4aad9c117`

| guard | lead-closer refused, of 192 | control refused, of 96 | null refused, of 8 | main_not_head |
|---|---|---|---|---|
| origin/main (null control) | 192 | 96 | 0 | 0 |
| `09b1d002c` (round 1, first commit) through `683dd52cb` (round 6), all seven heads | 0 | 96 | 0 | 192 |
| `e73424f24` (round 7), `4aad9c117` (round 8) | 45 | 96 | 0 | 147 |

The same result reproduces with the finder's harness. Take the round-8 reviewer's
plant (`git show origin/review/2697:evidence/md_plant.sh`), run it in a worktree of
`origin/main`, and pass each guard's ref:

- `origin/main`: plant refused at `web-fragments.md:157`;
- `09b1d002c`: plant not refused;
- `b4dd11917`: plant not refused;
- control without the parenthetical: refused at all three ends.

One run of `agreement_py.py --run` takes 28 to 32 s here (`time`).

So the regression that blocked round 8 was present at the PR's first commit. Seven
reviews ran over it. Review 7 found one spelling of it (the case arm) and measured it
against the previous heads, not against main. Review 8 was the first to measure
against main.

### The tree-generated differential names it at round 1

The planted mode takes a corpus from the tree instead of a hand list. Every non-blank
line of the 289 files the guard scans becomes a lead, and a subject writer is planted
after it on the same line. That gives 82735 lines:
`node dev/audit/rca/merge-subject-class-open/differential.mjs planted origin/main origin/main 09b1d002c 4aad9c117`
(12.1 s for four guard loads).

| guard | refused, of 82735 | main_not_head | of which: closer before any opener in the lead | comment line | other |
|---|---|---|---|---|---|
| origin/main (null control) | 82735 | 0 | 0 | 0 | 0 |
| `09b1d002c` (round 1) | 74251 | 8484 | 8412 | 16 | 56 |
| `4aad9c117` (round 8) | 74665 | 8070 | 8016 | 0 | 54 |

At round 1, 8412 of 8484 lines (99 %) that main refuses and the head does not fall in
the class review 8 named. The bucket rule is a quote-blind bracket count, written in
the script's `shape()`. The 54 `other` lines at round 8 hold a quote, or a bracket
inside a quote (for example `stamp.py`'s `'raise Refuse("rows"'`). That bucket rule
does not call them lead-closers, and no verdict named them. Section 6 carries them.

## 2. The cause, named

**Cause.** The guard's acceptance was measured only on the tree, and the tree holds no
merge writer. Every both-ends measurement in the contracts therefore read flat. The
finder's harness printed `refused=0` at base and head on every round (round 1 body:
"both base and head print `refused=0`"; review 3: base `73b69fe0a` and head both
`RESULT ... refused=0`). The one differential in the PR's tree,
`dev/audit/harnesses/r10_merge_subject_census.mjs <old guard>`, compares
**`MERGE_CALL` match counts** between two guards. It does not compare refusals, and it
runs over the same writer-free tree. A shorter extent loses a refusal and keeps the
call, so that census read `TOTAL old=63 new=63` with no `DIFF` line while 8070 planted
refusals were lost (review 8's `ev/census.txt` against the planted table above).

So the guard's input domain, meaning every text the scan reads with a writer in it,
was never generated at either end. Nobody measured the loss direction, refused at the
base and not at the head, until review 8 did it by hand with one plant. The gain
direction was measured only by sampling, one reviewer's spelling per round, with no
corpus that could say when to stop.

Both populations in section 1 are symptoms of that one cause:

- Reviews 2 to 6 sampled the gain direction because no corpus bounded the body's claim.
- Reviews 7 and 8 found the loss direction late because no corpus was ever run at the
  base.

The candidates the brief named, tested:

| candidate | measured | verdict |
|---|---|---|
| The class was never stated as a property; there was no domain or generator at round 1 | Round 1's brief gave the class by example ("for example a `--subject` split across a continuation line"). The bodies' class rules were tree greps: review 3 says rule 2, `git grep -E 'gh pr merge\|merge_pull_request'`, "enumerates scan sites, not call spellings" | **the cause, half**: no generated domain |
| The fixer's harness was the fixer's own list, and the finder's harness is a sample | The finder's harness is the tree, which is flat at both ends. Plants were per-spelling at each end. The fixer's seam harness (`r10_merge_subject_argv_seam.mjs`) is a hand list: 144 PROGRAM-CLASS rows and 12 WRAPPED rows | symptom: a hand list is the only corpus anyone could build without a generator |
| The brief never required a differential against main | True through round 8. The round-9 brief is the first to require one ("refused-at-main is a subset of refused-at-head"). `fixer.md` step 3 and `fix-review.md` step 2 require the finder's harness at both ends, and that harness is flat here | **the cause, other half**: the loss direction had no unit |
| The split arrived after round 7 instead of at round 4 | `fixer.md` "Past three rounds, re-cut rather than repair" dates from `e64d287fb` (2026-09-11) and re-cuts the body. Its only split is for "a re-cut body blocked on `claims` again". No policy splits a class-open PR: `grep -rn -i 'three-round\|split the' dev/governance/` returns only that line. Splitting appeared in the round-6 and round-7 briefs as an option and was imposed at round 8 by ruling | symptom, and a real one: the round-8 split closed the OPEN-AT-BOTH arm (review 8: "The narrowed class itself holds"). It could not close the regression arm, because a narrowing never measures the base |

Which side moved, by `git log`:

- Main's guard did not change in the window. The last commit to
  `tools/policy/agreement.mjs` on main is `ca1bc2b0e` (2026-10-23), before round 1, and
  every round's merge base carries the same guard.
- The contracts did not change either: each verdict records
  `git diff <merge-base>...origin/main -- dev/governance/roles/` as empty.
- The head moved. The regression is in `09b1d002c`'s `callExtent`, the round-1 design.

## 3. Process state

**(c) The process was followed and did not produce the intended result.**

Evidence, quoted:

- The process. `fixer.md` step 3: "Re-execute the finding's harness on your branch:
  before and after". `fix-review.md` step 2: "Measure with the finder's harness ... at
  the baseline SHA and at the PR head". `fix-review.md` step 6: "open the class".
  `fixer.md` step 8: "name a rule that enumerates the class's seams".
- Followed. Every body and every verdict ran the finder's harness at both ends.
  Round 1's body ran it unperturbed and perturbed at base and head. Every review named
  the round and ran its own generator (`probe.mjs`, `probe2.mjs` and `probe3.mjs` in
  review 8's evidence). Every body named a class rule and a census.
- Not the intended result. The harness's unit is the tree's refused set, which is
  empty on a tree with no writer, so "before and after" compares 0 with 0. Step 3's
  own escape is "a harness measuring what the fix rightly leaves alone reads flat at
  both ends: say so, and add a ... companion ... reading the defect at the baseline and
  not at the head". That companion points one way: defect at the base, gone at the
  head. The reverse, refused at the base and lost at the head, has no step. This is
  the shape `defect-root-cause.md` already records for #2073's step 6d, which "ran and
  passed ... while its unit read one of `mutation`'s two directions".
- Not (b). Nothing quoted above was skipped, and eight verdicts and eight bodies show
  it ran. A firmer "run the harness at both ends" would be a firmer instruction for
  something that was obeyed.
- Not (a). The checks existed and ran. What was missing was a unit: a generated corpus
  and the loss direction. That is a change to the unit, not a missing process.
  Root-cause.md says the countermeasure "changes the unit, not the arm count".
- Not (d). Nothing moved under the process; see "which side moved".

There is one sub-finding, state **(a)**: no policy splits a PR that is class-open past
round 3. The orchestrator ruled one in at round 8. The rule that exists, `fixer.md`'s
"orchestrator splits the branch or closes it", fires only on `claims`.

## 4. How far the class reaches

**Rule.** A tracked guard under `tools/` or `tests/` that runs `--check` over the
tree's text and refuses a call spelling through a hand-listed set of regexes. Found by
`git grep -l` for a `gh` or `git` subcommand inside a regex, then read by hand:

| guard | hand-listed arms | merges on main touching it, 2026-09-25 to `102f74975` | refusal differential against the base |
|---|---|---|---|
| `tools/policy/agreement.mjs` merge-subject guard | `MERGE_CALL` 4 arms at main (one regex line), and 916 file lines at `4aad9c117` against 596 at main | 10 | none at main; the round-9 brief requires one for this PR |
| `tests/throwaway_git.py --check` (`_SITE`) | 3 regexes | 1 | none: its merge-base use is absent (`grep -c` 0) |
| `tools/audit/seat/ref_privacy.py --check` (`_SITE`) | 8 alternation arms | 16 | none: its merge base scopes *which content* is judged (`--over origin/main`), not which guard version refuses |
| `tools/audit/seat/tmp_paths.py --check` (`CLASSES`) | 5 classes | 9 | none: the same scoping use |

Merge counts come from
`git log --first-parent --merges --since=2026-09-25 --oneline origin/main -- <file> | wc -l`.
29 distinct merges touched at least one of the four files, out of 809 merges on main
in the window. That is an upper bound on guard-changing PRs, because a touch need not
change a refusal path.

The same review shape elsewhere. Of 141 `review/*` refs on origin there are 300 verdict
commits, 16 of them `class-open`, spread over 9 PRs. Two PRs are spelling-sampling
loops on a lexical detector:

- #2697: 6 class-open verdicts;
- #2711: 2 class-open verdicts, on archscore getter spellings ("a bare getter spelt
  with a leading pass, tuple(...), a [:] copy ...").

The other 7 are seams of different kinds. The rule is a `for-each-ref` over
`refs/remotes/origin/review/` counting `git log --format=%s` subjects that hold
`class-open`. Only #2697 shows the regression-against-base shape. #2711's verdicts
were not checked for it.

## 5. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

The unit is wall-clock. The failure count is printed beside each figure.

**cost(defect), #2697 to round 8.** Rounds start at `09b1d002c` (2026-10-24T08:01Z)
and verdicts come from `git log --reverse --format=%cI origin/review/2697`.

| figure | value | failures |
|---|---|---|
| wall, first fixer commit to verdict 8 | 24.3 h | 8 of 8 verdicts blocked |
| per round (gap to each verdict) | 3.10, 4.94, 1.49, 1.90, 5.88, 1.99, 2.32, 2.71 h | 6 class-open, 2 mutation-vacuous |
| reviewer seats | 8 (`dispatch/reviewer-2697-*`, one per verdict) | 8 blocked |
| fixer dispatches | 9 dispatch commits on 7 refs (`dispatch/fixer-r10-merge-subject-harden`, `-r4` to `-r9`), plus 3 local seat branches named in merge commits (`seat/fixer-msh-r2`, `-r3`, `-r4`) | the 8 above are their results; round 9 is open |
| guard size | 596 lines at main, 916 at `4aad9c117` (`git show <ref>:tools/policy/agreement.mjs \| wc -l`) | n/a: a size, not a failure |
| regression arm only (reviews 7 and 8) | 2.32 + 2.71 = 5.03 h, round 9 not counted | 2 of 8 verdicts |
| OPEN-AT-BOTH arm (reviews 3 to 6) | 1.49 + 1.90 + 5.88 + 1.99 = 11.26 h | 4 of 8 verdicts; not all loss, because the guard gained (PROGRAM-CLASS rows 12 at main against 144 at the head, review 8's `ev/argv_seam.txt`) |

**P(recurrence)**, estimated:

- Basis: one regression-against-base on a guard PR found by review (#2697), against at
  most 29 guard-touching merges in 30 days (section 4).
- P is about 1 in 29, or 3.4 % per guard PR. This is an estimate from one instance,
  not a measured class frequency. No class records it.
- Expected loss per guard PR: 0.034 x 5.03 h, about 10 min.

**Candidate countermeasures**

| id | change | standing cost | state addressed | passes? |
|---|---|---|---|---|
| M0 | nothing | 0 | none | loses about 10 min per guard PR (5.0 h a month at 29 PRs), and the loop that produced it has no stopping rule |
| M1 | `fixer.md` step 3 and `fix-review.md` step 2: a change to a refusing guard measures its refused set at both ends over a **generated** corpus. `refused(base) \ refused(head)` is printed, and each member is either repaired or dispositioned by name as an intended narrowing. Policy, owner approves | about 3 s per guard version (planted mode: 12.1 s for 4 loads), run by the fixer and the reviewer: under 10 s per guard PR, under 5 min a month | (c), the unit | **passes**: under 10 s against about 10 min per guard PR |
| M2 | a tracked tree-planted differential per lexical guard, beside its self-test (`differential.mjs planted` is the shape for the merge-subject guard) | the same seconds; per-guard adapters for the three Python guards are unmeasured | (c), the instrument M1 needs | passes for agreement.mjs. The Python three are not costed: the builder's to measure |
| M3 | a split rule for class-open past round 3 in `fixer.md` beside the `claims` one. Policy, owner approves | 0 s | the (a) sub-finding | owner's call. A split at round 4 would have saved at most the reviews 5 and 6 cycles (7.87 h). The round-8 split shows it cannot reveal a regression, so it cannot replace M1 |
| M4 | brief-time domain: a lexical-guard group's brief names its acceptance corpus as a generator, not "for example ...". The orchestrator's brief template, not policy | 0 s | (c), the unit, at dispatch | passes; it is M1's corpus named before the fixer starts |

M1 and M4 together close the cause: a generated corpus at both ends, named before the
work. M2 is the instrument they need for this guard. M3 is recorded as the owner's
call, not a pass.

## 6. Recommendation

1. **M1 (policy, owner approval; the request states state (c)).** Draft for
   `fixer.md` step 3, after "reads flat at both ends":

   > A change to a check whose output is a refused set — a guard, a lint, a scan —
   > measures that set at the base and at the head over a generated corpus, not the
   > tree alone: print `refused(base) \ refused(head)` and dispose each member
   > (repaired, or an intended narrowing with its reason). A tree with no instance
   > reads flat at both ends and measures neither direction.

   Draft for `fix-review.md` step 2 to match: a non-empty, undispositioned
   `refused(base) \ refused(head)` is `blocked <sha> class-open: regression against
   base`. Do not land this here (`CLAUDE.md`: policy changes only with the owner's
   approval).
2. **M2 for this guard is already owed to round 9.** The round-9 brief's acceptance (1)
   is a differential "over the finder's harness corpus plus the reviewer's cases ...
   and your own generated lines for the closer-in-lead class". That is still a
   hand-bounded corpus. At `4aad9c117` the tree-planted corpus returns 54
   `main_not_head` lines outside the closer bucket (section 1). The forward-carry is in
   this PR's body, for that brief.
3. **M4 (the orchestrator's brief template, not policy):** a lexical-guard group's
   brief names its corpus generator and its base-versus-head differential as
   acceptance from round 1.
4. **M3:** for the owner. It is recorded with its cost, and it does not substitute for
   M1.

**Demonstration owed by `root-cause.md` step 5**, for the check-shaped M1 and M2:

- Fails on the defect: planted mode at `09b1d002c` and `4aad9c117` prints
  `main_not_head=8484` and `8070`.
- Passes once fixed: there is no fixed head yet; round 9 is open. As a stand-in, the
  null control at `origin/main` against itself prints `main_not_head=0` over the same
  82735 lines.
- Does not go green by skipping: the corpus size is printed (`corpus planted=82735`,
  `files=289`), so a run that read nothing reads `planted=0`, not a pass. The script
  exits 2 on a missing mode or base.

The builder of M2 owes the head-passes run against round 9's head.

## 7. Not covered

- Round 9 was running while this was written. Its outcome, and whether its
  differential is hand-bounded, are not measured.
- The 54 and 56 `other` lines are counted and bucketed, not classified by hand.
- The three Python guards in section 4 were not run under a planted differential. Only
  their shape and their lack of a base-version comparison were read.
- #2711's class-open verdicts were not checked for a regression against base.
- The seat counts are ref listings at the time of writing (`git ls-remote` and
  `for-each-ref`). They are not figures of the tree and cannot be re-derived at a SHA.
- P(recurrence) rests on one instance.
