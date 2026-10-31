`tools/audit/seat/bus.sh orphans` died on macOS bash 3.2 under `set -u` (`arms[@]: unbound variable`) whenever neither `--no-ancestry` nor `--no-content` was given, so `pulse.py`'s opener arm read UNREADABLE and orphaned handoffs were invisible (triage P303). Fix: the ledger.py call uses `${arms[@]+"${arms[@]}"}`. Class barrier: `tools/audit/seat/bare_array.py`, a static rule over every tracked `tools/**/*.sh` (a file with `set -u` may not expand a bare `"${a[@]}"` unless guarded or the line carries `# never-empty: <reason>`), pinned in `tests/entities.py` and run as a governance step. CI's bash 5 expands an empty array cleanly, so a run-time row would pass on the defect; the rule is therefore static. Design choice stated: a file without `set -u` is not judged (the sourced `pr_args.sh` is therefore guarded or marked by hand, see Figures). Alternative rejected: plain variables in bus.sh (the file's own rule) lose the two-flag list the call forwards; the guard is the smaller change.

## Head

5fa9275cc00e187a665624979e8c70e0dbaad461 (origin/main at 0cae227c3 merged, `prepr.sh` rc=0 at this head; main unmoved since).

## Mutation proof

Mutants of `bare_array.sites`, run in scratch on the real source:
- drop guard recognition (`if not ...endswith("${name[@]+")` replaced by `if True`): the guarded form `f ${arms[@]+"${arms[@]}"} x` under `set -u` is refused (1 site), red on `bare_array: the guarded form passes (control)` and the self-test's "the guarded form passes".
- drop the check (`sites` returns `[]`): the base line `f "${arms[@]}" x` is let through, red on `bare_array: the base bus.sh call is refused`.
`tests/entities.py` rows: "no tracked tools/**/*.sh script under set -u expands a bare ...", "bare_array: the base bus.sh call is refused", "...guarded form passes (control)", "...allow-marked never-empty site passes (null)", "...a file without set -u is not judged (null)", "...its own self-test passes".

## Null control

Failing test first: at the base, `python3 -I tools/audit/seat/bare_array.py --check --ref 3759d49a5` lists `tools/audit/seat/bus.sh` (line 654 at that base; 649 in the triage's older base). At this head `python3 -I tools/audit/seat/bare_array.py --check` prints nothing, rc 0. Controls driven by the self-test: guarded form passes; `# never-empty: <reason>` passes; a marker with no reason does not excuse; a file with `set -e` only is not judged; a guard on one array does not excuse another. No macOS bash 3.2 exists in this container (`bash --version` is 5.x), so the `bus.sh orphans` rc 0 run on 3.2 is not recorded; the static rule stands in for it.

## Figures

- Sites the base listed, `git grep -nE '"\$\{[A-Za-z_]+\[@\]\}"' -- 'tools/**/*.sh'`, and the rule's own enumeration `python3 -I tools/audit/seat/bare_array.py --check --ref 3759d49a5` (set -u files only). Dispositions: bus.sh ledger call: guarded (the fix). cloud-setup.sh `parts` (`read -ra` of an empty PATH is an empty array): guarded. prepr.sh body_check call with `reds`: guarded (its sibling call at the other site already was). Marked never-empty with the reason on the line: body_patch.sh `args`, cloud_relay.sh `upd`, cloud-setup.sh `vars` x3, app_approve.sh `d`, prepr.sh `args`, `TRANSPORT_ROOTS`, `PIPE_GREP_Q_FILES`. pr_args.sh has no `set -u` of its own but is sourced into set -u callers (cloud_relay.sh): `PR_FRESH_PATHS` guarded; the four `PR_REAP_PIDS`/`alive` sites marked with the early return that makes each non-empty.
- Residual seam: `tests/entities.py` reads blobs of HEAD (`scan("HEAD")`), so a tree edited and uncommitted is judged at its last commit; `bare_array.py --check` with no ref reads the working tree. A sourced library with no `set -u` of its own is not judged by the rule (pr_args.sh was classified by hand): distinct, not closed here.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL` (tests/closure.py's INERT_EXCEPT changed). Ran locally: `tests/entities.py` (all checks passed), `tests/structure.py` (RATCHET PASSED), `tools/pr/prepr.sh` rc=0, `tools/pr/ci_predict.py` no red. `tests/closures.json`: entities.py closure recorded with `derive_closures.sh --single tests/entities.py --record-only` then `closure.py merge --partial --allow-failures`; the recording's rc was 1 solely from the unclassified-file refusal this change fixes, and I set that rc to 0 by hand.

## Red checks

none

## Forward-carry

none

## Friction

none
