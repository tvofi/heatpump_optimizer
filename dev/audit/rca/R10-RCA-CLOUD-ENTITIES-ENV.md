# R10-RCA-CLOUD-ENTITIES-ENV: cloud fixers blocked by `tests/entities.py` at prepr's closures step

Root-cause seat, run beside the work and never inside it
(`dev/governance/roles/root-cause.md`). Base: `origin/main` at
`4a9d2d5425ea13e728dca20aff15d7f76345dc73`, read 2026-11-08 12:35Z.

## 1. The defect

On 2026-11-08 four cloud fixer handoffs stopped at `tools/pr/prepr.sh` step 6b
with `REFUSE closures: failed while being recorded: tests/entities.py (exit 1)`.
No diff touched what failed:

| seat | where recorded | what it reported |
|---|---|---|
| `r10-dispatch-at-handoff-p2` | `BLOCKED.md` at `79fba7f2ee` (07:31Z), cleared by `092a333d57` (11:51Z) | 3 of 2665 checks failed: the coverage job reuse; the release ZIP ("the build step fails"); the Pages workflow ("probe ... rc=1 enabled=[]"). They failed the same way at origin/main. |
| `r10-hotfix-codeql-headroom` | `handoff-body/r10-hotfix-codeql-headroom` `BODY.md` | with `tests/hastub`, "52 environment failures (a*:, hb:, coverage reuse, release ZIP)". The seat did not compare them to main. Against the image's real `homeassistant` 2026.10.4, setup fails. |
| `r10-fly-no-self-carry` | `handoff-wip/r10-fly-no-self-carry` `BLOCKED.md` at `2e2d132aad` (11:56Z) | `ModuleNotFoundError: homeassistant` under venv-ci's python3, and `No module named 'paho'` under `/opt/hpo/venv-ha` |

The brief counts `r10-dispatch-at-handoff-p2` twice. The table shows only one
recorded block for it.

## 2. Cause, per failure shape

### Shape A: three checks fail identically at main (coverage reuse, release ZIP, Pages probe)

**Cause.** The cloud container has a `BASH_ENV` that names the profile
`tools/audit/seat/cloud-setup.sh` writes. Bash sources `BASH_ENV` before every
non-interactive script, even with `--noprofile --norc`.

