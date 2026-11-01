Fix review: blocked a7e6a3e5dfa05028be5127fc7a60f512277d861c class-open: the parent-command redaction matches only space-delimited flags, so a python argv-list parent still logs census --body/-f values, and a sh -c parent logs a GH_TOKEN= assignment or a secret piped to gh secret set

bus-nonce: 0626161eb1d5d28483dcf0068b28d9b3

Round 2 (delta) of the review; the PR is at its third handoff (92fff84c3). I measured head a7e6a3e5dfa05028be5127fc7a60f512277d861c from a detached worktree at that SHA. It merges code head 92fff84c35ee82d727c5a81622980bef10207123 and origin/main 8fec54ee2. I reproduced the round-1 defects from a detached worktree at 87abaed68871d3141b8221965d5a5860a075c43f. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current. `review_carry.py 92fff84c3 a7e6a3e5` prints FRESH-REVIEW, as expected, because no earlier merge verdict exists.

## Block

- **class-open: the parent-command field (requirement "field values and bodies are never logged", P284; round-1 finding (a)).** The redaction is two `sed` patterns. Both key on a flag preceded by a space (`(^| )--body…`, `(^| )-[fFHbntTqd]…`), and the short-flag pattern also needs a space-delimited `gh` word. The body's census plants every value through a `sh -c 'gh api … FLAG VAL'` parent only. Every census flag is clean in that shape (25/25, plus 12 `=`/glued forms clean; ev/parent-leak-probes.txt). Three parent shapes outside that shape write the value to gh-calls.log. I reproduced each at this head through the real shim:
  1. Python argv-list parent: `python3 -c "import subprocess as s;s.run(['gh','pr','comment','--body','LEAKVAL'])"` logs `…['gh','pr','comment','--body','LEAKVAL'] pr comment`. With `'-fx=LEAKVAL'` the same shape logs the `-f` value. The quote before the flag defeats `(^| )`, and `'gh',` is not a `gh` word. In two longer probes the value was cut off only because it fell past the 80-character cut.
  2. Env-assignment parent: `sh -c 'GH_TOKEN=ghp_LEAKVAL gh api user'` logs the token.
  3. Piped-secret parent: `sh -c 'echo ghp_LEAKVAL | gh secret set NAME'` logs the secret value of `gh secret set`, the flag-free form that `gh secret set --help` documents.

  The body's census is a list of flags, but the field it guards is any command line, so a list of flags cannot close it. `gh_calls.py --top` prints this field, and that output is what gets pasted into an issue when the bucket next runs out. The round-1 verdict's first fix direction closes the class by construction. Log the parent's argv[0], plus argv[1] when argv[0] is an interpreter or shell, and never its later args. A wrapper that is itself a gh-carrying `sh -c` can be replaced by its grandparent. Add self-test arms for the three shapes above, so the fixture is not only `sh -c`.

## Findings

- A log or state directory created before this fix keeps its old mode. The umask governs only creation. Under umask 022, a `gh-calls.log` that the round-1/round-2 shim already wrote stays 0644. An existing `$HOME/.local/state/hpo`, which other tools may have made, stays 0755. `mv` rotation also keeps 0644. The body's "dir 0700, log 0600" holds for fresh paths only (ev/umask-modes.txt). One `chmod 600` of an existing log, or a statement that no host ran the earlier shim, settles it. Carry: R10-FLY-GH-CALL-LOG
- Minor body inaccuracies, to fix in the same re-handoff. `## Red checks` lists the hermetic tool dir as "ps, tr, cut, wc, mv, date, cat, sh". The code (gh_calls.py:170) also links sed, mkdir, env and python3. "the no-real-gh arm asserts first (`hermetic_ok`)": `hermetic_ok` is a separate `check`, not a gate in front of that arm. A failing guard and a failing arm print two FAILs, and neither stops the other. Carry: R10-FLY-GH-CALL-LOG
- Value flags missing from the census: `-A/--author-email`, `-S/--search`, `-m/--milestone`, `-l/--label`, `-a/--assignee`, `-r/--reviewer`, `-B/--base`, `--match-head-commit`, `-p/--preview`, `-e/--env` (ev/gh-help-valueflags.txt, gh 2.89.0; all leak, ev/parent-leak-probes.txt). They carry identifiers, not bodies or secrets, apart from `--author-email`, which is personal data, and `-S`, which is free text. I record this so the class rule in the Block can absorb it, not as a block of its own. Carry: R10-FLY-GH-CALL-LOG

## Evidence

- RESULT finder's harness (round-1 block): with a decoy `/usr/bin/gh` planted, `env -u BASH_ENV python3 -I tools/audit/seat/gh_calls.py --self-test` gives:
  - at 87abaed6: `18 checks, 1 failed` (FAIL no real gh: one line, rc 127, no self-exec);
  - at the head: `38 checks, 0 failed`.

  The decoy was removed afterwards (ev/finder-harness-usr-bin-gh.txt).
