Delivers the #2721 residual (not a closing keyword: the roster group does not list the issue, so `preflight` refuses `Closes`; the orchestrator closes it on delivery). Residue of R10-ORCH-LEDGER (#2671): five carries, each with its control. origin/main at 7e8939d38ced (unmoved since the last `tools/pr/prepr.sh` run, so no second run), measured 2026-11-06.

- Carry 0 (`cloud_relay-8` plant): no change owed at this base. The plant's pattern occurs once and the mutant is KILLED (`survivors=0`); the carry described the #2671 head, not main.
- Carry 1: an imported `verdict-unposted` now keeps the sha its journal line names (`ledger._import_log`), and `fold` closes it on a read-back naming that sha (the native row still closes on its first line). A sha-less import stays owed; `ledger.py close verdict-unposted <pr> -` is its closer.
- Carry 2: `ledger.escalate` takes the epoch of the newest `fix/`/`handoff/` pull-request opening; a tip committed at or before it is backlog and escalates nothing, only a later arrival ages (as `pulse.py` does). The tick reads the opening with one `gh pr list --state all` (`Tick.last_opening`); an unreadable listing is reported UNREADABLE and keys on age alone (over-owes, fails safe).
- Carry 3: `ledger.py dispose` into a non-default home prints one stderr line naming it and the default the tick reads; the row is still written.
- Carry 4: `bus.sh orphans` gets the level's merged-PR arm: a pull request of the topic merged at or after the tip's commit time reports `merged-pr=N` instead of ORPHAN. The listing is `gh pr list --state merged` (`HPO_BUS_MERGED` stubs it); unread, it says so on stderr and the refs-only answer stands, which can only add ORPHAN lines.

Alternatives that lost: carry 2 keyed in the relay's level lines (the relay has no opening time; the tick already holds the PR reads); carry 4 recorded as "may differ" (the relay's level closes the case, and one owner of the answer is sounder than two).

## Head

f699d5eb465c5ed560480a7ab9715f25964347cd

## Mutation proof

New plants in `tools/audit/seat/r10_ledger_mutants.py`, each run with `python3 tools/audit/seat/r10_ledger_mutants.py <plant>`: `L33_imported_verdict_unclosable` fails "an imported verdict-unposted closes on a read-back naming its sha (carry 1)"; `L34_backlog_escalates` fails "a tip committed before the last opening is backlog..." and "a tip committed exactly at the last opening is backlog"; `L32_dispose_home_silent` fails "dispose into a non-default home names it on stderr and still writes (carry 3)"; `B4_orphans_merged_pr_ignored` fails "a handoff whose pull request merged at or after its tip is merged-pr, not ORPHAN". `L3` and `T4` anchors retargeted; both still killed.

## Null control

Each self-test carries one: an imported row read against another sha stays open; `last_open=None` equals the old output; dispose into the default home prints nothing and writes; a pull request merged before the tip leaves the ORPHAN line; an unreadable merged listing says so and keeps the ORPHAN. Re-measurement of carry 2's replay (`dev/audit/harnesses/pulse_replay.py`) and of the `bus.sh orphans --min-age-h 24` backlog count needs `gh`, absent in this cloud seat: not taken; the control here is the self-tests above, not the live figures.

## Figures

- `python3 -I tools/audit/seat/ledger.py --self-test` -> 85 checks, 0 failed
- `python3 tools/audit/seat/orchestrator_tick.py --self-test` -> 274 checks, 0 failed
- `bash tools/audit/seat/bus.sh --self-test` -> 135 checks, 0 failed
- `python3 tools/audit/seat/r10_ledger_mutants.py --self-test` -> 146 checks, 0 failed
- `python3 tests/structure.py` -> STRUCTURE RATCHET PASSED
- `bash tools/pr/prepr.sh` at the tree of this head -> rc=0

## Red checks

none

## Forward-carry

none

## Friction

none
