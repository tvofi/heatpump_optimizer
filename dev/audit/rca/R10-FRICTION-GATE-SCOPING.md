# R10-FRICTION-GATE-SCOPING: the recurring-friction key `.claude/rules/gate-scoping.md` (#2835)

The root-cause record for the friction rule id `.claude/rules/gate-scoping.md`,
which the governance `record` job filed as #2835 (re-filing #2746 and #2768,
both closed by triage: `dev/programme/triage/s6-batch12.md` P81 and
`s6-batch22.md`). It groups every citing entry by the step of
`dev/governance/rules/gate-scoping.md` it names, gives each group a named
cause and a process state, and lands the one countermeasure the cost test
passes: the `tests/entities.py` stand-in environment, which no longer carries
`BASH_ENV` into a `bash -c` (section 3).

**Merge base and window.** Every figure was taken on 2026-10-29 with the merge
base at `88c6ad5bbec69bfe157e04597a74d0c9c3e4775c`, which was `origin/main` when
measured. Window `v7.0.4..origin/main`, tag `v7.0.4` =
`b448d26063cdb56aef915ceb604b807a885f9d71`. Nothing is carried from #2835's
body: its figure is a snapshot, and the count below is re-derived.

## 1. The count, and who it counts

`node tools/policy/policy_lint.mjs --stats --since v7.0.4` (rc=0;
`gate-scoping/stats_v7.0.4_88c6ad5.txt`, the scratch path in its `WINDOW_CACHE`
line replaced by `<seat-scratch>`, nothing else changed) prints
`10 / 11 .claude/rules/gate-scoping.md` over **285** merged pull requests:
10 distinct PRs, 11 entries. #2896's run at `6eb552157` printed `8 / 8` over 218
(`harness-friction/stats_v7.0.4.txt`), the control for the window's growth.

The histogram prints no PR numbers, so the entries were enumerated
independently: `gate-scoping/friction_lines.py` over the 285 merged bodies
(`gh api repos/tvofi/heatpump_optimizer/pulls/<N> --jq .body`, one per
`Merge pull request #N` subject in the window) prints
`TOTAL 10 PR(s) / 11 entr(ies) over 285 bodies` — the histogram's two numbers
exactly (`gate-scoping/friction_lines_88c6ad5.txt`). **Null control:** the same
bodies with `gate-scoping` rewritten to `gate-scopinX` print
`TOTAL 0 PR(s) / 0 entr(ies) over 285 bodies`, so the enumerator reads the key
and not the section.

## 2. The entries, by the rule's step

| step of `gate-scoping.md` | PRs (entries) | what each names |
|---|---|---|
| interpreter / environment: `BASH_ENV` | #2698, #2707, #2834, #2837 (4) | the same two `tests/entities.py` checks red at every tree under the container's `BASH_ENV` |
| interpreter / environment: the interpreter | #2627, #2870 (2) | default `python3` is 3.11 (`SyntaxError`); "no `homeassistant` module" |
| lease | #2873 (2) | wedged `prepr` runs held every heavy slot; a hand-held lease expired inside a 5857 s scoped gate |
| closures | #2780 (1) | the `tests/entities.py` strace recording is not deterministic at a fixed head |
| no step of the rule | #2622, #2700 (2) | a skipped `tmp_paths.py --check` at a handoff; the rule file at its token cap |

#2707 is filed under `BASH_ENV`, not closures: its body names the two checks
the closures recording failed on, `gate-sweep.yml: on CI's completion, …` and
`graders-head-copy's delivery_status step is red only when …`, failing at the
base `e97f5749b` and at its head alike — the pair #2834 and #2837 name. That
settles the "Unverified" line of `s6-batch22.md`.

## 3. `BASH_ENV` (4 PRs): a stand-in environment inherited whole

**Named cause.** Four `tests/entities.py` helpers plant a stand-in executable in
a temporary directory, put that directory first on `PATH`, and run a workflow
step's text under `bash -c` with `{**os.environ, "PATH": …}`: `_gs_step_verdict`
(U0c), `_train_hold_status`, `_pt_trigger` and `_pt_ds_rc` (delivery_status). A
fifth, `_raf_job_ok`, builds its environment from nothing under
`bash --noprofile --norc` and was never exposed. Bash sources `$BASH_ENV` before the script.
A cloud container whose environment sets `BASH_ENV=/etc/profile.d/hpo-toolchain.sh`
re-prepends `/opt/hpo/venv-ci/bin` there, and that directory holds `python3` and
`python` — exactly the two names U0c's and delivery_status's stand-ins carry —
so the real interpreter shadows the stand-in and both checks read red **at every
tree**. CI sets no `BASH_ENV`, so CI is green; the seat sees a red it cannot
attribute.

