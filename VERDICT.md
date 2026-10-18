Fix review: blocked e98c0dcd654a6cbd838ccfea54b8e303c5886303 harness: class-open tracked-path-names: the content arm judges what a file holds but never its name, so a diff adding a file under a dash-mangled home (the -Users-<name>- shape #2310 began with, and this host's own) passes, and WHAT IT DOES NOT CATCH does not name it

bus-nonce: e98d0d400f3b0a72b3c4de77100687ca

Round 2: a delta review of `ec773d944..e98c0dcd6`. The only code change is in `tools/audit/seat/ref_privacy.py` (`blob_text`, the binary skip removed, four self-test arms, a docstring entry). I reviewed from a fresh detached worktree at `e98c0dcd654a6cbd838ccfea54b8e303c5886303`, which was the live head when this was written. The merge base is `811df3cf3`, and `git merge-tree --write-tree origin/main <head>` returns rc 0. The host's account name, home and uid are written below as <account>, <home> and <uid>.

## Round 1's block is answered

Binary content is now judged. All of these were run with the head code and `--check --ref <plant>` (evidence: plants_round2.txt):

    RESULT plant=P4  NUL-bearing file, host line              rc=1 REFUSE dev/audit/nul.log:2 host-path
    RESULT plant=P7  UTF-16BE host line                       rc=1 REFUSE dev/audit/u16be.log:1 host-path
    RESULT plant=P8  UTF-32LE host line                       rc=1 REFUSE dev/audit/u32.log:1 host-path
    RESULT plant=P12 a NUL byte inside the host path itself   rc=1 REFUSE dev/audit/nulmid.log:2 host-path
    RESULT plant=none (the head itself)                       rc=0 1213 line(s) judged, 0 refused

Mutants, each restored to a clean tree (evidence: mutation_round2.txt; baseline `64 checks, 0 failed`):

    RESULT mutant blob_text NUL branch -> return ""           64 checks, 3 failed (NUL file, UTF-16, null control)
    RESULT mutant stock filter `not in was` dropped           64 checks, 3 failed (keep.log null control, clean.bin, scrubbed tree)
    RESULT mutant NULs kept (decode latin-1 undropped)        64 checks, 2 failed (my extra: UTF-16, null control)
    RESULT mutant content_refusals why=[]                     64 checks, 5 failed
    RESULT mutant move rule -> return added                   64 checks, 2 failed

Both mutants that survived round 1 are now killed.

## The new blocking finding: tracked path names are not judged

`added_lines` reads blob contents only. The name of a file a diff adds is never passed to `leaks`.

    RESULT plant=P11 new file dev/audit/rounds/<dash-mangled home of a synthetic account>-proj/x.log (content "ok")       rc=0 0 refused
    RESULT plant=P11-own new file dev/audit/rounds/<home with / as ->-heatpump-optimizer/memory/x.md  rc=0 0 refused

The second plant is the shape of a Claude project directory, `-Users-<account>-...`, copied into the tree. Its name carries this host's account name and the dash-mangled home. `ref_privacy.leaks` refuses exactly that string as a ref name (account-name, host-path), and `tmp_paths.py --check --ref <plant>` also returns rc 0, so nothing in the tree refuses it. A path name publishes on every clone just as content does (the docstring's own CONTENT rationale), and this was #2310's original shape. Neither the docstring's WHAT IT DOES NOT CATCH nor the body names it. No tracked name carries the account today: 0 at `811df3cf3`, 0 at the head, and 0 names in the `Users-<x>` / `tmp-claude-<n>` shape at the head. So nothing leaked; the claim is wider than the check. The fix is cheap: judge each path in `names` that is absent at the base with `leaks`, report it by class without echoing the path, and add a self-test arm with its null control (a clean new name passes).

Also declare, or judge, base64. `RESULT plant=P10 a JSON field holding base64 of a host line: rc=0 0 refused`. The docstring's "text encoded twice" covers URL-encoding, not base64, and embedded base64 bodies are common in .har files and HTML reports. A declaration is enough here, because decoding every base64-looking run is not obviously sound. Gzip is declared and evades as stated (`RESULT plant=P9 rc=0`).

## Body corrections

- nudge.md: the body now says "four path spans (4 lines, each `<home>/...` to `~/...`)". `git diff --word-diff=porcelain 811df3cf3 <head> -- dev/governance/roles/nudge.md` shows 4 added spans, and no rule text changes. tvofi's approving review is still owed.
- The figures are re-taken at `811df3cf3`, which is the merge base. I re-derived them under the body's commands: `RESULT ref=811df3cf3 account_files=128 uid_tmproot_files=13 vfolders_files=5` and `RESULT ref=e98c0dcd6 account_files=0 uid_tmproot_files=2 vfolders_files=1`. Diff shape: 139 files, 1255 insertions, 981 deletions, and only the four code files plus the delivery row differ in added and removed counts. All of these match the body.
- Observation, not blocking: the body's Figures line spells this host's uid in its command and its parenthesis. `ref_privacy.body_refusal` refuses that as the uid class. The body was posted through a path `gh_comment.py` does not guard. Writing `claude-$(id -u)` instead would publish nothing.

## CI (check-runs at the head, latest per name; evidence: check_runs_round2.tsv)

42 names: 27 success, 15 skipped, none failed or cancelled. `instrument-self-tests` success (117569507667), `wave-script` success (117569507647), `pr-contract` success (117569627554), `mutation` success (117569508248), `arch-score` success (117569507521). I re-ran no heavy script.

## Not verified

- I did not re-run the gate or the mutation table. CI's runs are cited instead.
- The round-1 checks on the files the delta did not touch (`bus.sh`, `app_approve.sh`, `gh_comment.py`, the scrub's hash and line-count checks) carry over unchanged. The delta does not touch those files.
