R10-GH-READ-RESIDUE-P3 (triage P755, carries 0-4): the shared REST core bucket read 0 of 5000 twice on 2026-11-14 and refused dispatches. This cuts the host's repeated reads of rarely-changing objects (conditional ETag reads, item 1), makes the host's call log whole (item 2), closes the shim's record-comment refusal (item 3, already on main) and bounds the ancestry reads of `prepr.sh` (item 4).

Carries of this group, each named with what became of it:
- Carry 0 (ruleset conditional read): built; both ruleset reads of `merge_train.py` and `orchestrator_tick.py` go through `gh_read.ruleset_checks`, which reads through `gh_read.conditional_get`.
- Carry 1 (host-wide call log): built; the shim writes the one log fixed at install, and `gh_calls.py --top` reads it plus a distinct state-dir log, each source labelled.
- Carry 2 (the shim refusing the train's postmerge record comment): re-measured, implemented on main at 0b276e8c0c (0aead91cf4, e899dde4ab); not rebuilt.
- Carry 3 (ancestry reads per commit): built as one read per commit and a kept final read; the cold-run bar is stated in `## Figures`.
- Carry 4 (the shared bucket under a full wave): its cache half is items 1 and 4; the separate-token half is not built, the round-end triage having refused it (P777).

## Head

prepr: passed rc=0 at 6e7fd991c0d184d21c89d0fd18fef1a64cbb890a

6e7fd991c0d184d21c89d0fd18fef1a64cbb890a, on origin/main 98847b99d7bb3238686efd6869f805c89c6d1ff1 at 2026-11-15T20:34Z.

## Mutation proof

Each production predicate deleted or replaced, the named self-test run, the failing check named; restored after.

- `gh_read.conditional_get` sends no `If-None-Match` (`gh_read.self_test`): FAIL "a 304 serves the stored body, from one request that carried the stored ETag", "and the next read is the 304 of the new ETag", "a warm ruleset read serves both reads as 304s".
- `gh_read.conditional_get` never serves the stored body on 304 (`if status == 304 and stored:` to `if False:`): the same three plus "ruleset_checks reads the required set and the strict flag".
- `gh_read.conditional_get` never stores a 200's ETag: FAIL "a 304 serves the stored body, from one request that carried the stored ETag".
- `orchestrator_tick.verdict_levels` drops the full-page fallback (`len(cs) >= gh_read.PER_PAGE`): FAIL "a full first page is read through to the end".
- `orchestrator_tick.Tick.conditional` reads plainly: the self-test crashes in `verdict_levels` (`'list' object has no attribute 'get'`, the plain read's slurp shape) -- killed by crash, not by a named arm.
- `merge_train.Train._checks_rule` reads through a fresh cache dir each time: `_ruleset_etag_self_test` FAIL "a second train process ... reads both rulesets conditionally".
- `shims/seat-gh` logs to `${HPO_STATE_DIR:-$loghome}` (`gh_calls.py --self-test`): FAIL "one log line naming parent and path" and "the call is logged at the install-fixed host log and never at the caller's HPO_STATE_DIR".
- `gh_calls.log_sources` drops the second source: FAIL "a call written with HPO_STATE_DIR unset is counted by --top with it set to another dir" and "the report labels each source's own count".
- `prepr.sh ancestry_reds` keeps a read that has a run pending (the `grep -qx P` guard dropped; run in a detached worktree): FAIL "a commit with a run still pending is read again each time (never kept), the other 519 are kept (got 0:closures:0, wanted 0:closures:1)".

## Null control

- Item 1: with no stored ETag the plain read is made (`gh_read.self_test`, "null control: with no stored ETag the plain read is made"); a corrupt stored file is the plain read; a stored body is never served on a failure.
- Item 2: one log holding one call prints today's tables with no `sources:` table (`gh_calls.py --self-test`, "null control: one log with one call prints today's tables, no sources table").
- Item 4: a 2-commit all-green branch makes 2 calls where the merge base made 3; with the keeping off (`PREPR_ANCESTRY_TTL_S=0`) all 520 commits are read again, so the zero on the warm read is the keeping's.
- Item 3 control: see Forward-carry's item 3 line; `gh_calls.py --self-test`'s "second tree" arms carry the nulls (an untracked, an untracked-in-HEAD, a locally edited and a foreign-repository script are refused).

## Figures

- Item 4, calls of one `ancestry_reds` read over a 520-commit all-green branch, merge base then head: `bash tools/audit/seat/ancestry_calls.sh <prepr.sh>` (landed here: a 520-commit synthetic branch, stub gh counting each check-runs url, real jq) printed `calls=521` at origin/main's `tools/pr/prepr.sh` and `calls=520` at this head: a cold run is not reduced (-0.2 %). The same driver at a 2-commit branch: 3 then 2. The merge base read each commit once and then one commit more for the total (`break` at the first non-empty); the head's one read carries the total.
- Item 4, the repeat run: `lreds` in `prepr.sh --self-test` ("a second run in the hour reads nothing", 520 then 0 calls): -100 % on a run in the hour after one that read the same commits; a commit with a run pending is read again each time. The owner's bar (after more than 20 % below before) is met on a repeat run and not on a cold one; the cold figure is stated, not hidden. The roster pull request's 767 calls per update attempt (the brief's figure, not re-measured here: that pull request is not in this checkout) are cold reads the first time and 0 after.
- Items 1-2, the proof after the merge: `python3 tools/audit/seat/gh_calls.py --top --since <utc>` per endpoint, against the carries' figures (rulesets reads 235 per hour from 120 processes; comments and check-runs per tick pass), re-measured at this group's own base by the orchestrator after the merge; with a warm ETag each of those reads is a 304, which P596 measured as free (`rate_limit` `used` moved 0 by five conditional reads and 6 by five plain).
- Item 1's self-test rows: `python3 tools/audit/seat/gh_read.py` through `record_row.py --self-test`'s call (`gh_read.self_test()`), `python3 tools/audit/seat/orchestrator_tick.py --self-test`, `python3 tools/audit/seat/merge_train.py --self-test`, `python3 tools/audit/seat/gh_calls.py --self-test`, `bash tools/audit/seat/seat_venv.sh --self-test`, `bash tools/pr/prepr.sh --self-test`, `python3 tests/structure.py`, `python3 tests/entities.py`.
- Item 3, the admit is on main: `git merge-base --is-ancestor 0aead91cf4 origin/main && git merge-base --is-ancestor e899dde4ab origin/main` printed success; the shim's second-tree arms are the pin.
- Ruleset reads, the shared owner: the two ruleset reads of `merge_train.py` and `orchestrator_tick.py` call `gh_read.ruleset_checks` (one parse, one required-set rule, `gh_read.required_contexts`), not two copies.

## Red checks

none

## Forward-carry

- Item 3 (carry 2, the shim refusing the train's postmerge record comment): re-measured, not rebuilt. The sounder arm (the guard admits another checkout's own `gh_comment.py` when tracked, unmodified, in a checkout of this repository) is on main at 0aead91cf4 and e899dde4ab, and `gh_calls.py --self-test` pins it with four nulls; no rebuild. Carry: dismissed: implemented on main at 0b276e8c0c, nothing left to build.
- Cold-run bar of item 4: the per-commit reads of a first prepr run still grow with the branch's commits (520 over 520; the bar is met only by repeat runs). A cold bound needs a per-branch runs listing, which cannot say a commit without a run is empty, and `ancestry_reds`'s fail-closed rule (an unread commit stays UNCHECKED) forbids skipping it; it would turn the arm's refusal into a skip. Carry: R11-INTAKE-R10-RESIDUE
- The ETag cache is shared state with no expiry: a ruleset changed by the owner is a 200 on the next read (an ETag changes with the object), so nothing stale is served; the `gh-etag` directory only grows by one file per path read. Carry: dismissed: one file per distinct path (a handful), bounded by the paths the instruments read.
- `R11-PRE-TOKEN-LEDGER` reads the host log this change fixes: the log is now one file at the install-time home, and `--top` reads a second distinct state-dir log only for logs an older shim left. Carry: R11-PRE-TOKEN-LEDGER

## Friction

none
