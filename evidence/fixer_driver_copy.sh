#!/bin/bash
# Round-2 plants from #2283's review: R4 entry ignored, R5 anchor href, R6 hass-more-info event.
cd /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-deeplink3/wt || exit 2
F=custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
:
echo "head $(git rev-parse HEAD)"
plant() { python3 -c "
import sys; p='$F'; s=open(p).read(); old, new = sys.argv[1], sys.argv[2]
assert s.count(old)==1, 'anchor not unique: '+old[:50]
open(p,'w').write(s.replace(old,new))" "$1" "$2"; }
run() { echo "== $1"; git diff --stat | tail -1; node tests/card.mjs 2>&1 | grep -A1 "^  FAIL" | sed 's/^/    /'; git checkout -q -- $F; }
plant '`${SETTINGS_PATH}#${q("config_entry", entryId)}`' 'SETTINGS_PATH'; run "M1 options drops #config_entry"
plant '}&${q("more-info-view", "settings")}`' '}`'; run "M2 entity drops the settings view"
cp tests/card.mjs /dev/null
python3 -c "
p='tests/card.mjs'; s=open(p).read(); old='    \"advisor:settings\": { group: \"R10-ADVISOR\", path: BARE },\n'
assert s.count(old)==1; open(p,'w').write(s.replace(old,''))"; echo "== M3 delete the advisor PENDING row"; git diff --stat | tail -1; node tests/card.mjs 2>&1 | grep -A1 "^  FAIL" | sed 's/^/    /'; git checkout -q -- tests/card.mjs
plant 'function healthPageHtml(host) {' 'function unreachedLink(host) { openHaLink(host, "entities"); }

function healthPageHtml(host) {'; run "M4 a link site no press reaches"
plant '    this.pickerFocus = !!viaKeyboard;' '    this.pickerFocus = false;'; run "M5 openPicker hands no focus"
plant '        navigateTo(SETTINGS_PATH);' '        await openHaLink(host, "options");'; run "M6 convert advisor settings (stale row)"
plant '    entryId = (reg && reg.config_entry_id) || null;' '    entryId = null;'; run "R4 entry ignored"
plant '<button type="button" class="adv-act" data-act="diagnostics">' '<a href="/config/integrations/integration/heatpump_optimizer">open</a><button type="button" class="adv-act" data-act="diagnostics">'; run "R5 anchor href"
plant '        navigateTo(SETTINGS_PATH);' '        host.dispatchEvent(new CustomEvent("hass-more-info", { detail: { entityId: "sensor.x" }, bubbles: true, composed: true }));'; run "R6 hass-more-info event"
# The event plants below assemble the type at run time, so the static regex
# cannot see them: each proves the dynamic sink on its own.
# R6b: a pending button keeps its unconverted path AND fires the event; the
# reach check still finds the navigateTo line, so only the sink can catch it.
plant '        navigateTo(SETTINGS_PATH);' '        navigateTo(SETTINGS_PATH); host.dispatchEvent(new CustomEvent(["hass", "more", "info"].join("-"), { detail: { entityId: "sensor.x" }, bubbles: true, composed: true }));'; run "R6b pending button fires hass-more-info too (runtime type)"
# R6c: the reviewer's shape, on the non-pending Assign branch.
plant '        openSetupSlot(host, btn.dataset.key, ev);' '        host.dispatchEvent(new CustomEvent(["hass", "more", "info"].join("-"), { detail: { entityId: "sensor.x" }, bubbles: true, composed: true }));'; run "R6c Assign fires hass-more-info (runtime type)"
# Round 3: an anchor's link written with setAttribute (R7b, the reviewer's plant verbatim).
plant2() { python3 -c "
import sys; p='$F'; s=open(p).read()
for old, new in zip(sys.argv[1::2], sys.argv[2::2]):
    assert s.count(old)==1, 'anchor not unique: '+old[:50]
    s=s.replace(old,new)
open(p,'w').write(s)" "$@"; }
LOOP='  for (const btn of root.querySelectorAll(".adv-act")) {
    btn.addEventListener("click", async (ev) => {'
DIAG='<button type="button" class="adv-act" data-act="diagnostics">'
plant2 "$DIAG" "<a class=\"zz\"></a>$DIAG" "$LOOP" "  for (const a of root.querySelectorAll(\"a.zz\")) a.setAttribute(\"href\", \"/config/integrations/integration/heatpump_optimizer\");
$LOOP"; run "R7b setAttribute(\"href\") on a.zz at attach (literal; the stub never resolves a.zz)"
# R7c: the same at attach, through a selector the stub resolves and an attribute
# name assembled at run time, so only the dynamic read can see it.
plant2 "$DIAG" "<a class=\"zz\"></a>$DIAG" "$LOOP" "  for (const a of root.querySelectorAll(\".zz\")) a.setAttribute([\"hr\", \"ef\"].join(\"\"), \"/config/integrations/integration/heatpump_optimizer\");
$LOOP"; run "R7c setAttribute(runtime name) on .zz at attach"
# R7d: written inside the click handler, so only the after-press walk sees it.
plant2 "$DIAG" "<a class=\"zz\"></a>$DIAG" '      stop(ev);
      const act = btn.dataset.act;' '      stop(ev);
      for (const a of root.querySelectorAll(".zz")) a.setAttribute(["hr", "ef"].join(""), "/config/integrations/integration/heatpump_optimizer");
      const act = btn.dataset.act;'; run "R7d setAttribute(runtime name) on .zz at click time"
git status --short
