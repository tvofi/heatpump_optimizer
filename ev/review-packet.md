# Review packet #2896
head: 318c9380d3267c141882c82d590949869ee1487a
base: b0b2d7697f8c5baaef2c082d9bf3242b57249e68

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=123124894897 success
arch-score / arch-score id=123124801741 success
arm id=123124611595 skipped
budget-raise-gate / budget-raise-gate id=123124801641 success
cancel-superseded id=123127165653 success
codeql / Analyze (actions) id=123124801549 success
codeql / Analyze (javascript-typescript) id=123124801502 success
codeql / Analyze (python) id=123124801723 success
governance / delivery-status id=123124801666 success
governance / delivery-status-publish id=123124803781 skipped
governance / env-matrix id=123124801536 success
governance / instrument-self-tests id=123124801623 in_progress
governance / policy-docs id=123124801480 success
governance / record id=123124803981 skipped
governance / wave-script id=123124801639 success
hassfest / hassfest id=123124801544 success
kernel-points id=123124803940 skipped
prelude id=123127165830 in_progress
refresh id=123127165844 success
tests / arch-instrument id=123125034631 success
tests / briefs id=123124801615 success
tests / browser id=123125034685 success
tests / ci-ratchet id=123127185735 skipped
tests / claims-autofix id=123127184841 skipped
tests / closure-scope id=123124801697 success
tests / closures id=123125034726 success
tests / closures-autofix id=123126616696 skipped
tests / coverage id=123125034617 success
tests / coverage-ratchet id=123125683182 success
tests / fast (3.14) id=123125034584 success
tests / graders-head-copy id=123125683207 success
tests / lane-proofs id=123127182906 success
tests / mutation id=123124801572 success
tests / mutation-autofix id=123125128353 skipped
tests / mutation-pins id=123125128097 skipped
tests / nightly-ha id=123125036002 skipped
tests / nightly-status id=123124801720 success
tests / replay id=123125035923 skipped
tests / typing id=123125034588 success
validate / validate-hacs id=123124801551 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item cb96a83b: R10-FLOW-TOOLKIT-MODEL
NOTE body item 3fc8ba05: R10-FLOW-TOOLKIT-MODEL
NOTE body item 18487d28: #2436
NOTE body item ad471048: #2437
NOTE body item 66a149b4: #2437
NOTE body item ec54bc5f: R10-ORCH-ROSTER-SCHEMA: R10-ORCH-ROSTER-SCHEMA resolved on origin/handoff/audit-r10-roster
NOTE body item e87d0907: #2429
NOTE body item 66eb85f9: #2438
NOTE body item 73f5f2eb: #2438
NOTE body item 197922d7: R10-ORCH-ROSTER-SCHEMA: R10-ORCH-ROSTER-SCHEMA resolved on origin/handoff/audit-r10-roster
NOTE body item fada85ad: dismissed:cheaper census is the spelling list that failed
NOTE body item 859a2672: R10-ROUND-PLAYBOOK
NOTE body item 2886fa1f: R10-FLOW-TOOLKIT-MODEL
NOTE body item d51bfdf8: #2436
NOTE body item 16da1cb1: #2429
NOTE body item 88fa4f6b: #2438
CARRY-AUDIT: 16 finding item(s): 16 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  unverified node --input-type=module -e "import {rosterIssues} from './tools/policy/brief_lint.mjs'; console.log(rosterIssues().size, rosterIssues('dev/programme/rosters').size)"
             node runs an inline script rather than a file
  ok         python3 -I tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 -I tools/audit/fold_ledger.py check
             `tools/audit/fold_ledger.py` is in the tree at this head
  ok         python3 -I tools/audit/carry_audit.py check --body <this body>
             `tools/audit/carry_audit.py` is in the tree at this head

FIGURES: 4 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/config/bugclasses.json b/dev/audit/config/bugclasses.json
index cbee21360..1b9896542 100644
--- a/dev/audit/config/bugclasses.json
+++ b/dev/audit/config/bugclasses.json
@@ -4567,6 +4567,24 @@
       "doc": [
         "dev/audit/rca/R10-RCA-CLOSURE-ARGV.md"
       ]
+    },
+    "R10-RCA-FRICTION-RESIDUE": {
+      "class": null,
+      "level": "instance-or-process",
+      "subject": "five recurring-friction keys measured at 6eb552157 -- carry-missing 26 PRs / 30 entries, the untaught-class `other` route 52 / 67 over 46 words, the root-cause family 6 / 6 over three words, ci-autofix 3 / 3 and finding-propagation 5 / 5 -- and the carry destination is prose no producing seat may write",
+      "trigger": "assigned by the orchestrator under mandate 6329234399 when R10-RCA-FRICTION went done (PR #2561); group R10-RCA-FRICTION-RESIDUE",
+      "date": "2026-10-27",
+      "status": "proposed",
+      "parts_missing": [
+        "A1 and A2 are a code change in brief_lint.mjs and a merge-step fold, neither in this record's pull request; the derived `other` family, the `root-cause` family, the ci-autofix wait bound and measured-pin rule, and the carry-control enumerator lint are policy or policy-tooling changes, drafted in the record and awaiting the owner"
+      ],
+      "process_state": "(d) carry-missing: the destination is sound, but the producing seat's writable artefact moved with the rosters -- the no-argument rosterIssues() indexes 1 of the 76 live-group issues, so a carry file at a covered issue is accepted instead of refused; (c) other and root-cause: the keying rules are obeyed and the threshold's unit is the spelling, so one obligation splits across 46 untaught words or three root-cause words",
+      "countermeasure": "A1 rosterIssues() reads dev/programme/rosters (1 -> 76 indexed; carry-2492 refused, control 999999 accepted); A2 a merge-time fold writes each body item's id into the destination group's brief, with a post-fold id assertion; B a derived `other (untaught)` family (union 52 PRs, family 46 after the #2410 subtraction); C a `root-cause` family (union 6, family 3); D a recorded refusal for harness and class-open with its cost test; E a ci-autofix wait bound and a measured-pin rule; F a carry-control enumerator lint. B-F are drafted, not landed",
+      "landed": null,
+      "in_tree_home": "dev/audit/rca/R10-RCA-FRICTION-RESIDUE.md",
+      "doc": [
+        "dev/audit/rca/R10-RCA-FRICTION-RESIDUE.md"
+      ]
     }
   },
   "N-registry-leak": {
@@ -5027,4 +5045,4 @@
       "class_rca_on_record": true
     }
   }
