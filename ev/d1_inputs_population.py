#!/usr/bin/env python3
"""Reviewer's instrument (the builder's, not the finder's): d1-inputs against two independent
enumerations of the configured entity slots. Run from the repository root at the head."""
import re, subprocess
P = "custom_components/heatpump_optimizer"
uni = {l.split()[1] for l in subprocess.run(["python3", "-I", "tools/audit/enumerate.py", "d1-inputs"], capture_output=True, text=True).stdout.splitlines()}
A = set(re.findall(r"const\.(CONF_\w+): \"an entity assignment\"", open(P + "/entry_config.py").read()))
B = {m.group(1) for m in re.finditer(r"_F\([^\n]*?(CONF_\w+)[^\n]*?(_entity_of|EntitySelector|_entity)\(", open(P + "/config_flow.py").read())}
print("RESULT d1-inputs universe=%d" % len(uni))
print("RESULT entry_config 'an entity assignment' keys=%d not in universe=%s" % (len(A), sorted(A - uni)))
print("RESULT config_flow entity-selector fields=%d not in universe=%s" % (len(B), sorted(B - uni)))
