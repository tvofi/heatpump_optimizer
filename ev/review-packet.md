# Review packet #3539
head: 9b811fdcefc6e0ff80c4bc78013d23d7f087be45
base: caacd43b4ee1b1ce849fbc92590e0b2191e6c02c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=131792727307 success
arch-score / arch-score id=131804369254 success
arm id=131792151003 skipped
budget-raise-gate / budget-raise-gate id=131804369378 success
cancel-superseded id=131803514669 success
codeql id=131804372580 skipped
codeql / Analyze (actions) id=131792448543 success
codeql / Analyze (javascript-typescript) id=131792448477 success
codeql / Analyze (python) id=131792448634 success
gate id=131807315309 queued
governance id=131804371248 skipped
governance / delivery-status id=131792448561 success
governance / delivery-status-publish id=131792451843 skipped
governance / env-matrix id=131792448461 success
governance / instrument-self-tests id=131792448592 success
governance / policy-docs id=131792448624 success
governance / record id=131792451364 skipped
governance / wave-script id=131792448775 success
hassfest id=131804370769 skipped
hassfest / hassfest id=131792448942 success
kernel-points id=131804371475 skipped
pr-contract id=131805625786 skipped
pr-contract / pr-contract id=131806919070 success
prelude id=131803515060 success
refresh id=131803515049 success
sweep-self id=131805924837 skipped
tests id=131804371819 skipped
tests / arch-instrument id=131793415346 success
tests / briefs id=131792448637 success
tests / browser id=131793415422 success
tests / ci-ratchet id=131806560250 skipped
tests / claims-autofix id=131801109890 skipped
tests / closure-scope id=131792448768 success
tests / closures id=131793415462 success
tests / closures-autofix id=131802827480 skipped
tests / coverage id=131793415310 success
tests / coverage-ratchet id=131806557189 success
tests / fast (3.14) id=131793415302 success
tests / graders-head-copy id=131806557024 success
tests / lane-proofs id=131806557027 success
tests / mutation id=131792448882 success
tests / mutation-autofix id=131793251131 skipped
tests / mutation-pins id=131793251188 skipped
tests / nightly-ha id=131793417392 skipped
tests / nightly-status id=131792448573 success
tests / replay id=131793417585 skipped
tests / typing id=131793415485 success
validate id=131804371648 skipped
validate / validate-hacs id=131792448416 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head 2e160c0c9b0cb4b00bdbd5f17defd63bfcfbfbee)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 2e160c0c9b0cb4b00bdbd5f17defd63bfcfbfbee
Fix review: blocked 2e160c0c9b0cb4b00bdbd5f17defd63bfcfbfbee mutation-vacuous: review_packet.py:847-849,853 handoff wiring and the new part-line base predicate survive; cloud_dispatch.py:681 fetch survives

bus-nonce: 55ce0064265b6ffbf6e084e24ecdd271
pending-ci: governance / instrument-self-tests, governance / policy-docs, governance / env-matrix, governance / wave-script, tests / briefs, tests / closure-scope, arch-score / arch-score, hassfest / hassfest, validate / validate-hacs, budget-raise-gate / budget-raise-gate

