Fix review: merge 6f0a5c1d5fc82c9bbfcd2e5c16672856c0a480a5
bus-nonce: 287285b4d0ea4887624132a54f026945

# Fix review -- PR #2902, triage s7 batch 46: rule P232-P234 (V146-V148)

Round 1. I reviewed head `6f0a5c1d5fc82c9bbfcd2e5c16672856c0a480a5` in a detached worktree at that
head, against origin/main `aaf8af512`. `dev/governance/roles/` has no diff between the merge base
and origin/main. The diff from `53c4b9cb0` to the head touches only `s6-batch46.md` and its
delivery row. P232-P234 collide with nothing:
- main's maximum is P226;
- #2900 holds P227-P231.

## Results

- P232 REJECT holds.
  - `review_packet.py:327` runs `carry_audit.py check --body {BODY}` on the body alone. `:31`
    and `:308` read as cited, and so does `ev/packet.md:52` of #2900's round-2 review.
  - The merge guard `findings_gate` (`queue_pre_flight.py:176`, called at `:172`) fetches every
    issue comment and calls `ca.finding_rows(body, comments)` at `:192`.
  - `carry_audit.py:91` (VERDICT) and `:189` (`blocked_verdict`) read as cited, and
    `.github/CODEOWNERS:89` is `/tools/audit/carry_audit.py @tvofi`.
  - I re-derived the figure. With #2900's live body and its two `hpo-approver` comments
    (6458631147, 6459350190) in a scratch `--from-dir`, `carry_audit.py --roster-ref origin/main
    sweep --prs 2900` prints `CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted`
    (`ev/p232-sweep.txt`). Those are round-1 F2, F3 and F4 and round-2 F2. Neither blocking F1 is
    counted.
  - `check --comments` on the host's `rev-fr10` verdicts gives 2900: 1, 2891: 2 and 2899: 2, all
    routed. That matches the ruling.
- P233 ACCEPT-narrowed into R10-FLOW-BODY-ONLY holds.
  - These lines read as cited:
    - `body_push.sh:40` refuses a body unless `handoff/<topic>` is the checkout's HEAD.
    - `:73` is the `commit-tree -m "body: $TOPIC"`.
    - `cloud_relay.sh:409-428` is the handoff arm, which reads `bs` from ls-remote.
    - `:392` is `cloud-handoff-failed`.
    - `:421` matches whole lines (`grep -qxF`).
    - `:444` writes `level_line handoff-update` with no why.
    - `:165`'s `level_line` takes `[why]` as its 4th argument.
    - `:711-749` is the bare-origin self-test fixture.
  - `~/.local/state/hpo/cloud-handoff-failed` line 115 is
    `triage-s6-batch45 2d296452f6db74afc8f8dd590f34daf27cb0d6dc`, a bare entry.
  - The roster at `5704c4048` (213 groups) has R10-FLOW-BODY-ONLY at `not-started` with 13
    carries. Its `files` do not include `body_push.sh`, so the ruling routes widening `files` to
    `edit-brief`. Carry 3 is the handoff-job seam and carry 5 is P22's exit 75.
  - The `Code:` predicate is sound: `body_push.sh:39-40` proves the trailer sha equals the
    handoff tip that the relay's `hs` reads.
- P234 ACCEPT-narrowed into R10-PREPR-CAP holds.
  - `prepr.sh` has 3,927 lines.
  - `copies_line` runs a bare `python3` at `:1034`.
  - `recorder_python` starts at `:519` and closes at `:534`, one line past the cited `:533`.
  - Step 6a calls it at `:716`, and the fixtures are at `:2380-2392`.
  - The roster has R10-PREPR-CAP at `done` with 1 carry, and its files are `prepr.sh` and
    `tests/gate_lock.py`. R10-FLY-NO-FOOTERS (carries-open) is the one live `prepr.sh` owner.
  - The false refusal reproduces (`ev/p234-nocopies.txt`):
    - Python 3.11.5 gives `SyntaxError: f-string: f-string: expecting '}'` with rc 1.
    - The seat venv's 3.14.7 gives `closure: no test file defines a symbol production also
      defines` with rc 0.
  - A clean `env -i` PATH resolves `/usr/bin/python3`, which is 3.9.6.
- Mutation proof, re-run (`ev/mutation.txt`):
  - P232 reads as REJECT and P233 and P234 as ACCEPT.
  - Both carries pass.
  - The heading mutant and the DEFER mutant refuse each carry.
  - Three null controls refuse: a missing file, an uncited text, and a carry citing the REJECT.
- Checks and merge state:
  - Live check-runs at the head (`ev/check-runs.txt`): 38 success, 17 skipped, 0 failure.
    `pr-contract` and `gate` are green.
  - `tests / nightly-status` is green at this head (job 122648464745). main's Nightly
    40595637258 is at attempt 2, completed success.
  - The packet refuses nothing, and `carry_audit` routes 0 items.
  - `git merge-tree --write-tree origin/main <head>` exits 0.
- No version file, claim file or budget is touched.

## Findings

- F1 (non-blocking): P234's "5.30 s" for one `recorder_parses` does not reproduce here.
  `/usr/bin/time -p` gives 12.94 s and 11.82 s real, and 5.69 s and 5.67 s user
  (`ev/p234-time.txt`), with the host's load average at 228. The user time agrees with the figure.
  The ruling's binding is the false refusal, not the seconds. Carry: dismissed: load-dependent wall time, conclusion unchanged
- F2 (non-blocking): P233's Cost omits one step. Part (c) needs `update_pr.sh`'s output captured,
  but `cloud_relay.sh:438` streams it to the relay's stderr (`>&2 &`). The fixer must also tee it
  into the per-run `$bd`, a few lines. Carry: dismissed: cost understated by one redirect, trade unchanged
- F3 (non-blocking): P234's "every pull request's handoff runs this step" overstates. `copies_line`
  returns 3 (skip) unless the diff touches a `.py` under `tests/` or `custom_components/`. The
  ruling's own Cost line states that condition. Carry: dismissed: the Cost line is correct
- F4 (non-blocking): I did not re-read the out-of-tree instances: the state-file note for #2890
  and #2891, #2894's pid 18235, and the 03:43:15Z `STALE CHECKOUT` line, which is in a loop stdout
  log I could not locate. The in-tree mechanism and the bare `cloud-handoff-failed:115` entry are
  verified. I also did not re-read the `V146`-`V148` sources: no `proposals.md` is on this host
  under the seat or state directories. Carry: dismissed: out-of-tree logs, in-tree mechanism verified

RESULT p232-sweep: 4 finding items, 4 routed (body + 2 verdicts); packet body-only check 0
RESULT p234-repro: 3.11.5 SyntaxError rc 1; venv 3.14.7 rc 0
RESULT mutation: heading and DEFER mutants refuse P233 and P234 carries; REJECT-cited refused
RESULT checks: 38 success, 17 skipped, 0 failure; nightly-status success
RESULT merge-tree: rc 0
