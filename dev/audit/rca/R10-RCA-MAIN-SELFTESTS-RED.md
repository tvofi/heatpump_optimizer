# R10-RCA-MAIN-SELFTESTS-RED: main's instrument-self-tests stayed red from #3315 on

This is the root-cause seat for the defect R10-HOTFIX-MAIN-SELFTESTS fixes. It
follows `dev/governance/roles/root-cause.md` and
`dev/governance/rules/defect-root-cause.md`, ran beside that hotfix and never
inside it, and edits no production code. Measured at `origin/main` `0362916ac`
(2026-11-10, after the push run of `57091a694` concluded); every figure was
re-derived at 2026-11-10T08:42Z (`date -u`) by the command printed beside it.
Run and job figures are `gh api` reads with `A=repos/tvofi/heatpump_optimizer`;
the local reproductions run in detached worktrees at the commit named.

## 1. The defect

`governance / instrument-self-tests` concluded `success` on no push to `main`
from #3315's merge (`ba6fd7e8b`, `gh api $A/pulls/3315 --jq .merged_at` =
2026-11-09T08:16:10Z) to `57091a694` (its push run 42758119155,
`gh api $A/actions/runs/42758119155 --jq .created_at` = 2026-11-10T04:47:59Z).
Over that span `main` took 36 commits after `ba6fd7e8b`
(`git log --first-parent --format=%h ba6fd7e8b..0362916ac | wc -l`), so 37
pushes counting #3315's own
(`git rev-list --first-parent --count ba6fd7e8b^..0362916ac`).

Enumerator E1, one row per first-parent commit: the commit, its latest
`ci.yml` push run, and that run's `governance / instrument-self-tests` job id
and conclusion.

    for c in $(git rev-list --first-parent --reverse ba6fd7e8b^..0362916ac); do
      r=$(gh api "$A/actions/workflows/ci.yml/runs?branch=main&event=push&head_sha=$c" \
            --jq '[.workflow_runs[]]|sort_by(.id)|last|.id')
      j=$(gh api "$A/actions/runs/$r/jobs?filter=latest&per_page=100" --paginate \
            --jq '.jobs[]|select(.name=="governance / instrument-self-tests")|"\(.id)\t\(.conclusion)"')
      printf '%s\t%s\t%s\n' "${c:0:9}" "$r" "$j"; done > pushes.tsv

It prints 37 rows (`wc -l < pushes.tsv`) and no `success`
(`cut -f4 pushes.tsv | grep -c success` = 0). The 37 pushes fall into three
phases and a tail, each phase a row range of `pushes.tsv`; its length is
`git rev-list --first-parent --count <first>^..<last>`. Enumerator E2, a row's
summary line and refusal kinds, from its job log:

    gh api $A/actions/jobs/<job>/logs > j.log
    grep -o 'selftest_scope check: .*' j.log
    grep -oE 'Z   [A-Z][A-Z-]+ step [^ :]+' j.log | awk '{print $2}' | sort | uniq -c

A step-level read of a job is
`gh api $A/actions/jobs/<job> --jq '.steps[]|"\(.conclusion) \(.name)"'`.
The baseline before #3315, `0a8033305` (`git rev-parse ba6fd7e8b^1`; run
42573791732), concluded `success`.

