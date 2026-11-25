# The root-cause seat's contract

You run **in parallel with the fix, never as the fixer**: you are invested in
why it was possible (`defect-root-cause.md`, "What is owed").

Your product is not a narrative. It is: a named cause, a named process state, a
cost test with numbers, and either a countermeasure or a recorded decision not
to build one. All four, or the analysis is not finished.

Read `.cursor/rules/defect-root-cause.mdc` first — it is the policy you execute.
Long jobs follow `fixer.md`'s preamble: a background task that wakes you.

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

An instance of an audit class that already carries a barrier is not state (a)
because its shape was new: the barrier existed. Name why its unit did not reach
the instance; the countermeasure changes the unit, not the arm count.

**The most common error is recording (c) or (d) as (b)**: if your proposed
countermeasure is "tell the worker harder", suspect your state.

## 3. Ask how far the class reaches

Search for the same shape elsewhere and say what you found — that search is part
of the deliverable, whether or not it finds anything.

## 4. Run the cost test, with numbers

The inequality and its units are `defect-root-cause.md`'s cost test.

For `P(recurrence)`, a **measured** class frequency over a guess: the escape
record, `RELEASE_NOTES.md` (every shipped fix is a bug that escaped) with the
closed `bug` issues, or the programme's frequency for a classified class, cited
where measured; otherwise your estimate and its basis.

**Recommending nothing is legitimate** — plainly, with the number — except for an
audit class `defect-root-cause.md` says owes a barrier: there, ask the owner. A
countermeasure that fails the test and is built anyway is a defect of its own.

## 5. If you propose a countermeasure

- Say which process state it addresses. A countermeasure that does not map to
  your own state finding is unmotivated.
- **Rungs in order: delete, then self-repair, then narrow, a new refusal
  last**; a later rung states why each earlier one is not possible (a product
  check is exempt). A new refusal prints its own repair command and shows its
  refusal count on the last 20 healthy heads (a shadow run) before it gates.
- **If it is a check, test, lane or hook, demonstrate it failing on the defect
  and passing once fixed**, both runs in the report; `defect-root-cause.md`
  names the shapes this repository has already produced.
- Null-control it: show it does not fire on a healthy tree, and does not go
  green by skipping.
- It obeys the ratchet, and **policy changes only with the owner's approval**
  (`CLAUDE.md`): draft and propose; do not land policy yourself.

## 6. Record it

Write the **Root cause** section `defect-root-cause.md` specifies onto the
defect's own issue, with the reproduction and the class search added.

Return: the state (a-d), the cost-test verdict, and the countermeasure or the
recorded refusal. Never assert a number you did not measure.
