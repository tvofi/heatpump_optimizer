# Review packet #3539
head: 2e160c0c9b0cb4b00bdbd5f17defd63bfcfbfbee
base: caacd43b4ee1b1ce849fbc92590e0b2191e6c02c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=131732218043 neutral
arch-score / arch-score id=131731752403 queued
arm id=131730381899 skipped
budget-raise-gate / budget-raise-gate id=131731752233 in_progress
cancel-superseded id=131730384875 queued
codeql / Analyze (actions) id=131731752161 success
codeql / Analyze (javascript-typescript) id=131731752155 queued
codeql / Analyze (python) id=131731752232 queued
governance / delivery-status id=131731752010 success
governance / delivery-status-publish id=131731753905 skipped
governance / env-matrix id=131731751983 queued
governance / instrument-self-tests id=131731752016 queued
governance / policy-docs id=131731752033 queued
governance / record id=131731754175 skipped
governance / wave-script id=131731752213 queued
hassfest / hassfest id=131731752240 queued
kernel-points id=131731753494 skipped
prelude id=131730384838 queued
refresh id=131730384476 queued
tests / briefs id=131731752141 queued
tests / closure-scope id=131731752040 in_progress
tests / mutation id=131731751958 success
tests / mutation-autofix id=131732232184 skipped
tests / mutation-pins id=131732231340 skipped
tests / nightly-status id=131731752012 failure
validate / validate-hacs id=131731751900 in_progress

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 131731752016: queued has not concluded: an introduced red cannot be ruled out (fail closed)

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

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3539.md b/dev/programme/delivery/3539.md
new file mode 100644
index 0000000000..80a5e06e48
--- /dev/null
+++ b/dev/programme/delivery/3539.md
@@ -0,0 +1 @@
+- [#3539](https://github.com/tvofi/heatpump_optimizer/pull/3539) — **open**, R10-REVIEW-DISPATCH-RESIDUE (part 6): r10 review dispatch residue p6 (R10-REVIEW-DISPATCH-RESIDUE)
diff --git a/tools/audit/seat/cloud_dispatch.py b/tools/audit/seat/cloud_dispatch.py
index 5516443f33..64fd8ca374 100644
--- a/tools/audit/seat/cloud_dispatch.py
+++ b/tools/audit/seat/cloud_dispatch.py
@@ -362,7 +362,8 @@ def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, br
             f"and run `bash tools/audit/seat/bus.sh push-design-verdict {topic} <verdict.md>`, which "
             f"pushes refs/heads/design-verdict/{topic} and refuses a design that has moved; that push "
             "is the return signal. You may push only to that ref. Write no design, open no pull "
-            "request and push no code.")
+            "request and push no code."
+            + (round_context(topic, design, verdict) if verdict else ""))
     else:
         body = (
             "Role: a read-only probe. Measure what the brief below asks against the tree at "
@@ -577,6 +578,18 @@ def publish_seat(repo_dir: str, ref: str, role: str, head: str, **args) -> dict:
     return payload
 
 
+def round_context(group_id: str, design: str, verdict: tuple) -> str:
+    """What a later-round design reviewer is given: the round (the verdict ref's
+    commit count plus one), the last verdict's commit and first line, and the range
+    from the design that line names to the design tip. A first round has no verdict
+    ref and renders none of it."""
+    sha, first, count = verdict
+    prev = first.split()[3:4]  # `Design review: <word> <design sha> ...`
+    rng = f" Review what changed: `git diff {prev[0]}..{design}`." if prev and prev[0] != design else ""
+    return (f" This is round {count + 1}: the previous verdict is at design-verdict/{group_id}, commit {sha}, "
+            f"first line `{first}` (`git show {sha}:verdict.md`).{rng}")
+
+
 def design_tip(repo_dir: str, group_id: str) -> str:
     """The 40-hex tip of `design/<group>` on origin, or "" when the designer has pushed none."""
     out = _git(repo_dir, "ls-remote", "origin", f"refs/heads/design/{group_id}").split()[:1]
@@ -661,12 +674,13 @@ def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
         if not design:
             raise Refusal(f"no design/{group_id} on origin to review")
     verdict = ()
-    if role == "designer":  # a revise routes the round-2 designer to the verdict commit, pinned by SHA
+    if role in ("designer", "design-reviewer"):  # a revise routes the next round to the verdict commit, pinned by SHA
         vref = f"refs/heads/design-verdict/{group_id}"
         vtip = _git(repo_dir, "ls-remote", "origin", vref).split()[:1]
         if vtip:
-            _git(repo_dir, "fetch", "-q", "origin", vtip[0])
-            verdict = (vtip[0], _git(repo_dir, "show", f"{vtip[0]}:verdict.md").split("\n", 1)[0])
+            _git(repo_dir, "fetch", "-q", "origin", vref)
+            verdict = (vtip[0], _git(repo_dir, "show", f"{vtip[0]}:verdict.md").split("\n", 1)[0],
+                       int(_git(repo_dir, "rev-list", "--count", vtip[0]).strip()))
     args = dict(design=design, verdict=verdict, env_id=known["env_id"], model=model, repo=roster.get("repo") or known["repo"],
                 pr=pr, topic=topic,
                 brief=group_brief(group, roster, fixer=role == "fixer") + (f"\n{pline}\n" if pline else ""),
@@ -841,6 +855,8 @@ def _group_checks(check) -> None:
               rref == "dispatch/design-reviewer-R10-BIG" and f"Design review: approve {tip}" in rtext
               and tip in rtext and "dev/governance/roles/design-review.md" in rtext
               and "push-design-verdict R10-BIG" in rtext and "only to that ref" in rtext)
+        check("a first-round design reviewer's text names no round and no verdict ref (null control)",
+              "This is round" not in rtext and "design-verdict/R10-BIG, commit" not in rtext)
         check("a fixer is still refused with a design and no verdict", refused("R10-BIG", design_exempt=""))
         _publish(str(work), "design-verdict/R10-BIG", {"verdict.md": f"Design review: revise {tip} class-open\n"})
         check("a fixer is refused on a `revise` verdict", refused("R10-BIG"))
@@ -849,6 +865,14 @@ def _group_checks(check) -> None:
         dtext2 = fetched(dref, "PROMPT.md")
         check("a designer's text pins the revise verdict's own commit and first line",
               dref == ref and vtip != tip and vtip in dtext2 and f"Design review: revise {tip} class-open" in dtext2)
+        rtext2 = fetched(dispatch("R10-BIG", "design-reviewer"), "PROMPT.md")
+        check("a design reviewer after one revise is told round 2, the verdict commit, its first line and the diff range",
+              "round 2" in rtext2 and vtip in rtext2 and f"Design review: revise {tip} class-open" in rtext2
+              and f"git diff {tip}..{tip}" not in rtext2)
+        _publish(str(work), "design-verdict/R10-BIG", {"verdict.md": f"Design review: revise {'b' * 40} class-open\n"})
+        rtext3 = fetched(dispatch("R10-BIG", "design-reviewer"), "PROMPT.md")
+        check("a second revise names round 3 and the range from the design it names to the design tip",
+              "round 3" in rtext3 and f"git diff {'b' * 40}..{tip}" in rtext3)
         _publish(str(work), "design-verdict/R10-BIG", {"verdict.md": f"Design review: approve {'a' * 40}\n"})
         check("a fixer is refused on an approval of a design that has since moved", refused("R10-BIG"))
         _publish(str(work), "design-verdict/R10-BIG", {"verdict.md": f"Design review: approve {tip}\n"})
diff --git a/tools/audit/seat/review_packet.py b/tools/audit/seat/review_packet.py
index 9e3476cc50..bae45479b5 100644
--- a/tools/audit/seat/review_packet.py
+++ b/tools/audit/seat/review_packet.py
@@ -615,7 +615,28 @@ def prompt_carries(prompt: str | None) -> list[int] | None:
     there is no prompt or it holds none: the carries the fixer was dispatched
     with, which a roster appended to afterwards does not change (S14)."""
     found = sorted({int(m) for m in re.findall(r"^Carry (\d+):", prompt or "", re.M)})
-    return found or None
+    assigned = part_carries(prompt)
+    return assigned or found or None
+
+
+def part_carries(prompt: str | None) -> list[int] | None:
+    """The indexes a split part is assigned, or None when the prompt has no part
+    line. Two spellings: the hand line `This part: Carries 25, 24, 10 (0-based
+    roster indexes` and the generated `Part k of N: build carries 15-17+19-20`
+    (`cloud_dispatch.part_split`'s runs). The prompt holds every roster carry
+    under the generated line, so the part line, not the `Carry N:` count, scopes it."""
+    text = prompt or ""
+    hand = re.search(r"^This part: Carries ([0-9, ]+?) \(0-based roster indexes", text, re.M)
+    if hand:
+        return sorted({int(n) for n in re.findall(r"\d+", hand.group(1))}) or None
+    gen = re.search(r"^Part \d+ of \d+: build carries ([0-9+-]+);", text, re.M)
+    if not gen:
+        return None
+    out: set[int] = set()
+    for run in gen.group(1).split("+"):
+        lo, _, hi = run.partition("-")
+        out.update(range(int(lo), int(hi or lo) + 1))
+    return sorted(out) or None
 
 
 def handoff_carries(prompt: str | None, live: int):
@@ -636,12 +657,12 @@ def dispatch_prompt(topic: str) -> str | None:
 
 
 def handoff_refusals(structure: str | None, hot: list[str], unnamed: list[int],
-                     unlanded: list[str] | None = None) -> list[str]:
+                     unlanded: list[str] | None = None, base: str = "") -> list[str]:
     """The refusals that need no CI run: the packet's `structure` and `hot-file`,
     and the handoff's `brief-carries` count (P256). One spelling for both callers."""
     out = [f"structure: tests/structure.py refuses the head merged with main: {structure}"] if structure else []
     out += [f"hot-file: {w}" for w in hot]
-    out += [f"brief-carries: carry {i} is not named in the body (`Carry N`)" for i in unnamed]
+    out += [f"brief-carries: carry {i} is not named in the body (`Carry N`){base}" for i in unnamed]
     return out + (unlanded or [])
 
 
@@ -823,13 +844,15 @@ def handoff(a) -> int:
         raise Unavailable(f"cannot read the roster at {ref}: {e}")
     gid = roster_lib.group_for_branch(roster, f"handoff/{a.topic}")
     live = len(roster_lib.groups_of(roster)[gid].get("carry") or []) if gid else 0
-    carries = handoff_carries(dispatch_prompt(a.topic), live)
+    prompt = dispatch_prompt(a.topic)
+    carries = handoff_carries(prompt, live)
+    base = " -- demanded by the dispatch PROMPT's part line" if part_carries(prompt) else ""
     open_prs, boarded = hot_prs(touched)
     anc = lambda sha: subprocess.run(  # noqa: E731
         ["git", "merge-base", "--is-ancestor", sha, head], cwd=repo(), capture_output=True).returncode == 0
     refusals = handoff_refusals(structure_at_merge(a.main, head),
                                 handoff_hot(touched, open_prs, boarded, a.topic, anc), unnamed_carries(body, carries),
-                                unlanded_carries(landed_cites(body), *reversed(roster_carry_reader([a.topic], ref))))
+                                unlanded_carries(landed_cites(body), *reversed(roster_carry_reader([a.topic], ref))), base)
     for x in refusals:
         print(f"review_packet: REFUSE {x}", file=sys.stderr)
     print(f"review-packet handoff: {gid or 'no group'} at {head[:12]}, {live} live, {carries if isinstance(carries, int) else len(carries)} dispatched carries, {len(refusals)} refused")
@@ -1100,6 +1123,25 @@ def _self_test() -> int:
           and handoff_carries(None, 3) == 3 and unnamed_carries("Carry 0: a\nCarry 1: b\n", handoff_carries(None, 3)) == [2])
     check("S14 brief-carries: with a 21-carry PROMPT and 27 live carries the check runs over the PROMPT's 21",
           handoff_carries(prompt21, 27) == list(range(21)))
