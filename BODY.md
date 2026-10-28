Makes one ruling mechanical (group R10-REVIEW-CARRY). tvofi, 2026-10-27, verbatim: **"if there are no code changes, the previous review can be carried"**. It also carries the group's fourth carry, triage P200 (`dev/programme/triage/s6-batch35.md#P200`): the cloud verdict relay layout stated where the reviewer reads.

The test is a commit range, not an opinion: `git rev-list --count <reviewed>..<new> --not origin/main`. Zero, or a count whose commits are all merges, is a carry. A merge authors no commit -- what it joins is main's history (`--not` drops it) or branch commits, which the range already returns as non-merge commits -- so a merge of the branch's own previous head, the shape `update_pr.sh` re-cuts a head into, is not a change either. Any non-merge commit means the head carries code and takes a fresh review. A body rewrite is not a commit in the range and voids nothing.

Five sites, each demonstrated below:

1. `tools/audit/seat/review_carry.py` (new): prints the branch-only commits and exactly one of `CARRY` / `FRESH-REVIEW`; exit 0/1, and 2 when it cannot decide (an unknown sha). Listed in `tools/audit/seat/INSTRUMENTS.md`.
2. `tools/audit/seat/bus.sh dispatch --reviewed-head`: a refusal, not a warning, when the range is clean -- it names the reviewed head, mints nothing and records nothing. It runs before `origin/main`'s review-packet render, which the merge kept intact: a carried head neither renders a packet nor mints a nonce.
3. `tools/pr/app_approve.sh --carry`: its rule was "every merge must merge a commit on `origin/main`", which refused #2876 at `d08647f05` -- a merge-only move of the branch's own previous head, the commonest clean carry there is. It now applies the same non-merge-commit criterion, and still reads the claim resolution: a `claimnotes` file resolved to the pure union of both parents' lines is not a change; one that drops or rewrites a line is. The literal union rule has a cost, measured in Figures: claim-file resolutions on `main` that are not the pure union each refuse a carry. None of them adds a line neither parent had: the rule can refuse content loss, never pass content a review did not see.
4. The contracts: `fix-review.md` says which head a `merge` verdict attaches to and that it carries while the range is clean; `orchestrator.md` says a second reviewer over a clean range is the error, not diligence.
5. P200: `fix-review.md`'s closing verdict paragraph now states the four things `cloud_relay.sh`'s `relay` refuses on and the file did not: the ref `probe/rev-<pr>-<nonce first 8>`, the commit subject `verdict <pr> <head40>`, the first-line grammar (`Fix review: merge <head40>` or `Fix review: blocked <head40> <class>: <reason>`, class `[a-z-]+`; spelled with its prefix so `check-wave-script.mjs` does not read a placeholder `<class>` as a verdict example), and the `ev/` directory -- beside the two it already stated (the `bus-nonce:` line, an evidence file naming the head), which moved into the same sentence. The verdict file's name stays `cloud_relay.sh`'s alone, and the sentence points there: `policy_lint`'s citation pass refuses a file name absent from the tree, in prose as in backticks (`path ...: not in the tree, and no tag SHA is cited alongside it`, which `tests/entities.py`'s template arm surfaced at this branch before the second commit). The P200 brief rejected a `bus.sh` template verb as a second statement of the relay's checks that can drift; the role-file sentence is a second statement too, so `cloud_relay.sh --self-test` now builds a probe from the templates `fix-review.md` states and relays it -- the sentence cannot drift from the relay without that check going red.

`merge_train.py`'s owner-approval carry answers a different question and is untouched.

Three repairs `prepr.sh` predicted on the earlier head, made before this handoff: `review_carry.py`'s self-test builds its repositories with `tests/throwaway_git.py` (`throwaway git` refused its bare `git init`); its self-test is wired as a step of `governance.yml`'s `instrument-self-tests` (`selftest_wiring.py --check`: `0 unwired`); and `tests/closures.json` lists it among `tests/entities.py`'s inert reads (`ci_predict.py --apply-inert`).

