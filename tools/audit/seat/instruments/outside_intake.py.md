# `outside_intake.py`

- `outside_intake.py` — lists the submissions outside users make (issues, pull
  requests, issue and review comments, discussions, by any author that is
  neither ours nor a bot) since a cursor, and what each is owed this turn
  (R10-OUTSIDE-INTAKE; tvofi, 2026-11-06). `list` prints `OUTSIDE #N
  owed=triage|answer|reply ...` lines, read from the roster and the thread and
  never from memory: on no roster group and not refused is `triage`; wired into
  a group's `issues` or `fixes` (`roster_edit.py wire-issue`; the group's
  `source` is then set with `set-source <GROUP> outside`, which the plan's top
  tier reads) and unanswered is
  `answer` once the plan page answers; an outside comment newer than every one
  of ours on a disposed thread is `reply`. `answer --issue N` posts the plan
  page link (`plan_public.PLAN_URL`) through `tools/pr/gh_comment.py` with its
  read-back; `refuse --issue N --reason-file F` posts a recorded refusal. Both
  mark the thread, and only a mark in a comment of ours counts. When: the beat's
  `outside-intake` row runs `list` each pass with `--cursor`, and the sweep acts
  on its lines; `answer` is the dispatch seat's, `refuse` the orchestrator's.
  Refusals: a failed read is `outside-intake: UNREADABLE`, rc 2, never a clean
  board; `answer` refuses a thread already answered or refused (none is
  answered twice), one on no roster group, one while the plan page does not
  answer, and a discussion (answered by hand). `--self-test` drives the
  round's three submissions (#3224, #3225, #3226) and their neighbours through
  the real `jq` over faked API answers, and one mutant per predicate
  (`outside_intake_selftest.py`).
