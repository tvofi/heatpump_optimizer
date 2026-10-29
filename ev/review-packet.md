# Review packet #2939
head: 6e7f2a1881b015e9de3038bd479e4db96671ca40
base: b87019b868ef0b8d713c2adcf0901f1a823cabc6

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123438888407 success
arch-score / arch-score id=123458369371 success
arm id=123438453179 skipped
budget-raise-gate / budget-raise-gate id=123458369789 success
cancel-superseded id=123458410732 success
codeql id=123458354491 skipped
codeql / Analyze (actions) id=123458369497 success
codeql / Analyze (javascript-typescript) id=123458439399 success
codeql / Analyze (python) id=123458369009 success
gate id=123458371412 in_progress
governance id=123458354467 skipped
governance / delivery-status id=123458368969 success
governance / delivery-status-publish id=123458369328 skipped
governance / env-matrix id=123458369076 success
governance / instrument-self-tests id=123458368869 success
governance / policy-docs id=123458429323 success
governance / record id=123458369107 skipped
governance / wave-script id=123458369149 success
hassfest id=123458354489 skipped
hassfest / hassfest id=123458421542 success
kernel-points id=123458369423 skipped
pr-contract / pr-contract id=123458912125 in_progress
prelude id=123458451100 success
refresh id=123458430874 success
tests id=123458354627 skipped
tests / arch-instrument id=123458371056 success
tests / briefs id=123458369234 success
tests / browser id=123458370869 success
tests / ci-ratchet id=123458372966 skipped
tests / claims-autofix id=123458372821 skipped
tests / closure-scope id=123458452539 success
tests / closures id=123458370492 success
tests / closures-autofix id=123458371783 skipped
tests / coverage id=123458370469 success
tests / coverage-ratchet id=123458372055 success
tests / fast (3.14) id=123458371592 success
tests / graders-head-copy id=123458373168 success
tests / lane-proofs id=123458371915 success
tests / mutation id=123458369896 success
tests / mutation-autofix id=123458371967 skipped
tests / mutation-pins id=123458371339 skipped
tests / nightly-ha id=123458371356 skipped
tests / nightly-status id=123458368828 failure
tests / replay id=123458371349 skipped
tests / typing id=123458370647 success
validate id=123458420409 skipped
validate / validate-hacs id=123458369373 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item c7c5cc8b: R10-ORCH-REVIEW-PACKET
NOTE body item 5f310c0f: R10-RECORD-API-O1
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/review_packet.py --self-test
             `tools/audit/seat/review_packet.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub bash tools/pr/prepr.sh --self-test
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/closure.py select
             `tests/closure.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 -I tools/audit/seat/review_packet.py handoff --topic r10-orch-review-packet --body <a body naming only carry 1>
             `tools/audit/seat/review_packet.py` is in the tree at this head

FIGURES: 8 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_seat_selftests_mutants.py b/dev/audit/harnesses/r10_seat_selftests_mutants.py
index 6605987d6..df45d5685 100644
--- a/dev/audit/harnesses/r10_seat_selftests_mutants.py
+++ b/dev/audit/harnesses/r10_seat_selftests_mutants.py
@@ -223,6 +223,25 @@ MUTANTS = [
     ("prepr-12", "tools/pr/ci_predict.py",
      '"under-scoped", "inert-siblings", "left-inert", "mutation")',
      '"under-scoped", "inert-siblings", "left-inert")'),
+    # R10-ORCH-REVIEW-PACKET (P229, P256): the handoff-not-applied signal, the
+    # handoff refusals and body_push's call of them; body_push-1/2 are graded by
+    # prepr's self-test (STEP_OF), which drives body_push.
+    ("review_packet-1", "review_packet.py",
+     "return None if is_ancestor(tip, head) else", "return None if not is_ancestor(tip, head) else"),
+    ("review_packet-2", "review_packet.py",
+     "        refusals.append(f\"handoff-not-applied: {facts['handoff']}\")\n", "        pass\n"),
+    ("review_packet-3", "review_packet.py",
+     "if not re.search(rf\"\\bcarry", "if False and re.search(rf\"\\bcarry"),
+    ("review_packet-4", "review_packet.py",
+     '[t, t[:-len("-pr")]] if t.endswith("-pr") else [t]', "[t]"),
+    ("review_packet-5", "review_packet.py",
+     '    out += [f"hot-file: {w}" for w in hot]\n', ""),
+    ("body_push-1", "tools/audit/seat/body_push.sh",
+     '  if [ "$prc" = 1 ]; then\n    echo "body_push: the review packet refuses',
+     '  if false; then\n    echo "body_push: the review packet refuses'),
+    ("body_push-2", "tools/audit/seat/body_push.sh",
+     '  if [ "$prc" = 1 ]; then\n    echo "body_push: the review packet refuses',
+     '  if [ "$prc" != 0 ]; then\n    echo "body_push: the review packet refuses'),
     # #2853's review: the class the copy enumeration missed is a link to an
     # in-tree file it does not name. prepr-11 renames a LISTED entry (the
     # pathspec arm); prepr-13 stops the copy taking the generator's own link
@@ -394,7 +413,8 @@ ENV_MUTANTS = [("S04U", "S04", {"PYTHONUNBUFFERED": "1"})]
 
 # A mutant planted in a file whose self-test is another instrument's step.
 STEP_OF = {"prepr-9": "tools/pr/prepr.sh", "prepr-10": "tools/pr/prepr.sh",
-           "prepr-12": "tools/pr/prepr.sh"}
+           "prepr-12": "tools/pr/prepr.sh", "body_push-1": "tools/pr/prepr.sh",
+           "body_push-2": "tools/pr/prepr.sh"}
 
 # The wrappers' own line is the dispatch to the self-tests they delegate.
 # S08's wrapper now runs both tallies (delivery_row.sh's and its own pushes):