Round 1 (first review of #3539). Measured head `2e160c0c9b0cb4b00bdbd5f17defd63bfcfbfbee`, which is the head the PR body names. Merge base `caacd43b4ee1b1ce849fbc92590e0b2191e6c02c`.

## Block

- mutation-vacuous: carry 25's new predicate in `handoff()` is never run by `review_packet.py --self-test`. At `tools/audit/seat/review_packet.py:849`, `base = " -- demanded by the dispatch PROMPT's part line" if part_carries(prompt) else ""` survives when it is inverted and when it is forced to `""` (both `128 checks, 0 failed`). So do `:848` `carries = handoff_carries(prompt, live)` → `handoff_carries(None, live)` (that drops the part scope from the live handoff path entirely) and the driver's STMT_DEL of `:847`, `:848`, `:849` and `:853`. `handoff()` has no self-test fixture, so nothing pins the wiring this carry exists to change. The body's "Carry 25 base text in the refusal dropped: KILLED" mutant is on `handoff_refusals`'s parameter, not on this predicate. Owed: a self-tested seam for the brief-carries step of `handoff()` (for example, lift lines 847-849 and the `unnamed_carries`/`handoff_refusals` call into one pure function over `(prompt, live, body)` that the self-test drives with a part-line prompt and with a no-part-line prompt), then show both mutants on 848/849 KILLED.
- mutation-vacuous: `tools/audit/seat/cloud_dispatch.py:681` `_git(repo_dir, "fetch", "-q", "origin", vref)` is a changed production line, and deleting it survives (`172 checks, 0 failed`). The fixture's verdict objects are already local, so the fetch is unobservable. The body does not say why the fetch target moved from `vtip[0]` to `vref`.
- Every survivor the driver run at this head reports (`mutant_run.py --diff caacd43b4e...<head>`, per file, each against that file's own `--self-test`; logs in `ev/mut-*.log`):
  - SURVIVED tools/audit/seat/review_packet.py:1133 CONST_SWAP  and unnamed_carries("Carry 2: a\n", handoff_carries(hand, 6)) == [3])
  - SURVIVED tools/audit/seat/review_packet.py:1138 CONST_SWAP  unnamed_carries(two, handoff_carries(hand, 7)) == [])
  - SURVIVED tools/audit/seat/review_packet.py:1141 CONST_SWAP  and unnamed_carries(two, handoff_carries(full5, 6)) == [0, 1, 4] and handoff_carries(None, 5) == 5)
  - SURVIVED tools/audit/seat/review_packet.py:847 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:848 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:849 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:853 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:1131 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:1134 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:1137 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:1139 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:1142 STMT_DEL  pass
  - SURVIVED tools/audit/seat/cloud_dispatch.py:681 CALL_DEL  pass
  - SURVIVED tools/audit/seat/cloud_dispatch.py:858 STMT_DEL  pass
  - SURVIVED tools/audit/seat/cloud_dispatch.py:869 STMT_DEL  pass
  - SURVIVED tools/audit/seat/cloud_dispatch.py:874 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_strength.py:586 STMT_DEL  pass
  - Excluded from this block: the 12 survivors on self-test lines (`review_packet.py:1131-1142`, `cloud_dispatch.py:858/869/874`, `review_strength.py:586`). Deleting or re-numbering an assertion is not production behaviour. They are listed above because the driver reported them; the block rests on `review_packet.py:847-849,853` and `cloud_dispatch.py:681`.
- My hand predicate mutants (`ev/hm.py`, `ev/hand-mutants.out`), one per new predicate, against the file's own `--self-test`:
  - SURVIVED: c25 base predicate inverted (849), c25 base always empty (849), c25 handoff ignores prompt (848), c24 fetch deleted (681).
  - KILLED: c25 `assigned or found` → `found` (3 failed), c25 hand branch disabled (2), c25 gen branch disabled (1), c24 range predicate always true (1) and always false (1), c24 render guard off (2), c24 role tuple narrowed to designer (2), c10 isinstance inverted (AttributeError), c10 string branch → None (1).
  - NULL (identical replacement): SURVIVED.

## Evidence

