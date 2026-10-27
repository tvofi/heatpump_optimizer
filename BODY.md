Triage batch 40's P211 ruling is corrected on main. #2886 merged its pre-correction text at 19:41Z,
and the triage seat's re-ruling -- which withdraws its own "the figure is absent from #2854's body"
claim and splits P211's second arm -- arrived after that PR's review had already returned
`Fix review: merge 0f779c2dc`. A merge verdict cannot cover a change made outside its diff, so the
correction is its own pull request rather than a re-push of a merged branch.

What changes in the ruling, and why it matters downstream: the second arm no longer reads "REJECTED
twice over". The **threshold raise stays REJECTED**; the **lease half is ACCEPTED narrowed** to
`R10-PREPR-CAP` as a second carry. The evidence is #2854's own body, which records `tests/stress.py`
and `tests/harness_headers.py` refused by `tests/gate_lock.py` "when the 30-minute lease lapsed
inside the 85-minute run". Without this correction the roster would carry a rejection of a mechanism
the tree's own record shows firing.

## Head

`1ca755414135d116cc815882b1f8f777053396d8`, three commits on `a0e7664ea` (main): the seat's
corrected entry (`2a92dd656`), two citation fixes measured at that head (`0dfca1cfb`), and one more
(`1ca755414`) after the triage seat showed the first fix had made the entry worse:

- `_cmd_flock_wrap` refuses at `tests/gate_lock.py:1124`; `:1123` only prints. Cited `:1119-1124`
  with both lines named, here and in Instances (6).
- #2854's `updatedAt` is dropped from both citations. It is not a body stamp: it answered
  18:23:17Z, then 19:09:27Z, then 19:39:04Z while this branch was being written, so it moves on any
  activity and each reading is stale within the hour. Citing it twice would give the entry a second
  self-invalidating figure, which is the defect this correction exists to remove. The quoted
  sentence and both refusal strings stay, verified present in `pulls/2854`'s body.

## Mutation proof

The file's only executable gate is `tools/audit/seat/roster_edit.py`'s `triage_refusal`, which
refuses a roster text naming a proposal whose cited entry is not an ACCEPT. Driven directly with a
carry text citing `triage: dev/programme/triage/s6-batch40.md#P211`:

- the corrected file (P211 `Verdict: ACCEPT`) -> `None`: the carry is routable;
- the same file with that verdict changed to `DEFER` -> `dev/programme/triage/s6-batch40.md#P211 is
  not an ACCEPT ruling (DEFER)`;
- the same file with the heading changed to `## P211 (relay P1):` -> `no such entry`;
- null control, a text naming no proposal -> `None` again, so the refuse in arm two comes from the
  verdict and not from the run.

## Null control

The unmodified tree (main `a0e7664ea`) states the second arm as REJECTED twice over, names one carry
and carries no `R10-PREPR-CAP`, no second carry and no Instances item (6): `git show
origin/main:dev/programme/triage/s6-batch40.md | grep -c 'R10-PREPR-CAP'` prints `0`, and the same
grep over this head prints `2`. The gate above passes on both trees for the P211 carry, so the
mutation proof is measuring the verdict line and not the correction.

## Figures

- `git diff --stat origin/main...1ca755414` -- `dev/programme/triage/s6-batch40.md | 61 +++---`:
  1 file changed, 47 insertions(+), 14 deletions(-) -- the same line counts as the two-commit head,
  because the third commit rewrites lines it had already changed.
- `git log --no-merges --oneline origin/main..1ca755414` -- three commits.
- `git diff --stat 1a6365f16:dev/programme/triage/s6-batch40.md a0e7664ea:dev/programme/triage/s6-batch40.md`
  -- empty: main's copy before this branch is the authored head's, so the diff carries the
  correction and nothing lost in #2886's merge.
- `grep -c 'updatedAt' dev/programme/triage/s6-batch40.md` -- `0`.

## Red checks

none

## Forward-carry

The corrected ruling creates a second carry, to `R10-PREPR-CAP` (it owns `tests/gate_lock.py` and
already holds P206's carry). The triage seat files its text on the roster queue and holds both of
this batch's append-carry ops until this file is on main.
Carry: R10-PREPR-CAP

## Friction

none