**Reproduction, at the merge base.** `/etc/profile.d/hpo-toolchain.sh` in this
seat is the unconditional form (`export PATH="/opt/hpo/venv-ci/bin:$PATH"`);
with it as `BASH_ENV`, `tests/entities.py` at `88c6ad5` reads
RESULT_BASE_BASHENV; the same tree under `env -u BASH_ENV` reads
RESULT_BASE_CLEAN.

**Process state: (d), with a (c) component.** The checks were sound under the
precondition CI keeps — no `BASH_ENV` — and a seat environment removed it.
The tree's answer to the environment, `8f2abbedf` (2026-10-24T10:31Z,
`cloud-setup.sh` writes a profile that prepends only when absent and tells the
owner to set variables instead of `BASH_ENV`), was followed and did not reach the
instances: its unit is a script the owner pastes into Project settings, and a
running environment keeps the profile it was built with — this seat's is the
pre-`8f2abbedf` form. All four entries merged after `8f2abbedf`
(#2707 2026-10-24T21:35Z, #2698 10-25T03:28Z, #2837 10-26T03:49Z,
#2834 10-26T16:58Z). `s6-batch22.md` named the condition that reopens it: "a
third entry from the `BASH_ENV` family after the profile lands". There are four.

**How far it reaches.** `grep -n '"PATH":' tests/*.py` at the merge base returns nine sites;
dispositions in the PR body's `## Figures`. Four `bash -c` sites inherited
`BASH_ENV` and are closed here; `:28268` builds a bare environment under
`--noprofile --norc` (already guarded); the two `node -e` sites
(`_fetch_ledger`, the `liveRequiredContexts` probe) resolve the stub through
node's `execFile`, which runs no `BASH_ENV` before the lookup (both green in the
`BASH_ENV` run above); the `("path", {"PATH": "1"})` row is a data literal;
`tests/throwaway_git.py`'s `hostile` builds a bare environment. Beyond `tests/`,
#2870 ran a seat's own `bus.sh --self-test` under `env -u BASH_ENV`: that
script's environment is the seat's, not a stand-in's, and the environment
repair is `R10-FLOW-DESIGN-STAGES`'s carried `cloud-setup.sh --check` arm.

**Cost test.** 4 PRs in 4.8 days since `8f2abbedf`, `P(recurrence)=1` while any
environment carries the old profile. Each instance costs a seat an
unattributable local red: #2707 states ~19 min of recording per occurrence and a
repeated round; #2834 and #2837 each spent a run proving the red is at the base.
The countermeasure is one helper (8 lines) and four call sites, and one check.

**Countermeasure (landed here).** `_stub_path_env(bindir, **extra)` in
`tests/entities.py` builds every stand-in environment: this process's
environment without `BASH_ENV`, `bindir` first on `PATH`. The four `bash -c`
helpers call it. A new check, "a stand-in on PATH wins in a bash -c under a
BASH_ENV that re-prepends a toolchain (#2835)", plants a profile that prepends a
directory holding a `python3` printing `toolchain`, sets it as `BASH_ENV` in
this process, and drives `_gs_step_verdict`; its control runs the same profile
through a plain `bash -c` and must read `toolchain`, so the arm cannot pass by
the profile failing to load. It is red at the merge base's behaviour (the
mutant that keeps `BASH_ENV` in the helper) and green at the head, in CI's own
environment, because it plants the `BASH_ENV` itself. Figures:
RESULT_HEAD_SUMMARY.

Refused: unsetting `BASH_ENV` once at the top of `tests/entities.py` (a check
that sets it later, as this one does, would not be covered, and the property
belongs to the helper that builds the environment); and a rule sentence in
`gate-scoping.md` (at its 794/794 token cap, and a tree that is immune needs no
instruction — `s6-batch22.md` reached the same refusal).

## 4. The interpreter (2 PRs)

**#2627** (2026-10-23): the container's default `python3` is 3.11 and cannot
parse `tests/entities.py`. **State (d)**, answered by `aa44f4bcc`
(2026-10-24T08:09Z), the rule's interpreter paragraph ("a `SyntaxError` or a
missing module is the interpreter: set `PYTHON` to `seat_venv.sh`'s venv").
After it, no entry names a `SyntaxError`. Reproduced here: this seat's
`python3` is `/usr/local/bin/python3`, 3.11.17, and
`bash tools/audit/seat/cloud-setup.sh --check` prints `REFUSE python3 is
/usr/local/bin/python3, HPO_TYPING_PYTHON is unset, OPENBLAS_CORETYPE is unset`,
while `/opt/hpo/venv-ci/bin/python` is 3.14.7 — the toolchain is built and the
environment's variables do not name it, although this seat's dispatch says "the
toolchain (venv python, node, gh) is on PATH from the environment".

