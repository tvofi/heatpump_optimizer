# `review_packet.py`

- `review_packet.py` — the fix reviewer's packet at the frozen head: three-dot
  diff (with `--reviewed-head <rh>`, which `bus.sh dispatch` and
  `cloud_dispatch.py --role reviewer` pass on, a later round's `git diff <rh> <head>`
  and the verdict naming `rh` instead; a first round, an `rh` not the head's
  ancestor or one no verdict names keeps the three-dot diff and says which), the head's check runs as read (red, pending, `none` or green, with run
  ids), `carry_audit.py` and `figure_lint.mjs` at the head, the finder's
  harness at both ends when one is named (`--harness`, at the base and
  untouched by the diff, or `--harness-file` outside the tree; `none named`
  and `not run` otherwise), and the mutation-ledger diff. When: through
  `bus.sh dispatch`, which runs it in the checkout it is dispatching for; a
  cloud reviewer, whose dispatcher's copy is a path on another machine,
  renders its own from its dispatch prompt. Refusal: carry-audit, a `## Head`
  not naming the head, a `tests/structure.py` refusal at the head merged with
  main, an unanswered concluded red, a required context concluded failure
  that `merge_train.py classify --pr` reads RED or cannot read (APPROVAL-OWED
  prints the `approval-owed` advisory instead, P345; WAIT or GREEN prints
  `required-wait`/`required-green`, #3379: classify decides, as in `bus.sh`), a host path, a hot file shared with an open pull request holding an
  unboarded merge verdict, or a `fix/<t>` head lacking its `handoff/<t>` tip
  (`handoff-not-applied`), a body line citing a carry as landed that the roster ref lacks at the cited sha (`carry-landed`), or an `instrument-self-tests` step red at the head and not at the merge base (`introduced-red`, one line per INTRODUCED step or timeout, by `merge_train.introduced_at` through `ci_facts`: one filtered check-run read and one job-step read per side, an unreadable one or a job still running refusing; R10-INTRODUCED-REDS-BARRIER); a pending check never refuses. A `head-note` refusal names the repair (`update_pr.sh`). The packet closes on the `carry_audit.py check` self-audit a reviewer runs before its verdict. `handoff`, run by
  `body_push.sh` before a PR body is pushed, refuses the structure and
  hot-file and `carry-landed` signals and `brief-carries` (a roster carry the body never names
  as `Carry N`). A refusal still
  WRITES the packet, so a held dispatch never withholds the evidence, except
  a host path, which writes nothing because the packet carries the diff.
  Unavailable (rc 3, `UNAVAILABLE`) is a different outcome: the seat cannot
  read the packet's inputs (no checkout, no `gh`/token, a missing tool, an
  unwritable `--out`), so it writes nothing and `dispatch` degrades.
