# D3 verify, lens V3 (reach and class), unit lc: D3-s1-91, box G1-V3

Evidence tree 79aa98ec. The quiet window was not run (tvofi rule): no pre-screen, no pool, no full gate. The harness is `tools/audit/round9/D3/verify-v3-lc/D3-s1-91_realha_reach.py`.

## D3-s1-91: coordinator.py tzinfo guards :8112 and :8384 are dead under the gate's naive clock

- **Re-run** of `lc_tz_probe_coordinator.py`: an exact match on all 8 RESULT lines.
  - At :8384, divergence is 0 with HASTUB_TZ unset and 1 (TypeError) with HASTUB_TZ=Europe/Stockholm.
  - :586 and :588 diverge under both settings.
- **Own measurement on real HA 2026.2.3**, using the unmodified clock:
  - `dt_util.now()` is aware.
  - With the guard on, `_immersion_dhw_margin` returns 0.0. With the guard off, it raises TypeError on a naive stored event.
  - load1 0.07, thread_factor 1.0.
- **Reach.** The guard is live on every real install, because real HA's now() is always aware. The blind spot exists only on the stub's naive default clock, so deleting the guard would crash real installs that hold a naive stored immersion event. That store is restored verbatim at coordinator.py:2945.
- **Severity:** medium. The precondition is a migration edge case, and the failure is loud.
- **Seam rule:** partial. The first grep returns 5 lines, but only 8112 and 8384 match this shape:
  - 6331 is unconditional.
  - 586 and 588 diverge at UTC too.
- **Class:** I1.
- **Vote:** verify.