diff --git a/dev/governance/roles/fix-review.md b/dev/governance/roles/fix-review.md
index 52ccc8949..1301bd7e1 100644
--- a/dev/governance/roles/fix-review.md
+++ b/dev/governance/roles/fix-review.md
@@ -4,8 +4,8 @@ You review one fix PR adversarially, fresh, from a worktree at
 the PR's head SHA. You check that the numbers are real, not that the code looks right.
 **Its copy of this contract is frozen with the tree, so can be old**; start from the dispatch's `review-packet:`, whose check digest is as rendered: re-read live checks before a verdict.
 Before step 1: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/`; empty is current.
-Before the handoff freezes the branch (`fixer.md`), prepare against the merge base only: steps 2, 12 govern after. Publish it with `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>` and report its output in your thread to be confirmed; it posts as `hpo-approver` (decision 0013) -- never as the author App (#1233) or the owner's approving review, which code-owned paths need.
-A long job, or a wait on CI, runs as `fixer.md`'s preamble says: one watcher whose exit wakes you, never sleeping and polling. Rotate to a fresh context between rounds through refs, never mid-review, by ~150 k tokens.
+Before the handoff freezes the branch (`fixer.md`), prepare against the merge base only: steps 2, 12 govern after. Publish with `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>` (a file there names the head) and report its output to be confirmed; a cloud seat, with no `push-verdict`, commits `cloud_relay.sh`'s verdict file and `ev/` in one commit, subject `verdict <pr> <head40>`, to a fresh repository and pushes `probe/rev-<pr>-<nonce first 8>`. First line: `Fix review: merge <head40>` or `Fix review: blocked <head40> <class>: <reason>`, class `[a-z-]+` (a script routes on it), then your brief's `bus-nonce: <nonce>`. It posts as `hpo-approver` (0013), never the author App (#1233) or the owner's review.
+Long jobs and CI waits follow `fixer.md`'s preamble; rotate context between rounds through refs, never mid-review, by ~150 k tokens.
 
 1. Re-run the mutation proof: delete the production line(s) the PR names,
    run the closure, confirm the named checks fail, restore. If nothing fails,
@@ -131,10 +131,7 @@ A long job, or a wait on CI, runs as `fixer.md`'s preamble says: one watcher who
 15. **Judge `fixer.md` step 17 on added lines**: a breach, or a departure
     from the architect or approved design note, is `blocked <sha> architecture-unsound: <how>`.
 
-Return a verdict with your RESULT lines under a first line `Fix review: merge <head40>`
-or `Fix review: blocked <head40> <class>: <reason>`, class `[a-z-]+` (a script routes on it), then
-`bus-nonce: <nonce>`; an evidence file names the head. A cloud seat, with no `push-verdict`,
-commits them in `cloud_relay.sh`'s layout (`ev/`, subject `verdict <pr> <head40>`) to a
-fresh repository and pushes `probe/rev-<pr>-<nonce first 8>`.
+Return a verdict with your RESULT lines, its first line and `bus-nonce:` line
+in the grammar above; one that does not parse is refused.
 
 **Say which round this is**: from the fourth, `fixer.md` owes a re-cut, not a repair.
diff --git a/dev/governance/roles/fixer.md b/dev/governance/roles/fixer.md
index 87d46db8b..0f50222a5 100644
--- a/dev/governance/roles/fixer.md
+++ b/dev/governance/roles/fixer.md
@@ -85,9 +85,9 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
    the evidence describes one tree, and either makes a new one — **the body included**, because a figure that is a function
    of `origin/main`'s tip is false the moment `main` moves. Stamp such a figure
    with that tip and `date -u`. The code head goes to `handoff/<topic>`, the
-   body to the orphan `handoff-body/<topic>` (`seat/body_push.sh`),
-   off the code head (`prepr.sh` step 1a); that push is the handoff; the
-   orchestrator's `handoff_push.sh` opens the PR and writes the row.
+   body to the orphan `handoff-body/<topic>` by `seat/body_push.sh`, which
+   runs `review_packet.py handoff`'s offline refusals; answer each before the
+   push. That push is the handoff; `handoff_push.sh` opens the PR and writes the row.
 
    **The handoff freezes the branch.** Until then, merge `origin/main` (never
    rebase) only when `git merge-tree --write-tree origin/main HEAD` reports a
diff --git a/dev/programme/delivery/2939.md b/dev/programme/delivery/2939.md
new file mode 100644
index 000000000..82a53df3a
--- /dev/null
+++ b/dev/programme/delivery/2939.md
@@ -0,0 +1 @@
+- [#2939](https://github.com/tvofi/heatpump_optimizer/pull/2939) — **open**, R10-ORCH-REVIEW-PACKET: review_packet refuses a head lacking its handoff; fixer handoff runs it first (R10-ORCH-REVIEW-PACKET)
diff --git a/tools/audit/seat/body_push.sh b/tools/audit/seat/body_push.sh
index b830a63e1..09742fbee 100644
--- a/tools/audit/seat/body_push.sh
+++ b/tools/audit/seat/body_push.sh
@@ -48,6 +48,19 @@ if [ -n "$HREF" ]; then
     exit 1
   fi
   printf '%s\n' "$LINT" | tail -1
+  # The review packet's refusals that need no CI run (P256): structure merged
+  # with main, hot-file and brief-carries, answered here rather than after the
+  # open. rc 3 is a seat that cannot read their inputs: said, never a refusal.
+  # HPO_HANDOFF_PACKER replaces the checker (prepr's self-test stub).
+  prc=0
+  PK=$(cd "$ROOT" && ${HPO_HANDOFF_PACKER:-python3 -I "$HERE/review_packet.py"} handoff --topic "$TOPIC" --body "$ABS" 2>&1) || prc=$?
+  printf '%s\n' "$PK"
+  if [ "$prc" = 1 ]; then
+    echo "body_push: the review packet refuses this head at the handoff (above); answer each, push the code, then the body" >&2
+    exit 1
+  elif [ "$prc" != 0 ]; then
+    echo "body_push: the review packet's handoff refusals were not run (rc $prc, above); dispatch still runs structure and hot-file" >&2
+  fi
 else
   echo "body_push: no handoff/$TOPIC on origin, so a result body: the pr-body lint does not apply"
 fi
diff --git a/tools/audit/seat/instruments/body_push.sh.md b/tools/audit/seat/instruments/body_push.sh.md
index 8523c480a..cee2b6d4f 100644
--- a/tools/audit/seat/instruments/body_push.sh.md
+++ b/tools/audit/seat/instruments/body_push.sh.md
@@ -6,7 +6,8 @@
   the code head's ancestry (`prepr.sh` step 1a refuses that). Refusal: a
   head `tools/pr/ci_predict.py` predicts a closures or `fast` red on, or a
   checkout with no predictor (R10-HANDOFF-PREPR-BOUNCE M2), is refused
-  before anything is pushed, with each arm's repair printed; a fetch that
+  before anything is pushed, with each arm's repair printed; so is a PR body
+  `review_packet.py handoff` refuses (P256); a fetch that
   half-failed leaves a parentless commit the push refuses as a
   non-fast-forward — a rewrite is never forced through; the body commit it
   wrote is read back through `ref_privacy.py guard --commits`, message and
diff --git a/tools/audit/seat/instruments/review_packet.py.md b/tools/audit/seat/instruments/review_packet.py.md
index 24d33aa6c..6dcbd5e42 100644
--- a/tools/audit/seat/instruments/review_packet.py.md
+++ b/tools/audit/seat/instruments/review_packet.py.md
@@ -11,8 +11,12 @@
   renders its own from its dispatch prompt. Refusal: carry-audit, a `## Head`
   not naming the head, a `tests/structure.py` refusal at the head merged with
   main, an unanswered concluded red, a required context concluded failure, a
