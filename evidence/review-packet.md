# Review packet #3256
head: 9c8ca4f7acfae4366671942a34afa978e722643e
base: 30638cf0c8a7114019682f87051a4a282d2981ff

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128021634674 success
arch-score / arch-score id=128053810121 success
arm id=128020606966 skipped
budget-raise-gate / budget-raise-gate id=128053724646 success
cancel-superseded id=128053805222 success
codeql id=128053725692 skipped
codeql / Analyze (actions) id=128053713529 success
codeql / Analyze (javascript-typescript) id=128053714458 success
codeql / Analyze (python) id=128053713882 success
gate id=128053723956 failure
governance id=128053724449 skipped
governance / delivery-status id=128053713740 success
governance / delivery-status-publish id=128053715222 skipped
governance / env-matrix id=128053714768 success
governance / instrument-self-tests id=128053713196 cancelled
governance / policy-docs id=128053713750 success
governance / record id=128053714103 skipped
governance / wave-script id=128053713848 success
hassfest id=128053725204 skipped
hassfest / hassfest id=128053712950 success
kernel-points id=128053778045 skipped
pr-contract id=128053725874 skipped
pr-contract / pr-contract id=128054392050 queued
prelude id=128053770286 success
refresh id=128053785136 success
tests id=128053724778 skipped
tests / arch-instrument id=128053716136 success
tests / briefs id=128053713844 success
tests / browser id=128053717234 success
tests / ci-ratchet id=128053720786 skipped
tests / claims-autofix id=128053720145 skipped
tests / closure-scope id=128053714013 success
tests / closures id=128053716902 success
tests / closures-autofix id=128053720565 skipped
tests / coverage id=128053716689 success
tests / coverage-ratchet id=128053721012 success
tests / fast (3.14) id=128053716570 success
tests / graders-head-copy id=128053719559 success
tests / lane-proofs id=128053720091 success
tests / mutation id=128053713628 success
tests / mutation-autofix id=128053718919 skipped
tests / mutation-pins id=128053716210 skipped
tests / nightly-ha id=128053717124 skipped
tests / nightly-status id=128053713859 success
tests / replay id=128053717044 skipped
tests / typing id=128053716671 success
validate id=128053724881 skipped
validate / validate-hacs id=128053714706 success

## Refusals
required-red: required context `gate` concluded failure at 9c8ca4f7acfae4366671942a34afa978e722643e

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE stale tree: 9c8ca4f7acfae4366671942a34afa978e722643e lacks origin/main 4b7e1770ba81fa02a8dda531463eba68e987ff59; roster read at origin/main
NOTE body item 99798c14: dismissed:closed in this diff (nudge.md steps 3 and 7)
NOTE body item 60ed18ec: #2717
NOTE body item 5c062def: #2717
NOTE body item 0cbeba06: #2717
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified bash -c '. tools/audit/seat/pr_args.sh; pr_pushers'
             bash runs an inline script rather than a file
  ok         tools/policy/role_pack.py
             `tools/policy/role_pack.py` is in the tree at this head
  ok         bash tools/audit/seat/pr_args.sh --self-test
             `tools/audit/seat/pr_args.sh` is in the tree at this head
  ok         python3 -I tools/policy/role_pack.py sizes
             `tools/policy/role_pack.py` is in the tree at this head
  ok         python3 -I tools/policy/role_pack.py check
             `tools/policy/role_pack.py` is in the tree at this head
  ok         python3 -I tools/policy/role_pack.py --self-test
             `tools/policy/role_pack.py` is in the tree at this head
  ok         bash .claude/hooks/session-start.sh --self-test
             `.claude/hooks/session-start.sh` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 -I tools/audit/seat/selftest_wiring.py --check
             `tools/audit/seat/selftest_wiring.py` is in the tree at this head
  ok         node tools/policy/rules_sync.mjs --check
             `tools/policy/rules_sync.mjs` is in the tree at this head
  ok         tests/closure.py
             `tests/closure.py` is in the tree at this head

FIGURES: 16 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.claude/hooks/session-start.sh b/.claude/hooks/session-start.sh
index 2b18d2349..79a6e7f16 100755
--- a/.claude/hooks/session-start.sh
+++ b/.claude/hooks/session-start.sh
@@ -122,6 +122,21 @@ report() {
   printf 'toolchain:      %s\n' "$(toolchain)"
 }
 
