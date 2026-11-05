Fix review: blocked 107b6137c8f277f2c8ca4ed94f90e161dabcf5cf class-open: seat-gh lets gh issue close 201 --comment and gh issue reopen 201 --comment post a comment on 201 unread

bus-nonce: 5a6ad5714e40034b8f95f659d92cab1c

Round 2 fix review (a delta round) of PR #3223 (R10-RAISE-GATE-SHIM, issue 3128) at head 107b6137c8f277f2c8ca4ed94f90e161dabcf5cf. I reviewed from a detached worktree at that SHA. The previous verdict blocked e7126ae228c8f99363dc0eec9e40920846b614f9, and the repair commit is 289fe24b401676199a4c10d0b181e9223cb458f3. The next round is the third. From the fourth, `fixer.md` owes a re-cut, not a repair.

## Block

The guard reads a #201 comment write only as `gh issue comment <target>` or `gh api .../issues/<n>/comments`. gh 2.89.0, the version on this host (`gh issue close --help`), also posts an ordinary issue comment through `gh issue close <n> -c/--comment <text>` ("Leave a closing comment") and through `gh issue reopen <n> -c/--comment <text>` ("Add a reopening comment"). Both calls name the issue as a plain number, which the shim can read, so they are not the declared residual (PATCH, graphql, `gh pr comment`).

I ran both offline against the stub, with the kill pairing built at runtime from fragments and the fixture id. Three calls reached the stub with rc 0 and one argv line each:
- `gh issue close 201 --comment <kill pairing>`
- `gh issue close 201 -c x`
- `gh issue reopen 201 --comment x`

The evidence is ev/shim-cases2-head.txt (`issue-close-comment-201`, `issue-close-c-201`, `issue-reopen-comment-201`). The gate's revocation reader takes any owner-account comment on #201 (the thread read of `issues/201/comments` in budget_raise_gate.py), so a closing comment counts exactly as a `gh issue comment` would. The class the body states is "a #201 comment write spelled so the shim cannot read the number", and this is a #201 comment write the shim does not read at all.

A sound repair treats a `--comment`/`-c` value on `issue close` and `issue reopen` as a comment write on that command's target. It runs the target through the same `num()`, and fails closed on an unreadable one. The `-c`/`--comment` value is skipped by gh's flag table, attached or detached. It needs pinned refusal arms in `gh_calls.py --self-test`, plus a null control: `issue close 202 --comment x`, and `issue close 201` with no comment, which writes no comment. It would be best to enumerate gh's issue subcommands that take a comment-writing flag, so the class closes by rule rather than by spelling.

## Findings

- Class-open (the block): `gh issue close 201 --comment <text>`, `gh issue close 201 -c <text>` and `gh issue reopen 201 --comment <text>` reach the real gh unread. The stub showed rc 0 and one argv line for each (ev/shim-cases2-head.txt). Carry: R10-RAISE-GATE-SHIM
- A gh alias passes the shim unread. `gh c201 -b x` reached the stub (ev/shim-cases2-head.txt, `alias-word`), and an alias `c201` defined in the seat's gh config as `issue comment 201` would post to #201. The shim cannot read aliases without running the real gh. The repair should either refuse a subcommand that is not one of gh's own, or declare aliases with the residual. Carry: R10-RAISE-GATE-SHIM
- The parent check trusts `ps -o args`, which a caller writes. `exec -a 'python3 <tree>/tools/pr/gh_comment.py' bash -c 'gh api -X POST .../issues/201/comments -f body=x; true'` reached the stub (ev/spoof-and-control-head.txt, `exec-a-argv0`). This is deliberate evasion, not a seat's habit, so it does not block this round. The instrument note should name it as a residual of a ps-based parent check. Carry: R10-RAISE-GATE-SHIM
- The body's `## Red checks` is still the account of head e7126ae2's runs (base dad3178d). It says it will be retaken at the next head. At this head the concluded reds are `governance / delivery-status` (127184912382) and `tests / nightly-status` (127184912222), both on base 79f765e6b2e0f97e61b57d7b605fc4e70b4bf21e. The arch-score and instrument-self-tests entries are about old-head runs. The next body should name this head's reds against this head's base. Carry: R10-RAISE-GATE-SHIM
- Carry (c), the budget-raise-gate job's 5-minute timeout on the mandated path, is still unmeasured. It is honestly carried in the body as dismissed to the orchestrator. The job took 29 s at this head (127184912361, 10:18:22 to 10:18:51), but this diff raises no cap, so that run is not the mandated path. Carry: dismissed: not measurable without a raise diff on CI's runner; the body routes it to the orchestrator's next raise PR, which this review cannot pre-empt

## Evidence

