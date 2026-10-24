# BLOCKED: carry index 6 (pool claims) has no tracked code path to change

Status: carry index 6 of R10-FLY-CLOUD-SETUP-TOOLCHAIN (roster db3e513ec) is
**not implemented**. The code head (handoff/r10-fly-cloud-setup-toolchain at
eec03e0ee65e) and BODY.md are unchanged. Nothing else was pushed. The fixer is
stopping to ask under `fixer.md` step 17 ("a fix that cannot be sound within
[the scope] stops and asks the orchestrator").

## Why

1. **There is no "pool path" in `cloud_dispatch.py`.** The carry says "In
   cloud_dispatch's pool path: (1) when it appends a line for a topic ...".
   No tracked code appends to `POOL.txt` or touches `claim/*`:
   `git grep -n -i 'pool\|claim/' origin/main -- tools/audit/seat/cloud_dispatch.py`
   prints nothing, and no remote branch's copy of `cloud_dispatch.py`
   contains `pool` (loop over every `refs/remotes/origin/*`, `git show
   $b:tools/audit/seat/cloud_dispatch.py | grep -qi pool`: no ref printed; the
   control, `grep -i pool` over `tests/mutation_table.py`, finds
   `--pool-seconds`). The only code that writes `POOL.txt` is the
   orchestrator's session scratch (`orch/r10s6/dispatch-STATE.md` and
   `sweep.md` on `wip-sync/orchestrator-scratch` 8ee173fbd), which already
   states both rules by hand (sweep.md: "a claim older than 90 min with no
   movement ... delete the claim and refire"; "Never hide a push error with
   2>/dev/null").
2. **Building that path is what triage P50 rejected.**
   `dev/programme/triage/s6-batch2.md` "P50: cloud seat pools", Verdict:
   REJECT, costed exactly this surface ("`cloud_dispatch.py --pool` writing
   `POOL.txt` and the atomic `claim/<session>/<topic>` push protocol, a
   `prune_refs.py` rule for `claim/*` ... plus a standing change of rule") and
   ruled "The pattern remains available to an orchestrator as session scratch
   ... Reopen only if the P-A stub lands and a per-seat fire still costs a
   measured, material share of a round."
3. **The ruling the carry cites is unreadable.** `dev/programme/triage/s6-batch4.md`
   is not on origin/main; the one commit holding it (5e469beeb, on
   `wip-sync/ext-wt-8aef46d4`) has no `S6-V1`/`S6-V2` section
   (`git log --all -S'S6-V1'` finds only the roster carry and this dispatch).
   So nothing readable reopens P50.
4. **Scope.** The group is XS, one file (`tools/audit/seat/cloud-setup.sh`);
   a new `--pool` path in `cloud_dispatch.py` with a claim-pruning rule, two
   control arms and two mutants is P50's M-cost instrument in a fly-in.

## What would unblock it (orchestrator's call)

- Land `s6-batch4.md` with S6-V1/S6-V2 reopening P50 (it must say which
  function owns the append: a new `cloud_dispatch.pool_append()` beside
  `_publish`, or a separate `tools/audit/seat/pool.py`), and either re-carry
  this item to its own group or confirm it rides this PR; or
- drop carry index 6 from this group and keep the two rules where they live
  today, in the orchestrator's sweep scratch.

Merging origin/main into the head (the brief's first step) was done locally
only; it is not pushed, because a head moved without the carry would restart
the review for no change of substance.
