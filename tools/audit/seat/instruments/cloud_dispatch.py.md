# `cloud_dispatch.py`

- `cloud_dispatch.py` — renders the whole cloud-runner trigger payload
  (`job_config.ccr`: `environment_id`, `session_context` with `allowed_tools`,
  `model` and `sources`, and one user-message event) for a `reviewer`,
  `fixer` or `probe` seat from the PR, the 40-hex head, the bus nonce and an
  optional brief file. The environment id, model and repository come from a
  flag, an overlay JSON (`--overlay` / `$HPO_CLOUD_OVERLAY`) or `HPO_CLOUD_*`,
  never from the tree. `--role R --group G --model M` is the one-call path
  (`dispatch_group()` for a host such as the beat): the brief, topic and
  repository come from the roster at `--roster-ref` (the brief is the group's
  brief, then `After:` its predecessors, then each carry verbatim as
  `Carry <i>:`, `<i>` its 0-based roster index; default the round's roster
  branch, `roster_lib.default_roster_ref`); the head is `--head`, else
  `origin/main`'s tip, never the roster ref's (a reviewer must pass its PR
  head); the environment is the overlay / `HPO_CLOUD_ENV_ID`; a flag it does
  not consume (`--topic`, `--brief`, `--repo`, `--env-id`, `--out`,
  `--publish`) refuses; it renders through the same `publish_seat` as the flag
  path's `--publish` (the payload is that path's byte for byte), publishes
  PAYLOAD.json and PROMPT.md on origin as `dispatch/<role>-<topic>`
  (fast-forwarded, an identical tree adds nothing, a render refusal pushes
  nothing) and prints that ref name, the one line a standing trigger is fired
  with. A published payload's event is a stub, not the prompt (the runner
  echoes the event into the orchestrator): the seat line and the footer ban
  inline, and PROMPT.md at the commit that holds it, pinned by SHA and never
  by the moving ref (PROMPT.md is committed alone, PAYLOAD.json on top);
  `--publish`
  on the flag path publishes to `dispatch/<role>-<topic>`, else
  `dispatch/<role>-rev-<PR>`, the same way; `dev/audit/harnesses/r10_flow_dispatch_mutants.py`
  re-runs its mutants. When: dispatching a seat to the cloud runner;
  paste the printed JSON as the trigger update, or fire the standing trigger
  with the printed ref. The measured shape of a cloud seat:
  every trigger update resends the full ccr and then `run`s it, never a
  patch; the brief is snapshotted at `run`, so it is inlined at render time
  (into the event, or into PROMPT.md at the pinned commit), an edit afterwards
  reaches no running seat, and overlapping runs are fine;
  the toolchain (`PATH` with `/opt/hpo/venv-ci/bin`, `BASH_ENV`,
  `HPO_TYPING_PYTHON`, `OPENBLAS_CORETYPE`) comes from the environment's
  variables, not from a profile the seat sources, so the prompt says only
  that it is on `PATH`; the seat starts off `main` in a shallow clone
  (`git fetch --unshallow --tags origin` first); the return signal is a
  pushed ref: `probe/rev-<pr>-<nonce first 8>` for a reviewer (see
  `cloud_relay.sh`: a cloud reviewer never runs `bus.sh`, whose dispatch record
  lives on the orchestrator's machine and refuses "unknown nonce" anywhere
  else, and a seat may not write a record it did not mint), `handoff/<topic>`
  plus `handoff-body/<topic>` for a fixer, `handoff-body/<topic>` for a probe,
  and a return push carries only the seat's own result tokens: a push
  carrying system-file dumps is refused; the session is reachable one way,
  by `SendMessage` to it, and nothing comes back on that channel. Refusal: a
  head that is not 40 lowercase hex, a reviewer without a nonce or `--pr`, a
  fixer or probe without `--topic`, a missing environment id, model or
  repository, and any home-directory path in the rendered text
  (`ref_privacy.HOME_DIR`, brief included). `--self-test` grades each
  refusal against a rendering that passes, offline.
  Two measured traps when driving the runner: an update and a run fired in
  parallel start the run on the PREVIOUS config, so a launch is update, wait
  for it, then run, sequentially; and, until the pasted setup script writes
  `cloud-setup.sh`'s idempotent profile, the container's `BASH_ENV` puts the venv
  python ahead of the test stubs, so a cloud seat runs `tests/entities.py` (and
  anything else resolving `homeassistant`) with `env -u BASH_ENV`.

Design roles (decision 0014): `--role designer` and `--role design-reviewer`
take the roster group id as the topic (`dispatch/designer-<group>`,
`dispatch/design-reviewer-<group>`); only L and XL groups are accepted. The
designer may push only `design/<group>` (through `bus.sh push-design`) and
opens no pull request; the design reviewer may push only
`design-verdict/<group>` and is pinned to the `design/<group>` tip read from
origin at the dispatch (`--design` on the flag path). Each role's text says so.
A `fixer` dispatch for an L or XL group is refused unless
`design-verdict/<group>` reads `Design review: approve <sha>` at the current
design tip, or `--design-exempt <reason>` names an approved design, pre-study
or prototype already on record. The tick board's `DESIGN OWED:` line lists the
groups whose designer is due.
