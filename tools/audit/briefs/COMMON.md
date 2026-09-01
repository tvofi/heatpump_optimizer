# The finder's contract (every dimension)

You are one of eleven auditors, each with one dimension, working in parallel
with fresh eyes against a pinned baseline of this Home Assistant integration.
Your job is to find what is wrong in your dimension and to prove it with an
executed number. An argument is not a finding. A number you did not execute is
not a finding. A number that cannot be re-executed from a committed harness is
not a finding.

## Where you work

- Your tree is an export of the baseline SHA named in your task, under the
  directory named in your task. It has no `.git`, no `docs/audit-*.md`, no
  `docs/backlog.md` and no `RELEASE_NOTES.md`. That is deliberate: earlier
  audit rounds must not steer you. Do not run `gh`, do not read GitHub, do not
  look for earlier findings anywhere (comments in code that cite a `D<k>-nn`
  id are context, not a to-do list). If your dimension forces you to read
  `docs/` (D5, D6), record what you were exposed to in the `exposure` field.
- Run everything from the export root with `PYTHONPATH=tests/hastub`. Read
  `tools/audit/README.md` before writing a harness: it lists the builders to
  reuse and the traps that have already cost a day each.
- Write only under `tools/audit/round<N>/D<k>/` in the export, plus temp
  directories. Set a private `HPO_PLANDATA` under the temp root before any
  Node harness. Never modify production or tests in the export unless your
  brief says you have an isolated worktree for that purpose (D3, and D0/D9
  when instrumenting).
- The box is shared with the other ten auditors. Only contention-immune
  numbers are final during the fan-out: counts, bytes, ratios against the
  stress reference solve (`tests/stress.py:reference_solve`). Every wall, CPU
  or RSS number you report is provisional, will be re-taken in a quiet
  window, and must carry `load1` and `thread_factor` so the judge can see the
  conditions.

## What a finding is

A finding is a falsifiable claim about the baseline with:

1. **An executed number** from a harness under `tools/audit/round<N>/D<k>/`
   that satisfies the harness contract in the README (header, `RESULT`
   lines, thread pin, private temp paths).
2. **An instrumented symbol**: the production `module:symbol` the harness
   hooks or drives. A number derived from constants or from reading code is
   not evidence.
3. **A perturbation**: a config change or one-line production edit under
   which the number must move, and the direction. The judge runs it; a
   harness whose number does not move is voided.
4. **A metric definition** in one line, so a verifier measuring the same
   thing can tell whether it measured the same thing.
5. **A null control** whenever the claim is about cost, gain or time: the
   same measurement at the flat price profile, or the equivalent arm where
   the effect should vanish. Five measurement designs on this project have
   failed the flat-price control; a gain that survives at flat prices is an
   artefact of the arms, not of the mechanism.
6. **Leave-one-out** whenever the number is an aggregate over a grid: at
   least five cells, the range across cells, and the value with the single
   most favourable cell dropped. A mean over hand-built scenarios is a
   referendum on row counts.
7. **Severity** by consequence for a user on Raspberry-Pi-class hardware
   running all of Home Assistant: `critical` = wrong money or wrong comfort
   silently, data loss, the host unreachable; `high` = a user-visible defect
   or a wrong published value; `medium` = a defect with a workaround or a
   bounded cost; `low` = hygiene. Do not inflate; the panel weakens inflated
   severities and it costs credibility.
8. **A stop-rule class**: `bug` (the code does something wrong) or `hygiene`
   (naming, wording, structure, dead code). Provisional; the judge sets it.

Group by phenomenon, not by symptom: one finding per mechanism, however many
places it shows.

## What a non-finding is

Everything you checked that held, each with the command and the number that
showed it. These matter as much as findings: they are what lets a later round
be called dry, and they stop the next auditor re-doing your work. Disproved
leads that turned out to be harness gaps go here with the gap named.

## Output

- `tools/audit/round<N>/D<k>/REPORT.md`: method, findings in full, non-findings,
  harness list, what you could not finish and why, and your `exposure`.
- The JSON report returned from your task, validating against
  `tools/audit/finding.schema.json`. The schema makes `evidence`,
  `instrumented_symbol`, `perturbation` and `metric_definition` required; a
  finding without them cannot be returned, so do not try to return one.
- Harnesses committed in place, each runnable by the single command in its
  header.

## Budget

Aim to return within about two hours of wall clock. Prefer three findings with
numbers the judge will reproduce over ten with numbers the judge will void.
If a measurement needs the quiet box (a full gate run, a long solve series),
report it as `provisional` with the fan-out number and the command, and the
quiet window re-takes it.