-}
\ No newline at end of file
+}
diff --git a/dev/audit/rca/R10-RCA-FRICTION-RESIDUE.md b/dev/audit/rca/R10-RCA-FRICTION-RESIDUE.md
new file mode 100644
index 000000000..5b3e6de12
--- /dev/null
+++ b/dev/audit/rca/R10-RCA-FRICTION-RESIDUE.md
@@ -0,0 +1,446 @@
+# R10-RCA-FRICTION-RESIDUE: five friction keys, and a destination no producing seat may write (#2428, #2436, #2437, #2429, #2438)
+
+The root-cause record for the recurring-friction residue that
+`dev/audit/rca/R10-RCA-HARNESS-FRICTION.md` (#2561) left unmeasured: the keys
+`carry-missing` (#2428, re-filed as #2855), `other` (#2436), `root-cause-unanswered`
+(#2437), and the two rule ids the verdict histogram also counts, `.claude/rules/ci-autofix.md`
+(#2429) and `.claude/rules/finding-propagation.md` (#2438). It ran apart from any
+fix (the root-cause role contract); it lands no production code.
+
+**Merge base and window.** Every figure below was taken on 2026-10-27 with the
+group's merge base at `6eb552157b63d1e98a9653250789d9fe0027b5bc`, which was also
+`origin/main` at the time of measurement. The histogram window is
+`v7.0.4..origin/main`, tag `v7.0.4` = `b448d26063cdb56aef915ceb604b807a885f9d71`.
+Nothing is carried from #2561: its figures are for `v7.0.0..origin/main` at
+`df6ca4bc` and are quoted below only as the control they are.
+
+## 1. The instrument the brief named does not exist
+
+The brief's method is "`rounds.py --stats` over `blocked_rounds.tsv`". It cannot
+be run, and the failure is silent:
+
+```
+$ python3 dev/audit/rca/harness-friction/rounds.py --stats <...>/blocked_rounds.tsv
+rc=0   stdout 0 bytes   stderr 0 bytes
+```
+
+`rounds.py` takes one argument, a **directory** of per-PR `.tsv` files
+(`sys.argv[1]` at its line 14, `glob.glob(os.path.join(sys.argv[1], '*.tsv'))`).
+`--stats` is not a mode; it becomes the directory name, the glob is empty, and
+the script prints nothing and exits 0. The same is true of
+`rounds.py blocked_rounds.tsv`: a file is not a directory. **A zero here is
+vacuous** — it is the exact shape `CLAUDE.md` rule 1 warns about for the gate.
+
+Two instruments do work, and they are the ones used below:
+
+- `node tools/policy/policy_lint.mjs --stats --since v7.0.4`, rc=0 in 669 s
+  (`dev/audit/rca/harness-friction/stats_v7.0.4.txt`). It reads the same
+  verdict grammar `rounds.py` does.
+- `rounds.py <dir>` over the window's 218 fetched per-PR files, one
+  `<PR>.tsv` each (`blocked_rounds_v7.0.4.tsv`, 132 block rows over 84 PRs,
+  plus its SUM lines). The fetch is `fetch_prs.py` in the seat's scratch, and the
+  enumeration `analyse.py`; both use `rounds.py`'s regex verbatim, so this is the
+  same reader, not a second classifier.
+
+**Control: the two readers agree on every key.** The independent enumeration
+finds 132 blocked verdicts over 84 PRs; the histogram's rows reproduce each key's
+distinct-PR count exactly (`carry-missing` 26, `mutation-vacuous` 8, `class-open`
+6, `root-cause-detectable` 3, `harness` 3, `mutation-survivor` 3, `regression` 3,
+`other` 2, …). The denominator is not the window's merge count: **173 of 218**
+merged PRs carried a parsable verdict; 45 carried none (44 of them `record`
+titled). Every rate below states which denominator it uses.
+
+## 2. The counts, at this base
+
+| key | PRs / entries | median min to next verdict | would-open |
+|---|---|---|---|
+| `carry-missing` | 26 / 30 | 103 | yes (#2855) |
+| `mutation-vacuous` | 8 / 9 | 111 | yes (#2660) |
+| `class-open` | 6 / 13 | 153 | yes (#2784) |
+| `mutation-survivor` | 3 / 5 | 119 | yes (#2840) |
+| `root-cause-detectable` | 3 / 3 | 181 | yes (#2875) |
+| `harness` | 3 / 3 | — | yes (#2597) |
+| `regression` | 3 / 3 | 153 | yes (#2860) |
+| `root-cause-unanswered` | 2 / 2 | 219 | no |
+| `root-cause-unrecorded` | 1 / 1 | 73 | no |
+| `other` (literal) | 2 / 3 | 164 | no |
+| the `other` route (untaught ∪ literal) | 52 / 67 | — | no single row |
+
+Twelve would-open lines were printed; `blocked_rounds_v7.0.4.tsv` holds every
+row they are counted from. The keys below are the five the brief scopes, plus the
+two it does not (#2593, #2597) and the four extra issues the roster lists.
+
+## 3. `carry-missing` (#2428, #2855): the destination is prose no producing seat may write
+
+**Named cause.** The rule names two destinations for a finding that constrains a
+live group: the group's `brief` string in the roster, or — only when no live
+group covers the destination issue — a `dev/programme/carries/carry-<N>.json`
+file (`finding-propagation.md`, "Where it goes"; `brief_lint.mjs`'s carry-file
+comment). A fixer reads its roster group and nothing more (`fixer.md`), and the
+PR and its row are written by the orchestrator's `handoff_push.sh`; two seats
+state the consequence in their own friction entries — #2612 "a seat with
+handoff-only write access cannot land a carry into a policy brief (D0.md) or a
+roster", #2708 the dispatch allows pushes only to two return refs so "the
+orchestrator corrects the roster carry". So it cannot write the first. For a
+**group** destination there is no `N` at all, so the second does not exist.
+**The seat's marker names a
+stage; the text that the destination seat reads has no writer on the producing
+PR.** The reviewer blocks step 10 (`carry-missing`) because the destination
+brief does not hold it — which is true, and which no seat on that PR could have
+made untrue.
+
+**Process state: (d), with a (c) component.** The rule is sound; its precondition
+— that the producing pull request can put the text in the destination — was
+removed by the roster's read-only role for a fixer (`fixer.md`, and the two
+measured entries above) and by the roster's move to
+`dev/programme/rosters/` (R10-TICK). The (c) component is the one artefact a
+seat *can* write: a carry file at an issue a live group covers is meant to be
+refused (`brief_lint.mjs` calls it the failure the file replaces), and at this
+base the refusal cannot fire.
+
+**The refusal is blind — #2561's finding, still live, and its destination held
+something else.** `rosterIssues()` with no argument reads
+`.claude/workflows/wave-*-groups.json` and `dev/programme/carries` — not
+`dev/programme/rosters/`, where `roster_lib.py` says the one owner put them.
+#2561's own `## Friction` entry states this finding and measured a planted
+`carry-2428.json` at `0 error(s)`, and routed it `Carry: #201`. At this base:
+
+- `rosterIssues()` indexes **1** issue (457, from the round-3L roster);
+  `rosterIssues('dev/programme/rosters')` indexes **76**, including every live R10
+  group's issues;
+- `dev/programme/carries/carry-201.json` holds no text about this finding — its
+  entries are other RCA findings — so `#201` was accepted as a destination
+  because *a* carry file exists at 201, not because this text landed. Six days
+  later the instrument is unchanged and the finding is in no file a seat reads.
+
+That is `brief_lint.mjs`'s own "case 3, existence not authorship" operating on
+the *finding about itself*. Perturbation and controls, run here:
+
+- as shipped, a carry file at issue 2492 (covered by the live `R10-SAV-COMFORT`)
+  is **accepted**, rc=0;
+- with the programme roster passed, the same file is **refused**: `issue 2492
+  already has a live roster group (wave-r10-groups.json R10-SAV-COMFORT)`;
+- control A, an issue no group covers (999999): accepted under both, so the
+  acceptance above is not a blanket failure to load;
+- control B, issue 457 — the only issue the shipped index sees: refused under the
+  shipped index, so the arm is live, just pointed at the wrong directory.
+
+CI runs the no-argument path (`tests.yml`, `prepr.sh`), so the arm is blind in
+exactly the place it is meant to enforce. Its self-test is green because it
+passes a **fixture** roster directory: the no-argument run here prints
+`TOTAL: 0 error(s) across 48 file(s)` (47 carry files and the round-3L roster),
+while its own acceptance assert prints the refusal against
+`wave-probe-groups.json PROBE-G1` from that fixture. The arm is demonstrated on a
+roster no production run reads.
+
+**The destination-text check is not mechanically decidable, measured.** Two
+predicates over the 205 finding items in the window that name a group
+destination (`pred*.py` in the seat's scratch):
+
+- "the destination brief contains the item" — matched by the 8-hex id
+  `carry_audit.py` prints: fires on **205 of 205**; zero quiet.
+- "the destination brief names the producing PR (`#N`)": fires on **193 of 205**,
+  quiet on 12. Of the fires, **29 are on PRs that were never blocked at all** and
+  merged. A predicate that reddens 29 clean merges is one seats route around —
+  the same conclusion `brief_lint.mjs` records from its own 2026-09-10
+  measurement of 6 of 6, now reproduced on a larger window.
+
+**Cost test.** In `v7.0.4..origin/main`, 30 entries on 26 PRs: **11.9% of the
+window's 218 merges**, against #2561's `v7.0.0` control of 12 of 229 = **5.2%**
+— the key has more than doubled. Elapsed time from each block to that PR's next
+verdict (fixer + CI + reviewer + idle) sums to **5076 min, median 103 min**.
+23 of the 30 entries name a destination group the text is not in; the mentions
+span 20 groups, at most 4 for one (`R10-ORCH-MACHINERY`), so this is not one
+group's neglect. `P(recurrence)=1`: filed in both windows (#2428 at 21/24,
+re-filed as #2855 at 26/30, and this seat reproduces 26/30 exactly). The
+*deterministic* half — the blind index — was recorded once already (#2561,
+2026-10-21, routed to #201) and did not land, so its P is 1 for the finding as
+well as for the class.
+
+**Countermeasure, two parts, both check-shaped.**
+A1. **Point the index at the rosters.** `rosterIssues()`'s no-argument path reads
+`roster_lib.ROSTERS_DIR` as well. Demonstration: indexed issues 1 → 76; the
+carry-2492 file refused; control 999999 still accepted. One line, and its
+red/green control is recorded above. Owned by `R10-FLOW-TOOLKIT-MODEL`, whose
+carry holds A1 and A2 with this acceptance — a group, not a tracking issue,
+because `#201` is the destination that absorbed the last attempt at it.
+A2. **Fold at merge, then assert.** The orchestrator, before merging a PR whose
+body names `Carry: <GROUP>`, appends that item (with the 8-hex id
+`carry_audit.py` computes) to the group's brief. The post-fold assertion is the
+same id predicate that is unusable *pre*-fold: after the fold writes the id it is
+quiet by construction, and it fires if the fold is skipped. That is the
+distinction — the predicate is exact about whether the tool ran, not about
+whether prose is a carry.
+
+Refused: redefining the body's `Carry:` line as the destination. It is the one
+change that would make the count fall without a destination seat ever reading the
+finding, which is what the rule exists to prevent.
+
+## 4. `other` (#2436) and `body-stale` (#2593): one open vocabulary, two readers, no key
+
+**Named cause.** A reviewer can write any class word: `VERDICT_RE` in
+`.claude/workflows/web-fix-wave.js` tolerates a word it was never taught, and the
+wave's `parseVerdict` routes it to `other`. The histogram deliberately keeps the
+raw word as its own row (the drift signal, `policy_lint.mjs`'s family comment).
+The threshold's unit is therefore **the spelling**, and an obligation whose
+spelling changes each time never reaches three: measured here, **46 untaught
+words hold 52 PRs / 67 entries**, and **44 of the words sit at one or two PRs
+each, holding 47 PRs / 56 entries**. **36 PRs were blocked only by untaught
+words** — no taught key saw them at all. The literal `other` row the filings see
+is 2 PRs / 3 entries, while the wave's own `other` route is **52 PRs / 67
+entries, 26× the filed row**.
+
+**Process state: (c).** The grammar, the drift signal and the threshold are each
+obeyed; the intended result — a recurring obligation files an issue — does not
+follow, because nothing folds the open vocabulary. `mutation-vacuous` and
+`mutation-survivor` were taught/declared and their family fires; the untaught
+vocabulary has no family and cannot have a declared one, since a word that is
+untaught is by definition not on a list.
+
+`body-stale` (#2593, 3/3 in `v7.0.2`) is a member of the same vocabulary: in this
+window it is 1 PR, and its siblings `body-head-stale` 2, `body-figure` 1,
+`body-claim-wrong` 1, `figure-false`, `figure-uncited`, `figure-unverified`,
+`figure-wrong`, `figures-unverified` 1 each — **nine spellings of one body-drift
+obligation over 10 PRs, no row at 3**. The filed key cannot recur because the
+spelling moves.
+
+**Cost test.** 36 PRs blocked only by untaught words = **16.5% of 218 merges**
+whose friction has no route to a filing; the derived family below would count
+46 PRs (52 less the 6 held by the already-filed `mutation-survivor` and
+`regression`, the #2410 subtraction). Countermeasure cost: one derived row, O(rows)
+on a pass whose 669 s is the network, not the fold. `P(recurrence)=1` in this
+window alone.
+
+**Countermeasure (drafted; policy tooling, owner approval).** Add a **derived**
+family to `statsFamilies`: every histogram key not in `VERDICT_CLASSES` folds to
+one `other (untaught)` row, members computed at read time so no list can go stale,
+with the #2410 subtraction applied as for the declared families. Demonstration:
+the union is 52 PRs / 67 entries; after subtracting the 6 PRs the filed members
+hold, the family is **46 PRs** and fires. Control: the fold is additive, so every
+taught row — `other` literal included — prints byte-identically; and with no
+untaught word in a window it prints no row, the declared-family rule. Refused:
+teaching 46 words (a list that cannot be complete), and changing `parseVerdict` to
+stop routing to `other` (it would erase the drift signal the histogram is built
+to keep).
+
+## 5. `root-cause-unanswered` (#2437) and its family: one obligation, three words
+
+**Named cause.** The root-cause obligation is written under three class words —
+`root-cause-unanswered` 2 PRs, `root-cause-detectable` 3, `root-cause-unrecorded`
+1 — and `FRICTION_FAMILIES` has no `root-cause` entry. The threshold counts a
+spelling, so the obligation's 6 PRs / 6 blocks are three counts of 1–3. The
+checks named are as fragmented as the words: `closures` (#2632),
+`instrument-self-tests` (#2664), `tests / nightly-ha` (#2753),
+`governance / delivery-status` (#2837), `pr-contract` (#2841 and #2869), and
+`tests/closure.py` selftest (#2869) — **the most any one check reaches is 2 PRs**,
+which is #2437's own finding ("7 blocks, 4 checks, none on 3 or more PRs")
+re-measured, not carried.
+
+**Process state: (c).** The split is deliberate and taught (`fix-review.md` steps
+10–11); the family map was extended for `mutation` (#1825) and `environment` but
+not for this obligation, so its unit is the word.
+
+**Cost test.** 3 of the 6 PRs are invisible to any filing at this base
+(`root-cause-unanswered` 2, `root-cause-unrecorded` 1); the family is 6 PRs, one
+obligation. Countermeasure cost: one member list and one family declaration,
+evaluated in the same pass. `P(recurrence)=1` — this window and #2561's.
+
+**Countermeasure (drafted; policy tooling, owner approval).** Declare
+`{ name: 'root-cause', members: ['root-cause-unanswered', 'root-cause-detectable',
+'root-cause-unrecorded'] }`. Demonstration: union 6 PRs; the filed member
+(`root-cause-detectable`, 3) is subtracted per #2410; **family 3 PRs** and fires.
+Control: #2875 already files the 3-PR member, so this window's marginal filing is
+zero — the family's value is that the *next* window with a different split files
+once instead of not at all, which is the case the map was built for.
+
+**#2479's item, taken here.** Its disposition — "a cross-run count before an
+answer of 'not a recurrence'" — is the count in this section: per check, across
+the window, `pr-contract` 2 PRs and five others 1 each. The method is measured;
+the policy sentence that requires it is the owner's.
+
+**#2875 is unowned.** The 3-PR member that fires in this window is an open issue
+no roster group lists — the routing audit's own subject (`carry_audit sweep
+--issues`), and the same existence-not-ownership gap as #2561's `#201` route.
+The obligation's countermeasure is filed under #2437; the ownership repair is
+`R10-ORCH-ROSTER-SCHEMA`'s, whose STRANDED-carry report names an issue no live
+group lists.
+
+## 6. `harness` (#2597), `class-open` (#2784), `mutation-vacuous` (#2660), `mutation` family (#2410)
+
+**#2597, `harness` 3 / 3.** The three blocks are three different children:
+`class-rule-missing` (#2524), `design-trace-missing` (#2780),
+`finder-harness-misreported` (#2843). **Zero are `harness: class-open`** — the
+compound word #2561 taught a spelling for. #2561's countermeasure held; #2597 is
+a recurrence of the parent word over *different obligations*, not of the class-open
+obligation. Cause: `harness` is a category, and the reviewer's vocabulary offers
+it when the child has no word. State (c). **Refusal, with the cost test:** the
+three children are not one obligation, so a `harness` family would be the wrong
+map (the family map folds siblings of one obligation); teaching three child words
+files each at 1 — below the threshold — and buys no filing; the only real
+alternative, a per-child check, is #2561 §8's and #2704 item 11's twice-recorded
+refusal. Cost of the countermeasure (two policy/tooling edits) exceeds a benefit
+of zero filings in this window; `P` of a class-open recurrence is 0.
+
+**#2784, `class-open` 6 / 13.** Every entry names the seam the change left open
+(#2697 six blocks on one merge-call parser, #2706 a torn write, #2707 an
+agreement lane, #2711 two getter shapes, #2770 a sweep, #2819 a plan slot):
+`class-open` is the reviewer refusing a change that closed some of a class.
+#2561's countermeasure — teach the word and the step — is in force and these six
+are its residue, not its recurrence. State (c), as #2561 §9 records it. The
+further countermeasure is refused in
+#2561 §8 and #2704 item 11; this seat does not reopen that refusal.
+
+**#2660, `mutation-vacuous` 8 / 9.** Control against the fix: 7 PRs / 8 entries
+before `662a380` merged (R10-POLICY-FIXER-MD, 2026-10-25 01:02:55Z) and
+1 PR / 1 entry after, inside this 5.2-day window. #2561's spelling fix and the
+`fixer.md` wording landed and the key fell from 8 entries on 7 PRs to 1 entry on
+1 PR: seven of its eight pre-fix entries are gone. Held; residue 1.
+
+**#2410, `mutation (family)`.** Measured at this base: the member union is
+12 PRs; the filed members hold 11; the family row is **1 PR / 2 entries** — the
+#2410 subtraction is implemented and the family fires only for what no member
+files. Control: without the subtraction the family would be 12, which is the
+double count #2410 records. Held; no new countermeasure.
+
+## 7. `ci-autofix` (#2429): an unbounded wait and an unmeasured claim
+
+Three PRs, three entries, and they are two gaps in one rule:
+
+- #2632 `unclear`: `mutation-autofix` pins only killed mutants, so a site whose
+  only driver times out stays `ADDED UNPINNED`; "nothing tells a seat to stop
+  waiting for the bot after one timed-out pin run".
+- #2698 `cost`: CI's `mutation-pins` shards were still `in_progress` hours after
+  `tests / mutation` concluded, so the pin the body relied on never came.
+- #2834 `cost`: a body wrote ten sites as "pinned by `mutation-autofix`" without
+  driving them, two were survivors the bot could not pin, "which cost a CI round
+  and a fixer round"; the rule says to run `--pin-killed` only when the bot goes
+  red, so a body can predict a pin it has not measured.
+
+**Named cause.** `ci-autofix.md` says to wait for the bot and to run
+`--pin-killed` only on a red; it states no terminating condition for the wait and
+does not require a pin claim to be measured. **State (c):** the rule is obeyed,
+and the two things a seat then does — wait, and assert — have no bound.
+
+**Cost test.** 3 PRs in this 5.2-day window; #2834's owner names its own cost (a
+CI round and a fixer round); #2698 is hours of a seat's wait.
+Countermeasure: one sentence with a bound (if `mutation-pins` has not concluded by
+the next `tests / mutation` conclusion, the pin is owed by the handoff and the body
+says `unmeasured`), plus "a body says `pinned` only when `--pin-killed` ran on
+this head". `P(recurrence)=1` (3 of 3). The countermeasure is a policy edit to a
+capped file, so it is **drafted and left to the owner**, not landed.
+
+## 8. `finding-propagation` (#2438), and C3's #2612 row
+
+Five PRs, five entries, and five different ways a carry is unreadable by its
+destination:
+
+- #2612 `unenforced`: "a seat with handoff-only write access cannot land a carry
+  into a policy brief (D0.md) or a roster" — the same cause as section 3, stated
+  by a seat in October.
+- #2645 `stale`: the carried null control asks to reproduce figures "in no tree
+  or ref this seat can read".
+- #2765 `unclear`: a carry's statistic says "trips at 4 or fewer first-pass
+  merges" where the arm implements incidence.
+- #2708 `unclear`: the dispatch allows pushes only to two return refs, so a
+  refuted reading in a roster carry cannot be corrected by the seat that found
+  it — "the orchestrator corrects the roster carry". This is #2612's write-access
+  condition from the other side: the seat can neither write the destination nor
+  correct it.
+- #2871 `contradiction`: a ruling names `R10-FLY-WIP`, which neither roster
+  holds; the intended group is `R10-FLOW-WIP`.
+
+**Named cause.** A carry is one seat's prose consumed by another, and only its
+*existence* is resolved: a `Carry:` marker to a group not in the roster is
+refused, but a destination that exists and received nothing passes both layers by
+design (`brief_lint.mjs`, cases 3–4), and a carried control's figures and
+statistic are not required to name their enumerator. **State (c).** #2612's row is
+dispositioned here, not left with `R10-BRIEFS-FOLD` (done, and did not implement
+it): its finding is section 3's cause, and its countermeasure is A1 + A2.
+
+**Cost test.** 5 entries over 5 PRs; each is re-derived by the destination seat,
+and two entries record the re-derivation itself (#2871 the fix review corrects
+the group name; #2708 the orchestrator corrects the roster carry). This seat
+cannot time that from the window and does not invent a figure; the countermeasure
+is one lint arm plus one sentence, which cannot cost more than the manual rewrite
+it replaces. `P=1` (5 PRs in this 5.2-day window).
+
+**Countermeasure (drafted; policy, owner approval).** (i) `brief_lint` lints a
+carry's `control` for a resolvable enumerator exactly as it lints `brief`, so
+"the FUTURE-STATE section 2 figures" (#2645) and a bare statistic (#2765) fail;
+control: a control naming `dev/audit/harnesses/x.py` passes. (ii) one sentence in
+`fix-review.md`/`judge.md`: a ruling that names a destination stage states it as a
+`Carry:` marker, so `R10-FLY-WIP` is refused by the existing check instead of
+corrected by hand (#2871). Refused: a policy-wide scan for group-shaped tokens in
+prose — section 3 measures that shape at 205 of 205.
+
+## 9. C1 and C2
+
+**C1, #2452's census cost: recorded refusal.** The `cost` entries say
+`tests/card.mjs` takes 159.43 s of CPU (322.45 s real) and the 182 plants took
+3 h 18 m over six lanes. The census is the *cheap* detector: it replaced a
+spelling list, and a spelling list is the defect it closed (#2317's class, a
+navigation in a handler the dynamic arm did not drive). A cheaper census is the
+spelling list. The cost test therefore fails for every cheaper design and passes
+for this one: the payment buys the class coverage, and no countermeasure is
+proposed. **Not re-measured here**: the plant-driven census needs the solver
+venv, which this record seat does not run; the figure is the producing seat's and
+is labelled as such. `Carry: dismissed: cheaper census is the spelling list that failed`
+
+**C1, #2479's cross-run count: taken.** Section 5 is the count, per check, over
+the window. Dispositioned here; the policy sentence is the owner's.
+
+**C2, this group's `issues` list.** The carry text says "seven numbers"; the
+roster at this base holds **eleven**: 2410, 2428, 2429, 2436, 2437, 2438, 2593,
+2597, 2660, 2784, 2855. The four the carry did not name (2410, 2660, 2784, 2855)
+all fired in the same window, which is itself an instance of this record's
+subject — a carried count is stale by the next window. Every one is dispositioned
+below; none is left unowned. #2428 is closed (superseded by #2855) and is also
+listed by the live `R10-FLOW-JIDOKA`, so it has two owners at this base.
+
+## 10. Dispositions
+
+| issue | key | disposition |
+|---|---|---|
+| #2410 | `mutation (family)` | held: family 1 PR after the #2410 subtraction (control: union 12) |
+| #2428 | `carry-missing` | closed; superseded by #2855, whose 26/30 this record reproduces |
+| #2429 | `ci-autofix` | cause + drafted countermeasure (section 7) |
+| #2436 | `other` | cause + derived-family countermeasure (section 4) |
+| #2437 | `root-cause-unanswered` | cause + `root-cause` family (section 5) |
+| #2438 | `finding-propagation` | cause + control-enumerator lint, and C3's #2612 (section 8) |
+| #2593 | `body-stale` | same vocabulary as `other`; 9 body-drift spellings over 10 PRs / 10 entries, no row at 3 (section 4) |
+| #2597 | `harness` | #2561 held (0 `harness: class-open`); refusal recorded (section 6) |
+| #2660 | `mutation-vacuous` | held: 7/8 before `662a380`, 1/1 after (section 6) |
+| #2784 | `class-open` | measured; the countermeasure refusal stands (section 6) |
+| #2855 | `carry-missing` | cause + A1/A2 (section 3) |
+
+## 11. Not established here
+
+- The census's 159.43 s was not re-timed (needs the solver venv); it is quoted
+  from #2452's `cost` entry and labelled.
+- The brief's `rounds.py --stats` was not run *as named*, because it is not a
+  mode (section 1); the substitute instruments and their agreement are given.
+- `brief_lint`'s no-argument run completes rc=0 (48 files, 0 errors) and lints
+  only the round-3L roster and the carry files; the R10 roster linted explicitly
+  is also 0 errors. The roster-index defect in section 3 was established by
+  calling `rosterIssues()` and `checkCarryShape()` directly, which is the same
+  code the run executes.
+- The policy and tooling changes in sections 3, 4, 5, 7 and 8 are **drafted, not
+  landed**. They are owner-approved changes and this record is not the PR that
+  makes them.
+
+## Evidence
+
+`dev/audit/rca/harness-friction/`:
+
+- `stats_v7.0.4.txt` — the `policy_lint --stats --since v7.0.4` run at
+  `6eb552157`, rc=0, 669 s; one host path in its second line replaced by the
+  `~` form `ref_privacy.py scrub --write` prescribes, nothing else changed.
+- `blocked_rounds_v7.0.4.tsv` — `rounds.py` over the window's 218 per-PR files:
+  132 block rows over 84 PRs and its SUM lines. `blocked_rounds.tsv` (#2561's
+  `v7.0.0` window) is untouched.
+- `rounds.py`, `stats_v7.0.0.txt` — #2561's instruments, unchanged; the control
+  the `v7.0.4` figures are compared against.
+
+Re-measurement is the two commands in section 1, plus the per-PR fetch
+(`gh api` `issues/<n>/comments` and `pulls/<n>/reviews`, first line each,
+`created_at`/`submitted_at`), which reproduces every row.
diff --git a/dev/audit/rca/harness-friction/blocked_rounds_v7.0.4.tsv b/dev/audit/rca/harness-friction/blocked_rounds_v7.0.4.tsv
new file mode 100644
index 000000000..52b91f269
--- /dev/null
+++ b/dev/audit/rca/harness-friction/blocked_rounds_v7.0.4.tsv
@@ -0,0 +1,136 @@
+#2524	2026-10-21T14:54:37Z	harness	class-rule-missing	harness:class-rule-missing	1724
+#2528	2026-10-21T14:36:00Z	vacuous-test	the	vacuous-test	367
+#2528	2026-10-21T20:43:20Z	vacuous-test	the	vacuous-test	1270
+#2579	2026-10-21T20:49:52Z	carry-missing	not	carry-missing	93
+#2579	2026-10-21T22:23:02Z	mutation-survivor	three	mutation-survivor	714
+#2579	2026-10-22T10:17:03Z	mutation-survivor	hand	mutation-survivor	172
+#2579	2026-10-22T13:08:40Z	mutation-survivor	probe	mutation-survivor	119
+#2580	2026-10-21T17:11:40Z	mutation-vacuous	the	mutation-vacuous	42
+#2584	2026-10-21T18:43:54Z	defect	conflicts()	defect	70
+#2584	2026-10-21T19:54:02Z	carry-missing	not	carry-missing	873
+#2589	2026-10-22T08:22:28Z	body-stale	the	body-stale	28
+#2605	2026-10-22T10:30:57Z	mutation-vacuous	the	mutation-vacuous	111
+#2606	2026-10-22T10:35:53Z	claim-refuted	the	claim-refuted	98
+#2628	2026-10-22T22:15:38Z	carry-missing	not	carry-missing	9
+#2629	2026-10-22T23:52:27Z	unpinned-site	the	unpinned-site	160
+#2632	2026-10-23T00:43:02Z	root-cause-unanswered	closures	root-cause-unanswered	17
+#2632	2026-10-23T06:11:42Z	mutation-unpinned	coordinator.py:9568	mutation-unpinned	375
+#2633	2026-10-22T23:58:43Z	merge-conflict	dev/governance/roles/orchestrator.md	merge-conflict	50
+#2633	2026-10-23T00:48:44Z	merge-conflict	the	merge-conflict	110
+#2639	2026-10-23T03:36:44Z	retry-rule-unsound	urllib_wait	retry-rule-unsound	151
+#2645	2026-10-23T03:55:48Z	mutation-vacuous	ci_critpath	mutation-vacuous	66
+#2645	2026-10-23T05:01:30Z	carry-missing	not	carry-missing	45
+#2647	2026-10-23T05:44:33Z	mutation-vacuous	restore's	mutation-vacuous	124
+#2664	2026-10-23T13:37:54Z	root-cause-detectable	instrument-self-tests	root-cause-detectable	255
+#2668	2026-10-23T18:19:05Z	carry-missing	not	carry-missing	103
+#2670	2026-10-23T16:56:24Z	carry-missing	not	carry-missing	81
+#2675	2026-10-24T00:30:15Z	carry-missing	not	carry-missing	94
+#2683	2026-10-24T02:31:11Z	carry-missing	not	carry-missing	33
+#2689	2026-10-24T09:23:46Z	figure-unverified	the	figure-unverified	33
+#2691	2026-10-24T09:56:50Z	carry-missing	G1-G3	carry-missing	214
+#2696	2026-10-24T12:11:04Z	record-contradicts-diff	R10-RCA-CI-RATCHET-RUN-NAME.md	record-contradicts-diff	102
+#2697	2026-10-24T11:07:35Z	mutation-vacuous	callExtent	mutation-vacuous	298
+#2697	2026-10-24T16:05:10Z	mutation-vacuous	MERGE_CALL's	mutation-vacuous	89
+#2697	2026-10-24T17:33:48Z	class-open	MERGE_CALL	class-open	113
+#2697	2026-10-24T19:26:51Z	class-open	spellings	class-open	353
+#2697	2026-10-25T01:19:55Z	class-open	program	class-open	119
+#2697	2026-10-25T03:19:08Z	class-open	a	class-open	139
+#2697	2026-10-25T05:38:05Z	class-open	a	class-open	163
+#2697	2026-10-25T08:20:39Z	class-open	the	class-open	108
+#2697	2026-10-25T10:08:12Z	carry-missing	not	carry-missing	416
+#2698	2026-10-24T13:32:03Z	regression	a	regression	729
+#2704	2026-10-24T13:53:05Z	carry-missing	not	carry-missing	81
+#2704	2026-10-24T15:14:17Z	carry-undisposed	roster	carry-undisposed	294
+#2706	2026-10-24T13:53:31Z	class-open	tests/gate_lock.py	class-open	424
+#2707	2026-10-24T13:58:03Z	class-open	the	class-open	310
+#2709	2026-10-24T14:01:08Z	mutation-vacuous	check's	mutation-vacuous	147
+#2709	2026-10-24T16:28:20Z	carry-missing	not	carry-missing	65
+#2711	2026-10-24T14:18:48Z	class-open	a	class-open	153
+#2711	2026-10-24T16:51:42Z	class-open	a	class-open	207
+#2712	2026-10-24T20:57:50Z	carry-missing	not	carry-missing	171
+#2712	2026-10-24T23:48:23Z	mutation-vacuous	_propagated_slab	mutation-vacuous	44
+#2712	2026-10-25T00:32:45Z	merge-conflict	semantic	merge-conflict	72
+#2712	2026-10-25T01:44:52Z	structure-breach	seam_cut_total	structure-breach	739
+#2712	2026-10-25T14:04:09Z	carry-missing	friction	carry-missing	19
+#2734	2026-10-24T14:36:48Z	dangling-owner	P58	dangling-owner	46
+#2735	2026-10-24T14:37:08Z	figure-uncited	P63	figure-uncited	63
+#2735	2026-10-24T15:40:18Z	host-path	s6-batch5.md	host-path	49
+#2736	2026-10-24T14:55:08Z	policy-loosened	severity	policy-loosened	69
+#2738	2026-10-24T14:55:56Z	ruling-unsound	the	ruling-unsound	28
+#2738	2026-10-24T15:23:39Z	ruling-unsound	the	ruling-unsound	52
+#2738	2026-10-24T16:15:45Z	ruling-unsound	the	ruling-unsound	36
+#2743	2026-10-24T16:04:57Z	brief-lint	P66	brief-lint	49
+#2745	2026-10-24T17:18:43Z	carry-missing	carry	carry-missing	88
+#2745	2026-10-26T19:38:26Z	metric-gamed	tests/structure.py	metric-gamed	601
+#2753	2026-10-24T20:58:13Z	carry-missing	not	carry-missing	358
+#2753	2026-10-25T02:56:10Z	root-cause-unrecorded	tests	root-cause-unrecorded	73
+#2753	2026-10-25T04:09:07Z	ratchet-unrecorded	tests/structure.py	ratchet-unrecorded	139
+#2753	2026-10-25T14:45:30Z	body-figure	the	body-figure	27
+#2755	2026-10-24T19:30:26Z	body-head-stale	the	body-head-stale	27
+#2756	2026-10-24T20:08:11Z	carry-missing	not	carry-missing	324
+#2756	2026-10-25T01:32:18Z	carry-missing	not	carry-missing	96
+#2758	2026-10-24T19:59:42Z	body-head-stale	the	body-head-stale	387
+#2759	2026-10-24T20:19:02Z	figure-false	the	figure-false	40
+#2765	2026-10-24T22:20:33Z	carry-missing	not	carry-missing	171
+#2765	2026-10-25T01:11:38Z	carry-missing	not	carry-missing	15
+#2767	2026-10-24T22:16:05Z	figure-wrong	P88	figure-wrong	176
+#2770	2026-10-24T22:48:08Z	class-open	tools/ci/sweep.py:115	class-open	165
+#2772	2026-10-24T22:48:32Z	ci-red	tests	ci-red	121
+#2772	2026-10-25T00:49:06Z	carry-missing	not	carry-missing	50
+#2773	2026-10-25T05:49:04Z	pr-contract-refused	the	pr-contract-refused	684
+#2775	2026-10-25T00:05:43Z	head-moved	measured	head-moved	265
+#2775	2026-10-25T04:31:08Z	contract-incomplete	learner_progress	contract-incomplete	367
+#2780	2026-10-25T01:13:51Z	harness	design-trace-missing	harness:design-trace-missing	526
+#2797	2026-10-25T09:04:56Z	body-claim-wrong	title	body-claim-wrong	15
+#2798	2026-10-25T09:10:50Z	carry-missing	not	carry-missing	231
+#2799	2026-10-25T13:02:15Z	figures-unverified	body	figures-unverified	19
+#2804	2026-10-25T10:17:29Z	ruling-misrouted	P101	ruling-misrouted	149
+#2807	2026-10-25T13:59:33Z	carry-dest-done	P110	carry-dest-done	24
+#2812	2026-10-25T14:59:11Z	pin-wrong	R10-LEARNER-DEFAULT	pin-wrong	27
+#2813	2026-10-25T15:15:13Z	ruling-refuted	P117	ruling-refuted	11
+#2817	2026-10-25T18:24:13Z	mutation-survivor	two	mutation-survivor	91
+#2818	2026-10-25T15:51:17Z	ruling-refuted	P123	ruling-refuted	22
+#2819	2026-10-25T16:49:37Z	class-open	coordinator.py::_plan_slots	class-open	5
+#2819	2026-10-25T16:54:15Z	class-open	coordinator._plan_slots	class-open	143
+#2819	2026-10-25T19:17:16Z	claim-drift	on	claim-drift	164
+#2819	2026-10-25T22:01:40Z	claim-drift	on	claim-drift	122
+#2820	2026-10-25T17:18:20Z	mutation-survivor	the	mutation-survivor	38
+#2822	2026-10-25T16:59:39Z	released-early	P133's	released-early	15
+#2822	2026-10-25T17:14:51Z	claims	P139	claims	9
+#2823	2026-10-25T17:35:41Z	carry-missing	1ac59f510	carry-missing	21
+#2824	2026-10-25T18:59:52Z	carry-missing	carries	carry-missing	105
+#2825	2026-10-25T19:13:08Z	carry-missing	carry	carry-missing	81
+#2825	2026-10-25T20:34:32Z	regression	pr_bounded's	regression	96
+#2825	2026-10-25T22:10:07Z	nondeterministic-arm	the	nondeterministic-arm	203
+#2825	2026-10-26T01:33:14Z	carry-missing	carry	carry-missing	154
+#2827	2026-10-25T19:50:21Z	ruling-change	P142	ruling-change	44
+#2828	2026-10-25T19:50:34Z	verdict-word	P152-P157	verdict-word	35
+#2829	2026-10-25T19:50:49Z	ruling-unsound	P162	ruling-unsound	35
+#2830	2026-10-25T20:04:45Z	verdict-word	P169-P175	verdict-word	22
+#2830	2026-10-25T20:26:31Z	head-moved	measured	head-moved	14
+#2831	2026-10-25T19:51:06Z	ruling-incomplete	none	ruling-incomplete	36
+#2832	2026-10-25T21:55:35Z	mutation-vacuous	legionella.py:655	mutation-vacuous	496
+#2836	2026-10-25T21:18:28Z	carry-missing	carry	carry-missing	187
+#2837	2026-10-25T22:32:18Z	root-cause-unanswered	governance	root-cause-unanswered	219
+#2838	2026-10-25T22:32:35Z	ci-red	pr-contract	ci-red	286
+#2841	2026-10-26T01:01:44Z	regression	tests	regression	153
+#2841	2026-10-26T03:34:24Z	root-cause-detectable	pr-contract	root-cause-detectable	181
+#2843	2026-10-26T02:21:57Z	harness	finder-harness-misreported:	harness:finder-harness-misreported:	180
+#2843	2026-10-26T05:21:29Z	harness-nondeterministic	the	harness-nondeterministic	152
+#2846	2026-10-26T03:18:27Z	duplicate-ruling	P189	duplicate-ruling	10
+#2849	2026-10-26T05:06:37Z	carry-missing	not	carry-missing	555
+#2852	2026-10-26T07:21:25Z	carry-missing	not	carry-missing	127
+#2864	2026-10-26T15:42:39Z	ci-unconcluded	gate	ci-unconcluded	285
+#2869	2026-10-27T03:53:05Z	root-cause-detectable	six	root-cause-detectable	150
+#2871	2026-10-27T04:40:22Z	carry-missing	P199,	carry-missing	216
+#2877	2026-10-27T11:02:48Z	other	the	other	276
+#2877	2026-10-27T15:39:08Z	other	the	other	68
+#2877	2026-10-27T16:47:17Z	prior	round	prior	49
+#2879	2026-10-27T14:05:20Z	other	the	other	164
+#2879	2026-10-27T16:49:08Z	ruling	"the	ruling	85
+#2881	2026-10-27T14:05:46Z	claim	the	claim	92
+#2881	2026-10-27T15:37:18Z	claim	s6-batch38.md:76-77	claim	70
+SUM harness:class-rule-missing 1 entries 1724 min
+SUM class-open 13 entries 2402 min
+SUM harness:design-trace-missing 1 entries 526 min
+SUM harness:finder-harness-misreported: 1 entries 180 min
diff --git a/dev/audit/rca/harness-friction/stats_v7.0.4.txt b/dev/audit/rca/harness-friction/stats_v7.0.4.txt
new file mode 100644
index 000000000..62d03047f
--- /dev/null
+++ b/dev/audit/rca/harness-friction/stats_v7.0.4.txt
@@ -0,0 +1,245 @@
+GAP: 0 merge(s) recovered from the commit's own "Merge pull request #N" subject after /commits/<sha>/pulls answered []
+WINDOW_CACHE: commit-to-PR map fetched, not served by; per-PR reads fetched, not served by ~/hpo-seats/r10s6/scratch-rca-residue/window.json
+STATS: 218 merged pull request(s) in v7.0.4..origin/main; verdict grammar ["blocked","merge"] over block classes ["mutation-vacuous","harness","null-control","claims","version","head-moved","carry-missing","root-cause-unanswered","preflight-mismatch","class-open","conflict","other","product-tradeoff-regression","metric-gamed","architecture-unsound","root-cause-detectable","root-cause-unrecorded"] read from .claude/workflows/web-fix-wave.js
+STATS COVERAGE: 173 of 218 merged pull request(s) in the window carried a parsable verdict; 45 carried none (#2868 #2863 #2847 #2845 #2795 #2786 #2781 #2774 #2769 #2760 +35 more); the histogram's verdict denominator is 173, not the window's merge count
+STATS COVERAGE BY CLASS: merged pull request(s) carrying no parsable verdict, of each class's window, by the title's type -- record 44 of 51 (#2868 #2863 #2847 #2845 #2795 #2786 #2781 #2769 #2760 #2757 +34 more); build 1 of 2 (#2774); (untyped) 0 of 83; ci 0 of 2; coordinator 0 of 1; depgraph 0 of 1; fix 0 of 8; flow 0 of 1; fly 0 of 1; inputs 0 of 1; plan 0 of 1; policy 0 of 2; rca 0 of 3; roles 0 of 1; roster 0 of 26; train 0 of 1; triage 0 of 33
+STATS ENDPOINTS: parsable verdict(s) by the endpoint they arrived on -- /issues/<n>/comments (issue comment): 383; /pulls/<n>/reviews (review): 0. Both endpoints are read, so a verdict posted as a review is counted rather than read as a merge that carried none.
+STATS ROUNDS: over the 173 merged pull request(s) carrying a parsable verdict, first-verdict yield 90/173 = 0.520 (the first verdict was `merge`), one-round yield 67/173 = 0.387 (merged on that one verdict, no later parsable one). Of the 210 parsable verdict(s) after a pull request's first, by the verdict before each: 32 re-verified a head that moved after a `merge` (19 PR(s), the "head-moved (rework)" row), 132 repaired after a `blocked`, 46 repeated the previous verdict's head. A `Fix review:` line outside the grammar is in none of these; each is reported below.
+
+verdict class (PRs / entries):
+   173 / 251   merge   <- at or over threshold
+    26 / 30    carry-missing   <- at or over threshold
+     8 / 9     mutation-vacuous   <- at or over threshold
+     6 / 13    class-open   <- at or over threshold
+     3 / 5     mutation-survivor   <- at or over threshold
+     3 / 3     root-cause-detectable   <- at or over threshold
+     3 / 3     harness   <- at or over threshold
+     3 / 3     regression   <- at or over threshold
+     2 / 4     ruling-unsound
+     2 / 3     other
+     2 / 3     merge-conflict
+     2 / 2     ci-red
+     2 / 2     root-cause-unanswered
+     2 / 2     verdict-word
+     2 / 2     head-moved
+     2 / 2     ruling-refuted
+     2 / 2     body-head-stale
+     1 / 2     claim
+     1 / 2     claim-drift
+     1 / 2     vacuous-test
+     1 / 1     ruling
+     1 / 1     prior
+     1 / 1     metric-gamed
+     1 / 1     ci-unconcluded
+     1 / 1     harness-nondeterministic
+     1 / 1     nondeterministic-arm
+     1 / 1     duplicate-ruling
+     1 / 1     root-cause-unrecorded
+     1 / 1     ratchet-unrecorded
+     1 / 1     body-figure
+     1 / 1     ruling-incomplete
+     1 / 1     ruling-change
+     1 / 1     released-early
+     1 / 1     claims
+     1 / 1     pr-contract-refused
+     1 / 1     pin-wrong
+     1 / 1     structure-breach
+     1 / 1     carry-dest-done
+     1 / 1     ruling-misrouted
+     1 / 1     figures-unverified
+     1 / 1     contract-incomplete
+     1 / 1     body-claim-wrong
+     1 / 1     figure-wrong
+     1 / 1     carry-undisposed
+     1 / 1     figure-false
+     1 / 1     brief-lint
+     1 / 1     figure-uncited
+     1 / 1     host-path
+     1 / 1     policy-loosened
+     1 / 1     dangling-owner
+     1 / 1     record-contradicts-diff
+     1 / 1     figure-unverified
+     1 / 1     mutation-unpinned
+     1 / 1     retry-rule-unsound
+     1 / 1     unpinned-site
+     1 / 1     claim-refuted
+     1 / 1     defect
+     1 / 1     body-stale
+     1 / 2     mutation (family) (of 12; mutation-vacuous, mutation-survivor file their own)
+CENSUS	verdict class	173	251	merge
+CENSUS	verdict class	26	30	carry-missing
+CENSUS	verdict class	8	9	mutation-vacuous
+CENSUS	verdict class	6	13	class-open
+CENSUS	verdict class	3	5	mutation-survivor
+CENSUS	verdict class	3	3	root-cause-detectable
+CENSUS	verdict class	3	3	harness
+CENSUS	verdict class	3	3	regression
+CENSUS	verdict class	2	4	ruling-unsound
+CENSUS	verdict class	2	3	other
+CENSUS	verdict class	2	3	merge-conflict
+CENSUS	verdict class	2	2	ci-red
+CENSUS	verdict class	2	2	root-cause-unanswered
+CENSUS	verdict class	2	2	verdict-word
+CENSUS	verdict class	2	2	head-moved
+CENSUS	verdict class	2	2	ruling-refuted
+CENSUS	verdict class	2	2	body-head-stale
+CENSUS	verdict class	1	2	claim
+CENSUS	verdict class	1	2	claim-drift
+CENSUS	verdict class	1	2	vacuous-test
+CENSUS	verdict class	1	1	ruling
+CENSUS	verdict class	1	1	prior
+CENSUS	verdict class	1	1	metric-gamed
+CENSUS	verdict class	1	1	ci-unconcluded
+CENSUS	verdict class	1	1	harness-nondeterministic
+CENSUS	verdict class	1	1	nondeterministic-arm
+CENSUS	verdict class	1	1	duplicate-ruling
+CENSUS	verdict class	1	1	root-cause-unrecorded
+CENSUS	verdict class	1	1	ratchet-unrecorded
+CENSUS	verdict class	1	1	body-figure
+CENSUS	verdict class	1	1	ruling-incomplete
+CENSUS	verdict class	1	1	ruling-change
+CENSUS	verdict class	1	1	released-early
+CENSUS	verdict class	1	1	claims
+CENSUS	verdict class	1	1	pr-contract-refused
+CENSUS	verdict class	1	1	pin-wrong
+CENSUS	verdict class	1	1	structure-breach
+CENSUS	verdict class	1	1	carry-dest-done
+CENSUS	verdict class	1	1	ruling-misrouted
+CENSUS	verdict class	1	1	figures-unverified
+CENSUS	verdict class	1	1	contract-incomplete
+CENSUS	verdict class	1	1	body-claim-wrong
+CENSUS	verdict class	1	1	figure-wrong
+CENSUS	verdict class	1	1	carry-undisposed
+CENSUS	verdict class	1	1	figure-false
+CENSUS	verdict class	1	1	brief-lint
+CENSUS	verdict class	1	1	figure-uncited
+CENSUS	verdict class	1	1	host-path
+CENSUS	verdict class	1	1	policy-loosened
+CENSUS	verdict class	1	1	dangling-owner
+CENSUS	verdict class	1	1	record-contradicts-diff
+CENSUS	verdict class	1	1	figure-unverified
+CENSUS	verdict class	1	1	mutation-unpinned
+CENSUS	verdict class	1	1	retry-rule-unsound
+CENSUS	verdict class	1	1	unpinned-site
+CENSUS	verdict class	1	1	claim-refuted
+CENSUS	verdict class	1	1	defect
+CENSUS	verdict class	1	1	body-stale
+CENSUS	verdict family	1	2	mutation (family)
+
+rework (PRs / entries):
+    19 / 32    head-moved (rework)   <- at or over threshold
+CENSUS	rework	19	32	head-moved (rework)
+
+friction rule id (PRs / entries):
+     8 / 8     .claude/rules/gate-scoping.md   <- at or over threshold
+     5 / 5     .claude/rules/finding-propagation.md   <- at or over threshold
+     4 / 6     tools/audit/briefs/fixer.md   <- at or over threshold
+     3 / 3     .claude/rules/ci-autofix.md   <- at or over threshold
+     2 / 3     .claude/rules/brief-citations.md
+     2 / 3     brief
+     2 / 2     environment
+     2 / 2     fixer-env
+     1 / 2     roster
+     1 / 1     round-3-instrument-rewrite
+     1 / 1     entity-heartbeat-load
+     1 / 1     roster-vocabulary
+     1 / 1     roster-stage-derivation
+     1 / 1     stage-flag-stored
+     1 / 1     seat-brief-hold
+     1 / 1     roster-moves-under-a-count
+     1 / 1     policy-cap
+     1 / 1     duplicate-proposal
+     1 / 1     out-of-tree-wiring
+     1 / 1     tests/run.sh
+     1 / 1     carries-omitted
+     1 / 1     tests/entities.py
+     1 / 1     .claude/workflows/agreement.mjs
+     1 / 1     gate-sweep-step-under-bash-env
+     1 / 1     proxy-write
+     1 / 1     R10-PIN-DRIVE-INCONCLUSIVE
+     1 / 1     harness
+     1 / 1     fixer-instrument
+     1 / 1     cloud_dispatch
+     1 / 1     brief-diagnosis
+     1 / 1     tools/audit/harnesses/r10_relay_owed_class_reach.py
+     1 / 1     tools/audit/briefs/orchestrator.md
+     1 / 1     r10_seat_selftests_mutants
+     1 / 1     .claude/rules/ratchet-budgets.md
+     1 / 1     policy_lint.mjs
+     1 / 1     tools/audit/prepr.sh
+     1 / 1     tools/audit/seat/seat_venv.sh
+     1 / 1     fixer
+     1 / 1     fixer-handoff
+     1 / 1     dispatch
+     1 / 1     .claude/rules/defect-root-cause.md
+     1 / 1     .claude/rules/writing-for-agents.md
+     1 / 1     fixes-vs-disposition
+     1 / 1     cloud-seat-toolchain
+     2 / 2     environment (family)
+CENSUS	friction rule id	8	8	.claude/rules/gate-scoping.md
+CENSUS	friction rule id	5	5	.claude/rules/finding-propagation.md
+CENSUS	friction rule id	4	6	tools/audit/briefs/fixer.md
+CENSUS	friction rule id	3	3	.claude/rules/ci-autofix.md
+CENSUS	friction rule id	2	3	.claude/rules/brief-citations.md
+CENSUS	friction rule id	2	3	brief
+CENSUS	friction rule id	2	2	environment
+CENSUS	friction rule id	2	2	fixer-env
+CENSUS	friction rule id	1	2	roster
+CENSUS	friction rule id	1	1	round-3-instrument-rewrite
+CENSUS	friction rule id	1	1	entity-heartbeat-load
+CENSUS	friction rule id	1	1	roster-vocabulary
+CENSUS	friction rule id	1	1	roster-stage-derivation
+CENSUS	friction rule id	1	1	stage-flag-stored
+CENSUS	friction rule id	1	1	seat-brief-hold
+CENSUS	friction rule id	1	1	roster-moves-under-a-count
+CENSUS	friction rule id	1	1	policy-cap
+CENSUS	friction rule id	1	1	duplicate-proposal
+CENSUS	friction rule id	1	1	out-of-tree-wiring
+CENSUS	friction rule id	1	1	tests/run.sh
+CENSUS	friction rule id	1	1	carries-omitted
+CENSUS	friction rule id	1	1	tests/entities.py
+CENSUS	friction rule id	1	1	.claude/workflows/agreement.mjs
+CENSUS	friction rule id	1	1	gate-sweep-step-under-bash-env
+CENSUS	friction rule id	1	1	proxy-write
+CENSUS	friction rule id	1	1	R10-PIN-DRIVE-INCONCLUSIVE
+CENSUS	friction rule id	1	1	harness
+CENSUS	friction rule id	1	1	fixer-instrument
+CENSUS	friction rule id	1	1	cloud_dispatch
+CENSUS	friction rule id	1	1	brief-diagnosis
+CENSUS	friction rule id	1	1	tools/audit/harnesses/r10_relay_owed_class_reach.py
+CENSUS	friction rule id	1	1	tools/audit/briefs/orchestrator.md
+CENSUS	friction rule id	1	1	r10_seat_selftests_mutants
+CENSUS	friction rule id	1	1	.claude/rules/ratchet-budgets.md
+CENSUS	friction rule id	1	1	policy_lint.mjs
+CENSUS	friction rule id	1	1	tools/audit/prepr.sh
+CENSUS	friction rule id	1	1	tools/audit/seat/seat_venv.sh
+CENSUS	friction rule id	1	1	fixer
+CENSUS	friction rule id	1	1	fixer-handoff
+CENSUS	friction rule id	1	1	dispatch
+CENSUS	friction rule id	1	1	.claude/rules/defect-root-cause.md
+CENSUS	friction rule id	1	1	.claude/rules/writing-for-agents.md
+CENSUS	friction rule id	1	1	fixes-vs-disposition
+CENSUS	friction rule id	1	1	cloud-seat-toolchain
+CENSUS	friction family	2	2	environment (family)
+
+CENSUS: 105 key(s)
+
+threshold: 3 or more of one key in the window opens "[policy] recurring friction: <key>". Nothing is opened here.
+
+(window)
+  INFO    [stats] (window): not opened: verdict class "merge" at 173 pull request(s) is the passing verdict .claude/workflows/web-fix-wave.js requires before a merge, so this row counts rework nowhere -- a merge verdict re-verifying a head that moved after a `merge` is counted on the "head-moved (rework)" row, and a repair after a block is on the STATS ROUNDS line. Friction is rework.
+  INFO    [stats] (window): would open "[policy] recurring friction: carry-missing" -- verdict class at 26 in this window, threshold 3. Counted as DISTINCT pull requests (30 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: mutation-vacuous" -- verdict class at 8 in this window, threshold 3. Counted as DISTINCT pull requests (9 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: class-open" -- verdict class at 6 in this window, threshold 3. Counted as DISTINCT pull requests (13 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: root-cause-detectable" -- verdict class at 3 in this window, threshold 3. Counted as DISTINCT pull requests (3 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: harness" -- verdict class at 3 in this window, threshold 3. Counted as DISTINCT pull requests (3 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: regression" -- verdict class at 3 in this window, threshold 3. Counted as DISTINCT pull requests (3 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: mutation-survivor" -- verdict class at 3 in this window, threshold 3. Counted as DISTINCT pull requests (5 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: head-moved (rework)" -- rework at 19 in this window, threshold 3. Counted as DISTINCT pull requests (32 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: .claude/rules/gate-scoping.md" -- friction rule id at 8 in this window, threshold 3. Counted as DISTINCT pull requests (8 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: .claude/rules/finding-propagation.md" -- friction rule id at 5 in this window, threshold 3. Counted as DISTINCT pull requests (5 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: tools/audit/briefs/fixer.md" -- friction rule id at 4 in this window, threshold 3. Counted as DISTINCT pull requests (6 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+  INFO    [stats] (window): would open "[policy] recurring friction: .claude/rules/ci-autofix.md" -- friction rule id at 3 in this window, threshold 3. Counted as DISTINCT pull requests (3 entries in all); recurrence is across occasions, not within one body. Not opened here: a seat measures and files, a report does not.
+
+WOULD OPEN: 12 issue(s)
+rc=0 secs=669
diff --git a/dev/programme/delivery/2896.md b/dev/programme/delivery/2896.md
new file mode 100644
index 000000000..1ee9f6d16
--- /dev/null
+++ b/dev/programme/delivery/2896.md
@@ -0,0 +1 @@
+- [#2896](https://github.com/tvofi/heatpump_optimizer/pull/2896) — **open**, RCA: the friction residue — five keys, named causes and dispositions (R10-RCA-FRICTION-RESIDUE)

