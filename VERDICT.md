Fix review: blocked befd1f54144062002c51c88c0c181eccdd37c00c mutation-vacuous: m8 (confirm_arm after handoff_arm) and m7 (carry_fold_arm before probe_arm) survive the self-test; body at handoff-body/r10-relay-arm-order is stale

bus-nonce: 61be6c484a46a8268476b809ff74eb5a

This is round 2, a handoff review with no pull request at this tip. I measured the handoff tip befd1f54144062002c51c88c0c181eccdd37c00c (base cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf) from a detached worktree. Round 1 blocked 332f882c (verdict/3465 at d1ce0cc571). Its two items are resolved at this tip:
- m2 and m3 are now killed;
- the P603 carry is now on the roster with its control.

The tip does not merge yet, for two reasons below.

## Block

- mutation-vacuous. The new order in `pass()` is the fix (`probe_arm; [ -z "${CONFIRM:-}" ] || confirm_arm; handoff_arm; carry_fold_arm`). The self-test pins only one part of it: that `probe_arm`'s POSTED comes before `handoff_arm`. Two reorderings of that same line pass the full self-test at rc 0, with 422 checks and 0 failed:
  - m8 moves `confirm_arm` behind `handoff_arm` (`ev/mutant-m8.diff`, `ev/RESULT-mutant-m8.txt`). `confirm_arm` posts the confirm for each delivered `review/*` tip. Under m8, a delivered review again waits behind every serial `update_pr.sh` plus full prepr. That is P601's defect, on the `--confirm` path. The body's own sentence names both arms: "ran `handoff_arm` ... before `probe_arm`/`confirm_arm`, so a returned verdict waited". An arm like the existing `aorun` stub would kill m8: a review tip delivered before the pass is confirmed before `handoff_arm` begins.
  - m7 moves `carry_fold_arm` ahead of `probe_arm` (`ev/mutant-m7.diff`, `ev/RESULT-mutant-m7.txt`). `carry_fold_arm` fetches refs and re-runs `body_push.sh` serially per topic. Under m7, that serial work again runs ahead of the probe posts. The body states the order "probe_arm, confirm_arm, handoff_arm, carry_fold_arm", and nothing pins the `carry_fold_arm` slot.

  These are every survivor my drive found at this tip (m1 to m9, listed under Evidence). Both survivors ride this group's re-cut, so neither is carried. For m7, a stated reason that it is equivalent would also settle it.
- body-stale. The body this review is given is BODY.md at `refs/heads/handoff-body/r10-relay-arm-order` (51953f127c, `ev/body-handoff-body-51953f12.md`). It is still the round-1 body, and three things in it are wrong for this tip:
  - its `## Head` names 332f882cf8e9ba5c0415df400d89dda1682babf1, not this tip (step 7). `review_carry.py 332f882c befd1f54` prints FRESH-REVIEW, so that head does not carry (`ev/review-carry.txt`);
  - it quotes "420 checks". This tip runs 422;
  - its Forward-carry routes P603 to R10-REVIEW-DISPATCH-RESIDUE. The roster now records that carry as superseded because it "dropped the control".

  The repaired body is on `handoff-wip/r10-relay-arm-order-body` at 888b11e6 (`ev/body-refused-handoff-wip-888b11e6.md`). It names this tip, 422 checks and `Carry: R10-SEAT-IDENTITY-P5`, with the control. `body_push` refused that body at 13:43 with CARRY-LANDED (`ev/BLOCKED-347b713f.md`), before the fold landed. The destination is now in the tree: `origin/handoff/audit-r10-roster` at 338ad786bc, which contains e661f1ca06. Group R10-SEAT-IDENTITY-P5's carry holds the P603 card verbatim with its self-test, mutation proof, null control and a re-measure instruction for the 18 SKIP moved figure (`ev/carry-destination.txt`). That body still needs `body_push.sh` re-run so it reaches handoff-body. Its Mutation proof section must also cover m7 and m8 after the re-cut.

## Evidence

- RESULT head self-test: `bash tools/audit/seat/cloud_relay.sh --self-test` rc 0, "422 checks, 0 failed" (`ev/selftest-head.tail.log`). This matches the refused body's figure. The handoff-body's 420 was the count at 332f882c.
- Each mutant ran in its own detached worktree at the tip. Each applied exactly one replacement, then ran the full self-test (`ev/mutant-<id>.diff`, `ev/RESULT-mutant-<id>.txt`, `ev/selftest-mutant-<id>.tail.log`):
  - RESULT m1 (body's named mutant, old order `handoff_arm; carry_fold_arm; probe_arm; confirm_arm`): KILLED, rc 1. Failing check: `a verdict returned before the pass is POSTED before handoff_arm starts`. This matches the body.
  - RESULT m2 (delete the `open_prs > "$pst/cloud-prs-open.$$"` line in `pass()`): KILLED, rc 1. Failing check: `one pass under --confirm lists the open PRs once`. Round 1's survivor is now fixed.
  - RESULT m3 (`handoff_arm` always lists, `if false`): KILLED, rc 1. Same failing check. Round 1's survivor is now fixed.
  - RESULT m4 (`confirm_arm` always lists, `if false`): KILLED, rc 1. Same failing check.
  - RESULT m5 (drop the listing `rm -f` at the end of the arm line): KILLED, rc 1, two checks: `the pass leaves no listing file behind` and the lone-`handoff_arm` null control.
  - RESULT m6 (failed listing leaves an empty file, `|| true` in place of `|| rm -f`): KILLED, rc 1. Failing check: `null control: with the open-PR listing failed, the same shape on #68 stays owed`.
  - RESULT m7 (`carry_fold_arm` first): SURVIVED, rc 0. See Block.
  - RESULT m8 (`confirm_arm` after `handoff_arm`): SURVIVED, rc 0. See Block.
  - RESULT m9 (the lone `handoff_arm`'s fallback lists nothing): KILLED, rc 1, 90 checks failed. This shows the null control "a lone handoff_arm lists for itself, once" depends on the fallback.
- m1–m5 ran concurrently, then m6–m9, each in a separate worktree. The self-test makes its own temp dir. Each mutant's outcome matches its own diff.
- Null control for the lister-count arm: on the unmodified tip, both the count arm and "a lone handoff_arm lists for itself, once" are green. m2, m3 and m4 turn the count arm red, and m9 turns the lone-arm check red. So the counter does read the listing path.
- Finder's harness: the triage s6-batch182 log measurement (probe-to-POSTED latency) has no committed harness, as round 1 recorded. I did not re-run it at either end. The self-test arms are the fixer's instruments.
- Class rule: the issue states one seam, the arm order in `pass()`, and the body names no enumeration rule. So this is a one-seam class. Within that seam, the line's other arms are the survivors above.
- Merge with main: `git merge-tree --write-tree origin/main <tip>` rc 0, tree e1d6703aa8, origin/main 60413046e3 (`ev/merge-tree.txt`).
- The diff touches only `tools/audit/seat/cloud_relay.sh` and its instrument doc (`ev/diffstat.txt`). VERSION, the manifest, RELEASE_NOTES and both claim files are untouched.
- `tests/structure.py` at the tip: STRUCTURE RATCHET PASSED (`ev/structure-head.txt`).
- CI: no pull request exists at this tip, so there are no check runs, no review packet and no red to answer. PR #3465's head 76e9852fad has not taken the tip. The owed-reds set is in `ev/owed-reds.txt`.
- The tip I measured is `ev/HEAD.txt`. It was still `refs/heads/handoff/r10-relay-arm-order` when I wrote this verdict.