-  host path, or a hot file shared with an open pull request holding an
-  unboarded merge verdict; a pending check never refuses. A refusal still
+  host path, a hot file shared with an open pull request holding an
+  unboarded merge verdict, or a `fix/<t>` head lacking its `handoff/<t>` tip
+  (`handoff-not-applied`); a pending check never refuses. `handoff`, run by
+  `body_push.sh` before a PR body is pushed, refuses the structure and
+  hot-file signals and `brief-carries` (a roster carry the body never names
+  as `Carry N`). A refusal still
   WRITES the packet, so a held dispatch never withholds the evidence, except
   a host path, which writes nothing because the packet carries the diff.
   Unavailable (rc 3, `UNAVAILABLE`) is a different outcome: the seat cannot
diff --git a/tools/audit/seat/review_packet.py b/tools/audit/seat/review_packet.py
index 3c5c6901b..d04fd0323 100644
--- a/tools/audit/seat/review_packet.py
+++ b/tools/audit/seat/review_packet.py
@@ -4,6 +4,7 @@
     review_packet.py render --pr N --head SHA --out FILE [--main REF]
                             [--harness PATH | --harness-file FILE] [--harness-arg A]...
     review_packet.py check FILE --head SHA     (rc 1: the packet names another head)
+    review_packet.py handoff --topic T --body FILE [--main REF] [--roster-ref REF]
     review_packet.py --self-test
 
 `bus.sh dispatch` renders it (owner ruling tvofi 2026-10-24, card 8) and names