| phase | pushes | conclusion | what the log shows |
|---|---|---|---|
| P1: #3315 `ba6fd7e8b` to `3aac11dfb`, rows 1-28 | 28 (`git rev-list --first-parent --count ba6fd7e8b^..3aac11dfb`) | 24 `cancelled` (timeout at 60 min, or by hand), 4 `failure` (`sed -n 1,28p pushes.tsv \| cut -f4 \| sort \| uniq -c`) | "Install strace for the read-set measurement" concluded `failure` in all 28 jobs (step-level read), its log line `sudo: The "no new privileges" flag is set, which prevents sudo from running as root.`; five "Show ..." waiter steps fail on `.../bg/lib.sh: No such file or directory`; all 24 cancelled jobs stop in "Refuse a self-test read set the committed table misses" (step-level read, the step whose conclusion is `cancelled`) before it prints. The 4 that concluded (`6d660061d`, `72a2acee5`, `53f4a051b`, `b8f67a775`) print, by E2, `106 gated step(s), 39 refusal(s)` (the first three: 33 `UNMEASURED`, 6 `UNDER-SCOPED`) and `108 gated step(s), 47 refusal(s)` (`b8f67a775`: 34 `UNMEASURED`, 13 `UNDER-SCOPED`) |
| P2: #3375 `2cf0f129b` to `5ab6030d7`, rows 29-33 | 5 (`git rev-list --first-parent --count 2cf0f129b^..5ab6030d7`) | 5 `failure` | only "Refuse a self-test read set the committed table misses": by E2, `109 gated step(s), 37 refusal(s)` (3 runs), then `38` (2 runs, from `b07627250`, which adds a `sweep-template` line), all `UNDER-SCOPED`, `push-names-the-host` among them |
| P3: #3361 `8652aa65c`, `57091a694`, rows 34-35 | 2 (`git rev-list --first-parent --count 8652aa65c^..57091a694`) | 2 `failure` | adds "Show the self-test scope ... refusing its own fixtures" (`FAIL the live job parses (118 steps) and its gating is consistent`), "Show the self-test scope refusing each mutant of its trace rules" (`BASELINE RED: the unmutated self-test fails`; `grep -c` of each quoted line is 1 in both P3 logs and 0 in P2's first and last), and an `UNGATED step 'Show the workflow read runner refusing its own fixtures'` line in the drift step; by E2, 39 refusals (38 `UNDER-SCOPED`, 1 `UNGATED`) then 38 (37 and 1) |

So 28 + 5 + 2 = 35 pushes fall in the three phases. The tail, rows 36-37
(`e3295ba46`, `0362916ac`), was still in progress at this seat's first read;
both have since concluded `failure` (E1), with 39 and 46 refusals (E2). This
seat analyses no log of the tail.
Phase P1's refusal count is not a measurement of drift: with strace absent
the steps ran untraced, and the check reads the missing traces as
`UNMEASURED`. P2 is the first phase whose figure measures drift.

