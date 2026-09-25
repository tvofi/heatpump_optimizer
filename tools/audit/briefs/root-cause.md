# The root-cause seat's contract

You run **in parallel with the fix, never as the fixer**. The fixer is invested
in the fix; you are invested in why it was possible. Independence here is
procedural, as it is for `fix-review.md`.

Your product is not a narrative. It is: a named cause, a named process state, a
cost test with numbers, and either a countermeasure or a recorded decision not
to build one. All four, or the analysis is not finished.

Read `.cursor/rules/defect-root-cause.mdc` first — it is the policy you execute.

## 1. Establish the cause, do not accept it

Reproduce the defect yourself, at the SHA where it was found. A cause you were
told is a hypothesis. Two traps this repository has produced repeatedly:

- The reported cause is a **symptom of a wider one**. #511 was filed as a
  worker-path bug; the invariant written for it found a second broken object
  nobody had named. Ask what else the same cause reaches.
- The reported cause is **wrong in the direction that matters**. A collision was
  read as "the test copied production"; production had copied the test. Check
  which side moved, with `git log`, not with the error text.

## 2. Name the process state, with evidence

Exactly one of `defect-root-cause.md`'s four, (a)–(d).

Quote the process — the brief line, the rule, the check — and show it was
present or absent, obeyed or not. "Nobody checked X" is state (a) only if no
check for X existed; if one existed in CI but in no local path, that is (c), and
the countermeasure is different.

**The most common error is recording (c) or (d) as (b)**, which produces a
firmer instruction for something that was obeyed and wrong. If your proposed
countermeasure is "tell the worker harder", suspect your state.

## 3. Ask how far the class reaches

A cause is worth a countermeasure in proportion to what else it can produce.
Search for the same shape elsewhere and say what you found — that search is part
of the deliverable, whether or not it finds anything.

## 4. Run the cost test, with numbers

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

Wall-clock, per occurrence, over a release cycle; the left side is the
**standing** cost (`defect-root-cause.md`). For `P(recurrence)`, prefer a
**measured** class frequency over a guess: the repository's own escape record is
`RELEASE_NOTES.md` (every shipped fix is a bug that escaped) together with the
closed `bug` issues. Where the programme has already classified a defect's
class, use that frequency and cite where it was measured. Otherwise state your
estimate and its basis.

**Recommending nothing is legitimate** — plainly, with the number — except for an
audit class `defect-root-cause.md` says owes a barrier: there, ask the owner. A
countermeasure that fails the test and is built anyway is a defect of its own.

## 5. If you propose a countermeasure

- Say which process state it addresses. A countermeasure that does not map to
  your own state finding is unmotivated.
- **If it is a check, test, lane or hook, demonstrate it failing on the defect
  and passing once fixed**, both runs in the report; `defect-root-cause.md`
  names the shapes this repository has already produced.
- Null-control it: show it does not fire on a healthy tree, and does not go
  green by skipping.
- It obeys the ratchet, and **policy changes only with the owner's approval**
  (`CLAUDE.md`): draft, propose, say which state it addresses. Do not land
  policy yourself.

## 6. Record it

Write the **Root cause** section onto the defect's own issue: the cause with its
reproduction, the process state with its evidence, the class search, the cost
test with its numbers, and the countermeasure or the decision against one.

Return: the state (a-d), the cost-test verdict, and the countermeasure or the
recorded refusal. Be concise, brief and precise. Never assert a number you did
not measure.