@@ -36,9 +37,17 @@ REFUSALS (rc 1, each named by its signal), all mechanical:
   required-red     a required context's latest run concluded failure;
   host-path        the body or an added line names this host (`ref_privacy.py`);
   hot-file         the diff shares a HOT_FILES path with an open pull request
-                   whose merge verdict is at its head and not on the train.
+                   whose merge verdict is at its head and not on the train;
+  handoff-not-applied  the PR's branch is `fix/<t>` or `fix/<t>-pr`, `handoff/<t>`
+                   exists on origin, and its tip is not an ancestor of the head.
 A pending check never refuses. Every other finding prints as an advisory.
 
+AT THE HANDOFF (P256). `body_push.sh` runs `handoff` at the code head before
+the body is pushed, so a fixer answers before the open what dispatch would
+refuse after it: `structure` and `hot-file` as above, and `brief-carries`, each
+carry on the group's roster entry (the round roster, `group_for_branch` of
+`handoff/<topic>`) not named `Carry N` in the body. Same exit codes as `render`.
+
 EVIDENCE IS NEVER WITHHELD. A refusal that leaves the packet truthful still
 WRITES it and then exits 1, so whoever holds a refused dispatch reads the same
 facts the reviewer would have: `bus.sh dispatch` dies on the rc and records
@@ -119,7 +128,8 @@ HOT_FILES = ("tools/audit/seat/pr_args.sh", "tools/audit/seat/update_pr.sh",
              "dev/audit/harnesses/r10_seat_selftests_mutants.py")
 RED = {"failure", "cancelled", "timed_out", "action_required", "startup_failure"}
 LEDGER = "tests/mutation_ledger"
-SIGNALS = ("carry-audit", "head-note", "structure", "red-unanswered", "required-red", "host-path", "hot-file")
+SIGNALS = ("carry-audit", "head-note", "structure", "red-unanswered", "required-red", "host-path", "hot-file",
+           "handoff-not-applied")
 
 
 def git(*a: str, cwd: Path | None = None, check: bool = True) -> str:
