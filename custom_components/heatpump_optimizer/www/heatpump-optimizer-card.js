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
const CARD_VERSION = "2.8.0";

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
  // The what-if simulator lives in the expanded view. Off by default because
  // it calls a service that runs a real solve on the Home Assistant host.
  what_if: false,
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

// SVG text is sized in viewBox units, so a chart scaled up to fill a dialog
// renders the same nominal glyph size across a much larger area — which reads
// as cramped and low-resolution even though the text is still vector. Scaling
// the in-viewBox size back down keeps the *apparent* size constant.
const FONT_BASE = 10;
const FONT_EXPANDED = 15;

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
    this._whatIfValue = null;
    this._whatIfTimer = null;
    this._onLegendClick = this._onLegendClick.bind(this);
    this._onPointerMove = this._onPointerMove.bind(this);
    this._onPointerLeave = this._onPointerLeave.bind(this);
    this._onCardClick = this._onCardClick.bind(this);
    this._onExpandClick = this._onExpandClick.bind(this);
    this._onDialogClick = this._onDialogClick.bind(this);
    this._onDialogClose = this._onDialogClose.bind(this);
    this._onWhatIfInput = this._onWhatIfInput.bind(this);
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
   * Setpoints are normally chosen blind: the optimizer can price a plan, but
   * the user never sees the price of their own comfort choices. Dragging a
   * slider here re-solves against the current forecast and reports the monthly
   * cost difference, which turns "I set 21 because it sounds about right" into
   * an informed decision.
   *
   * The evaluation runs off a copy of the configuration on the coordinator
   * side, so an exploratory drag never disturbs actual operation, and the
   * service call is both debounced here and rate-limited there.
   */
  _whatIfHtml() {
    if (!this._config.what_if) return "";
    const target = this._whatIfTarget();
    return `
      <div class="whatif">
        <label>
          Comfort temperature
          <input type="range" class="wi-temp" min="16" max="24" step="0.5"
            value="${target}" aria-label="Comfort temperature">
          <span class="wi-value">${target.toFixed(1)}&nbsp;°C</span>
        </label>
        <div class="wi-result" role="status">
          Drag to see what a different comfort temperature would cost.
        </div>
      </div>
    `;
  }

  /** Current comfort target, read from the climate entity when there is one. */
  _whatIfTarget() {
    if (this._whatIfValue !== undefined && this._whatIfValue !== null) {
      return this._whatIfValue;
    }
    const states = (this._hass && this._hass.states) || {};
    for (const id of Object.keys(states)) {
      if (!id.startsWith("climate.")) continue;
      const attrs = states[id].attributes || {};
      const temp = Number(attrs.temperature);
      if (Number.isFinite(temp)) return temp;
    }
    return 21;
  }

  /** Wire the what-if slider, if it is present. */
  _attachWhatIf(root) {
    const slider = root.querySelector(".wi-temp");
    if (!slider) return;
    slider.addEventListener("input", this._onWhatIfInput);
    slider.addEventListener("click", (ev) => ev.stopPropagation());
  }

  _onWhatIfInput(ev) {
    if (ev && typeof ev.stopPropagation === "function") ev.stopPropagation();
    const value = Number(ev.target.value);
    if (!Number.isFinite(value)) return;
    this._whatIfValue = value;

    const scope = this.shadowRoot;
    const label = scope.querySelector(".wi-value");
    if (label) label.textContent = `${value.toFixed(1)}\u00a0°C`;

    // Debounce so a drag does not fire a solve per pixel. The coordinator
    // rate-limits as well, but sending the calls at all is wasteful.
    if (this._whatIfTimer) clearTimeout(this._whatIfTimer);
    this._whatIfTimer = setTimeout(() => this._runWhatIf(value), 400);
  }

  async _runWhatIf(value) {
    const out = this.shadowRoot && this.shadowRoot.querySelector(".wi-result");
    if (!out || !this._hass || typeof this._hass.callService !== "function") {
      return;
    }
    out.className = "wi-result";
    out.textContent = "Working out what that would cost…";
    try {
      const response = await this._hass.callService(
        "heatpump_optimizer",
        "simulate_plan",
        { target_temp: value, comfort_temp_day: value },
        undefined,
        false,
        true
      );
      const results = (response && response.response &&
        response.response.results) || {};
      const first = Object.values(results)[0];
      if (!first || first.error) {
        out.textContent = first && first.error
          ? `Could not simulate: ${first.error}`
          : "No answer from the optimizer.";
        return;
      }
      const delta = Number(first.monthly_cost_delta);
      if (!Number.isFinite(delta)) {
        out.textContent = "No answer from the optimizer.";
        return;
      }
      if (Math.abs(delta) < 0.5) {
        out.textContent = `${value.toFixed(1)} °C costs about the same as now.`;
        return;
      }
      const cheaper = delta < 0;
      out.className = `wi-result ${cheaper ? "cheaper" : "dearer"}`;
      out.textContent =
        `${value.toFixed(1)} °C would cost about ` +
        `${Math.abs(delta).toFixed(0)} ${cheaper ? "less" : "more"} per month` +
        (first.rate_limited ? " (using the previous estimate)" : "") +
        ".";
    } catch (err) {
      out.textContent = `Could not simulate: ${err && err.message ? err.message : err}`;
    }
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

        /* The legend is plain HTML, so it does not scale with the chart. Its
           chips are sized in em against the inherited card font, which stays
           at card size no matter how large the dialog gets — that is what made
           them look cramped and low-resolution next to a much bigger chart.
           Setting an explicit base font on the dialog lets the em units
           cascade to a size that matches. */
        dialog.expanded .legend {
          font-size: 1.15rem; gap: 10px; padding: 0 2px 14px 2px;
        }
        dialog.expanded .chip {
          font-size: 0.8em; padding: 6px 14px; border-radius: 20px;
          border-width: 1.5px;
        }
        dialog.expanded .chip .dot { width: 14px; height: 14px; }
        dialog.expanded .tooltip { font-size: 0.95rem; padding: 8px 11px; }
        dialog.expanded .tooltip .dot { width: 10px; height: 10px; }

        /* What-if simulator (item 21) */
        .whatif {
          display: flex; flex-wrap: wrap; align-items: center; gap: 14px;
          padding: 12px 4px 2px 4px; border-top: 1px solid
          var(--divider-color, #e0e0e0); margin-top: 10px;
        }
        .whatif label {
          display: flex; align-items: center; gap: 8px; font-size: 0.95rem;
          color: var(--primary-text-color);
        }
        .whatif input[type="range"] { width: 150px; }
        .whatif .wi-value {
          min-width: 3.5em; font-variant-numeric: tabular-nums;
          font-weight: 600;
        }
        .whatif .wi-result {
          flex: 1 1 100%; font-size: 0.95rem;
          color: var(--secondary-text-color); min-height: 1.4em;
        }
        .whatif .wi-result.cheaper { color: var(--success-color, #2fae7a); }
        .whatif .wi-result.dearer { color: var(--error-color, #e0544e); }
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

    // Time gridlines + labels (hour grid, label every 3h)
    // The expanded view has room to label every hour instead of every third.
    parts.push(
      this._timeAxis(
        scaleX, plotT, plotB, windowStart, windowEnd, expanded ? 1 : 3, font
      )
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

  _timeAxis(scaleX, plotT, plotB, windowStart, windowEnd, labelEvery, font) {
    const every = labelEvery || 3;
    const size = font || FONT_BASE;
    const out = [];
    const first = new Date(windowStart);
    first.setMinutes(0, 0, 0);
    if (first.getTime() < windowStart) first.setHours(first.getHours() + 1);
    for (let t = first.getTime(); t <= windowEnd; t += 3600 * 1000) {
      const x = scaleX(t);
      const d = new Date(t);
      const label3h = d.getHours() % every === 0;
      out.push(
        `<line x1="${x}" y1="${plotT}" x2="${x}" y2="${plotB}" stroke="var(--divider-color,#eee)" stroke-width="${
          label3h ? 1 : 0.5
        }" opacity="${label3h ? 0.7 : 0.35}"/>`
      );
      if (label3h) {
        const lbl = d.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        });
        out.push(
          `<text x="${x}" y="${plotB + size + 4}" font-size="${size}" text-anchor="middle" fill="var(--secondary-text-color,#888)">${esc(
            lbl
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

if (!customElements.get(CARD_TAG)) {
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
