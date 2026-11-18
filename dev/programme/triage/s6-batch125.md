# Proposal triage, session s12, batch 125 (P390)

The rolling batch after batch 124. Facts were read at origin/main, at the round's roster branch and in the seat ledger. The cloud seats'
transcripts are not readable from here.

## P390: a refused body dies with the cloud seat, and the frugal guard in the cloud env

Verdict: ACCEPT narrowed. Part 1 goes to R10-BODY-CONTRACT in a different form: `body_push.sh` keeps a refused body itself, on its own ref, and the
brief gains no step. Part 2, disabling the frugal guard in the cloud env, is DEFER: it is the owner's call, and its cost is uncounted.

**Owner ruling after this entry (tvofi, 2026-11-04, relayed by the orchestrator): "Turn it off in the cloud".** The orchestrator had laid out the guard, the options and a recommendation to keep it on. Part 2's DEFER is closed by that ruling, and the route is the orchestrator's group R10-FLY-CLOUD-FRUGAL-OFF. The figures below stay as read; no count of blocks was taken.

Source: the orchestrator's queue line of 2026-11-04T22:10:46Z.

Instances:
- **Part 1, a body lost or stranded on a `body_push` refusal, in three cases in four days.**

  | case | refusal | result | source |
  |---|---|---|---|
  | #3055 round 3, 2026-11-01 | `hot-file` | "body lost with the container"; a body-only fixer re-fired | seat ledger, 16:53:15Z |
  | r10-closeout-cleanup, 2026-11-01 | `hot-file`, `brief-carries` | stranded in session scratch, not lost | seat ledger, 22:19Z |
  | f-3197-r3, 2026-11-04 | CARRY-MISSING | lost; a second seat rebuilds it | this queue line |

  The rule on each: all three refused before `body_push.sh` reaches its push, so a keep on that path holds all three bodies. The seat time of a rebuild is not measured, but each is one whole body-only seat.
- **Why not the form proposed.** `handoff-wip/<topic>` is the code's fast-forward step ref. A `PR-BODY.md` committed there enters the code's ancestry when a code fixer hands off from it, and `body_push.sh`'s header states the rule that a body never does (`prepr.sh` step 1a). The orchestrator's hand-written brief for #3197's body seat already uses that form, which is safe only for a body-only seat with no code to hand off. A sentence in the render also binds only cloud seats that read it, where the tool binds every caller.
- **Part 2, the guard.** The owner ruled on 2026-10-21 that the guard "should be on but it should allow you to read the policy that binds you", with no cloud exception. Two seats are named, f-3085-r9 and f-3197-r3, with no count of blocks, tokens or turns. The guard's budget is per prompt, and a cloud seat runs on one prompt, which may be the real difference from a local seat. That is a reading, not a measurement: the plugin is not in this repository, and it was not found on this host's plugin path.

Cost:
- **Part 1:** an estimated 10 to 20 lines in `body_push.sh`, reusing its own `commit-tree` path, with self-test arms, inside an existing not-started group. Only a refused push pays: one ref. No standing cost. `body_push.sh` is not a policy file, so it has no `policy_lint.mjs --budgets` row.
- **Part 2's binding cost:** it overrides an owner ruling, on an unmeasured benefit.

Binding:
- **Carry on R10-BODY-CONTRACT:** When `body_push.sh` refuses after the body file exists (predictor, pr-body lint, review packet, carry landing), it first publishes the refused body on an orphan ref `handoff-wip/<topic>-body`, the same parentless or fast-forward `commit-tree` the real push uses, prints `body_push: refused body kept at <ref> <sha>`, and keeps its refusal and exit code. A failed keep is printed and never changes the refusal. Cases on record: #3055 round 3, r10-closeout-cleanup, f-3197-r3. Check before building: that the seat tail and `ref_privacy` allow the ref, that `cloud_relay.sh` and `bus.sh orphans` stay blind to it as they are to `handoff-wip/`, that `prune_refs.py` collects it, and that a successful push deletes it. Arms: each refusal path keeps the body and still exits non-zero; a keep whose push fails leaves the same refusal; a successful push publishes `handoff-body/<topic>` and leaves no keep ref; a refused body is not in the code head's ancestry (null). Mutant: dropping the keep fails the refusal arms. triage: dev/programme/triage/s6-batch125.md#P390
- **Until that lands:** a hand-written brief may keep `PR-BODY.md` on `handoff-wip/<topic>` only for a body-only seat, never for a seat that hands off code.
- **The guard:** off in the cloud env, by the owner's ruling above, through R10-FLY-CLOUD-FRUGAL-OFF. The ruling names the cloud only, so the 2026-10-21 ruling keeps binding local seats.
