# `state_docs.py`

- `state_docs.py` — one call regenerates the four state docs
  (`plan_table.py`, `merge_throughput.py flow`, `resume_doc.py`,
  `handover_prompt.py`), commits exactly
  their outputs to the orphan ref `handoff/audit-r<N>-plan` at
  `handoff/round<N>/state/`, N the roster's round, and mirrors them to
  `--mirror`. The flow board publishes beside the plan table, so a beat
  pass carries the throughput figures with the plan they explain. When: every state
  beat — it replaces the five hand commands (worktree, copy, commit, push,
  mirror) and runs the generators instead of copying their logic. Dry run by
  default: without `--push` nothing remote is written. Refusals: any path
  outside the four state docs (the write set is checked before a commit
  exists to push; every other path at the ref — a round's evidence — is
  carried untouched), a first commit that would not be exactly the four
  files, and an already-current tip, which is reported and left alone. The
  commit is plumbing over a temp index, so the calling checkout's index is
  never touched.
  `state_docs.py beat` is the same instrument on a loop, and it lives here
  rather than in a session's scratch for decision 0013's reason — an
  instrument the programme runs belongs where a later session can test it. A
  pass reads `--watch-ref` and the roster ref at origin (O17: a roster edit
  moves the state docs as a merge does); when either has moved it refreshes
  the roster ref (so resume fields other seats wrote are visible),
  regenerates and pushes, and when neither has it writes nothing at all.
  With no `--roster-ref` the roster ref is `roster_lib.default_roster_ref`'s. When:
  continuously beside a merge train, since it takes no lock and cancels
  nothing — the state docs are regenerated rather than rebuilt at session
  end. Refusal, and the one that saves you: the tip is recorded ONLY on a
  regeneration that returned 0, so a push the remote rejected is retried on
  the next pass instead of silently dropping that merge from the record.
  `--apply` runs `roster_sync.py --apply` at the start of each pass, before
  the memo check, since a pull request can open or merge without moving a ref
  the beat watches; without it the beat derives nothing.
  `--once` is one pass and returns that pass's code; without `--tip-file` a
  `--once` caller regenerates every time, so give it one to keep the loop's
  memo on disk. `--self-test` drives all three arms offline.
