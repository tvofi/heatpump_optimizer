A cloud reviewer's verdict was refused by the relay twice on 2026-10-21 (probe/rev-2544-131f9c75, probe/rev-2513-e19a37e0, both merge verdicts): the reviewer prompt in `tools/audit/seat/cloud_dispatch.py` said "put the evidence in `ev/`" but never that a file there must contain the full 40-hex head, which `bus.sh push-verdict` (`grep -rqF "$hsha" "$ev"`) and app_approve's evidence gate require. The prompt now states the requirement as bus.sh tests it (a file under `ev/` containing the full head, e.g. `ev/HEAD.txt`) and `--self-test` asserts the rendered prompt carries it. cloud_relay.sh is unchanged: it already surfaces push-verdict's refusal "no file under <ev> names the head <sha>", which names the remedy; the relay does not synthesize evidence, as the reviewer's evidence is the reviewer's. Alternatives rejected: relay writing ev/HEAD.txt itself (fabricates evidence); loosening bus.sh (weakens the gate).

## Head

a90d2bc1490db396d6e432e9f9bee7144b46cb6f

## Mutation proof

Removing the new prompt clause (sed on the "make at least one file under ev/ contain the full 40-hex head" text) turns `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` red: "FAIL the reviewer is told a file under ev/ must contain the full head", 30 checks, 1 failed.

## Null control

The unmodified fix tree: the same self-test is 30 checks, 0 failed. On origin/main the clause is absent from the rendered prompt, which is the defect (the two refused refs carry no head-naming file).

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
