// In-memory fix emulation: every P9 instance the grid names at baseline 1936d5ca,
// fixed the way the sweep's perturbations fix the round-9 four, plus the
// instances the grid's reach states found. Used only to show the barrier CAN
// go green on a fixed card; the real fixes are F6.1's.
const rep = (s, a, b) => { if (!s.includes(a)) throw new Error(`anchor missing: ${a.slice(0, 70)}`); return s.split(a).join(b); };
export const FIXES = {
  // D4-s1-01: status text in the readable text token (sweep: status_text_token).
  status_text_token: (s) => rep(rep(rep(s,
    "color: var(--success-color, #2fae7a);", "color: var(--primary-text-color);"),
    "color: var(--error-color, #e0544e);\n      }\n      @media", "color: var(--primary-text-color);\n      }\n      @media"),
    "color: var(--warning-color, #d98e00);", "color: var(--primary-text-color);"),
  // D4-s1-01 sibling + new .sp-save.confirm: white on a red that clears 4.5:1.
  confirm_fill: (s) => rep(rep(s,
    "      .whatif .wi-save.confirm {\n        border-color: var(--error-color, #e0544e);\n        background: var(--error-color, #e0544e);",
    "      .whatif .wi-save.confirm {\n        border-color: #b3261e;\n        background: #b3261e;"),
    "      .sp-save.confirm {\n        border-color: var(--error-color, #e0544e) !important;\n        background: var(--error-color, #e0544e);",
    "      .sp-save.confirm {\n        border-color: #b3261e !important;\n        background: #b3261e;"),
  // D4-s1-02 (sweep: menu_clamp).
  menu_clamp: (s) => rep(s, "    host.appendChild(menu);\n",
    "    host.appendChild(menu);\n    menu.style.left = `${Math.max(0, Math.min(parseFloat(menu.style.left), host.clientWidth - menu.offsetWidth))}px`;\n"),
  // D4-s1-03 (sweep: picker_wrap).
  picker_wrap: (s) => rep(s, "      .sp-filter {\n        box-sizing: border-box; margin-bottom: 0.4em;",
    "      .sp-select option { white-space: normal; overflow-wrap: anywhere; }\n      .sp-filter {\n        box-sizing: border-box; margin-bottom: 0.4em;"),
  // D4-s1-05 (sweep: now_temp_below).
  now_temp_below: (s) => rep(s, '`<text class="now-temp" x="${plotL + 6}" y="${plotT + font}"',
    '`<text class="now-temp" x="${plotL + 6}" y="${plotT + 2 * font + 4}"'),
  // New (grid reach): the estimated-prices label, two lines lower and in the text token.
  estimated_label: (s) => rep(s, '`<text x="${ex + 4}" y="${plotT + font + 4}" font-size="${font}" fill="var(--secondary-text-color,#888)">',
    '`<text x="${ex + 4}" y="${plotT + 3 * font + 8}" font-size="${font}" fill="var(--primary-text-color,#212121)">'),
  // New (grid reach): two neighbours grow into one gap by at most half of it each.
  slot_hit_half_gap: (s) => rep(rep(s,
    "          const roomL = Math.max(0, x1 - limitL);", "          const roomL = Math.max(0, x1 - limitL) / 2;"),
    "          const roomR = Math.max(0, limitR - x2);", "          const roomR = Math.max(0, limitR - x2) / 2;"),
};
const only = process.env.P9_FIXES ? process.env.P9_FIXES.split(",") : Object.keys(FIXES);
const skip = process.env.P9_SKIP ? process.env.P9_SKIP.split(",") : [];
export default (s) => only.filter((k) => !skip.includes(k)).reduce((acc, k) => FIXES[k](acc), s);