+    full5 = "".join(f"Carry {i}: t\n" for i in range(5))
+    hand = full5 + "This part: Carries 3, 2 (0-based roster indexes, texts verbatim below).\n"
+    gen = full5 + "Part 2 of 3: build carries 2-3; the others are later parts dispatched at this part's handoff; answer none of them\n"
+    gen2 = full5 + "Part 1 of 2: build carries 0-1+4; the others are later parts dispatched at this part's handoff; answer none of them\n"
+    two = "Carry 2: a\nCarry 3: b\n"
+    check("P593 brief-carries: a part assigned {2,3} (hand line) of a 5-carry prompt demands Carry 2 and Carry 3 only",
+          prompt_carries(hand) == [2, 3] and unnamed_carries(two, handoff_carries(hand, 5)) == []
+          and unnamed_carries("Carry 2: a\n", handoff_carries(hand, 5)) == [3])
+    check("P593 brief-carries: the generated `Part k of N: build carries <runs>` line scopes alike, runs joined by +",
+          prompt_carries(gen) == [2, 3] and unnamed_carries(two, handoff_carries(gen, 5)) == []
+          and prompt_carries(gen2) == [0, 1, 4] and unnamed_carries("Carry 0: a\nCarry 1: b\n", handoff_carries(gen2, 5)) == [4])
+    check("P593 brief-carries: a carry appended after dispatch (live 6, prompt holds 5) is not demanded",
+          unnamed_carries(two, handoff_carries(hand, 6)) == [])
+    check("P593 brief-carries null: no part line demands all 5 of the prompt; no prompt demands the live count",
+          prompt_carries(full5) == list(range(5)) and part_carries(full5) is None
+          and unnamed_carries(two, handoff_carries(full5, 5)) == [0, 1, 4] and handoff_carries(None, 5) == 5)
+    check("P593 brief-carries: the refusal names its base only when given one",
+          handoff_refusals(None, [], [3], None, " -- x") == ["brief-carries: carry 3 is not named in the body (`Carry N`) -- x"]
+          and handoff_refusals(None, [], [3]) == ["brief-carries: carry 3 is not named in the body (`Carry N`)"])
     check("brief-carries null: a group with no carries passes", unnamed_carries("", 0) == [])
     check("brief-carries: `carry 1` does not name carry 10, and `Carry [10]` does",
           unnamed_carries("Carry 1: x\n", 11)[-1] == 10 and 10 not in unnamed_carries("Carry [10]: x\n", 11))
