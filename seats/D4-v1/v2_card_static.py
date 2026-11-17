#!/usr/bin/env python3
"""V2 (D4-v1) static source measures over the production card (heatpump-optimizer-card.js).
Run from the export root. Per finding: the source facts the rendered number must come from.
s1-01: pipe rules (stroke-width, any wider transparent hit path for pipes).
s1-03: .hl-fold-head rules and the coarse-pointer floor selector list.
s3-01: sites printing err.message vs sites reading translation_key.
s3-03: em font-sizes on tooltip/tt-shared/sp-note/verdict rules.
s3-04: *_READABLE constants and --hpo-crit/ok/warn literals.
s3-05: distinct literal font-size values in the stylesheet.
"""
import re
s = open("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js").read()
def rules(pat):
    for m in re.finditer(r"([^{}]*%s[^{}]*)\{([^{}]*)\}" % pat, s):
        yield " ".join(m.group(1).split())[-90:], " ".join(m.group(2).split())[:200]
print("== s1-01")
for sel, body in rules(r"setup-pipe"): print(f"  {sel} {{ {body} }}")
print("  pipe-hit class present:", bool(re.search(r"pipe-hit|pipeHit", s)))
print("== s1-03")
for sel, body in rules(r"hl-fold-head"): print(f"  {sel} {{ {body} }}")
m = re.search(r"pointer: *coarse\)[^{]*\{(.{0,1500})", s, re.S)
print("  coarse block mentions hl-fold-head:", bool(m and "hl-fold-head" in m.group(1)))
print("  .sp-filter, .sp-select floor list line:", [l.strip() for l in s.splitlines() if ".sp-filter, .sp-select" in l][:3])
print("== s3-01")
em = [i + 1 for i, l in enumerate(s.splitlines()) if re.search(r"err(\.message| && err\.message)", l)]
tk = [i + 1 for i, l in enumerate(s.splitlines()) if "translation_key" in l]
print(f"RESULT err_message_sites={len(em)} lines={em} translation_key_reads={len(tk)} {tk}")
print("== s3-03")
for p in (r"\.tooltip", r"tt-shared", r"sp-note", r"verdict"):
    for sel, body in rules(p):
        fs = re.findall(r"font-size:[^;]*", body)
        if fs: print(f"  {sel} -> {fs}")
print("== s3-04")
for l in s.splitlines():
    if re.search(r"(ERROR|SUCCESS|WARNING)_READABLE[_A-Z]* *=|--hpo-(crit|ok|warn)[a-z-]*:", l): print("  ", l.strip()[:140])
print("== s3-05")
fs = sorted(set(re.findall(r"font-size: *([^;\"`}]+)", s)))
print(f"RESULT distinct_font_size_exprs={len(fs)}"); print("  ", fs)
