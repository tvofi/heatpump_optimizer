# Review packet #2980
head: 3fbbb46f67f3905a804f458068fb3cf8a266e9e3
base: 1148ee635e8278ebbb033b524d54001b2a89218c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=123935495964 success
arch-score / arch-score id=123935440264 success
arm id=123935321105 skipped
budget-raise-gate / budget-raise-gate id=123935440341 success
cancel-superseded id=123935327018 success
codeql / Analyze (actions) id=123935440306 success
codeql / Analyze (javascript-typescript) id=123935440180 success
codeql / Analyze (python) id=123935440231 success
governance / delivery-status id=123935440362 success
governance / delivery-status-publish id=123935441632 skipped
governance / env-matrix id=123935440269 in_progress
governance / instrument-self-tests id=123935440251 in_progress
governance / policy-docs id=123935440319 success
governance / record id=123935441561 skipped
governance / wave-script id=123935440325 success
hassfest / hassfest id=123935440321 success
kernel-points id=123935441774 skipped
prelude id=123935327061 success
refresh id=123935326629 success
tests / arch-instrument id=123935599092 success
tests / briefs id=123935440253 success
tests / browser id=123935599101 in_progress
tests / closure-scope id=123935440419 success
tests / closures id=123935599134 in_progress
tests / coverage id=123935599019 in_progress
tests / fast (3.14) id=123935599076 in_progress
tests / mutation id=123935440330 success
tests / mutation-autofix id=123935597227 skipped
tests / mutation-pins id=123935597618 skipped
tests / nightly-ha id=123935600472 skipped
tests / nightly-status id=123935440282 success
tests / replay id=123935600878 skipped
tests / typing id=123935599064 in_progress
validate / validate-hacs id=123935440240 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git log -1 --format=%cI
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         gh pr view 2976
             gh pr view: every long flag accepted

