Fix review: merge 4e71069554593ac37bbd3bb3feaf5e98245618b5

bus-nonce: d5f9d19b9c3a1616e9cb0324913ceb4a

## Summary

Round 1 review of PR #3037 (R10-FLOW-BODY-ONLY, V147, the roster's carry 14) at head 4e71069554593ac37bbd3bb3feaf5e98245618b5 (authored code head cde451a79b4f326211defd961ee0155ce0480b38; the head adds only `dev/programme/delivery/3037.md`). Every part of carry 14, (a) to (c), is built as the roster states it. The five named mutants are killed. The fixture rows and null controls pass. CI is GREEN, and the PR merges cleanly into current origin/main. My own extra mutants left three survivors on the added production lines: two are test gaps on secondary behaviour, the third is near-equivalent. Those gaps and a stale instrument guide go to the group's own brief below; none of them blocks this PR.

## Findings

- Surviving reviewer mutant M2: changing `grep REFUSE "$bd/update.out" | tail -n 1` to `| head -n 1` in `cloud_relay.sh` passes all 294 self-test checks. The carry's rule is "the last line ... that contains REFUSE", but the fixture stub prints only one REFUSE line, so the "last" half is never tested. A stub that prints two REFUSE lines and expects the second would kill it. Carry: R10-FLOW-BODY-ONLY
- Surviving reviewer mutant M5: deleting `cat "$bd/update.out" >&2` passes all 294 checks. The update's output now goes to a file and is replayed to the relay's stderr only after the update ends, and nothing tests that the replay happens. With that line gone, the relay log would silently lose all update output (including the `STALE CHECKOUT` stdout the carry cites from #2900). Carry: R10-FLOW-BODY-ONLY
- The instrument guides were not updated for the new grammar. In `tools/audit/seat/instruments/cloud_relay.sh.md` the handoff arm (around lines 115-118) still documents `OWED <utc> handoff-update <ref> <sha>`, with no `<why>`. It also does not mention `cloud-handoff-failed.why`, the `Code:` comparison, or the new `handoff-body-stale` level kind. `tools/audit/seat/instruments/body_push.sh.md` does not mention the `Code:` trailer. A seat reading the guides would not know a stale body is held. Carry: R10-FLOW-BODY-ONLY

## Evidence

- Head: `git ls-remote origin refs/heads/fix/r10-flow-body-only` reads 4e71069554593ac37bbd3bb3feaf5e98245618b5 when this verdict was written. I measured that head (worktree detached at it). `git diff cde451a7..4e710695` touches only `dev/programme/delivery/3037.md`, as the body says.
- Roles are current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Review packet: rendered here (`ev/review-packet.md`). Gate digest is green, refusals are none, `FIGURES: 8 resolved, 0 not verified, 0 refused`, and carry_audit shows 1 item routed. The finder's harness is "none named". Carry 14 names its controls as the self-test's bare-origin fixture rows, and those are the rows run here.
- CI: `merge_train.py classify 4e71069554593ac37bbd3bb3feaf5e98245618b5` gives `GREEN ... pending: none red: none` (rc 0, `ev/ci-classify.txt`). I read all 55 live check runs on the head, across every run rather than one per check: none failed. `tests / nightly-status` is success at this head. The body's `## Red checks` line names it red on main's ancestry, which carry 4(d) asks for, and no gate check on this head went red, so step 11 owes no root-cause answer.
- Merge: `git merge-tree --write-tree origin/main(0d33c9348b39) 4e71069554593ac37bbd3bb3feaf5e98245618b5` gives tree 0fe4b1536f92, rc 0, with no conflict and no claim-file involvement (`ev/merge-tree.txt`).
- Named mutants: `r10_seat_selftests_mutants.py cloud_relay-35 cloud_relay-36 cloud_relay-37 cloud_relay-38 body_push-3` killed all five, `RESULT survivors=0` (`ev/mutants.txt`).
- I planted body_push-3 by hand in a separate worktree and ran `prepr.sh --self-test`: 429 passed, 2 failed. The two failures are exactly "that body's commit names the handoff head it describes in a Code: trailer (V147)" and "a result body, with no handoff/<topic>, names no Code: (null control)" (`ev/prepr-body_push-3.txt`).
- Reviewer mutants on `cloud_relay.sh` (`ev/reviewer-mutants.txt`):
  - M1 compares `Code:` against the PR `$head` instead of `$hs`: killed, 2 failed.
  - M3 removes `level_set handoff-body-stale`: killed.
  - M4 also records the stale body in `cloud-handoff-failed`: killed, 4 failed.
  - M2 and M5 survived; see Findings.
  - M6 (first `Code:` line instead of last) survived. It is near-equivalent because body_push writes exactly one `Code:` line. Recorded as evidence only.
- Attack (1), the P321 fixture row: a body whose `Code:` names the previous handoff head (`$HS`) runs no update_pr and writes exactly one `handoff-body-stale refs/heads/handoff/topic-a $HS2 body names <sha12>` level line. It records nothing in `cloud-handoff-failed`. The null control, `Code:` naming `$HS2`, updates, and the stale line is gone. Relay self-test at the head: `cloud_relay self-test: 294 checks, 0 failed` (`ev/relay-selftest.txt`).
- Attack (2): a newer body for an unchanged handoff head with the same `Code:` updates, as shown by the null-control row (a fresh commit naming `$HS2`). The comparison is sha equality only: there is no timestamp comparison in the diff, and I grepped the added lines for date and time arithmetic and found none. The case where the PR head already equals the handoff and only the body moved is V191, carry 16. The body marks it owed and this diff does not touch it.
- Attack (3), legacy bodies: a body commit with no `Code:` line updates exactly as it did before this change (the null-control row): it is neither held nor dropped. The body says so: "A body with no `Code:` line (pushed before this change) updates as before."
- Attack (4): the exit-75 rows still pass ("a busy update is tried again on the next pass", "and is not recorded failed", "nor owed"). A refusing stub (`update_pr: REFUSE: X`, exit 1) is tried once, its level line ends in that REFUSE line, and the next pass keeps the line without retrying. `cloud-handoff-failed` keeps its bare `topic-a <sha>` line. With no REFUSE line, the last line (`update_pr: STALE CHECKOUT`) is recorded. The body marks the rest of carry 5 owed: 75 for checked-out-elsewhere, and keying the failure on the body sha.
- Attack (5):
  - There is no new git push site. body_push's push is unchanged; only its commit message changed, and that message still goes through `ref_privacy.py guard --commits`, which prepr's self-test exercises.
  - `python3 tests/throwaway_git.py --check` gives 0 sites refused and 0 stale allow entries. The new rows reuse the fixture's existing `$t/b` repository.
  - `## Red checks` is present and no check on this head is red.
- `python3 -I tools/audit/seat/ledger.py --self-test`: 77 checks, 0 failed. The census row "every kind cloud_relay.sh writes is a ledger kind" passes with `handoff-body-stale` registered.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. The diff moves no budget, closure, golden or claim file.
- `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading are untouched, and no claim file is touched, so steps 4 and 5 are clear.
- Carry numbering: the dispatch brief called V147 "Carry 13". The roster's `carry` list numbers it 14, with carry 13 being auto-open on handoff, and the body's numbering matches the roster. All 16 carries are named in the body. The forward-carry points to the group's own roster brief, which still holds the owed carries.
- Step 6, class: the body names no enumeration rule. The issue is one seam: body_push writes the trailer, and handoff_arm is the only reader of `handoff-body/<topic>` that runs update_pr.sh.
- Step 8: every figure in the body's `## Figures` I re-derived at this head except `tests/closure.py select` and doc_claims/entities. I did not re-run those three: CI's `tests / closure-scope` and the gate are green at this head, and I cite them rather than re-running them.
- Round: 1.
