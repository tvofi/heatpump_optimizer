Fix review: blocked e7126ae228c8f99363dc0eec9e40920846b614f9 class-open: seat-gh lets gh issue comment --body x 201 and --body-file f 201 through to the real gh

bus-nonce: eb3e3c39e33d28f580551b43c270a90c

Round 1 fix review of PR #3223 (R10-RAISE-GATE-SHIM, issue 3128), at head e7126ae228c8f99363dc0eec9e40920846b614f9. I reviewed from a detached worktree at that SHA. The merge base is dad3178d6c81cfe2bb410e7045de28f686a6f845, which is also origin/main. `dev/governance/roles/` is unchanged between the merge base and origin/main, so the role contract I followed is current.

## Block

The shim's #201 guard can be bypassed by an ordinary spelling of the call the brief tells it to refuse. `seat-gh` finds the issue number by taking the third positional word. Its skip list covers `-b` but not `--body`, and it does not list `--body-file`. So in `gh issue comment --body x 201`, the shim reads `x` as the target, and in `gh issue comment --body-file f 201` it reads `f`. In both cases the call goes to the real gh, which takes interspersed flags and posts to #201.

I ran both calls offline against the stub. Each exits 0, and the stub file holds the argv (ev/shim-cases-head.txt, lines `issue-long-body-before` and `issue-body-file-before`). The attached form `--body=x 201` is refused. The brief asks me to check that alternate spellings of the call cannot bypass the shim, and these two do. The body does not list them under its stated residual (PATCH and graphql only), so this is `class-open`.

A sound repair parses `issue comment` by gh's own flag table: every value-taking flag, including `--body`, `--body-file` and `-F`, is skipped. It also normalises the target and the api path, covering the spellings under Findings. Each new spelling gets a pinned refusal arm in `gh_calls.py --self-test`.

## Findings

- Class-open (the block): `gh issue comment --body <text> 201` and `gh issue comment --body-file <f> 201` reach the real gh. The shim's positional parse skips `-b` but not `--body` or `--body-file`, so the number is never read. Offline stub: rc 0 and one argv line for each. Carry: R10-RAISE-GATE-SHIM
- Further spellings that the target and path match does not normalise. Each was run offline, and each reached the stub with rc 0:
  - `gh api repos/o/r/issues/201/comments/ -f body=x`, with a trailing slash;
  - `gh issue comment https://github.com/o/r/issues/201/ -b x`, an issue URL with a trailing slash;
  - `gh issue comment 0201 -b x` and `gh api repos/o/r/issues/0201/comments -f body=x`, with a leading zero;
  - `gh api repos/o/r/issues/%32%30%31/comments -f body=x`, percent-encoded.

  I did not verify whether GitHub or gh accepts each of these as #201. Proving that needs a live write, which the brief forbids. A leading zero passed through an integer parse, and a trailing slash on an issue URL, are the likeliest to land. Carry: R10-RAISE-GATE-SHIM
- The parent check reads the first non-option word after the interpreter, by basename. Two calls with no gh_comment.py in their path got through, offline:
  - `python3 -X gh_comment.py -c '<subprocess gh api -X POST .../issues/201/comments -f body=x>'`: `-X` takes a value, and the shim reads that value as the script.
  - `python3 <any dir>/gh_comment.py`: a different file with that basename.

  Both exit 0 and reach the stub (ev/spoof-and-control.txt). The self-test's spoof arm covers only a shell that names the file. The check should skip the values of value-taking options (`-X`, `-W`), and preferably resolve the script to the tree's own `tools/pr/gh_comment.py`. Carry: R10-RAISE-GATE-SHIM
- The body's `## Red checks` reads "none known at this head". Two checks concluded red at this head and the body does not answer them:
  - `governance / delivery-status` (id 127115047469): OVERDUE on main's rows #3201, #3206, #3189 and others, not on #3223.
  - `tests / nightly-status` (id 127115047402): the `slow` lane of nightly run 41943946464 failed at 499162c.

  Both pin the base dad3178d6c81cfe2bb410e7045de28f686a6f845, and neither is required. Each is inherited red from the base's ancestry. The body should name each one that way, giving the base SHA and the check. Carry: R10-RAISE-GATE-SHIM
- Carry (c) is still unmeasured: the `budget-raise-gate` job's 5-minute timeout against the scorer's CPU on the mandated path. The body dismisses it to the orchestrator. The job's run at this head took 29 s (07:37:44 to 07:38:13), but this diff raises no cap, so that run is not the mandated path and does not measure (c). The PR adds a scorer run to `--check-body` on a raise, which widens the same exposure. Carry: R10-RAISE-GATE-SHIM

## Evidence

