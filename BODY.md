R10-ROUND-PLAYBOOK-FINAL, **draft pass** (dispatched ahead of closure: every carry is answered from the tree at the base; a short final pass after the last after-group merges adds only what merged after this handoff). The round playbook in `dev/audit/README.md` gains the freeze's red definition (carry 29), the pre-v10.0.0 soak step in the closure sequence (carry 30), the P545 lessons and the spelling-corpus rule (carries 27, 28), and the round-11 opening items (brief intake (a) and (b), carries 32-40). Six contracts take the carried paragraphs (carries 14, 15, 16, 18), and `roster_edit.py` reads a `LOG` verdict as itself (carry 18's vocabulary half). Every policy file stays inside its `policy_lint.mjs --budgets` cap: no cap is raised; each addition is paid by cuts of prose that has a surviving copy in the tree (each named under Repair) and by correcting stale claims. Every sentence the diff removes that has no verbatim copy at the head is enumerated by command under Figures, each with its disposition; none is left without one.

**This is policy.** `CLAUDE.md`, `dev/audit/README.md` and five role contracts change, so it merges only on tvofi's approving review at its head (`CLAUDE.md`, "Where the policy is"). Carry 14's own terms apply: if the owner accepts no cut, that paragraph is closed unimplemented.

## Approval

Awaiting tvofi's approving review at the head: the diff changes `CLAUDE.md`, `dev/audit/README.md` and five role contracts, all of them policy. No budget is raised. Two questions for that review:

- Carry 29 quotes the 2026-11-01 freeze as "proves 20%" (a plan's constraints table, triage P664). The same ruling, as recorded on R10-ROUND-PLAYBOOK's carry 19 and in the README, says "more than a 10% improvement". The README keeps 10%, and `proposal-triage.md` keeps its separate over-20% bar for adding machinery. Which figure is the ruling's?
- Carry 31 (the D11 and D13 paragraphs) has no lawful payment: D13.md is at its exact cap, and the carry forbids changing any other sentence. It needs your budget-raise confirmation, or the paragraphs wait.

## Head

4e47ee583efdf8f066dfc5739a7db1131c2d2137: the repair of 9d3da28204b0683981252bff8651c19b8f89f3f7 (second `Fix review: blocked`, class evidence-cut; the first was at 11a6c579bb8e354b4f76209b1b4c472ddfee5c19). Three commits on that head, no merge: 909a36c8502a restores or relocates the sole-copy cuts, and 50089cd95b3a and this head build roster carry 44, which landed after dispatch. The merge base is still 8c10361eb1fea539dc5acb8f7442eac2810faa47, and `git merge-tree --write-tree origin/main HEAD` against `origin/main` = d9270211c088b6ede324a6be7ef1c8ed16311106 reports no conflict. Steps 2-8 of `fixer.md` were re-executed on this head (2026-11-12, `date -u`). The earlier fix commit is a75d2565170045c6ad90d94009d5bdb5fa2c2cbf.

## Repair

The class is closed by rule, not by the two cited instances. The rule is the enumerator under Figures: every sentence of a changed file's base text with no verbatim copy in any tracked file at the head. At 9d3da282 it returned 75; it returns 77 at this head (73 before carry 44's four removals), each dispositioned under Sole-copy enumeration.

Restored in this round, each the only copy in the tree at 9d3da282:

