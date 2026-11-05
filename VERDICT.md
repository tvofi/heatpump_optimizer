Fix review: blocked 4404f5e7435b5a574204a5f51c004a364f7817df class-open: an api write to repos/o/r/ISSUES/201/comments (and issues/201/COMMENTS, Issues/201/Comments, GRAPHQL) reaches the real gh; the case-gap repair the round-4 block asked for is not at this head

bus-nonce: 6512631b9b2b12eb990a754ec6091174

Round 5 (delta) of PR #3223, R10-RAISE-GATE-SHIM (issue #3128). Reviewed head `4404f5e7435b5a574204a5f51c004a364f7817df` from a detached worktree; previous reviewed head `6b416a18fc8752eaa3c10404cec43f896df3ed60`. From the fourth round `fixer.md` owes a re-cut, not a repair.

## Block

The dispatch names three repairs (f-3223-r4, handoff `725410a6`) for this round to verify. **None of them is at this head.** The only commit since `6b416a18` that is not a main merge is `725410a6b`, and it adds three lines to `tools/audit/seat/queue_pre_flight.py`'s self-test (a stub for `Train._measured_score`). Nothing in the shim, `gh_calls.py` or `seat_venv.sh` changed.

1. **Case gap: still open.** `norm()` keeps case and `api_gate` matches `issues`, `comments` and `graphql` case-sensitively. Offline, against a stub gh: `api repos/o/r/ISSUES/201/comments -f body=x`, `.../issues/201/COMMENTS`, `.../Issues/201/Comments` and `api GRAPHQL -f query=mutation{x}` all reach the stub with rc 0. There is no lower-casing in the head, so the "mutate the lower-casing out" control cannot be run. I did not check GitHub's own routing case-sensitivity live (no network control). The round-4 review treated this as a bypass, and so does the dispatch.
2. **Literal word: not removed, and the body's claim about it is false.** The three-dot diff adds the revoke word whole twice in `tools/audit/seat/gh_calls.py` (the `planted` list, and the `gh issue comment 201` row), each time paired with the mandate-shaped id `1234567`. `fixture-mandate-0000` occurs 0 times in the diff (`ev/literal-word-grep.txt`, word masked as `<RV>`). The body's `## Null control` says "The mandate id in tests is the fixture `fixture-mandate-0000`; the revoke word is never written whole in a file", and that is false at this head.
3. **`--install-shims` bake-line mutant: survives and is not carried.** I replaced `seat_venv.sh`'s bake line with `:`, so the installed shim keeps `gcpy=@HPO_GH_COMMENT@` and refuses even the known poster. `seat_venv self-test` still reads 25/0 and `gh_calls self-test` 190/0. `gh_calls.py`'s `install()` bakes its own copy, so no row reads the installer. The body neither kills nor carries it.
4. **The body is still stale against this head:**
   - `## Red checks` is "Retaken against the PR head `6b416a18`". This head's concluded reds are `tests / nightly-status` (127408111130) and `governance / delivery-status` (127408110624), and the body's run ids are the old head's.
   - `## Head` gives `origin/main` as `8bf45e5d`, but the head merges `8b49d50b0a4c3eebee0edeb6ec98aa365e3d004f`.
   - It names **Carry 3** and **Carry 4**, which do not exist in the roster (see Findings).

## Findings

- Case variants of the #201 comment path (`ISSUES`, `COMMENTS`, `Issues/Comments`) and `GRAPHQL` pass `api_gate` to the real gh; the repair owed by the round-4 block is absent at 4404f5e7. Carry: R10-RAISE-GATE-SHIM
- The revoke word is written whole twice in `tools/audit/seat/gh_calls.py`'s self-test, paired with id `1234567`, not the fixture `fixture-mandate-0000` built from fragments; the body's no-literal sentence is false. Carry: R10-RAISE-GATE-SHIM
- Surviving mutant: `seat_venv.sh --install-shims` bake line removed, every self-test still green (seat_venv 25/0, gh_calls 190/0); a self-test row exercising the installer's baked `gcpy=` line is owed, or a carry with its reason. Carry: R10-RAISE-GATE-SHIM
- Orchestrator's check of the body's carry numbers: wrong. Roster `dev/programme/rosters/wave-r10-groups.json` (origin/main) gives group R10-RAISE-GATE-SHIM exactly **2** carries. Index 0 is the revoke-guard fixer's (a)/(b)/(c), and the job-duration measurement is its sub-item **(c)**, not a "Carry 3". Index 1 is the #3045 dS value check. No roster carry concerns the `exec -a` argv0 spoof, so "Carry 4" names nothing; that residual is a body-declared residual, routed by its own Forward-carry line. The body's Carry 1 and Carry 2 match the roster. Carry: R10-RAISE-GATE-SHIM
- Declared residual confirmed, not a new defect: a forking `exec -a 'python3 <tree>/tools/pr/gh_comment.py' bash -c 'gh api .../issues/201/comments -f body=x; true'` reaches the stub (rc 0, 1 line). The non-forking form is refused. Carry: R10-RAISE-GATE-SHIM

