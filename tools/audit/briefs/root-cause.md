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

Exactly one of:

- **(a) The process did not exist.**
- **(b) The process existed and was not followed.**
- **(c) The process was followed and did not produce the intended result.**
- **(d) The process was sound and its preconditions changed underneath it.**

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

Wall-clock, per occurrence, over a release cycle. The left side is the
**standing** cost — what it adds to every run forever — not what it costs you to
write it. For `P(recurrence)`, prefer a **measured** class frequency over a guess: the
repository's own escape record is `RELEASE_NOTES.md` (every shipped fix is a bug
that escaped) together with the closed `bug` issues. Where the programme has
already classified a defect's class, use that frequency and cite where it was
measured. Otherwise state your estimate and its basis.

**Recommending nothing is a legitimate result.** Say so plainly and give the
number that says so. A countermeasure that fails the test and is built anyway is
a defect of its own.

## 5. If you propose a countermeasure

- Say which process state it addresses. A countermeasure that does not map to
  your own state finding is unmotivated.
- **If it is a check, test, lane or hook, demonstrate it failing on the defect
  and passing once fixed.** Both runs in the report. A check that passes while
  the bug is present converts an open defect into a closed one — this repository
  has produced that shape three times.
- Null-control it: show it does not fire on a healthy tree, and does not go
  green by skipping.
- It obeys the ratchet. If it needs a budget raised, that is the owner's call,
  asked before any push.
- **Repository rules and policy change only with the owner's approval.** Draft,
  propose, and say which state it addresses. Do not land policy yourself.

## 6. Record it

Write the **Root cause** section onto the defect's own issue: the cause with its
reproduction, the process state with its evidence, the class search, the cost
test with its numbers, and the countermeasure or the decision against one.

Return: the state (a-d), the cost-test verdict, and the countermeasure or the
recorded refusal. Be concise, brief and precise. Never assert a number you did
not measure.
