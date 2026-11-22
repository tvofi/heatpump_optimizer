# Review packet #3844
head: 6a76c6071db6d7e4abaadcc9b9f4b0605d16c3a5
base: 8ef450936a1786abf4bb9610dc3336da4e77e8de

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=137243144334 success
arch-score / arch-score id=137249428251 success
arm id=137238384145 skipped
budget-raise-gate / budget-raise-gate id=137249440625 success
cancel-superseded id=137249426859 success
codeql id=137249395542 skipped
codeql / Analyze (actions) id=137241156957 success
codeql / Analyze (javascript-typescript) id=137241156902 success
codeql / Analyze (python) id=137241156947 success
gate id=137249395218 success
governance id=137249396160 skipped
governance / env-matrix id=137241156970 success
governance / instrument-self-tests id=137241157018 success
governance / policy-docs id=137241157041 success
governance / record id=137241158208 skipped
governance / wave-script id=137241157016 success
hassfest id=137249395987 skipped
hassfest / hassfest id=137241156843 success
kernel-points id=137249428164 skipped
pr-contract id=137249396399 skipped
pr-contract / pr-contract id=137248428684 success
prelude id=137249395357 success
refresh id=137249395840 success
sweep-self id=137249628327 skipped
tests id=137249445600 skipped
tests / arch-instrument id=137241397541 success
tests / briefs id=137241156913 success
tests / browser id=137241397465 success
tests / ci-ratchet id=137246240445 skipped
tests / claims-autofix id=137245378074 skipped
tests / closure-scope id=137241156901 success
tests / closures id=137241397612 success
tests / closures-autofix id=137246241274 skipped
tests / coverage id=137241399177 skipped
tests / coverage-ratchet id=137241399226 skipped
tests / fast (3.14) id=137241397507 success
tests / graders-head-copy id=137241397792 success
tests / lane-proofs id=137245376789 success
tests / mutation id=137241156973 success
tests / mutation-autofix id=137242531748 skipped
tests / mutation-pins id=137242531034 skipped
tests / nightly-ha id=137241399426 skipped
tests / nightly-status id=137241157038 success
tests / replay id=137241399064 skipped
tests / typing id=137241397467 success
validate id=137249432237 skipped
validate / validate-hacs id=137241156930 success

## Refusals
none

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
diff --git a/dev/programme/delivery/3822.md b/dev/programme/delivery/3822.md
index 16ce753098..3704772e18 100644
--- a/dev/programme/delivery/3822.md
+++ b/dev/programme/delivery/3822.md
@@ -1 +1 @@
-- [#3822](https://github.com/tvofi/heatpump_optimizer/pull/3822) — **open**, audit round 11: land finder box D3-u1a (-)
+- [#3822](https://github.com/tvofi/heatpump_optimizer/pull/3822) — **merged `8ef4509`**, audit round 11: land finder box D3-u1a.
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
diff --git a/dev/programme/delivery/3837.md b/dev/programme/delivery/3837.md
index 86b07c9d43..fe0befa83a 100644
--- a/dev/programme/delivery/3837.md
+++ b/dev/programme/delivery/3837.md
@@ -1 +1 @@
-- [#3837](https://github.com/tvofi/heatpump_optimizer/pull/3837) — **open**, R11-PRE-SHARED-FILES (part 2): r11 pre shared files p2 (R11-PRE-SHARED-FILES)
+- [#3837](https://github.com/tvofi/heatpump_optimizer/pull/3837) — **merged `fc06c46`**, R11-PRE-SHARED-FILES (part 2): r11 pre shared files p2 (R11-PRE-SHARED-FILES).
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
diff --git a/dev/programme/delivery/3850.md b/dev/programme/delivery/3850.md
index 9ca1a71876..d03e708bbf 100644
--- a/dev/programme/delivery/3850.md
+++ b/dev/programme/delivery/3850.md
@@ -1 +1 @@
-- [#3850](https://github.com/tvofi/heatpump_optimizer/pull/3850) — **open**, R11-RCA-BOTMERGE-ROW: root cause of a branch-only budget key carried across main merges (R11-PRE-SHARED-FILES)
+- [#3850](https://github.com/tvofi/heatpump_optimizer/pull/3850) — **merged `024895c`**, R11-RCA-BOTMERGE-ROW: root cause of a branch-only budget key carried across main merges.
diff --git a/dev/programme/delivery/3851.md b/dev/programme/delivery/3851.md
new file mode 100644
index 0000000000..814d8e54ef
--- /dev/null
+++ b/dev/programme/delivery/3851.md
@@ -0,0 +1 @@
+- [#3851](https://github.com/tvofi/heatpump_optimizer/pull/3851) — **merged `eaaaf24`**, build(deps): bump playwright from 1.65.0 to 1.65.1 in /tests/pwlane in the pwlane group.
diff --git a/dev/programme/delivery/3852.md b/dev/programme/delivery/3852.md
new file mode 100644
index 0000000000..1d5e3f2ecc
--- /dev/null
+++ b/dev/programme/delivery/3852.md
@@ -0,0 +1 @@
+- [#3852](https://github.com/tvofi/heatpump_optimizer/pull/3852) — **merged `0c69bd1`**, build(deps): bump actions/create-github-app-token from 3.3.0 to 3.4.0 in the actions group.
diff --git a/dev/programme/delivery/3853.md b/dev/programme/delivery/3853.md
new file mode 100644
index 0000000000..4456b3e889
--- /dev/null
+++ b/dev/programme/delivery/3853.md
@@ -0,0 +1 @@
+- [#3853](https://github.com/tvofi/heatpump_optimizer/pull/3853) — **merged `0ff1b6b`**, build(deps): bump the pip group in /tests with 13 updates.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
