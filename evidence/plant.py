"""Reviewer's own plant harness (built by the reviewer): copies the card into a temp root, applies one plant,
prints the finder's card_shapes total and the archscore card metrics under a given instrument."""
import sys, json, shutil, subprocess, tempfile
from pathlib import Path
inst, src_tree, which = sys.argv[1], sys.argv[2], sys.argv[3]
REL = "custom_components/heatpump_optimizer/www"
ANCHOR = "  const now = Number(opts.now);\n"
PLANTS = {
 "none": "",
 "finder3": ('  const lv = opts.live || {};\n'
             '  if (lv.state === "unavailable" || lv.state === "unknown") return out;\n'
             '  const rw = opts.raw;\n'
             '  if (rw === null || rw === undefined || rw === "") return out;\n'
             '  if (typeof opts.now === "number" && Number.isFinite(opts.now)) out.push(null);\n'),
 "live1": '  const lv = opts.live || {};\n  if (lv.state === "unavailable" || lv.state === "unknown") return out;\n',
 "null1": '  const rw = opts.raw;\n  if (rw === null || rw === undefined || rw === "") return out;\n',
 "fin1": '  if (typeof opts.now === "number" && Number.isFinite(opts.now)) out.push(null);\n',
 "fin1_reordered": '  if (Number.isFinite(opts.now) && typeof opts.now === "number") out.push(null);\n',
 "null_loose": '  if (opts.raw == null) return out;\n',
 "state_sig1": '  const sx = opts.st;\n  const sig = sx ? `${sx.state}@${sx.last_updated || ""}` : "-";\n',
 "picker1": '  this.pickerFocus = !!opts.kb;\n',
 "charw1": '  const wpx = opts.label.length * CHAR_WIDTH_EM;\n',
 "noplan1": '  const empty = `<div class="empty">${L("errors.no_plan_data")}</div>`;\n',
 "null_unrelated": '  const span = out.length * 2 + now;\n',
 "null_distinct_rule": '  if (opts.kind === "dhw_overlay" || opts.kind === "dhw_window") return out;\n',
 "null_identical_stmt": '  const v = Number(opts.probe);\n',
 "null_comment": ('  // if (lv.state === "unavailable" || lv.state === "unknown") return out;\n'
                  '  /* if (opts.raw === null || opts.raw === undefined || opts.raw === "") return out; */\n'),
 "null_docstring": '  /** typeof opts.now === "number" && Number.isFinite(opts.now) */\n',
 "null_string": ('  const note = \'x.state === "unavailable" || x.state === "unknown"\';\n'),
}
with tempfile.TemporaryDirectory() as d:
    dst = Path(d) / REL
    shutil.copytree(Path(src_tree) / REL, dst)
    card = dst / "heatpump-optimizer-card.js"
    s = card.read_text(); assert s.count(ANCHOR) == 1
    card.write_text(s.replace(ANCHOR, ANCHOR + PLANTS[which]))
    fin = subprocess.run(["node", str(Path.home()/"finder/card_shapes.mjs"), str(card)], capture_output=True, text=True).stdout
    total = [l for l in fin.splitlines() if l.startswith("RESULT total=")][0].split()[1]
    sys.path.insert(0, inst + "/tools/audit")
    from archscore.metrics import card as K
    r = K.measure(Path(d))
    print(f"RESULT plant={which} finder_{total} card_clone_copies={r['card_clone_copies']} "
          f"card_dead_definitions={r['card_dead_definitions']} card_rule_copies={r.get('card_rule_copies')}")