- Offline arm. Every shim control ran under `env -i` with HOME set to an empty directory. PATH held the head shim (installed by seat_venv's own bake loop, `gcpy=<worktree>/tools/pr/gh_comment.py`), then a local stub `gh` that appends its argv and exits 0, then the venv and `/usr/bin:/bin`. `type -a gh` showed only the shim and the stub. `env | grep -i token` returned rc 1 (no tokens). A harmless `gh repo view o/r` reached the stub as exactly one line (ev/offline-proof.txt). I made no GitHub write of any kind. The kill pairing was built from fragments at runtime with fixture-mandate-0000 (ev/cases.sh, ev/cases2.sh).
- RESULT previous reviewer's cases (ev/cases.sh, unchanged, from probe/rev-3223-eb3e3c39), at this head: 38 OK of 40. All 22 refusals refused, and all 9 former bypass probes (trailing slash on the api path and the URL, `--body x 201`, `--body=x 201`, `--body-file f 201`, leading zero on the api path and the issue number, percent-encoding) are refused with an empty stub file. All 8 null controls passed with exactly one argv line. The 2 FAILs are `graphql-declared-residual` and `pr-comment-201`, which are the declared residual (ev/shim-cases-head.txt).
- RESULT my further spellings (ev/cases2.sh, ev/shim-cases2-head.txt): 15 refused with an empty stub file. These were a `--` before the path, `repositories/<id>/issues/201/comments`, `%63omments`, `-X Post` with `-F`, `./` segments, `--input=`, `--hostname`, `--edit-last`, `--body-file=`, `-Ff`, a URL with a query, `+201`, `--repo=`, and a `/pull/201` URL. The 4 null controls passed with one line each (`--paginate` GET, `issue close 202 --comment`, 2010, 1201). 4 calls passed through: the three `issue close/reopen --comment` calls (the block) and the alias word.
- RESULT parent check (ev/spoofs.sh, ev/spoof-and-control-head.txt, stub ev/stub2-gh.py that serves gh_comment.py's calls). The following were refused with an empty stub file: `python3 -X gh_comment.py -c ...`; a copy of gh_comment.py in another directory; a hard link under another name; `python3 -c`; bash; `-c` code naming the tree's path; `-m gh_comment`. `exec -a` passed (see Findings). The control `python3 -I <tree>/tools/pr/gh_comment.py post --repo o/r --issue 201 --body-file ...` reached the stub by an absolute path, a relative path and a symlinked directory: rc 0, holding the post argv `api /repos/o/r/issues/201/comments --method POST --input <tmp>.json` plus gh_comment.py's own read-back `api /repos/o/r/issues/comments/1`, two lines by gh_comment.py's design.
- RESULT mutants, each in a copy of the head tree (ev/mutants.sh, ev/mutants-r2.txt):
  - refusal line changed to `true ||`: gh_calls 146 checks, 38 failed, and offline planted case through;
  - `--body|--body-file` dropped from the skip list: 2 failed (offline, fail-closed still refuses `--body x 201`, so the kill is the in-suite #202 null control);
  - leading-zero strip removed: 3 failed, and `0201` through;
  - trailing-slash strip removed: 3 failed;
  - `write=1` dropped from the field flags: 12 failed, and through;
  - `tracker=0`: 34 failed, and through.

  All six were killed.
- RESULT self-tests at head (ev/selftests-head.txt): `gh_calls self-test: 146 checks, 0 failed`; `seat_venv self-test: 25 checks, 0 failed`; `budget_raise_gate self-test: 274 checks, 0 failed`; `merge_train self-test: 443 checks, 0 failed`. The body's 146 and 25 re-derive. The body's "38 failed" for the refusal mutant re-derives.
- RESULT dS value arm (files only, ev/ds/RESULT-head-r2.txt). The planted #3045 round-1 body (dS +0.0012 IMPROVES), checked against the measured `dS +0.0000 NULL`, is refused by `check_body(raises=[x])` and by `justified`. The measured body passes. This is unchanged in this delta.
- The delta e7126ae2..107b6137c8f277f2c8ca4ed94f90e161dabcf5cf: the authored change is 289fe24b (seat-gh, its installer, gh_calls.py, the instrument note). The rest is main's merge of #3185. The three-dot diff against the base names 7 files (ev/diff-files.txt), with no budget file and no structure budget. VERSION, RELEASE_NOTES.md, the manifest and both claim files are byte-identical to origin/main (ev/untouched.txt).
- No guard is weakened: gh_comment.py is untouched. The `--input` mutant pin is re-spelled to `--raw-field`, and the skip still holds. The new value flags only add skips.
- `git merge-tree --write-tree origin/main 107b6137c8f277f2c8ca4ed94f90e161dabcf5cf`, with origin/main at 0ae75bf31, returned rc 0 with tree 5266c089fbd218f6a4b8ffbc007c7018ceaba55f, and no conflict (ev/merge-tree.txt).
- CI on this head (ev/red-checks.txt). Concluded red: delivery-status and nightly-status, both inherited from the base's ancestry (79f765e6) and outside this diff's closure. `merge_train.py classify 107b6137c8f277f2c8ca4ed94f90e161dabcf5cf --pr 3223` re-run in the background every ~90 s: WAIT from 10:24Z, then exit 0 at 10:58Z, `GREEN 107b6137c8f277f2c8ca4ed94f90e161dabcf5cf pending: none red: none` (ev/classify.txt, ev/classify.log). The block does not rest on CI.
- The finder's harness: the packet names none. The offline stub arm is the previous reviewer's, re-used unchanged, plus my cases2.sh and spoofs.sh. Those two are mine, not the finder's.
- The body's `## Head` names 107b6137c8f277f2c8ca4ed94f90e161dabcf5cf, which is the head I measured.
