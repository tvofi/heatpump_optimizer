Fix review: blocked 16cb22f640f325e86411d6b9734203f39b1e7ecb class-open: the parent field still logs caller words past argv[0], in glued code options (-cCODE, -eCODE, --eval=CODE) and stdin-script or option-value words (sh -s ARGS, python -W/-X VALUE)

bus-nonce: 4ca2508c1e47ecc70591d494ada72668

Review round 3 of PR #3049 (R10-FLY-GH-CALL-LOG, P284). I measured head `16cb22f640f325e86411d6b9734203f39b1e7ecb` (code head e24bda11a) from a detached worktree, using the round-2 finder's leak shapes (origin review/3049, evidence/parent-leak-probes.txt) plus my own shapes. Baseline: a7e6a3e5d.

## Block

The fix claims the parent field is built by construction: argv[0], then for an interpreter one word (the script, `-m <module>`, or the `-c`/`-e`/`--eval`/`--print`/`--command` option that ends the field), and that "no later word of the caller's command line is read". The PR body, `instruments/shims_seat-gh.md` and the shim's header comment all say this. The code does not do it. The round-2 shapes are closed. But the same class (a caller's argument value reaching `gh-calls.log`) is still open through seams the rule admits. Every probe below uses a LEAKVAL marker, and the logged line holds the marker at the evidence location given:

- **Glued code option.** The `-*[ce]*)` and `--eval*|--print*|--command*)` cases append the whole token `$a`. When the code is attached to the flag, the token is the code. `python3 -c<code>` and `python3 -Bc<code>` with no space in the code log the code up to the 80-char cut, flag values included (ev/probes2-head.txt lines 1-4). The same holds for `perl -e<code>` (ev/probes-head.txt "perl -eCODE glued"), `ruby -e<code>` (ev/probes2-head.txt line 7) and `node --eval=<code>` (ev/probes2-head.txt line 11). The `?` cleaning only replaces quotes, parentheses and `=`; the value itself survives.
- **Stdin script (`sh -s`/`bash -s`).** `-s` is skipped as an option, so the first positional argument is logged as if it were the script. `sh -s LEAKVAL < s.sh`, `sh -s -- LEAKVAL`, `bash -s LEAKVAL` and the common install shape `... | bash -s -- --token LEAKVAL` all log `sh LEAKVAL` or `bash LEAKVAL` (ev/probes-head.txt "sh -s" lines; ev/probes2-head.txt last line).
- **Value-taking interpreter options.** `python3 -W <v> script` and `python3 -X <v> script` log `<v>` as the script (ev/probes-head.txt "-W"/"-X" lines). `python3 -W error -m mod` logs `python3 error`, which also loses the module.

These are the same class round 2 blocked (a value from the caller's command line reaching the log), now reached through the interpreter rule rather than gh's flags. The enumeration the body names ("no word past the one it keeps") does not hold on the code: the kept word is chosen by a predicate whose domain includes option values, positional arguments of a stdin script, and option tokens that carry their own argument. A direction, not a requirement: for any `-c`/`-e`/`--eval`/`--print`/`--command` match, log only the flag name, cut at the first character after the flag letter (or `=`). Treat `-s` as ending the field. Treat any option the field rule does not know as ending the field, rather than skipping it and taking the next word. Pin each with an exact-field arm.

## Findings

- class-open: glued `-c<code>` / `-e<code>` / `--eval=<code>` tokens log the caller's code, flag values included (python, perl, ruby, node). No arm covers an attached-code token, and the planted mutant "skip `--eval*`" survives the self-test (ev/mutants-head.txt). Carry: #3049 (this PR's fixer owes it (round 4 means a re-cut per fixer.md))
- class-open: `sh -s ARGS` / `bash -s -- ARGS` logs the first stdin-script argument as the script, and so does an interpreter option's value (`python3 -W v`, `-X v`). The body's "no later word is ever read" claim is stronger than the check. Carry: #3049 (this PR's fixer owes it)
- surviving mutants at the head. (a) `tr -c` allowing `=` in the parent field survives (50 checks, 0 failed). (b) Removing the 80-char cut survives: no arm pins the cut the body claims. (c) Skipping `--eval*|--print*|--command*` survives. Each is a claim in the body with no arm. Carry: #3049 (add arms in the re-cut)
- script-path and argv[0] secrets are logged by design. `sh ./GH_TOKEN=abcLEAKVAL/script` logs the path, with `=` turned into `?`, and an argv[0] whose basename holds the marker logs it. These follow from the rule (argv[0] and script are the caller identity), so they are disclosed rather than blocked. The body should state this residual explicitly. Carry: #3049 (a body disclosure in the re-cut)
- body figure: "51 checks" and "34 at a7e6a3e5" (brief). As root, this container prints 50 at the head and 38 at a7e6a3e5, because one arm self-skips as root ("skip unwritable-directory arm"), so 51 non-root at the head agrees. The new-arm count is 17 by my own diff of the ok lines (38 − 5 removed + 17 added = 50). I found no 34 at a7e6a3e5: it prints 38 as root here. Carry: dismissed: the 51 agrees under the root skip, and 34 appears only in the dispatch brief, not the body

