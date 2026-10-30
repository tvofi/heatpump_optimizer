Fix review: blocked edf1cba7cda43790435d1d4b5aa1b3b24562912a carry-missing: not carried to R10-FLY-STAMP-CHECK-NOTES

bus-nonce: a5ab5bbb07c0ed8390787b5a4e2299ee

Round 1 of fix review. Measured head: edf1cba7cda43790435d1d4b5aa1b3b24562912a (still the PR head when read). Merge base e77418f9b48f89421bd72b0ab511c057341c7fa4; roles diff merge-base...origin/main empty.

## Block

Step 10 (finding-propagation.md, Enforcement: "the producing PR does not merge until the carry is in the tree"). The body's first `## Forward-carry` item hands `tools/release/stamp.py` `get_rest` (an unretried GitHub REST read; the class's open seam) to R10-FLY-STAMP-CHECK-NOTES, with a brief and control. That brief is not written in the destination: at origin/handoff/audit-r10-roster tip 4f54f1d94ccc0e0375d3a125dda098ee7afa9d60 the group's `carry` is `[]` and its `brief` says nothing of `get_rest`, retry or transport; `git grep get_rest` over dev/programme and .claude/workflows finds nothing at the roster tip, at 78c0bb77b (the SHA the body cites, for the group's own carries), at this head or at origin/main. The body names no roster SHA at which this carry was written. So the carry exists only in the PR body, which is a record, not propagation. Repair: append the carry (control and re-measure instruction as the body states them) to R10-FLY-STAMP-CHECK-NOTES on handoff/audit-r10-roster with roster_edit.py append-carry, read it back with brief_lint.mjs, and name that roster SHA in the body. The code itself passes every other step below; nothing in tools/ci/ghapi.py needs to change.

## Findings

- The body dismisses `dev/audit/harnesses/r10_main_gate_replay.py`'s unretried urlopen read, a sibling seam the body's own enumerator returns, because #2731 has no live group. finding-propagation.md routes a sibling seam to a new issue filed by the same PR or to a carry file `dev/programme/carries/carry-<N>.json` ("creating it is part of the finding"), not to dismissal. Not a block alone: step 6 counts it as dispositioned, and the harness is a one-shot replay of a finished group. Settling which destination applies is the orchestrator's call. Carry: #2731

## Evidence

- RESULT selftest-head: `python3 -I tools/ci/ghapi.py --self-test` → `ghapi self-test: 32 checks, 0 failed` (ev/selftest.txt). Base 507a9ec26 ghapi: `19 checks, 0 failed`. Both match the body.
- RESULT mutants: `r10_seat_selftests_mutants.py ghapi-1..ghapi-10` → all KILLED rc=1 by self-test FAILs, `RESULT survivors=0` (ev/mutants.txt). The fail counts match the body (ghapi-4 8, ghapi-5..8 2 each, ghapi-9 4, ghapi-10 12).
- RESULT own-mutants (ev/own_mutants.txt). Dropping `or nap is None` and dropping the final `(None,)` attempt are both killed, by a TypeError crash rather than a named FAIL. Retrying 4xx, removing the backoff, and broadening `except TRANSPORT` to `except Exception` are each killed with 1 failed. The checks that kill them are the 404-not-retried, backoff-recorder and null-control/rate-limit arms.
- RESULT null-control: the base `get` spliced with the head `self_test` gives `32 checks, 8 failed`. The 8 are exactly the transient and persists arms of the four failures (ev/null_control.txt), which matches the body. To build it I had to add `import http.client` to the spliced file for the test's IncompleteRead.
- RESULT class-rule: `git grep -n "urlopen(" -- tools dev/audit/harnesses .github` returns 7 hits (ev/enumerator.txt). Each one is dispositioned in the body: ghapi in the diff; record_row behind gh_read (plus its stub); stamp 1826 get_rest carried (see Block); stamp 2214 a POST; replay harness dismissed (see Findings); d6_page_anchors not the GitHub API. No undispositioned seam.
- RESULT archscore: `score.py --diff 507a9ec26` → `Architecture score: dS +0.0000 NULL` (ev/archscore.txt), which matches the body.
- Code reading: `_request` catches HTTPError before TRANSPORT sees it, so an HTTP answer is never retried as transport. RateLimited and ApiError are not TRANSPORT subclasses, so a rate limit still raises at once. A POST goes through `_request` directly with no loop.
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched (507a9ec26..0c66226e6). The diff writes no claim file and no budget file.
- Merge: `git merge-tree --write-tree origin/main edf1cba7cda43790435d1d4b5aa1b3b24562912a` exit 0, no conflict (ev/merge-tree.txt).
- CI at this head (check-runs API): 0 failures. 6 runs were still in_progress when read: tests/fast (3.14), closures, coverage, arch-instrument, governance/instrument-self-tests, codeql python. Their outcome is unverified by this review (ev/ci.txt). The body's `## Red checks: none` is consistent with what had concluded.
- The body's head section names edf1cba7cda43790435d1d4b5aa1b3b24562912a, which is the head measured here.