@@ -187,6 +197,39 @@ def hot_file_refusals(paths: set[str], open_prs: list[dict], boarded: set[int],
     return out
 
 
+def handoff_topics(branch: str) -> list[str]:
+    """The handoff topics a pull request's branch can carry: `fix/<t>` or
+    `fix/<t>-pr`, `open_pr.sh`'s two spellings; none for any other shape."""
+    t = branch[len("fix/"):] if branch.startswith("fix/") else ""
+    return [x for x in ([t, t[:-len("-pr")]] if t.endswith("-pr") else [t]) if x]
+
+
+def handoff_not_applied(branch: str, head: str, tip_of, is_ancestor) -> str | None:
+    """Why `head` lacks its own handoff (P229), or None. `tip_of(topic)` is
+    `handoff/<topic>`'s tip on origin or None; the first topic with a ref
+    decides. A branch of another shape, or no handoff ref, is never refused."""
+    for t in handoff_topics(branch):
+        tip = tip_of(t)
+        if tip:
+            return None if is_ancestor(tip, head) else f"handoff/{t} {tip} is not an ancestor of {head}"
+    return None
+
+
+def origin_handoff_tip(topic: str) -> str | None:
+    tip = git("ls-remote", "origin", f"refs/heads/handoff/{topic}").split()
+    if not tip:
+        return None
+    git("fetch", "-q", "origin", f"refs/heads/handoff/{topic}")
+    return tip[0]
+
+
+def is_ancestor(a: str, b: str) -> bool:
+    r = subprocess.run(["git", "merge-base", "--is-ancestor", a, b], cwd=repo(), capture_output=True, text=True)
+    if r.returncode not in (0, 1):
+        raise Unavailable(f"git merge-base --is-ancestor {a} {b}: {r.stderr.strip()[:200]}")
+    return r.returncode == 0
+
+
 def verdict_merge_head(sha: str, read=None) -> str | None:
     """The head a merge verdict names, or None: the first line of `VERDICT.md`
     in the verdict ref's commit, parsed by `proof_watch.parse_verdict`, the one
@@ -277,6 +320,23 @@ def writes_packet(refusals: list[str]) -> bool:
     return not any(r.startswith("host-path:") for r in refusals)
 
 
+def unnamed_carries(body: str, n: int) -> list[int]:
+    """The 1-based indexes of a group's `n` roster carries the body never names
+    as `Carry N` (any case, `[N]` too). A count, not a judgement: whether the
+    named carry is answered well is the reviewer's."""
+    return [i for i in range(1, n + 1)
+            if not re.search(rf"\bcarry\s*\[?{i}\]?(?![0-9])", body, re.I)]
+
+
+def handoff_refusals(structure: str | None, hot: list[str], unnamed: list[int]) -> list[str]:
+    """The refusals that need no CI run: the packet's `structure` and `hot-file`,
+    and the handoff's `brief-carries` count (P256). One spelling for both callers."""
+    out = [f"structure: tests/structure.py refuses the head merged with main: {structure}"] if structure else []
+    out += [f"hot-file: {w}" for w in hot]
+    out += [f"brief-carries: carry {i} is not named in the body (`Carry N`)" for i in unnamed]
+    return out
+
+
 # ------------------------------------------------------------------- the packet
 def build(facts: dict) -> tuple[list[str], list[str], str]:
     """(refusals, advisories, packet text) from gathered facts; pure."""
@@ -287,16 +347,15 @@ def build(facts: dict) -> tuple[list[str], list[str], str]:
         refusals.append("carry-audit: carry_audit.py check returned 1 on the body")
     if not head_note_ok(body, head):
         refusals.append(f"head-note: ## Head does not name the dispatched head {head}")
-    if facts["structure"]:
-        refusals.append(f"structure: tests/structure.py refuses the head merged with main: {facts['structure']}")
+    refusals += handoff_refusals(facts["structure"], facts["hot"], [])
     for n in facts["red_unanswered"]:
         refusals.append(f"red-unanswered: concluded red check `{n}` is not named in ## Red checks")
     for n in sorted(set(reds) & set(REQUIRED)):
         refusals.append(f"required-red: required context `{n}` concluded failure at {head}")
     for w in facts["host"]:
         refusals.append(f"host-path: {w}")
-    for w in facts["hot"]:
-        refusals.append(f"hot-file: {w}")
+    if facts.get("handoff"):
+        refusals.append(f"handoff-not-applied: {facts['handoff']}")
     advisories = [a for a in facts.get("advisories", [])]
     parts = [
         f"# Review packet #{facts['pr']}",
@@ -321,7 +380,9 @@ def gather(a) -> dict:
     touched = set(git("diff", "--name-only", "--no-renames", f"{base}...{head}").split())
     label, data = (harness_source(a.harness, a.harness_file, base, touched)
                    if (a.harness or a.harness_file) else ("none named", b""))
-    body = gh(f"repos/{REPO}/pulls/{a.pr}").get("body") or ""
+    pr = gh(f"repos/{REPO}/pulls/{a.pr}") or {}
+    body = pr.get("body") or ""
+    handoff = handoff_not_applied((pr.get("head") or {}).get("ref") or "", head, origin_handoff_tip, is_ancestor)
     runs = gh(f"repos/{REPO}/commits/{head}/check-runs?per_page=100").get("check_runs", [])
     gate = gate_digest(runs)
     crc, cout = tool([sys.executable, "-I", "tools/audit/carry_audit.py", "check", "--body", "{BODY}"], body)
@@ -334,22 +395,12 @@ def gather(a) -> dict:
     ident = ref_privacy.Identity.of_host()
     host = [w for w in [ref_privacy.body_refusal(body, ident)] if w]
     host += ref_privacy.content_refusals(ref_privacy.added_lines(base, head, repo()), ident)
-    open_prs, boarded = [], set()
-    if touched & set(HOT_FILES):
-        for p in gh(f"repos/{REPO}/pulls?state=open&per_page=100"):
-            files = [f["filename"] for f in gh(f"repos/{REPO}/pulls/{p['number']}/files?per_page=100")]
-            tip = git("ls-remote", "origin", f"refs/heads/verdict/{p['number']}", check=False).split()
-            merge_head = None
-            if tip and not git("fetch", "-q", "origin", f"refs/heads/verdict/{p['number']}", check=False):
-                merge_head = verdict_merge_head(tip[0])
-            open_prs.append({"number": p["number"], "head": p["head"]["sha"], "files": files,
-                             "merge_verdict_head": merge_head})
-        boarded = train_boarded()
+    open_prs, boarded = hot_prs(touched)
     return {
         "pr": a.pr, "head": head, "base": base, "body": body, "gate": gate,
         "carry_rc": crc, "carry_out": cout, "figure_out": fout,
         "structure": None if a.no_structure else structure_at_merge(main, head),
-        "red_unanswered": red_unanswered, "host": host,
+        "red_unanswered": red_unanswered, "host": host, "handoff": handoff,
         "hot": hot_file_refusals(touched, open_prs, boarded, a.pr),
         "advisories": [] if os.environ.get("HPO_BUS_TRAIN_STATE") or not open_prs
         else ["hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded"],
@@ -361,6 +412,51 @@ def gather(a) -> dict:
     }
 
 
+def hot_prs(touched: set[str]) -> tuple[list[dict], set[int]]:
+    """(open pull requests, boarded numbers) the hot-file rule reads; no read
+    at all when the diff touches no hot file."""
+    open_prs: list[dict] = []
+    if not touched & set(HOT_FILES):
+        return open_prs, set()
+    for p in gh(f"repos/{REPO}/pulls?state=open&per_page=100"):
+        files = [f["filename"] for f in gh(f"repos/{REPO}/pulls/{p['number']}/files?per_page=100")]
+        tip = git("ls-remote", "origin", f"refs/heads/verdict/{p['number']}", check=False).split()
+        merge_head = None
+        if tip and not git("fetch", "-q", "origin", f"refs/heads/verdict/{p['number']}", check=False):
+            merge_head = verdict_merge_head(tip[0])
+        open_prs.append({"number": p["number"], "head": p["head"]["sha"], "files": files,
+                         "merge_verdict_head": merge_head})
+    return open_prs, train_boarded()
+
+
+def handoff(a) -> int:
+    """`handoff`: the refusals a fixer answers before the push (P256), at this
+    checkout's HEAD. `head-note` is prepr's own at the same push (`--body-check`
+    hands policy_lint `--head HEAD`), and the CI-dependent ones stay at dispatch
+    (card 5), so this runs `structure`, `hot-file` and `brief-carries`."""
+    import roster_lib
+    head = git("rev-parse", "HEAD").strip()
+    body = Path(a.body).read_text()
+    touched = set(git("diff", "--name-only", "--no-renames", f"{git('merge-base', a.main, head).strip()}...{head}").split())
+    ref = a.roster_ref or roster_lib.round_ref(roster_lib.git_in(str(repo())))
+    if not ref:
+        raise Unavailable("roster_lib.round_ref names no round roster branch")
+    git("fetch", "-q", "--no-tags", "origin", f"+refs/heads/{ref.removeprefix('origin/')}:refs/remotes/{ref}")
+    try:
+        roster = roster_lib.show_roster(str(repo()), ref)
+    except Exception as e:  # noqa: BLE001 -- an unread roster is not an empty one
+        raise Unavailable(f"cannot read the roster at {ref}: {e}")
+    gid = roster_lib.group_for_branch(roster, f"handoff/{a.topic}")
+    carries = len(roster_lib.groups_of(roster)[gid].get("carry") or []) if gid else 0
+    open_prs, boarded = hot_prs(touched)
+    refusals = handoff_refusals(structure_at_merge(a.main, head),
+                                hot_file_refusals(touched, open_prs, boarded, 0), unnamed_carries(body, carries))
+    for x in refusals:
+        print(f"review_packet: REFUSE {x}", file=sys.stderr)
+    print(f"review-packet handoff: {gid or 'no group'} at {head[:12]}, {carries} carries, {len(refusals)} refused")
+    return 1 if refusals else 0
+
+
 def train_boarded() -> set[int]:
     state = os.environ.get("HPO_BUS_TRAIN_STATE")
     if not state:
@@ -436,6 +532,21 @@ def _self_test() -> int:
     check("write-on-refusal: one host path beside other refusals still writes nothing",
           not writes_packet(["required-red: gate", "host-path: a home directory"]))
 
+    # brief-carries (P256): every index on the group's roster entry is named.
+    six = "".join(f"Carry {i}: answered.\n" for i in range(1, 6))
+    check("brief-carries: a body answering carries 1-5 of 6 is refused naming carry 6",
+          unnamed_carries(six, 6) == [6]
+          and handoff_refusals(None, [], unnamed_carries(six, 6)) == ["brief-carries: carry 6 is not named in the body (`Carry N`)"])
+    check("brief-carries null: the same body with carry 6 dispositioned passes",
+          unnamed_carries(six + "Carry 6: carried to R10-X.\n", 6) == [])
+    check("brief-carries null: a group with no carries passes", unnamed_carries("", 0) == [])
+    check("brief-carries: `carry 1` does not name carry 10, and `Carry [10]` does",
+          unnamed_carries("Carry 1: x\n", 10)[-1] == 10 and 10 not in unnamed_carries("Carry [10]: x\n", 10))
+    check("handoff: structure and hot-file refuse beside the count, each named",
+          [r.split(":")[0] for r in handoff_refusals("max_class_loc", ["#9 x"], [2])]
+          == ["structure", "hot-file", "brief-carries"])
+    check("handoff null: a clean head refuses nothing", handoff_refusals(None, [], []) == [])
+
     prs = [{"number": 9, "head": H, "files": [HOT_FILES[0]], "merge_verdict_head": H}]
     check("hot-file arm: an unboarded merge verdict sharing a hot file refuses",
           len(hot_file_refusals({HOT_FILES[0]}, prs, set(), 7)) == 1)
@@ -487,6 +598,31 @@ def _self_test() -> int:
             ok = "inside the tree" in str(e)
         check("independence: --harness-file inside the checkout is refused", ok)
 
+        # handoff-not-applied (P229), over real ancestry: #2887's shape is the
+        # bot's merge of the OLD head with main, the fixer's handoff tip outside it.
+        def commit(msg: str, *parents: str) -> str:
+            tree = tgit("rev-parse", f"{parents[0]}^{{tree}}").strip()
+            return tgit("commit-tree", tree, *[x for p in parents for x in ("-p", p)], "-m", msg).strip()
+        old = commit("old head", base)
+        tip = commit("handoff tip", old)
+        mainc = commit("main moves", base)
+        stale, fresh = commit("merge old head + main", old, mainc), commit("merge tip + main", tip, mainc)
+
+        def anc(a: str, b: str) -> bool:
+            return subprocess.run(["git", "merge-base", "--is-ancestor", a, b], cwd=t, env=denv).returncode == 0
+        tips = {"g": tip}.get
+        check("handoff-not-applied: #2887's shape (old head merged with main, tip outside) refuses",
+              (handoff_not_applied("fix/g", stale, tips, anc) or "").startswith(f"handoff/g {tip} is not an ancestor of {stale}")
+              and refused("handoff-not-applied", handoff=handoff_not_applied("fix/g", stale, tips, anc)))
+        check("handoff-not-applied: the `fix/<t>-pr` spelling reads handoff/<t>",
+              handoff_not_applied("fix/g-pr", stale, tips, anc) is not None)
+        check("handoff-not-applied null: a head containing the handoff tip renders",
+              handoff_not_applied("fix/g", fresh, tips, anc) is None)
+        check("handoff-not-applied null: a pull request with no handoff ref renders",
+              handoff_not_applied("fix/nohandoff", stale, tips, anc) is None)
+        check("handoff-not-applied null: a branch not spelled fix/<t> renders",
+              handoff_not_applied("g", stale, tips, anc) is None and handoff_not_applied("feat/g", stale, tips, anc) is None)
+
         # WHICH CHECKOUT, pinned by a read, not by a comment: every git read
         # goes through `repo()`, and `repo()` is the working directory's
         # checkout. Read from this self-test's own checkout instead and the
@@ -562,6 +698,11 @@ def main(argv: list[str]) -> int:
     g.add_argument("--harness-file")
     r.add_argument("--harness-arg", action="append", default=[])
     r.add_argument("--no-structure", action="store_true", help="skip the structure merge check (self-test only)")
+    h = sub.add_parser("handoff")
+    h.add_argument("--topic", required=True)
+    h.add_argument("--body", required=True)
+    h.add_argument("--main", default="origin/main")
+    h.add_argument("--roster-ref")
     c = sub.add_parser("check")
     c.add_argument("packet")
     c.add_argument("--head", required=True)
@@ -572,6 +713,12 @@ def main(argv: list[str]) -> int:
             print(f"review_packet: REFUSE stale: {a.packet} names head {got}, not {a.head}", file=sys.stderr)
             return 1
         return 0
+    if a.cmd == "handoff":
+        try:
+            return handoff(a)
+        except Unavailable as e:
+            print(f"review_packet: UNAVAILABLE: {e}", file=sys.stderr)
+            return 3
     if not re.fullmatch(r"[0-9a-f]{40}", a.head):
         print("review_packet: --head takes a 40-hex sha", file=sys.stderr)
         return 2
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index 5cd48da69..549ef9215 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -2788,6 +2788,19 @@ https://claude.ai/code/session_011aqzm4YL9jLhU4jLvbkLYE'; got=$(lpush)
   bbody none none; got=$(lpush)
   grep -q '^rc=0$' <<<"$got" && grep -q '^ref refs/heads/handoff-body/zz-lint$' <<<"$got"
   st $? 0 "and pushes a body the lint passes (null control: the same body without the session link)"
+  # P256: body_push runs the review packet's handoff refusals after the lint;
+  # a refusal (rc 1) pushes nothing, a seat that cannot run them (rc 3) pushes.
+  printf '#!/bin/bash\necho "review_packet: REFUSE brief-carries: carry 6 is not named in the body" >&2; exit %s\n' 1 > "$PDX/pk1"
+  printf '#!/bin/bash\necho "review_packet: UNAVAILABLE: no roster" >&2; exit %s\n' 3 > "$PDX/pk3"
+  was=$(git --git-dir="$PDX/bodies.git" rev-parse refs/heads/handoff-body/zz-lint)
+  got=$(HPO_HANDOFF_PACKER="bash $PDX/pk1" lpush)
+  grep -q 'REFUSE brief-carries: carry 6' <<<"$got" && grep -q '^rc=1$' <<<"$got" \
+    && [ "$(git --git-dir="$PDX/bodies.git" rev-parse refs/heads/handoff-body/zz-lint)" = "$was" ]
+  st $? 0 "and refuses a body the review packet's handoff refusals refuse, naming the signal and pushing nothing (P256)"
+  got=$(HPO_HANDOFF_PACKER="bash $PDX/pk3" lpush)
+  grep -q 'were not run (rc 3' <<<"$got" && grep -q '^rc=0$' <<<"$got" \
+    && [ "$(git --git-dir="$PDX/bodies.git" rev-parse refs/heads/handoff-body/zz-lint)" != "$was" ]
+  st $? 0 "and pushes, saying so, when the handoff refusals cannot be run (rc 3 is never a refusal)"
   (cd "$PDX/r" && git push -q -f origin pinert:refs/heads/handoff/zz-lint); got=$(lpush)
   grep -q 'push the code, then the body' <<<"$got" && grep -q '^rc=1$' <<<"$got"
   st $? 0 "and refuses a body pushed from a checkout that is not the head at handoff/<topic>"