## Evidence

- RESULT finder-harness a7e6a3e5: 44 LEAK lines out of the round-2 shapes plus mine (ev/probes-a7e6a3e5.txt). The census and argv-list shapes are clean there too (sed redaction), and the 19 out-of-census flags, GH_TOKEN= and piped-secret shapes leak, so the harness fires.
- RESULT finder-harness head, round-2 shapes: 0 LEAK. All 25 census flags log exactly `sh -c`. The 19 out-of-census flags log `sh -c`. `sh -c GH_TOKEN=... gh` logs `sh -c`. Piped `gh secret set` logs `sh -c`. The python argv-list parent logs `python3 -c` (ev/probes-head.txt).
- RESULT null control head: `PY -I W/caller.py --body LEAKVAL` logs `python3 <W>/caller.py`, and `cd W && PY -m caller_mod --body LEAKVAL` logs `python3 -m caller_mod`, so the field is not cut to nothing.
- RESULT reviewer shapes head: 9 LEAK in ev/probes-head.txt and 5 in ev/probes2-head.txt; these are the shapes listed under Block and Findings. Clean (no leak, though sometimes misattributed): `bash -x s.sh LEAKVAL` gives `bash s.sh`; `node --require ./r.js n.js LEAKVAL` gives `node ./r.js` (misattributed to the required file); `perl -Mstrict -e` gives `perl -Mstrict`; `ruby -rjson -e` gives `ruby -e`; `xargs gh` gives `xargs`; `env GH_TOKEN=... gh` gives the env's caller; argv[0] with a space gives the first word.
- RESULT self-test head (root): `gh_calls self-test: 50 checks, 0 failed`. a7e6a3e5 (root): 38 checks, 0 failed. `seat_venv self-test: 21 checks, 0 failed`.
- RESULT body mutants, all killed (ev/mutants-head.txt):
  - whole argv logged: 11 FAIL
  - `-*[ce]*)` skipping: 9 FAIL
  - `chmod 600 "$log"` deleted: 2 FAIL
  - `&& chmod 600 "$log.1"` deleted: 1 FAIL
  - exec pass-through dropped: 7 FAIL
  - -f/-F removed: 1 FAIL
  - hermetic_ok forced True: 2 FAIL
  - umask 077 dropped: 2 FAIL
  - umask 077 outside the subshell: 1 FAIL
- RESULT planted leak mutants:
  - read one word past the script: killed, 1 FAIL
  - include the first word after -c: killed, 8 FAIL
  - `-m` takes module and next word: killed, 2 FAIL
  - combined `-Bc` treated as no code flag: killed, by the in-test mutant arm only
  - follow `env` into its command: survives. I judge it equivalent, because env execs its command, so gh's parent is never `env` (a live probe confirms this). Not counted as a finding.
  - `=` allowed, 80-char cut removed, `--eval*` skipped: survive (Findings O3).
