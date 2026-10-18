Fix review: merge 60308ef8ff6e0a7e6ec5792f203e32ca7c653721

bus-nonce: d2d60624902ec83236d3c5364e3cb657

Round 3. This is a delta review of `e98c0dcd6..60308ef8f`, done from a fresh detached worktree at the head. The authored code head is `e73c683a1`. The merge base is `9a1ce39c3`, and `git merge-tree --write-tree origin/main <head>` returns rc 0. The PR's own code change in this delta is `tools/audit/seat/ref_privacy.py` only: `added_names` and `name_refusals` wired into `content_check`, two new self-test arms with one arm amended, and base64 declared. `orchestrator_tick.py` arrived with the main merge: it is not in `git diff 9a1ce39c3...<head>`. The host's account name, home and uid are written below as <account>, <home> and <uid>.

## Round 2's block is answered

Planted commits on the head, run as `--check --ref <plant>` with head code (evidence: plants_round3.txt):

    RESULT plant=P11 new file under a synthetic account's dash-mangled home            rc=1 REFUSE added path #1: host-path in the name
    RESULT plant=P11-own new file under this host's dash-mangled home                  rc=1 REFUSE added path #1: account-name, host-path in the name
    RESULT plant=P11-rename an existing file renamed into a dash-mangled directory    rc=1 REFUSE added path #1: host-path in the name
    RESULT plant=P11-null a new file under an ordinary name                            rc=0 0 refused (null control)
    RESULT plant=none (the head itself)                                                rc=0 1239 line(s) judged, 0 refused

A refusal names the path by its index, never by its text: neither the planted name nor <account> appears in the output.

Mutants, each restored to a clean tree; baseline `66 checks, 0 failed` (evidence: mutation_round3.txt):

    RESULT mutant name arm dropped from content_check           3 failed
    RESULT mutant name_refusals predicate why=[]                3 failed (my extra)
    RESULT mutant --diff-filter=A -> X (no names enumerated)     3 failed (my extra)
    RESULT mutant blob_text NUL branch -> return ""              3 failed (round 2's, still killed)
    RESULT mutant stock filter `not in was` dropped              3 failed (round 2's, still killed)

base64 is now listed in WHAT IT DOES NOT CATCH, with its reason. Gzip and zip were already listed there.

## Figures

Re-derived under the body's own commands (evidence: counts_round3.txt):

    RESULT ref=9a1ce39c3 account_files=128 uid_tmproot_files=13 vfolders_files=5
    RESULT ref=60308ef8f account_files=0   uid_tmproot_files=2  vfolders_files=1

These match the body: 128 to 0, 13 to 2, 5 to 1, with B = `9a1ce39c3`. The kept files are the round-1 fixture pair and the guard's own pattern, unchanged. The body now builds the uid with `$(id -u)`: it contains no `claude-<uid>`, no bare <uid> and no <account>. No tracked path name at the head carries <account> or the `Users-<x>` shape. The body's `## Head` names `60308ef8f` and code head `e73c683a1`.

## Carried from rounds 1 and 2 (files unchanged since)

- The `bus.sh`, `app_approve.sh` and `gh_comment.py` reverts all fail their self-tests.
- No scrubbed file is cited by hash: 399 prefixes, 0 hits.
- Every scrubbed record kept its line count.
- The `nudge.md` change is four path spans, with no rule text changed. tvofi's approving review at the head is still required before merge (code-owned, policy) and is the orchestrator's to obtain.
- `VERSION`, the manifest version and the notes heading are untouched.

## CI (check-runs at the head, latest per name)

42 names: 25 success, 15 skipped, 1 neutral (CodeQL), 1 in progress (Analyze (python)), none failed or cancelled. `instrument-self-tests` success (117587774316), `wave-script` success (117587774332), `pr-contract` success (117587865582), `mutation` success (117587774655), `arch-score` success (117587774226). There was no failed or cancelled run at this head. `closures` success (117588770095), awaited before posting. I re-ran no heavy script.
