# `roster_sync.py`

- `roster_sync.py` — derives the factual half of a roster group's `resume`
  from pull-request state: a merged pull request on the group's branch makes
  it `done` at the merge commit (and routes the body's `Carry: <GROUP>` items
  to the destination's `carry`), an open one makes it `in-progress` with
  `resume.pr`. Branch matching is the topic rule its docstring states; a head
  two topics match is the longer one's. It prints `RECORD-INVALID <group>` for
  a `resume.commit` naming no commit or several, or a done group's off
  `origin/main` -- a finding, never a refusal. When:
  every `state_docs.py beat --apply` pass runs it; run it alone to see what a
  pass would write. Dry run by default; `--apply` writes through
  `roster_edit.write_roster()`, the one write path, lint gate and push-race retry. Refusals: an
  unreadable pull-request read (never "no mismatches"), a `Carry:` to a done
  group, `--apply` with `--roster-file`; a human disposition (`deferred`,
  `refused` and every stage outside `DERIVABLE_STAGES`) is never rewritten,
  and no pull request is no evidence. `--self-test` drives it offline over a
  recorded `--pr-state`; `r10_roster_sync_mutants.py` plants its predicates.
