Fix review: blocked 1386441425905fd0d7bb0571f1bac61ff5d7777b darwin-red: the new null-control arm compares a padded wc to the literal "       1", which a BSD wc under the stub pads twice, so self-test is still 537 passed, 1 failed on macOS

bus-nonce: 6f9931717882a44452cb6b566efc6d3a

## Block

The hotfix exists to make `bash tools/pr/prepr.sh --self-test` pass on a macOS host. At the head it still fails there, just on a different arm. The added null-control line

    st "$(PATH="$PW:$PATH"; printf 'x\n' | wc -l)" "       1" "the padding wc stub pads its count ..."

is itself a raw-`wc` string compare. It is exact only when the underlying `/usr/bin/wc` does not pad. On Darwin `/usr/bin/wc -l` already prints `%8d` (`       1`). The stub then prepends seven more spaces, so the arm gets `              1` (14 spaces) and FAILs. Every macOS full-prepr open or update stays refused, which is the exact symptom P676 was written to remove.

Reproduced on Linux by bind-mounting a BSD-style padding `wc` over `/usr/bin/wc` in a private mount namespace (`ev/bsdwc-emulator.sh`, `unshare -m`), then running the self-test at the head:
`FAIL the padding wc stub pads its count, so the next comparison is measured under it (null control) (got               1, wanted        1)`, `537 passed, 1 failed`, rc=2 (`ev/selftest-head-bsdwc.log`). The fixed clean-tree arm itself passes under that emulation, so the `tr -d ' '` repair is right. Only the null-control assertion is platform-dependent. `ev/double-pad-demo.txt` shows 7 vs 14 leading spaces.

Repair, for the fixer: make the null control independent of the host's padding. For example, assert that the stub's output *differs from* its `tr -d ' '`-stripped form (`[ "$x" != "$(printf %s "$x" | tr -d ' ')" ]`), or that it starts with a space. Then run it under a BSD-style `/usr/bin/wc` the way this review did, or show it on a Darwin host.

## Findings

- Follow-up: the body's sibling sweep (`git grep -n 'wc -[lc]' -- '*.sh'`, string compares lacking `tr -d`/`$(( ))`) says the only site is the clean-tree arm. At the head, though, the diff's own line 2406 is a new raw-`wc` string compare, and it is the one that reds on Darwin. Re-derived sweep in `ev/sibling-sweep.txt`: 8 lines, and every other one is numeric (`-ge`, `-gt`, awk, `$((LOG_MARK + 1))`). The re-cut must re-run the sweep at its own head. This is the third Darwin-only prepr self-test red the body counts toward the P676(b) class barrier (body: "a third triggers the class barrier"). Carry: dismissed: settled within this PR's re-cut (P676 hotfix); the body's own class-barrier count is the owner's to act on and needs no new destination

## Evidence

- Round 1 review at the handoff; no pull request exists yet, so there is no review packet, no CI run and no check to read. RESULT: owed-reds set (`merge_train.py owed-reds`, `ev/owed-reds.txt`): tests / coverage-ratchet, tests / fast (3.14), tests / mutation, tests / typing, validate / validate-hacs. No CI exists, so no red is owed an answer.
- RESULT: head measured 1386441425905fd0d7bb0571f1bac61ff5d7777b (`ev/HEAD.txt`), which is the body's `## Head`. Merge base 6d16af36c26ad5a3d9610a9c8412cc54dc3c12dd. The only changed file is `tools/pr/prepr.sh` (`ev/changed-files.txt`). VERSION, the manifest and RELEASE_NOTES are untouched. No claim file was touched.
- RESULT: `git merge-tree --write-tree origin/main 1386441425905fd0d7bb0571f1bac61ff5d7777b` gave tree af4f9e4fb2e329b71e66bc7fca100e070a71388c, rc=0: it merges cleanly.
- RESULT: mutation proof reproduced. With `| tr -d ' '` deleted from the clean-tree arm (worktree `wtm`), self-test gives `FAIL and the in-place run leaves the work tree clean, under a wc that pads its count (got        0, wanted 0)`, `537 passed, 1 failed` (`ev/selftest-mutant-linux.log`). That matches the body. So on Linux the test fails on the old line, as claimed.
- RESULT: head self-test on Linux: the first run went concurrently with the BSD run in the same worktree and showed 2 unrelated policy-rot fixture FAILs (shared-worktree interference, `ev/selftest-head-linux.log`). Solo re-run: `538 passed, 0 failed`, rc=0 (`ev/selftest-head-linux-alone.log`). That matches the body on Linux.
- RESULT: under the BSD-style wc, head self-test is 537 passed, 1 failed, on the null-control arm (Block above). The body's "538 passed, 0 failed" holds only on a non-padding wc.
- `fix-review.md` has not drifted between the merge base and origin/main. Only other roles changed.
- The full prepr `entities.py` REFUSE disclosed in the body was not re-run: it is a heavy run, and the diff touches no file that check reads.