FIGURES: 1 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2980.md b/dev/programme/delivery/2980.md
new file mode 100644
index 000000000..ce6a134be
--- /dev/null
+++ b/dev/programme/delivery/2980.md
@@ -0,0 +1 @@
+- [#2980](https://github.com/tvofi/heatpump_optimizer/pull/2980) — **open**, triage: s7 batch 64, P293 carry_audit Evidence items (R10-TRIAGE-S7)
diff --git a/dev/programme/triage/s6-batch64.md b/dev/programme/triage/s6-batch64.md
new file mode 100644
index 000000000..669ac6694
--- /dev/null
+++ b/dev/programme/triage/s6-batch64.md
@@ -0,0 +1,165 @@
+# Proposal triage, session s7, batch 64 (P293-P294)
+
+The rolling batch (V182) after batch 63 (#2974, merge verdict at `ddd88d3ed`, not yet merged).
+Facts were read at origin/main `043b111d0` and on the remote `verdict/<pr>` refs.
+
+## P293: carry_audit's evidence arm flags a reviewer's measurements as unrouted findings
+
+Verdict: ACCEPT, narrowed, as one carry on R10-FLY-CARRY-DISPOSITION, which owns
+`tools/audit/carry_audit.py`'s item classifier (its P-G carry, lead inheritance in `items()`). Two
+of the three over-fire classes measured below are accepted. The proposal's first arm is rejected:
+counting an `## Evidence` item as a finding only when LEAD leads it. That would drop two classes
+the arm exists to catch, both pinned in the self-test today:
+- "a defect left in place, not blocking, under the Evidence heading is a finding (#2465's shape)";
+- "a deferral under the Evidence heading is a finding".
+
+The second arm is accepted for a check's state only. Freeing every clause that calls something
+"not this PR's" would free a pre-existing defect a reviewer found and left in place, which is a
+finding that owes a route.
+
+Source: the orchestrator's triage-queue line of 2026-10-30T00:33Z. The train parked #2969 (item
+`c21695db`) and #2955 (item `158ad202`) on `## Evidence` items that are a reviewer's
+measurements. The proposal: an evidence item counts only when LEAD leads it; the NONBLOCK
+exemption covers any clause that calls a check not required or not this PR's; measure the
+over-fire rate on the last 30 merge verdicts.
+
+Instances. The sample is the 30 highest-numbered `verdict/<pr>` refs whose `VERDICT.md` opens
+`Fix review: merge`, #2936 to #2974. Each was run through `carry_audit.items(text, True)` at
+`043b111d0`.
+- **Rate.** 9 items flagged in all. 7 of them are in `## Evidence` (`why` = `evidence`), in 5 of
+  the 30 verdicts (#2937, #2939, #2955, #2959, #2969). On a read of each, none of the 7 is a
+  finding. All 7 are measurements.
+- **Class A: a red check that is not the PR's. 4 items.**
+  - #2937 `19d896fa`: "the packet's red-unanswered refusal on it does not block here".
+  - #2939 `f76b3ac3`: "nightly-status is not a required context and does not block: `gate`
+    concluded green". The carve-out refuses to free it because of its `(?!\s*:)` guard.
+  - #2955 `158ad202`: "it is NOT one of the required contexts on main-protect and does not block
+    a merge".
+  - #2959 `dde38e84`: "It is not this pull request's and does not block".
+  The tripping word in each is NONBLOCK's `does not block`. `NOT_REQUIRED` frees only the exact
+  shape `not (a )required (context|check)[,] [and] does not block`.
+- **Class C: a NONBLOCK word inside a code span. 1 item.** #2969 `c21695db`: the CLI flag
+  `` `--bump minor` ``, written twice, matches `\bminor\b`.
+- **Class B: the review packet's own "advisory" label. 2 items.**
+  - #2939 `3c055bc1`: "Its one advisory is hot-file: ...".
+  - #2959 `50a530e7`: "The packet advisory `HPO_BUS_TRAIN_STATE is unset` ...".
+
+Cost: S. All of it is in `items()` and `NOT_REQUIRED` in `tools/audit/carry_audit.py`, plus self-test
+rows. `carry_audit.py` has no `policy_lint.mjs --budgets` row, and the `--budgets` output at
+`043b111d0` names it 0 times. Benefit, measured: 5 of the 7 over-fires clear, and with them every
+flagged item of #2937, #2955 and #2969. #2939 and #2959 keep one class-B item each. Each
+over-fire costs a park and a dismissal line, or a body patch.
+
+Binding: R10-FLY-CARRY-DISPOSITION is not started, and its other carries are larger. This carry
+touches only the classifier (`items()` and `NOT_REQUIRED`), so the orchestrator may dispatch it on
+its own ahead of the group's `landed` / `land-ops` carries, on the same file. Until it lands, the
+workaround is unchanged: `Carry: dismissed (item <id>)`.
+
+The carry:
+1. **Code spans.** In a verdict's `## Evidence` arm, LEAD, DEFERRED and NONBLOCK read the item
+   with code spans removed, using the module's own `CODE_SPAN`. A code span is a literal (a flag,
+   a path, a check name), not the reviewer's prose. Fixture: #2969's `c21695db` text goes from
+   flagged to clear.
+2. **A check's state.** The `NOT_REQUIRED` carve-out also frees the clause in three shapes:
+   - "not one of the required contexts" or "not a required context" followed by up to a few
+     words (`on main-protect`), then `and does not block`, with an optional `a merge`;
+   - "not this pull request's" or "not this PR's", joined by `and` to `does not block`, but only
+     in an item that names a red check (a backticked `<job>` or `<caller> / <job>`, or the words
+     `red` / `failure`);
+   - the same clause ending in `:` when what follows names the gate's state (`gate` passed or
+     green).
+   Fixtures: #2937 `19d896fa`, #2939 `f76b3ac3`, #2955 `158ad202` and #2959 `dde38e84` go from
+   flagged to clear.
+3. **Null controls, each still a finding:**
+   - the existing #2465-shape row (a defect left in place, not blocking);
+   - the existing deferral row;
+   - a new row, "a pre-existing defect in the parser is not this pull request's and does not
+     block", which names no check;
+   - "`minor` drift, noted for a later tightening", where DEFERRED reads outside the span.
+4. **Mutation.** Each of the two arms has its own mutant: dropping the code-span strip re-flags
+   `c21695db`, and dropping the new shapes re-flags the four class-A items.
+5. **Declined: class B.** The two class-B items keep costing a dismissal each. Freeing "advisory"
+   by context is the word-level second classifier the P-G carry declined (s4 P-G, carried
+   verbatim on this group). An advisory a reviewer reports can be a real note, so it is not
+   freed. Re-measure on the next 30 merge verdicts after the fix lands. If class B is still the
+   only over-fire left and runs above 2 in 30, the lever is `review_packet.py` naming its
+   environment advisories as such, not a carry_audit word list.
+
+## P294: the tick never names a merge verdict that is waiting on its approval
+
+Verdict: ACCEPT, extended, as a new S fly-in, R10-FLY-TICK-APPROVAL-OWED. The proposal's level is
+accepted as written. One catch-all line is added: it is the countermeasure for the class, and the
+new level alone does not give one. No separate root-cause seat is owed. The reasons are under
+Binding.
+
+Source: the orchestrator's message of 2026-10-30, P294. `verdict_levels()` prints MERGE-READY only
+for a `merge` verdict at the head on a PR whose `mergeStateStatus` is CLEAN or UNSTABLE. Approval is
+what turns a code-owned PR from BLOCKED/REVIEW_REQUIRED to CLEAN, so a merge verdict at the head
+of an unapproved PR prints nothing. The proposal: add `APPROVAL-OWED: #N <head8>` for BLOCKED +
+REVIEW_REQUIRED + a merge at the head; `owed_unactioned.py`'s `FAMILY` parses it; and the
+self-test gets a red arm.
+
+Instances, read at origin/main `1148ee635`:
+- **The gap is in the code.** In `tools/audit/seat/orchestrator_tick.py`, `verdict_levels`
+  (line 653) has two arms:
+  - line 689, `kind == "merge" and at == head and ms in ("CLEAN", "UNSTABLE")`, which prints
+    MERGE-READY;
+  - line 691, `kind == "blocked" and at == head`, which prints BLOCKED-UNFIXED.
+  A merge at the head while BLOCKED falls through both and prints nothing. The docstring (lines
+  654-660) states the level's purpose: "#2401 sat merge-ready ... unacted, because only events
+  reached it".
+- **The PR list does not carry the state the new level needs.** `prs()` (line 552) asks for
+  `number,headRefOid,headRefName,isDraft,mergeStateStatus,title,createdAt,updatedAt,author`, and
+  `reviewDecision` is not among them. So the fix has to add the field, not only an arm.
+- **The three PRs, on the verdict refs.**
+  - `verdict/2962` reads `Fix review: merge 9ce0179f`, committed 2026-10-29T19:56Z.
+  - `verdict/2976` reads `Fix review: merge 1381df1f`, committed 2026-10-30T02:02Z.
+  - `verdict/2977` reads `Fix review: merge 9f0e4478`, committed 2026-10-30T01:18Z.
+  The orchestrator gives their standing ages as 11 h, 5 h and 5 h. #2976 now reads
+  `reviewDecision: APPROVED`, `CLEAN` at that same head (one `gh pr view`). So the approval was
+  the only thing missing.
+- **`FAMILY`** in `tools/audit/seat/owed_unactioned.py` (line 53) lists `MERGE-READY:` and
+  `BLOCKED-UNFIXED:`, and no third level.
+
+Cost: S. The work is one `--json` field, one arm, and one catch-all arm in `verdict_levels`, plus
+one alternative in `FAMILY` and self-test rows in both files. Neither file has a `policy_lint.mjs
+--budgets` row: the `--budgets` output at `1148ee635` names neither of them. Benefit, measured:
+21 PR-hours of merge-verdicted heads stood with no tick line (11 + 5 + 5) before the owner asked.
+
+Binding:
+- **The root-cause question.** Neither trigger in `defect-root-cause.md` fires: nothing reached a
+  release, and no check went red. The recurrence rule in `CLAUDE.md` ("at roughly the third
+  instance it is root-cause.md") does fire on the idle-PR class. That class already has its
+  root-cause seat, `dev/audit/rca/R10-RCA-OWED-UNACTIONED.md` (2026-10-28, the #2916 instance).
+  Its countermeasure acts on owed lines the tick prints. This instance is a PR state for which the
+  tick prints no line at all, so no countermeasure keyed on printed lines can see it.
+- **Process state: (c), as the orchestrator reads it.** The tick ran and was read, and the level
+  meant to name every actionable verdicted PR did not produce that result for one state. A third
+  instance of the same class, after a seat already ruled on it, owes a barrier rather than a
+  second seat. So the countermeasure is the catch-all line below, built in this group. It moves
+  the class from "a missing level is silent" to "a missing level prints". That is the
+  check-shaped demonstration `defect-root-cause.md` asks for, held by the red arm and its
+  mutation.
+- **Dispatch.** The group dispatches ahead of other instrument fly-ins. Each hour a verdicted PR
+  waits unnamed is an hour of the round's closure, and two of the three instances (#2976, #2977)
+  were round-10 work.
+
+The fix:
+1. `prs()` asks for `reviewDecision` too.
+2. `verdict_levels` gains `APPROVAL-OWED: #N <head8>` (flagged). It fires on a `merge` verdict at
+   the current head where `mergeStateStatus` is BLOCKED and `reviewDecision` is REVIEW_REQUIRED.
+3. The catch-all is `UNLEVELLED: #N <head8> <mergeStateStatus>/<reviewDecision>` (flagged). It
+   fires on a `merge` verdict at the current head that matches none of MERGE-READY,
+   APPROVAL-OWED or a documented non-actionable state. The non-actionable states are DIRTY (the
+   existing null-control row), BEHIND and a draft; each is named in the docstring. A future state
+   that the levels miss then prints, instead of standing silent.
+4. `owed_unactioned.py`'s `FAMILY` adds `APPROVAL-OWED:` and `UNLEVELLED:`.
+5. Red arm: a board with #N BLOCKED, REVIEW_REQUIRED and a merge verdict at its head prints
+   `APPROVAL-OWED: #N`. Under the current code it prints nothing, so the arm fails there. The
+   failing test comes first.
+6. Mutation:
+   - dropping the APPROVAL-OWED arm fails the red arm, which then prints `UNLEVELLED` instead;
+   - dropping the catch-all fails a row with a real state no arm handles (`mergeStateStatus:
+     UNKNOWN`, or BLOCKED under APPROVED) that must print `UNLEVELLED`.
+7. Null controls: a merge verdict at a stale head prints neither line (the existing #41 row
+   still holds); DIRTY prints neither line; an APPROVED + CLEAN PR prints MERGE-READY only.

