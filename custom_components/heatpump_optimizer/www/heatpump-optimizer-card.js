/*
 * heatpump-optimizer-card
 *
 * A self-contained Lovelace custom card that plots the Heat Pump Cost
 * Optimizer planning series (electricity price, heating power, temperatures)
 * on a single shared time axis with per-series legend toggles.
 *
 * No build step, no npm, no external dependencies. The chart is drawn as
 * hand-written inline SVG inside a shadow root.
 */

const CARD_TAG = "heatpump-optimizer-card";
const CARD_VERSION = "3.1.2";

const DEFAULTS = {
  title: "Heat pump plan",
  // Entity ids are derived from the device name ("Heat Pump Optimizer"), since
  // the plan sensors use has_entity_name. These are the ids a default install
  // produces; if they are absent the card auto-discovers by the `plan_kind`
  // attribute, so a renamed entity still works with no config change.
  space_entity: "sensor.heat_pump_optimizer_space_heating_plan",
  dhw_entity: "sensor.heat_pump_optimizer_dhw_heating_plan",
  solar_entity: "sensor.heat_pump_optimizer_solar_irradiance",
  hours: 24,
  // The schedule editor lives in the expanded view. On by default: opening it
  // and editing costs nothing, because the draft is held in the card. Only the
  // "Simulate" button runs a solve on the Home Assistant host, and only "Save"
  // changes any configuration. Set `what_if: false` to hide the panel entirely.
  what_if: true,
};

// Series metadata. `axis` selects one of four value axes: temp / power / price
// / solar. `sensor` selects which forecast the values come from ("space",
// "dhw", "solar", or "either" meaning prefer space then fall back to dhw).
// `field` is the forecast attribute key. Colours are fixed and chosen to read
// on light + dark themes.
const SERIES_DEFS = [
  {
    key: "price",
    label: "Electricity price",
    axis: "price",
    unit: "SEK/kWh",
    color: "#f5a623",
    sensor: "either",
    field: "price",
    style: "stepArea",
  },
  {
    key: "dhw_slots",
    label: "DHW heating",
    axis: "power",
    unit: "kW",
    color: "#e0544e",
    sensor: "dhw",
    field: "dhw_power",
    style: "stepBars",
  },
  {
    key: "space_slots",
    label: "Space heating",
    axis: "power",
    unit: "kW",
    color: "#4a90e2",
    sensor: "space",
    field: "space_power",
    style: "stepBars",
  },
  {
    key: "outdoor",
    label: "Outdoor temperature",
    axis: "temp",
    unit: "\u00b0C",
    color: "#7d8794",
    sensor: "either",
    field: "outdoor",
    style: "smooth",
  },
  {
    key: "dhw_temp",
    label: "DHW tank temperature",
    axis: "temp",
    unit: "\u00b0C",
    color: "#c264d0",
    sensor: "dhw",
    field: "dhw_temp",
    style: "smooth",
  },
  {
    key: "house_temp",
    label: "House temperature",
    axis: "temp",
    unit: "\u00b0C",
    color: "#2fae7a",
    sensor: "space",
    field: "room",
    extra: ["upper", "lower"],
    style: "smooth",
  },
  {
    // W/m² is a fourth unit, and both plot edges were already occupied, so it
    // gets an inner right-hand axis that only appears when the series is on.
    // Scaling it into the power axis as kW/m² was the alternative, but a
    // 0.8 kW/m² line sharing a scale with a 5 kW compressor is unreadable.
    key: "solar",
    label: "Solar irradiance",
    axis: "solar",
    unit: "W/m\u00b2",
    color: "#f2c94c",
    sensor: "solar",
    field: "ghi",
    style: "stepArea",
  },
];

const VIEW_W = 900;
const VIEW_H = 380;
// Aspect ratio of the plot, used to size the dialog so the chart fills it
// without the non-uniform scaling that would distort the axis labels.
const VIEW_RATIO = VIEW_W / VIEW_H;
const EXPAND_ICON =
  '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">' +
  '<path fill="currentColor" d="M10 21v-2H6.4l4.5-4.5-1.4-1.4L5 17.6V14H3v7h7zm4-18v2h3.6l-4.5 4.5 1.4 1.4L19 6.4V10h2V3h-7z"/></svg>';
const CLOSE_ICON =
  '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
  '<path fill="currentColor" d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';
const MARGIN = { top: 16, right: 62, bottom: 34, left: 92 };
// When the irradiance series is on, the right margin has to make room for a
// second axis inside the price one.
const SOLAR_AXIS_INSET = 46;
const MARGIN_RIGHT_WITH_SOLAR = MARGIN.right + SOLAR_AXIS_INSET;

// The chart is drawn in a fixed 900x380 coordinate system and stretched to
// whatever width it is given, so text sized in these units already grows with
// the chart: the same label renders around 6px in a dashboard column and around
// 20px once the chart fills a dialog. That scaling is wanted and is not what
// these constants control.
//
// What they must respect is the layout. Every position in the chart -- the
// margins above, the axis tick spacing, the legend rows -- is authored in the
// same units against a font of roughly this size. Raising the font without
// moving everything else makes labels collide, so treat these as part of the
// geometry rather than as a free preference.
const FONT_BASE = 10;
const FONT_EXPANDED = 15;

// Estimating how wide a rendered label will be, so labels can be thinned out
// before they collide. Characters of the default sans-serif face average a
// little over half an em at the sizes this chart uses.
const CHAR_WIDTH_EM = 0.55;
// Label intervals that divide 24, so labels fall on the same clock times every
// day instead of drifting across midnight.
const TIME_LABEL_STEPS = [1, 2, 3, 4, 6, 8, 12, 24];

// The expanded dialog's chrome is sized from one font size, set from the
// dialog's measured width so it grows with the chart it sits beside.
const DIALOG_FONT_RATIO = 0.0105;
const DIALOG_FONT_PX_MIN = 12;
const DIALOG_FONT_PX_MAX = 21;

// Human-readable labels for the plan reason codes the optimizer publishes.
// Without these an unexpected slot is indistinguishable from a bug.
const REASON_LABELS = {
  comfort_floor: "Holding the minimum temperature",
  cheap_price: "Cheapest hours",
  preheat_weather: "Pre-heating before colder weather",
  terminal_value: "Leaving the house warm past the horizon",
  solar_surplus: "Using solar surplus",
  recovery: "Warming up before you return",
  dhw_window: "Hot water needed now",
  dhw_ready: "Getting the tank ready for a demand window",
  dhw_preheat: "Charging the tank while electricity is cheap",
  legionella: "Anti-legionella cycle",
  peak_avoidance: "Staying under the capacity tariff peak",
  idle: "Not heating",
};

/** Stop a click inside the panel from reaching the card's expand handler. */
function stop(ev) {
  if (ev && typeof ev.stopPropagation === "function") ev.stopPropagation();
}

/** True when two measured widths differ enough to be worth re-rendering for.
 *
 * Sub-pixel jitter from fractional layout would otherwise re-render on every
 * resize callback for no visible gain.
 */
function significantlyDifferent(next, previous) {
  if (!next) return false;
  if (!previous) return true;
  return Math.abs(next - previous) > 1.5;
}

/** "7" -> "07:00", for a time input. */
function hhmm(hour) {
  const h = Math.max(0, Math.min(23, Math.round(Number(hour) || 0)));
  return `${String(h).padStart(2, "0")}:00`;
}

/** "07:30" -> 7.5, or `fallback` when it is not a time. */
function hourOf(value, fallback) {
  const m = /^(\d{1,2}):(\d{2})$/.exec(String(value || "").trim());
  if (!m) return fallback;
  const h = Number(m[1]);
  const min = Number(m[2]);
  if (h > 23 || min > 59) return fallback;
  return h + min / 60;
}