No job log of the 37 holds `exists on disk, but not in` or a
`ref_privacy: REFUSE` line
(`cat *.log | grep -cE 'exists on disk, but not in|ref_privacy: REFUSE'` = 0
over the 37 E2 logs; null control: the same logs hold 8
`ref_privacy self-test:` lines, so `ref_privacy`'s output does reach them).
Cause 2b below never failed as an error; it showed only as a drift refusal of
step `push-names-the-host`
(`grep -cE 'Z   [A-Z-]+ step push-names-the-host' j.log`: 1 in every concluded
P1, P2 and tail log and at `8652aa65c`, 0 at `57091a694`; this seat did not
establish why it is absent there, and claims nothing from it).

## 2. The named causes, reproduced

The brief named three causes; the run logs add a fourth that came first
(2d). All four are reds of one job whose design (#3315, R10-CI-SELFTEST-SCOPE)
measures the read-set table on `main` only, which is why the analysis below
treats them as one defect with one process.

### 2a. Table drift: `tools/ci/selftest_closures.json` misses what steps read

The drift check (`selftest_scope.py check`, step `drift`) runs on every push
to `main` and refuses any gated step whose committed entry misses a file,
probe, directory or flag the push run measured. At `57091a694` (run
42758119155, job 129637321760) it printed, by E2,
`selftest_scope check: 109 gated step(s), 38 refusal(s)`: 37 `UNDER-SCOPED`
lines and the UNGATED line of 2c.

Which side moved. Enumerator E3, the file entries the run's measured table
(its `selftest-closures` artifact 13737009763) adds over the committed one,
unioned over steps:

    gh api $A/actions/artifacts/13737009763/zip > a.zip && unzip -o a.zip
    git show 57091a694:tools/ci/selftest_closures.json > committed.json
    python3 -c 'import json; c=json.load(open("committed.json"))["steps"]
    m=json.load(open("selftest_closures.json"))["steps"]
    print("\n".join(sorted({f for k,v in m.items() if k in c
        for f in set(v.get("files",[]))-set(c[k].get("files",[]))})))' > missed.txt

It prints 37 entries (`wc -l < missed.txt`): 6 glob patterns
(`grep -c '\*\*' missed.txt`) and 31 concrete files. The table was last
recorded on #3315's branch at `a751546c5` (2026-11-08T18:06Z;
`git log -1 --format='%h %cI' ba6fd7e8b^2 -- tools/ci/selftest_closures.json`).
Of the 31, 4 did not exist there
(`grep -v '\*\*' missed.txt | while read p; do git cat-file -e a751546c5:"$p" 2>/dev/null || echo "$p"; done`),
each merged into `main` later by its own first-parent merge
(`git log --first-parent --diff-filter=A --format='%h %cI' 0362916ac -- <path> | tail -1`):
`tools/audit/seat/topic_grammar.py` `2b777aad7` 2026-11-09T16:23Z,
`tools/audit/seat/bottleneck_check.py` `b8f67a775` 2026-11-09T22:19Z,
`tools/ci/selftest_scope_mutants.sh` `2cf0f129b` 2026-11-10T01:47Z,
`tools/audit/seat/gh_read_run.py` `8652aa65c` (#3361) 2026-11-10T04:34Z.
The other 27 existed when the table was recorded; this seat did not establish,
per step, whether the step began reading them after the recording or the
recording missed them, and claims neither. The `probes` and `dirs` entries
show the same shape (section 4, E4): four directories absent at the
recording, among them `tests/mutation_ledger/killed_by/heat_curve.py`, merged
by `20d96598c` 2026-11-10T02:06Z (same command).

The table only grew after #3315: three first-parent commits touched it
(`git log --first-parent --format=%h ba6fd7e8b..0362916ac -- tools/ci/selftest_closures.json`:
`2cf0f129b`, `b8f67a775`, `2b777aad7`), each adding one step's entry and
deleting nothing (`git diff --stat <c>^1 <c> -- tools/ci/selftest_closures.json`:
26, 16 and 13 insertions, 0 deletions), taking its step count from 106 to 109
(`git show <c>:tools/ci/selftest_closures.json | jq '.steps|length'` at
`ba6fd7e8b` and at `0362916ac`). Its last change on `main` is #3375
(`2cf0f129b`). Nothing re-recorded the table wholesale after #3315 merged.

The measurement the repair needs already existed on every push run that
reached the `drift` step (the 13 `failure` rows of E1; section 3): the
`drift` step's `--write` uploads the run's own measured table as the
`selftest-closures` artifact (run 42758119155: artifact 13737009763, by
`gh api $A/actions/runs/<run>/artifacts --jq '.artifacts[]|select(.name=="selftest-closures")|.id'`). The
docstring of `tools/ci/selftest_scope.py` states the repair as
"`--write` saves the run's own measurement, which main uploads as the
`selftest-closures` artifact: commit that file, or re-record with `record`
(Linux, strace)". No seat, job or tick names who commits it. The hotfix brief
does it by hand: R10-HOTFIX-MAIN-SELFTESTS step 3, "Union
tools/ci/selftest_closures.json with main's later measurements, artifacts
13735714488 and 13737089304" (`git show 7901978c6:PROMPT.md`, that seat's
dispatched brief; the two are the artifacts of runs 42754467528 at
`5ab6030d7` and 42756781826 at `8652aa65c`, by the command above).

The drift is not a one-off of #3315's landing. #3315's own branch re-recorded
the table three times while it was open because `main` moved under it
(`git log --no-merges --format='%h %s' ba6fd7e8b^1..ba6fd7e8b^2 -- tools/ci/selftest_closures.json | grep -c "main's"`
= 3 of the 7 commits that touched it):
`2ff33ff92` ("re-record the 47 steps main's delta reaches"), `d9990a12f`
("gate main's new gantt-drift self-test step and record its read set"),
`a751546c5` ("gate main's plan-public, outside-intake and hooks-setup
self-test steps and record their read sets").

### 2b. A read set that moves every merge: `ref_privacy.added_lines`

`tools/audit/seat/ref_privacy.py` `added_lines` runs `git show REV:path` for
both sides of every path `git diff --name-only base ref` lists. For a path
absent on one side, git does not stop at the object store: to print
`fatal: path '<p>' exists on disk, but not in '<rev>'` it stats the worktree
path. So every step that calls it reads the push's own added and deleted
files, and no committed table can ever hold that set.

Reproduced in a worktree at `0362916ac`, counting the worktree path in the
trace:

    strace -f -qq -e trace=%file git show <rev>:tools/audit/seat/gh_read_run.py 2>&1 >/dev/null \
      | grep -c '"tools/audit/seat/gh_read_run.py"'

- absent side (`<rev>` = `HEAD~400`, before the file was added): 1, the
  worktree path beside the revision spec;
- present side (`<rev>` = `HEAD`), the null control: 0; no worktree path is
  touched.

On `main` this showed as an `UNDER-SCOPED` refusal of step
`push-names-the-host` (phase P2), never as an error: `added_lines` captures
git's stderr and reads an absent side as empty, so the step passed and only
its read set moved.

`selftest_scope.py`'s docstring lists the class as a stated blind spot ("a
step whose behaviour depends on the environment rather than the tree is not
scoped by any table"); `added_lines` is an instance whose environment is the
event's diff. The hotfix's fix (show only the sides that exist, from
`--name-status`) is R10-HOTFIX-MAIN-SELFTESTS's, not this seat's.

### 2c. #3361 landed an ungated step

#3361 (`8652aa65c`, merged 2026-11-10T04:34:59Z by
`gh api $A/pulls/3361 --jq .merged_at`) added the step "Show the
workflow read runner refusing its own fixtures" with `if: ${{ !cancelled()
}}`, which reads no `steps.scope.outputs.<id>`.

Reproduced with `python3 -I tools/ci/selftest_scope.py --self-test` in
detached worktrees:

- at `5ab6030d7` (`8652aa65c^1`): `selftest_scope self-test: 103 checks, 0 failed`;
- at `8652aa65c`: `FAIL the live job parses (118 steps) and its gating is
  consistent`, `103 checks, 1 failed`.

**This red was visible on #3361's own pull request and merged anyway.** Run
42748431595 ("CI code pr=3361", a `workflow_dispatch` at head `825f54927`,
the merged head; `gh api $A/actions/runs/42748431595 --jq '"\(.event) \(.head_sha[:9]) \(.conclusion)"'`)
concluded `failure` with one red job, `governance / instrument-self-tests`
(job 129632432183), at one step: "Show the self-test scope
(tools/ci/selftest_scope.py) refusing its own fixtures"
(`gh api "$A/actions/runs/42748431595/jobs?filter=latest&per_page=100" --paginate --jq '.jobs[]|select(.conclusion=="failure")|"\(.id) \(.name): \([.steps[]|select(.conclusion=="failure")|.name])"'`
prints that one job and that one step). #3361's body (`gh api $A/pulls/3361 --jq .body`) names
no such red: its `## Red checks` answers only a `gate` deferral, and it states
`CI PREDICT: no closures, fast, governance or instrument red predicted
against 51cd5ec8a42a`, a figure taken before #3315 landed the gating check it
later failed (`git merge-base --is-ancestor 51cd5ec8a ba6fd7e8b` exits 0). Two rules let that through as written:

