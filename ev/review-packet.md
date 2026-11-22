# Review packet #3844
head: 4c875cad33394e55efacc65ffa85ff061eda182e
base: eaaaf24e5becdf9682e961cc3ca33f25df920438

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=137209062105 success
arch-score / arch-score id=137222654475 success
arm id=137208694933 skipped
budget-raise-gate / budget-raise-gate id=137222653846 success
cancel-superseded id=137222653049 success
codeql id=137222631184 skipped
codeql / Analyze (actions) id=137222653863 success
codeql / Analyze (javascript-typescript) id=137222654180 success
codeql / Analyze (python) id=137222654016 success
gate id=137222655519 success
governance id=137222665108 skipped
governance / env-matrix id=137222654716 success
governance / instrument-self-tests id=137222654025 success
governance / policy-docs id=137222654590 success
governance / record id=137222654113 skipped
governance / wave-script id=137222653973 success
hassfest id=137222631110 skipped
hassfest / hassfest id=137222654658 success
kernel-points id=137222668307 skipped
pr-contract id=137222632329 skipped
pr-contract / pr-contract id=137222656686 success
prelude id=137222684306 success
refresh id=137222673550 success
sweep-self id=137222925708 skipped
tests id=137222631273 skipped
tests / arch-instrument id=137222654837 success
tests / briefs id=137222653921 success
tests / browser id=137222654527 success
tests / ci-ratchet id=137222655931 skipped
tests / claims-autofix id=137222655402 skipped
tests / closure-scope id=137222653903 success
tests / closures id=137222655247 success
tests / closures-autofix id=137222655691 skipped
tests / coverage id=137222654877 skipped
tests / coverage-ratchet id=137222655758 skipped
tests / fast (3.14) id=137222655439 success
tests / graders-head-copy id=137222655811 success
tests / lane-proofs id=137222655953 success
tests / mutation id=137222653870 success
tests / mutation-autofix id=137222655868 skipped
tests / mutation-pins id=137222655313 skipped
tests / nightly-ha id=137222654765 skipped
tests / nightly-status id=137222654102 success
tests / replay id=137222655278 skipped
tests / typing id=137222655281 success
validate id=137222631512 skipped
validate / validate-hacs id=137222679789 success

## Refusals
moved-head: the pull request's head is 9a152f177a3ae3849cbaeb806dc6c77b7198b02b, not the dispatched 4c875cad33394e55efacc65ffa85ff061eda182e
head-note: ## Head does not name the dispatched head 4c875cad33394e55efacc65ffa85ff061eda182e -- repair: the body's ## Head must name 4c875cad33394e55efacc65ffa85ff061eda182e; `tools/audit/seat/update_pr.sh record/autofix - <body-file>` (PR branch record/autofix)

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/delivery_status.py
             `tests/delivery_status.py` is in the tree at this head