- `dev/audit/README.md`, Production share: "the rest waits for an instrument window the owner opens", verbatim, after the freeze's red definition (the verdict's first item).
- `dev/audit/README.md`, rounds 1-3: which round-2 harnesses still run "is `round2/HARNESSES.md` at `d5d8c4a`, final at that commit only" (the verdict's second item). `git cat-file -e d5d8c4a:tools/audit/round2/HARNESSES.md` exits 0; the same at `757e164` prints `fatal: path ... does not exist`.
- `dev/audit/README.md`, rounds 1-3: `d5d8c4a` is "`origin/main` at v6.3.18, on `main`'s first-parent history". The tree does not answer it by tag (`git describe --tags --exact-match d5d8c4a`: `fatal: no tag exactly matches`); `git show d5d8c4a:VERSION` prints 6.3.18.
- `dev/audit/README.md`, Production share: the 10 slots are "not a tree value" (`git grep "10 slots"` finds the README alone outside round evidence).
- `dev/audit/README.md`, round-11 list: "Context: the Lean flow pre-study, section K9 (out of the tree)", verbatim. `.github/workflows/ci.yml` names K9 but not the document.
- `CLAUDE.md`'s four-issues measurement (three refutation seats and a judge), cut under carry 14: relocated verbatim to `dev/programme/plan-2026-09-open-issues.md`, "Standing rules", where the reviewer already accepted the range-in-prose record. The cut in `CLAUDE.md` still needs the owner's acceptance (Approval).

Paid in this round with two README cuts whose content survives elsewhere:

- The layout block's first line, the file describing itself ("this file: the round playbook, the harness contract, the instruments kept live"): the README's own first paragraph says the same three things.
- "Drift mode and the `run.sh` lease are `.claude/rules/gate-scoping.md`'s; a direct `stress.py` run takes none": the pointer is `CLAUDE.md`'s rule-index row for `gate-scoping.md` and `fixer.md` step 5; the direct-run half is `.claude/skills/steward/SKILL.md` S6 ("a `stress.py` run outside `run.sh` takes" none).

Restored at 9d3da282 and unchanged here (round 1's five): the `load1` floor 1.86 (best of ten: 1.55); `thread_factor` 1.27-1.30 over four re-takes; `c398fc84`, the `d5d8c4a` rosters and "read them before re-deriving"; "says which they could not separate"; "twenty had no disposition while the check reported clean". The six payments of that round are unchanged: `preflight.sh` (`tests/closure.py`'s `INERT_EXCEPT`), `stamp.py` (`CLAUDE.md` rule 4), `rounds.py` (`dev/audit/rca/R10-RCA-FRICTION-RESIDUE.md`), `../setup-qa/` (`tests/README.md`, `tests/closure.py`), the register path and workflows (the README's rounds 1-3 section and playbook table), and `orchestrator.md`'s 500 k clause (the README's context-rotation bullet).

## Mutation proof

`roster_edit.py`'s `VERDICT_LINE_RE` with `LOG` removed from its alternation (the fix's production line), then `python3 tools/audit/seat/roster_edit.py --self-test`: `281 checks, 1 failed`, `FAIL triage gate: a LOG ruling is refused as LOG, never routed (got: )`. Restored: `281 checks, 0 failed`. Re-run at this head with the same result both ways. The prose changes have no executable predicate. Their control is `brief_lint.mjs`'s PLAYBOOK fixture: the renamed-instrument fixture is refused and the null fixture lints clean.

## Null control

At the base, `tools/policy/brief_lint.mjs` prints `PLAYBOOK ok: the renamed fixture is refused for its 7 moved instruments and the null fixture lints clean`. The head prints the same line, and the edited README lints with 0 errors. That is the unchanged-tree control the brief asks for. At the base, a `Verdict: LOG` entry reads `unreadable` (the mutant above is the base's regex), so the base cannot tell LOG from a missing verdict.

Cap null control, taken at this head: with this round's two payment cuts put back (restorations kept) and the tree otherwise the head's, `node tools/policy/policy_lint.mjs --budgets` prints `tools/audit/README.md` 317/321, 6111/6059, over its token cap; the head prints 315/321, 6056/6059. Taken at 909a36c8502a; carry 44's commit does not touch the README. The file was restored afterwards (`git status --short` empty). The six-hunk control of the previous round was taken at 9d3da282 and is not re-taken here.

## Figures

- Caps, `node tools/policy/policy_lint.mjs --budgets` (columns lines/cap, ~tokens/cap), at the head: `tools/audit/README.md` (the README's cap key, carry 25) 315/321, 6056/6059; `CLAUDE.md` 214/221, 3605/3605; `fixer.md` 315/315, 5210/5216; `orchestrator.md` 293/295, 4231/4251; `architect-planner.md` 84/85, 1261/1261; `plan-review.md` 24/24, 304/304; `proposal-triage.md` 36/36, 488/489; `D13.md` 79/79, 1149/1149; `D11.md` 99/103, 1494/1499. No cap is raised.
- Bytes, `wc -c` base -> head: README 24230 -> 24224; `dev/programme/plan-2026-09-open-issues.md` 529108 -> 529486 (the relocated sentence; no per-file cap, and the `record` aggregate reads ~7427 against 7405 + 500 before and after); `CLAUDE.md` 14401 -> 14421, where carry 14's paragraph (414 bytes) is paid by 428 bytes of cuts and carry 44's corrected row adds 6 (the token count rises by one, to the cap exactly; the cap is unchanged); `orchestrator.md` 16984 -> 16922.
- `node tools/policy/brief_lint.mjs`: 0 errors on every linted file; PLAYBOOK fixture line as quoted under Null control.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Scope, `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. It names `tests/doc_claims.py` (`ALL 343 checks PASSED`) and `tests/entities.py` (`ALL 2709 ENTITY CHECKS PASSED`, rc 0, run with `env -u BASH_ENV PYTHONPATH=tests/hastub`).
- Stale claims corrected, each checked by reading the tree. The README intro said "the three harnesses a judge still re-runs", but its own table lists four. The traps said `optimizer.py` has two `sleep(0.002)` calls; `grep -n 'sleep(0.002)' custom_components/heatpump_optimizer/optimizer.py` returns three (`_lbfgsb_restart`, `_multi_start_minimize`, the DHW-to-space seam), so the text now names them and carries no count. `architect-planner.md`'s "the 17 scored metrics" is a count the tree answers, so it now reads "the scored metrics".
- Sole-copy enumeration. Command, from the repository root, with the script below saved as `sole_copy.py` (it is not in the tree; see Friction): `python3 sole_copy.py 8c10361eb1fea539dc5acb8f7442eac2810faa47 4e47ee583efdf8f066dfc5739a7db1131c2d2137`, each `CUT` line numbered and cut to 150 characters for this body. Null control: the same command at 9d3da28204b0683981252bff8651c19b8f89f3f7 prints `SOLE-COPY: 75 of 912`, and its two extra units are the `CLAUDE.md` four-issues sentence and the K9 context sentence, both absent from this head's output because their verbatim text is back in the tree. At 909a36c8502a it prints 73; the four units added since are carry 44's removed citations (2, 60, 61, 62). (The total rose from 912 to 3478 because the plan file is now a changed file; its base sentences all survive.)
 Its last line: `SOLE-COPY: 77 of 3478 base sentence(s) in 9 changed file(s) survive nowhere in 10295 tracked file(s) at 4e47ee583efd`. The script, the full output and each unit's disposition are under Sole-copy enumeration below.

<!-- figure-block: scope-line mb=8c10361eb1fea539dc5acb8f7442eac2810faa47 head=4e47ee583efdf8f066dfc5739a7db1131c2d2137 -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->

## Sole-copy enumeration

~~~python
"""Every sentence the diff base..head removes that survives nowhere in the tree at head.

usage: sole_copy.py <base> <head> [--pair]
A sentence is a unit of a changed file's base text: blocks split on blank
lines, list items and table rows split apart, then split after . ! ? before
whitespace. Text is normalised to lower-case alphanumeric words, so wrapping,
markdown markers and punctuation never separate two copies. A unit survives
when its normalised words are a contiguous run in ANY tracked file at head.
Units under 4 words are skipped (headings, table rules).
"""
import difflib
import re
import subprocess
import sys

base, head = sys.argv[1], sys.argv[2]
pair = "--pair" in sys.argv


def git(*a):
    return subprocess.run(("git",) + a, capture_output=True, check=True).stdout


def norm(s):
    return " ".join(re.findall(r"[a-z0-9]+", s.lower()))


def units(text):
    out = []
    for block in re.split(r"\n\s*\n", text):
        block = re.sub(r"\n(?=\s*(?:[-*] |\d+\. |\|))", "\n\n", block)
        for item in block.split("\n\n"):
            item = " ".join(item.split())
            out += [u for u in re.split(r"(?<=[.!?])\s+", item) if u]
    return out


changed = [
    f for f in git("diff", "--name-only", "--diff-filter=MD", base, head).decode().split("\n") if f
]
corpus = []
for f in git("ls-tree", "-r", "--name-only", "-z", head).decode().split("\0"):
    if f:
        corpus.append(norm(git("show", f"{head}:{f}").decode("utf-8", "replace")))
tree = " \n ".join(corpus)
total = cut = 0
for f in changed:
    old = units(git("show", f"{base}:{f}").decode())
    new = units(git("show", f"{head}:{f}").decode()) if pair else []
    for u in old:
        n = norm(u)
        if len(n.split()) < 4:
            continue
        total += 1
        if f" {n} " in f" {tree} ":
            continue
        cut += 1
        print(f"CUT {f}: {u}")
        if pair and new:
            best = max(new, key=lambda v: difflib.SequenceMatcher(None, n, norm(v)).ratio())
            print(f"    ~ {best}")
print(f"SOLE-COPY: {cut} of {total} base sentence(s) in {len(changed)} changed file(s) "
      f"survive nowhere in {len(corpus)} tracked file(s) at {head[:12]}")
~~~

~~~text
 1 CLAUDE.md: `AGENTS.md`, at the root, is the entry point for a harness that auto-loads that name instead of this one (ZCode, Codex); it states no polic
 2 CLAUDE.md: | `orchestrator.md` | dispatches, merges, holds the freeze, records, stamps; turn `nudge.md`.
 3 CLAUDE.md: This rule is stated here and again in `dev/governance/roles/orchestrator.md` section 8.
 4 CLAUDE.md: That duplication is deliberate and is the owner's call: it binds every seat, so it belongs where every seat reads, and it binds the orchest
 5 dev/audit/README.md: Everything the per-dimension audit runs on, so that a finding can be re-measured by someone who was not there: the briefs each au
 6 dev/audit/README.md: The register that records what came of it is `dev/programme/register/audit-2026-09.md`; the orchestration scripts are `.claude/wo
 7 dev/audit/README.md: Almost nothing here is read by the gate.
 8 dev/audit/README.md: `tests/closure.py`'s `INERT` tuple and its `INERT_EXCEPT` record which paths under `tools/` that covers and which it does not, in
 9 dev/audit/README.md: ``` dev/audit/README.md this file: the round playbook, the harness contract, the instruments kept live dev/audit/config/ finding.
10 dev/audit/README.md: - The standing set is the triage seat (`proposal-triage.md`) plus the beat jobs `beatd.py` runs from `tools/audit/seat/beat_jobs.
11 dev/audit/README.md: A seat's work moves to a beat job, never into the orchestrator's turns, and the seat stays until its job is live and verified.
12 dev/audit/README.md: From the v10.0.0 stamp, a change to the machinery (`tools/audit/`, `tools/pr/`, `tools/plan/`, `tools/policy/`, `.github/workflow
13 dev/audit/README.md: The open-PR cap is the owner's: read it from `DEFAULT_CAPS` in `tools/plan/replan.py`.
14 dev/audit/README.md: Of it, 10 slots (a fixed count, the owner's ruling, not a tree value) are reserved for pull requests touching `custom_components/
15 dev/audit/README.md: A proposal is accepted only when its friction blocks a production merge, otherwise ruled LOG (`proposal-triage.md`).
16 dev/audit/README.md: Exemption from all three: a proposal proving more than 10% on CI time, programme completion time, right-first-time rate or token 
17 dev/audit/README.md: - An owner decision on moving the repository to an organization so the native merge queue can replace the train: a merge-queue ru
18 dev/audit/README.md: Confirm plan and visibility; weigh the HACS URL redirect, App installations, deploy key, ruleset ids and owner-keyed instruments;
19 dev/audit/README.md: - `dev/audit/rca/harness-friction/rounds.py` takes one directory argument and no `--stats` mode.
20 dev/audit/README.md: A RESULT whose `thread_factor` exceeds 1.05 is rejected and re-taken; the factor is a BLAS signal, not a tax on real threads.
21 dev/audit/README.md: A harness that deliberately runs work on a second thread (the real `ThreadPoolExecutor` the FakeHass trap below mandates) can nev
22 dev/audit/README.md: **`load1` is quoted, not gated**: the round-2 judge measured this box's ambient floor at 1.86 (best of ten retries: 1.55), so a `
23 dev/audit/README.md: What protects a timing number is a *ratio* metric and a null control under the same load in the same session.
24 dev/audit/README.md: Quote the real `load1`; do not wait for 1.5.
25 dev/audit/README.md: - `tests/setup_qa_render.mjs` writes SVGs to `../setup-qa/`, outside the repository.
26 dev/audit/README.md: - The GIL yields in `optimizer.py` are two `sleep(0.002)` calls: one between consecutive L-BFGS-B starts (`_multi_start_minimize`
27 dev/audit/README.md: Neither sits inside an iteration.
28 dev/audit/README.md: ## Running the gate on the audit box
29 dev/audit/README.md: Drift mode against the merge base, and the lease `run.sh` takes around `stress.py`, are `.claude/rules/gate-scoping.md`.
30 dev/audit/README.md: A direct `stress.py` run takes no lease.
31 dev/audit/README.md: A ratio cancels load, an absolute number does not.
32 dev/audit/README.md: The audit measures the integration with instruments that are themselves code: `tests/hastub`, the gate's checks and budgets, the 
33 dev/audit/README.md: A defect your dimension's method meets in one of those is a finding **of your dimension**, under the same bar as any other — exec
34 dev/audit/README.md: It travels the ordinary route: panel, judge, then an issue.
35 dev/audit/README.md: **Filing waits for the judge**: the seat that finds an instrument defect is using the instrument it accuses, and the judge re-mea
36 dev/audit/README.md: A verifier who cannot make the accused check fire has not refuted the finding; say which you could not separate.
37 dev/audit/README.md: `CLAUDE.md`'s order still governs — fix it, verify it independently if you cannot, file it only then — so a one-line instrument r
38 dev/audit/README.md: What this refuses is the third outcome: a report nobody carries, met again next round.
39 dev/audit/README.md: `audit-round2-evidence` harnesses disagree on the repository root: `D6/claims.py` measures the working directory, `D7/sysid_plant
40 dev/audit/README.md: **Copy a harness into the tree under test first**, say which root rule it used, and cite the SHA you ran, never the tag name: the
41 dev/audit/README.md: Which of those harnesses still run is `round2/HARNESSES.md` at `d5d8c4a`, final at that commit only.
42 dev/audit/README.md: ## Rounds 1-3 are at a tag
43 dev/audit/README.md: `tools/audit/round1/` to `round3/`, three closed rounds' write-once evidence, are reachable in full at **`d5d8c4a72fa7be7aebecc9e
44 dev/audit/README.md: Cite that SHA, never a tag:
45 dev/audit/README.md: Round 2's executable harnesses are at `audit-round2-evidence` (`757e164`).
46 dev/audit/README.md: The done rosters `wave-1b-groups.json`, `wave-2-groups.json` and `wave-3-groups.json`, with `web-phase0.js` and `triage-quiet-jud
47 dev/audit/README.md: Each was added by a fix pull request *after* its round closed, and each is an instrument someone re-runs rather than a report som
48 dev/audit/README.md: That is the whole of the rule: evidence is archived, instruments are kept.
49 dev/audit/README.md: All four drive production symbols and print `RESULT` lines under the harness contract in this file.
50 dev/audit/README.md: `j5_gil.py` must never be run on `FakeHass`, whose executor runs inline and would measure nothing.
51 dev/governance/roles/architect-planner.md: **Method:** ATAM's quality scenarios with sensitivity and tradeoff points; fitness functions; the Mikado me
52 dev/governance/roles/architect-planner.md: **Write the quality scenarios**, two or three per quality the owner's briefs name, marking the sensitivity 
53 dev/governance/roles/architect-planner.md: **Plan the moves to the programme target.** Findings first; where they fall short, add refactor groups with
54 dev/governance/roles/architect-planner.md: Never plan a move that deletes behaviour, renames to dodge a counter, splits or merges to move a count, or 
55 dev/governance/roles/architect-planner.md: **Name the risks**: sensitivity points the moves touch, seams likely to need redesign, and where the score 
56 dev/governance/roles/architect-planner.md: A round's end-to-end `score.py --diff <fork SHA> <main after the last merge>`, at frozen weights, reads **d
57 dev/governance/roles/architect-planner.md: The target binds this plan, never a single seat.
58 dev/governance/roles/architect-planner.md: A fixer and a fix reviewer still ask only whether the change is sounder (`fixer.md` step 17) and whether ev
59 dev/governance/roles/fixer.md: Wait on CI through one `seat/ci-watch.sh` or `seat/proof_watch.py` (the 60 s API floor is theirs), woken once by its ex
60 dev/governance/roles/fixer.md: **The handoff freezes the branch.** Until then, merge `origin/main` (never rebase) only when `git merge-tree --write-tr
61 dev/governance/roles/orchestrator.md: The turn is `dev/governance/roles/nudge.md`.
62 dev/governance/roles/orchestrator.md: That, or a merge-tree conflict, is the one reason to absorb `main` into a head (`nudge.md` 9).
63 dev/governance/roles/orchestrator.md: - **A range in prose is not a disposition.** `#470–#500` reads as complete and absorbs thirty-one numbers while 
64 dev/governance/roles/orchestrator.md: It binds you additionally, because you write the rosters and you decide the merge order.
65 dev/governance/roles/plan-review.md: **Check the target's conditions**: admissible end to end, the spread rule, the holdouts named, and fitness functi
66 dev/governance/roles/plan-review.md: **Check the ADRs** against the scenarios: each decision serves a named scenario, and its tradeoffs are written do
67 dev/governance/roles/plan-review.md: After two `revise` rounds the plan goes to the owner with the open points, never to a third round.
68 dev/governance/roles/proposal-triage.md: A process, tooling or instrument proposal passes this gate before building (decision 0015).
69 dev/governance/roles/proposal-triage.md: Sources: the sweep and Proposals line, seat results, verdict optimisation notes.
70 dev/governance/roles/proposal-triage.md: A countermeasure policy requires (root cause, red-check carry, finding fix) keeps its route.
71 dev/governance/roles/proposal-triage.md: **Bar:** measured benefit clearly outweighs cost: critical-path wall-clock/seat time; tokens (model x effort 
72 dev/governance/roles/proposal-triage.md: **Machinery.** A planned instrument/machinery group, or existing non-production CI lane or seat, stays only o
73 dev/governance/roles/proposal-triage.md: **A ruling**: a `## P<n>: <title>` entry in a `dev/programme/triage/` batch file: `Verdict:`, `Source:`, `Ins
74 tools/audit/seat/roster_edit.py: LABEL = r"P(?:\d+|-[A-Q])\b" PROPOSAL_RE = re.compile(rf"\b(?:triage|proposal)\s+{LABEL}", re.I) RULING_CITE_RE = re.
75 tools/audit/seat/roster_edit.py: def ruling_verdict(src, pid): """The `Verdict:` of the `## <pid>:` entry in a triage batch file: ACCEPT, REJECT or DE
76 tools/audit/seat/roster_edit.py: ruling = "dev/programme/triage/s9-batch1.md" (seed / ruling).parent.mkdir(parents=True, exist_ok=True) (seed / ruling
77 tools/audit/seat/roster_edit.py: triage: {ruling}#P4")) check("triage gate: an entry with no verdict line is refused", refuses("unreadable", "append-c
SOLE-COPY: 77 of 3478 base sentence(s) in 9 changed file(s) survive nowhere in 10295 tracked file(s) at 4e47ee583efd
~~~

Dispositions, by the number the output gives each unit. "Reworded" means the head sentence named carries every fact of the base one; anything a rewording dropped is listed separately with where it survives.

- 1: reworded in `CLAUDE.md`; "at the root" is the tree's to answer (`git ls-files AGENTS.md` prints `AGENTS.md`).
- 3, 4: reworded into one `CLAUDE.md` sentence ("stated again in ... section 8, deliberately (the owner's call: it binds every seat, the orchestrator hardest)").
- 5: reworded as the README's first paragraph. "The three harnesses" was stale (the table lists four). The briefs are `CLAUDE.md`'s dimension table; the schema is the layout block's `finding.schema.json` line.
- 6: paid at 9d3da282; the register path is in the rounds 1-3 section, the workflows in the playbook table.
- 7, 8: reworded ("Which of these paths the gate reads is `tests/closure.py`'s `INERT` and `INERT_EXCEPT` to say"); "almost nothing" and "the one file a test executes" are those two tuples' content, which the sentence forbids restating.
- 9: the layout block, one unit. Three lines cut: `preflight.sh` and `stamp.py` (paid at 9d3da282), and the self-description (paid here). The other three lines are unchanged.
- 10, 11: reworded as the standing-set bullet. Dropped and surviving: the `standing-merge.md` and `standing-dispatch.md` pointers (`CLAUDE.md`'s role table); "under the beat's state directory" (`tools/audit/seat/instruments/beat_jobs.py.md`: `S/digest/jobs/<row>`).
- 12: restored here (the instrument window). "Fixes a red on main or on one" is replaced by carry 29's definition of the red, which is the carry's ask.
- 13, 14: reworded ("Of the owner's open-PR cap (`DEFAULT_CAPS` in `tools/plan/replan.py`), 10 slots ..."); "not a tree value" restored here.
- 15, 16: reworded, one word each ("otherwise" to "else", "more than" to "over").
- 17, 18: reworded as the merge-queue bullet; every named group, the HTTP 422 and the probe are kept. The K9 context sentence after them is restored here.
- 19: paid at 9d3da282 (`R10-RCA-FRICTION-RESIDUE.md`).
- 20, 21: reworded; 1.27-1.30 kept. Dropped and surviving: why the second thread's CPU misses the ratio (`dev/audit/rounds/round4/D9/h2_cycle.py`'s header and `d9common.py`: "honest CPU lands in `process_time` and not in" `thread_time`); the real `ThreadPoolExecutor` (the README's first trap).
- 22, 23, 24: reworded; 1.86 and 1.55 kept. Dropped and surviving: the refused `load1 <= 1.5` bar (`dev/audit/rounds/round4/quiet-window.md`: "so a `load1 <= 1.5` bar is a stall").
- 25: paid at 9d3da282 (`tests/README.md`, `tests/closure.py`).
- 26: corrected, a stale count (two calls; `grep -n 'sleep(0.002)'` on `optimizer.py` returns three).
- 27: "Neither sits inside an iteration" survives in `dev/governance/dimensions/D9.md` ("not inside an iteration"); with three calls the README no longer asserts it for the third.
- 28, 29, 30: paid here (the gate-scoping pointer and the direct-run half, above).
- 31: reworded ("a timing is protected by a *ratio* metric and a null control under the same load").
- 32, 33, 34: reworded as the instrument-defect paragraph. The bar's five parts are the same file's harness contract (metric definition, `instrumented_symbol`, `perturbation`, RESULT, null control).
- 35: reworded ("filing waits for the judge, who re-measures with the accused instrument"). Dropped and surviving: the reason, in `dev/programme/plan-2026-09-open-issues.md`'s #900 row ("because the seat that finds one is using the instrument it accuses").
- 36: restored at 9d3da282.
- 37: reworded; the order itself is `CLAUDE.md`'s heading.
- 38: reworded ("not prose in a report" is the refusal; the sentence restated it).
- 39, 40: reworded ("A harness's root rule varies ...: copy it into the tree under test and say which it used"; "the tag ... moved once, so cite the SHA"). `c398fc84` and `757e164` kept.
- 41: restored here (`HARNESSES.md` at `d5d8c4a`).
- 42, 44: the heading and "Cite that SHA, never a tag", reworded ("Rounds 1-3 are at a SHA"; "so cite the SHA").
- 43: reworded; the v6.3.18 clause restored here; the register sentence kept verbatim.
- 45, 46: reworded; restored at 9d3da282.
- 47, 48: reworded into one sentence, same rule.
- 49, 50: reworded; why `j5_gil.py` never runs on `FakeHass` is the first trap ("runs the function inline ... measures nothing").
- 51, 52, 54, 55: `architect-planner.md`, reworded with no fact dropped (articles and "the round touches").
- 53: carry 16's rewrite of step 6 (the target as a floor); the findings-first rule is kept.
- 56: corrected, a count the tree answers ("the 17 scored metrics").
- 57, 58: carry 16's rewrite of the closing paragraph. "Whether every number is earned" is `fix-review.md` step 14's heading.
- 59: `fixer.md`, reworded ("woken once" to "woken", "sleeping and polling" to "polling").
- 63: "absorbs thirty-one numbers while naming eight" survives verbatim in `dev/programme/plan-2026-09-open-issues.md` (the three-sets paragraph).
- 64: reworded ("and you too: you write the rosters and order the merges").
- 65, 66, 67: `plan-review.md`, reworded; 61 also takes carry 16's `revise` clause. "Fitness functions per move" is `architect-planner.md` step 7 ("Name each move's fitness functions").
- 68, 70: `proposal-triage.md`, reworded into one sentence.
- 69: reworded into 68's parenthesis; the Proposals line is the sweep's own item 7 in `tools/audit/seat/sweep_template.md`.
- 71, 72, 73: reworded ("expected runs" to "runs"; "instrument/machinery" to "machinery"; "cite, don't carry" folded into "each figure with its command or log").
- 74, 75, 76, 77: `roster_edit.py`, code: the regex, its docstring and the self-test fixture, each changed only by the `LOG` addition (Mutation proof).
- 2: carry 44, corrected: `CLAUDE.md`'s orchestrator row now reads "Cursor turn `nudge.md`", the scope `nudge.md` states for itself ("binds the Cursor orchestrators on grok and qwen").
- 60, 61, 62: carry 44, removed on the owner's instruction: `orchestrator.md` section 0's "The turn is `dev/governance/roles/nudge.md`" and the two `nudge.md` step-9 citations (`fixer.md` step 6, `orchestrator.md` section 6). The rule those two cited stays stated in place, word for word; what `nudge.md` says is still in `dev/governance/roles/nudge.md`, which this pull request does not edit.

What the rule does not see: a fact dropped inside a reworded sentence is found by reading the unit against its head sentence, which is what the list above records; the rule guarantees only that no changed base sentence escaped that reading. Units under four words (headings, table rules) are skipped.

## Red checks

none

## Carries answered

Each carry, 0-based as dispatched, with its answer :

- Carry 0, Carry 1, Carry 2, Carry 3, Carry 4, Carry 5, Carry 6, Carry 7, Carry 8, Carry 9, Carry 10, Carry 11, Carry 12: dismissed duplicates of carries 13 to 25 in order (roster marks); each is answered under its kept twin below.
- Carry 13: decided. A decision record is named by number, never by path, so none joins `policy_lint`'s named-docs corpus, and 0015 and 0016 need no caps. The decision is written into the README's "Recorded decisions" item.
- Carry 14: built. The paragraph is in `CLAUDE.md` verbatim, after the fix-or-file rule that binds every seat. It is paid by cutting the four-issues anecdote, the `AGENTS.md` sentence and the duplication-rationale sentence (428 bytes); the token cap is unchanged and not raised. This needs the owner's acceptance of the cuts at review; otherwise it closes unimplemented, as the carry states.
- Carry 15: built. `orchestrator.md` section 9 rotates the orchestrator at a ledger-clean point near 500 k through `state_docs.py` and the resume, and points to the README for seat caps. It is paid by dropping section 9's anecdote counts and tightening section 10's preamble.
- Carry 16: built. (1) `architect-planner.md` step 6 makes the target a floor, not a cap, with cheap moves past it costed beside their dS; its closing paragraph now says a seat is never credited for dS alone. (2) `plan-review.md` step 4 sends back as `revise` a plan that stops at the floor with a cheap move left. `fixer.md` step 17's score bullet makes a production diff take sound score gains in code it touches, with the dS in `## Figures`. (3) was already stated in the README.
- Carry 17: written into the README's round-11 list (`pr_cap.py`'s production slots), because the machinery code half is not this group's seam.
- Carry 18: built. `proposal-triage.md`'s Bar and Verdicts now carry LOG, citing the README's exemption, and `roster_edit.py`'s `VERDICT_LINE_RE` reads LOG (mutation proof above).
- Carry 19: already answered at the base. `grep -n -i owed dev/programme/HANDOVER.md` lists no `pr_cap` owed entry, and the open-PR-cap bullet describes `pr_cap.py` as it is. The exemption is `pr_cap.py`'s module docstring ruling: "opening or updating a pull request for an owed handoff is never refused by it".
- Carry 20: still true at the base. `beat_jobs.py`'s `ROWS` has no dispatch or relay row, so the README keeps "has no row and stays". The final pass re-checks this, and carry 32's retirement item is now on the round-11 list.
- Carry 21: answered by rule. The README states no record-merge figure. The baseline belongs to the 2026-10-24 rule quoted in R10-ROUND-PLAYBOOK's own body, so this draft carries no number.
- Carry 22: still true at the head. The R10-ROUND-PLAYBOOK items stay in the README's round-11 list and production-share paragraph, and the closure sentence is unchanged and verbatim.
- Carry 23: already fixed at the base. `review_packet.py`'s `unnamed_carries` counts 0-based (`range(carries)`) and states that `cloud_dispatch.py` renders from 0.
- Carry 24: already answered at the base. The README's last round-11 item states the one invocation; kept.
- Carry 25: written into the README's round-11 list: re-key the moved files' `policy_budgets.json` caps at their new paths, as a re-key the raise gate reads as no raise. It was not done here because 50 keys still sit under `tools/audit/` (`grep -c '"tools/audit/' dev/governance/config/policy_budgets.json`), and re-keying one alone would split the convention.
- Carry 26: written into the README's round-11 list by pointer to this roster carry (D15's drawn-power gain). Its text stays verbatim on the roster, because restating 350 words in full does not fit the README's cap.
- Carry 27: written into the README as the "Lessons" paragraph after the phase table (all four).
- Carry 28: written. The Lessons paragraph cites `fixer.md` step 2 for the spelling-corpus rule; phase 7's contract column already names `fixer.md`.
- Carry 29: written. Production share now says the machinery is frozen. "Fixes a red" means the required `gate` job's red on main (`tools/ci/gate.py`) or a self-test red the pull request introduces, never one inherited from main. Each round-11 machinery group names its ground. Policy wording: it binds only on tvofi's approving review. See Approval for 10% versus 20%.
- Carry 30: written. The closure sentence is followed by the soak step: the patch release, tvofi's own install, and the card's tabs opened before v10.0.0, never without.
- Carry 31: not landed. It stays open as this group's own roster carry 31, for the final pass. `dev/governance/dimensions/D13.md` is at its exact cap (79/79 lines, 1149/1149 tokens), and the carry forbids changing any other sentence, so no payment exists. D11.md has 5 tokens of headroom. The scorecard has not landed, because R10-TICK-RESIDUE-P3 is deferred to round 11 (carry 33). Both paragraphs need the owner's budget-raise confirmation, which this seat may not presume. The README's deferred-groups item reopens the scorecard group.
- Carry 32: written into the round-11 list (seat retirement, its precondition, the s14 load, size L, design first).
- Carry 33: written. Every round-10 group at stage deferred reopens as written, and the re-homes to the groups owning `merge_train.py`, `tools/pr/cancel_superseded.py` and `tests/entities.py` are named with their triage batches.
- Carry 34: written through the same deferred-groups item; R10-DISINFECTION-STEP-NOTICE is at stage deferred.
- Carry 35: written into the round-11 list by pointer (the stubs bump).
- Carry 36, Carry 37 and Carry 38: written into the round-11 list by pointer (R10-CI-PRIORITY-PAUSE's three).
- Carry 39: written into the round-11 list by pointer (the boost settling tail).
- Carry 40 (appended after dispatch): written into the round-11 list by pointer (R10-PREPR-RESIDUE's seven).
- Brief intake (a) and (b): the round-11 list names R10-PROTECTION-CENSUS's rows as the intake baseline (the census is in progress at this draft; the final pass adds its result) and B1 as conditional on it, unless the owner orders it into round 10.
- The `CLAUDE.md` index row for `dev/audit/README.md` is unchanged, because the README's role did not change.
- Carry 41: written into the README's round-11 list beside carries 35 to 40: R10-PREPR-DARWIN-SELFTEST-LANE is un-deferred with the widened macOS-leg brief, as written on the roster (round 10 only if the owner approves the runner spend and the replan shows closure does not move).
- Carry 42: answered by this group's final pass, which the opening paragraph already scopes to what merged after this handoff. Before the v10.0.0 stamp, that pass re-reads the merged diff of each of the eleven named groups that merged after this group, folds in what changed, and records the groups, merge SHAs and what was folded (or nothing) in `dev/programme/HANDOVER.md`. Nothing is owed at this head: the re-read is keyed to merges that follow this group's own.
- Carry 43: superseded by carry 44, which says so; answered there.
- Carry 44: built, with one departure the tree forced. (1) `orchestrator.md` section 0 loses "The turn is `dev/governance/roles/nudge.md`". `CLAUDE.md`'s orchestrator row could not lose the name: with the clause deleted (head 50089cd95b3a), `node tools/policy/policy_lint.mjs` printed `ERROR [index] CLAUDE.md: does not name tools/audit/briefs/nudge.md. The index is the only way a seat finds a policy file; an unnamed one binds nobody`, and `tests/entities.py` exited 1 on it. The row therefore reads "Cursor turn `nudge.md`", which corrects the reference to the scope `nudge.md`'s own first paragraph states, as the owner's sentence allows ("correct any references to that script or remove it entirely"); at this head `policy_lint.mjs` prints `TOTAL: 0 error(s) across 51 policy file(s)`. R10-NUDGE-RETIRE removes the row with the file. (2) `orchestrator.md` section 6 and `fixer.md` step 6 already state the rule in place (a `DIRTY` head or a `git merge-tree` conflict is the one reason to absorb `main`), so only the citation goes. (3) `nudge.md`, `gate-scoping.md` and `sweep_template.md` are untouched. No cap is raised; `CLAUDE.md` rises one token to its cap, the other two fall (Figures). The carry's enumerator, `git grep -n nudge -- CLAUDE.md AGENTS.md dev/governance/roles`, lines cut to 160 characters, before (909a36c8502a; the merge base prints the same six, `CLAUDE.md`'s at line 114):

~~~text
CLAUDE.md:113:| `orchestrator.md` | dispatches, merges, holds the freeze, records, stamps; turn `nudge.md`. |
dev/governance/roles/fixer.md:105:   conflict or the head is `DIRTY` (`nudge.md` step 9). A delta re-applied to
dev/governance/roles/nudge.md:1:# The orchestrator nudge
dev/governance/roles/nudge.md:81:If a push or an open is refused and no fixer is working on that group, dispatch a fixer this turn. Do not leave the refusal for
dev/governance/roles/orchestrator.md:19:The turn is `dev/governance/roles/nudge.md`.
dev/governance/roles/orchestrator.md:165:one reason to absorb `main` into a head (`nudge.md` 9).
~~~

  and after, at this head: `CLAUDE.md`'s corrected row and `nudge.md`'s own two lines:

~~~text
CLAUDE.md:113:| `orchestrator.md` | dispatches, merges, holds the freeze, records, stamps; Cursor turn `nudge.md` |
dev/governance/roles/nudge.md:1:# The orchestrator nudge
dev/governance/roles/nudge.md:81:If a push or an open is refused and no fixer is working on that group, dispatch a fixer this turn. Do not leave the refusal for
~~~

  Outside the carry's enumerator: `tools/audit/seat/roster_edit.py`, which this pull request edits, names `nudge.md` once, in a comment recounting who runs two callables by hand. It is left as written, since it is true until R10-NUDGE-RETIRE removes the file, and carry 44's three items do not list it. `dev/audit/README.md` names `nudge.md` nowhere (`git grep -n nudge -- dev/audit/README.md` prints nothing, rc 1).

## Forward-carry

none

## Friction

- writing-for-agents: unenforced: "cutting evidence is never compliance" has no in-tree enumerator of sole-copy cuts, so two review rounds of this pull request found them by reading; the enumerator used here is printed in full under Figures and adds no file to this repair. Carry: dismissed: the command is in this body in full; building it as a seat instrument is a machinery proposal for triage, not a finding of this group