- `instrument-self-tests` is not a required context (`governance.yml`
  job `instrument-self-tests`, comment "R10-CI-SLIM C7(a): not a required
  name");
- "Only a red on a required check is owed an answer (tvofi, 2026-11-07)"
  (`defect-root-cause.md`, Enforcement). So no reviewer verdict was owed a
  block on it.

### 2d. The push-only arm first ran on `main`

Everything #3315 added for a push (the `strace` install step, the tracing
wrapper `tools/ci/selftest_step.sh` under `SELFTEST_TRACE`, the `drift`
step) runs only when `github.event_name == 'push'`, which a pull request
never is. Its first execution was #3315's own merge. There, "Install strace"
failed on the runner's no-new-privileges sudo (phase P1, quoted above), the
launcher step was skipped after it so every waiter read a `lib.sh` no step
wrote, and the untraced job hit its 60-minute push timeout
(`timeout-minutes: ${{ github.event_name == 'push' && 60 || 30 }}` on the
job). The workflow comment at `ba6fd7e8b` records the push path as "measured
locally: about 34 minutes for both"
(`git grep -n -A1 'measured locally' ba6fd7e8b -- .github/workflows/governance.yml`),
on a Linux host where sudo works. #3375 (`2cf0f129b`,
R10-HOTFIX-SELFTEST-SCOPE-HANG) repaired it: `f27e09c38` "untraced ungated
steps", and `if: ${{ !cancelled() }}` on the launcher with the comment
"without its launcher each read a lib.sh no step wrote (run 42623897209)".
So phase P1 hid 2a for 28 pushes (E1, rows 1-28): the drift step could not
report.