+role_pack() { # the `role pack:` line, printed only when HPO_SEAT_ROLE is set
+  # tools/policy/role_pack.py says why the pack is a file and not this stdout.
+  local role=$1 out err
+  out=$(git rev-parse --git-path "role-pack-$role.md" 2>/dev/null) || out=
+  if [ -z "$out" ]; then
+    printf 'role pack:      REFUSE -- no git directory to write it in; read your contract and INSTRUMENTS.md as before\n'; return
+  fi
+  if err=$(python3 -I tools/policy/role_pack.py render "$role" --out "$out" 2>&1 </dev/null); then
+    printf 'role pack:      %s -- %s bytes: your dev/governance/roles/ contract, the rules its reads load and the INSTRUMENTS.md entries it names, verbatim; read it once in place of those files\n' \
+      "$out" "$(wc -c < "$out" | tr -d ' ')"
+  else
+    printf 'role pack:      REFUSE -- %s; read your contract and INSTRUMENTS.md as before\n' "$(printf '%s' "$err" | tail -1)"
+  fi
+}
+
 if [ "${1:-}" = "--env-lines" ]; then
   env_lines; exit 0
 fi
@@ -180,10 +195,27 @@ if [ "${1:-}" = "--self-test" ]; then
   else
     fail=$((fail+1)); printf '  FAIL %s\n' "the claimnotes merge driver is configured after a run"
   fi
+  # THE ROLE PACK (tools/policy/role_pack.py). Unset, the hook prints exactly
+  # what it printed before the pack existed: the same run with the variable
+  # set must be that output plus one `role pack:` line, and nothing else.
+  unset_out=$(env -u HPO_SEAT_ROLE bash "$0" </dev/null)
+  set_out=$(HPO_SEAT_ROLE=fixer bash "$0" </dev/null)
+  if [ "$unset_out" = "$(report)" ]; then pass=$((pass+1)); printf '  ok   %s\n' "unset, the hook prints the clone-fact report and not a byte more"
+  else fail=$((fail+1)); printf '  FAIL %s\n' "unset, the hook prints the clone-fact report and not a byte more"; fi
+  ans "$(printf '%s\n' "$unset_out" | grep -c '^role pack:')" "0" "unset, no role pack line is printed"
+  ans "$set_out" "$unset_out
+role pack:      " "set, the output is the unset output plus one role pack line"
+  ans "$(printf '%s\n' "$set_out" | grep -c '^role pack:')" "1" "set, exactly one role pack line"
+  ans "$(printf '%s\n' "$set_out" | wc -l | tr -d ' ')" "$(( $(printf '%s\n' "$unset_out" | wc -l) + 1 ))" "set, one line more than unset, and no other"
+  P=$(git rev-parse --git-path role-pack-fixer.md)
+  ans "$(python3 -I tools/policy/role_pack.py check fixer --pack "$P" 2>&1 | head -1)" "ok   fixer:" "the pack the line names checks clean as the fixer's"
+  ans "$(HPO_SEAT_ROLE=planner bash "$0" </dev/null | tail -1)" "role pack:      REFUSE -- " "an unknown role prints a REFUSE line and still starts"
+  ans "$(python3 -I tools/policy/role_pack.py --self-test 2>&1 | tail -1 | sed -n 's/^[1-9][0-9]* passed, \([0-9]*\) failed$/\1/p')" "0" "role_pack.py's self-test passes: every role clean, every rule's mutant refused"
   printf '\n%s passed, %s failed\n' "$pass" "$fail"
   [ "$fail" -eq 0 ] || exit 2
   exit 0
 fi
 
 report
+[ -n "${HPO_SEAT_ROLE:-}" ] && role_pack "$HPO_SEAT_ROLE"
 exit 0
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index a3b2ce4db..759ec575e 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -610,6 +610,7 @@ jobs:
           python3 -I tools/pr/head_note.py --self-test
           python3 -I tools/release/stamp.py --self-test
           python3 -I tools/policy/agreement_py.py --self-test
+          python3 -I tools/policy/role_pack.py --self-test
           # The wave-script restore list is derived, never carried: every .py
           # file the agreement reader loads must be restored from the base,
           # or a head whose readers agree still reads divergent (#2423).
