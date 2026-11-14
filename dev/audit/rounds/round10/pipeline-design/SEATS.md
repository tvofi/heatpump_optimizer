# Appendix F: cloud seats for the search, on haiku (R11-PRE-PARALLEL-PIPELINE)

Owner, 2026-11-14, verbatim: "Speculative gating could be done by running the
scripts in cloud seats." and "If cloud seats for speculative gating is
feasible, they should run haiku".

## What a seat may and may not decide

A seat's result is a ref, never a check. It may reorder a batch, hold an entry
out of the next proof, or name a suspect. It never merges, promotes, evicts or
posts a verdict, and an absent result after the deadline is no result, never
green. Anything GitHub must show stays GitHub's: `gate` at the reviewed head,
and the proof.

## The one tracked instrument it needs

Feasible on haiku only if the judgement is in a script. That script does not
exist; it is the shadow's second part (a seat-side instrument under
`tools/audit/seat/`, with a self-test). Arguments: the tip sha, the base sha,
full or scoped. It does everything, in this order:

1. runs `tools/audit/seat/cloud-setup.sh --check`; on refusal the result is
   REFUSED env and nothing else runs;
2. fetches the tip and refuses unless the fetched sha equals its argument;
3. checks it out detached;
4. runs one fixed invocation: `GATE_SCOPE=full ./tests/run.sh`, or the scoped
   form `gate-scoping.md` gives, against the base sha;
5. takes the exit code and the failing script names from `run.sh`'s own
   summary lines;
6. reports the scripts on a fixed list as INCONCLUSIVE itself: the
   value-bearing golden scripts (the seat pins `OPENBLAS_CORETYPE`, the hosted
   runner does not, so equal floats are not shown) and closure recording
   (`strace` in the seat's container is unverified);
7. appends the result to a ref named for the tip sha and prints one RESULT
   line.

Not run by a seat, and so not covered by its result: CodeQL, the environment
matrix, the jobs that call the GitHub API, and the instrument self-tests and
policy lanes that are jobs of governance.yml and not scripts of `run.sh`.

The seat's prompt, fired through `cloud_dispatch.py`'s probe role on a haiku
model, then holds only: the repository source; that one command with literal
shas; "run it, wait until it exits, reply with its last line verbatim"; "if it
prints REFUSED or has not exited after the stated minutes, reply with that and
stop"; and four prohibitions: no other command, no edit, no re-run, no reading
of a red.

## Where it helps, and where it removes the gain

| use | effect | figure |
|---|---|---|
| search of a red range (one seat a prefix, all at once) | the culprit is named in one seat wall instead of two to four proof walls | main's worst trail at a 60 / 75 / 105 min proof: 7.20 / 19.04 / 34.34 h with FULL-proof bisection, 6.20 / 7.63 / 15.77 h with seat search (`COST.md` T-f, T-s) |
| pre-proof of the next batch while a proof runs | a predicted-red entry is held out of the next proof | not replayed: 6 culprits in 215 entries leave little to predict |
| a gate before a successor starts from a landing | removes the risk of building on an unproved parent | costs the seat wall: the saving falls from S-i to S-ig, which is day 1's own figure at a 45 to 75 min proof (S-1). With this gate the integration branch has no wall-clock edge over day 1 except under load |

Under day 1 alone the first row still applies: a red batch proof is searched
by seats instead of by further batch proofs.

## Cost a run (estimates, none measured on a seat)

A FULL tip: 60 to 70 seat-minutes, from the CI job `fast (3.14)`'s median of
55.2 min in `tools/plan/durations.json` plus checkout and the environment
check. A FULL proof on GitHub: 197 runner-minutes over 39 jobs (the s12
study). Searching a red range of 12: eleven seats in one wall, against four
proofs in four walls.

## The three measurements the shadow takes

1. Agreement between a seat's result and GitHub's `gate` at the same sha,
   false green and false red, by failing script. A false green on any script
   not on the INCONCLUSIVE list cancels the seat's use as a successor gate.
2. The seat wall for a FULL and for a scoped tip.
3. The share of fires that end with no result ref.
