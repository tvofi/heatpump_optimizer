Fix review: blocked ec773d944b749865f4f0a343c8f0a67e33d35e5c harness: class-open binary-content: added_lines skips any file holding a NUL byte in its first 8000 bytes at either end, so a new host path in a binary or NUL-bearing file (a .gz evidence log, a UTF-16 capture) is never judged, and WHAT IT DOES NOT CATCH does not name it

bus-nonce: 7a367ecda8669471de4446a47b1451be

Round 1. Reviewed from a detached worktree at the head `ec773d944b749865f4f0a343c8f0a67e33d35e5c` (still the live head when this was written), with a second detached worktree at the merge base `e5f7e169d64b93d4ae117eb07c68ecef6d47aea6` (= origin/main when measured; `git merge-tree --write-tree origin/main <head>` rc 0). `git diff <base>...origin/main -- dev/governance/roles/` is empty, so this contract is current. The host's account name, home and uid are written below as <account>, <home> and <uid>.

## The blocking finding

`ref_privacy.added_lines` reads `git show <rev>:<path>` and returns `None` (meaning binary) when `b"\0"` appears in the first 8000 bytes; `if old is None or new is None: continue` then drops the whole file. A planted commit on the head adding `dev/audit/nul.log` = `bin\0\nran at <another account's /Users home>/w\n`:

    RESULT plant=P4 code=head rc=0 1189 line(s) added since e5f7e169d64b judged, 0 refused

The same line in a plain text file (P1) is refused, so the skip alone lets it through. The tree has carriers of this shape: 268 tracked `.png` and 3 tracked `.gz` at the head, and a compressed evidence log or a diagnostics bundle is exactly the kind of record #2310's scrub covered. No such binary carrier exists today (128 account-name files at the base under `git grep -a`, and all 128 under `git grep -I` too), so nothing leaked. The defect is that the body and the docstring claim more than the check does. The docstring's CONTENT paragraph says the check judges "every line a diff adds to a tracked file", and its WHAT IT DOES NOT CATCH list names JSON-escaped and twice-encoded text but not binary content. The body's own figure counts binary files ("text and binary alike"), and that is the shape the check cannot see.

To clear it, pick one: (a) judge the bytes of a binary file the diff adds or changes (for example a NUL-tolerant scan of the raw blob with the same classes, charged per file rather than per line), with a self-test arm that plants a NUL-bearing file and its null control; or (b) disposition binary content explicitly in WHAT IT DOES NOT CATCH and in the body, and have `--check` print how many files it skipped as binary beside the judged-line count. Either way, add a self-test arm that kills the mutant `if old is None or new is None:` -> `if False:`. Today that mutant survives the self-test (60 checks, 0 failed).

## Also owed (not blocking alone)

- The rule "main's stock is not charged" within a changed file is not pinned by the self-test. Mutant `... if t.strip() not in was]` -> `... ]`: `ref_privacy.py --self-test` 60 checks, 0 failed. At the real head the same mutant makes `--check` refuse 5 lines (95759 judged), so CI catches it on this diff only by accident. One arm is enough: a changed file that keeps a stock host line, with that line not charged.
- The body says the nudge.md scrub "rewrites two path spans". `git diff --word-diff` shows four (`<home>/hpo-seats`, `<home>/hpo-orch/state` twice, `<home>/hpo-orch`, each to `~/...`), 4 lines changed and 4 removed. No rule text changes: each span names the same path, home-relative. tvofi's approving review is still owed (code-owned, policy).
- The body's figures are against B = `0b1ddb7fd`. The merge base is now `e5f7e169d`. I re-took the scrub counts at both, and they are equal.

## RESULT lines

Planted commits on the head, `--check --ref <plant>`, head code vs base code (evidence/plants.txt):

    RESULT plant=H (the head itself) head rc=0 1189 judged, 0 refused | base rc=0, 0 refused
    RESULT plant=P1 new file, another account's home: head rc=1 REFUSE dev/audit/plant.log:1 host-path | base rc=0
    RESULT plant=P2 delete README.md + add README2.md (rename by content) with one host line: head rc=1 REFUSE README2.md:239 host-path | base rc=0
    RESULT plant=P2b pure rename (identical blob): head rc=0 0 refused (null control)
    RESULT plant=P3u a unique stock line moved to a new file unchanged: head rc=0 0 refused (move rule holds)
    RESULT plant=P3u-edit the same moved line with one character edited: head rc=1 REFUSE dev/audit/moved.log:1 host-path
    RESULT plant=P3-reorder a stock line moved within its own file: head rc=0 0 refused
    RESULT plant=P3 a stock line duplicated elsewhere in its file, copied out: head rc=1 refused (the text was not given up, so it is charged: stricter, not an evasion)
    RESULT plant=P4 a NUL-bearing file with a host line: head rc=0 0 refused  <-- the evasion
    RESULT plant=P5 this seat's own home, built from $HOME: head rc=1 REFUSE home-directory, account-name, host-path | base rc=0
    RESULT plant=P6 a symlink whose target is another account's home: head rc=1 REFUSE host-path