- RESULT self-tests at the head: review_packet 128 checks, 0 failed; cloud_dispatch 172 checks, 0 failed; review_strength 117 checks, 0 failed (`ev/selftests-head.txt`). These match the body's three green figures. I did not re-derive the body's red-at-base FAIL counts (3, 2, NameError).
- RESULT carry 25 hand spelling, real p6 PROMPT `8602c93e58:PROMPT.md`: `prompt_carries` gives [10, 24, 25]. In a 27-carry prompt with the hand line, a body naming 25, 24 and 10 has unnamed [] (passes). A body missing 10 is refused for [10]. A body naming only Carry 3, outside the part, is refused for [10, 24, 25] (`ev/c25.out`).
- RESULT carry 25 generated spelling `Part 2 of 3: build carries 15-17+19-20;`: assigned [15, 16, 17, 19, 20]. The exact body passes. A body naming 18 (outside) in place of 20 is refused for [20]. A round trip of `cloud_dispatch.part_line` for a 20-carry split parses every part to its own runs: 0-4, 5-9, 10-11+13-15, 16-17+19-20+22.
- RESULT carry 25 null: a prompt with no part line demands all 27 (a 3-carry body leaves 24 unnamed). At the merge base, the generated-line prompt demands all 27 (22 unnamed for the 5-carry body), so the fix moves it.
- RESULT carry 25 domain: a body naming its own three carries plus an outside `Carry 3` is not refused (unnamed []). Carry 25 asks only to demand the assigned indexes; "names no other carry" is a fixer-brief rule that no instrument here enforces. I record this as the check's domain, not a defect of this part.
- RESULT the roster-at-dispatch-time base (`rev-list -1 --before`) is not built. The body says so and why. That matches the fixer brief, which made it conditional on a prompt holding no Carry lines.
- RESULT merge with main: `git merge-tree --write-tree origin/main 2e160c0c9b…` (main `b5057b0525`) gives rc=0, tree `87edde0b79`. It is clean, not textual-only (`ev/mergetree.out`).
- RESULT PR #3533: `refs/pull/3533/head` `faf8676984` is already an ancestor of origin/main (merged at `b5057b0525`), so the merge-tree against it is that same clean rc=0. Against the p6 merge base, #3533's `cloud_dispatch.py` hunks are at 934+ and 1147+ in `_group_checks`. p6's hunks are at 362, 577-592, 674-683 and 855-875, so p6 did not edit #3533's lines: clean, not textual-only.
- RESULT scope: the diff touches only `review_packet.py`, `cloud_dispatch.py`, `review_strength.py` and its own delivery row. There is no role or policy file and no `VERSION`, manifest, notes heading, golden or claim file. The body names Carry 25, 24 and 10 and no other carry of the group, which matches the part scope.
- RESULT carry 10: `fixer_of` reads a string model, a dict's `fixer` key, `{}` and None as sonnet / opus / none / none. Both of its predicate mutants are killed.
- RESULT roster destinations: `dev/programme/rosters/wave-r10-groups.json` holds `R10-REVIEW-DISPATCH-RESIDUE` at origin/handoff/audit-r10-roster `d12ffa3aaf` (506 groups) but not at origin/main `b5057b0525` (342 groups) (`ev/roster-dest.out`). A `Carry:` to this group therefore fails the both-rosters rule today, which is why this verdict hands the block back to the PR instead of carrying it.
- RESULT CI: `merge_train.py classify … --pr 3539` printed `WAIT 2e160c0c9b0cb4b00bdbd5f17defd63bfcfbfbee pending: gate red: none` (rc 3) at both reads. Per the dispatch, I did not wait. The packet render refused `introduced-red: unreadable` because `instrument-self-tests` had not concluded, and showed `tests / nightly-status` failure, which is outside `owed-reds` (`ev/review-packet.md`). No red-check answer is owed yet.
- RESULT `env -u BASH_ENV python3 tests/entities.py` could not run in this container: `ModuleNotFoundError: No module named 'homeassistant'` under venv-ci (`ev/entities.out`). It is not verified here; CI's governance lanes run it.

## Delta diff: git diff 2e160c0c9b0cb4b00bdbd5f17defd63bfcfbfbee 9b811fdcefc6e0ff80c4bc78013d23d7f087be45
diff --git a/tools/audit/seat/cloud_dispatch.py b/tools/audit/seat/cloud_dispatch.py
index 64fd8ca374..edf4a4a4ca 100644
--- a/tools/audit/seat/cloud_dispatch.py
+++ b/tools/audit/seat/cloud_dispatch.py
@@ -869,10 +869,14 @@ def _group_checks(check) -> None:
         check("a design reviewer after one revise is told round 2, the verdict commit, its first line and the diff range",
               "round 2" in rtext2 and vtip in rtext2 and f"Design review: revise {tip} class-open" in rtext2
               and f"git diff {tip}..{tip}" not in rtext2)