FIGURES: 1 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3728.md b/dev/programme/delivery/3728.md
index 32273bfc3b..b30a8f40f7 100644
--- a/dev/programme/delivery/3728.md
+++ b/dev/programme/delivery/3728.md
@@ -1 +1 @@
-- [#3728](https://github.com/tvofi/heatpump_optimizer/pull/3728) — **open**, R11-SEAM-kernel-step: one plan step kernel (R11-SEAM-kernel-step)
+- [#3728](https://github.com/tvofi/heatpump_optimizer/pull/3728) — **merged `4ebd430`**, R11-SEAM-kernel-step: one plan step kernel (R11-SEAM-kernel-step).
diff --git a/dev/programme/delivery/3729.md b/dev/programme/delivery/3729.md
index d95d02f4e1..179b19697e 100644
--- a/dev/programme/delivery/3729.md
+++ b/dev/programme/delivery/3729.md
@@ -1 +1 @@
-- [#3729](https://github.com/tvofi/heatpump_optimizer/pull/3729) — **open**, R11-SEAM-ratchets: ratchets (R11-SEAM-ratchets)
+- [#3729](https://github.com/tvofi/heatpump_optimizer/pull/3729) — **merged `f269ecc`**, R11-SEAM-ratchets: ratchets (R11-SEAM-ratchets).
diff --git a/dev/programme/delivery/3735.md b/dev/programme/delivery/3735.md
index 771f99440a..0d78d6dee1 100644
--- a/dev/programme/delivery/3735.md
+++ b/dev/programme/delivery/3735.md
@@ -1 +1 @@
-- [#3735](https://github.com/tvofi/heatpump_optimizer/pull/3735) — **open**, R11-SEAM-ratchet-raise: ratchet raise (R11-SEAM-ratchet-raise)
+- [#3735](https://github.com/tvofi/heatpump_optimizer/pull/3735) — **merged `59b17e9`**, R11-SEAM-ratchet-raise: ratchet raise (R11-SEAM-ratchet-raise).
diff --git a/dev/programme/delivery/3737.md b/dev/programme/delivery/3737.md
index ad60a38cb7..2673a169f6 100644
--- a/dev/programme/delivery/3737.md
+++ b/dev/programme/delivery/3737.md
@@ -1 +1 @@
-- [#3737](https://github.com/tvofi/heatpump_optimizer/pull/3737) — **open**, R11-CARRY-DRAWMAP: r11 carry drawmap (R11-CARRY-DRAWMAP)
+- [#3737](https://github.com/tvofi/heatpump_optimizer/pull/3737) — **merged `35402f7`**, R11-CARRY-DRAWMAP: r11 carry drawmap.
diff --git a/dev/programme/delivery/3814.md b/dev/programme/delivery/3814.md
index 5f1da62025..8667e19032 100644
--- a/dev/programme/delivery/3814.md
+++ b/dev/programme/delivery/3814.md
@@ -1 +1 @@
-- [#3814](https://github.com/tvofi/heatpump_optimizer/pull/3814) — **open**, audit round 11: land finder box D3-top6 (-)
+- [#3814](https://github.com/tvofi/heatpump_optimizer/pull/3814) — **merged `e4c929b`**, audit round 11: land finder box D3-top6.
diff --git a/dev/programme/delivery/3821.md b/dev/programme/delivery/3821.md
index e2cf9cf7cd..532cb355ac 100644
--- a/dev/programme/delivery/3821.md
+++ b/dev/programme/delivery/3821.md
@@ -1 +1 @@
-- [#3821](https://github.com/tvofi/heatpump_optimizer/pull/3821) — **open**, R11-SEAM-card: dashboard card hit targets, type and spacing scale, status colours, failure text, history retention (R11-SEAM-card)
+- [#3821](https://github.com/tvofi/heatpump_optimizer/pull/3821) — **merged `608c95d`**, R11-SEAM-card: dashboard card hit targets, type and spacing scale, status colours, failure text, history retention.
diff --git a/dev/programme/delivery/3832.md b/dev/programme/delivery/3832.md
index 3bde92fcf9..e4b22258de 100644
--- a/dev/programme/delivery/3832.md
+++ b/dev/programme/delivery/3832.md
@@ -1 +1 @@
-- [#3832](https://github.com/tvofi/heatpump_optimizer/pull/3832) — **open**, ci: absorb main's measured selftest reads (7 steps, 738 reads) (R11-HOTFIX)
+- [#3832](https://github.com/tvofi/heatpump_optimizer/pull/3832) — **merged `726e5bb`**, ci: absorb main's measured selftest reads (7 steps, 738 reads).
diff --git a/dev/programme/delivery/3836.md b/dev/programme/delivery/3836.md
index 8ea4970e80..b6af1baf54 100644
--- a/dev/programme/delivery/3836.md
+++ b/dev/programme/delivery/3836.md
@@ -1 +1 @@
-- [#3836](https://github.com/tvofi/heatpump_optimizer/pull/3836) — **open**, roster: land the round-11 roster from handoff/audit-r10-roster 320a1ada
+- [#3836](https://github.com/tvofi/heatpump_optimizer/pull/3836) — **merged `6f6a85c`**, roster: land the round-11 roster from handoff/audit-r10-roster 320a1ada.
diff --git a/dev/programme/delivery/3839.md b/dev/programme/delivery/3839.md
index a121027045..fd0598e7ba 100644
--- a/dev/programme/delivery/3839.md
+++ b/dev/programme/delivery/3839.md
@@ -1 +1 @@
-- [#3839](https://github.com/tvofi/heatpump_optimizer/pull/3839) — **open**, rca-open-axis: axis block and repeat-axis escalation (R11-RCA-3729-OPEN-AXIS) (R11-RCA-3729-OPEN-AXIS)
+- [#3839](https://github.com/tvofi/heatpump_optimizer/pull/3839) — **merged `505ed38`**, rca-open-axis: axis block and repeat-axis escalation (R11-RCA-3729-OPEN-AXIS).
diff --git a/dev/programme/delivery/3840.md b/dev/programme/delivery/3840.md
index 8b3d0b1ee4..a7c3b1ce32 100644
--- a/dev/programme/delivery/3840.md
+++ b/dev/programme/delivery/3840.md
@@ -1 +1 @@
-- [#3840](https://github.com/tvofi/heatpump_optimizer/pull/3840) — **open**, fix(policy): one gitRead with a 64 MiB maxBuffer for tree-sized git reads (HOTFIX-BRIEF-LINT-MAXBUFFER)
+- [#3840](https://github.com/tvofi/heatpump_optimizer/pull/3840) — **merged `35c3e31`**, fix(policy): one gitRead with a 64 MiB maxBuffer for tree-sized git reads.
diff --git a/dev/programme/delivery/3842.md b/dev/programme/delivery/3842.md
index 7d13df2b0a..a27d604e44 100644
--- a/dev/programme/delivery/3842.md
+++ b/dev/programme/delivery/3842.md
@@ -1 +1 @@
-- [#3842](https://github.com/tvofi/heatpump_optimizer/pull/3842) — **open**, R11-RCA-ENOBUFS: root cause of the brief_lint maxBuffer red (#3840) (R11-RCA-ENOBUFS)
+- [#3842](https://github.com/tvofi/heatpump_optimizer/pull/3842) — **merged `2ceb62b`**, R11-RCA-ENOBUFS: root cause of the brief_lint maxBuffer red (#3840).
diff --git a/dev/programme/delivery/3843.md b/dev/programme/delivery/3843.md
index c1185f53cf..10fe8c68aa 100644
--- a/dev/programme/delivery/3843.md
+++ b/dev/programme/delivery/3843.md
@@ -1 +1 @@
-- [#3843](https://github.com/tvofi/heatpump_optimizer/pull/3843) — **open**, R11-RCA-MODEX: root cause of PR-local ratchet rows breaking on bot main merges (#3735) (R11-CLOSEOUT-CLEANUP)
+- [#3843](https://github.com/tvofi/heatpump_optimizer/pull/3843) — **merged `40e513e`**, R11-RCA-MODEX: root cause of PR-local ratchet rows breaking on bot main merges (#3735).
diff --git a/dev/programme/delivery/3844.md b/dev/programme/delivery/3844.md
new file mode 100644
index 0000000000..a0a2db73a3
--- /dev/null
+++ b/dev/programme/delivery/3844.md
@@ -0,0 +1 @@
+- [#3844](https://github.com/tvofi/heatpump_optimizer/pull/3844) — **open**, record: delivery rows (autofix)
diff --git a/dev/programme/delivery/3846.md b/dev/programme/delivery/3846.md
index 5b10861812..3fc466e28f 100644
--- a/dev/programme/delivery/3846.md
+++ b/dev/programme/delivery/3846.md
@@ -1 +1 @@
-- [#3846](https://github.com/tvofi/heatpump_optimizer/pull/3846) — **open**, ci: read introduced self-test reds by the diff's scope; track the rerun and supersede seat drivers (CI-CARDS)
+- [#3846](https://github.com/tvofi/heatpump_optimizer/pull/3846) — **merged `3a98735`**, ci: read introduced self-test reds by the diff's scope; track the rerun and supersede seat drivers.
diff --git a/dev/programme/delivery/3851.md b/dev/programme/delivery/3851.md
new file mode 100644
index 0000000000..814d8e54ef
--- /dev/null
+++ b/dev/programme/delivery/3851.md
@@ -0,0 +1 @@
+- [#3851](https://github.com/tvofi/heatpump_optimizer/pull/3851) — **merged `eaaaf24`**, build(deps): bump playwright from 1.65.0 to 1.65.1 in /tests/pwlane in the pwlane group.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
