# `cloud_relay.sh`

- `cloud_relay.sh` — the orchestrator's half of a cloud reviewer's return:
  `cloud_relay.sh <pr> <nonce> <head40>` fetches
  `probe/rev-<pr>-<nonce8>`, grades it, then runs `bus.sh push-verdict` locally,
  where the dispatch record lives; `bus.sh confirm` follows as for any verdict.
  When: a `probe/rev-*` ref appears after dispatching a cloud reviewer. Refusal:
  a nonce that does not match the verdict's `bus-nonce:` line, a ref whose
  commit subject (`verdict <pr> <head>`) or verdict first line names another PR
  or head, a missing `ev/`, and a ref already relayed (a ledger of
  `<ref> <sha>` under the state directory, written only after `push-verdict`
  succeeded, so a re-pushed ref relays again). `--self-test` grades each
  refusal against a clean ref, offline, with `push-verdict` stubbed. It also
  NORMALISES one shape and logs it (`normalised first line: A -> B`): a blocked
  first line whose tail the reviewer wrapped, `blocked <head> [class: reason]`,
  loses its one outer bracket pair in the relay's temp copy, which is lossless
  and puts the line in `bus.sh`'s grammar (`blocked <head> <class>: <reason>`).
  Chosen over refusing because the relay is the one place the verdict can be
  repaired without a round trip to a cloud seat that has exited, and the
  rewrite changes no word; a bracketed merge suffix, a nested bracket or a
  class outside `[a-z-]+` is refused unchanged (stripping a merge suffix would
  lose text). `cloud_dispatch.py`'s prompt now gives the unbracketed grammar.
  `cloud_relay.sh --watch [--interval N] [--once]` is the orchestrator's poll
  loop, tracked: every N seconds (default 120) it runs the probe arm, which
  lists every `refs/heads/probe/*` with `git ls-remote origin`. A probe ref
  that is not `rev-*` (a probe seat's return, a stray push) is
  `OWED <utc> probe-ref <ref> <sha>` in `<log>.level` until
  `cloud_relay.sh dispose <ref> <sha>` records it handled: a level, not a
  diff, so a missed line is repeated rather than lost, and a disposed ref
  that moves is owed again at its new sha. Every pass REWRITES its kind's
  lines in `<log>.level` and appends none to the log (appended, 2026-10-21: 34757 copies
  of ~281 items once reached the board); `dispose [--log FILE]` drops the
  line at once from the level beside that log (the pass's `--log`), and a
  failed listing leaves the level as it was. It relays each `rev-*` ref+sha
  once, taking the head and full nonce from the dispatch record (`$HPO_BUS_STATE`
  or `~/.zcode/bus`, `pr head thread nonce`). A ref with no record is logged and
  left for a later pass; a refused ref+sha (relay rc 2, a refusal of the ref
  itself) goes to `<ledger>.refused` and is not retried until it is pushed
  again, so one refusal does not repeat every interval. Any other failure (a
  push or a fetch; an HTTP 400 push once left a verdict refused in silence for
  3 h) is retried on later passes, `HPO_RELAY_TRIES` times in all (default 3),
  then refused. A refusal prints `REFUSED <ref> <sha> <reason>` (the relay's
  last stderr line) and is `OWED <utc> probe-refused <ref> <sha> <reason>` in
  `<log>.level` until disposed; one refused before reasons were kept stays
  silent. Run it detached (`daemonize.py`); it uses ls-remote, not the REST
  quota. `--once` is one pass.
  `--confirm` (on `--watch` and on a single relay) keeps going past
  `push-verdict`: after one that passed it runs `bus.sh confirm <pr>
  <review-sha>` (review/<pr>'s tip as `git ls-remote` answers it, when that tip
  carries this verdict's tree: confirm takes only a tip) and appends `POSTED
  <utc> <pr> <sha>` or `OWED <utc> <pr> <sha|-> <why>`, `<why>` carrying
  confirm's last output line, to `--log FILE` (default
  `cloud-relay.log` under the state directory), the file the orchestrator
  reads; two verdicts once sat relayed and unposted for 20 minutes. Confirm
  never runs after a refused relay or a failed `push-verdict`, and those write
  no line (the refusal is printed; `--watch` also keeps it in `.refused`).
  A `push-verdict` refused non-fast-forward (review/<pr> moved under it) is
  run again, three times at most: `bus.sh` re-reads the fresh tip and appends
  the same verdict there, never forcing; a fresh tip already carrying this
  verdict's tree is not re-applied. Both are printed, and so is
  `review/<pr> remote tip <sha>` after the push.
  `cloud_relay.sh pass [--confirm] [--log FILE] [--loop [--interval N]]` is the
  orchestrator's whole beat as ONE entry point (it replaces the session-local
  `relay_watch.sh`): a driver calls it once per tick, or `--loop` repeats it
  (default every 120 s). A pass runs the handoff arm, then the relay arm above,
  then with `--confirm` the confirm arm, then the stuck arm. Stuck arm (a
  report-only trial, triage P163): each branch lock held now whose recorded
  start epoch is older than `HPO_PUSH_STUCK_SECS` (default 900) prints
  `STUCK <branch> <pid> <age>s` (the lock's name, the run's pid) and is
  `OWED <utc> push-stuck <branch> <pid> STUCK ...` in `<log>.level`; a
  released lock is never read. Confirm arm: the ledger is written
  before confirm runs, so a confirm that failed, or a relay by a stale script
  or a call without `--confirm`, was never confirmed later (#2659, #2632). For
  every `review/<pr>` tip the relay pushed (its `bus-nonce:` matches a
  ledgered `probe/rev-<pr>-<nonce8>`) whose tree is not in `bus.sh`'s posted
  record (`posted-signed`), it runs `bus.sh confirm <pr> <tip>`: `POSTED` on
  success; on failure `OWED <utc> confirm-owed refs/heads/review/<pr> <tip>
  tries=<n>/<max>: <last output line>` in `<log>.level`, retried next pass up
  to `HPO_RELAY_CONFIRM_TRIES` (default 3), then owed untried until the posted
  record shows it or `dispose` takes it (`dispose` takes `review/` refs). A tip
  with no dispatch for its PR, head and nonce is owed `undispatched` and never
  confirmed; a tip the relay did not push waits for the orchestrator's own
  read. It makes no `gh` call (`bus.sh confirm` posts).
  Handoff arm: for each OPEN pull request, topic = `headRefName` less `fix/` and
  `-pr`; if `handoff-body/<topic>` and `handoff/<topic>` exist and the handoff is
  not an ancestor of the PR head, it runs `update_pr.sh <branch> <code-sha>
  <BODY.md> <issues>` (issues = the body's closing keywords; BODY.md is written
  to a per-run `cloud-body.*` directory under the state dir and removed after,
  since prepr refuses a body directly in a shared temp root), then
  `approve_held_runs.sh` on the branch, then `bus.sh dispatch <pr> <new head>
  cloud`, and appends `OWED reviewer-fire <pr> <head40> <nonce> <utc>` to the
  log (firing the cloud reviewer stays with the orchestrator). It only updates an
  existing PR, which the soft cap never refuses (it gates only group dispatch).
  Hold: `cloud-handoff-hold` under the state dir lists PR numbers, one per line
  (blank and `#` lines allowed); only the orchestrator writes it. A listed PR
  whose handoff is ahead is not updated and prints `HELD #<pr> <handoff tip>`
  once per pass, so a frozen PR's head stays put while its handoff branch keeps
  moving; removing the number resumes it. A missing or empty file holds nothing;
  a line that is not a plain PR number refuses the whole handoff arm for that
  pass (rc 2, `OWED handoff-hold-malformed` in `<log>.level`), never hold-all or hold-none.
  `cloud_relay.sh held <pr>` answers from the same file (rc 0 held, 1 not, 2
  malformed) for a driver that updates PRs itself.
  Tools tree (P283): the update runs `update_pr.sh` from `<state>/relay-tools`,
  a worktree the relay adds once detached and checks out at origin/main before
  each update when clean, so `pr_tools_fresh` passes however stale the relay's
  own checkout is (never moved: bash reads a running script as it goes). A
  dirty tree is refused by name, left untouched and owed as `handoff-update`;
  one held by a live relay (`relay-tools.lock`, a dead pid's taken over) is
  busy and retried next pass.
  Freeze (R10-FLOW-ROSTER-FREEZE): a PR whose live head is under review is not
  updated either, so roster edits accumulate on the handoff ref and land between
  reviews: a `Fix review: merge <head>` tip on `verdict/<pr>` at that head
  (`HELD-VERDICT`), or a review of that head in flight with no verdict at it
  (`HELD-REVIEW`: a `bus.sh dispatch` record of the PR at the head, the worker
  registry and only it, P288; its nonce prefix and time are printed as
  `dispatch=<nonce8> at=<utc>`). A verdict ref the listing names but the fetch
  cannot read freezes too (`HELD-UNREAD`): it may be a merge at the head. A
  blocked verdict, or one at an older head, freezes nothing. Each prints
  `HELD-<why> #<pr> <handoff tip>[ dispatch=<nonce8> at=<utc>]` once per pass and is
  `OWED <utc> handoff-held <ref> <tip> #<pr> <why>` in `<log>.level`;
  `cloud-handoff-release` (the hold file's grammar) releases a listed PR from the
  freeze, never from the hold, for new work that voids a merge verdict.
  A handoff already inside its PR, or with no body ref, does nothing; a failed
  update is noted in `cloud-handoff-failed` by `<topic> <code-sha>`, owed as
  `OWED <utc> handoff-update <ref> <sha>` in `<log>.level` while that entry
  matches the handoff's tip, and retried only when the handoff moves. An update that
  exits 75 is BUSY (another `open_pr.sh` or `update_pr.sh` run holds the branch's
  `upd-<branch>.lock`, typically the orchestrator's own update of that PR, or an `open_pr.sh` between its two pushes): it is
  not recorded, and the next pass retries it. The update runs in a process
  group of its own, so a signal to the loop's whole group reaches it only
  through the loop's reap, and a KILL to that group leaves it to finish. The
  `handoff-no-pr` lines in `<log>.level` are `ledger.py level`'s fold of
  every `handoff/*` and `handoff-body/*` ref, rewritten every pass: owed unless
  its topic has an open pull request, it is disposed at its sha, or main
  already carries the change (`ledger.py landed`, the one classifier `bus.sh
  orphans` asks too: ancestry, clean merges, reverse-apply, content), one line
  per topic (a body ref rides its code ref's), each
  with its tip's commit time and last opener attempt; a failed PR listing or
  ledger read leaves those lines as they were, since an empty list would make
  every ref look orphaned. Every event the relay owes (`verdict-unposted` at
  each passed push-verdict, `reviewer-fire`, `approve-held-runs`, `dispatch`)
  is opened in the ledger, never appended to the log, which keeps only the
  `POSTED` journal.
  No-return line (triage P-E): each pass, a `dispatch/fixer-<topic>` tip older
  than `HPO_RELAY_NORETURN_SECS` (default 7200) and younger than
  `HPO_RELAY_NORETURN_WINDOW_SECS` (default 172800), with no `handoff-wip/`,
  `handoff/`, `handoff-body/<topic>`, `fix/<topic>-pr` or `fix/<topic>`
  commit newer than it, prints `SEAT ENDED NO RETURN <topic>` and is
  `OWED <utc> seat-no-return <ref> <sha> SEAT ENDED NO RETURN <topic> <age>h`
  in `<log>.level`. Git only; deleting the dispatch ref disposes it.
