CLOUD PROBE seat for tvofi/heatpump_optimizer, topic r10-arch-docs-study, at head 28d46c4918285d36c409c1fb2f72eb77e04e569e. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: a read-only probe. Measure what the brief below asks against the tree at 28d46c4918285d36c409c1fb2f72eb77e04e569e (`git fetch origin 28d46c4918285d36c409c1fb2f72eb77e04e569e`); change no tracked file and send no code to any ref.
Output: write your result as a body file and run `bash tools/audit/seat/body_push.sh r10-arch-docs-study <result.md>`, which pushes refs/heads/handoff-body/r10-arch-docs-study; that push is the return signal. A return push carries only your own result tokens.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
R10-ARCH-DOCS study step, read-only (the group's roster carry 3, 0-based, on handoff/audit-r10-roster). This seat is a probe: it edits no tracked file, opens no pull request, and pushes only its study note as handoff-body/r10-arch-docs-study (the probe return ref). The note is input to R10-ARCH-DOCS's later fixer; it does not change the figure itself.

The carry, verbatim:
Study step, run first (owner suggestion tvofi 2026-10-22; triage P5 ACCEPT, timing set by the orchestrator to the owner's "at the end of the programme"). Before this group's fixer is dispatched, run one read-only study seat (sonnet, medium effort, git only, spare the API, about 1 seat-hour) for the dev/README.md "Its components" machinery figure alone. Read design note 16954f0c first.
The seat writes a study note with:
(1) an edge table, one row per edge: actor, target, verb ("writes" or "triggers"), and the file:line that performs it;
(2) every current edge marked right, reversed, missing or spurious;
(3) a redrawn mermaid draft with one entrypoint (the owner or orchestrator dispatching a seat), top-down, stores grouped apart from actors, with a one-line legend.
Triage's starting evidence, counted from the mermaid source at #2609 and not yet checked against the code:
- 24 edges, 11 of them touching [target:] nodes;
- at least 6 edges read "is read by": tick-->orch, ledger-.->tick, roster-->docs, model-.->docs, kit-.->model, hold-.->relayh;
- orch has no incoming edge.
The note lands as this group's fixer-brief input. The fixer implements and pins it under the preceding owner-direction carry. It never re-derives the shape itself.

Read at origin/main's tip (the head this dispatch pins). The figure is the dev/README.md section "## The orchestration machinery", its "Its components" mermaid block. Design note 16954f0c: resolve it with git show 16954f0c --stat and git show 16954f0c; if it does not resolve in this clone after git fetch --unshallow --tags origin, say so in the note and continue from the figure and the code. Re-count the triage starting evidence from the mermaid source at this head; do not carry its counts. Every edge row cites the file:line that performs the write or trigger, read at this head. No GitHub API reads are needed: git only.
