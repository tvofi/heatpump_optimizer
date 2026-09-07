---
description: How to run the scoped gate, hold the gate lease, and never re-derive closures off Linux
paths:
  - "tests/**"
  - "custom_components/**"
---
# Running the gate

`./tests/run.sh` is unscoped and long. On a branch, what you almost always want
is the scoped gate against your merge base:

```
GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh
```

`/tmp/hpo-gate.lock` serialises anything that runs `tests/stress.py`, which
measures the machine while it solves and is wrong if something else is running.
Take it for a full or stress-selecting run; a scoped run that does not select
`stress.py` does not need it. Use `tests/gate_lock.py` — not `mkdir` and a
shell pid:

```
python3 tests/gate_lock.py take --label <your-label>
HPO_GATE_LOCK_LABEL=<your-label> GATE_SCOPE=auto GOLDEN_MODE=drift \
  GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh
python3 tests/gate_lock.py renew --label <your-label>   # between commands
python3 tests/gate_lock.py release --label <your-label>
```

The owner file carries your label and an `expires_at` lease (30 minutes, above
the longest observed gate). Every script under lock renews it; an expired lease
or an abandoned hold (`holding` marker, no live flock) may be taken without
forensics. `run.sh` holds `flock` for the gate run so a crash drops flock and
a waiter can take immediately — the lease covers the window between commands
when nothing holds flock (#404).

## Never run a full `tests/derive_closures.sh` off Linux

The union that lets a
Darwin recording *grow* a node closure without dropping files only Linux
`strace` saw lives inside `closure.py`'s `if partial:` branch — and `--single`
is what passes `--partial`. The full path does not, so a full re-derivation on
this box **replaces** the Linux recordings wholesale: `card_drift.mjs` measured
**66 scripts → 6**. Worse, the refusal message you will be reading when you
reach for it says *"Regenerate with tests/derive_closures.sh"*, with no
`--single` and no platform caveat. Use `--single` on the one script.

Node lanes (`tests/card.mjs`, `tests/card_drift.mjs`) record on Darwin via
`node --import tests/node_fs_trace.mjs` (Node `fs` / loader, not `strace`).
`--single` of an existing node script **unions** into the committed list;
it cannot shrink a Linux `strace` closure. Python closures re-derive locally
as before. Do not Darwin `--single` a CI `UNDER-SCOPED` **while the autofix
job is green and its summary line says `changed`** — it already has the Linux
recordings and the commit is coming. Once that job goes red it has told you it
did not merge them, and re-deriving the script its summary names is then the
only thing that moves the PR. Green on `skip-not-allowed` is the third case:
the loop guard fired after the bot's own push, so no second commit is coming
either.
