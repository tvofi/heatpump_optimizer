import sys, subprocess, shutil, os, re
W = open('/root/W').read().strip()
SRC = f"{W}/wt"; CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
M = {
 "M01_copstate_step2_gone": ('if (obs === "not_measurable" || obs === "no_electric_meter") {', 'if (false) {'),
 "M02_debug_read_level": ('const s = res && res.response && res.response.debug && res.response.debug[entryId];', 'const s = res && ((res.response && res.response.debug && res.response.debug[entryId]) || (res.debug && res.debug[entryId]) || res.response || res);'),
 "M03_debug_any_entry": ('res.response.debug[entryId];', 'Object.values(res.response.debug)[0];'),
 "M04_no_confirm": ('&& !host._debugArmed) {', '&& false) {'),
 "M05_diag_no_fallback": ('navigateTo(url || haLink("options", entryId), url ?', 'if (url) navigateTo(url, url ?'),
 "M06_settling_eta": ('return { text: pct === null ? L("health.learner_settling_any") : L("health.learner_settling", { pct }),', 'return { text: (pct === null ? L("health.learner_settling_any") : L("health.learner_settling", { pct })) + (readNumber(p.eta_days) === null ? "" : " " + L("health.learner_eta", { d: Math.round(readNumber(p.eta_days)) })),'),
 "M07_unobservable_gone": ('const detail = !inputAssigned(plan, "heat_pump_power_entity") ? L("health.model_unobservable")', 'const detail = false ? L("health.model_unobservable")'),
 "M08_raw_key_label": ('return STRINGS.en[k] !== undefined ? L(k) : null;', 'return STRINGS.en[k] !== undefined ? L(k) : String(key).replace(/_entity$/, "").replace(/_/g, " ");'),
 "M09_valve_number": ('const from = readNumber(attrs.configured_target);\n      if (!Number.isFinite(to) || from === null', 'const from = Number(attrs.configured_target);\n      if (!Number.isFinite(to) || !Number.isFinite(from)'),
 "M10_hover_envelope_only": ('parts.map((p) => `\\n${L(`score.part_${p.key}`)}`).join("")', '(parts[0].drivers ? `\\n${L("score.part_envelope")}` : "")'),
 "M11_unknown_code_raw": ("L(`health.cop_reason_${code}`) : null);", "L(`health.cop_reason_${code}`) : code);"),
 "M12_off_renders": ('if (p.phase === "off") return null;', 'if (p.phase === "off") return undefined;'),
 "M13_drivers_all_parts": ('if (part !== "envelope" && !Array.isArray(drivers)) return "";', ''),
 "M14_measured_age_gone": ('const age = Number.isFinite(at) && at <= Date.now()', 'const age = false'),
 "M15_counting_no_eta": ('eta === null ? "" : L("health.learner_eta"', 'true ? "" : L("health.learner_eta"'),
 "M16_learning_row_static": ('return cop ? copState(cop).reason : scoreReasonText("cop_watch_learning");', 'return "Needs a power meter on the heat pump, then some running time";'),
 "M17_unwatched_normal": ('if (readNumber(c.watched_buckets) > 0 && scale !== null) {', 'if (scale !== null) {'),
 "M18_show_entities_options": ('openHaLink(host, "entities", null);', 'openHaLink(host, "options", null);'),
 "M19_debug_refresh_after_start_off": ('await healthDebugRefresh(host, "start");', 'await healthDebugRefresh(host, "status");'),
}
names = sys.argv[1:] or list(M)
for n in names:
    d = f"{W}/mut_{n}"; shutil.rmtree(d, ignore_errors=True)
    subprocess.run(["git","-C",SRC,"worktree","add","-q","--detach",d,"HEAD"],check=True)
    p = f"{d}/{CARD}"; s = open(p).read(); a,b = M[n]
    c = s.count(a)
    if c != 1: print(f"{n} ANCHOR count={c}", flush=True); continue
    open(p,"w").write(s.replace(a,b))
    env = dict(os.environ, PYTHONPATH="tests/hastub")
    r = subprocess.run(["node","tests/card.mjs"],cwd=d,capture_output=True,text=True,env=env)
    out = r.stdout + r.stderr
    fails = [l.strip() for l in out.splitlines() if re.match(r"\s*(FAIL|not ok|✗)", l) or l.strip().startswith("FAIL")]
    open(f"{W}/ev/{n}.txt","w").write(out)
    print(f"{n} rc={r.returncode} fails={len(fails)} :: " + " | ".join(fails[:6]), flush=True)
    subprocess.run(["git","-C",SRC,"worktree","remove","--force",d])