## 3. The process state: (c)

**(c) The process was followed and did not produce the intended result.**

The process is #3315's own design for keeping the table true, quoted from
`.github/workflows/governance.yml` (job `instrument-self-tests`): "a push to
main runs each under strace ... and refuses a table that misses what it read
(`drift`), so a wrong closure turns main red within one merge", with its
repair stated in `selftest_scope.py`'s docstring (quoted in 2a), and the
orchestrator tick's main-red arm as the trigger for a repair seat
(`tools/audit/seat/orchestrator_tick.py` `red_brief`: "A main-red lane
becomes a FIXER DISPATCH BRIEF, required or not").

- **Present and obeyed.** The `drift` step ran and refused on every push run
  that reached it (E2: a summary line with a nonzero refusal count in all 13
  `failure` rows of E1, none in the 24 `cancelled`); the artifact was
  uploaded (`gh api $A/actions/runs/<run>/artifacts --jq '[.artifacts[]|select(.name=="selftest-closures")]|length'`
  = 1 for each of the 13); the tick's arm produced
  dispatch briefs, and the orchestrator dispatched two hotfix seats and this
  RCA seat against this one job inside the window:
  R10-HOTFIX-SELFTEST-SCOPE-HANG (#3375, merged 2026-11-10T01:47:42Z,
  `gh api $A/pulls/3375 --jq .merged_at`) and
  R10-HOTFIX-MAIN-SELFTESTS (in progress).
- **Wrong result.** The design converts drift into a red `main` and then into
  a fixer seat. The drift rate is a property of ordinary merges (2a, E3: 4
  missed files merged into `main` by 4 first-parent merges between
  2026-11-09T16:23Z and 2026-11-10T04:34Z, after the table's last recording;
  #3315's branch re-recorded three times in its own life), while a hand repair is one fixer
  cycle and lands a table measured at a base `main` has already left. So the
  repair is outrun: no push in the window concluded green.
- **Why the PR-side gates did not stop 2c.** Each was obeyed. The job is
  non-required by design; the answer rule covers required reds only; and
  `tools/pr/ci_predict.py` predicts `instrument-self-tests` reds through three
  hand-added arms (REF PRIVACY, WIRING, SEAT MUTANT SELF-TEST; 3 by
  ``git show 0362916ac:tools/pr/ci_predict.py | grep -c "instrument-self-tests\`'s"``),
  each written after an earlier escape, and none for `selftest_scope.py`'s
  own gating check (the same file's `grep -c selftest_scope` = 0). `prepr.sh` exited 0 at #3361's head (its body, `## Head`).

**Not (a).** A process existed for every arm: detection (`drift`), a stated
repair (commit the artifact), and a trigger (the tick's main-red brief). They
ran.

**Not (b).** No seat skipped a step it owed. #3361's red was not owed an
answer under the 2026-11-07 ruling; the hotfix seats were dispatched as the
tick briefed them. A firmer instruction ("commit the artifact", "answer every
instrument red") would be obeyed and still be outrun by the merge rate for
the first, and contradict an owner ruling for the second: the (c)-as-(b)
error `root-cause.md` section 2 warns of.

**Not (d).** No precondition moved after the design was made: the merge rate
and `main`'s habit of adding imported tools were already visible on #3315's
own branch (its three re-records), before it merged.

## 4. How far the class reaches

The class is **a gated step's measured read set that is false on `main`
without a seat writing it**. Three shapes, each with the rule that enumerates
it.

1. **Tree drift (2a).** Enumerator: the `drift` step itself on any push,
   `python3 -I tools/ci/selftest_scope.py check --traces DIR`. At `57091a694`
   it returns 38 refusals over 109 gated steps (the run's own summary line, E2).
   Every one is this class; none is closed by anything but a re-record.
2. **A read set that is a function of the event, not the tree (2b).**
   Enumerator, static: files that both list a diff's names
   (`--name-only`, `--name-status`, `diff-tree`) and run `git show REV:PATH`:

       for f in $(git grep -lE '"show", *f"\{' -- tools tests); do
         grep -qE -- '--name-only|--name-status|diff-tree' "$f" && echo "$f"; done

   It returns 23 files at `0362916ac` (`... | wc -l`). It over-approximates
   (a file may list names and show a fixed path); which of them a gated step
   reaches with an absent side is what the `drift` step measures. Its
   measurement at `57091a694` does not separate this shape from shape 1.
   Enumerator E4, the `probes` and `dirs` entries the run's measured table adds
   over the committed one (E3's two files), keeping those whose path, less a
   trailing `/.gitattributes`, is absent at the recording `a751546c5`:

       python3 -c 'import json; c=json.load(open("committed.json"))["steps"]
       m=json.load(open("selftest_closures.json"))["steps"]
       [print(k,n,f) for k,v in m.items() if k in c for n in ("probes","dirs")
        for f in sorted(set(v.get(n,[]))-set(c[k].get(n,[])))]' |
       while read k n f; do git cat-file -e a751546c5:"${f%/.gitattributes}" 2>/dev/null \
         || echo "$k $n $f"; done

   It returns 23 lines (`| wc -l`). 20 name four directories,
   `tests/mutation_ledger/{killed_by,survivor_triage}/{heat_curve,off_restore}.py`,
   under steps `beatd`, `dependency-graph-census`, `prepr`,
   `temp-or-machine-path` and `throwaway-git-helper` (4 lines each); 3 are a
   `-c` probe (`open-pr`, `pr-args`, `update-pr`), not a path. Those four
   directories reached `main` after the recording, so on its face this is
   tree drift; whether any of these steps also reads them only through an
   absent diff side is not measured here. The one instance of this shape the
   seat established is `push-names-the-host`, through 2b's mechanism. A
   second suspected instance, not of the `git show` shape, is named by the
   hotfix brief: beatd's recorded read set "(80, 20 and 235 files across
   runs, mostly dev/audit logs and PNGs)" may be timing-dependent
   (`git show 7901978c6:PROMPT.md`, R10-HOTFIX-MAIN-SELFTESTS step 4).
   Disposition: `push-names-the-host` and beatd are the hotfix's; the other
   files the static rule returns are reached by no refusal and carry no
   finding.
3. **A step added or changed without its gating (2c).** Enumerator:
   `selftest_scope.wiring_gaps(selftest_scope.workflow_steps(root))`, driven
   by a scratch probe at each commit's tree. Enumerator E5, the first-parent
   commits after #3315 that change the job's step count:

       for c in $(git rev-list --first-parent --reverse ba6fd7e8b^..0362916ac); do
         git show $c:.github/workflows/governance.yml | python3 -c 'import yaml,sys
       print(len(yaml.safe_load(sys.stdin)["jobs"]["instrument-self-tests"]["steps"]))' \
         | sed "s/^/${c:0:9} /"; done | awk '$2!=p&&p!=""{print}{p=$2}'

   It returns 4: `2b777aad7` (#3345, 115 steps), `b8f67a775` (#3350, 116),
   `2cf0f129b` (#3375, 117) and `8652aa65c` (#3361, 118). `wiring_gaps`
   returns 0 gaps at the first three and 1 at `8652aa65c` (and 0 at its parent
   `5ab6030d7`). Three of the four PRs that added a step after #3315 gated it
   themselves (#3345 by `977fd0033` topic-grammar, #3350 by `bb84b1bd2`
   bottleneck alert, #3375 its mutants step), so the rule was known and
   usually kept.

The same symptom recurs in round 10 independently of #3315. Enumerator E6,
the roster on `handoff/audit-r10-roster` (`1f0ea2c27`):

    git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json \
      | jq -r '.groups[]|select((.group|startswith("R10-HOTFIX")) and (.brief|test("instrument-self-tests")))|.group'

It returns 6 groups. One, R10-HOTFIX-NONREQUIRED-REDS-2, is a policy group
whose brief names the job as an example, not a red on it. The other five are
hotfixes of this one job on `main`: R10-HOTFIX-UUTILS-SLEEP (a `pr_args`
self-test red on an `ubuntu-26.04` runner), R10-HOTFIX-SELFTEST-TIMEOUT
(#3275, merged 2026-11-07T23:39:04Z), R10-HOTFIX-MAIN-IST-RED (#3307, merged
2026-11-08T06:58:52Z), R10-HOTFIX-SELFTEST-SCOPE-HANG (#3375) and
R10-HOTFIX-MAIN-SELFTESTS (merge times by `gh api $A/pulls/<n> --jq .merged_at`).
Only the last two are this design's.

## 5. The cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

Unit: wall-clock, per occurrence, over the round.

**cost(defect), this occurrence.**

| measure | value | how measured |
|---|---|---|
| main pushes with no green instrument-self-tests | 37 | E1: `wc -l < pushes.tsv`, and `cut -f4 pushes.tsv \| grep -c success` = 0 |
| span red or unconcluded | 20.5 h (2026-11-09T08:16:10Z to 2026-11-10T04:47:59Z) and open at the tip | `gh api $A/pulls/3315 --jq .merged_at` to `gh api $A/actions/runs/42758119155 --jq .created_at`, section 1 |
| hotfix and RCA seats dispatched on it | 3 (SCOPE-HANG, MAIN-SELFTESTS, this) | `jq -r '.groups[]\|select(.group\|test("SELFTEST-SCOPE-HANG\|MAIN-SELFTESTS"))\|.group'` on E6's roster file |
| a new cause landed under the standing red | 1 (#3361's UNGATED, 2c) | E5's `wiring_gaps` at `8652aa65c`; run 42748431595 |
| one traced push run | up to 60 min of runner per push | `timeout-minutes: ${{ github.event_name == 'push' && 60 \|\| 30 }}` on the job (2d) |

Each hotfix seat is a fixer cycle plus a review; the round's two earlier
hotfix merges on this job (#3307, #3375) are not re-timed here. The masking cost is the one that
compounds: while the job is red at `main`, a pull request's red on the same
job reads as inherited, and the one-step red that was #3361's own landed.

**P(recurrence).** Of the drift shape: every merge that adds a file a gated
step imports or lists re-drifts the table. Measured in the window: 4
missed files reached `main` by 4 first-parent merges inside about 12 h,
2026-11-09T16:23Z to 2026-11-10T04:34Z (2a, E3), and 4 more missed
directories by later merges (section 4, E4); the first fully traced phase
(P2) grew from 37 to 38 refusals at its fourth push, `b07627250` (#3399,
E2), whose diff changes `tools/plan/replan.py` and `sweep_template.md`
(`git diff --name-only b07627250^1 b07627250`), the new refusal being step
`sweep-template`'s probe of `tools/plan/replan.py`; and #3315's branch needed
three re-records while it was open (2a). So, without a mechanical repair, the
measured rate is several drifting merges per day at the round's merge rate,
and P(a drift after any hand re-record lands) is close to 1 within a day. Of
the ungated-step shape: 1 of the 4 PRs that added a step after #3315 (E5:
#3345, #3350 and #3375 gated theirs; #3361 did not).

**Countermeasure A: commit the measured table mechanically.** On a push to
`main` whose `drift` step refuses only `UNDER-SCOPED` or missing-entry lines,
a job downloads the `selftest-closures` artifact and pushes it to the
`record/autofix` branch, the route `nightly.yml`'s record-autofix already
uses (`push --force-with-lease=refs/heads/record/autofix:...` in
`nightly.yml` job `record-autofix`, one PR to `main`).
Standing cost: zero on a green push (skipped by `if:`); on a drifted push one
short job of a checkout, an artifact download and one push (the run's
artifact is already written: run 42758119155's job log shows 0.42 s from
`Uploading artifact: selftest-closures.zip` to `has been successfully
uploaded! Final size is 34857 bytes`, by the two lines' timestamps in
`gh api $A/actions/jobs/129637321760/logs | grep -E 'Uploading artifact: selftest-closures|successfully uploaded'`).
Its merge rides the record PR's route: #3393 (head `record/autofix`,
`gh api $A/pulls/3393 --jq .head.ref`) took 148 min open-to-merge
(`--jq '.created_at, .merged_at'`: 2026-11-09T22:20:14Z to
2026-11-10T00:48:48Z) with no seat time. Against an occurrence of 20.5 h red
and three seats, at a recurrence of several drifting merges per day, A
passes the test.
It addresses state (c): the process stays, its repair arm stops depending on
a seat outrunning the merge rate. It needs `.github/workflows/` (code-owned),
so it is a proposal for the owner, not built here. Its detector arm owes the
demonstration `defect-root-cause.md` requires: on a drifted push it opens a
record PR whose table makes the next `check` pass; on a clean push it does
nothing.

A cannot repair shape 2 (the event-dependent set re-drifts every push) and
must not try: a record of the push's own diff paths makes the table name
paths no other push reads. Its `if:` keys on the refusal lines, and a step
whose missed paths are the push's own added files is the fixer's
(R10-HOTFIX-MAIN-SELFTESTS), not the bot's.

**Countermeasure B: predict the ungated step before the PR.** A
`tools/pr/ci_predict.py` arm that runs
`selftest_scope.wiring_gaps(selftest_scope.workflow_steps(root))` on a diff
touching `.github/workflows/governance.yml`, predicting an
`instrument-self-tests` red per gap, in the same shape as its WIRING arm.
Standing cost: the whole self-test runs in 0.53 s
(`python3 -I tools/ci/selftest_scope.py --self-test` in a worktree at
`8652aa65c`, wall clock by `date +%s.%N` before and after, one run on this
seat's container), and the arm calls one function of it; `python3 -I
tools/pr/ci_predict.py` takes 2.2 s at that tree by the same clock. Against
one masked landing in four step additions (E5), B passes.

Demonstrated with a scratch probe calling that function (not committed:
`wiring_gaps` is production, the probe only drives it; it prints
`wiring_gaps: <len> <gaps>` and exits 1 on any gap):

- at `8652aa65c`: `wiring_gaps: 1 ["UNGATED step 'Show the workflow read runner
  refusing its own fixtures': its if: does not read steps.scope.outputs.<its
  own id>"]`, rc 1;
- at `5ab6030d7` (null control): `wiring_gaps: 0 []`, rc 0;
- at `8652aa65c` with that step given `id: gh-read-run` and
  `if: ${{ !cancelled() && steps.scope.outputs.gh-read-run == 'true' }}`
  (the fix, applied in scratch and reverted): `wiring_gaps: 0 []`, rc 0.

B addresses the same state (c): a gate that ran (`ci_predict.py`) and
predicted no red because none of its arms read this step's check.

**2d: no countermeasure, recorded.** The cheaper detector for a push-only arm
that breaks on the runner is running that arm before the merge: a
`workflow_dispatch` of the job with the push path forced on, on the pull
request's branch. Standing cost: one traced run (up to 60 min of runner, and
the push timeout) on every pull request that touches the job, or a seat step
to remember it. Recurrence: the enumerator
`git grep -c "event_name == 'push'" -- .github/workflows` returns 19 lines in
four files at `0362916ac` (1 `codeql.yml`, 3 `governance.yml`, 1
`nightly.yml`, 14 `tests.yml`), the oldest arm from 2026-08-26 (`13aa7b189`,
which adds `tests.yml`; `git log --reverse -S"event_name == 'push'" --format='%h %ad' --date=short 0362916ac -- .github/workflows | head -1`);
this seat found one of them, #3315's, that broke on its first push, and
measured no other. Cost of this occurrence: 28 pushes, phase P1 (E1, rows
1-28), until #3375 merged 17.5 h after #3315 (2026-11-09T08:16:10Z to
2026-11-10T01:47:42Z, the two PRs' `merged_at`). One instance in the 75 days
from 2026-08-26 to 2026-11-09
(`echo $(( ($(date -d 2026-11-09 +%s) - $(date -d 2026-08-26 +%s)) / 86400 ))`)
of push-only arms does not buy a standing 60-minute run per touching PR, so
none is built; the record stands until a second instance.

## 6. Verdict

- State: **(c)**.
- Cost test: **A and B both pass**; neither is built in this seat, which
  writes no production code. A changes `.github/workflows/`, which is
  code-owned, so it is drafted here for the owner, as `root-cause.md`
  section 5 requires; B is a `tools/pr/ci_predict.py` arm a fixer can build
  under ordinary review.
- 2d (a push-only arm first run on `main`): no countermeasure, recorded with
  its numbers in section 5.
- Shape 2 (event-dependent read sets) is not countered here: its established
  instance (`push-names-the-host`) and its suspected one (beatd) are the
  hotfix's, and the `drift` step already fires on it.