diff --git a/dev/governance/roles/nudge.md b/dev/governance/roles/nudge.md
index 8270360db..73198fb27 100644
--- a/dev/governance/roles/nudge.md
+++ b/dev/governance/roles/nudge.md
@@ -44,12 +44,12 @@ Find a live `tools/audit/seat/merge_train.py` and read its log. A live process h
 
 Load a train on the hourly pitch, with `--bot-prs`, when no train is running and fewer than four preprs are running. One verdicted pull request is still a train. The record pull request merges inside the pitch, not between pitches. Verdicted means the newest posted fix review is merge for this 40-hex head, or `tools/pr/app_approve.sh` carry says the verdict carries. The train waits for CI in its own ci step, so do not wait for it. Order the queue by creation time, oldest first. Each entry carries the pull request number, the 40-hex the merge verdict names, the comment id (the comment must cite an absolute evidence path), and the issues the body intends to close.
 
-Leave out of the queue: a change to a `*_budgets.json` file, a policy path as `policy_lint.mjs --corpus-filter` defines it, and a `record:` pull request, which `--bot-prs` merges. Never pass `--allow-red`.
+Leave out a `record:` pull request, which `--bot-prs` merges. A `*_budgets.json` or policy-path head stays in: the train routes it serial, and `--pre-flight` parks one the owner has not approved at that head (`Train.raise_hold`, `Train.policy_gate`) for step 7. Never pass `--allow-red`.
 
 The command is detached, because a background waiter dies at two hours:
 
 ```
-python3 -u tools/audit/seat/merge_train.py run <queue.json> --mandate "<the session mandate cite>" --ignore-red 'tests / nightly-status' --ignore-red 'governance / delivery-status'
+python3 -u tools/audit/seat/merge_train.py run <queue.json> --bot-prs --pre-flight --mandate "<the session mandate cite>" --ignore-red 'tests / nightly-status' --ignore-red 'governance / delivery-status'
 ```
 
 ## 4. Required checks
@@ -66,7 +66,7 @@ A `record:` pull request needs no fix review and no reviewer. The nightly record
 
 ## 7. Direct merge, when no train is running
 
-Direct-merge only what step 3 leaves out of the queue, other than a `record:` pull request: a budgets-file or policy-path pull request whose mandate review is already on that head. Ready means required checks are success or skipped, GitHub reports it mergeable, and the newest posted fix review is merge for this head or carries. Oldest first. Anything the queue takes waits for the pitch.
+Direct-merge only what `--pre-flight` parked: a budgets-file or policy-path pull request whose mandate review is already on that head. Ready means required checks are success or skipped, GitHub reports it mergeable, and the newest posted fix review is merge for this head or carries. Oldest first. Anything the queue takes waits for the pitch.
 
 ## 8. Prepr slots
 