/** '06:00-08:30, 17:00-22:00' -> [{start,end}, ...] */
function parseWindows(spec) {
  if (typeof spec !== "string" || !spec.trim()) return [];
  const out = [];
  for (const part of spec.split(",")) {
    const m = /^\s*(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\s*$/.exec(part);
    if (m) out.push({ start: m[1], end: m[2] });
  }
  return out;
}

/** The inverse, in the format the integration's parser expects. */
function formatWindows(windows) {
  return (windows || [])
    .map((w) => `${w.start}-${w.end}`)
    .join(", ");
}

function esc(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function niceNum(range, round) {
  const exponent = Math.floor(Math.log10(range || 1));
  const fraction = range / Math.pow(10, exponent);
  let niceFraction;
  if (round) {
    if (fraction < 1.5) niceFraction = 1;
    else if (fraction < 3) niceFraction = 2;
    else if (fraction < 7) niceFraction = 5;
    else niceFraction = 10;
  } else {
    if (fraction <= 1) niceFraction = 1;
    else if (fraction <= 2) niceFraction = 2;
    else if (fraction <= 5) niceFraction = 5;
    else niceFraction = 10;
  }
  return niceFraction * Math.pow(10, exponent);
}

// Return { min, max, ticks[] } for a "nice" axis covering [lo, hi].
function niceAxis(lo, hi, maxTicks) {
  if (!isFinite(lo) || !isFinite(hi)) return { min: 0, max: 1, ticks: [0, 1] };
  if (lo === hi) {
    lo -= 1;
    hi += 1;
  }
  const range = niceNum(hi - lo, false);
  const step = niceNum(range / Math.max(1, maxTicks - 1), true);
  const niceMin = Math.floor(lo / step) * step;
  const niceMax = Math.ceil(hi / step) * step;
  const ticks = [];
  for (let v = niceMin; v <= niceMax + step * 0.5; v += step) {
    ticks.push(Math.round(v * 1e6) / 1e6);
  }
  return { min: niceMin, max: niceMax, ticks };
}

function fmtTick(v) {
  if (Math.abs(v) >= 10) return v.toFixed(0);
  if (Number.isInteger(v)) return String(v);
  return v.toFixed(1);
}

class HeatpumpOptimizerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
    this._sig = null;
    this._hidden = {}; // key -> true when hidden
    this._series = [];
    this._plot = null;
    this._resizeObserver = null;
    this._expanded = false;
    // What-if simulator state (item 21). Kept on the instance so a re-render
    // triggered by a data refresh does not reset the slider under the user.
    this._whatIf = null;
    this._whatIfTimer = null;
    this._pendingSave = false;
    this._saveTimer = null;
    this._dialogFontPx = 0;
    this._onLegendClick = this._onLegendClick.bind(this);
    this._onPointerMove = this._onPointerMove.bind(this);
    this._onPointerLeave = this._onPointerLeave.bind(this);
    this._onCardClick = this._onCardClick.bind(this);
    this._onExpandClick = this._onExpandClick.bind(this);
    this._onDialogClick = this._onDialogClick.bind(this);
    this._onDialogClose = this._onDialogClose.bind(this);
    this._onWhatIfInput = this._onWhatIfInput.bind(this);
    this._onSlotEdit = this._onSlotEdit.bind(this);
    this._onAddWindow = this._onAddWindow.bind(this);
    this._onRemoveWindow = this._onRemoveWindow.bind(this);
    this._onApplySlots = this._onApplySlots.bind(this);
    this._onSaveSchedule = this._onSaveSchedule.bind(this);
    this._onResetWhatIf = this._onResetWhatIf.bind(this);
  }

  // ---- Lovelace contract -------------------------------------------------

  setConfig(config) {
    if (config === null || typeof config !== "object") {
      throw new Error("heatpump-optimizer-card: configuration must be an object");
    }
    const cfg = { ...DEFAULTS, ...config };

    if (typeof cfg.space_entity !== "string" || !cfg.space_entity.includes(".")) {
      throw new Error(
        "heatpump-optimizer-card: 'space_entity' must be an entity id string"
      );
    }
    if (typeof cfg.dhw_entity !== "string" || !cfg.dhw_entity.includes(".")) {
      throw new Error(
        "heatpump-optimizer-card: 'dhw_entity' must be an entity id string"
      );
    }
    if (typeof cfg.solar_entity !== "string" || !cfg.solar_entity.includes(".")) {
      throw new Error(
        "heatpump-optimizer-card: 'solar_entity' must be an entity id string"
      );
    }
    if (typeof cfg.what_if !== "boolean") {
      throw new Error("heatpump-optimizer-card: 'what_if' must be true or false");
    }
    const hours = Number(cfg.hours);
    if (!Number.isFinite(hours) || hours <= 0 || hours > 168) {
      throw new Error(
        "heatpump-optimizer-card: 'hours' must be a number between 1 and 168"
      );
    }
    cfg.hours = hours;
    if (cfg.title !== undefined && typeof cfg.title !== "string") {
      throw new Error("heatpump-optimizer-card: 'title' must be a string");
    }
    if (cfg.series !== undefined) {
      if (typeof cfg.series !== "object" || cfg.series === null) {
        throw new Error("heatpump-optimizer-card: 'series' must be a map");
      }
      for (const k of Object.keys(cfg.series)) {
        if (!SERIES_DEFS.some((s) => s.key === k)) {
          throw new Error(
            `heatpump-optimizer-card: unknown series '${k}' in 'series'`
          );
        }
        if (typeof cfg.series[k] !== "boolean") {
          throw new Error(
            `heatpump-optimizer-card: series '${k}' visibility must be true or false`
          );
        }
      }
    }

    this._config = cfg;
    this._hidden = this._loadHidden(cfg);
    this._sig = null; // force re-render on next hass
    if (this._hass) this._maybeRender(true);
  }

  set hass(hass) {
    this._hass = hass;
    this._maybeRender(false);
  }

  get hass() {
    return this._hass;
  }

  getCardSize() {
    return 8;
  }

  static getStubConfig() {
    return {
      type: `custom:${CARD_TAG}`,
      space_entity: DEFAULTS.space_entity,
      dhw_entity: DEFAULTS.dhw_entity,
    };
  }

  connectedCallback() {
    if (typeof ResizeObserver !== "undefined" && !this._resizeObserver) {
      this._resizeObserver = new ResizeObserver(() => {
        // Width changes don't alter the viewBox model, but refreshing the
        // cached bounding rect keeps hover geometry accurate after layout.
        this._cacheRect();
      });
      try {
        this._resizeObserver.observe(this);
      } catch (e) {
        /* ignore */
      }
    }
  }

  disconnectedCallback() {
    // A modal dialog left open would outlive the card in the top layer.
    if (this._expanded) this._closeExpandedQuietly();
    // A pending what-if solve would otherwise fire after the card is gone,
    // spending seconds of coordinator CPU to write into a detached DOM.
    if (this._whatIfTimer) {
      clearTimeout(this._whatIfTimer);
      this._whatIfTimer = null;
    }
    // Likewise an armed save confirmation: it must not survive the card.
    if (this._saveTimer) {
      clearTimeout(this._saveTimer);
      this._saveTimer = null;
    }
    this._pendingSave = false;
    if (this._resizeObserver) {
      try {
        this._resizeObserver.disconnect();
      } catch (e) {
        /* ignore */
      }
      this._resizeObserver = null;
    }
  }

  // ---- persistence -------------------------------------------------------

  _storageKey(cfg) {
    return `${CARD_TAG}:${cfg.space_entity}:${cfg.dhw_entity}`;
  }

  _loadHidden(cfg) {
    const hidden = {};
    // Config-provided initial visibility (false => hidden).
    if (cfg.series) {
      for (const [k, v] of Object.entries(cfg.series)) {
        if (v === false) hidden[k] = true;
      }
    }
    // localStorage overrides config so user toggles survive reloads.
    try {
      if (typeof localStorage !== "undefined") {
        const raw = localStorage.getItem(this._storageKey(cfg));
        if (raw) {
          const saved = JSON.parse(raw);
          if (saved && typeof saved === "object") {
            for (const s of SERIES_DEFS) {
              if (typeof saved[s.key] === "boolean") {
                hidden[s.key] = saved[s.key];
              }
            }
          }
        }
      }
    } catch (e) {
      /* ignore malformed storage */
    }
    return hidden;
  }

  _saveHidden() {
    try {
      if (typeof localStorage !== "undefined" && this._config) {
        localStorage.setItem(
          this._storageKey(this._config),
          JSON.stringify(this._hidden)
        );
      }
    } catch (e) {
      /* ignore quota / disabled storage */
    }
  }

  // ---- data extraction ---------------------------------------------------

  // Resolve which entity to read for a plan kind ("space" | "dhw").
  //
  // Entity ids are not a stable contract: they are derived from the device
  // name and the user can rename them. So the configured id wins if it exists,
  // otherwise fall back to discovering the sensor that advertises the matching
  // `plan_kind` attribute, and finally to a naming-convention match for
  // integration versions predating that attribute.
  _resolveEntity(kind) {
    const cfg = this._config;
    const configured =
      kind === "space"
        ? cfg.space_entity
        : kind === "dhw"
        ? cfg.dhw_entity
        : cfg.solar_entity;
    if (!this._hass || !this._hass.states) return configured;
    const states = this._hass.states;
    if (states[configured]) return configured;

    if (!this._resolvedCache) this._resolvedCache = {};
    const cached = this._resolvedCache[kind];
    if (cached && states[cached]) return cached;

    const suffix =
      kind === "space"
        ? "space_heating_plan"
        : kind === "dhw"
        ? "dhw_heating_plan"
        : "solar_irradiance";
    let byMarker = null;
    let bySuffix = null;
    for (const id of Object.keys(states).sort()) {
      if (!id.startsWith("sensor.")) continue;
      const attrs = states[id].attributes || {};
      if (attrs.plan_kind === kind) {
        byMarker = id;
        break;
      }
      if (bySuffix === null && id.endsWith(suffix)) bySuffix = id;
    }
    const found = byMarker || bySuffix;
    if (found) {
      this._resolvedCache[kind] = found;
      return found;
    }
    return configured;
  }

  _stateOf(entityId) {
    if (!this._hass || !this._hass.states) return undefined;
    return this._hass.states[entityId];
  }

  _forecast(entityId) {
    const st = this._stateOf(entityId);
    if (!st || st.state === "unavailable" || st.state === "unknown") return null;
    const attrs = st.attributes || {};
    let fc = attrs.forecast;
    if (typeof fc === "string") {
      try {
        fc = JSON.parse(fc);
      } catch (e) {
        return null;
      }
    }
    if (!Array.isArray(fc)) return null;
    return fc;
  }

  _signature() {
    const cfg = this._config;
    const spId = this._resolveEntity("space");
    const dhwId = this._resolveEntity("dhw");
    const solarId = this._resolveEntity("solar");
    const space = this._stateOf(spId);
    const dhw = this._stateOf(dhwId);
    const solar = this._stateOf(solarId);
    const spFc = this._forecast(spId);
    const dhwFc = this._forecast(dhwId);
    const solarFc = this._forecast(solarId);
    return [
      spId,
      dhwId,
      solarId,
      cfg.hours,
      cfg.title,
      space ? space.last_updated : "-",
      space ? space.state : "-",
      dhw ? dhw.last_updated : "-",
      dhw ? dhw.state : "-",
      solar ? solar.last_updated : "-",
      spFc ? spFc.length : -1,
      dhwFc ? dhwFc.length : -1,
      solarFc ? solarFc.length : -1,
      JSON.stringify(this._hidden),
    ].join("|");
  }

  _maybeRender(force) {
    if (!this._config || !this._hass) return;
    const sig = this._signature();
    if (!force && sig === this._sig) return;
    this._sig = sig;
    this._render();
  }

  // Build this._series from the current forecasts.
  _buildSeries() {
    const cfg = this._config;
    const spFc = this._forecast(this._resolveEntity("space")) || [];
    const dhwFc = this._forecast(this._resolveEntity("dhw")) || [];
    // The irradiance sensor publishes its own horizon. Its timestamps are
    // already interval *starts* — `_solar_forecast_view` converts Open-Meteo's
    // end-of-interval stamps on the way out — so they must not be shifted again.
    const solarFc = this._forecast(this._resolveEntity("solar")) || [];

    const now = Date.now();
    let windowStart = now;
    let windowEnd = now + cfg.hours * 3600 * 1000;

    const parse = (p) => {
      const t = Date.parse(p.t);
      return Number.isNaN(t) ? null : t;
    };

    // Determine whether any data actually falls inside [now, now+hours]. If not
    // (e.g. purely historical or test data), fall back to the full extent so the
    // card still shows something instead of an empty plot.
    const allTimes = [];
    for (const p of spFc) {
      const t = parse(p);
      if (t !== null) allTimes.push(t);
    }
    for (const p of dhwFc) {
      const t = parse(p);
      if (t !== null) allTimes.push(t);
    }
    const inWindow = allTimes.some((t) => t >= windowStart && t <= windowEnd);
    if (!inWindow && allTimes.length) {
      windowStart = Math.min(...allTimes);
      windowEnd = Math.min(
        Math.max(...allTimes),
        windowStart + cfg.hours * 3600 * 1000
      );
    }

    const pick = (sensor) =>
      sensor === "dhw" ? dhwFc : sensor === "solar" ? solarFc : spFc;
    const either = (field) => {
      // prefer space forecast, fall back to dhw
      if (spFc.some((p) => p[field] !== undefined && p[field] !== null))
        return spFc;
      return dhwFc;
    };

    const series = [];
    for (const def of SERIES_DEFS) {
      const fc = def.sensor === "either" ? either(def.field) : pick(def.sensor);
      const lines = [];
      const fields = [def.field].concat(def.extra || []);
      for (const field of fields) {
        const pts = [];
        for (const p of fc) {
          const t = parse(p);
          if (t === null) continue;
          if (t < windowStart || t > windowEnd) continue;
          const v = p[field];
          if (v === null || v === undefined || Number.isNaN(Number(v))) continue;
          pts.push({
            t,
            v: Number(v),
            // Reason codes and price provenance ride along on the point so the
            // tooltip can explain a slot without a second lookup.
            reason: p.reason,
            priceKnown: p.price_known,
          });
        }
        pts.sort((a, b) => a.t - b.t);
        if (pts.length) {
          lines.push({ field, points: pts, primary: field === def.field });
        }
      }
      series.push({
        ...def,
        lines,
        hasData: lines.length > 0,
        visible: !this._hidden[def.key],
      });
    }

    return { series, windowStart, windowEnd };
  }

  // ---- rendering ---------------------------------------------------------

  // Explain precisely why a plan is missing. "Waiting for an entity" is not
  // actionable when the real problem is that the entity is named something
  // else, so distinguish not-found from present-but-empty.
  _diagnose(kind) {
    const id = this._resolveEntity(kind);
    const label = kind === "space" ? "Space heating" : "DHW";
    const st = this._stateOf(id);
    if (!st) {
      return `${label}: no entity found. Looked for <code>${esc(id)}</code>.
        Check the entity id in Developer Tools &gt; States and set
        <code>${kind}_entity</code> in the card config.`;
    }
    if (st.state === "unavailable" || st.state === "unknown") {
      return `${label}: <code>${esc(id)}</code> is ${esc(st.state)}.`;
    }
    const fc = this._forecast(id);
    if (!fc) {
      return `${label}: <code>${esc(id)}</code> has no forecast attribute yet.
        It appears after the first optimization run.`;
    }
    if (!fc.length) {
      return `${label}: <code>${esc(id)}</code> published an empty forecast.`;
    }
    return `${label}: <code>${esc(id)}</code> has ${fc.length} points, but none
      fall in the selected window.`;
  }

  _render() {
    const cfg = this._config;
    const built = this._buildSeries();
    this._series = built.series;

    const anyData = this._series.some((s) => s.hasData);

    const style = this._styleBlock();
    const legend = this._legendHtml();

    let body;
    if (!anyData) {
      body = `<div class="empty">No plan data available yet.<br>
        ${this._diagnose("space")}<br>
        ${this._diagnose("dhw")}</div>`;
      this._plot = null;
    } else {
      body = this._chartBlock(built, false);
    }

    // The dialog is a sibling of ha-card, not a child, so a click inside it
    // never bubbles into the card's own open-on-click handler.
    const dialog = this._expanded && anyData ? this._dialogHtml(built) : "";

    this.shadowRoot.innerHTML = `
      <ha-card class="${anyData ? "clickable" : ""}">
        ${style}
        <div class="header">
          <span class="title">${esc(cfg.title)}</span>
          ${
            anyData
              ? `<button type="button" class="expand" title="Enlarge"
                   aria-label="Enlarge chart">${EXPAND_ICON}</button>`
              : ""
          }
        </div>
        ${legend}
        ${body}
      </ha-card>
      ${dialog}
    `;

    this._attachChartEvents(this.shadowRoot);

    const expandBtn = this.shadowRoot.querySelector(".expand");
    if (expandBtn) expandBtn.addEventListener("click", this._onExpandClick);

    const card = this.shadowRoot.querySelector("ha-card");
    if (card && anyData) card.addEventListener("click", this._onCardClick);

    this._syncDialog();
    this._cacheRect();
  }
  /** Chart markup plus the tooltip that belongs to it.
   *
   * The tooltip lives inside the wrapper rather than beside it so that the two
   * copies of the chart, inline and expanded, each own theirs. Positioning it
   * against the wrapper also removes a dependency on `ha-card` happening to be
   * a positioned ancestor.
   */
  _chartBlock(built, expanded) {
    const chart = this._chartSvg(built, expanded);
    return `<div class="chartwrap${expanded ? " big" : ""}">${chart}
      <div class="tooltip" hidden></div></div>`;
  }

  _dialogHtml(built) {
    const cfg = this._config;
    return `
      <dialog class="expanded" aria-label="${esc(cfg.title)}">
        <div class="dlg-head">
          <span class="title">${esc(cfg.title)}</span>
          <button type="button" class="close" title="Close"
            aria-label="Close">${CLOSE_ICON}</button>
        </div>
        ${this._legendHtml()}
        ${this._chartBlock(built, true)}
        ${this._whatIfHtml()}
      </dialog>
    `;
  }

  /** The what-if simulator, shown in the expanded view only.
   *
   * Setpoints and time slots are normally chosen blind: the optimizer can
   * price a plan, but the user never sees the price of their own comfort
   * choices. Here they can change the comfort temperature, the hours the house
   * is heated to it, and the hot water demand windows, and see what each would
   * cost per month.
   *
   * Everything runs against a *copy* of the configuration on the coordinator
   * side, so exploring here cannot disturb actual operation. The temperature
   * slider is debounced; the slot editors are applied on an explicit button,
   * because editing a time range is not a drag gesture and half-typed times
   * should not trigger a solve.
   *
   * Saving is a separate, deliberate step. Once a user has found a schedule
   * they prefer, "Save as my schedule" writes it into the config entry through
   * the `apply_schedule` service — the only way anything here reaches real
   * configuration, and it asks for confirmation first.
   */
  _whatIfHtml() {
    if (!this._config.what_if) return "";
    const draft = this._whatIfDraft();
    const windows = draft.dhwWindows;
    return `
      <div class="whatif">
        <div class="wi-row">
          <label class="wi-field">
            <span>Comfort temperature</span>
            <input type="range" class="wi-temp" min="16" max="24" step="0.5"
              value="${draft.comfort}" aria-label="Comfort temperature">
            <span class="wi-value">${draft.comfort.toFixed(1)}&nbsp;°C</span>
          </label>
        </div>

        <div class="wi-row wi-slots">
          <div class="wi-group">
            <div class="wi-group-title">Heating hours</div>
            <label class="wi-field">
              <span>Day from</span>
              <input type="time" class="wi-day-start" step="3600"
                value="${hhmm(draft.dayStart)}" aria-label="Heating day starts">
            </label>
            <label class="wi-field">
              <span>to</span>
              <input type="time" class="wi-day-end" step="3600"
                value="${hhmm(draft.dayEnd)}" aria-label="Heating day ends">
            </label>
            <div class="wi-hint">Outside these hours the night setback applies.</div>
          </div>

          <div class="wi-group">
            <div class="wi-group-title">Hot water windows</div>
            <div class="wi-windows">
              ${windows.length
                ? windows
                    .map(
                      (w, i) => `
                <div class="wi-window" data-index="${i}">
                  <input type="time" class="wi-win-start" step="900"
                    value="${esc(w.start)}" aria-label="Window ${i + 1} start">
                  <span>–</span>
                  <input type="time" class="wi-win-end" step="900"
                    value="${esc(w.end)}" aria-label="Window ${i + 1} end">
                  <button type="button" class="wi-remove" data-index="${i}"
                    title="Remove" aria-label="Remove window ${i + 1}">×</button>
                </div>`
                    )
                    .join("")
                : `<div class="wi-hint">No windows: hot water is never
                     required, so the tank is only kept above its idle
                     minimum.</div>`}
            </div>
            <button type="button" class="wi-add">+ Add window</button>
          </div>
        </div>

        <div class="wi-row wi-actions">
          <button type="button" class="wi-apply">Simulate these slots</button>
          <button type="button" class="wi-save">Save as my schedule</button>
          <button type="button" class="wi-reset">Reset</button>
        </div>

        <div class="wi-result" role="status">
          Change a setting to see what it would cost. Simulating changes
          nothing; saving replaces your configured schedule.
        </div>
      </div>
    `;
  }

  /** The values the editor is currently showing.
   *
   * Held on the instance so a data refresh, which rebuilds the whole shadow
   * root, does not throw away half-finished edits.
   */
  _whatIfDraft() {
    if (!this._whatIf) {
      this._whatIf = {
        comfort: this._currentComfortTemp(),
        dayStart: this._planAttr("day_start_hour", 7),
        dayEnd: this._planAttr("day_end_hour", 22),
        dhwWindows: this._currentDhwWindows(),
      };
    }
    return this._whatIf;
  }

  /** Current comfort target, as the optimizer itself is planning against.
   *
   * This has to come from our own plan sensor. Scanning `climate.*` picks an
   * arbitrary thermostat -- a frost-protection TRV, an AC, a towel rail --
   * whose setpoint has nothing to do with the space-heating plan.
   */
  _currentComfortTemp() {
    return this._planAttr("comfort_temp_day", 21);
  }

  _planAttr(name, fallback) {
    const st = this._stateOf(this._resolveEntity("space"));
    const value = Number(((st && st.attributes) || {})[name]);
    return Number.isFinite(value) ? value : fallback;
  }

  /** Demand windows the DHW plan sensor is currently planning against. */
  _currentDhwWindows() {
    const st = this._stateOf(this._resolveEntity("dhw"));
    const spec = ((st && st.attributes) || {}).dhw_windows;
    return parseWindows(spec);
  }

  /** Wire the what-if controls, if the panel is present. */
  _attachWhatIf(root) {
    const panel = root.querySelector(".whatif");
    if (!panel) return;

    // Every control stops propagation: without it, a click inside the panel
    // reaches the card handler and toggles the expanded view underneath.
    const slider = root.querySelector(".wi-temp");
    if (slider) {
      slider.addEventListener("input", this._onWhatIfInput);
      slider.addEventListener("click", stop);
    }
    root.querySelectorAll("input[type=time]").forEach((el) => {
      el.addEventListener("click", stop);
      el.addEventListener("change", this._onSlotEdit);
    });
    const add = root.querySelector(".wi-add");
    if (add) add.addEventListener("click", this._onAddWindow);
    root
      .querySelectorAll(".wi-remove")
      .forEach((el) => el.addEventListener("click", this._onRemoveWindow));
    const apply = root.querySelector(".wi-apply");
    if (apply) apply.addEventListener("click", this._onApplySlots);
    const save = root.querySelector(".wi-save");
    if (save) save.addEventListener("click", this._onSaveSchedule);
    const reset = root.querySelector(".wi-reset");
    if (reset) reset.addEventListener("click", this._onResetWhatIf);
  }

  _onWhatIfInput(ev) {
    stop(ev);
    const value = Number(ev.target.value);
    if (!Number.isFinite(value)) return;
    this._whatIfDraft().comfort = value;

    const label = this.shadowRoot.querySelector(".wi-value");
    if (label) label.textContent = `${value.toFixed(1)}\u00a0°C`;

    // Debounce so a drag does not fire a solve per pixel. The coordinator
    // rate-limits as well, but sending the calls at all is wasteful.
    if (this._whatIfTimer) clearTimeout(this._whatIfTimer);
    this._whatIfTimer = setTimeout(() => this._runWhatIf(), 400);
  }

  /** Read the editors back into the draft, without simulating. */
  _onSlotEdit(ev) {
    stop(ev);
    const root = this.shadowRoot;
    const draft = this._whatIfDraft();
    const before = this._draftSignature();

    const dayStart = root.querySelector(".wi-day-start");
    const dayEnd = root.querySelector(".wi-day-end");
    if (dayStart) draft.dayStart = hourOf(dayStart.value, draft.dayStart);
    if (dayEnd) draft.dayEnd = hourOf(dayEnd.value, draft.dayEnd);

    draft.dhwWindows = [...root.querySelectorAll(".wi-window")].map((row) => ({
      start: (row.querySelector(".wi-win-start") || {}).value || "00:00",
      end: (row.querySelector(".wi-win-end") || {}).value || "00:00",
    }));

    // An armed confirmation refers to the values that were on screen when it
    // was armed. Only disarm if they actually changed — the save handler
    // itself calls this to flush the editors, and that must not cancel the
    // confirmation it is in the middle of.
    if (this._pendingSave && this._draftSignature() !== before) {
      this._cancelPendingSave();
    }
  }

  /** A comparable summary of the draft, for spotting real edits. */
  _draftSignature() {
    const d = this._whatIfDraft();
    return JSON.stringify([
      d.comfort,
      d.dayStart,
      d.dayEnd,
      d.dhwWindows.map((w) => `${w.start}-${w.end}`),
    ]);
  }

  _onAddWindow(ev) {
    stop(ev);
    this._onSlotEdit(ev);
    this._whatIfDraft().dhwWindows.push({ start: "06:00", end: "08:00" });
    this._sig = null;
    this._render();
  }

  _onRemoveWindow(ev) {
    stop(ev);
    this._onSlotEdit(ev);
    const index = Number(ev.currentTarget.getAttribute("data-index"));
    const draft = this._whatIfDraft();
    if (Number.isFinite(index)) draft.dhwWindows.splice(index, 1);
    this._sig = null;
    this._render();
  }

  _onApplySlots(ev) {
    stop(ev);
    this._onSlotEdit(ev);
    if (this._whatIfTimer) clearTimeout(this._whatIfTimer);
    this._runWhatIf();
  }

  _onResetWhatIf(ev) {
    stop(ev);
    this._whatIf = null;
    this._sig = null;
    this._pendingSave = false;
    this._render();
  }

  /** Persist the edited schedule, on a deliberate second press.
   *
   * Simulating is free and reversible, so it happens on one click. Saving
   * replaces the schedule the house actually runs on and reloads the
   * integration, so it asks first. The confirmation lives in the button label
   * rather than a `confirm()` dialog because the card is already inside a
   * modal, and a nested browser prompt inside a `showModal()` dialog is easy
   * to miss behind the backdrop.
   */
  async _onSaveSchedule(ev) {
    stop(ev);
    this._onSlotEdit(ev);

    const root = this.shadowRoot;
    const out = root && root.querySelector(".wi-result");
    const button = root && root.querySelector(".wi-save");
    if (!out || !button) return;

    if (!this._hass || typeof this._hass.callService !== "function") {
      out.className = "wi-result dearer";
      out.textContent = "Not connected to Home Assistant.";
      return;
    }

    const draft = this._whatIfDraft();
    const invalid = draft.dhwWindows.find(
      (w) => hourOf(w.start, null) === null || hourOf(w.end, null) === null
    );
    if (invalid) {
      out.className = "wi-result dearer";
      out.textContent = "One of the hot water windows is not a valid time.";
      return;
    }
    if (draft.dayStart === draft.dayEnd) {
      out.className = "wi-result dearer";
      out.textContent =
        "The heating day starts and ends at the same hour, which would " +
        "leave no comfort period at all.";
      return;
    }

    if (!this._pendingSave) {
      this._pendingSave = true;
      button.textContent = "Confirm: overwrite my schedule";
      button.classList.add("confirm");
      out.className = "wi-result";
      out.textContent =
        "This replaces your configured heating hours and hot water windows, " +
        "and reloads the integration. Press again to confirm.";
      // Let the decision lapse rather than sit armed indefinitely: a stray
      // click minutes later should not rewrite the configuration.
      clearTimeout(this._saveTimer);
      this._saveTimer = setTimeout(() => this._cancelPendingSave(), 8000);
      return;
    }

    this._cancelPendingSave();
    out.className = "wi-result";
    out.textContent = "Saving…";
    button.disabled = true;
    try {
      await this._hass.callService("heatpump_optimizer", "apply_schedule", {
        day_start_hour: draft.dayStart,
        day_end_hour: draft.dayEnd,
        dhw_windows: formatWindows(draft.dhwWindows),
        comfort_temp_day: draft.comfort,
      });
      out.className = "wi-result cheaper";
      out.textContent =
        "Saved. The optimizer is reloading and will plan against the new " +
        "schedule.";
      // The draft has become the configuration, so drop it: keeping it would
      // leave the editor showing an "unsaved" copy of what is now saved.
      this._whatIf = null;
    } catch (err) {
      out.className = "wi-result dearer";
      out.textContent = `Could not save: ${(err && err.message) || err}`;
    } finally {
      button.disabled = false;
    }
  }

  _cancelPendingSave() {
    clearTimeout(this._saveTimer);
    this._saveTimer = null;
    this._pendingSave = false;
    const button =
      this.shadowRoot && this.shadowRoot.querySelector(".wi-save");
    if (button) {
      button.textContent = "Save as my schedule";
      button.classList.remove("confirm");
    }
  }

  /** Everything the draft changes, as service call arguments. */
  _whatIfOverrides() {
    const draft = this._whatIfDraft();
    return {
      target_temp: draft.comfort,
      comfort_temp_day: draft.comfort,
      day_start_hour: draft.dayStart,
      day_end_hour: draft.dayEnd,
      // Deliberately sent even when empty: an empty schedule is a legitimate
      // thing to price, and it is how a user asks "what if I stopped
      // guaranteeing hot water at fixed times?"
      dhw_windows: formatWindows(draft.dhwWindows),
    };
  }

  async _runWhatIf() {
    const out = this.shadowRoot && this.shadowRoot.querySelector(".wi-result");
    if (!out || !this._hass || typeof this._hass.callService !== "function") {
      return;
    }
    const draft = this._whatIfDraft();
    const invalid = draft.dhwWindows.find(
      (w) => hourOf(w.start, null) === null || hourOf(w.end, null) === null
    );
    if (invalid) {
      out.className = "wi-result dearer";
      out.textContent = "One of the hot water windows is not a valid time.";
      return;
    }

    out.className = "wi-result";
    out.textContent = "Working out what that would cost…";
    try {
      const response = await this._hass.callService(
        "heatpump_optimizer",
        "simulate_plan",
        this._whatIfOverrides(),
        undefined,
        false,
        true
      );
      const results =
        (response && response.response && response.response.results) || {};
      const first = Object.values(results)[0];
      if (!first || first.error) {
        out.className = "wi-result dearer";
        out.textContent = first && first.error
          ? `Could not simulate: ${first.error}`
          : "No answer from the optimizer.";
        return;
      }
      out.className = "wi-result";
      out.innerHTML = this._whatIfSummary(first);
    } catch (err) {
      out.className = "wi-result dearer";
      out.textContent = `Could not simulate: ${
        err && err.message ? err.message : err
      }`;
    }
  }

  /** Money first, then what it costs in comfort.
   *
   * Reporting only the saving would invite the obvious mistake: a plan is
   * always cheaper if it is allowed to be colder, or to let the tank run down.
   */
  _whatIfSummary(result) {
    const delta = Number(result.monthly_cost_delta);
    const parts = [];

    if (!Number.isFinite(delta)) {
      return "No answer from the optimizer.";
    }
    if (Math.abs(delta) < 0.5) {
      parts.push(`<b>About the same cost</b> as the current plan.`);
    } else {
      const cheaper = delta < 0;
      parts.push(
        `<b class="${cheaper ? "cheaper" : "dearer"}">` +
          `${Math.abs(delta).toFixed(0)} ${cheaper ? "less" : "more"} per month` +
          `</b> than the current plan.`
      );
    }

    const room = Number(result.min_room_temperature);
    const roomBase = Number(result.baseline_min_room_temperature);
    if (Number.isFinite(room)) {
      const drop = Number.isFinite(roomBase) ? room - roomBase : null;
      parts.push(
        `Coldest the house gets: ${room.toFixed(1)} °C` +
          (drop !== null && Math.abs(drop) >= 0.1
            ? ` (${drop > 0 ? "+" : ""}${drop.toFixed(1)})`
            : "")
      );
    }

    const dhw = Number(result.min_dhw_temperature);
    const dhwBase = Number(result.baseline_min_dhw_temperature);
    if (Number.isFinite(dhw)) {
      const drop = Number.isFinite(dhwBase) ? dhw - dhwBase : null;
      parts.push(
        `Lowest tank temperature: ${dhw.toFixed(1)} °C` +
          (drop !== null && Math.abs(drop) >= 0.1
            ? ` (${drop > 0 ? "+" : ""}${drop.toFixed(1)})`
            : "")
      );
    }

    if (Number.isFinite(Number(result.compressor_starts))) {
      parts.push(`${result.compressor_starts} compressor starts`);
    }
    if (result.rate_limited) {
      parts.push("<i>(previous estimate; simulations are rate-limited)</i>");
    }

    return (
      `<div>${parts[0]}</div>` +
      `<div class="wi-detail">${parts.slice(1).join(" · ")}</div>`
    );
  }

  /** Wire hover and legend handling for every chart in a root. */
  _attachChartEvents(root) {
    root
      .querySelectorAll(".chip")
      .forEach((el) => el.addEventListener("click", this._onLegendClick));

    root.querySelectorAll("svg").forEach((svg) => {
      svg.addEventListener("mousemove", this._onPointerMove);
      svg.addEventListener("mouseleave", this._onPointerLeave);
      svg.addEventListener("touchmove", this._onPointerMove, { passive: true });
      svg.addEventListener("touchend", this._onPointerLeave);
    });

    this._attachWhatIf(root);
  }

  /** Bring the dialog element in the DOM into line with `_expanded`.
   *
   * `_render` rebuilds the shadow root wholesale, so on every data refresh the
   * open dialog is replaced by a fresh element that has to be shown again.
   */
  _syncDialog() {
    const dlg = this.shadowRoot.querySelector("dialog");
    if (!dlg) return;

    dlg.addEventListener("click", this._onDialogClick);
    dlg.addEventListener("close", this._onDialogClose);
    dlg.addEventListener("cancel", this._onDialogClose);
    const closeBtn = dlg.querySelector(".close");
    if (closeBtn) closeBtn.addEventListener("click", this._onDialogClick);

    if (this._expanded && !dlg.open) {
      // showModal promotes the dialog to the top layer, which is what keeps it
      // clear of the dashboard's stacking contexts and any clipping ancestor.
      if (typeof dlg.showModal === "function") dlg.showModal();
      else dlg.setAttribute("open", "");
    }
  }

  _styleBlock() {
    return `
      <style>
        ha-card { padding: 12px 12px 8px 12px; }
        ha-card.clickable { cursor: pointer; }
        .header {
          font-size: 1.15em; font-weight: 500; padding: 2px 4px 8px 4px;
          color: var(--primary-text-color);
          display: flex; align-items: center; gap: 8px;
        }
        .header .title { flex: 1 1 auto; min-width: 0; }
        .expand, .close {
          flex: 0 0 auto; display: inline-flex; align-items: center;
          justify-content: center; background: transparent; border: none;
          padding: 4px; margin: -4px; border-radius: 50%; cursor: pointer;
          color: var(--secondary-text-color); font: inherit;
        }
        .expand:hover, .close:hover { color: var(--primary-text-color); }
        .expand:focus-visible, .close:focus-visible,
        .chip:focus-visible {
          outline: 2px solid var(--primary-color, #03a9f4); outline-offset: 2px;
        }
        .legend {
          display: flex; flex-wrap: wrap; gap: 6px; padding: 0 2px 8px 2px;
        }
        .chip {
          display: inline-flex; align-items: center; gap: 6px;
          border: 1px solid var(--divider-color, #e0e0e0);
          border-radius: 14px; padding: 3px 10px; cursor: pointer;
          font-size: 0.82em; user-select: none; background: transparent;
          color: var(--primary-text-color); font-family: inherit;
        }
        .chip .dot {
          width: 10px; height: 10px; border-radius: 50%;
          display: inline-block; flex: 0 0 auto;
        }
        .chip.off { opacity: 0.4; text-decoration: line-through; }
        .chip.nodata { cursor: not-allowed; opacity: 0.3; }
        .chartwrap { position: relative; width: 100%; }
        svg { width: 100%; height: auto; display: block; touch-action: none; }
        .empty {
          padding: 28px 12px; text-align: center;
          color: var(--secondary-text-color); line-height: 1.5em;
        }
        .empty code { color: var(--primary-text-color); }
        .tooltip {
          position: absolute; pointer-events: none; z-index: 5;
          background: var(--card-background-color, #fff);
          border: 1px solid var(--divider-color, #ccc);
          border-radius: 6px; padding: 6px 8px; font-size: 0.78em;
          color: var(--primary-text-color);
          box-shadow: 0 2px 6px rgba(0,0,0,0.2); white-space: nowrap;
        }
        .tooltip .tt-row { display: flex; align-items: center; gap: 6px; }
        .tooltip .tt-time { font-weight: 600; margin-bottom: 3px; }
        .tooltip .tt-reason {
          margin-top: 4px; padding-top: 4px; font-style: italic;
          border-top: 1px solid var(--divider-color, #eee);
          color: var(--secondary-text-color);
        }
        .tooltip .dot {
          width: 8px; height: 8px; border-radius: 50%; display: inline-block;
        }

        /* Expanded view. The dialog width is capped so that the chart's own
           aspect ratio still fits the viewport height; sizing by width alone
           would overflow on short windows, and forcing the height instead
           would stretch the labels. */
        dialog.expanded {
          box-sizing: border-box;
          width: min(96vw, calc((100vh - 168px) * ${VIEW_RATIO}));
          max-width: 96vw;
          border: none; border-radius: 12px; padding: 16px;
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color);
          box-shadow: 0 8px 32px rgba(0,0,0,0.35);
          overflow: visible;
        }
        dialog.expanded::backdrop {
          background: rgba(0, 0, 0, 0.55);
        }
        .dlg-head {
          display: flex; align-items: center; gap: 8px;
          font-size: 1.25em; font-weight: 500; padding: 0 2px 10px 2px;
        }
        .dlg-head .title { flex: 1 1 auto; min-width: 0; }
        .chartwrap.big { aspect-ratio: ${VIEW_W} / ${VIEW_H}; }
        .chartwrap.big svg { height: 100%; }

        /* The legend, header and what-if panel are plain HTML, so unlike the
           chart they do not scale with the dialog: left alone they stay at card
           size no matter how large the dialog gets, which is what made them
           look cramped beside a chart three times their size.

           Everything below is therefore in em, and _scaleDialogFont sets the
           one font size they all derive from once the dialog has been laid
           out. Container query units would express this in CSS alone, but
           container-type: inline-size also applies inline-axis containment,
           and a dialog sized by its contents then has nothing to size from. */
        dialog.expanded .legend {
          font-size: 1em; gap: 0.5em; padding: 0 2px 0.75em 2px;
        }
        dialog.expanded .dlg-head {
          font-size: 1.4em; padding: 0 2px 0.55em 2px; gap: 0.45em;
        }
        dialog.expanded .chip {
          font-size: 1em; padding: 0.32em 0.85em; border-radius: 1.3em;
          gap: 0.45em; border-width: 1.5px;
        }
        dialog.expanded .chip .dot { width: 0.72em; height: 0.72em; }
        dialog.expanded .tooltip {
          font-size: 0.92em; padding: 0.5em 0.7em; border-radius: 0.4em;
        }
        dialog.expanded .tooltip .dot { width: 0.6em; height: 0.6em; }
        dialog.expanded .whatif { font-size: 1em; }
        dialog.expanded .close svg { width: 1.4em; height: 1.4em; }

        /* What-if simulator */
        .whatif {
          padding: 0.8em 0.3em 0.15em 0.3em; margin-top: 0.7em;
          border-top: 1px solid var(--divider-color, #e0e0e0);
          font-size: 0.95rem; color: var(--primary-text-color);
        }
        .whatif .wi-row {
          display: flex; flex-wrap: wrap; align-items: flex-start; gap: 1.2em;
          margin-bottom: 0.7em;
        }
        .whatif .wi-field {
          display: flex; align-items: center; gap: 0.55em;
        }
        .whatif .wi-field > span { white-space: nowrap; }
        .whatif input[type="range"] { width: 10em; max-width: 100%; }
        .whatif input[type="time"] {
          font: inherit; padding: 0.2em 0.4em; border-radius: 0.4em;
          border: 1px solid var(--divider-color, #ccc);
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color);
        }
        .whatif .wi-value {
          min-width: 3.5em; font-variant-numeric: tabular-nums;
          font-weight: 600;
        }
        .whatif .wi-group {
          flex: 1 1 16em; min-width: 14em;
          display: flex; flex-direction: column; gap: 0.4em;
        }
        .whatif .wi-group-title {
          font-weight: 600; font-size: 0.9em;
          color: var(--secondary-text-color);
          text-transform: uppercase; letter-spacing: 0.04em;
        }
        .whatif .wi-hint {
          font-size: 0.85em; color: var(--secondary-text-color);
          line-height: 1.35em;
        }
        .whatif .wi-windows {
          display: flex; flex-direction: column; gap: 0.4em;
        }
        .whatif .wi-window {
          display: flex; align-items: center; gap: 0.4em;
        }
        .whatif button {
          font: inherit; cursor: pointer; border-radius: 1.1em;
          border: 1px solid var(--divider-color, #ccc);
          background: transparent; color: var(--primary-text-color);
          padding: 0.35em 0.8em;
        }
        .whatif button:hover { border-color: var(--primary-color, #03a9f4); }
        .whatif .wi-remove {
          border: none; padding: 0 0.4em; font-size: 1.1em; line-height: 1;
          color: var(--secondary-text-color);
        }
        .whatif .wi-remove:hover { color: var(--error-color, #e0544e); }
        .whatif .wi-add { align-self: flex-start; font-size: 0.9em; }
        .whatif .wi-apply {
          border-color: var(--primary-color, #03a9f4);
          color: var(--primary-color, #03a9f4); font-weight: 600;
        }
        .whatif .wi-save {
          border-color: var(--primary-color, #03a9f4);
          background: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, #fff); font-weight: 600;
        }
        .whatif .wi-save.confirm {
          border-color: var(--error-color, #e0544e);
          background: var(--error-color, #e0544e);
        }
        .whatif .wi-save[disabled] { opacity: 0.6; cursor: default; }
        .whatif .wi-result {
          flex: 1 1 100%; min-height: 1.4em; line-height: 1.5em;
          color: var(--secondary-text-color);
        }
        .whatif .wi-result .wi-detail {
          font-size: 0.88em; margin-top: 2px;
        }
        .whatif .wi-result.cheaper, .whatif .cheaper {
          color: var(--success-color, #2fae7a);
        }
        .whatif .wi-result.dearer, .whatif .dearer {
          color: var(--error-color, #e0544e);
        }
        @media (max-width: 600px) {
          dialog.expanded { width: 96vw; padding: 12px; }
          dialog.expanded .legend { font-size: 1rem; }
        }
      </style>
    `;
  }

  _legendHtml() {
    const chips = SERIES_DEFS.map((def) => {
      const s = this._series.find((x) => x.key === def.key);
      const hasData = s ? s.hasData : false;
      const hidden = !!this._hidden[def.key];
      const cls = "chip" + (hidden ? " off" : "") + (hasData ? "" : " nodata");
      return `<button type="button" class="${cls}" data-key="${def.key}" title="${esc(
        def.label
      )} (${esc(def.unit)})">
        <span class="dot" style="background:${def.color}"></span>${esc(def.label)}
      </button>`;
    }).join("");
    return `<div class="legend">${chips}</div>`;
  }

  _chartSvg(built, expanded) {
    const { windowStart, windowEnd } = built;
    const visible = this._series.filter((s) => s.visible && s.hasData);
    const font = expanded ? FONT_EXPANDED : FONT_BASE;

    // Axis domains from visible series grouped by axis.
    const groups = { temp: [], power: [], price: [], solar: [] };
    for (const s of visible) {
      for (const line of s.lines) {
        for (const p of line.points) groups[s.axis].push(p.v);
      }
    }
    const axisRange = (vals, forceZero) => {
      if (!vals.length) return null;
      let lo = Math.min(...vals);
      let hi = Math.max(...vals);
      if (forceZero) lo = Math.min(0, lo);
      return niceAxis(lo, hi, 6);
    };
    const axes = {
      temp: axisRange(groups.temp, false),
      power: axisRange(groups.power, true),
      price: axisRange(groups.price, true),
      solar: axisRange(groups.solar, true),
    };

    const plotL = MARGIN.left;
    // Only pay for the solar axis's width when it is actually drawn; a
    // permanently narrower plot would be a real cost to every user who does
    // not use the series.
    const rightMargin = axes.solar ? MARGIN_RIGHT_WITH_SOLAR : MARGIN.right;
    const plotR = VIEW_W - rightMargin;
    const plotT = MARGIN.top;
    const plotB = VIEW_H - MARGIN.bottom;
    const plotW = plotR - plotL;
    const plotH = plotB - plotT;

    const xSpan = windowEnd - windowStart || 1;
    const scaleX = (t) => plotL + ((t - windowStart) / xSpan) * plotW;
    const scaleY = (v, axisName) => {
      const a = axes[axisName];
      if (!a) return plotB;
      const span = a.max - a.min || 1;
      return plotB - ((v - a.min) / span) * plotH;
    };

    // Store geometry for hover.
    this._plot = {
      windowStart,
      windowEnd,
      scaleX,
      scaleY,
      axes,
      plotL,
      plotR,
      plotT,
      plotB,
    };

    const parts = [];

    // Plot frame
    parts.push(
      `<rect x="${plotL}" y="${plotT}" width="${plotW}" height="${plotH}" fill="none" stroke="var(--divider-color,#e0e0e0)" stroke-width="1"/>`
    );

    // Hourly gridlines. How often they are labelled is worked out from the
    // space available, so a wider chart or a shorter horizon labels more.
    parts.push(
      this._timeAxis(scaleX, plotT, plotB, windowStart, windowEnd, font)
    );

    // Value axes
    if (axes.temp)
      parts.push(
        this._valueAxis(axes.temp, plotL, plotB, plotH, "left", 0, scaleY, "temp", "\u00b0C", font)
      );
    if (axes.power)
      parts.push(
        this._valueAxis(axes.power, plotL, plotB, plotH, "left", 44, scaleY, "power", "kW", font)
      );
    if (axes.price)
      parts.push(
        this._valueAxis(axes.price, plotR, plotB, plotH, "right", 0, scaleY, "price", "SEK/kWh", font)
      );
    if (axes.solar)
      parts.push(
        this._valueAxis(
          axes.solar, plotR, plotB, plotH, "right", SOLAR_AXIS_INSET,
          scaleY, "solar", "W/m\u00b2", font
        )
      );

    // Now marker
    const now = Date.now();
    if (now >= windowStart && now <= windowEnd) {
      const nx = scaleX(now);
      parts.push(
        `<line x1="${nx}" y1="${plotT}" x2="${nx}" y2="${plotB}" stroke="var(--primary-color,#03a9f4)" stroke-width="1.5" stroke-dasharray="4 3"/>`
      );
      parts.push(
        `<text x="${nx + 3}" y="${plotT + font + 1}" font-size="${font}" fill="var(--primary-color,#03a9f4)">now</text>`
      );
    }

    // Shade the stretch of the horizon whose prices are the learned diurnal
    // prior rather than published market data. A plan that looks identical
    // whether or not it rests on real prices cannot be audited.
    const estimatedFrom = this._estimatedPricesFrom();
    if (estimatedFrom !== null && estimatedFrom < windowEnd) {
      const ex = Math.max(plotL, scaleX(Math.max(estimatedFrom, windowStart)));
      parts.push(
        `<rect class="estimated" x="${ex}" y="${plotT}" width="${Math.max(
          0,
          plotR - ex
        )}" height="${plotH}" fill="var(--secondary-text-color,#888)" fill-opacity="0.07"/>`
      );
      parts.push(
        `<text x="${ex + 4}" y="${plotB - 5}" font-size="${font}" fill="var(--secondary-text-color,#888)">estimated prices</text>`
      );
    }

    // Series paths (filled/area series first, lines on top)
    const order = ["stepArea", "stepBars", "smooth"];
    for (const st of order) {
      for (const s of visible) {
        if (s.style !== st) continue;
        parts.push(this._seriesPath(s, scaleX, scaleY, plotB));
      }
    }

    // Crosshair placeholder (updated on hover)
    parts.push(
      `<line class="crosshair" x1="0" y1="${plotT}" x2="0" y2="${plotB}" stroke="var(--secondary-text-color,#888)" stroke-width="1" visibility="hidden"/>`
    );

    return `<svg viewBox="0 0 ${VIEW_W} ${VIEW_H}" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${esc(
      this._config.title
    )}">${parts.join("")}</svg>`;
  }

  /** Hourly gridlines, labelled as often as the width actually allows.
   *
   * Label density cannot be a fixed choice. The horizon is configurable, the
   * chart is drawn in a fixed coordinate system, and the labels are formatted
   * for the user's locale, so their width is not known in advance either --
   * "13:00" is five characters but "12:00 AM" is eight. Build the labels
   * first, measure the widest, and only then decide how many to show.
   */
  _timeAxis(scaleX, plotT, plotB, windowStart, windowEnd, font) {
    const size = font || FONT_BASE;
    const hour = 3600 * 1000;

    const first = new Date(windowStart);
    first.setMinutes(0, 0, 0);
    if (first.getTime() < windowStart) first.setHours(first.getHours() + 1);

    const ticks = [];
    for (let t = first.getTime(); t <= windowEnd; t += hour) {
      const d = new Date(t);
      ticks.push({
        t,
        x: scaleX(t),
        hours: d.getHours(),
        label: d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      });
    }
    if (!ticks.length) return "";

    // Widest rendered label, plus a gap, in viewBox units. The chart uses the
    // default sans-serif face, whose characters average a little over half an
    // em at these sizes.
    const widest = ticks.reduce((n, tick) => Math.max(n, tick.label.length), 0);
    const labelWidth = size * widest * CHAR_WIDTH_EM + size * 0.6;
    const unitsPerHour = Math.abs(scaleX(windowStart + hour) - scaleX(windowStart));
    const needed = unitsPerHour > 0 ? Math.ceil(labelWidth / unitsPerHour) : 3;
    // Intervals that divide the day, so labels land on the same clock times
    // each day rather than drifting across midnight.
    const every =
      TIME_LABEL_STEPS.find((step) => step >= Math.max(1, needed)) ||
      TIME_LABEL_STEPS[TIME_LABEL_STEPS.length - 1];

    const out = [];
    for (const tick of ticks) {
      const labelled = tick.hours % every === 0;
      out.push(
        `<line x1="${tick.x}" y1="${plotT}" x2="${tick.x}" y2="${plotB}" stroke="var(--divider-color,#eee)" stroke-width="${
          labelled ? 1 : 0.5
        }" opacity="${labelled ? 0.7 : 0.35}"/>`
      );
      if (labelled) {
        out.push(
          `<text x="${tick.x}" y="${plotB + size + 4}" font-size="${size}" text-anchor="middle" fill="var(--secondary-text-color,#888)">${esc(
            tick.label
          )}</text>`
        );
      }
    }
    return out.join("");
  }

  _valueAxis(
    axis, xBase, plotB, plotH, side, inset, scaleY, axisName, unit, font
  ) {
    const size = font || FONT_BASE;
    const out = [];
    const x = side === "left" ? xBase - inset : xBase + inset;
    const anchor = side === "left" ? "end" : "start";
    const tx = side === "left" ? x - 5 : x + 5;
    for (const tick of axis.ticks) {
      const y = scaleY(tick, axisName);
      out.push(
        `<text x="${tx}" y="${y + size / 3}" font-size="${size}" text-anchor="${anchor}" fill="var(--secondary-text-color,#888)">${esc(
          fmtTick(tick)
        )}</text>`
      );
      const t1 = side === "left" ? x - 3 : x + 3;
      out.push(
        `<line x1="${x}" y1="${y}" x2="${t1}" y2="${y}" stroke="var(--secondary-text-color,#aaa)" stroke-width="0.75"/>`
      );
    }
    const uy = MARGIN.top - 4;
    out.push(
      `<text x="${tx}" y="${uy}" font-size="${size}" text-anchor="${anchor}" fill="var(--secondary-text-color,#888)">${esc(
        unit
      )}</text>`
    );
    return out.join("");
  }

  /** Timestamp from which the plan's prices are the learned prior, or null. */
  _estimatedPricesFrom() {
    const spFc = this._forecast(this._resolveEntity("space")) || [];
    const dhwFc = this._forecast(this._resolveEntity("dhw")) || [];
    const fc = spFc.length ? spFc : dhwFc;
    for (const p of fc) {
      if (p.price_known === false) {
        const t = Date.parse(p.t);
        return Number.isNaN(t) ? null : t;
      }
    }
    return null;
  }

  _seriesPath(s, scaleX, scaleY, plotB) {
    const out = [];
    for (const line of s.lines) {
      const pts = line.points.map((p) => ({
        x: scaleX(p.t),
        y: scaleY(p.v, s.axis),
      }));
      if (!pts.length) continue;

      if (s.style === "stepArea" || s.style === "stepBars") {
        const stepD = this._steppedLine(pts);
        const baseY = plotB;
        const areaD =
          stepD +
          ` L ${pts[pts.length - 1].x.toFixed(2)} ${baseY.toFixed(2)}` +
          ` L ${pts[0].x.toFixed(2)} ${baseY.toFixed(2)} Z`;
        const fillOpacity = s.style === "stepBars" ? 0.35 : 0.18;
        out.push(
          `<path class="series" data-key="${s.key}" d="${areaD}" fill="${s.color}" fill-opacity="${fillOpacity}" stroke="none"/>`
        );
        out.push(
          `<path class="series" data-key="${s.key}" d="${stepD}" fill="none" stroke="${s.color}" stroke-width="1.5"/>`
        );
      } else {
        const d = this._smoothLine(pts);
        const dash = line.primary
          ? ""
          : ` stroke-dasharray="3 3" stroke-opacity="0.7"`;
        out.push(
          `<path class="series" data-key="${s.key}" d="${d}" fill="none" stroke="${s.color}" stroke-width="1.8"${dash}/>`
        );
      }
    }
    return out.join("");
  }

  _steppedLine(pts) {
    let d = `M ${pts[0].x.toFixed(2)} ${pts[0].y.toFixed(2)}`;
    for (let i = 1; i < pts.length; i++) {
      d += ` L ${pts[i].x.toFixed(2)} ${pts[i - 1].y.toFixed(2)}`;
      d += ` L ${pts[i].x.toFixed(2)} ${pts[i].y.toFixed(2)}`;
    }
    return d;
  }

  _smoothLine(pts) {
    if (pts.length < 3) {
      let d = `M ${pts[0].x.toFixed(2)} ${pts[0].y.toFixed(2)}`;
      for (let i = 1; i < pts.length; i++)
        d += ` L ${pts[i].x.toFixed(2)} ${pts[i].y.toFixed(2)}`;
      return d;
    }
    let d = `M ${pts[0].x.toFixed(2)} ${pts[0].y.toFixed(2)}`;
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[i - 1] || pts[i];
      const p1 = pts[i];
      const p2 = pts[i + 1];
      const p3 = pts[i + 2] || p2;
      const c1x = p1.x + (p2.x - p0.x) / 6;
      const c1y = p1.y + (p2.y - p0.y) / 6;
      const c2x = p2.x - (p3.x - p1.x) / 6;
      const c2y = p2.y - (p3.y - p1.y) / 6;
      d += ` C ${c1x.toFixed(2)} ${c1y.toFixed(2)} ${c2x.toFixed(2)} ${c2y.toFixed(
        2
      )} ${p2.x.toFixed(2)} ${p2.y.toFixed(2)}`;
    }
    return d;
  }

  // ---- interaction -------------------------------------------------------

  _onLegendClick(ev) {
    // A legend click must not also count as a click on the card, or toggling a
    // series would open the expanded view every time.
    if (ev && typeof ev.stopPropagation === "function") ev.stopPropagation();
    const el = ev.currentTarget;
    const key = el.getAttribute("data-key");
    if (!key) return;
    this._hidden[key] = !this._hidden[key];
    this._saveHidden();
    this._sig = null; // force
    this._render();
  }

  _onCardClick(ev) {
    // Ignore clicks that a control has already handled, and text selection.
    if (ev && ev.defaultPrevented) return;
    const sel = this.shadowRoot && this.shadowRoot.getSelection
      ? this.shadowRoot.getSelection()
      : null;
    if (sel && String(sel).length) return;
    this._openExpanded();
  }

  _onExpandClick(ev) {
    if (ev && typeof ev.stopPropagation === "function") ev.stopPropagation();
    this._openExpanded();
  }

  _onDialogClick(ev) {
    const dlg = this.shadowRoot && this.shadowRoot.querySelector("dialog");
    if (!dlg) return;
    // A click on the dialog element itself is a click on the backdrop: the
    // content sits in child elements, so anything else has a deeper target.
    const onBackdrop = ev && ev.target === dlg;
    const onClose =
      ev &&
      ev.currentTarget &&
      ev.currentTarget.classList &&
      ev.currentTarget.classList.contains("close");
    if (onBackdrop || onClose) this._closeExpanded();
  }

  _onDialogClose() {
    // Fires for Escape and for close() alike, so this is the single place the
    // flag is cleared and the two cannot drift apart.
    this._expanded = false;
  }

  _openExpanded() {
    if (this._expanded) return;
    this._expanded = true;
    this._sig = null; // force
    this._render();
  }

  _closeExpanded() {
    this._closeExpandedQuietly();
    this._sig = null;
    this._render();
  }

  /** Dismiss the dialog without re-rendering, for teardown paths. */
  _closeExpandedQuietly() {
    const dlg = this.shadowRoot && this.shadowRoot.querySelector("dialog");
    this._expanded = false;
    if (dlg && dlg.open && typeof dlg.close === "function") {
      dlg.close(); // triggers _onDialogClose, which is idempotent
    }
  }

  /** The chart wrapper owning an element, so each copy finds its own parts. */
  _wrapOf(el) {
    let node = el;
    while (node && node !== this.shadowRoot) {
      if (node.classList && node.classList.contains("chartwrap")) return node;
      node = node.parentNode;
    }
    return null;
  }

  _cacheRect() {
    const svg = this.shadowRoot && this.shadowRoot.querySelector("svg");
    if (svg && typeof svg.getBoundingClientRect === "function") {
      this._svgRect = svg.getBoundingClientRect();
    }
    this._scaleDialogFont();
  }

  /** Size the dialog's own text from how wide the dialog actually is.
   *
   * The chart scales itself, because it is stretched from a fixed coordinate
   * system. The chrome around it -- header, legend, tooltip, what-if panel --
   * is ordinary HTML inheriting the card's font, so it stays at card size no
   * matter how large the dialog gets, which is what made it look cramped
   * beside a chart three times its size.
   *
   * Setting one font size on the dialog fixes all of it at once, because every
   * measurement in the chrome is expressed in `em`. This is done here rather
   * than with container query units because `container-type: inline-size`
   * applies inline-axis containment, and a dialog sized by its own contents
   * then has nothing to size itself from.
   */
  _scaleDialogFont() {
    const root = this.shadowRoot;
    if (!root || !this._expanded) return;
    const dlg = root.querySelector("dialog");
    if (!dlg || typeof dlg.getBoundingClientRect !== "function") return;
    const rect = dlg.getBoundingClientRect();
    const width = (rect && Number(rect.width)) || 0;
    if (!Number.isFinite(width) || width <= 0) return;

    // Clamped at both ends: a phone-width dialog has to stay legible, and a
    // very wide monitor must not turn the legend into a headline.
    const px = Math.min(
      DIALOG_FONT_PX_MAX,
      Math.max(DIALOG_FONT_PX_MIN, width * DIALOG_FONT_RATIO)
    );
    // Writing an unchanged value would dirty style on every pointer move.
    if (significantlyDifferent(px, this._dialogFontPx)) {
      this._dialogFontPx = px;
      dlg.style.fontSize = `${px.toFixed(2)}px`;
    }
  }

  _onPointerLeave(ev) {
    const wrap = ev && ev.currentTarget ? this._wrapOf(ev.currentTarget) : null;
    const roots = wrap ? [wrap] : [this.shadowRoot];
    for (const root of roots) {
      if (!root) continue;
      const cross = root.querySelector(".crosshair");
      if (cross) cross.setAttribute("visibility", "hidden");
      const tt = root.querySelector(".tooltip");
      if (tt) tt.hidden = true;
    }
  }

  /** Why the plan is heating at the hovered step, plus price provenance.
   *
   * Only reasons for steps that are actually heating are shown; "not heating"
   * is not an explanation anyone needs, and printing it for every idle hour
   * would bury the ones that matter.
   */
  _reasonHtml(rows) {
    const out = [];
    const seen = new Set();
    for (const r of rows) {
      if (!r.reason || r.reason === "idle" || seen.has(r.reason)) continue;
      seen.add(r.reason);
      const label = REASON_LABELS[r.reason] || r.reason;
      out.push(`<div class="tt-reason">${esc(label)}</div>`);
    }
    if (rows.some((r) => r.priceKnown === false)) {
      out.push(
        `<div class="tt-reason">Price is estimated, not published yet</div>`
      );
    }
    return out.join("");
  }

  _onPointerMove(ev) {
    if (!this._plot) return;
    const svg = ev && ev.currentTarget;
    if (!svg || typeof svg.getBoundingClientRect !== "function") return;
    const wrap = this._wrapOf(svg);
    const rect = svg.getBoundingClientRect() || this._svgRect;
    if (!rect || !rect.width) return;

    let clientX;
    if (ev.touches && ev.touches.length) clientX = ev.touches[0].clientX;
    else clientX = ev.clientX;
    if (clientX === undefined) return;

    const vbX = ((clientX - rect.left) / rect.width) * VIEW_W;
    const { plotL, plotR, plotT, plotB, windowStart, windowEnd, scaleX } =
      this._plot;
    if (vbX < plotL || vbX > plotR) {
      this._onPointerLeave();
      return;
    }
    const span = windowEnd - windowStart || 1;
    const t = windowStart + ((vbX - plotL) / (plotR - plotL)) * span;

    const visible = this._series.filter((s) => s.visible && s.hasData);
    const rows = [];
    let snapX = vbX;
    let snapped = false;
    for (const s of visible) {
      const line = s.lines.find((l) => l.primary) || s.lines[0];
      if (!line) continue;
      let best = null;
      let bestDt = Infinity;
      for (const p of line.points) {
        const dt = Math.abs(p.t - t);
        if (dt < bestDt) {
          bestDt = dt;
          best = p;
        }
      }
      if (best) {
        if (!snapped) {
          snapX = scaleX(best.t);
          snapped = true;
        }
        rows.push({
          color: s.color,
          label: s.label,
          value: best.v,
          unit: s.unit,
          t: best.t,
          reason: best.reason,
          priceKnown: best.priceKnown,
        });
      }
    }
    if (!rows.length) {
      this._onPointerLeave();
      return;
    }

    const scope = wrap || this.shadowRoot;
    const cross = scope.querySelector(".crosshair");
    if (cross) {
      cross.setAttribute("x1", snapX);
      cross.setAttribute("x2", snapX);
      cross.setAttribute("y1", plotT);
      cross.setAttribute("y2", plotB);
      cross.setAttribute("visibility", "visible");
    }

    const tt = scope.querySelector(".tooltip");
    if (tt) {
      const time = new Date(rows[0].t).toLocaleString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
      const bodyHtml =
        `<div class="tt-time">${esc(time)}</div>` +
        rows
          .map(
            (r) =>
              `<div class="tt-row"><span class="dot" style="background:${r.color}"></span>${esc(
                r.label
              )}: ${esc(fmtTick(r.value))} ${esc(r.unit)}</div>`
          )
          .join("") +
        this._reasonHtml(rows);
      tt.innerHTML = bodyHtml;
      tt.hidden = false;
      const leftPx = clientX - rect.left;
      const place = leftPx > rect.width * 0.6 ? leftPx - 160 : leftPx + 14;
      tt.style.left = `${Math.max(0, place)}px`;
      // The tooltip is positioned against its own chart wrapper, so a
      // small inset keeps it clear of the plot frame in both views.
      tt.style.top = `8px`;
    }
  }
}

