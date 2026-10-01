# Re-introduce one round-9 P9 instance into a worktree's card (or grid), in place.
import sys
wt, key = sys.argv[1], sys.argv[2]
card = f"{wt}/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
grid = f"{wt}/tests/card_browser.mjs"
def rep(path, a, b, count=1):
    s = open(path).read()
    assert s.count(a) == count, (key, a[:60], s.count(a))
    open(path, "w").write(s.replace(a, b))
if key == "status_text_token":  # D4-s1-01: status text in HA's status tokens
    rep(card, "const warnColor = darkMode ? WARNING_READABLE_DARK : WARNING_READABLE;", 'const warnColor = "var(--warning-color, #d98e00)";')
    rep(card, "const errorColor = darkMode ? ERROR_READABLE_DARK : ERROR_READABLE;", 'const errorColor = "var(--error-color, #e0544e)";')
    rep(card, "const successColor = darkMode ? SUCCESS_READABLE_DARK : SUCCESS_READABLE;", 'const successColor = "var(--success-color, #2fae7a)";')
elif key == "confirm_fill":  # D4-s1-01 sibling, P9-rca1: white on --error-color
    rep(card, "border-color: ${ERROR_READABLE} !important;\n        background: ${ERROR_READABLE};", "border-color: var(--error-color, #e0544e) !important;\n        background: var(--error-color, #e0544e);")
    rep(card, "border-color: ${ERROR_READABLE};\n        background: ${ERROR_READABLE};", "border-color: var(--error-color, #e0544e);\n        background: var(--error-color, #e0544e);")
elif key == "menu_clamp":  # D4-s1-02: the slot menu at the raw tap point
    rep(card, "menu.style.left = `${Math.min(Math.max(0, rawLeft), maxLeft)}px`;", "menu.style.left = `${rawLeft}px`;")
    rep(card, "menu.style.top = `${Math.min(Math.max(0, rawTop), maxTop)}px`;", "menu.style.top = `${rawTop}px`;")
elif key == "picker_wrap":  # D4-s1-03: a fixed head/tail budget per id
    rep(card, "function pickerLabelIds(ids) {", "function pickerLabelIds(ids) {\n  return Object.fromEntries(ids.map((id) => [id, middleEllipsis(id)]));\n}\nfunction pickerLabelIdsUnused(ids) {")
elif key == "now_temp_below":  # D4-s1-05: now-temp on the first label row
    rep(card, '`<text class="now-temp" x="${plotL + 6}" y="${plotT + labelRow * 2}"', '`<text class="now-temp" x="${plotL + 6}" y="${plotT + font}"')
elif key == "estimated_label":  # P9-rca2/rca3: label on row one, secondary token
    rep(card, '`<text class="estimated-label" x="${ex + 4}" y="${plotT + labelRow * 3}" font-size="${font}" fill="var(--primary-text-color,#212121)">', '`<text class="estimated-label" x="${ex + 4}" y="${plotT + font + 4}" font-size="${font}" fill="var(--secondary-text-color,#888)">')
elif key == "slot_hit_ink":  # P9-rca4/P9-f61c: each target grows against its neighbours' INK again
    rep(card, "  for (let pass = 0; pass < 4 * order.length + 4; pass++) {", "  for (let pass = 0; pass < 0; pass++) {")
    rep(card, "    if (t[p].r <= t[p + 1].l) continue;\n    const lo = ink(p).x2", "    if (free[p]) t[p].r = Math.min(t[p].r, ink(p + 1).x1);\n    if (free[p + 1]) t[p + 1].l = Math.max(t[p + 1].l, ink(p).x2);\n    continue;\n    const lo = ink(p).x2")
elif key == "dark_unwired":  # carry 1652: the grid never sets hass.themes.darkMode
    rep(grid, "themes: { darkMode: dark } };", "};")
elif key == "drop_status_states":  # null control on reach: no cell renders the status rules
    rep(grid, "  const states = gridStates(plan);\n  // Contrast", '  const states = gridStates(plan).filter((s) => !["pin_ok", "pin_fail", "save_ok", "save_fail", "dhw_clamped", "save_confirm", "setup_clear_armed"].includes(s.name));\n  // Contrast')
else:
    raise SystemExit("unknown " + key)
print("perturbed", key)
