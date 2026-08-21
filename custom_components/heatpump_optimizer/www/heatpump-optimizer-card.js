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
const CARD_VERSION = "2.6.1";

const DEFAULTS = {
  title: "Heat pump plan",
  // Entity ids are derived from the device name ("Heat Pump Optimizer"), since
  // the plan sensors use has_entity_name. These are the ids a default install
  // produces; if they are absent the card auto-discovers by the `plan_kind`
  // attribute, so a renamed entity still works with no config change.
  space_entity: "sensor.heat_pump_optimizer_space_heating_plan",
  dhw_entity: "sensor.heat_pump_optimizer_dhw_heating_plan",
  hours: 24,
};

// Series metadata. `axis` selects one of three value axes: temp / power / price.
// `sensor` selects which forecast the values come from ("space", "dhw" or
// "either" meaning prefer space then fall back to dhw). `field` is the forecast
// attribute key. Colours are fixed and chosen to read on light + dark themes.
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
];

const VIEW_W = 900;
const VIEW_H = 380;
const MARGIN = { top: 16, right: 62, bottom: 34, left: 92 };

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
    this._onLegendClick = this._onLegendClick.bind(this);
    this._onPointerMove = this._onPointerMove.bind(this);
    this._onPointerLeave = this._onPointerLeave.bind(this);
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
    const configured = kind === "space" ? cfg.space_entity : cfg.dhw_entity;
    if (!this._hass || !this._hass.states) return configured;
    const states = this._hass.states;
    if (states[configured]) return configured;

    if (!this._resolvedCache) this._resolvedCache = {};
    const cached = this._resolvedCache[kind];
    if (cached && states[cached]) return cached;

    const suffix = kind === "space" ? "space_heating_plan" : "dhw_heating_plan";
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
    const space = this._stateOf(spId);
    const dhw = this._stateOf(dhwId);
    const spFc = this._forecast(spId);
    const dhwFc = this._forecast(dhwId);
    return [
      spId,
      dhwId,
      cfg.hours,
      cfg.title,
      space ? space.last_updated : "-",
      space ? space.state : "-",
      dhw ? dhw.last_updated : "-",
      dhw ? dhw.state : "-",
      spFc ? spFc.length : -1,
      dhwFc ? dhwFc.length : -1,
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

    const pick = (sensor) => (sensor === "dhw" ? dhwFc : spFc);
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
          pts.push({ t, v: Number(v) });
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
      const chart = this._chartSvg(built);
      body = `<div class="chartwrap">${chart}</div>`;
    }

    this.shadowRoot.innerHTML = `
      <ha-card>
        ${style}
        <div class="header">${esc(cfg.title)}</div>
        ${legend}
        ${body}
        <div class="tooltip" id="tt" hidden></div>
      </ha-card>
    `;

    // Attach interactions
    this.shadowRoot
      .querySelectorAll(".chip")
      .forEach((el) => el.addEventListener("click", this._onLegendClick));

    const svg = this.shadowRoot.querySelector("svg");
    if (svg) {
      svg.addEventListener("mousemove", this._onPointerMove);
      svg.addEventListener("mouseleave", this._onPointerLeave);
      svg.addEventListener("touchmove", this._onPointerMove, { passive: true });
      svg.addEventListener("touchend", this._onPointerLeave);
    }
    this._cacheRect();
  }

  _styleBlock() {
    return `
      <style>
        ha-card { padding: 12px 12px 8px 12px; }
        .header {
          font-size: 1.15em; font-weight: 500; padding: 2px 4px 8px 4px;
          color: var(--primary-text-color);
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
        .tooltip .dot {
          width: 8px; height: 8px; border-radius: 50%; display: inline-block;
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

  _chartSvg(built) {
    const { windowStart, windowEnd } = built;
    const visible = this._series.filter((s) => s.visible && s.hasData);

    // Axis domains from visible series grouped by axis.
    const groups = { temp: [], power: [], price: [] };
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
    };

    const plotL = MARGIN.left;
    const plotR = VIEW_W - MARGIN.right;
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
    parts.push(this._timeAxis(scaleX, plotT, plotB, windowStart, windowEnd));

    // Value axes
    if (axes.temp)
      parts.push(
        this._valueAxis(axes.temp, plotL, plotB, plotH, "left", 0, scaleY, "temp", "\u00b0C")
      );
    if (axes.power)
      parts.push(
        this._valueAxis(axes.power, plotL, plotB, plotH, "left", 44, scaleY, "power", "kW")
      );
    if (axes.price)
      parts.push(
        this._valueAxis(axes.price, plotR, plotB, plotH, "right", 0, scaleY, "price", "SEK/kWh")
      );

    // Now marker
    const now = Date.now();
    if (now >= windowStart && now <= windowEnd) {
      const nx = scaleX(now);
      parts.push(
        `<line x1="${nx}" y1="${plotT}" x2="${nx}" y2="${plotB}" stroke="var(--primary-color,#03a9f4)" stroke-width="1.5" stroke-dasharray="4 3"/>`
      );
      parts.push(
        `<text x="${nx + 3}" y="${plotT + 11}" font-size="10" fill="var(--primary-color,#03a9f4)">now</text>`
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
      `<line id="crosshair" x1="0" y1="${plotT}" x2="0" y2="${plotB}" stroke="var(--secondary-text-color,#888)" stroke-width="1" visibility="hidden"/>`
    );

    return `<svg viewBox="0 0 ${VIEW_W} ${VIEW_H}" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${esc(
      this._config.title
    )}">${parts.join("")}</svg>`;
  }

  _timeAxis(scaleX, plotT, plotB, windowStart, windowEnd) {
    const out = [];
    const first = new Date(windowStart);
    first.setMinutes(0, 0, 0);
    if (first.getTime() < windowStart) first.setHours(first.getHours() + 1);
    for (let t = first.getTime(); t <= windowEnd; t += 3600 * 1000) {
      const x = scaleX(t);
      const d = new Date(t);
      const label3h = d.getHours() % 3 === 0;
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
          `<text x="${x}" y="${plotB + 14}" font-size="10" text-anchor="middle" fill="var(--secondary-text-color,#888)">${esc(
            lbl
          )}</text>`
        );
      }
    }
    return out.join("");
  }

  _valueAxis(axis, xBase, plotB, plotH, side, inset, scaleY, axisName, unit) {
    const out = [];
    const x = side === "left" ? xBase - inset : xBase + inset;
    const anchor = side === "left" ? "end" : "start";
    const tx = side === "left" ? x - 5 : x + 5;
    for (const tick of axis.ticks) {
      const y = scaleY(tick, axisName);
      out.push(
        `<text x="${tx}" y="${y + 3}" font-size="10" text-anchor="${anchor}" fill="var(--secondary-text-color,#888)">${esc(
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
      `<text x="${tx}" y="${uy}" font-size="10" text-anchor="${anchor}" fill="var(--secondary-text-color,#888)">${esc(
        unit
      )}</text>`
    );
    return out.join("");
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
    const el = ev.currentTarget;
    const key = el.getAttribute("data-key");
    if (!key) return;
    this._hidden[key] = !this._hidden[key];
    this._saveHidden();
    this._sig = null; // force
    this._render();
  }

  _cacheRect() {
    const svg = this.shadowRoot && this.shadowRoot.querySelector("svg");
    if (svg && typeof svg.getBoundingClientRect === "function") {
      this._svgRect = svg.getBoundingClientRect();
    }
  }

  _onPointerLeave() {
    const cross = this.shadowRoot.querySelector("#crosshair");
    if (cross) cross.setAttribute("visibility", "hidden");
    const tt = this.shadowRoot.querySelector("#tt");
    if (tt) tt.hidden = true;
  }

  _onPointerMove(ev) {
    if (!this._plot) return;
    const svg = this.shadowRoot.querySelector("svg");
    if (!svg) return;
    const rect =
      (svg.getBoundingClientRect && svg.getBoundingClientRect()) ||
      this._svgRect;
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
        });
      }
    }
    if (!rows.length) {
      this._onPointerLeave();
      return;
    }

    const cross = this.shadowRoot.querySelector("#crosshair");
    if (cross) {
      cross.setAttribute("x1", snapX);
      cross.setAttribute("x2", snapX);
      cross.setAttribute("y1", plotT);
      cross.setAttribute("y2", plotB);
      cross.setAttribute("visibility", "visible");
    }

    const tt = this.shadowRoot.querySelector("#tt");
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
          .join("");
      tt.innerHTML = bodyHtml;
      tt.hidden = false;
      const leftPx = clientX - rect.left;
      const place = leftPx > rect.width * 0.6 ? leftPx - 160 : leftPx + 14;
      tt.style.left = `${Math.max(0, place)}px`;
      tt.style.top = `44px`;
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
