Fix review: merge 33b128eb7f3e01b7f3a4cfe38f864ce2742095de

bus-nonce: 829c9561a62a9434ae40ceddebdc70ab

## Round

This is round 2. Round 1 was `Fix review: blocked 172afa85d2bc2f68b402217981f22cfb26e86b56 class-open` (`origin/review/2933`, also `probe/rev-2933-357739f4`). That is fewer than four rounds, so `fixer.md` owes a repair, not a re-cut. I measured head `33b128eb7f3e01b7f3a4cfe38f864ce2742095de`, which is the head the PR body's `## Head` names.

## Block closed

The round-1 block was that `review_carry.py` answered `CARRY` for the hand-resolved merge `98c6676a8`, a range that `app_approve.sh --carry` refuses. The harness used here is the finder's: the round-1 reviewer's instance, plus the class census that round 1's class-open called for. It is not the fixer's.

- Instance (ev/instance.txt). At this head, `review_carry.py 32221ca27 98c6676a8` prints `FRESH-REVIEW` with rc 1 and the reason `not the automatic merge of its parents`. `app_approve.sh --carry` over the same range refuses with the same reason, also rc 1. As a null control, the blocked head's `review_carry.py`, run on the same range in the same tree, prints `CARRY` with rc 0.
- Class census (ev/census-head.raw, ev/census-head.txt). Scope: the newest 200 main-into-branch merges reachable from `origin/main` `66974d473`, one range `M^1..M` per merge with main pinned to `M^2`, answered by both instruments. Command: `ev/census.sh`, which is the body's Figures command. Result: `136 CARRY CARRY`, `64 FRESH-REVIEW FRESH-REVIEW`, and 0 mixed lines.
- Census null control (ev/census-null.txt). The same 200 ranges with the blocked head's `review_carry.py` give `136 CARRY CARRY` and `64 CARRY FRESH-REVIEW`, so 64 disagreements. The census can see a disagreement, and at this head it finds none. The body's figure of 63 was taken at `14fbf218d`; the window has since slid by one merge. That is consistent with the body's "re-run, do not carry" note.
- This PR's own moves (ev/own-ranges.txt). Both instruments agree on all five ranges I tried: `172afa85d..33b128eb7`, `004d445ac..5402c2ba9`, `5402c2ba9..33b128eb7` and `c1a5cd91c..004d445ac`, plus the identity range at this head.

## Findings

- Surviving mutant on the degenerate path. In `review_carry.py`'s `app_approve_carry`, I replaced the `raise Undecidable("app_approve.sh --carry answered neither ...")` branch with `return None`, so that "answered neither" is read as CARRY. `--self-test` still reports `26 checks, 0 failed`, so no fixture reaches the fail-closed branch the body and the docstring claim ("2 when it cannot decide (... `app_approve.sh --carry` answering neither)"). I ran the unmutated behaviour by hand: with `tools/pr/app_approve.sh` moved away, the instrument prints `CANNOT DECIDE ... (rc 127)` and exits 2, while the mutant prints `CARRY` and exits 0 (ev/mutants.txt). So the claim holds at this head, but nothing pins it. Carry: dismissed: the fail-closed behaviour is verified by hand at this head (rc 2), and the unpinned branch is reachable only when app_approve.sh is missing or answers outside its two documented lines, so it does not justify a third review round on an otherwise closed block

## Evidence

- Mutation proof, re-run at this head with the tree restored after each mutant (ev/mutants.txt):
  - The delegation removed (`why = None`): 26 checks, 7 failed, the same seven the body lists.
  - The merge predicate set to `if True:`: 26 checks, 8 failed.
  - My own mutant, which accepts any rc 0/1 output from app_approve as carry: 26 checks, 7 failed.
  - My own fail-closed mutant: survives (see Findings).
