# R10-RCA-CLASS-OPEN: the reviewer finds the next spelling of a class the change left open (#2950)

The root-cause record for the recurring-friction key `class-open` (#2950, verdict
class), which `R10-RCA-FRICTION-RESIDUE.md` section 6 measured at 6 PRs / 13
entries (#2784) and left with "the countermeasure refusal stands".

**Merge base and window.** Measured on 2026-11-06 at `origin/main`
`7e8939d38`; window `v7.0.4..origin/main` (tag `b448d26063cd`), 517 merged
PRs, 450 with a parsable verdict. The earlier record's 5.2-day window is a
control, not a source.

## 1. The count

`node tools/policy/policy_lint.mjs --stats --since v7.0.4`: `class-open` **32 PRs
/ 56 entries** (threshold 3), against 6 / 13 in the earlier record's window.
Read comment by comment, the 56 entries are 55 distinct heads (#3223's last
verdict was posted twice on the same head) on 32 PRs, so **23 repeat rounds**:
the reviewer blocked the same PR on `class-open` more than once. Twelve PRs
hold 35 of the 55 (#2697 6, #2925 5, #3085 4, #3049 3, #3223 3, and #2711,
#2819, #2872, #2989, #3048, #3170, #3218 two each); 20 PRs hold one.

PRs, by search over the window's merge list then a first-line read of each
`blocked <sha> class-open:` comment (the search matched 34 PRs; #2698 and
#2798 name the word elsewhere than as the verdict's class, so 32 remain,
equal to the histogram): #2697, #2706, #2707, #2711, #2770, #2819, #2853,
#2872, #2887, #2903, #2915, #2925, #2933, #2989, #3006, #3016, #3048, #3049,
#3055, #3062, #3073, #3085, #3089, #3090, #3169, #3170, #3174, #3181, #3186,
#3191, #3218, #3223.

## 2. What the entries say

Every first line names a *sibling spelling or site the change left open*, not
a defect in what it changed:

- Guards over text shapes, where the input space is open: #2697 (a merge-call
  parser, six rounds: `gh  pr merge` double-space, quoted arm, case-arm writer,
  wrapped argv), #3049 (parent-command redaction: space-delimited flags, then
  glued `-cCODE`/`--eval=CODE`, then `-W/-X` values), #3048 and #3062 (a
  change-history lexicon: four passages, then more in other docs, then
  translated strings), #3223 (`seat-gh` blocking `issue comment 201`, then
  `issue close --comment`, then `api` writes with case variants), #3055
  (`bare_array.py` a never-empty reason after a mut marker).
- Deletion and race guards over many sites: #3085 (`prune_refs`, then
  `worktree_gc.sh` classes A, B and C, each a ref or HEAD that moved after
  the read), #2989 (`open_pr.sh` two failure paths), #3089.
- Production-code siblings: #2819 and #2872 (two code paths with the same
  threshold or derate), #2887, #3006, #3170 (host-zone checks under other
  zones), #3218.
- Grader and key coverage: #2925 (five files outside the graders key, four
  rounds).

Of the 55 distinct entries the guard-and-lexicon shapes (nine PRs: #2697,
#3049, #3048, #3062, #3223, #3055, #3085, #2989, #3089) hold **23**, and
**14 of the 23 repeat rounds** (#2697 5, #3085 3, #3049 2, #3223 2, #3048 1,
#2989 1), counted per PR from the distinct heads above.

## 3. Named cause

The fixer closes the instances the finder named and the class by *examples*:
for a guard over a space of spellings (shell syntax, flags, option forms,
case, quoting, refs that move), the fixer's enumeration of the class is
manual, and the reviewer's adversarial enumeration is the first one that is
independent. Each reviewer round produces the next sibling because neither
side holds a *generated* corpus over the space: the fixer's harness is the
finder's harness plus the ones the fixer thought of, and `fix-review.md`
asks the reviewer to probe the class (step 10), which it does, once per
round, by hand.

This cause is **checked against the alternative** that class-open is the
reviewer's vocabulary for any rework: it is not. The other 23 of the 32 PRs
are not guards (for example #2819, #2872, #2887, #3006, #3170, #3218, #3174,
#3186, #2853, #2915), and they hold 9 of the 23 repeat rounds: their siblings are sites in production code or docs, one
round each, and are the ordinary cost of a review finding a second instance.
Only the guard population repeats.

## 4. Process state

**(c)**: the process was followed and did not produce the intended result.
`fixer.md` requires a class sweep and a null control, `fix-review.md` step 10
refuses a class left open, and both were obeyed (the blocks quote the missed
sibling and the fixer's next head covers it). The intended result, a class
closed in one fixer round, is not produced for guards over open spaces,
because a hand enumeration of an open space has no stopping point the
fixer can verify. Not (b): the entries say the sweep was done. Not (a): the
step and the word exist, #2561 taught them. Not (d): nothing changed
underneath it. The rate rose: **6 / 173 = 3.5 %** of verdict-carrying PRs in the earlier
record's window (its section 1 denominator) against **32 / 450 = 7.1 %** here, about twice.

## 5. Cost test

Defect: `R10-RCA-FRICTION-RESIDUE.md` section 2 measured `class-open` at a
median **153 min** from block to next verdict (6 PRs; quoted, not re-timed).
Repeat rounds in the window: 23 x 153 min = **3519 min**; of which guard
shapes 14 x 153 = **2142 min**.

Candidate countermeasure (not built; policy text and a per-PR cost): for a PR
that adds or changes a guard that classifies text by shape (parser, redaction,
allow-list, lexicon), the fixer drives the real guard over a *generated*
spelling corpus (case, quoting, glued options, wrapping, delimiters) and
states the corpus size in the body, and the reviewer's surviving siblings are
added to the corpus. Standing cost: the fixer's time per guard PR, which this
record cannot measure from the window (no PR reports the time its sweep took).
If the corpus costs one review round (153 min) per guard PR, the nine guard
PRs cost 1377 min against 2142 min of guard repeat rounds, so it pays only if
it removes at least 64 % of them. No measurement of the removal rate exists; the closest evidence
is that #2697's six rounds closed only when the parser was rewritten around
the grammar rather than patched by spelling, which is the shape of the
candidate but one instance.

## 6. Decision: recorded refusal, with the numbers, owner informed

The candidate passes the cost test only at a removal rate the window cannot
confirm and changes `fixer.md`, which is policy and capped. Per
`defect-root-cause.md` ("policy changes only with the owner's approval"), this
record **does not land it**: it drafts the wording below and routes the
decision, with the numbers, to the owner. The earlier refusals
(`R10-RCA-FRICTION-RESIDUE.md` section 6; `R10-RCA-HARNESS-FRICTION.md`
section 8: a per-child check) priced 6 PRs; at 32 PRs / 3519 min the same
refusal's price side has moved 5x. It is not reopened as "built"; it is
reopened as "owed a ruling".

Draft sentence for `fixer.md` step 5, if the owner approves:
"A guard that classifies text by shape is driven over a generated spelling
corpus (case, quoting, glued options, delimiters, wrapping) with the corpus
size named in the body; a spelling the reviewer finds is added to it."

**Waiting on the owner's ruling** for that sentence; nothing else is waiting.

## 7. Not established here

- The removal rate is unknown; so is the fixer-side cost.
- The shape split (guard vs production) is by first-line text read, not a
  mechanical classifier; a re-count by another reader may differ by a PR or
  two. The totals (32 / 56 / 24) are the histogram's.
- Whether the twofold rate rise has a cause beyond more guard PRs in the
  round is not established.