- RESULT hermetic PATH: with a fake `/usr/bin/gh` planted, the unmutated self-test reads 50/0 and the no-real-gh arm stays ok. Adding `:/usr/bin:/bin` to the arm's `no_gh_path` reads 3 FAIL (the guard, the no-real-gh arm, the control) when /usr/bin/gh exists, and 0 FAIL when it does not. This is host-dependent by nature; the decoy control arm reproduces it on any host.
- RESULT umask (ev/umask-modes.txt): under caller umask 022 a fresh state dir is 700 and the log 600, and the caller's umask afterwards is 0022. The real gh ran under 0022. An existing 0644 log becomes 600 after the next call. With umask 077 planted outside the subshell, the real gh ran under 0077 and the self-test arm goes red.
- RESULT alert 46: the head's self-test has no `0o755`; every directory mode it sets is 0o700. It still sets a test log to 0o644 (`0o600 | 0o044`, gh_calls.py lines 282/285/291) to pin the existing-log chmod, which py/overly-permissive-file may flag. I could not read code-scanning alerts from this seat: there is no gh CLI for REST and no MCP code-scanning tool. The `CodeQL` check run is `neutral` and `codeql / Analyze (python)` was still in progress at read time. Whether alert 46 is fixed, dismissed or renamed is not verified here.
- RESULT shim cost (ev/latency.txt, 200 calls each, stub real gh): no shim 1.8 ms/call, head shim 27.8 ms/call, a7e6a3e5 shim 23.4 ms/call. So the head adds about 26 ms per call over a bare gh, about 4.5 ms more than round 2.
- RESULT harness_headers: here it fails 56 of 112 on both runs at the head, and also 56 of 112 at origin/main (ev/harness_headers-main.txt; venv-ha python; the harness scripts fail to run in this container). That is environmental, so this seat cannot say whether the body's "12 of 112 once, then 0" is flaky or load-dependent. The PR touches nothing under dev/audit/, and CI is the authority.
- RESULT daemon coverage: the body's statement is accurate and claims no more than it measured. roster_queue.py:95-97 prepends `tools/audit/seat/shims`, which holds only `seat-gh`, so it is not logged. beatd prepends `beatd_shims`. The body defers a live count to `gh_calls.py --coverage` on the host, which the instrument implements (gh_calls.py:124).
- RESULT gate: `git merge-tree --write-tree origin/main(df66556f2) <head>` exits 0 (LEDGER-MERGE resolved tests/closures.json as a set). Both claim files, VERSION, RELEASE_NOTES.md and the manifest are byte-identical to the merge base (three-dot). gh_calls.py is in tests/closures.json; the other new files are under INERT tools/audit/. INSTRUMENTS.md lists both instruments. The delivery row dev/programme/delivery/3049.md is in the three-dot diff. `STRUCTURE RATCHET PASSED`. `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
- RESULT head check: the head was 16cb22f640f325e86411d6b9734203f39b1e7ecb when measured and when this verdict was written (PR get).
- Red checks: no concluded red check at read time across the 37 check runs. See CI below. The body's `## Red checks` answers instrument-self-tests and alert 46 from earlier heads; I verified the self-test answer by mutation (hermetic arms above). The alert answer is unverified, as noted under alert 46.
- RESULT CI: `merge_train.py classify 16cb22f640f325e86411d6b9734203f39b1e7ecb` printed `GREEN ... pending: none red: none` and exited 0 at 07:34:48Z (ev/ci-classify.txt). No check went red at this head, so no `## Red checks` answer is owed for this head. CI green does not settle the block: no committed arm exercises the leak shapes above.
- RESULT live head: `refs/pull/3049/head` is still 16cb22f640f325e86411d6b9734203f39b1e7ecb when this verdict was finalised.