- Self-tests at this head (ev/selftests.txt): `review_carry` 26/0, `app_approve` 265/0, `bus` 100/0, `cloud_relay` 284/0. These match the body's merged-head figures.
- Delta since the blocked head. The only branch-authored non-merge commit is `c1a5cd91c`, which touches `review_carry.py` (delegating to `app_approve.sh --carry`, plus seven fixtures) and a comment in `bus.sh`. The diff-line digest of the branch's own three-dot diff over the code, policy and workflow files is identical at `c1a5cd91c` and at this head (ev/delta-and-merge.txt).
- Merges in the range (ev/merges-in-range.txt). `8143243c9`, `004d445ac`, `6b65d24a1` and `33b128eb7` are git's automatic merges. `5402c2ba9` is hand-resolved, and I judged its resolution: it takes main's index for `tools/audit/seat/INSTRUMENTS.md`, adds one index line for `review_carry.py`, adds the `--carry` clause to `instruments/app_approve.sh.md`, and adds the new `instruments/review_carry.py.md`. All of it is prose and accurate to the code. `selftest_wiring.py --check` reports `0 unwired` and `0 index gap(s)`.
- `5402c2ba9..33b128eb7` answers `FRESH-REVIEW` from both instruments, because `6b65d24a1`'s automatic resolution of `tests/golden/claimed_drift.txt` is not a pure line union: main replaced lines. This is the conservative cost the body measured ("the rule can refuse content loss, never pass content a review did not see"). It is not a disagreement.
- `git merge-tree --write-tree origin/main 33b128eb7f3e01b7f3a4cfe38f864ce2742095de` exits 0 with tree `e1e61c7bb`, which equals the head's tree. origin/main was `66974d473` at the time.
- Claim files are byte-identical to `origin/main`, and `env_drift.py --claims-only` reports `claims hygiene: origin/main ok`. `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (three-dot).
- `policy_lint.mjs` reports `TOTAL: 0 error(s) across 50 policy file(s)`. Under `--budgets`, `fix-review.md` is at 140/140 lines and 2449/2451 tokens, and `orchestrator.md` is at 294/295 lines and 4251/4251 tokens. No budget file is touched. `tests/structure.py` reports `STRUCTURE RATCHET PASSED`. The policy prose is unchanged since round 1, which judged it. It still needs tvofi's approving review at the head, as the body's `## Approval` states.
- `dev/governance/roles/` on main has no change against this head's merge base, so the contract I followed is current.
- Finder's harness: none is committed. This group implements an owner ruling, not an audit finding. The harness used here is the round-1 reviewer's instance and census command, which this PR now carries in its body. I ran the census myself (ev/census.sh).
- CI on this head (ev/ci.txt) was read from the check-runs API at 10:31Z, after every workflow had concluded. The latest run of every check is `success`, `skipped` or `neutral`, except `tests / nightly-status`, which is answered below. `gate` is green (123394120002). The PR head was still `33b128eb7f3e01b7f3a4cfe38f864ce2742095de` at my last read before publishing.
- Red checks (step 11). At this head `tests / nightly-status` concluded `failure` (job 123369882923): `NIGHTLY FAILED: nightly-ha (stable) failed last night`, from scheduled run 40806276912 on main's head `ee48937`. `pr-contract` first refused twice (123384489819 and 123385575697) because the body's `## Red checks` did not name it while the diff touches `.github/workflows/governance.yml`. I waited rather than verdicting (ev/pr-contract-watch.txt). The body was then edited to name the red: main's `hb:positive_control` runner-load flake, owned by R10-FLY-NIGHTLY-HB, with no cheaper detector. A `pr-contract` run that started after every other workflow had concluded (123393758997, 10:29:46Z) passed, and `gate` passed after it. Per step 11, that green run is the evidence. Independently, this PR's three-dot diff to `governance.yml` is the one added `instrument-self-tests` step and does not touch the nightly lanes. `tests / nightly-status` is not a required check on `main-protect` and does not block.
- Not re-derived: the body's 377-pure/23-not claim-resolution count over 200 first-parent merges. It is a sliding window and figure_lint marks it unverified. I did not re-run it, so it is not verified by me.
