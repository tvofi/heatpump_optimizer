"""F3.3 mutation proof: each mutant deletes or inverts one fix predicate,
the quick block runs, and the tree is restored."""
import subprocess, sys, pathlib
ROOT = pathlib.Path("/tmp/claude-0/f33/wt/custom_components/heatpump_optimizer")
M = [
 ("M1 defrost duty domain", "defrost.py", "            return 0.0 <= v <= 1.0  # observe_duty's gate; NaN fails it", "            return True"),
 ("M2 defrost cell-wise (all-or-nothing grid)", "defrost.py", "                grid.append(cells)\n            return grid", "                grid.append(cells)\n            return None if any(c is None for r in grid for c in r) else grid"),
 ("M3 defrost unreadable v2 half labelled migrated", "defrost.py", '        elif any(k in data for k in ("duty", "duty_counts")):', "        elif False:"),
 ("M4 price profile cone gate", "price_model.py", "    if low > 0.0 and high <= low * (hi / lo) * (1.0 + 1e-9):", "    if True:"),
 ("M5 price variance bound", "price_model.py", "if var is not None and max(max(s) for s in var) <= RESIDUAL_VAR_MAX:", "if var is not None:"),
 ("M6 price day-count floor (days and quarter_days)", "price_model.py", "return [max(0, int(v)) for v in raw]", "return [int(v) for v in raw]"),
 ("M8 tariff negative peak", "tariff.py", "if not math.isfinite(value) or value < 0.0:", "if not math.isfinite(value):"),
 ("M9 tariff window domain", "tariff.py", "            or not 0.0 <= tracker._window_factor <= 1.0\n        ):", "            or False\n        ) and False:"),
 ("M10 _raw_value overflow", "price_model.py", "        value = float(raw)\n    except (TypeError, ValueError, OverflowError):", "        value = float(raw)\n    except (TypeError, ValueError):"),
 ("M11 _entries_by_day overflow", "price_model.py", "            value = float(total)\n        except (TypeError, ValueError, OverflowError):", "            value = float(total)\n        except (TypeError, ValueError):"),
 ("M12 apply_price_adjustments overflow", "price_model.py", '* factor + extra\n        except (TypeError, ValueError, OverflowError):', '* factor + extra\n        except (TypeError, ValueError):'),
 ("M13 _parse_block overflow", "open_meteo.py", "            value = float(raw_v)\n        except (TypeError, ValueError, OverflowError):", "            value = float(raw_v)\n        except (TypeError, ValueError):"),
 ("M14 _parse_block smallest gap", "open_meteo.py", "min(gaps, key=lambda gap: (-gaps[gap], gap))", "min(gaps)"),
]
for name, f, a, b in M:
    p = ROOT / f; src = p.read_text()
    assert src.count(a) == 1, (name, a)
    p.write_text(src.replace(a, b))
    try:
        out = subprocess.run(["bash", "/tmp/claude-0/f33/quick.sh"], capture_output=True, text=True, env={"W": "120", "PATH": "/usr/bin:/bin"}).stdout
    finally:
        p.write_text(src)
    fails = [l.strip()[6:120] for l in out.splitlines() if l.strip().startswith("FAIL")]
    crash = "Traceback" in out
    print(f"{name}: {'KILLED' if fails or crash else 'SURVIVED'} by {len(fails)} check(s){' +crash' if crash else ''}")
    for l in fails: print(f"    FAIL {l}")