**#2870** (2026-10-27): "needs a `homeassistant` module this seat's interpreter
lacks". `tests/run.sh` exports `PYTHONPATH=$PWD/tests/hastub` for every child,
and the rule names "a missing module" as the interpreter case, so a gate run
through `run.sh` under any 3.12+ interpreter finds the stub; the body quotes no
command or error text, and this seat cannot establish which of the two (a run
outside `run.sh`, or 3.11's error misread) it was. **State (b)** either way: the
rule names the symptom and the cure.

**Countermeasure: already owned, not duplicated.** The (d) repair is that a
cloud seat never starts on a toolchain `cloud-setup.sh --check` refuses:
`R10-FLOW-DESIGN-STAGES` (live, files include `tools/audit/seat/cloud_dispatch.py`,
whose `_prompt` renders the false sentence) carries it from #2709. This record
adds the measurement above to that carry's evidence; it builds nothing for it.
**Cost test for anything more:** one (b) instance in six days after the rule
named its cure; a firmer instruction is the "tell the worker harder" shape
`root-cause.md` warns against. Refused.

## 5. The lease (1 PR, 2 entries)

**#2873, first entry:** four wedged `prepr` runs held every heavy slot. A slot is
free "once its pid is gone"; a wedged run's pid is alive, so the pool is correct
to hold it. The cause is the wedge, answered by the orchestrator's `PREPR WEDGE`
directive the entry itself cites and by `R9-RCA-TRAIN-WEDGE.md`; not a step of
this rule.

**#2873, second entry:** the seat exported `HPO_GATE_LOCK_LABEL` for a scoped
gate that ran 5857 s; the lease it held by hand expires at 30 minutes and
`run.sh` renews it only at a leased script, so `stress.py` and
`harness_headers.py` found none and refused (`flock-wrap refused, … holds no
lease: no live gate lease to renew`). The rule says `run.sh` "under
`HPO_GATE_LOCK_LABEL` renews it", and `fixer.md` step 5 says `run.sh` "takes
the gate lease itself, around `tests/stress.py` alone" — with the label unset,
`run.sh` takes `auto-lease` per leased script and no expiry arises. **State (c)**:
the hand-held path was followed and its renewal unit (a leased script's start)
is longer apart than the expiry on a long gate.

**Cost test: refused.** One instance in the window; its cost, stated by the
entry, is one re-run of two scripts. A change to `flock-wrap` (re-take an expired
own-label lease) alters the refusal #2368 added for a label never taken, and is
not worth its review for one re-run. What would change the answer: a second
entry naming `no live gate lease to renew` under a run longer than the expiry.

## 6. Closures (1 PR)

**#2780:** of three `--single tests/entities.py --record-only` runs at one head,
one listed 2924 inert reads and two listed 6. One unreproduced instance; the
producer recorded "owed a root-cause seat if it recurs". No second entry names a
non-deterministic recording in the window (section 2's table is the whole
enumeration). **Refused, with that trigger kept:** this record does not run a
recorder race it cannot reproduce. (#2707's closures refusal is section 3's
cause, and is closed by it.)

## 7. Entries that name no step of the rule (2 PRs)

- **#2622:** a handoff did not run `tmp_paths.py --check`, which refused a
  self-test fixture on the assembled tree. That is `prepr.sh`'s check and the
  handoff's, not the gate's; the entry was carried to `R10-CI-LAYOUT-P2` and
  P81 dispositioned it.
- **#2700:** the rule is at its token cap after restoring what #2341 dropped. It
  is the rule's own budget, dispositioned `dismissed: an observation, no defect`
  by its author, and this record adds no tokens to it.

The key is a tag seats write for any gate-adjacent friction: 4 of the 10 PRs
(#2622, #2700, #2780's recorder, #2873's wedge) name nothing the rule's text
governs, and 4 more name the container. A rule edit would address none of the
ten, which is why this record edits no policy file.

## 8. Dispositions

| group | PRs | state | disposition |
|---|---|---|---|
| `BASH_ENV` | #2698 #2707 #2834 #2837 | (d) + (c) | countermeasure landed: `_stub_path_env` and its check |
| interpreter | #2627 | (d) | answered by `aa44f4bcc`; environment repair owned by `R10-FLOW-DESIGN-STAGES` |
| interpreter | #2870 | (b) | refused: cure is in the rule; one instance |
| lease | #2873 | wedge: not this rule; expiry: (c) | refused, trigger recorded |
| closures | #2780 | — | refused, producer's trigger kept |
| no step | #2622 #2700 | — | dispositioned by P81 and their authors |

## Evidence

`dev/audit/rca/gate-scoping/`:

- `stats_v7.0.4_88c6ad5.txt` — `policy_lint --stats --since v7.0.4` at `88c6ad5`, rc=0.
- `friction_lines.py` and `friction_lines_88c6ad5.txt` — the enumeration of
  section 1, and its output.