diff --git a/dev/programme/delivery/3256.md b/dev/programme/delivery/3256.md
new file mode 100644
index 000000000..354dec696
--- /dev/null
+++ b/dev/programme/delivery/3256.md
@@ -0,0 +1 @@
+- [#3256](https://github.com/tvofi/heatpump_optimizer/pull/3256) — **open**, R10-POLICY-ROLE-PACK: policy role pack (R10-POLICY-ROLE-PACK)
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index e12dbe55b..57fcb0697 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -24,6 +24,7 @@ re-runnable measurement harnesses a fixer or judge lands with a PR — its
 - [`app_push.sh`](instruments/app_push.sh.md) — pushes a branch and opens or re-bodies its pull request as the `hpo-author` App
 - [`depgraph.py` (tools/pr/)](instruments/depgraph.py.md) — compares GitHub's dependency graph with the tree's pins
 - [`head_note.py` (tools/pr/)](instruments/head_note.py.md) — prefixes a note under a body's `## Head` heading, found as `checkPrBody`'s `sections()` reads it (outside a fence, `##`, whitespace, `Head`)
+- [`role_pack.py` (tools/policy/)](instruments/role_pack.py.md) — renders one seat's policy pack: its role contract, the rules its reads load and the INSTRUMENTS.md entries it names, verbatim, in one file
 - [`approve_held_runs.sh`](instruments/approve_held_runs.sh.md) — approves the workflow runs GitHub holds `action_required` on a branch
 - [`check_scopes.py`](instruments/check_scopes.py.md) — proves the finder scopes are disjoint and complete within each dimension
 - [`fold_ledger.py`](instruments/fold_ledger.py.md) — folds a round's JUDGE.json and sweeps into `bugclasses.json`
diff --git a/tools/audit/seat/instruments/role_pack.py.md b/tools/audit/seat/instruments/role_pack.py.md
new file mode 100644
index 000000000..546e3943c
--- /dev/null
+++ b/tools/audit/seat/instruments/role_pack.py.md
@@ -0,0 +1,20 @@
+# `role_pack.py`
+
+- `role_pack.py` (tools/policy/) — renders one seat's policy pack: its
+  contract under `dev/governance/roles/` (`fixer`, `fix-review`, `designer`,
+  `design-review`, `root-cause`, `verifier`, `judge`, and `finder` for
+  `COMMON.md`), every rule under `dev/governance/rules/` whose `paths:` globs
+  the contract or `INSTRUMENTS.md` matches, and the `INSTRUMENTS.md` entry
+  lines whose instrument the contract names, each framed and byte-equal to its
+  file. CLAUDE.md is left out: the harness has already loaded it.
+  `.claude/hooks/session-start.sh` writes the pack to `git rev-parse
+  --git-path role-pack-<role>.md` and prints one `role pack:` line when
+  `HPO_SEAT_ROLE` names a role; unset, the hook's output is unchanged. A file
+  rather than the hook's stdout, because Claude Code keeps at most 10,000
+  characters of hook output in context. An Agent-tool subagent runs no
+  SessionStart hook, so a local seat's brief names `render <role> --out
+  <path>` itself. When: a seat brief that would otherwise tell a seat to read
+  its contract and this guide. `check [<role> ...] [--pack FILE]` refuses a
+  paraphrased line, a missing or extra block, a line outside every frame and a
+  pack larger than the files it frames; `--self-test` drives every role and
+  one mutant per rule. Refusal: an unknown role exits 2, naming the roles.
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index 177a289c2..164eea228 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -365,6 +365,7 @@ tools/pr/head_note.py mention: its docstring
 tools/policy/check-wave-script.mjs mention: a test title
 tools/policy/friction_issues.mjs mention: comments
 tools/audit/seat/gh_read.py mention: its docstring cites the read-back rule of app_push.sh; it runs no subprocess
+tools/policy/role_pack.py mention: its docstring and name-match self-test use the pusher names as sample instrument names; it runs no subprocess
 tools/audit/seat/body_patch.sh mention: comments; it PATCHes a body through app_mint.sh and runs no push
 tools/audit/seat/body_push.sh mention: comments; it writes the Prepr: trailer app_push.sh --reuse reads, and runs no push
 tools/pr/prepr.sh mention: comments; it honours the receipt app_push.sh --reuse passes it, and runs no push
diff --git a/tools/policy/role_pack.py b/tools/policy/role_pack.py
new file mode 100644
index 000000000..c30018bd1
--- /dev/null
+++ b/tools/policy/role_pack.py
@@ -0,0 +1,371 @@
+#!/usr/bin/env python3
+"""One seat's policy, verbatim, in one read: its role contract, the rules that
+contract's reads load, and the INSTRUMENTS.md entries the contract names.
+
+    python3 tools/policy/role_pack.py render <role> [--out FILE]
+    python3 tools/policy/role_pack.py check [<role> ...] [--pack FILE]
+    python3 tools/policy/role_pack.py sizes
+    python3 tools/policy/role_pack.py --self-test
+
+WHY. A seat opens by reading its contract under dev/governance/roles/ and
+tools/audit/seat/INSTRUMENTS.md with tool calls; each read lands the same text in
+its context again, and INSTRUMENTS.md arrives whole although a contract names a
+fraction of its entries. The pack is that reading done once, by a program, and
+filtered only where the filter is mechanical. `.claude/hooks/session-start.sh`
+writes it when HPO_SEAT_ROLE names a role, and prints one line naming it.
+
+WHY A FILE, NOT THE HOOK'S STDOUT. Claude Code (2.1.318, read in its bundle)
+keeps hook stdout of at most 10,000 characters in context; longer output is
+saved to disk and the context gets a preview whose path it hides. Every pack
+is longer than that (`check` prints each size), so a pack printed whole would
+reach a seat as a preview it cannot follow. The pack goes under the git
+directory (`git rev-parse --git-path`): in the checkout, untracked, and read
+once by a path the seat can name.
+
+VERBATIM, NEVER PARAPHRASED. Every byte between a BEGIN and an END frame is a
+byte of the file the frame names: a whole file, or (INSTRUMENTS.md) whole entry
+lines of it. A paraphrase once made a seat read real policy as something else,
+so `check` refuses any line no source holds, and every source the role's plan
+names must be present whole.
+
+CLAUDE.md IS NOT IN THE PACK, deliberately. The harness injects it into every
+Claude Code session before any hook output (a session transcript carries it as
+a system-reminder), and this hook is Claude Code's, so a pack holding it would
+put the same text in the same context twice.
+
+WHICH RULES. Claude Code loads a rule under .claude/rules/ when a read matches
+its `paths:` globs. A seat given the pack does not read its contract or
+INSTRUMENTS.md, so the rules those reads would have loaded come in the pack:
+every rule under dev/governance/rules/ (the canonical text; .claude/rules/ is
+generated from it) with a glob matching one of the role's files. Derived at
+each render, never listed: a rule whose globs change moves with them.
+
+WHICH INSTRUMENTS. An INSTRUMENTS.md entry line is `- [`name ...`](instruments/
+...) -- ...`; it is in the pack when the contract's text names `name` (the first
+word in the backticks) as a whole token: not preceded by a word character, `.`
+or `-`, so `push.sh` does not match inside `app_push.sh`.
+"""
+from __future__ import annotations
+
+import argparse
+import fnmatch
+import re
+import sys
+from pathlib import Path
+
+ROOT = Path(__file__).resolve().parents[2]
+ROLES_DIR = "dev/governance/roles"
+RULES_DIR = "dev/governance/rules"
+INSTRUMENTS = "tools/audit/seat/INSTRUMENTS.md"
+ENV_VAR = "HPO_SEAT_ROLE"
+
+# The roles a pack is rendered for, and the contract each opens. `finder` is
+# every audit dimension's finder, whose contract is COMMON.md.
+ROLE_CONTRACT = {
+    "fixer": "fixer.md",
+    "fix-review": "fix-review.md",
+    "designer": "designer.md",
+    "design-review": "design-review.md",
+    "root-cause": "root-cause.md",
+    "verifier": "verifier.md",
+    "judge": "judge.md",
+    "finder": "COMMON.md",
+}
+
+BEGIN = "===== BEGIN {} ====="
+END = "===== END {} ====="
+FRAME = re.compile(r"^===== (BEGIN|END) (\S+)(?: \((.*)\))? =====$")
+ENTRY = re.compile(r"^- \[`([^`]+)`(?:[^\]]*)\]\(instruments/")
+
+
+class Refusal(Exception):
+    """A pack that cannot be rendered or does not check, in one line."""
+
+
+def _read(root: Path, rel: str) -> str:
+    try:
+        return (root / rel).read_text(encoding="utf-8")
+    except OSError as e:
+        raise Refusal(f"{rel}: {e.strerror}") from e
+
+
+def rule_globs(text: str) -> list[str]:
+    """The `paths:` list of a rule's YAML frontmatter; [] when it has none."""
+    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
+    if not m:
+        return []
+    globs, inside = [], False
+    for line in m.group(1).splitlines():
+        if re.match(r"paths:\s*$", line):
+            inside = True
+        elif inside and re.match(r"\s+-\s+", line):
+            globs.append(line.split("-", 1)[1].strip().strip("\"'"))
+        elif inside and line.strip():
+            inside = False
+    return globs
+
+
+def glob_match(pattern: str, path: str) -> bool:
+    """Claude Code's rule-glob reading: `**` spans any number of segments
+    (none included), every other segment is an fnmatch pattern that never
+    crosses a `/`."""
+    pat, segs = pattern.split("/"), path.split("/")
+
+    def go(i: int, j: int) -> bool:
+        if i == len(pat):
+            return j == len(segs)
+        if pat[i] == "**":
+            return any(go(i + 1, k) for k in range(j, len(segs) + 1))
+        return j < len(segs) and fnmatch.fnmatchcase(segs[j], pat[i]) and go(i + 1, j + 1)
+
+    return go(0, 0)
+
+
+def role_files(role: str) -> list[str]:
+    """The files a seat in `role` opens by reading, which the pack replaces."""
+    if role not in ROLE_CONTRACT:
+        raise Refusal(f"role must be one of {', '.join(ROLE_CONTRACT)} (got {role!r})")
+    return [f"{ROLES_DIR}/{ROLE_CONTRACT[role]}", INSTRUMENTS]
+
+
+def named_entries(contract: str, instruments: str) -> list[str]:
+    """INSTRUMENTS.md's entry lines whose instrument the contract names."""
+    out = []
+    for line in instruments.splitlines():
+        m = ENTRY.match(line)
+        if not m:
+            continue
+        name = m.group(1).split()[0]
+        if re.search(r"(?<![\w.-])" + re.escape(name) + r"(?![\w-])", contract):
+            out.append(line)
+    return out
+
+
+def plan(role: str, root: Path = ROOT) -> list[tuple[str, str, str]]:
+    """(path, note, text) blocks, in pack order: contract, rules, instruments."""
+    files = role_files(role)
+    contract_rel = files[0]
+    contract = _read(root, contract_rel)
+    blocks = [(contract_rel, "", contract)]
+    for rule in sorted((root / RULES_DIR).glob("*.md")):
+        rel = f"{RULES_DIR}/{rule.name}"
+        text = _read(root, rel)
+        hits = [f for f in files if any(glob_match(g, f) for g in rule_globs(text))]
+        if hits:
+            blocks.append((rel, "loaded by a read of " + ", ".join(hits), text))
+    if INSTRUMENTS in files:
+        entries = named_entries(contract, _read(root, INSTRUMENTS))
+        blocks.append((INSTRUMENTS, f"the {len(entries)} entries {contract_rel} names; "
+                       "read the file for any other",
+                       "".join(e + "\n" for e in entries)))
+    return blocks
+
+
+def render_blocks(role: str, blocks: list[tuple[str, str, str]]) -> str:
+    head = (f"ROLE PACK for {role} (tools/policy/role_pack.py): each block is the verbatim text "
+            "of the file its frame names, at this checkout, read in place of opening it; "
+            "CLAUDE.md is not repeated, the harness loaded it above.\n")
+    parts = [head]
+    for rel, note, text in blocks:
+        label = f"{rel} ({note})" if note else rel
+        body = text if text.endswith("\n") or not text else text + "\n"
+        parts.append(BEGIN.format(label) + "\n" + body + END.format(rel) + "\n")
+    return "".join(parts)
+
+
+def render(role: str, root: Path = ROOT) -> str:
+    return render_blocks(role, plan(role, root))
+
+
+def parse(pack: str) -> tuple[list[tuple[str, str]], list[str]]:
+    """((path, text) per block, stray lines outside any block but the header)."""
+    blocks, stray, cur, buf = [], [], None, []
+    for i, line in enumerate(pack.splitlines(keepends=True)):
+        m = FRAME.match(line.rstrip("\n"))
+        if m and m.group(1) == "BEGIN" and cur is None:
+            cur, buf = m.group(2), []
+        elif m and m.group(1) == "END" and cur == m.group(2):
+            blocks.append((cur, "".join(buf)))
+            cur = None
+        elif cur is not None:
+            buf.append(line)
+        elif not (i == 0 and line.startswith("ROLE PACK for ")):
+            stray.append(line.rstrip("\n"))
+    if cur is not None:
+        stray.append(f"(unterminated block {cur})")
+    return blocks, stray
+
+
+def check(role: str, pack: str, root: Path = ROOT) -> list[str]:
+    """Each way `pack` fails to be `role`'s pack, one line each; [] when it is."""
+    errs = []
+    want = plan(role, root)
+    got, stray = parse(pack)
+    got_paths = [p for p, _ in got]
+    errs += [f"a line outside every frame: {s!r}" for s in stray]
+    # Stated here, not read from role_files(): a file dropped from the role's
+    # list drops it from plan() too, so only an independent statement sees it.
+    for rel in (f"{ROLES_DIR}/{ROLE_CONTRACT[role]}", INSTRUMENTS):
+        if rel not in got_paths:
+            errs.append(f"{rel}: every {role} pack holds it, and this one does not")
+    for rel, _, text in want:
+        if rel not in got_paths:
+            errs.append(f"{rel}: in the role's plan, absent from the pack")
+    for rel, text in got:
+        source = _read(root, rel) if (root / rel).is_file() else None
+        if source is None:
+            errs.append(f"{rel}: the pack frames a file the tree does not hold")
+            continue
+        if rel == INSTRUMENTS:
+            lines = set(source.splitlines())
+            extra = [l for l in text.splitlines() if l not in lines]
+            errs += [f"{rel}: a line the file does not hold: {l!r}" for l in extra]
+            expect = next((t for r, _, t in want if r == INSTRUMENTS), None)
+            if expect is not None and text != expect:
+                errs.append(f"{rel}: the entries differ from those the contract names")
+        elif text != source:
+            errs.append(f"{rel}: not byte-equal to the file")
+        if rel not in [r for r, _, _ in want]:
+            errs.append(f"{rel}: framed, but not in the role's plan")
+    body = sum(len(t) for _, t in got)
+    whole = sum(len(_read(root, r)) for r in dict.fromkeys(got_paths) if (root / r).is_file())
+    if body > whole:
+        errs.append(f"the framed text ({body} chars) exceeds the files it frames ({whole})")
+    return errs
+
+
+def sizes(root: Path = ROOT) -> list[str]:
+    """Per role, in characters: the read set a pack replaces -- the contract,
+    the rules a Read of it loads and the whole INSTRUMENTS.md -- beside the pack.
+    A seat that reads its contract through Bash loads no rule, so its read set
+    is the contract and INSTRUMENTS.md alone: the third column."""
+    whole = len(_read(root, INSTRUMENTS))
+    out = ["role read_set(Read) read_set(Bash) pack pack-read_set(Read) entries"]
+    for role in ROLE_CONTRACT:
+        blocks = plan(role, root)
+        contract = len(blocks[0][2])
+        rules = sum(len(t) for r, _, t in blocks if r.startswith(RULES_DIR))
+        pack = len(render(role, root))
+        out.append(f"{role} {contract + rules + whole} {contract + whole} {pack} "
+                   f"{pack - contract - rules - whole} {len(blocks[-1][2].splitlines())}")
+    return out
+
+
+def self_test() -> int:
+    """Every role's pack checks clean, and each rule refuses its own mutant."""
+    passed = failed = 0
+
+    def t(ok: bool, what: str) -> None:
+        nonlocal passed, failed
+        passed, failed = passed + ok, failed + (not ok)
+        print(f"  {'ok  ' if ok else 'FAIL'} {what}")
+
+    for role in ROLE_CONTRACT:
+        pack = render(role)
+        t(check(role, pack) == [], f"{role}: the rendered pack checks clean (null control)")
+        contract = _read(ROOT, role_files(role)[0])
+        t(contract in pack, f"{role}: the pack holds its contract byte-equal")
+    t(glob_match("dev/governance/**", "dev/governance/roles/fixer.md"), "`**` spans segments")
+    t(glob_match("dev/governance/**", "dev/governance/x.md"), "`**` spans one segment")
+    t(not glob_match("tests/**", "dev/governance/roles/fixer.md"), "a foreign prefix does not match")
+    t(not glob_match("dev/*.md", "dev/governance/x.md"), "`*` does not cross a `/`")
+    t(named_entries("run seat/bus.sh", "- [`push.sh`](instruments/p) -- x\n"
+                    "- [`bus.sh`](instruments/b) -- y\n") == ["- [`bus.sh`](instruments/b) -- y"],
+      "an entry is named by its whole token, and only then")
+    t(named_entries("app_push.sh", "- [`push.sh`](instruments/p) -- x\n") == [],
+      "`push.sh` is not named by `app_push.sh`")
+
+    role = "fixer"
+    blocks = plan(role)
+    rules = [b for b in blocks if b[0].startswith(RULES_DIR)]
+    t(len(rules) > 0, "the fixer's plan carries at least one rule, so the rule mutant has a target")
+    entries = blocks[-1][2].splitlines()
+    t(len(entries) > 0, "the fixer's plan carries at least one instrument entry")
+
+    def refuses(mutant: list | str, what: str, rule: str) -> None:
+        """The mutant is refused BY ITS OWN RULE: `rule` is a fragment of the one
+        message that rule prints, so a mutant another rule happens to catch
+        does not count as this rule's."""
+        pack = mutant if isinstance(mutant, str) else render_blocks(role, mutant)
+        errs = check(role, pack)
+        t(any(rule in e for e in errs), f"mutant refused by its rule -- {what}"
+          + (f": {errs[0]}" if errs else ": not refused"))
+
+    absent, unequal, entries_rule = "absent from the pack", "not byte-equal", "the entries differ"
+    refuses(blocks[1:], "the contract dropped from the role's list", absent)
+    refuses([b for b in blocks if b is not rules[0]], f"a matched rule dropped ({rules[0][0]})", absent)
+    rel, note, text = blocks[0]
+    refuses([(rel, note, text.replace("Failing test first", "Write a test first", 1))] + blocks[1:],
+            "one contract line paraphrased", unequal)
+    other = next(l for l in _read(ROOT, INSTRUMENTS).splitlines()
+                 if ENTRY.match(l) and l not in entries)
+    refuses(blocks[:-1] + [(INSTRUMENTS, "", blocks[-1][2] + other + "\n")],
+            "an entry the contract does not name added", entries_rule)
+    refuses(blocks[:-1] + [(INSTRUMENTS, "", "".join(e + "\n" for e in entries[1:]))],
+            "an entry the contract names dropped", entries_rule)
+    refuses(blocks[:-1] + [(INSTRUMENTS, "", blocks[-1][2] + "- an instrument nobody wrote\n")],
+            "a line no source holds, inside a frame", "a line the file does not hold")
+    refuses(blocks + [("CLAUDE.md", "", _read(ROOT, "CLAUDE.md"))],
+            "a file outside the role's plan framed", "not in the role's plan")
+    module = sys.modules[__name__]
+    kept = module.role_files
+    module.role_files = lambda r: kept(r)[:1]  # INSTRUMENTS.md dropped from the list
+    try:
+        refuses(render(role), "INSTRUMENTS.md dropped from the role's list", "every fixer pack holds it")
+    finally:
+        module.role_files = kept
+    refuses(render_blocks(role, blocks) + "a sentence of paraphrase\n",
+            "a line outside every frame", "a line outside every frame")
+    refuses(blocks[:1] + blocks, "the contract framed twice (each copy byte-equal)", "exceeds the files")
+    try:
+        role_files("planner")
+        t(False, "an unknown role is refused")
+    except Refusal:
+        t(True, "an unknown role is refused")
+    print(f"\n{passed} passed, {failed} failed")
+    return 0 if failed == 0 else 1
+
+
+def main(argv: list[str]) -> int:
+    if argv == ["--self-test"]:
+        return self_test()
+    ap = argparse.ArgumentParser(prog="role_pack.py")
+    sub = ap.add_subparsers(dest="cmd", required=True)
+    r = sub.add_parser("render")
+    r.add_argument("role")
+    r.add_argument("--out")
+    sub.add_parser("sizes")
+    c = sub.add_parser("check")
+    c.add_argument("roles", nargs="*")
+    c.add_argument("--pack", help="check this file as the pack of the one role named")
+    a = ap.parse_args(argv)
+    try:
+        if a.cmd == "render":
+            pack = render(a.role)
+            if a.out:
+                Path(a.out).write_text(pack, encoding="utf-8")
+            else:
+                sys.stdout.write(pack)
+            return 0
+        if a.cmd == "sizes":
+            print("\n".join(sizes()))
+            return 0
+        if a.pack and len(a.roles) != 1:
+            raise Refusal("--pack checks one file, so name exactly one role")
+        bad = 0
+        for role in a.roles or list(ROLE_CONTRACT):
+            pack = _read(Path.cwd(), a.pack) if a.pack else render(role)
+            errs = check(role, pack)
+            print(f"{'ok  ' if not errs else 'FAIL'} {role}: {len(pack)} chars, "
+                  f"{len(parse(pack)[0])} blocks")
+            for e in errs:
+                print(f"     {e}")
+            bad += bool(errs)
+        return 1 if bad else 0
+    except Refusal as e:
+        print(f"role_pack: REFUSE {e}", file=sys.stderr)
+        return 2
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