**Payment (P200 binding: `fix-review.md` is at its policy cap).** `policy_lint.mjs --budgets` holds `fix-review.md` at its line and token caps, so the sentence is paid by deletion in the same file, no `*_budgets.json` touched: step 9's two instance examples (`#373's was an issue-body grep, #258's a judge comment` -- motivation, the rule stands without them), step 11's "only the run's own log separates them" (restated by the next sentence, "read the lane's log"), the parenthetical in the publish paragraph (now in the verdict sentence), and the closing paragraph's deference to `web-fix-wave.js` (replaced by the grammar it parses, which `web-fix-wave.js`, `bus.sh verdict_sha` and `cloud_relay.sh` all accept). Considered and not taken: the reviewer-brief fallback in `handover_prompt.py` (the brief's second choice, only where no payment exists; a payment existed), and rewrapping lines to fit the line cap (moves the metric without improving the text).

## Approval

Policy: this changes what a fix reviewer and the orchestrator must do (`dev/governance/roles/fix-review.md`, `dev/governance/roles/orchestrator.md`), so it merges only on tvofi's approving review at this head (`CLAUDE.md`; decision 0009 step 6), or under a mandate in force scoped to it. The ruling it makes mechanical, verbatim: **"if there are no code changes, the previous review can be carried"** (tvofi, 2026-10-27), and the coordinator's 2026-10-27 addition that a claim file resolved to the pure union of both sides is not a change. No cap raised; `policy_budgets.json` is untouched and both role files stay inside it by cutting prose. `.github/workflows/governance.yml` (one added `instrument-self-tests` step) is code-owned too (`CODEOWNERS` `/.github/workflows/`), so the same approving review covers it.

## Head

`32221ca27fadfcf5735889b24cafa162eb395cd8`

Merged `origin/main` at `6d86acc909f7fc465e5736771daf8fa45c1373a4` into the earlier fixer's `6f905c40f7e48f640e849352e0696af5585874f9` (not re-cut); one conflict, `tools/audit/seat/bus.sh`'s `dispatch` signature and usage line, where main's `--harness` and this branch's `--reviewed-head` both stand. Every figure below was re-taken after that merge (2026-10-28, `origin/main` at `6d86acc90`).

## Mutation proof

Each run at the merged tree, mutant applied, the file restored byte-identical after:

