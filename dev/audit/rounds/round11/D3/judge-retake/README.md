# R11-D3-JUDGE-RETAKE: the D3 wave's gate re-take and the sysid x86 probes

Evidence for the two carries of roster group R11-D3-JUDGE-RETAKE (roster
`handoff/audit-r11-roster` at db492eae), both against the D3 wave judge record
`dev/audit/rounds/round11/D3/wave-judge/JUDGE.md` at a826f55f8c.

Box: a cloud container, Linux x86_64, 4 vCPU Intel Xeon @ 2.10GHz, CPython
3.14.7, numpy 2.5.5, scipy 1.18.1, `OPENBLAS_CORETYPE=Haswell` (pinned by
`tools/audit/seat/cloud-setup.sh`), BLAS threads 1, no other seat on it.

Tree: the baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, unstripped, with
`dev/audit/rounds/round11/D3/` from main a59a1b0d9a copied over it (untracked)
and `s1/wave/D3-g35/` added from `handoff/audit-r11-verify-D3W`. The copied
`s1/state/gates/` was moved aside before the run, so the null and every verdict
below were written by this box alone.

## R11-D3-JUDGE-LINUX: the three sysid exact-float boundary probes

Command, per key, from the tree above:
`PYTHONPATH=tests/hastub OPENBLAS_NUM_THREADS=1 python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_<key>.py`
(probe sha1s: 64f3ef1f 81c55fdc72, d661d68f 5807f79bfc, 4da9d281 4586c6d41a;
`sysid_probe_common.py` 69c3f882de). Output: `sysid/<key>.out`.

Each probe runs every case under the baseline line and under the one-line
mutant in one process; `differing_cases` counts cases whose result tuple
differs. The probe's own null is its other cases, which run the same code on
inputs that land off the boundary and must not differ.

| key | site | judge's host (arm64) | this box (x86_64) | the case that moves |
|---|---|---|---|---|
| 64f3ef1feaaf7bc9 | sysid.py:2223, `0.01 <= ua` -> `0.01 < ua` | hunt_hit 0, differing 0 of 29 | hunt_hit 1 (x=0.01000000000032415), differing 1 of 30 | KEY hunted: completed fit ua=0.01 -> refused "fitted parameters outside plausible bounds" |
| d661d68f54982097 | sysid.py:2223, `tau <= 200.0` -> `tau < 200.0` | key_tapped_tau 200.00000000000887, differing 0 of 30 | key_tapped_tau 200.0, differing 1 of 30 | KEY tau==200: completed fit -> refused "fitted parameters outside plausible bounds" |
| 4da9d281d4714565 | sysid.py:2246, `> 0.10` -> `>= 0.10` | hunt_hit 0, differing 0 of 29 | hunt_hit 1 (x=1.3920022034486481), differing 1 of 30 | KEY hunted: completed fit -> refused "sensor drift collapsed into heat-loss" |

The null holds on all three: on each probe, 29 cases do not differ and 1
does, and that one is the key case on the boundary. All three move, so by the
carry's rule none is void. Each goes to R11-D3-PINS-sysid as a carry. The
precondition the carry states: the boundary is reached only where the fit's
floats land exactly on it, which happens on this x86_64 OpenBLAS-Haswell box
and not on the judge's arm64 macOS host (same CPython, numpy and scipy
versions). A pin that relies on the hit is
per-architecture (`fixer.md` step 15).
