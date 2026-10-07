import sys, pathlib
p = pathlib.Path("/Users/timmalmstrom/hpo-seats/r9c-rev-2025/custom_components/heatpump_optimizer/entry_config.py")
s = p.read_text()
M = {
 "M0": ('def _flag(value: Any, default: bool) -> bool:\n    return bool(value)', 'def _flag(value: Any, default: bool) -> bool:\n    return bool(value)  # null'),
 "M1": ("    return result if math.isfinite(result) else default\n", "    return result\n"),
 "M2": ("    except (TypeError, ValueError, OverflowError):\n        return default\n    return result if", "    except (TypeError, ValueError, OverflowError):\n        return value\n    return result if"),
 "M3": ("    return None if math.isnan(result) else result\n", "    return result\n"),
 "M4": ('    return str(value) if value else ""\n', '    return str(value)\n'),
 "M5": ('    return str(value) if value else None\n', '    return str(value)\n'),
 "M6": ('f.metadata["parse"](merged[f.name], f.default)', 'merged[f.name]'),
 "M7": ("    return _number(value, default) or default\n", "    return _number(value, default)\n"),
 "M8": ("    try:\n        return int(value)\n    except (TypeError, ValueError, OverflowError):\n        return default\n", "    return int(value)\n"),
}
old, new = M[sys.argv[1]]
assert s.count(old) == 1, sys.argv[1]
p.write_text(s.replace(old, new))