// A custom element name can only be claimed once per page. If an older copy of
// this card is still registered as a Lovelace resource -- typically a manual
// install left behind under /local/, or a browser holding a cached file -- it
// claims the name first and this file is then loaded but ignored. That failure
// is completely silent, and looks exactly like an upgrade that did nothing, so
// say so loudly and record which version actually won.
const previous = customElements.get(CARD_TAG);
if (previous) {
  if (previous.cardVersion !== CARD_VERSION) {
    // eslint-disable-next-line no-console
    console.error(
      `[${CARD_TAG}] v${CARD_VERSION} was loaded but v${
        previous.cardVersion || "unknown"
      } is already registered and stays in use. A duplicate copy of this card ` +
        "is installed. Remove the extra resource under Settings > Dashboards > " +
        "Resources (keep only the /heatpump_optimizer_static/ one), then reload."
    );
  }
} else {
  HeatpumpOptimizerCard.cardVersion = CARD_VERSION;
  customElements.define(CARD_TAG, HeatpumpOptimizerCard);
}

window.customCards = window.customCards || [];
window.customCards.push({
  type: CARD_TAG,
  name: "Heat Pump Optimizer Card",
  description:
    "Plots heat-pump price, power and temperature plans on one shared time axis with per-series toggles.",
  preview: false,
});

// eslint-disable-next-line no-console
console.info(
  `%c ${CARD_TAG} %c v${CARD_VERSION} `,
  "color:#fff;background:#2fae7a;border-radius:3px 0 0 3px;padding:2px 4px;",
  "color:#2fae7a;background:#222;border-radius:0 3px 3px 0;padding:2px 4px;"
);