So for the brief's questions: renames are covered (`--no-renames` makes delete + add, and the move rule nets out the unchanged text). A moved block with an edit is charged on the edited line. A file outside the text compare evades (P4).

Mutation proof, each mutant on a clean detached tree, then restored (`git status --short` 0 after each; evidence/mutation_ref_privacy.txt, evidence/mutation_bus_arm.txt):

    RESULT mutant ref_privacy content_refusals why=[]          -> self-test 3 failed (the body's three)
    RESULT mutant ref_privacy move rule return added            -> 1 failed (the null control)
    RESULT mutant ref_privacy check() wiring None,[],[]         -> 1 failed (the source pin)
    RESULT mutant ref_privacy binary skip -> if False           -> 0 failed  (survives; see the finding)
    RESULT mutant ref_privacy was-filter dropped                -> 0 failed  (survives; see Also owed)
    RESULT mutant bus.sh post_verdict "$(home_rel "$d")" -> "$d" -> bus self-test 2 failed (baseline 64/0)
    RESULT mutant app_approve.sh ~/ resolution -> :             -> 1 failed (baseline 169/0)
    RESULT mutant app_approve.sh token regex ~?/ -> /           -> 1 failed (my extra; the body names the resolution line only)
    RESULT mutant gh_comment.py privacy_check(body) -> pass     -> 1 failed (the wiring)
    RESULT mutant gh_comment.py body_refusal predicate off      -> 2 failed (my extra)

Scrub counts, re-derived under the body's own commands (account name from `basename "$HOME"` at run time):

    RESULT ref=0b1ddb7fd  account_files=128 uid_tmproot_files=13 vfolders_files=5
    RESULT ref=e5f7e169d  account_files=128 uid_tmproot_files=13 vfolders_files=5
    RESULT ref=ec773d944  account_files=0   uid_tmproot_files=2  vfolders_files=1

Kept files, checked line by line: the 2 temp-root files are `tools/pr/gh_comment.py:227` `DEFECT_BODY` and `tools/audit/seat/tmp_paths.py:102`, its `ALLOW` key. They are a fixture pair, not this host's session. The 1 per-user-temp file is `ref_privacy.py:48,138`: the docstring and the `_HOST_PATH` pattern. The `/Users/<x>` / `Users-<x>` hits are `ref_privacy.py:569` and `tmp_paths.py:269,330-342`, synthetic accounts (`exampleuser`, `someone`, `me`).

Citations by hash: for the 133 modified non-tool files (everything modified except `tools/` and the delivery row), I took 10-hex prefixes of each file's blob id, sha1 and sha256 at the base, 399 prefixes in all, and searched with `git grep -lI -F -f` at the head: 0 files. So no scrubbed file is cited by hash. Line counts: `git diff --numstat <base> <head> | awk '$1!=$2'` returns only the four code files plus the delivery row. Every scrubbed record kept its line count. The ledger: 31 added `"reason"` lines, all `<seat-scratch>/...` or unchanged text.

VERSION, the manifest version and the RELEASE_NOTES.md heading: untouched (0 files).

## CI (check-runs API at the head, latest run per name; evidence/check_runs_latest.tsv)

42 names: 25 success, 15 skipped, 1 neutral (CodeQL), 1 in progress (Analyze (python)). No failure or cancelled run at this head. Cited:

- `instrument-self-tests` success, job 117556777434. Its log: `ref_privacy self-test: 60 checks, 0 failed` and `ref_privacy --check at HEAD: 17 file(s) with a push site, 9 guarded, 1189 line(s) added since e5f7e169d64b judged, 0 refused`. CI's arm is live and judges the same 1189 lines as my local run.
- `wave-script` success, job 117556777589: `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`. The agreement-lane fix holds at the head: `added_lines` compares text and parses no hunk header, and `tools/policy/agreement.mjs` is not in the diff.
- `pr-contract` success (117556868900), `mutation` success (117557042889), `arch-score` success (117556777138), `budget-raise-gate` success (117556777174).
- The earlier-head red (`wave-script` on `78dbdbda6`) is named and answered in `## Red checks`.

## Not verified

- I did not re-run the gate, `harness_headers.py` or the mutation table. CI's runs are cited instead.
- The 128-file scrub's own hash check was done by `0855dad0f`'s body. My 133-file prefix search above covers the same files at the current base.
- `merge_pr.sh`'s change has no self-test arm (the script has none). I read it only: it renders through `ref_privacy.py path`, and a verdict that already holds the absolute path would now be refused by `gh_comment.py`'s privacy check rather than posted.