- `cloud_relay.sh` (P200), the new check failing first: at the merged tree before the `fix-review.md` edit, `FAIL the probe layout fix-review.md states relays (rc=3, want 0)` -- 276 checks, 1 failed; after it, 276 checks, 0 failed.
- `review_carry.py`, merge predicate mutated (`if len(parents_of(repo, sha)) < 2:` -> `if True:`, every commit carries): `FAIL a merge-only move answers CARRY`, `FAIL a re-cut merge of the branch's own previous head answers CARRY`, `FAIL a newer main ref does not change the answer` -- 14 checks, 3 failed.
- `bus.sh`, refusal branch disabled (`elif [ "$rc" = 0 ]; then` -> `elif false; then`): `FAIL dispatch refuses to mint a nonce over a clean range, naming the reviewed head, and records nothing` -- 94 checks, 1 failed; its null control, `dispatch mints at a head that does carry code`, stays green.
- `app_approve.sh`, the old on-main merge rule restored (`git merge-base --is-ancestor "$2" "$main" || ... return 1` after the two-parent check): `FAIL CARRY: a re-cut merge of the branch's own previous head (#2876's shape) (got '1', want '0')` -- 261 checks, 1 failed.
- `app_approve.sh`, the claim driver's stderr left visible (`2>/dev/null` dropped from the `merge-tree` call): `FAIL with the refusing driver's own words kept out of the carry (got '1', want '0')` -- 261 checks, 1 failed.
- The two carry contract sentences (site 4) are prose no check reads; what is measured is their size -- `policy_lint` budgets hold both role files at or under cap, and `RULES-SYNC ok: every generated rule is the generated form of its source`.

## Null control

- P200: the check fails on each perturbation of the stated layout and on `origin/main`'s `fix-review.md` (rc=3, templates absent), and only this head's text relays. With `fix-review.md` stating `probe/rev-<pr>-<nonce>` (rev-2745's full-nonce defect): 276 checks, 1 failed (the relay finds no ref). With the subject stated as `verdict <head40>`: 1 failed. With `ev/` stated as `evidence/`: 1 failed. Each `FAIL the probe layout fix-review.md states relays`; the full-nonce ref with rc=2, the relay's own refusal.
- At `origin/main`, `review_carry.py` does not exist (`git cat-file -e origin/main:tools/audit/seat/review_carry.py` fails) and `bus.sh dispatch --reviewed-head` dies on the unknown flag.
- #2876 is on `main` now, so its range is empty at the current tip and both rules carry it; the discriminating run pins main to `53c4b9cb0de45bbfadb19ea6adbe15dd7d7034e1`, the first parent of #2876's merge `b2a7e4493`. There, `origin/main`'s `app_approve.sh --carry` prints `CARRY: no ...: b71541154e1f85ed9da2b86cb543a0cf9cbf49bf merges e0237e6d0e860f664512b2970d7ad65a54db8acd, which is not on 53c4b9cb0...`, exit 1; this head's prints `CARRY: yes`, exit 0.
- #2854's range still refuses at this head, from both instruments: `review_carry` `FRESH-REVIEW` (`force-push: 9f424cf74 is not a descendant of fccb88371`), `app_approve` `fccb883716ce7f8677ea64a2107971baa5381ea9 is not an ancestor of 9f424cf742eee1c00ab13a75a926874f72470eab`.

## Figures

- #2876 `253dc4867 -> d08647f05`, main pinned before its merge: branch-only 3, all merges, `CARRY` -- `python3 tools/audit/seat/review_carry.py 253dc4867cf39f2aa9875f5f2540c5b67b7c1018 d08647f0513a5a568b5ac917748df02adf9fded6 --main 53c4b9cb0de45bbfadb19ea6adbe15dd7d7034e1`
- the same at the current tip: branch-only 0, `CARRY` -- the same command without `--main`
- #2854 `fccb88371 -> 9f424cf74`: `FRESH-REVIEW`, force-push -- `python3 tools/audit/seat/review_carry.py fccb883716ce7f8677ea64a2107971baa5381ea9 9f424cf742eee1c00ab13a75a926874f72470eab`
- #2876 carried by `app_approve` -- `bash tools/pr/app_approve.sh --carry 253dc4867cf39f2aa9875f5f2540c5b67b7c1018 d08647f0513a5a568b5ac917748df02adf9fded6 53c4b9cb0de45bbfadb19ea6adbe15dd7d7034e1`
- claim-file resolutions over the last 200 first-parent merges of `origin/main` at `6d86acc90` (2026-10-28 09:5x UTC): 377 pure union, 23 not, and the 23 add 0 lines neither parent had -- `git log --merges --first-parent -n 200 --format=%H origin/main | while read c; do set -- $(git rev-list --parents -n 1 $c); shift; [ $# -eq 2 ] || continue; for f in $(git show origin/main:.gitattributes | awk '$2=="merge=claimnotes"{print $1}'); do got=$(git show $c:$f 2>/dev/null | awk NF | sort -u); want=$({ git show $1:$f 2>/dev/null; git show $2:$f 2>/dev/null; } | awk NF | sort -u); [ "$got" = "$want" ] && echo pure || { echo other; comm -13 <(printf '%s\n' "$want") <(printf '%s\n' "$got") | wc -l | sed 's/^/added /'; }; done; done | sort | uniq -c`. A sliding window: re-run it, do not carry the counts.
- self-tests at this head: `bash tools/audit/seat/cloud_relay.sh --self-test` (276, 0 failed), `bash tools/audit/seat/bus.sh --self-test` (94, 0), `python3 tools/audit/seat/review_carry.py --self-test` (14, 0), `bash tools/pr/app_approve.sh --self-test` (261, 0).
- `fix-review.md` at or under its line and token caps, and the whole policy corpus clean: `node tools/policy/policy_lint.mjs --budgets` (its row) and `node tools/policy/policy_lint.mjs` (`TOTAL: 0 error(s)`).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` (the one script `closure.py select` runs for this diff, `MODE: SCOPED`): `ALL 2467 ENTITY CHECKS PASSED`; `python3 tests/structure.py` rc 0.

## Red checks

`none`

## Forward-carry

`none`

## Friction

- `brief-citations`: stale: the brief names `python3 tools/audit/carry_audit.py pr-body <body>`, and the CLI is `{check,pr,sweep,owners}` with the body arm `check --body <file>`. Carry: dismissed: one command's cost on an out-of-tree brief; `--help` names the arm.
