Fix review: merge f475901cacf05fc6b106610d90db01cff7e08a07

bus-nonce: b58545582ab7a2110dbcd9a0a5e040fa

## Verdict

Round 4 by the body's own count; the body says it is the re-cut that `fixer.md` owes from the fourth round. Code, tests and harness hold at this head; what is left is paperwork and one equivalent-direction survivor, both below.

## Evidence

- Head: `f475901cacf05fc6b106610d90db01cff7e08a07` is `refs/pull/3626/head` (ls-remote, re-read before the return), which is also the head named in the body's `## Head`. Merge base `ebe83a1b82`. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- CI: `merge_train.py classify f475901cac... --pr 3626` printed WAIT (`pending: gate red: none`) at every poll from 22:19 to 22:38 UTC, then `GREEN f475901cacf05fc6b106610d90db01cff7e08a07 pending: none red: none` at 22:42 UTC (ev/classify-log.txt). After that, `review_packet.py render` reads `## Refusals none`, `gate` success and `governance / instrument-self-tests` success (ev/review-packet.md), so this head introduces no instrument-self-tests red.
- Merge with main: `git merge-tree --write-tree origin/main <head>` exits 0 against origin/main `31117b1029` (ev/merge-tree.txt).
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched in the three-dot diff (ev/version-untouched.txt). No claim file moved and no golden moved, so step 4 has nothing to compare.
- Mutation proof: `python3 tools/audit/seat/hooks_setup.py --self-test` at the head printed `hooks_setup self-test: 74 checks, 0 failed`. That run includes the un-mutated-copy null control and every MUTANTS entry the branch adds, all killed (ev/hooks_selftest.txt).
- Reviewer's own mutants on `tools/audit/seat/hooks/liveness.py`, run with `--no-mutants` and restored afterwards (ev/reviewer_mutants.txt):
  - removed pages never listed: killed (2 FAIL)
  - a content change of a known page ignored: killed
  - manifest omits the by-change pages: killed (3 FAIL)
  - unchanged-page count wrong: killed
  - stale manifest kept when no pending manifest exists: SURVIVED (see Findings)
  - after the restore: `51 checks, 0 failed`
- Null control: the self-test's case "nothing changed since the proof reads the core and the rules only (null control)" passes un-mutated. It goes red under the reviewer's manifest-omission and count mutants, so it discriminates.
- Body figures I re-derived at this head:
  - `TOTAL: 0 error(s) across 52 policy file(s)`
  - `SELF-TEST passed (every perturbed scope refused)`
  - `STRUCTURE RATCHET PASSED`
  - `RULES-SYNC ok` (ev/figures_head.txt)
- `policy_lint.mjs --budgets` on a scratch merge of the head onto origin/main `31117b1029` gave `corpus: ~69748 tokens, cap 69333 +band 500 = 69833`, `role fixer ~6252 ... = 6352` and `role policy ~9985 ... = 10458`. These are identical to the body's figures (ev/budgets_merged.txt). No `*_budgets.json` and no cap file is in the diff.
- Step 14, metric earned: the corpus fits by two mechanisms:
  - excluding `RULINGS.md` through `corpus_excluded.json`, which is the owner ruling quoted verbatim in `RULINGS.md` ("This file should be excluded by the corpus but still needs to be re-read on changes"). The hook implements the re-read side of that ruling, so the exclusion is earned, not gamed.
  - real prose cuts in `orchestrator.md`, `CLAUDE.md` and `proposal-triage.md`.
- Class (step 6): the body names no enumeration rule. My own sweep was `git grep` for `policy-corpus|policy_reread|re-read CLAUDE.md`, scoped to the instruments. It found the post-compaction read set stated only in `liveness.py`, `hooks_setup.py`, `instruments/hooks_setup.py.md`, `sweep_template.md` step 0 and `orchestrator.md` section 0, and the diff updates all five. I read this as a one-seam class; the rule is my own, not the body's.
- Red checks: `merge_train.py owed-reds` lists the set (ev/owed-reds.txt). The body answers the earlier-head reds of `governance / policy-docs`, `governance / env-matrix` and `tests / fast (3.14)` at `91f6dc48e2` and `03c8a59184`. Each answer names a state and a cheaper detector, and the second has a `Carry:`. There is no red at this head.
- Forward-carry: the body routes it to R11-INTAKE-R10-RESIDUE, and the packet's `carry_audit` reads it as routed (1 routed, 0 unrouted). I did not open the roster branch copy.
- No finder's harness applies: this is a roster-group feature, not an audit finding. The harness is the fixer's own self-test in `hooks_setup.py`, and it is committed.

## Findings

- Residual: in `liveness.py` `prove()`, the `except OSError: (state / PROVEN).unlink(missing_ok=True)` branch has no test, and replacing it with `pass` survives the self-test. Keeping a stale manifest only treats pages as changed relative to an older proof, which enlarges the next corpus. The one exception is a page that went X→Y→X between proofs, which is negligible. No read goes unowed. Carry: dismissed: the survivor is on a fail-safe branch whose mutation can only widen the owed read
- Note: body-incomplete: the "Hunks kept and dropped" section omits several cuts in the diff:
  - in `CLAUDE.md`: the "Root-cause remediation" section (its rules stay indexed through `defect-root-cause.md` and `root-cause.md`), the `AGENTS.md` "states no policy" clause and the `babysit/` sentence
  - in `proposal-triage.md`: the sentence "A fix to an instrument a running seat depends on stays local and in-round, ruled by no one."
  - in `orchestrator.md`: the section 1 bullets citing `fixer.md` steps 3 and 8, the section 4 GitHub-tool sentence, and the section 9 propagation bullets

  These are policy deletions the owner should see named before approving. Carry: dismissed: the owner's approving review at this head reads the same diff, and the gate for a policy change is that review
- Note: policy-reference: `CLAUDE.md`'s new "What the repository may carry" names a "security-and-privacy audit dimension". No such brief is in the D0–D15 dimension table. Carry: dismissed: the text is the owner's 2026-11-15 ruling and the owner's review of this hunk decides it

## Friction

none