- RESULT self-test at the head under `env -u BASH_ENV`, as root: `38 checks, 0 failed`. The read-only-directory arm prints `skip`, because root can write anyway (ev/selftest-head.txt). As `nobody`: `39 checks, 0 failed` (ev/selftest-head-nonroot.txt). CI job 124725103432 (`governance / instrument-self-tests`) at this head: `gh_calls self-test: 39 checks, 0 failed` (ev/ci-instrument-self-tests-gh_calls.txt). The body's 39 is re-derived.
- RESULT mutants. I ran each one against the head's committed files under `env -u BASH_ENV`, restored the files after each, and the worktree was clean afterwards (ev/mutants-head.txt). Every mutant was killed:
  - (b) `--input|` removed: 2 FAIL.
  - (c) `clean()` `tr` replaced by `cat`: 2 FAIL.
  - `mkdir -p` dropped: 3 FAIL.
  - Redaction disabled (both seds): 4 FAIL.
  - `umask 077` dropped: 2 FAIL.
  - Widened to `umask 022` or to `umask 027`: 2 FAIL each.
  - Subshell dropped (`umask 077` at top level, no `( … )`): 3 FAIL.
  - My plant, `umask 077` moved outside the subshell: 2 FAIL.
  - My plant, `umask 077; exec`: 1 FAIL ("the real gh runs under the caller's umask").
  - Exec pass-through dropped: 7 FAIL.
  - Hermetic guard disabled (`hermetic_ok` returns True): exactly its two mutation arms FAIL.
  - Old-style PATH (`…:/usr/bin:/bin`) restored in the test with a decoy `/usr/bin/gh` planted: 3 FAIL, including the no-real-gh arm.
  - (d) Self-recursion (`! is_shim` removed): the self-test terminates after 60 s with `subprocess.TimeoutExpired`, rc 1. It no longer hangs. It prints no summary line, so the CI `grep` step fails.
- RESULT (U) umask, by hand with a stub gh that prints its umask (ev/umask-modes.txt), caller umask 022:
  - at 87abaed6: log 0644, real gh umask 0022, and a missing state dir is not created;
  - at the head: log 0600, a new state dir 0700 with log 0600, real gh umask 0022, and the caller's umask is 0022 after the call.

  The umask is confined to the logging subshell.
- RESULT (A) alert 46. The code-scanning API answers HTTP 403 from this seat (ev/codeql-46.txt). I read the alert from the check-run annotations instead (ev/codeql-annotations.txt). `CodeQL` check 124609893863 at 87abaed6 concluded failure with 1 annotation: `tools/audit/seat/gh_calls.py:211` "Overly permissive mask in chmod sets file to world readable". That line is `os.chmod(w / "state", 0o755)` in the self-test. The body's answer (the self-test restore at 0o755, not the shim) is true. The head's self-test chmods are all 0o700 or 0o500 (gh_calls.py:158, 163, 281, 290, 297, 354, 384), so the flagged pattern is gone, not renamed. The bash umask change is a separate, real fix, and its arms cover it.
- CI at this head:
  - `merge_train.py classify a7e6a3e5…` printed `GREEN a7e6a3e5dfa05028be5127fc7a60f512277d861c pending: none red: none`, rc 0 at 03:23:23Z (ev/ci-classify.txt). Every check run concluded success or skipped.
  - `CodeQL` check 124725215898 at this head: success, 0 annotations, "No new alerts in code changed by this pull request". It read neutral while the python leg was still running. Alert 46 is resolved by the code change; it was not dismissed.
- (B) Red checks. No check run at this head concluded `failure` (check-runs API, whole set). The body names and answers the earlier reds: UNDER-SCOPED/INERT READS, `governance / instrument-self-tests` (cause, process state, cheaper detector) and alert 46. The `CodeQL` check is answered through alert 46. My block does not rest on step 11.
- (C) prepr: the body states no prepr rc. My own run at the head (detached, with the PR body) prints `PRE-PR: a7e6a3e5… rc=0` (ev/prepr-head.txt).
- `git merge-tree --write-tree origin/main a7e6a3e5`: rc 0, tree bbf3aebff92ee6a208ee98197c6e5e58f85a24d2, no conflict (ev/merge-claims.txt).
- Claim files, VERSION, the manifest and RELEASE_NOTES.md: the three-dot diff is empty.
- The delivery row `dev/programme/delivery/3049.md` is in the three-dot diff. `gh_calls.py` is in tests/closures.json. The other new files are under INERT `tools/audit/`. INSTRUMENTS.md lists both instruments.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `tests/closure.py select`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (ev/structure-scope.txt).
- Latency: 200 calls each against an `exit 0` stub, in this container: 1.674 ms direct, 24.102 ms through the shim, so about 22.4 ms per call (ev/latency.txt). The body's 56 ms was taken on its own host and I did not re-derive it. My figure is from a different host.
- The body's census of 25 flags is re-derived: each of the 25 is clean through a `sh -c` parent (ev/parent-leak-probes.txt).
