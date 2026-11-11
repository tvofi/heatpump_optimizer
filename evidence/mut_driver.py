import subprocess, sys, os
F = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
M = {
 "NULL": ("// R10-CARD-COLLAPSE: the headline's two folds.", "// R10-CARD-COLLAPSE (null mutant): the headline's two folds."),
 "M1": ("this._folds = { narrative: false, whynow: false };", "this._folds = { narrative: true, whynow: true };"),
 "M2": ("this._folds = { ...this._folds, [key]: !this._folds[key] };", ""),
 "M3": ("        ${stats}\n        ${body}\n      </ha-card>", "        ${stats}\n        ${this.legend.html(this._series, \"card-\")}\n        ${body}\n      </ha-card>"),
 "M4": ("[...this.shadowRoot.querySelectorAll(\"[data-fold]\")][i];\n        if (again && typeof again.focus === \"function\") again.focus();", "[...this.shadowRoot.querySelectorAll(\"[data-fold]\")][i];"),
 "M5": ("        ev.stopPropagation();\n        const key = foldHead.getAttribute(\"data-fold\");", "        const key = foldHead.getAttribute(\"data-fold\");"),
 "M6": ("(lab.clamped || kept[kept.length - 1].clamped ? clampedGap : minLabelGap)", "minLabelGap"),
 "M7": ("  const summary = totals\n", "  const summary = false\n"),
 # reviewer's own
 "R1_reset_on_refresh": ("    setLanguage(hass && hass.language);\n    this._maybeRender(false);", "    setLanguage(hass && hass.language);\n    this._folds = { narrative: false, whynow: false };\n    this._maybeRender(false);"),
 "R2_focus_first_copy": ("const again = [...this.shadowRoot.querySelectorAll(\"[data-fold]\")][i];", "const again = this.shadowRoot.querySelector(`[data-fold=\"${key}\"]`);"),
 "R3_aria_always_false": ("aria-expanded=\"${unfolded ? \"true\" : \"false\"}\"", "aria-expanded=\"false\""),
 "R4_lead_weakest": ("Math.abs(weightOf(d)) > Math.abs(weightOf(a))", "Math.abs(weightOf(d)) < Math.abs(weightOf(a))"),
 "R5_body_always": ("(unfolded ? body : \"\") + `</div>`", "body + `</div>`"),
}
names = sys.argv[1:] or list(M)
src0 = open(F).read()
env = dict(os.environ, PYTHONPATH="tests/hastub")
for n in names:
    a, b = M[n]
    assert src0.count(a) == 1, (n, src0.count(a))
    open(F, "w").write(src0.replace(a, b))
    p = subprocess.run(["node", "tests/card.mjs"], capture_output=True, text=True, env=env, timeout=600)
    open(F, "w").write(src0)
    fails = [l for l in p.stdout.splitlines() if l.strip().startswith("FAIL")]
    print(f"{n}: {'KILLED' if p.returncode else 'SURVIVED'} rc={p.returncode} fails={len(fails)}")
    for l in fails[:8]: print("   ", l.strip()[:200])
    sys.stdout.flush()
subprocess.run(["git", "diff", "--exit-code", "--stat", F])
