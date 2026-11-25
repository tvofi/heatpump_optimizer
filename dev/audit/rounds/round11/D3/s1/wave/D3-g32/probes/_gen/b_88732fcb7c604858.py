from custom_components.heatpump_optimizer import sysid

cfg = sysid.SysIdConfig()  # settle 1 h, step 2 h, relax 2 h: shortest phase 1 h
moved, rows = 0, []
# tau_fast = c_r*c_s/((c_r+c_s)*k_s); c_r = c_s = 1 gives tau_fast = 0.5/k_s
for k_s in (0.4, 1.0, 1.5, 1.6, 2.0, 2.5, 3.0, 3.1, 4.0, 6.0):
    b = sysid.slab_mode_one_state_identifiability(1.0, 1.0, k_s, cfg)
    with mock.patch.object(sysid, "FAST_MODE_SETTLE_TAUS", 6.0):
        m = sysid.slab_mode_one_state_identifiability(1.0, 1.0, k_s, cfg)
    tau = sysid.slab_mode_tau_fast(1.0, 1.0, k_s)
    print(f"RESULT tau_fast_{tau:.3f}h_baseline_ok={b[0]} mutant_ok={m[0]}")
    moved += b[0] != m[0]
print(f"RESULT verdicts_moved={moved} count  (tau_fast in (1/6, 1/3] h)")
b = sysid.slab_mode_one_state_identifiability(1.0, 1.0, 2.0, cfg)
with mock.patch.object(sysid, "FAST_MODE_SETTLE_TAUS", 6.0):
    m = sysid.slab_mode_one_state_identifiability(1.0, 1.0, 2.0, cfg)
print(f"RESULT tau_0.25h_baseline={b!r}")
print(f"RESULT tau_0.25h_mutant={m!r}")
# null control: an unconfigured slab, refused before the constant is read
b = sysid.slab_mode_one_state_identifiability(1.0, 0.0, 2.0, cfg)
with mock.patch.object(sysid, "FAST_MODE_SETTLE_TAUS", 6.0):
    m = sysid.slab_mode_one_state_identifiability(1.0, 0.0, 2.0, cfg)
print(f"RESULT null_delta={int(b != m)} count")
tail()
