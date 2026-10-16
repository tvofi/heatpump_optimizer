---
description: How to run the scoped gate, hold the gate lease, and never re-derive closures off Linux
paths:
  - "tests/**"
  - "custom_components/**"
---
# Running the gate

`./tests/run.sh` is unscoped and long; on a branch you want the scoped gate
against your merge base:

```
GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh
```

**A shallow clone or a stale cached `origin/main` is the environment, not the tree.** `tests/entities.py`'s history
checks go red on a shallow clone; `git fetch --unshallow origin main` clears it, and a cached ref can sit behind the tip (#1693, #1699, #1704).

`/tmp/hpo-gate.lock` holds two leases, and `tests/gate_lock.py needs-lease` answers
which a script takes: `lease`, exclusive, for the scripts that measure the machine
(`tests/stress.py`, `tests/harness_headers.py`), comparable only alone; `slot`, a pool
of four, for the multi-minute CPU scripts (a `closures.json` recording at or above
`SLOT_MIN_SECONDS`); `none`, for the seconds side. The pool is `$HPO_HEAVY_SLOTS`
slots, and `$HPO_SLOT_LABEL` joins one it is inside. First come, first served; a dead
or expired ticket is skipped. A seat that waited one lease period may leave `stress.py`
to CI and name it unrun in the body. That lease, not the tick's count, is nudge.md
§8's cap; hold it by hand only to measure across commands, with `tests/gate_lock.py`, never `mkdir`:

```
python3 tests/gate_lock.py take --label <your-label>
python3 tests/gate_lock.py renew --label <your-label>   # between commands
python3 tests/gate_lock.py release --label <your-label>
```

The owner file carries your label and a 30-minute `expires_at` lease. `renew` exits 75 while another
label waits: finish the run, release, and take again behind it; `run.sh` under `HPO_GATE_LOCK_LABEL` renews itself.

**The mypy census runs here too, when you have the pins.** `HPO_TYPING_PYTHON`
points the ruler at an interpreter carrying them; unset it prints the install
command and what goes unchecked, and an unpinned one fails rather than
measuring (#1091, #1099, #1095).

**A gate run regenerates the D6 claims artifacts under `tools/audit/round4/D6/`**
against the live `VERSION`. `git checkout -- tools/audit/round4/D6` after it,
before any `git add -A` sweeps them into your commit (#1054).

## Never run a full `tests/derive_closures.sh` off Linux

The union that lets a Darwin recording *grow* a node closure without dropping
files only Linux `strace` saw lives inside `closure.py`'s `if partial:` branch,
and `--single` is what passes `--partial`. The full path does not, so a full
re-derivation on this box **replaces** the Linux recordings wholesale:
`card_drift.mjs` measured **66 scripts → 6**. Use `--single` on the one script.
Node lanes (`tests/card.mjs`, `tests/card_drift.mjs`) record on Darwin via
`node --import tests/node_fs_trace.mjs` (Node `fs` / loader, not `strace`).

**`--single` cannot re-record a script whose own checks pin the classification
being re-recorded**: the recording exits 1 until `tests/closures.json` already
lists the files. `closure.py merge`'s refusal names the two-step route out
(#1071).
