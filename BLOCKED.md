Question: carry 1 (R11-D3-JUDGE-GATE) needs 32 sequential full gates at 92d38ecb, about 28 h of one exclusive box (null measured green here at 3165 s). Carries 0, 2 and 3 need no code from this group, so there is no diff to hand off. Should carry 1 be (a) dispatched as its own box run, split across boxes by key, with this group's carries then closed as a record-only handoff; or (b) run on by this seat over the next ~28 h, pushing each key's gate record to handoff-wip as it lands?

# BLOCKED: R11-SEAM-tests fixer, carries pass: measurements at origin/main ac9045c223721608e684c8a2213831aa34c1fa4f

Box: cloud container, x86_64, 4 cores, venv-ci CPython 3.14.7, numpy 2.5.5, scipy 1.18.1,
OPENBLAS_CORETYPE Haswell (`cloud-setup.sh --check` OK).

The group's four findings are on main: #3825 (A, B, D; merged 2026-11-25) and #3890
(C; merged 2026-11-25). The roster resume reads `carries-open`. This pass measures
the four carries.

## Carry 0: the #3195 review's mutants (M13, M3, M9, M10)

Rule: each mutant is the review's own text (verdict/3195 at 6f742a33, comment 6638991342),
planted once in a detached worktree of ac9045c2. `PYTHONPATH=tests/hastub python3 -u
tests/features.py` is run in that worktree. The planting script asserts that the `old`
text occurs exactly once.

| arm | edit | features.py | killing check(s) |
|---|---|---|---|
| NULL | none | `ALL 6322 FEATURE CHECKS PASSED`, rc 0 | - |
| M13 | optimizer.py `_settlement_schedule`: `step["baseline_kw"] = baseline[i]` -> `pass` | `1 of 6322 FEATURE CHECKS FAILED`, rc 1 | `R10-SAV-COMFORT: the baseline is booked on the steps it covers and no further` |
| M3 | `delivered = 0.5 * (zone[i] + zone[j])` -> `delivered = zone[i]` | `4 of 6322`, rc 1 | `the comfort shortfall floors each demand at zero` (outdoor 10.0, 20.2); `two-zone, the comfort shortfall is the lower floor's` (outdoor 10.0, 20.2) |
| M9 | ledger.py `savings_months`: `scale` dropped from `stored_sek` | `1 of 6322`, rc 1 | `R11-SEAM-tests (carry 0, M9): a calibrated month scales the stored-heat line as it scales the thermostat` |
| M10 | `scale` dropped from `comfort_sek` | `1 of 6322`, rc 1 | `R11-SEAM-tests (carry 0, M10): a calibrated month scales the comfort line as it scales the thermostat` |