-        _publish(str(work), "design-verdict/R10-BIG", {"verdict.md": f"Design review: revise {'b' * 40} class-open\n"})
+        vclone = work.parent / "vclone"  # a second clone: this verdict commit is on origin and not in `work` until fetched
+        throwaway_git_clone(origin, vclone, "-q", "--no-checkout")
+        vtip3 = _publish(str(vclone), "design-verdict/R10-BIG", {"verdict.md": f"Design review: revise {'b' * 40} class-open\n"})
+        check("the fixture's third verdict commit is absent from the dispatching clone before the dispatch (the fetch is observable)",
+              subprocess.run(["git", "-C", str(work), "cat-file", "-e", vtip3], capture_output=True).returncode != 0)
         rtext3 = fetched(dispatch("R10-BIG", "design-reviewer"), "PROMPT.md")
         check("a second revise names round 3 and the range from the design it names to the design tip",
-              "round 3" in rtext3 and f"git diff {'b' * 40}..{tip}" in rtext3)
+              "round 3" in rtext3 and f"git diff {'b' * 40}..{tip}" in rtext3 and vtip3 in rtext3)
         _publish(str(work), "design-verdict/R10-BIG", {"verdict.md": f"Design review: approve {'a' * 40}\n"})
         check("a fixer is refused on an approval of a design that has since moved", refused("R10-BIG"))
         _publish(str(work), "design-verdict/R10-BIG", {"verdict.md": f"Design review: approve {tip}\n"})
diff --git a/tools/audit/seat/review_packet.py b/tools/audit/seat/review_packet.py
index bae45479b5..55b0500f98 100644
--- a/tools/audit/seat/review_packet.py
+++ b/tools/audit/seat/review_packet.py
@@ -644,6 +644,16 @@ def handoff_carries(prompt: str | None, live: int):
     return prompt_carries(prompt) or live
 
 
+def brief_carries(prompt: str | None, live: int, body: str) -> tuple[object, list[int], str]:
+    """The handoff's brief-carries step, pure: (the carries checked, the indexes
+    the body leaves unnamed, the refusal's base text). The base names the part
+    line only when the dispatch PROMPT carries one, so the refusal says why a
+    carry outside a part is not demanded."""
+    carries = handoff_carries(prompt, live)
+    base = " -- demanded by the dispatch PROMPT's part line" if part_carries(prompt) else ""
+    return carries, unnamed_carries(body, carries), base
+
+
 def dispatch_prompt(topic: str) -> str | None:
     """PROMPT.md of `origin`'s `dispatch/fixer-<topic>`, or None when the ref is
     absent here or unreadable (the caller falls back to the live roster)."""
@@ -845,13 +855,12 @@ def handoff(a) -> int:
     gid = roster_lib.group_for_branch(roster, f"handoff/{a.topic}")
     live = len(roster_lib.groups_of(roster)[gid].get("carry") or []) if gid else 0
     prompt = dispatch_prompt(a.topic)
-    carries = handoff_carries(prompt, live)
-    base = " -- demanded by the dispatch PROMPT's part line" if part_carries(prompt) else ""
+    carries, unnamed, base = brief_carries(prompt, live, body)
     open_prs, boarded = hot_prs(touched)
     anc = lambda sha: subprocess.run(  # noqa: E731
         ["git", "merge-base", "--is-ancestor", sha, head], cwd=repo(), capture_output=True).returncode == 0
     refusals = handoff_refusals(structure_at_merge(a.main, head),
-                                handoff_hot(touched, open_prs, boarded, a.topic, anc), unnamed_carries(body, carries),
+                                handoff_hot(touched, open_prs, boarded, a.topic, anc), unnamed,
                                 unlanded_carries(landed_cites(body), *reversed(roster_carry_reader([a.topic], ref))), base)
     for x in refusals:
         print(f"review_packet: REFUSE {x}", file=sys.stderr)