- Offline arm. Every shim control ran under `env -i` with HOME set to an empty directory. PATH held the shim, then a local stub `gh` that appends its argv to a file and exits 0, then the venv and `/usr/bin:/bin`. The real `/usr/local/bin/gh` was not on that PATH. `env -i ... env | grep -i token` returned rc 1 (no tokens). A harmless `gh repo view` reached the stub and was recorded. The kill pairing was built at runtime from fragments, with the fixture id fixture-mandate-0000 (ev/cases.sh, ev/run.sh, ev/stub-gh.sh). I made no GitHub write of any kind.
- RESULT shim at head: 22 of 22 refusal arms refused, rc 1 with an empty stub file. These cover the planted kill-pairing `gh api -X POST .../issues/201/comments -f body=<kill>`, the field forms, flags placed first, a leading slash, a full URL, `{owner}/{repo}`, a query string, `--method POST`, `--method=POST`, `-XPOST`, `-X post`, `--input`, `--field=`, `--raw-field`, `-Fbody=`, `gh issue comment 201`, `--repo` after and before the number, `-R` before, `#201`, the issue URL and the issue URL with an anchor. All 8 of 8 null controls passed with exactly one argv line: a GET of #201, an explicit `-X GET`, posts to 202 and to 2011, `issue comment 202`, `issue view 201`, and the declared PATCH residual. The bypass probes are listed under Findings. The graphql `addComment` mutation also passes, which is the residual the body declares (ev/shim-cases-head.txt).
- RESULT shim at base (null control): the base `seat-gh` passes the planted post (rc 0, stub line), and only the 8 null controls pass (ev/shim-cases-base.txt).
- RESULT gh_comment.py control: `python3 -I tools/pr/gh_comment.py post --repo o/r --issue 201 --body-file body.txt` returned rc 0 through the head shim. The stub holds `api /repos/o/r/issues/201/comments --method POST --input <tmp>.json`, then the read-back `api /repos/o/r/issues/comments/1`. `--dry-run` left the stub file empty (ev/gh_comment-control-stub-argv.txt, ev/stub2-gh.py).
- RESULT mutation, each applied in a copy of the head tree (ev/mutants.txt, ev/mut-*.out):
  - shim refusal line `[ -n "$ok" ] || {` changed to `true || {`: gh_calls 98 checks, 7 failed;
  - `write=1` dropped from `-f|-F|--field|--raw-field|--input`: 2 failed;
  - `issue:comment` arm disabled: 2 failed;
  - parent check accepting any caller: 6 failed;
  - train `g.justified(...)` changed to `g.justification(...)`: merge_train 443 checks, 1 failed;
  - `--check-body` `justified(...) if raises else ...` changed to `justification(body)`: budget_raise_gate 274 checks, 1 failed.

  All six were killed. I also deleted the refusal line in the offline arm, and the planted post then reached the stub.
- RESULT self-tests at head: `gh_calls self-test: 98 checks, 0 failed`; `budget_raise_gate self-test: 274 checks, 0 failed`; `merge_train self-test: 443 checks, 0 failed` (ev/selftests-head.txt). The body's 443 for merge_train re-derives. Its "260 checks, 1 failed" for budget_raise_gate was taken at code head dc321a18. At this head the count is 274, and the 1 failed re-derives.
- RESULT dS value arm (files only):
  - The planted body is the #3045 `## Raise justification`, with the round-1 line `Architecture score: dS +0.0012 IMPROVES (coord_footprint 2390 -> 2388)`, which 0ec244aa's VERDICT.md quotes.
  - The measured line is `Architecture score: dS +0.0000 NULL`, from CI arch-score job 124591643014 (0ec244aa evidence/ci-arch-score-log.txt line 7).
  - At head, `check_body(body, [raise], score_fn)` refuses the planted body and passes the measured one. The train's `justified` read gives the same result.
  - At base, `check_body` takes no score_fn, and the shape-only `justification` passes the planted body. That was the gap.

  The body was reconstructed from the merged #3045 body, because 0ec244aa holds the review verdict rather than the PR body. The mandate id in it is replaced by a fixture (ev/ds/).
- No existing guard is weakened:
  - gh_comment.py's mandate guard is unchanged.
  - With no diff named, or a diff that raises nothing, `check_body` keeps its base `justification` path. It is stricter only on a raise.
  - The train's justify is stricter, and an exception from the scorer falls into the existing fail-closed `except`.
  - The shim's logged `sub`/`verb` fields are parsed as before. The only change is that the parse continues to a third positional.
  - The re-spelled `no --input skip` mutant still pins the `--input` skip.
- `git merge-tree --write-tree origin/main e7126ae2` returned rc 0 with tree 874638aec02fce28602c75e81a41682310504830. There were no conflicts and no claim-file merge.
- Untouched, compared with origin/main: the claim files are byte-identical (tests/golden/claimed_drift.txt and card_claimed_drift.txt), and so are VERSION, the manifest and RELEASE_NOTES.md. No `*_budgets.json` file is in the diff. `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED` (ev/untouched.txt, ev/structure.txt, ev/diffstat.txt).
- The body's `## Head` names e7126ae228c8f99363dc0eec9e40920846b614f9, which is the head I measured.
- Check runs, read live with get_check_runs: total_count 40, all on one page of 100. Concluded red: `governance / delivery-status` and `tests / nightly-status`, both inherited (ev/red-checks.txt). The rest are success, neutral (CodeQL) or skipped, or in progress at the time of reading. I re-read the checks at about 07:59Z, when total_count had risen to 56. `merge_train.py classify e7126ae228c8f99363dc0eec9e40920846b614f9 --pr 3223` exited 1 with `RED e7126ae228c8f99363dc0eec9e40920846b614f9 pending: none red: gate`. The red `gate` is job 127123127775 of run 41988826127, concluded `cancelled` at 07:59:06. Its `prelude` (127115920232) was also cancelled, after running from 07:40:03. Every other job of that run is skipped. In the push-time run 41988495627, `governance / instrument-self-tests`, `codeql / Analyze (python)` and `tests / graders-head-copy` were still in progress, and every other concluded job was success or skipped, apart from the two inherited reds. The `gate` red is a cancellation, not a failing test. The verdict above does not rest on it. The head was still e7126ae228c8f99363dc0eec9e40920846b614f9 at that read.
- The finder's harness: the packet names none, and the group has no committed harness. I built the offline stub arm myself, following the brief's own control design (ev/cases.sh, ev/run.sh). It is mine, not the finder's.