The verdict is that all four are closed with the killing tests above, and no pin is owed. M9 and
M10 were pinned by fc544a6739 (#3825). M13 and M3 were already killed by the R10-SAV-COMFORT
block. One residue is a note, not a gap. The review asked for M13 to be pinned end to end through
`get_current_action`. The killing check drives `_settlement_schedule` directly, and the
action's `baseline_kw` read goes through `_settlement_at`. The carry's control ("a mutant
already killed is recorded as closed with the killing test") is met.

## Carry 2: R11-D3-JUDGE-LINUX, the three sysid.py exact-float boundary probes

Harness: `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/` from a826f55f8c. The
sha1s are: sysid_probe_common.py 69c3f882dec0bf90122469983b81f3c3ea126455,
probe_64f3ef1feaaf7bc9.py 81c55fdc723f485a9b4b53351e285c349b30717a,
probe_d661d68f54982097.py 5807f79bfc7eb8bea9a166dcf712339593ad6107,
probe_4da9d281d4714565.py 4586c6d41a1a82e6ad327a6bd9ad3b54af2b97ec.
Command: `PYTHONPATH=tests/hastub python3 -u <probe>`, run from a worktree.

| key | mutant | recorded baseline 92d38ecb (unported) | head ac9045c2 (port: `SysIdConfig(enabled=True, ...)` -> `SysIdConfig(...)`, the only change) |
|---|---|---|---|
| 64f3ef1feaaf7bc9 | sysid.py `0.01 <= ua` -> `0.01 < ua` | `hunt_hit=1` (x=0.01000000000032415), key completed True -> False, `differing_cases=1` of 30 | same readings |
| d661d68f54982097 | `tau <= 200.0` -> `tau < 200.0` | `key_tapped_tau=200.0` (arm64 read 200.00000000000887), key completed True -> False, `differing_cases=1` of 30 | same |
| 4da9d281d4714565 | `abs(ua_ss - ua) / ua > 0.10` -> `>= 0.10` | `hunt_hit=1` (x=1.3920022034486481), key True -> False (`sensor drift collapsed into heat-loss`), `differing_cases=1` of 30 | same |

Null control: in each probe the 29 non-key cases read identically in both arms
(`differing_cases=1` of `cases=30`). Unported, the head arm fails with `TypeError:
SysIdConfig.__init__() got an unexpected keyword argument 'enabled'`, so the port is the
reading's precondition.

The verdict is that all three move on Linux x86_64, at the recorded baseline and at ac9045c2. Per
the carry text, each goes to R11-D3-PINS-sysid as a carry. The judge's own note stands:
"Even reproduced, an exact-equality boundary of a fitted parameter is a nit".

## Carry 3: class I1 (#3755), the RCA path

`dev/audit/rca/` at ac9045c2 holds no round-11 I1 class analysis. `ls dev/audit/rca | grep
-iE 'I1'` returns only `R9-I1.md`. `bugclasses.json` I1 `.rca` lists R9-I1,
R9-N-cpu-gate-blind, RCA-1336-d9-memory-arm, RCA-1485-ledger-line-shift,
RCA-1595-nan-ratchets, RCA-R8-I1a-kill-rule and RCA-vacuous-acceptance-arm, and no R11
document. The carry says the analysis is owed by a root-cause seat beside this group, never
inside it, so there is no path to record on #3755 yet.

## Carry 1: R11-D3-JUDGE-GATE

The record (JUDGE.json at a826f55f8c, `.verdicts[]`) has 426 keys. Taking the first key of
each (basename(file), gap_kind) pair in record order gives 32 keys:
`python3 -c "import json,os;v=json.load(open('JUDGE.json'))['verdicts'];s={};[s.setdefault((os.path.basename(x['site'].rsplit(':',1)[0]),x['gap_kind']),x) for x in v];print(len(v),len(s))"`
prints `426 32`. Each key is one `GATE_SCOPE=full GATE_JOBS=1 ./tests/run.sh` under
`fullgate.py run` at 92d38ecb, alone on the box. The green null precondition is one more
such gate (`fullgate.py null`).

Null control: `fullgate.py null` (a826f55f8c, `dev/audit/rounds/round11/D3/s1/fullgate.py`)
was run in a worktree at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 with the script copied in,
alone on this box. It read `gate_rc=0`, `failed_scripts=0`, `ALL TEST SCRIPTS PASSED`,
wall 3164.6 s, child CPU 5214.1 s, load1 0.62 -> 1.00. So the precondition ("a tree whose null
gate is green") holds on Linux x86_64 at the record's own baseline. The judge's box read the
null red on `closure.py selftest`, `entities.py` and `harness_headers.py`.

Cost: 32 keys x 3165 s is about 28 h of exclusive box time. The keys must run one at a time,
because each takes the gate_lock lease and stress.py's timing channels need the box alone.
A killed key also re-opens its stratum's other keys (up to 426 in all). No key was run.

Carry: R11-SEAM-tests (pending orchestrator ruling: the question above)

## Forward-carry (for the relay to fold; this seat writes no roster)

- The three sysid.py exact-float boundary mutants 64f3ef1feaaf7bc9, d661d68f54982097 and
  4da9d281d4714565 reproduce on Linux x86_64, at 92d38ecb and at ac9045c2. In each probe
  `differing_cases=1` of 30, and the key case's `completed` goes True -> False. The control is
  the 29 non-key cases, which are identical in both arms. The probes are at a826f55f8c
  `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/` (sha1s above). At the current base the
  one port is dropping `enabled=True` from `SysIdConfig(...)`. Re-measure at your merge base;
  claim each kill from your own pin under the patch. Carry: R11-D3-PINS-sysid
- Class I1 (#3755): no round-11 I1 class analysis exists under `dev/audit/rca/` at ac9045c2,
  so there is no path to record on the issue yet. The analysis is the root-cause seat's.
  Carry: R11-SEAM-tests (pending orchestrator ruling: dispatch the I1 root-cause seat; this group records its path on #3755 once it exists)