diff --git a/tools/audit/seat/review_strength.py b/tools/audit/seat/review_strength.py
index e0a4043170..c35b2f7b33 100644
--- a/tools/audit/seat/review_strength.py
+++ b/tools/audit/seat/review_strength.py
@@ -248,12 +248,19 @@ def pr_facts(repo: Path, tree: str, roster: str | None, verdicts: list[dict],
                 lines += (int(a) if a != "-" else 0) + (int(d) if d != "-" else 0)
         facts[pr] = dict(
             origin="none" if grp is None else "finding" if (grp.get("issues") or grp.get("findings") or grp.get("fixes")) else "group",
-            fixer=((grp or {}).get("model") or {}).get("fixer") or "none",
+            fixer=fixer_of(grp),
             size="?" if not mb else "S<150" if lines < 150 else "M<600" if lines < 600 else "L>=600",
             product=any(f.startswith(("custom_components/", "blueprints/")) for f in files))
     return facts
 
 
+def fixer_of(grp: dict | None) -> str:
+    """The group's fixer model: `model.fixer`, or a string `model` itself (a roster
+    group may hold `"model": "sonnet"`), else "none"."""
+    model = (grp or {}).get("model")
+    return (model if isinstance(model, str) else (model or {}).get("fixer")) or "none"
+
+
 def stratum(by: str, v: dict, facts: dict[int, dict], taught: tuple[str, ...] = ()) -> str:
     if "+" in by:
         return "+".join(stratum(b, v, facts, taught) for b in by.split("+"))
@@ -576,6 +583,9 @@ def self_test() -> int:
               (f4[5]["origin"], f4[6]["origin"]) == ("finding", "group"))
         check("fixer: the joined group's model.fixer, opus for 5 and sonnet for 6",
               (f4[5]["fixer"], f4[6]["fixer"]) == ("opus", "sonnet"))
+        check("fixer: a string model is the fixer model (R10-REPLAY-OPEN-LOG's \"sonnet\"); null: the dict reads its fixer key, none reads none",
+              (fixer_of({"model": "sonnet"}), fixer_of({"model": {"fixer": "opus"}}), fixer_of({"model": {}}), fixer_of(None))
+              == ("sonnet", "opus", "none", "none"))
         check("size: merged PR 5 reads its merge diff (160 lines, M<600); unmerged 6 its verdict head (20, S<150)",
               (f4[5]["size"], f4[6]["size"]) == ("M<600", "S<150"))
         check("product: 5 touches custom_components/, 6 only docs/",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