Since `44c51bfec7` (2026-11-05, landed on main by #3222), that profile exports
`RUNNER_TEMP` unconditionally. `2fdab54f21` moved the value to
`/opt/hpo/runner-temp`, and nothing creates that directory: the header says
"exported, not created".

Each of the three harnesses gives its child bash its own `RUNNER_TEMP`, a
scratch directory, and then reads the result from that same directory:

- `_pg_probe_defects` (`tests/entities.py:41083`) runs the Pages `probe` step.
  The step redirects to `"$RUNNER_TEMP/probe.err"`.
- `_rel_zip_defects` (`:34309`) runs `release.yml`'s build step, which runs
  `git archive -o "${RUNNER_TEMP}/${ASSET}"`.
- `_cov_trust` / `_cov_marker` (`:31725`) run `tests.yml`'s `covtrust` step,
  which reads `"$RUNNER_TEMP/coverage-base"`.

Under the profile, each child's `RUNNER_TEMP` became the missing prefix
directory:

- the probe's redirect fails on every case;
- `git archive` cannot open its output;
- covtrust reads a directory the harness never wrote.

**Reproduction.** I wrote the profile from `write_profile` at base, under a
prefix with no `runner-temp`. I then ran the probe harness (a copy of
`_pg_probe_defects` over `pages.yml`'s own `probe` step) and the ZIP build (over
`release.yml`'s own step), under `env -u BASH_ENV` and under `BASH_ENV=<profile>`:

| run | Pages probe | release ZIP build |
|---|---|---|
| no `BASH_ENV` (control) | no defects | rc 0, the ZIP is where the reader looks |
| `BASH_ENV` = base profile | `probe on workflow: rc=1 enabled=[]`, the same on `404` and `legacy` | rc 128, `fatal: could not open '<prefix>/runner-temp/a.zip'` |
| `BASH_ENV` = base profile, `runner-temp` created | no defects (writer and reader both moved) | rc 0, but the ZIP is not where the reader looks |
| `BASH_ENV` = head profile (section 5) | no defects | rc 0, the ZIP is where the reader looks |

Rows 2 and 3 match what `BLOCKED.md` recorded: "probe ... rc=1 enabled=[]"
and "the build step fails". So the container's directory did not exist, and its
`BASH_ENV` named this profile. The coverage arm has the same writer/reader split,
known **by inspection only**: `covtrust` calls `python tests/closure.py`, and
this Mac has no `python` to replay it.

The full `tests/entities.py` (868 s and an exclusive lease, `tests/closures.json`
and `gate_lock.py needs-lease`) was not re-run on this Mac.

**Which side moved** (`git log -S`). The harnesses did not change. The
profile's `RUNNER_TEMP` export is the new part (`44c51bfec7`, `2fdab54f21`).
`cloud_dispatch.py.md` already listed `BASH_ENV` among the environment's
toolchain variables, although `cloud-setup.sh --variables` has never printed it
since `8f2abbedfb` (2026-10-24).

### Shape B: `ModuleNotFoundError: homeassistant`, then `paho` (r10-fly-no-self-carry)

**Cause: a misdiagnosis.** The recording itself ran under `derive_closures.sh`,
which exports `PYTHONPATH=tests/hastub` (`tests/derive_closures.sh:61`).

The seat's own diagnostic run did not. It ran `tests/entities.py` without the
`PYTHONPATH=tests/hastub` that the file's line 3 names and `tests/run.sh:101`
exports, so it found no `homeassistant`. Its second try, `venv-ha`, holds the
real `homeassistant` installed `--no-deps` for the mypy census
(`cloud-setup.sh`'s `pins venv-ha --no-deps`), so `paho` is missing by design.

The error the seat read was therefore not the recording's error. What made the
recording exit 1 is **not reproduced**. The same container on the same day
showed shape A, so shape A is the likely cause: an inference, not a measurement.

The codeql seat's real-HA failures (`dt.freeze`, `FakeConfig.config_dir`) are
the same misdiagnosis: it ran the suite against an interpreter the suite does not
target. Its 52 hastub failures include the two shape-A names. The rest (`a*:`,
`hb:`) were not compared to main, and this seat has no log to compare them with.

## 3. Process state: (d), with a barrier whose unit was too narrow

**(d) The preconditions changed.** The harnesses were correct, and so was the
setup process: tvofi pastes the script, the prompt runs `cloud-setup.sh --check`
(`cloud_dispatch.py`'s `SETUP_CHECK`), and that check read OK. Two things under
them changed:

1. the profile gained an unconditional `RUNNER_TEMP` export (#3222);
2. the environment carries a `BASH_ENV` that no current instruction asks for:
   `--variables` prints none, and the header says a seat's Bash call reads none.

The script *was* pasted, and recently. A container running a profile without
`RUNNER_TEMP` cannot produce the shape-A signatures. Its version is therefore at
or after `2fdab54f21`. That is inferred, not read: Project settings are not
readable from a seat.

**This is not state (a).** The class already had a barrier. The #2452 fix made
the profile's `PATH` line idempotent, with a self-test arm for `PATH` only. The
#2835 RCA (`dev/audit/rca/R10-FRICTION-GATE-SCOPING.md`) made the four `PATH`
stand-in helpers drop `BASH_ENV` (`_stub_path_env`).

Neither unit reached this instance:

- the first unit was one variable, `PATH`;
- the second was the helpers that put a stand-in on `PATH`.

The probe, ZIP and covtrust harnesses use no stand-in on `PATH`, and the variable
was new. `cloud_dispatch.py.md`'s workaround (`env -u BASH_ENV` for
`tests/entities.py`) was stated as lasting "until the pasted setup script writes
`cloud-setup.sh`'s idempotent profile". That had happened, so the rule read as
expired, and no prompt carries it.

**Shape B is (c).** `gate-scoping.md` says "Step 6b's `failed while being
recorded` is an exit code from one unleased run, not a cause: re-run that script
alone first". The seat did re-run it, but without `PYTHONPATH=tests/hastub`. The
rule names no command, and prepr's line names none either.

## 4. How far the class reaches

The class: **a profile sourced through `BASH_ENV` overwrites a variable that a
caller set for its child**.

Instances:

- #2452 (`PATH`);
- the #2835 group (`PATH`; friction entries #2698, #2707, #2834, #2837, counted
  in `R10-RCA-FRICTION-SWEEP.md` section 2);
- this one (`RUNNER_TEMP`, three checks, four blocks today).

That is three or more in round 10, so it is an **audit class**: it owes a
barrier that removes the class, not a refusal (`defect-root-cause.md`).

**Latent instances found by the search.** The base profile also overwrote these
variables unconditionally:

- `GIT_AUTHOR_*` and `GIT_COMMITTER_*`. `tests/throwaway_git.sh:28`,
  `tests/throwaway_git.py:95`, `tests/entities.py:30754` and `tools/pr/prepr.sh:2044`
  hand children their own identity, and any of those children that is a bash got
  `hpo-fixer` instead.
- `HPO_TYPING_PYTHON`. `tools/audit/seat/seat_venv.sh:130` sets it per child.
- `OPENBLAS_CORETYPE`.

The arm in section 5 reads all seven exports, and on the base profile it names
every one of them as overwritten.

## 5. Countermeasure: built, at the profile (the class's source)

`tools/audit/seat/cloud-setup.sh`'s `write_profile` now sets every variable
except `PATH` with `${NAME:-default}`. A value a caller set survives a nested
bash, and an unset one gets the old default. `PATH` keeps its prepend-when-absent
line.

The agent's own environment already gets the same values from the environment's
variables, or from `session-start.sh --env-lines`. The seat identity and the
pinned core type therefore still reach every seat shell, and a profile can no
longer change a value that a caller handed its child.

A new `--self-test` arm turns this from a promise about one variable into a
barrier on the profile:

- it derives the profile's exported names, as the `compgen -e` difference between
  a shell that sourced the profile and one that did not;
- it asserts there are seven besides `PATH`, a never-empty guard;
- as a control, it shows that a nested bash under `BASH_ENV` does run the profile;
- it requires each name to keep a caller's value under `BASH_ENV`.

A variable added to the profile later is covered without an edit to the arm.

**Fail-then-pass.** This Mac's `/bin/bash` 3.2 has no `mapfile`, so the whole
`--self-test` dies at its second arm here. It runs in `governance.yml`'s
"Show the cloud setup profile refusing its own fixtures" step. The new arm
uses no `mapfile`, so I ran it alone, extracted verbatim, against each
`write_profile`:

    == base (origin/main 4a9d2d5425) profile
    ok   the profile exports seven names besides PATH
    ok   control: a nested bash under BASH_ENV runs the profile
         overwritten: GIT_AUTHOR_EMAIL=e@x GIT_AUTHOR_NAME=hpo-fixer GIT_COMMITTER_EMAIL=e@x GIT_COMMITTER_NAME=hpo-fixer HPO_TYPING_PYTHON=<W>/hpo/venv-ha/bin/python OPENBLAS_CORETYPE=Haswell RUNNER_TEMP=<W>/hpo/runner-temp
    FAIL under BASH_ENV a nested bash keeps every variable its caller set
    == head profile
    ok   the profile exports seven names besides PATH
    ok   control: a nested bash under BASH_ENV runs the profile
    ok   under BASH_ENV a nested bash keeps every variable its caller set

The red-on-base run is the mutant run: the base `write_profile` *is* the defect.
The control arm cannot pass because the profile failed to load: it reads the
profile's own `RUNNER_TEMP` from a nested bash.

The defect's own harnesses also turn green under the head profile (the
last row of section 2's table).

**Not built:**

- **prepr tells an environment failure from a diff failure by re-running the
  failing script at the merge base.** Refused. It costs one more full run of the
  failing script on every failed recording; that is 868 s for `tests/entities.py`,
  the only script that failed today.
  It also converts a red into a pass. Had it existed today, all four seats
  would have handed off green over a broken environment, and the class would
  have stayed latent, as the `GIT_*` overwrites did. Its null control,
  "fails identically at main", is exactly what hid shape A from each seat.
- **The prompt names the `env -u BASH_ENV` rule.** Refused as the
  countermeasure. It is a workaround per command, and it would be state (b)
  treatment of a (d) defect. Until the next session's setup run writes the new
  profile, the corrected `cloud_dispatch.py.md` keeps the workaround, worded as
  conditional on that.
- **prepr's 6b line names the re-run command (`PYTHONPATH=tests/hastub python3
  <script>`) for shape B.** Not built here. It would not have changed today's
  outcome: the seat blocked correctly, and the cost came from shape A. It is
  offered to the orchestrator as a one-line candidate for `prepr.sh`'s
  `closures_verdict`.

## 6. Cost test

Wall-clock per occurrence, from today's record:

- `r10-dispatch-at-handoff-p2`: blocked from 07:31:36Z to 11:51:56Z, which is
  **4 h 20 min**.
- `r10-fly-no-self-carry`: blocked since 11:56:07Z, and still blocked at
  12:35Z, so **at least 39 min** and counting.
- `r10-hotfix-codeql-headroom`: the seat never ran prepr to a clean end, so its
  time on this is not separable from the rest of its round. **Not measured.**

All three needed an orchestrator ruling (`PREPR_SKIP_CLOSURES=1`) to proceed.

P(recurrence) is the measured class frequency: at least three instances in round
10 (section 4). Today's defect also stays live for every cloud fixer session
until the profile changes. Today that was 4 of 4 cloud fixer handoffs that
reached step 6b.

The standing cost is the arm, 0.24 s to 0.39 s for each `cloud-setup.sh
--self-test` run (three runs of `/usr/bin/time -p` here, profile write included),
and 0 s for the profile change. Set against at least 5 h of blocked seats in one
day, the inequality holds by four orders of magnitude.

**Verdict: build it** (built, section 5). The class also owes a barrier under the
audit-class rule, and this is it.

## 7. What needs tvofi

The environment is the owner's, so two settings are on the owner's side. Both
are needed, whatever this PR does.

1. **Remove `BASH_ENV` from the cloud environment's variables.** No seat
   process needs it: the agent's Bash call does not read it (the
   `cloud-setup.sh` header), and `--variables` does not print it. Its only
   effect is to run the profile ahead of every bash a test spawns. With it
   gone, the class has no way in. The profile change above is the barrier for
   the case where it is set again.
2. **Re-paste `tools/audit/seat/cloud-setup.sh` into Project settings >
   Environment > Setup script once this merges.** That applies if the pasted text is
   the script itself rather than a call to the checkout's copy. A seat cannot read
   which it is. Until a session's setup run writes the new profile, a cloud seat
   that keeps `BASH_ENV` reproduces shape A.

Until both are done, the orchestrator's per-case `PREPR_SKIP_CLOSURES=1` ruling
remains the interim. So does `env -u BASH_ENV ./tests/derive_closures.sh`,
which, by section 2's mechanism, would also record cleanly; that run was not
made.
