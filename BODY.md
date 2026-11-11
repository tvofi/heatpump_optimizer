Triage batch 163 rules queue line 259. It holds one ruling.

- **P577, REJECT: BOTTLENECK-MUTATION-VACUOUS.**
  - Both arms are rejected:
    - (a) the handoff REFUSE on an unanswered `mutant_run --diff` survivor;
    - (b) a per-group mutant command in the fixer brief.
  - Measured on the five blocked heads, `mutant_run.py --diff` generates 2 of the 11 named sites at prepr's default cap of 40, and 3 of 11 uncapped. It would have removed the block on 1 PR of 5 (3425).
  - The other 8 sites are outside its reach: YAML, a shell shim, `tests/`, comprehension and conditional-expression conjuncts, and a path literal.
  - On the two heads where it catches anything, 47 survivors would need answering against 3 named sites. 18 of the 47 mutate the self-test itself.
  - No root-cause seat is newly owed. `R10-RCA-MUTATION-VACUOUS.md`'s tools/ refusal waited on exactly this number, and the number confirms the refusal.
  - Skipping self-test bodies in `mutant_run` is DEFERRED, pending a measured fixer cost or a live owner of the file.

The diff is one file against the merge base: `dev/programme/triage/s6-batch163.md`, the ruling. No product behaviour changes.

## Head

`3b077a16c49765a215dd7cfca2c38130748f57b3`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P577 as REJECT.
- A citation of P577 is refused as "not an ACCEPT ruling (REJECT)".
- With P577's verdict flipped to ACCEPT, the same citation passes (`None`).

## Null control

- P578 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat dbd1ab5b07...3b077a16c49765a215dd7cfca2c38130748f57b3`: 1 file, 1 commit.
- The mutant lists and runs come from `mutant_run.py` at main `dbd1ab5b07`, in copy-tree mode, about 05:05-05:15Z:
  - `--list` at the five heads: 51, 58, 19, 65 and 0 mutants;
  - full run at 3419: 35 of 51 survived, in 116 s;
  - full run at 3425: 12 of 16 survived, in 31 s.
- No API calls.

## Red checks

`none`. The merge base is main `dbd1ab5b07`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
