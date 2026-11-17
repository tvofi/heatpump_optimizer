# Review packet #3684
head: d401f1498734d5c8633b74b28b0948d9da27a4b7
base: 5e2ef89b4e7348b190aa917dc032da73ba04998e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=134170870106 success
arch-score / arch-score id=134195321234 success
arm id=134170269407 skipped
budget-raise-gate / budget-raise-gate id=134195322267 success
cancel-superseded id=134195318677 success
codeql id=134195411292 skipped
codeql / Analyze (actions) id=134170731194 success
codeql / Analyze (javascript-typescript) id=134170731469 success
codeql / Analyze (python) id=134170731218 success
gate id=134195320621 success
governance id=134195320607 skipped
governance / env-matrix id=134170731164 success
governance / instrument-self-tests id=134170731022 success
governance / policy-docs id=134170730794 success
governance / record id=134170734558 skipped
governance / wave-script id=134170731109 success
hassfest id=134195320515 skipped
hassfest / hassfest id=134170730705 success
kernel-points id=134195427154 skipped
pr-contract id=134195322416 skipped
pr-contract / pr-contract id=134193605837 success
prelude id=134195320332 success
refresh id=134195379913 success
sweep-self id=134195937768 skipped
tests id=134195320672 skipped
tests / arch-instrument id=134171306353 success
tests / briefs id=134170730607 success
tests / browser id=134171306525 success
tests / ci-ratchet id=134193602881 skipped
tests / claims-autofix id=134178619116 skipped
tests / closure-scope id=134170731275 success
tests / closures id=134171306351 success
tests / closures-autofix id=134193603279 skipped
tests / coverage id=134171306626 success
tests / coverage-ratchet id=134181647884 success
tests / fast (3.14) id=134171306355 success
tests / graders-head-copy id=134181647763 success
tests / lane-proofs id=134181648516 success
tests / mutation id=134170731416 success
tests / mutation-autofix id=134171337430 skipped
tests / mutation-pins id=134171337327 skipped
tests / nightly-ha id=134171308369 skipped
tests / nightly-status id=134170730690 failure
tests / replay id=134171309979 skipped
tests / typing id=134171306312 success
validate id=134195397771 skipped
validate / validate-hacs id=134170730597 success

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

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/audit/harnesses/r11_selftest_static_edge.py b/dev/audit/harnesses/r11_selftest_static_edge.py
new file mode 100644
index 0000000000..97bf018176
--- /dev/null
+++ b/dev/audit/harnesses/r11_selftest_static_edge.py
@@ -0,0 +1,76 @@
+#!/usr/bin/env python3
+"""R11-RCA-SELFTEST-TABLE-DRIFT harness, the rejected countermeasure: one-hop static detector of new reads by gated self-test steps.
+
+    python3 dev/audit/harnesses/r11_selftest_static_edge.py REPO BASE HEAD [--table-ref REF]
+
+For each gated step's committed entry (table at --table-ref, default HEAD), every
+file the diff BASE..HEAD changes that the entry already reads is scanned at BASE
+and HEAD for references to tracked paths (literal path strings, a bare file name
+resolved beside the file, Python imports); a reference new at HEAD that the entry
+does not name (files, dirs, probes) is printed: STEP KIND PATH VIA.
+"""
+import json, os, re, subprocess, sys
+
+repo, base, head = sys.argv[1:4]
+tref = sys.argv[sys.argv.index("--table-ref") + 1] if "--table-ref" in sys.argv else head
+
+
+def git(*a):
+    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout
+
+
+def show(ref, path):
+    r = subprocess.run(["git", "-C", repo, "show", f"{ref}:{path}"], capture_output=True)
+    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None
+
+
+tracked = set(git("ls-tree", "-r", "--name-only", head).split("\n")) - {""}
+dirs = set()
+for p in tracked:
+    d = os.path.dirname(p)
+    while d:
+        dirs.add(d)
+        d = os.path.dirname(d)
+TOK = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./-]*")
+IMP = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import\s+([\w, ]+)|import\s+([\w., ]+))", re.M)
+
+
+def refs(path, text):
+    out = set()
+    here = os.path.dirname(path)
+    for t in TOK.findall(text):
+        t = t.rstrip("/.")
+        if t.startswith("./"):
+            t = t[2:]
+        for c in (t, os.path.normpath(os.path.join(here, t)) if "/" not in t or t.startswith("..") else None):
+            if c and c != path and (c in tracked or (c in dirs and "/" in c)):
+                out.add(c)
+    if path.endswith(".py"):
+        for m in IMP.finditer(text):
+            mods = [m.group(1)] if m.group(1) else [x.strip().split(" ")[0] for x in m.group(3).split(",")]
+            if m.group(1):
+                mods += [m.group(1) + "." + x.strip().split(" ")[0] for x in m.group(2).split(",")]
+            for mod in mods:
+                rel = mod.replace(".", "/")
+                for c in (rel + ".py", rel + "/__init__.py", os.path.join(here, rel + ".py")):
+                    if c in tracked and c != path:
+                        out.add(c)
+    return out
+
+
+table = json.loads(show(tref, "tools/ci/selftest_closures.json"))["steps"]
+changed = [l.split("\t") for l in git("diff", "--name-status", "--no-renames", base, head).splitlines()]
+changed = {p for s, p in changed if s != "D"}
+cache = {}
+n = 0
+for sid, e in sorted(table.items()):
+    known = set(e.get("files", [])) | set(e.get("dirs", [])) | set(e.get("probes", []))
+    for f in sorted(changed & set(e.get("files", []))):
+        if f not in cache:
+            h, b = show(head, f), show(base, f)
+            cache[f] = refs(f, h or "") - refs(f, b or "")
+        for r in sorted(cache[f] - known):
+            kind = "dirs" if r in dirs and r not in tracked else "files"
+            print(sid, kind, r, "via", f)
+            n += 1
+print(f"# {n} flagged, {len(changed)} changed files", file=sys.stderr)
diff --git a/dev/audit/rca/R11-RCA-SELFTEST-TABLE-DRIFT.md b/dev/audit/rca/R11-RCA-SELFTEST-TABLE-DRIFT.md
new file mode 100644
index 0000000000..90e64bb5ca
--- /dev/null
+++ b/dev/audit/rca/R11-RCA-SELFTEST-TABLE-DRIFT.md
@@ -0,0 +1,242 @@
+# R11-RCA-SELFTEST-TABLE-DRIFT: main's self-test read-set table lags the merges that add reads
+
+Root-cause seat beside R11-HOTFIX-MAIN-SELFTEST-DRIFT (`handoff/r11-hotfix-main-selftest-drift`,
+code `142926ec66`). It runs beside that fix and lands no code. Measured at `origin/main`
+`6f422812d5` on 2026-11-16. It extends `R10-RCA-FAMILY-SELFTEST-SCOPE-DRIFT.md` (the round-10
+family record) with round 11's instances. It also judges the PR-time detector the hotfix body
+proposes.
+
+## 1. The defect, reproduced
+
+Push run 43884631892 at `e352724335` (merge of #3645): `governance / instrument-self-tests`,
+step "Refuse a self-test read set the committed table misses", 27 `UNDER-SCOPED` refusals.
+Reproduced off-Linux from that run's `selftest-closures` artifact: `selftest_scope.drift(table
+at e352724335, artifact steps, job_steps(governance.yml at e352724335))` returns 27 refusals.
+Against the artifact itself it returns 0, and against `142926ec66`'s table it also returns 0.
+The added reads are 67 (step, kind, path) triples: 45 `files`, 13 `dirs`, 9 `probes`.
+
+**The reported attribution is partly wrong.** The hotfix body names #3644, #3625 and #3651.
+To check it, I took each read path the window added and found the first-parent merge that
+added it (`git log --first-parent --diff-filter=A 82e301585d..e352724335 -- PATH`):
+
+| merge | reads of paths it added |
+|---|---|
+| #3622 (`tools/audit/seat/plan_phases.py`, `dev/programme/round11/`) | 14 |
+| #3644 (`round_metrics.py`, `round_metrics_selftest.py`) | 8 |
+| #3625 (`tools/audit/enumerate.py`) | 7 |
+| #3640 (`tests/mutation_ledger/*/slab_seed.py`) | 6 |
+| #3627 (`dev/governance/config/machinery_target_budgets.json`) | 3 |
+| #3641 (`dev/governance/dimensions/criteria/`) | 2 |
+
+That accounts for 40 of the 67 reads. The other 27 are reads of older files, most of them in
+`plan-page` (8) and `orchestrator-tick` (8). #3651 added none of the read paths.
+
+The race in one example: #3652, the previous re-record, measured at `82e301585d`. #3622 merged
+at 04:16:31Z and #3652 at 04:20:42Z. So the largest group of reads in this instance landed four
+minutes before the hotfix meant to clear main's red.
+
+## 2. Named cause
+
+The table is measured only on a push to main. The drift step's `if:` reads
+`env.SELFTEST_TRACE != ''`, and `SELFTEST_TRACE` is set only when `github.event_name ==
+'push'` (`governance.yml` lines 313 and 1592). So no pull request can see that its merge adds a
+read. The repair is a hand re-record, as a hotfix pull request, measured at one main SHA. It
+merges 1 to 2.5 hours later, and in that time main merges about 1.6 pull requests an hour
+(77 first-parent merges from 2026-11-14T15:40Z to 2026-11-16T15:44Z). The hotfix therefore
+almost never catches up:
+
+- Over the 80 `ci.yml` push runs on main from 2026-11-14T14:59Z to 2026-11-16T15:50Z, the drift
+  step concluded 55 times. It failed 54 times and succeeded once, at `dd62a612a2` (#3606's own
+  merge). The run after it was red again. Source: the jobs API for each run, step "Refuse a
+  self-test read set the committed table misses".
+- The re-record merges #3629 and #3652 were red at their own merge commits (`f7ead6bb1f` and
+  `5aaf9c112f`).
+
+Every round-11 instance so far is a pull request that adds a file or an edge some gated step
+reads, merging after the last measurement. Some of those pull requests re-recorded their own new
+steps (#3644, #3625 and #3651 each touched the table); none re-measures the other steps.
+
+## 3. Process state: (c)
+
+**The process existed and was followed:**
+- The drift check ran on every push that reached it and refused 54 of its 55 conclusions.
+- A re-record hotfix was dispatched six times in 48 hours: #3589, #3595, #3606, #3629 and
+  #3652 were reviewed and merged, and `142926ec66` is handed off.
+
+**It did not produce the intended result.** The intent was a green main and a table that scopes
+pull requests correctly. Main got one green drift run in 55. The unit is wrong: a hand repair
+measured at one SHA cannot outrun a merge rate higher than its own turnaround.
+
+Why the other states do not fit:
+- **Not (a):** a check exists.
+- **Not (b):** no step was skipped.
+- **Not (d):** the table has lagged additions since #3315 introduced it. Nothing changed
+  underneath it.
+
+**Why the existing barriers do not reach these instances:**
+- `R10-SELFTEST-TABLE-SHRINK`'s barrier is the `union_record` that #3551 landed. It stops a
+  re-record from *dropping* reads. These instances *add* reads.
+- `R10-SELFTEST-RED-INTRODUCED`'s barrier, `merge_train.py introduced`, compares a pull
+  request's self-test steps at its head and at the merge base. The drift step does not run on a
+  pull request, so it is red at neither end.
+
+This agrees with the family record's state (c). Round 11 adds the measurement that the hotfix
+unit leaves main red even when it is followed promptly.
+
+## 4. Class reach
+
+- **The same class:** 13 hotfix re-records to date. That is the family record's ten (#3375 to
+  #3606), plus #3629, #3652 and `142926ec66`.
+- **The same shape elsewhere:** a measured file that is repaired by hand inside pull requests
+  while main measures it. The family record and loop card L9 name four such files:
+  - `tests/closures.json`, which `closures-autofix` already repairs on the pull request in CI;
+  - the figure blocks;
+  - the brief line pins;
+  - the claim files' stamp line.
+
+  This search found no fifth.
+- **Not yet in `dev/audit/config/bugclasses.json`.** The nearest class is
+  `R10-SELFTEST-TABLE-SHRINK`, which covers drops, not additions. Adding the class belongs to the
+  countermeasure's group, below.
+
+## 5. The detectors judged, measured over this instance's window
+
+The window is the 15 first-parent merges from `5aaf9c112f` (#3652) to `e352724335`. The truth
+set is the 67 reads `142926ec66` adds.
+
+**C1, the hotfix body's proposal: a static PR-time detector "like step 6d".** I built it as
+`dev/audit/harnesses/r11_selftest_static_edge.py`. For each gated step, it scans the files the
+diff changes that the step already reads, at the base and at the head, for:
+- literal tracked paths;
+- bare file names beside the file;
+- Python imports.
+
+It flags each new reference the step's entry lacks. I ran it per merge, against each merge's own
+table:
+
+| measure | result |
+|---|---|
+| reads caught | 14 of 67 (21%) |
+| flags raised | 333 unique flags (412 per-merge lines) |
+| precision | 14 of 333 (4%) |
+| flags per merge | about 22 per merge on average, up to 119 at #3641 |
+
+A second static rule flags a file the diff adds under a directory the step lists. It caught 8 of
+the 45 file reads with 384 flags.
+
+Static analysis misses because most new reads are not import edges from a changed file. They
+are:
+- a step listing a directory and reading what it finds (`dirs` and `probes`, 22 of the 67, which
+  include git's `config`, `objects` and `refs` probes);
+- a data-driven read through a list held elsewhere, such as `tests/closure.py`'s INERT entries;
+- a new file opened by a tool that walks the tree.
+
+With C1, 53 reads would still have reached main: main stays red and the hotfix is still owed.
+The detector avoids no instance and costs a seat about 22 false lines a merge to read. **It
+fails the cost test.**
+
+Step 6d is not static either. `tests/closures.json` closures are recorded dynamically:
+- Python lanes run under `sys.addaudithook`;
+- the inert dimension runs under strace on Linux.
+
+The faithful analogue is a traced run, priced as C3 and C4.
+
+**C2, a Darwin approximation.** Darwin has no strace. `selftest_scope precheck`, built on
+`fix/r11-pre-shared-files`, returns rc 3 (skip) there. An audit-hook tracer would see Python
+processes only. Not measured. At least the 9 git and directory probes in the truth set come from
+non-Python processes, so the most it could reach is 58 of 67. **Not recommended:** it would be
+a second, weaker recorder beside the strace one.
+
+**C3, `precheck` as built on `fix/r11-pre-shared-files` (`fe138c567b`).** It traces, on Linux
+in a scratch clone, only the gated steps whose own command-named script the diff changes. I ran
+its `touched_steps` per merge over the window:
+- it selects 6 of the 20 drifting steps;
+- those 6 steps hold 22 of the 67 reads (33%). That is an upper bound, because a touched step is
+  not always touched by the merge that added its read.
+
+Tracing every step whose recorded files the diff changes was its builder's first cut: 17 steps
+and 43 minutes for one diff. It was dropped on cost. **No change recommended to the build.** It
+would not have prevented this instance.
+
+**C4, tracing the selected steps in pull-request CI on Linux.** This is exact.
+
+Its cost, measured as `instrument-self-tests` job wall time:
+- untraced on a pull request: 18.9 to 23.8 minutes for 51 to 130 steps (six concluded runs on
+  2026-11-16);
+- traced on a push: 38.5 to 71.7 minutes over main's last 12 concluded push runs.
+
+So about +35 minutes per FULL pull-request job, over the 30-minute pull-request cap. The pull
+requests that drift (adding files under `tools/`) are exactly the ones that run FULL. The fix
+would also have to commit the table inside the pull request, which is a gate file. That is the
+hand-edit L9 directs away from. **It fails the cost test** (77 merges × ≥35 runner-minutes in
+the window, against six hotfixes), and the owner has ruled out CI widening.
+
+## 6. Cost test
+
+    cost(countermeasure, recurring) < cost(defect) x P(recurrence)
+
+**cost(defect), per instance:**
+- one hotfix pull request, open for 62, 64, 105, 129 and 152 minutes (#3589, #3595, #3606,
+  #3629, #3652; median 105), created to merged;
+- one fixer and one reviewer each;
+- one FULL CI run, because the table is a gate file;
+- the job left red on main. This hides any other step's red at job level, as #3629 found its
+  60-minute-cap cause inside it.
+
+**P(recurrence), measured:** 6 instances in 48 hours (2026-11-14T15:40Z to 2026-11-16T15:44Z), about 1 per 13 merges. That is up from the
+family record's 1 per 25. A hotfix also clears main's red in only 1 of 6 instances, so on
+present form the defect does not end.
+
+| option | standing cost | instances avoided | verdict |
+|---|---|---|---|
+| C1 static detector | about 22 false flags per merge | 0 of 1 in the window (21% recall) | fails |
+| C2 Darwin audit hook | a second recorder; recall not measured, at most 58 of 67 | not measured | not recommended |
+| C3 `precheck` (built) | already paid by its group | 0 of 1 (at most 33% recall) | keep as built |
+| C4 PR-time CI trace | about +35 min per FULL PR job, over the cap | all PR-made | fails |
+| C5 main-side absorb bot | zero on a green push; one bot commit per red push batch; no seat | every hotfix seat | **passes** |
+| C6 batch absorb, interim | one artifact data commit per record batch | at one batch a day, 4 of 6 hotfix pull requests (estimate) | **passes** |
+
+**C5** is countermeasure A's unbuilt half: P748 part 1, which the R11-PRE-SHARED-FILES fix
+body records as "not built", with placement D1/D2 still the owner's decision. Its standing cost
+on a green push is zero. It removes the fixer, the reviewer and the FULL CI run from every
+instance. It closes the race only if it keeps **one standing pull request**: every red push
+unions its artifact into it (`absorb --from`), and that pull request merges on the next train.
+A new pull request per measurement would race exactly as the hotfixes do.
+
+**C6** needs no tooling and is legal under the round-11 freeze. The drift red is a non-required
+red that every pull request inherits (owner ruling 2026-11-07: only owed reds block). So:
+- stop dispatching a hotfix per red;
+- once per record batch, commit main's latest push run's `selftest-closures` artifact as
+  `tools/ci/selftest_closures.json`. This is what `142926ec66` did, and the docstring's own
+  repair.
+
+Its residual cost: while the table lags, a pull request that edits a newly read file does not run
+the step that reads it. A break there is caught on main's FULL push run, one merge late. That
+is CLAUDE.md rule 1's stated design for a wrong closure, and the same exposure every lag window
+already has.
+
+## 7. Countermeasure
+
+- **Recommended: C5**, as proposal P-R11-41 in the round-11 proposals file, with C6 as its
+  interim until it lands. C5 addresses the state-(c) unit: the repair moves off hand-made
+  pull requests onto main's own measurement, with one standing pull request so it cannot fall
+  behind.
+- **Refused, with the numbers above:** C1 (the hotfix body's static detector), C2 and C4.
+- **C3** stays as its group built it.
+- **Owed by C5's group:**
+  - the `bugclasses.json` entry for this class (additions, as against `R10-SELFTEST-TABLE-SHRINK`),
+    citing this file;
+  - the demonstration the family record states: the job red on a planted unrecorded read and
+    green after the bot commit, and, as the null control, a green push that writes nothing.
+
+## Reproduction
+
+    W=<checkout at origin/main>
+    gh run download 43884631892 -n selftest-closures -D art
+    python3 -c 'import sys,json; sys.path.insert(0,"tools/ci"); import selftest_scope as s, subprocess as p
+    g=lambda r,f: p.check_output(["git","show",f"{r}:{f}"]).decode()
+    a=json.load(open("art/selftest_closures.json"))["steps"]; st=s.job_steps(g("e352724335",s.WORKFLOW))
+    print(len(s.drift(json.loads(g("e352724335",s.TABLE)),a,st)[0]), len(s.drift(json.loads(g("142926ec66",s.TABLE)),a,st)[0]))'
+    # 27 0
+    for m in $(git rev-list --first-parent 5aaf9c112f..e352724335); do
+      python3 dev/audit/harnesses/r11_selftest_static_edge.py . $m^1 $m; done   # C1's flags
diff --git a/dev/programme/delivery/3684.md b/dev/programme/delivery/3684.md
new file mode 100644
index 0000000000..671927e4c1
--- /dev/null
+++ b/dev/programme/delivery/3684.md
@@ -0,0 +1 @@
+- [#3684](https://github.com/tvofi/heatpump_optimizer/pull/3684) — **open**, R11-RCA-SELFTEST-TABLE-DRIFT: r11 rca selftest table drift (R11-RCA-SELFTEST-TABLE-DRIFT)
diff --git a/tests/closures.json b/tests/closures.json
index f2955a75cc..db7b8fbdd0 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4584,6 +4584,7 @@
    "dev/audit/harnesses/r11_owner_criteria.py",
    "dev/audit/harnesses/r11_plan_page_inventory.py",
    "dev/audit/harnesses/r11_relay_3358_skip.py",
+   "dev/audit/harnesses/r11_selftest_static_edge.py",
    "dev/audit/harnesses/r11_toolchain_mutants.py",
    "dev/audit/harnesses/r9_ci2b_closures_merge.py",
    "dev/audit/harnesses/r9_dbg2_selftest_price.py",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