## Evidence

- RESULT offline harness at head (`ev/harness.sh`, `ev/harness-head.txt`): 61 controls, 57 as expected, 4 mismatches, all of them the case variants above. Stub recorded a harmless probe (`STUB-RECORDS: ok`); `env | grep -i token` inside the arm was empty; HOME was an empty directory; `env -i`, no proxy. The kill pairing used `fixture-mandate-0000`, with the word built at runtime from fragments.
- The refused rows, each with an empty stub log and rc 1:
  - the planted raw kill-pairing post;
  - implicit POST, trailing slash, leading slash, full URL, leading zero, %-encoded, `//`, query, anchor, `..` segments;
  - `--method=POST --input`, `-XPOST`, `-F`, `--raw-field`, an `X-HTTP-Method-Override` header;
  - PATCH by comment id; graphql mutation inline, from `@file` and via `--input`;
  - `issue comment 201` with `--repo` first or last and with `-R`, by URL, URL with a trailing slash, `0201`, `#201`, a `-Rb` cluster and `--`;
  - `issue close --comment`, `issue reopen -c`, `issue edit`;
  - `pr comment 201`, and by `/pull/201` URL;
  - an unlisted subcommand, an alias word, an extension word, a leading `-R`, an unknown issue verb, an unknown api flag, two api paths.
- The pass-through rows, each with the stub holding the argv: GET of #201 comments, posts to 202 and 2011, `issue comment 202` (with and without `--body 201`), `issue view 201`, `issue list`, `issue close 202 --comment`, `pr view`, a graphql read, an Accept-header GET, `--version`, `run list`, `workflow run`, an api write to `git/refs`.
- Known poster: `python3 -I <tree>/tools/pr/gh_comment.py post --repo o/r --issue 201 --body-file f` reached the stub with `api /repos/o/r/issues/201/comments --method POST --input <tmp>.json`. gh_comment.py then exits 2, because the stub returns no readback; that is expected offline.
- Deny-by-default: unlisted subcommand `foo`, alias `co`, extension `my-ext` are refused.
- RESULT mutants (`ev/mutants.txt`): deny-by-default arm, comments-by-id, graphql-mutation, issues/201/comments and the refusal exit are each killed, by both the self-test (4, 3, 2, 20 and 65 failures) and the harness. The bake-line mutant survives.
- Self-tests at head, re-derived: `gh_calls self-test: 190 checks, 0 failed`; `queue_pre_flight self-test: 45 checks, 0 failed`; `merge_train self-test: 443 checks, 0 failed`; `budget_raise_gate self-test: 274 checks, 0 failed`; `STRUCTURE RATCHET PASSED`. I did not re-derive the body's "184 checks, 22 failed on the old shim" figure (no pre-rewrite shim run); it is not verified.
- dS value arm, files only, against `budget_raise_gate.justified` with a stub scorer reading `dS +0.0000 NULL`. The planted #3045 round-1 shape (`dS +0.0012 IMPROVES`, from verdict/3045 0ec244aa) returns False with "claims dS +0.0012 IMPROVES, but ... measures dS +0.0000 NULL". A body quoting the measured value returns True. Null control: the shape-only `justification()` passes the planted body, so the value check is what refuses it.
- `git merge-tree --write-tree origin/main 4404f5e7` exits 0 (tree 9b21a314). Merge base is `8b49d50b0a4c3eebee0edeb6ec98aa365e3d004f`. `dev/governance/roles/` three-dot diff to main is empty.
- Claim files, VERSION, manifest, RELEASE_NOTES.md and every `*_budgets.json` are byte-identical to origin/main.
- review_carry.py 6b416a18 -> 4404f5e7: FRESH-REVIEW (branch-only commit 725410a6b).
- Check runs of 4404f5e7, all pages, 40 runs (`ev/check-runs-*.txt`). Concluded reds:
  - `tests / nightly-status` (127408111130): log `NIGHTLY FAILED: slow failed last night.`
  - `governance / delivery-status` (127408110624): log `DELIVERY STATUS OVERDUE — 10 rowed, 12 pending, 17 overdue`, rows of other PRs, "NOT a required context".
  - Both are inherited from base 8b49d50b0a4c3eebee0edeb6ec98aa365e3d004f's ancestry and outside this diff's closure (the diff adds only its own delivery row). The body's `## Red checks` does not name these runs (it was taken at 6b416a18).
- CI: `merge_train.py classify 4404f5e7 --pr 3223` exited 0: `GREEN 4404f5e7435b5a574204a5f51c004a364f7817df pending: none red: none` (18:02 UTC). After that, all 68 check runs of the head (2 pages) had concluded; the only reds were the two inherited checks above.
- Instrument disclosure: the offline harness `ev/harness.sh` is mine (this seat's), not the finder's. The group has no committed finder harness beyond the PR's own self-test rows.