@@ -1142,6 +1151,51 @@ def _self_test() -> int:
     check("P593 brief-carries: the refusal names its base only when given one",
           handoff_refusals(None, [], [3], None, " -- x") == ["brief-carries: carry 3 is not named in the body (`Carry N`) -- x"]
           and handoff_refusals(None, [], [3]) == ["brief-carries: carry 3 is not named in the body (`Carry N`)"])
+    base_txt = " -- demanded by the dispatch PROMPT's part line"
+    check("brief_carries: a part line (hand, then generated) scopes the check and the refusal names it",
+          brief_carries(hand, 6, two) == ([2, 3], [], base_txt) and brief_carries(gen, 6, "Carry 2: a\n") == ([2, 3], [3], base_txt))
+    check("brief_carries null: a prompt with no part line demands every prompt carry and names no base",
+          brief_carries(full5, 5, two) == (list(range(5)), [0, 1, 4], "") and brief_carries(None, 3, "") == (3, [0, 1, 2], ""))
+
+    def drive_handoff(prompt: str | None, body_text: str) -> tuple[int, str]:
+        """`handoff()` over stubbed edges: the wiring of the brief-carries step, end to end."""
+        import contextlib
+        import io
+        import roster_lib
+        import types
+        g = globals()
+        saved = {k: g[k] for k in ("git", "repo", "fetch_roster_ref", "dispatch_prompt", "hot_prs",
+                                   "structure_at_merge", "roster_carry_reader")}
+        rl = {k: getattr(roster_lib, k) for k in ("show_roster", "group_for_branch", "groups_of")}
+        g.update(git=lambda *a, **k: "f" * 40 + "\n", repo=lambda: Path("."), fetch_roster_ref=lambda r: "R",
+                 dispatch_prompt=lambda t: prompt, hot_prs=lambda t: ([], set()), structure_at_merge=lambda m, h: None,
+                 roster_carry_reader=lambda t, r: (lambda sha: True, lambda sha: 0))
+        roster_lib.show_roster = lambda r, ref, path=None: {}
+        roster_lib.group_for_branch = lambda r, b: "G"
+        roster_lib.groups_of = lambda r: {"G": {"carry": [0] * 6}}
+        err = io.StringIO()
+        try:
+            with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
+                f.write(body_text)
+            ns = types.SimpleNamespace(body=f.name, main="main", roster_ref=None, topic="t")
+            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
+                rc = handoff(ns)
+        finally:
+            g.update(saved)
+            for k, v in rl.items():
+                setattr(roster_lib, k, v)
+            os.unlink(f.name)
+        return rc, err.getvalue()
+
+    rc_h, err_h = drive_handoff(hand, "Carry 2: a\n")
+    rc_g, err_g = drive_handoff(gen, two)
+    rc_n, err_n = drive_handoff(None, two)
+    check("handoff driven: a part-line prompt (hand) refuses the one unnamed assigned carry, naming the part line",
+          rc_h == 1 and err_h.count("brief-carries") == 1 and "carry 3 is not named" in err_h and base_txt in err_h)
+    check("handoff driven: a part-line prompt (generated) with its assigned carries named passes, 5 outside ignored",
+          rc_g == 0 and err_g == "")
+    check("handoff driven null: no prompt falls to the live 6, refusing the four unnamed with no base text",
+          rc_n == 1 and err_n.count("brief-carries") == 4 and base_txt not in err_n)
     check("brief-carries null: a group with no carries passes", unnamed_carries("", 0) == [])
     check("brief-carries: `carry 1` does not name carry 10, and `Carry [10]` does",
           unnamed_carries("Carry 1: x\n", 11)[-1] == 10 and 10 not in unnamed_carries("Carry [10]: x\n", 11))

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
