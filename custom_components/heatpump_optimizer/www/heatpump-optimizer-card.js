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
const CARD_VERSION = "3.7.1";

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

// The editable lanes along the bottom of the plot, in viewBox units. Slots are
// dragged here rather than on the power bars themselves: the bars vary in
// height with power, which makes them an awkward and inconsistent hit target,
// whereas a lane is a constant band that reads as a timeline.
const LANE_H = 15;
const LANE_GAP = 3;
const LANE_BOTTOM_INSET = 3;
// How close to an edge a grab counts as a resize rather than a move.
const LANE_EDGE_GRAB = 6;
const PLAN_STEP_MS = 15 * 60000;

// How far ahead a hand-arranged plan may be pinned. The integration owns this
// number and publishes it as `manual_plan_window_hours`; this is only the value
// used before the first plan has been received. A copy that could drift from the
// service's expiry default is exactly the bug the published attribute prevents.
const MANUAL_PLAN_WINDOW_FALLBACK_H = 20;

// Range of the hot water minimum slider. The floor matches the options flow so
// the two editors of the same setting agree. There is deliberately no margin
// constant here: the *ceiling* is computed by the integration and published as
// `dhw_min_temperature_max`, because the backend has to validate against the
// same number and a copy in the card would be free to drift from it. The
// fallback is only reached before the first plan is published.
const DHW_MIN_FLOOR = 35;
const DHW_MIN_FALLBACK = 45;

// Pan and zoom over the plan window (item 23).
//
// Forward-only, deliberately: there is no history to scroll back into, because
// both plan sensors declare `forecast` unrecorded, so nothing stores what the
// plan used to say. The window is therefore confined to [now, end of plan], and
// zooming out stops at the plan's real extent rather than at the configured
// plot width -- past the horizon there is empty space, not more plan.
const VIEW_MIN_SPAN_MS = 2 * 3600 * 1000;
const VIEW_ZOOM_STEP = 1.4;

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
  manual_plan: "You scheduled this",
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

function clampNum(v, lo, hi) {
  return v < lo ? lo : v > hi ? hi : v;
}

/** An expiry for prose.
 *
 * A pinned plan now lasts 20 hours from the moment it is applied, so the expiry
 * usually falls on the following day. Under the old midnight rule the day was
 * implicit and a bare "until 08:30" was unambiguous; it no longer is, so say
 * which day whenever it is not today.
 */
function fmtExpiry(when) {
  const time = when.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const today = new Date();
  const sameDay =
    when.getFullYear() === today.getFullYear() &&
    when.getMonth() === today.getMonth() &&
    when.getDate() === today.getDate();
  if (sameDay) return time;
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  const isTomorrow =
    when.getFullYear() === tomorrow.getFullYear() &&
    when.getMonth() === tomorrow.getMonth() &&
    when.getDate() === tomorrow.getDate();
  if (isTomorrow) return `${time} tomorrow`;
  return `${time} on ${when.toLocaleDateString([], { weekday: "long" })}`;
}

/** A temperature for prose: no trailing ".0" on whole degrees. */
function fmtTemp(v) {
  return Number.isInteger(v) ? String(v) : v.toFixed(1);
}

function fmtTick(v) {
  if (Math.abs(v) >= 10) return v.toFixed(0);
  if (Number.isInteger(v)) return String(v);
  return v.toFixed(1);
}

/** Rough rendered width of a label, in the chart's viewBox units. */
function textWidth(str, size) {
  return str.length * size * CHAR_WIDTH_EM;
}

/** Editing model for hand-arranged run slots.
 *
 * The plan is published per timestep, but nobody thinks in timesteps: a user
 * thinks "hot water runs from 04:00 to 06:00". So the steps are collapsed into
 * runs, all editing happens on runs, and the result is only ever expanded back
 * to steps when a cost is needed.
 *
 * Everything here is pure and knows nothing about the DOM or the chart, which
 * is what makes the dragging logic testable at all -- the geometry can be
 * exercised without a browser, and a pointer event ends up being nothing more
 * than a delta in milliseconds.
 *
 * Times are epoch milliseconds throughout. Runs are always kept sorted, gap-
 * free of overlaps, and inside the horizon, so no caller has to defend itself
 * against a half-edited arrangement.
 */
const SlotModel = {
  /** Collapse per-step power into contiguous runs of "on". */
  runsFrom(forecast, field, threshold = 0.05, stepMs = 15 * 60000) {
    const runs = [];
    let open = null;
    for (const point of forecast || []) {
      const t = Date.parse(point.t);
      if (!Number.isFinite(t)) continue;
      const on = Number(point[field]) > threshold;
      if (on && !open) open = { start: t, end: t + stepMs };
      else if (on && open) open.end = t + stepMs;
      else if (!on && open) {
        runs.push(open);
        open = null;
      }
    }
    if (open) runs.push(open);
    return runs;
  },

  /** Round to the planning grid. Anything finer cannot be acted on anyway. */
  snap(ms, stepMs) {
    return Math.round(ms / stepMs) * stepMs;
  },

  /** Sort, drop empties and merge what now touches.
   *
   * Dragging one run across another is a normal gesture, not an error, so
   * overlaps are resolved by merging rather than by refusing the move.
   *
   * This deliberately does *not* clamp to the editable range. That range
   * begins at the present, so clamping every run to it would haul slots that
   * have already run forward into the future and merge them together --
   * rewriting history to make room for an edit. Only the run being edited is
   * constrained, by the caller that knows which one that is.
   */
  normalize(runs, stepMs) {
    const clean = (runs || [])
      .map((r) => ({ start: r.start, end: r.end }))
      .filter((r) => r.end - r.start >= stepMs)
      .sort((a, b) => a.start - b.start);

    const out = [];
    for (const run of clean) {
      const last = out[out.length - 1];
      if (last && run.start <= last.end) last.end = Math.max(last.end, run.end);
      else out.push({ ...run });
    }
    return out;
  },

  /** Slide a whole run, keeping its length. */
  move(runs, index, deltaMs, stepMs, bounds) {
    const run = runs[index];
    if (!run) return runs;
    const length = run.end - run.start;
    const [lo, hi] = bounds;
    let start = this.snap(run.start + deltaMs, stepMs);
    // Clamp the run as a unit; letting the start clamp alone would silently
    // stretch or shrink it at the horizon edges.
    start = Math.max(lo, Math.min(hi - length, start));
    const moved = runs.map((r, i) =>
      i === index ? { start, end: start + length } : r
    );
    return this.normalize(moved, stepMs);
  },

  /** Drag one end of a run. The other end stays put. */
  resize(runs, index, edge, deltaMs, stepMs, bounds) {
    const run = runs[index];
    if (!run) return runs;
    const next = { ...run };
    const [lo, hi] = bounds;
    if (edge === "start") {
      next.start = Math.max(
        lo,
        Math.min(this.snap(run.start + deltaMs, stepMs), run.end - stepMs)
      );
    } else {
      next.end = Math.min(
        hi,
        Math.max(this.snap(run.end + deltaMs, stepMs), run.start + stepMs)
      );
    }
    const resized = runs.map((r, i) => (i === index ? next : r));
    return this.normalize(resized, stepMs);
  },

  /** Add a run at a point, sized to fit whatever gap it lands in. */
  add(runs, atMs, stepMs, bounds, preferredMs = 60 * 60000) {
    const [lo, hi] = bounds;
    const at = Math.max(lo, Math.min(hi - stepMs, this.snap(atMs, stepMs)));
    // Grow up to the preferred length but stop at the next run, so adding
    // between two runs does not silently swallow the one after it.
    const following = runs.find((r) => r.start >= at);
    const limit = following ? following.start : hi;
    const end = Math.min(at + preferredMs, limit, hi);
    if (end - at < stepMs) return runs;
    return this.normalize([...runs, { start: at, end }], stepMs);
  },

  remove(runs, index) {
    return runs.filter((_, i) => i !== index);
  },

  /** Index of the run containing a time, or -1. */
  indexAt(runs, ms) {
    return runs.findIndex((r) => ms >= r.start && ms < r.end);
  },

  /** Typical power of a channel while it is running.
   *
   * The arrangement says when to run, not how hard; the optimizer still picks
   * the magnitude. For an estimate, what the plan already does while running
   * is a far better guide than a nameplate rating.
   */
  typicalPower(forecast, field, threshold = 0.05) {
    const on = (forecast || [])
      .map((p) => Number(p[field]))
      .filter((v) => Number.isFinite(v) && v > threshold);
    if (!on.length) return 0;
    return on.reduce((a, b) => a + b, 0) / on.length;
  },

  /** Cost of running a channel over these runs, at the horizon's prices. */
  cost(runs, forecast, powerKw, stepMs) {
    if (!powerKw) return 0;
    const dtHours = stepMs / 3600000;
    let total = 0;
    for (const point of forecast || []) {
      const t = Date.parse(point.t);
      const price = Number(point.price);
      if (!Number.isFinite(t) || !Number.isFinite(price)) continue;
      // A step counts when its midpoint is covered, so a run that starts
      // mid-step is not double-counted at both ends.
      const mid = t + stepMs / 2;
      if (runs.some((r) => mid >= r.start && mid < r.end)) {
        total += powerKw * dtHours * price;
      }
    }
    return total;
  },
};

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
    this._dialogScroll = 0;
    // Pan/zoom window (item 23). `null` means "the default window", so an
    // untouched card behaves exactly as it did before this existed.
    this._view = null;
    this._viewLimits = null;
    this._viewFrame = 0;
    this._pan = null;
    this._suppressClick = false;
    this._onLegendClick = this._onLegendClick.bind(this);
    this._onChartWheel = this._onChartWheel.bind(this);
    this._onPanDown = this._onPanDown.bind(this);
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
    // A newly published plan replaces the slot draft, unless the user is part
    // way through rearranging it. Their edits have to survive a refresh -- but
    // an untouched draft must not survive one, or the lanes would keep showing
    // an arrangement the optimizer has already moved on from, the cost delta
    // would compare against a plan that no longer exists, and Apply would pin
    // something the user is not looking at.
    if (!this._runsDirty) this._runs = null;
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

    // Everything above is the default window. `_applyView` narrows it to
    // whatever the user has panned or zoomed to, and is a no-op until they
    // touch a control -- so the untouched card renders exactly as before.
    // Filtering below this point then happens against the visible window, which
    // is what keeps the value axis scaled to what is actually on screen.
    const view = this._applyView(
      windowStart,
      windowEnd,
      allTimes.length ? Math.max(...allTimes) : windowEnd
    );
    windowStart = view.start;
    windowEnd = view.end;

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

    return { series, windowStart, windowEnd, zoomed: this._view !== null };
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
    // The dialog body scrolls now, and `_render` replaces the whole shadow root
    // on every plan refresh -- which happens on the coordinator's schedule, not
    // the user's. Without carrying the offset across the rebuild the panel would
    // jump back to the top by itself every few minutes, mid-edit.
    const openBody = this.shadowRoot.querySelector("dialog.expanded .dlg-body");
    this._dialogScroll = openBody ? openBody.scrollTop : this._dialogScroll || 0;
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

    // The rebuild below replaces the <dialog> element wholesale, so the font
    // memo must forget the old element's size or _scaleDialogFont will skip
    // the write and leave the fresh dialog's chrome at card size.
    this._dialogFontPx = 0;

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
    // The controls overlay the chart rather than sitting under it: the expanded
    // dialog budgets its height from a fixed guess at how tall the chrome is
    // (item 26), and a new row of buttons would eat straight into that budget.
    const pannable = this._viewAdjustable() ? " pannable" : "";
    return `<div class="chartwrap${expanded ? " big" : ""}${pannable}">${chart}
      ${this._viewControlsHtml()}
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
        <div class="dlg-body">
          ${this._chartBlock(built, true)}
          ${this._whatIfHtml()}
        </div>
      </dialog>
    `;
  }

  /** The what-if panel, shown in the expanded view only.
   *
   * Two different questions live here, so they are kept visibly apart.
   *
   * "Today's slots" is about *this* day. The plan is drawn as draggable slots
   * on their own lanes under the chart, and moving them re-prices the day
   * against the published plan so the cost of the change is visible before it
   * is made. "Apply this plan" pins the arrangement through the
   * `apply_manual_plan` service; the optimizer then keeps the timing but is
   * still free to choose how hard to run, and safety limits still override it.
   *
   * "My usual schedule" is about *every* day: the hours the house is heated
   * and the hot water demand windows. "Temperatures" holds the two setpoints
   * those hours are measured against -- the comfort target and the usable hot
   * water minimum. They are split because a lone temperature slider inside a
   * section about scheduling reads as a stray control with no context; paired
   * under a heading of their own, both are obviously the same kind of setting.
   *
   * All of it is priced per month against a copy of the configuration on the
   * coordinator side, so exploring cannot disturb operation. Both temperature
   * sliders are debounced, and deliberately share one timer: two independent
   * debounces racing on one service call is how the delta ends up showing the
   * price of the previous drag. The time fields apply on an explicit button,
   * because editing a time range is not a drag gesture and half-typed times
   * should not trigger a solve. "Save as my schedule" writes all of it into the
   * config entry through `apply_schedule`, and asks for confirmation first.
   */
  _whatIfHtml() {
    if (!this._config.what_if) return "";
    const draft = this._whatIfDraft();
    const windows = draft.dhwWindows;
    const setpoint = this._planAttr("dhw_setpoint", null);
    const ceiling = this._dhwMinCeiling();
    // Re-clamp on every render rather than only when the draft is seeded: the
    // setpoint is configurable and may have moved since, and a slider whose
    // maximum was computed against a stale setpoint is precisely the bug this
    // item warns about. `clamped` is the value the user had *before* the clamp,
    // and is non-null only when it genuinely had to be lowered -- silently
    // reducing someone's hot water minimum deserves saying so out loud.
    let clamped = null;
    if (draft.dhwMin > ceiling) {
      clamped = draft.dhwMin;
      draft.dhwMin = ceiling;
    }
    return `
      <div class="whatif">
        <div class="wi-section">
          <div class="wi-group-title">Today's slots</div>
          <div class="wi-hint">
            Drag a slot along its lane at the bottom of the chart to move it,
            drag either edge to resize it, or right-click a lane to add and
            remove slots. Applying pins them for the next 20 hours.
          </div>
          ${this._overrideHtml()}
          <div class="wi-row wi-delta">${this._deltaHtml()}</div>
          <div class="wi-row wi-actions">
            <button type="button" class="wi-pin">Apply this plan</button>
            <button type="button" class="wi-revert">Undo my changes</button>
            ${
              this._manualOverride()
                ? `<button type="button" class="wi-auto">Back to automatic</button>`
                : ""
            }
          </div>
          <div class="wi-pin-result" role="status"></div>
        </div>

        <div class="wi-section">
          <div class="wi-group-title">My usual schedule</div>
          <div class="wi-hint">
            These are the recurring hours the optimizer plans against every
            day, not just today.
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

        <div class="wi-section">
          <div class="wi-group-title">Temperatures</div>
          <div class="wi-hint">
            How warm the house is kept during the heating day, and how cool the
            hot water tank is allowed to get inside a demand window. Both are
            priced the same way as the schedule above.
          </div>
          <div class="wi-row">
            <label class="wi-field">
              <span>Comfort temperature</span>
              <input type="range" class="wi-temp" min="16" max="24" step="0.5"
                value="${draft.comfort}" aria-label="Comfort temperature">
              <span class="wi-value wi-comfort-value">${draft.comfort.toFixed(1)}&nbsp;°C</span>
            </label>
          </div>
          <div class="wi-row">
            <label class="wi-field">
              <span>Minimum hot water</span>
              <input type="range" class="wi-dhw-min" min="${DHW_MIN_FLOOR}"
                max="${ceiling}" step="0.5" value="${draft.dhwMin}"
                aria-label="Minimum hot water temperature">
              <span class="wi-value wi-dhw-value">${draft.dhwMin.toFixed(1)}&nbsp;°C</span>
            </label>
          </div>
          <div class="wi-hint">
            ${
              setpoint === null
                ? `Capped at ${fmtTemp(ceiling)}&nbsp;°C, far enough below the
                   hot water setpoint to leave the tank a band to work in.`
                : `Capped at ${fmtTemp(ceiling)}&nbsp;°C: a
                   ${fmtTemp(setpoint - ceiling)}&nbsp;°C band below the
                   ${fmtTemp(setpoint)}&nbsp;°C setpoint, so the tank has room
                   to work in instead of chasing its target.`
            }
          </div>
          ${
            clamped
              ? `<div class="wi-hint wi-warn">Your saved minimum of
                   ${fmtTemp(clamped)}&nbsp;°C is above that limit, so the
                   slider shows ${fmtTemp(draft.dhwMin)}&nbsp;°C. Saving will
                   store the lower value.</div>`
              : ""
          }
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
        dhwMin: this._currentDhwMin(),
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

  /** Current usable hot water minimum, as configured. */
  _currentDhwMin() {
    return Math.min(
      this._planAttr("dhw_min_temperature", DHW_MIN_FALLBACK),
      this._dhwMinCeiling()
    );
  }

  /** Highest hot water minimum that still leaves a deadband under the setpoint.
   *
   * Computed by the integration and published on the plan sensor, so the margin
   * exists in one place: the backend validates `apply_schedule` against the same
   * number, and the card cannot drift away from it. The fallback only matters
   * before the first plan arrives, when no setpoint has been published yet.
   */
  _dhwMinCeiling() {
    const published = this._planAttr("dhw_min_temperature_max", null);
    return published === null ? DHW_MIN_FALLBACK : published;
  }

  _planAttr(name, fallback) {
    const st = this._stateOf(this._resolveEntity("space"));
    const raw = ((st && st.attributes) || {})[name];
    // `Number(null)` is 0, and 0 is finite -- so without this guard an
    // attribute the coordinator published as None would read as a real
    // measurement of zero rather than "not known", silently producing a 0 °C
    // comfort target or a hot water ceiling of nothing.
    if (raw === null || raw === undefined || raw === "") return fallback;
    const value = Number(raw);
    return Number.isFinite(value) ? value : fallback;
  }

  /** The manual override the integration is currently honouring, if any.
   *
   * Published by both plan sensors, so either will do; the space sensor is the
   * one the rest of the card already resolves.
   */
  _manualOverride() {
    for (const which of ["space", "dhw"]) {
      const st = this._stateOf(this._resolveEntity(which));
      const info = ((st && st.attributes) || {}).manual_override;
      if (info && info.active) return info;
    }
    return null;
  }

  /** How the override is going, in the user's terms.
   *
   * A pinned slot is not a guarantee: the optimizer releases pins that would
   * take the house below its comfort floor or the tank below its minimum. That
   * has to be said out loud, because the whole point of pinning is that the
   * user believes the plan they see is the plan that will run.
   */
  _overrideHtml() {
    const info = this._manualOverride();
    if (!info) return "";
    const until = info.expires_at ? new Date(info.expires_at) : null;
    const when =
      until && !Number.isNaN(until.getTime())
        ? ` until ${fmtExpiry(until)}`
        : "";
    const released =
      (info.released_space || []).length + (info.released_dhw || []).length;
    const note = released
      ? ` <span class="dearer">${released} slot${
          released === 1 ? " was" : "s were"
        } released to protect the house or the tank.</span>`
      : "";
    return `<div class="wi-row wi-override" role="status">Your slots are pinned${esc(
      when
    )}.${note}</div>`;
  }

  /** Demand windows the DHW plan sensor is currently planning against. */
  _currentDhwWindows() {
    const st = this._stateOf(this._resolveEntity("dhw"));
    const spec = ((st && st.attributes) || {}).dhw_windows;
    return parseWindows(spec);
  }

  /** Wire the buttons that act on today's hand-arranged slots. */
  _attachSlotActions(root) {
    const pin = root.querySelector(".wi-pin");
    if (pin) {
      pin.addEventListener("click", (ev) => {
        stop(ev);
        this._applyManualPlan();
      });
    }
    const revert = root.querySelector(".wi-revert");
    if (revert) {
      revert.addEventListener("click", (ev) => {
        stop(ev);
        this._resetRuns();
        this._render();
      });
    }
    const auto = root.querySelector(".wi-auto");
    if (auto) {
      auto.addEventListener("click", (ev) => {
        stop(ev);
        this._clearManualPlan();
      });
    }
  }

  _slotResult(message, cls) {
    const box = this.shadowRoot && this.shadowRoot.querySelector(".wi-pin-result");
    if (box) box.innerHTML = `<span class="${cls || ""}">${esc(message)}</span>`;
  }

  /** Pin the current arrangement for the manual-plan window.
   *
   * Only the editable part of the horizon is sent: the past cannot be
   * rescheduled, and pinning a slot that has already happened would be
   * meaningless.
   */
  _applyManualPlan() {
    if (!this._hass || !this._hass.callService) return;
    const [lo] = this._editBounds();
    const runs = this._draftRuns();
    const payload = {};
    for (const spec of this._laneSpecs()) {
      // Omitting a channel leaves it automatic; sending an empty list means
      // "off until the override expires". A channel whose plan sensor is
      // missing or has not published yet has an empty draft that means neither
      // of those things, so it must be left out rather than silently switched
      // off for the rest of the day.
      if (!this._forecastOf(spec.channel).length) continue;
      payload[`${spec.channel}_slots`] = (runs[spec.channel] || [])
        .filter((r) => r.end > lo)
        .map((r) => ({
          start: new Date(Math.max(r.start, lo)).toISOString(),
          end: new Date(r.end).toISOString(),
        }));
    }
    if (!Object.keys(payload).length) {
      this._slotResult("No plan to pin yet.", "dearer");
      return;
    }
    this._slotResult("Applying…");
    Promise.resolve(
      this._hass.callService(
        "heatpump_optimizer",
        "apply_manual_plan",
        payload,
        undefined,
        false,
        true
      )
    )
      .then((response) => {
        this._runsDirty = false;
        const applied = Object.values(
          (response && response.response && response.response.applied) || {}
        )[0];
        const until = applied && applied.expires_at
          ? new Date(applied.expires_at)
          : null;
        const when =
          until && !Number.isNaN(until.getTime())
            ? ` until ${fmtExpiry(until)}`
            : "";
        // Deliberately not a promise that these slots will run: the optimizer
        // releases a pin that would take the house or the tank below its
        // limits, and saying otherwise would be a lie the user acts on.
        this._slotResult(
          `Pinned${when}. These slots will be kept unless doing so would take` +
            ` the house or the tank below its limits.`,
          "cheaper"
        );
      })
      .catch((err) => {
        this._slotResult(
          `Could not apply: ${(err && err.message) || err}`,
          "dearer"
        );
      });
  }

  _clearManualPlan() {
    if (!this._hass || !this._hass.callService) return;
    this._slotResult("Clearing…");
    Promise.resolve(
      this._hass.callService("heatpump_optimizer", "clear_manual_plan", {})
    )
      .then(() => {
        this._resetRuns();
        this._slotResult("Back to automatic planning.");
        this._render();
      })
      .catch((err) => {
        this._slotResult(
          `Could not clear: ${(err && err.message) || err}`,
          "dearer"
        );
      });
  }

  /** Wire the what-if controls, if the panel is present. */
  _attachWhatIf(root) {
    const panel = root.querySelector(".whatif");
    if (!panel) return;

    // Every control stops propagation: without it, a click inside the panel
    // reaches the card handler and toggles the expanded view underneath.
    // Both temperature sliders share this handler, and therefore share the
    // single debounce timer it sets. Giving each its own timer would let two
    // solves race on one service call, and the delta would end up reporting the
    // price of whichever drag happened to land second.
    [".wi-temp", ".wi-dhw-min"].forEach((sel) => {
      root.querySelectorAll(sel).forEach((slider) => {
        slider.addEventListener("input", this._onWhatIfInput);
        slider.addEventListener("click", stop);
      });
    });
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
    const draft = this._whatIfDraft();
    const target = ev.target || {};
    const isDhw = !!(
      target.classList &&
      target.classList.contains &&
      target.classList.contains("wi-dhw-min")
    );
    if (isDhw) draft.dhwMin = value;
    else draft.comfort = value;

    // Each readout carries its own class. There are two `.wi-value` spans now,
    // so a lookup on the shared class would keep rewriting whichever came
    // first regardless of which slider actually moved.
    const label = this.shadowRoot.querySelector(
      isDhw ? ".wi-dhw-value" : ".wi-comfort-value"
    );
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
      d.dhwMin,
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
        "This replaces your configured heating hours, hot water windows and " +
        "temperatures, and reloads the integration. Press again to confirm.";
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
        dhw_min_temperature: draft.dhwMin,
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
      // Already accepted by SERVICE_SCHEMA_SIMULATE_PLAN and applied to the
      // scratch parameters by the coordinator, so pricing this needs no
      // backend change; only the save path below did.
      dhw_min_temperature: draft.dhwMin,
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

    this._chartSvgs(root).forEach((svg) => {
      svg.addEventListener("mousemove", this._onPointerMove);
      svg.addEventListener("mouseleave", this._onPointerLeave);
      svg.addEventListener("touchmove", this._onPointerMove, { passive: true });
      svg.addEventListener("touchend", this._onPointerLeave);
    });

    this._attachViewControls(root);
    this._attachWhatIf(root);
    this._attachSlotActions(root);
    this._attachSlotEditing(root);
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

    // Restore where the user was. Done after showModal, because a dialog that
    // is not yet in the top layer has no laid-out scroll height to set against.
    const body = dlg.querySelector(".dlg-body");
    if (body && this._dialogScroll) body.scrollTop = this._dialogScroll;
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
        /* Overlaid on the chart so the row costs no layout height -- the
           expanded dialog's height budget is already the tight one. Kept out of
           the top-right corner, which the solar axis uses. */
        .viewctl {
          position: absolute; top: 4px; left: 50%; transform: translateX(-50%);
          display: flex; gap: 2px; z-index: 4;
          opacity: 0; transition: opacity 120ms ease-in-out;
        }
        .chartwrap:hover .viewctl,
        .viewctl:focus-within { opacity: 1; }
        /* No hover on touch, so the controls have to be permanently visible
           there: they are the only way to zoom without a trackpad. */
        @media (hover: none) {
          .viewctl { opacity: 1; }
        }
        .viewctl button {
          width: 1.7em; height: 1.7em; padding: 0; line-height: 1;
          font: inherit; font-size: 0.85em; cursor: pointer;
          border: 1px solid var(--divider-color, #ccc); border-radius: 0.35em;
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color);
        }
        .viewctl button:disabled { opacity: 0.4; cursor: default; }
        .chartwrap.pannable svg { cursor: grab; }
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

        /* Expanded view.

           The width used to be min(96vw, calc((100vh - 168px) * RATIO)), where
           168px was a hardcoded guess at how tall the chrome around the chart
           would be. That guess was made when the dialog was a header, a legend
           and a chart; it never grew with the override banner, the delta row,
           the third button, the status line or the Temperatures section. Once
           the real chrome passed the budget the content ran past the dialog's
           painted background instead of being contained -- 449px past it at
           1400x700, measured.

           Worse than a stale number, it was a feedback loop: a shorter viewport
           made the dialog *wider*, and _scaleDialogFont derives the font every
           piece of chrome is sized from off the measured width, so the chrome
           grew in the same direction as the overflow.

           So the height budget is gone. The dialog is a flex column bounded by
           the viewport; the header and legend keep their natural height and
           everything below them scrolls. The width is still tied to viewport
           height, but only to keep the chart a sensible size -- nothing depends
           on guessing the chrome, and being wrong now costs a scrollbar rather
           than spilled content.

           The chart keeps its exact aspect ratio deliberately. It is drawn with
           preserveAspectRatio="none", so constraining its height instead would
           stretch every axis label horizontally. */
        dialog.expanded {
          box-sizing: border-box;
          width: min(96vw, calc(78vh * ${VIEW_RATIO}), 1700px);
          max-width: 96vw;
          /* vh is the *large* viewport: on a phone it includes the strip behind
             a retracted URL bar, so a dialog sized in vh can sit partly under
             browser chrome. dvh tracks what is actually visible. The vh line is
             the fallback for engines without dvh, and is no worse than the
             unbounded height this replaced. */
          max-height: 92vh;
          max-height: 92dvh;
          display: flex;
          flex-direction: column;
          border: none; border-radius: 12px; padding: 16px;
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color);
          box-shadow: 0 8px 32px rgba(0,0,0,0.35);
          overflow: hidden;
        }
        .dlg-body {
          flex: 1 1 auto;
          min-height: 0;
          overflow-y: auto;
          overflow-x: hidden;
          /* Room for the scrollbar so it never lands on top of the chart. */
          scrollbar-gutter: stable;
        }
        dialog.expanded::backdrop {
          background: rgba(0, 0, 0, 0.55);
        }
        .dlg-head {
          display: flex; align-items: center; gap: 8px;
          font-size: 1.25em; font-weight: 500; padding: 0 2px 10px 2px;
        }
        .dlg-head .title { flex: 1 1 auto; min-width: 0; }
        dialog.expanded .dlg-head,
        dialog.expanded .legend { flex: 0 0 auto; }
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

        /* Editable slot lanes */
        .slot { cursor: grab; }
        .slot.locked { cursor: not-allowed; }
        .slot-handle { cursor: ew-resize; }
        .lane { cursor: context-menu; }
        /* A drag that selects the chart's text instead of moving the slot is
           the single most common way this kind of editor feels broken. */
        .lanes { user-select: none; }
        .slot-menu {
          position: absolute; z-index: 5;
          background: var(--card-background-color, #fff);
          border: 1px solid var(--divider-color, #ccc);
          border-radius: 0.4em; padding: 0.2em;
          box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        .slot-menu button {
          display: block; width: 100%; text-align: left;
          font: inherit; border: none; background: none; cursor: pointer;
          padding: 0.4em 0.7em; border-radius: 0.3em;
          color: var(--primary-text-color);
        }
        .slot-menu button:hover {
          background: var(--secondary-background-color, #eee);
        }
        .whatif .wi-section + .wi-section {
          margin-top: 0.9em; padding-top: 0.7em;
          border-top: 1px solid var(--divider-color, #e0e0e0);
        }
        .whatif .wi-delta { align-items: baseline; gap: 0.6em; }
        .whatif .delta {
          font-size: 1.25em; font-weight: 600;
          font-variant-numeric: tabular-nums;
        }
        .whatif .wi-pin {
          border-color: var(--primary-color, #03a9f4);
          color: var(--primary-color, #03a9f4);
        }
        .whatif .wi-pin-result { margin-top: 0.4em; min-height: 1.2em; }

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
        /* A stored value the setpoint no longer allows. Warning rather than
           error: nothing is broken, but the number on screen is not the number
           that was saved, and that must not pass unremarked. */
        .whatif .wi-hint.wi-warn {
          color: var(--warning-color, #d98e00);
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

    // Value axes. Where two axes share a side, the inner one's title has only
    // the gap to the outer axis to live in, and that gap does not grow with
    // the font: at the expanded size "SEK/kWh" is wider than the 46 units
    // between the price and solar axes, so it used to run straight through
    // "W/m2". Measure the title and, when it does not fit, hang it off the
    // inside of its own axis line instead -- the strip above the plot frame
    // is empty, so the title stays beside the axis it names either way.
    const titleFits = (unit, room) =>
      textWidth(unit, font) + font * 0.6 <= room;
    const powerTitleInset = 44;
    const tempAnchor =
      axes.power && !titleFits("\u00b0C", powerTitleInset) ? "start" : "end";
    const priceAnchor =
      axes.solar && !titleFits("SEK/kWh", SOLAR_AXIS_INSET) ? "end" : "start";

    if (axes.temp)
      parts.push(
        this._valueAxis(
          axes.temp, plotL, plotB, plotH, "left", 0,
          scaleY, "temp", "\u00b0C", font, tempAnchor
        )
      );
    if (axes.power)
      parts.push(
        this._valueAxis(
          axes.power, plotL, plotB, plotH, "left", powerTitleInset,
          scaleY, "power", "kW", font
        )
      );
    if (axes.price)
      parts.push(
        this._valueAxis(
          axes.price, plotR, plotB, plotH, "right", 0,
          scaleY, "price", "SEK/kWh", font, priceAnchor
        )
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

    // Editable slot lanes, and the geometry a pointer event needs to turn a
    // screen coordinate back into a time.
    if (this._editingEnabled()) {
      this._geom = {
        windowStart, windowEnd, plotL, plotW, plotR, plotB, font,
      };
      parts.push(`<g class="lanes">${this._laneGroupInner()}</g>`);
    } else {
      this._geom = null;
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

  /** The right-click menu for a lane.
   *
   * Rendered as plain HTML positioned over the card rather than as SVG, so it
   * is not clipped by the chart and inherits the dialog's font.
   */
  _openSlotMenu(channel, at, clientX, clientY, svg) {
    const root = this.shadowRoot;
    if (!root) return;
    this._closeSlotMenu();
    const runs = this._draftRuns()[channel] || [];
    const index = SlotModel.indexAt(runs, at);
    const [lo] = this._editBounds();
    const editable = index >= 0 && runs[index].end > lo;

    // Anchored to the chart it was opened from: when the card is expanded
    // there are two, and the menu must not land on the wrong one.
    const host = this._wrapOf(svg);
    if (!host) return;
    const rect = host.getBoundingClientRect
      ? host.getBoundingClientRect()
      : { left: 0, top: 0 };
    const menu = document.createElement("div");
    menu.className = "slot-menu";
    menu.style.left = `${clientX - (rect.left || 0)}px`;
    menu.style.top = `${clientY - (rect.top || 0)}px`;
    const label = channel === "dhw" ? "hot water" : "heating";
    menu.innerHTML = editable
      ? `<button type="button" data-act="remove">Remove this ${esc(label)} slot</button>`
      : `<button type="button" data-act="add">Add a ${esc(label)} slot here</button>`;

    menu.addEventListener("click", (ev) => {
      const act = ((ev.target || {}).dataset || {}).act;
      stop(ev);
      if (act === "add") {
        this._commitRuns(
          channel,
          SlotModel.add(runs, at, PLAN_STEP_MS, this._editBounds())
        );
      } else if (act === "remove") {
        this._commitRuns(channel, SlotModel.remove(runs, index));
      }
      this._closeSlotMenu();
      this._render();
    });
    host.appendChild(menu);
    this._slotMenu = menu;
  }

  _closeSlotMenu() {
    const menu = this._slotMenu;
    if (menu && menu.parentNode && menu.parentNode.removeChild) {
      menu.parentNode.removeChild(menu);
    }
    this._slotMenu = null;
  }

  /** What the current arrangement would cost against the published plan.
   *
   * Both sides are priced over the same horizon at the same prices, so the
   * difference isolates the effect of moving the slots. It is an estimate:
   * the arrangement fixes when the pump runs, not how hard, and the optimizer
   * still chooses the power within each slot.
   */
  _costDelta() {
    let planned = 0;
    let edited = 0;
    const runs = this._draftRuns();
    for (const spec of this._laneSpecs()) {
      const forecast = this._forecastOf(spec.channel);
      if (!forecast.length) continue;
      const power = SlotModel.typicalPower(forecast, spec.field);
      const base = SlotModel.runsFrom(
        forecast, spec.field, 0.05, PLAN_STEP_MS
      );
      planned += SlotModel.cost(base, forecast, power, PLAN_STEP_MS);
      edited += SlotModel.cost(
        runs[spec.channel] || [], forecast, power, PLAN_STEP_MS
      );
    }
    return { planned, edited, delta: edited - planned };
  }

  /** The currency to price the delta in.
   *
   * The plan carries prices but not a currency, so take Home Assistant's own
   * configured currency rather than assuming the author's. `currency:` in the
   * card config still wins, for installs where the two disagree.
   */
  _currency() {
    const hass = this._hass || {};
    return (
      this._config.currency ||
      (hass.config && hass.config.currency) ||
      "SEK"
    );
  }

  _deltaHtml() {
    const { planned, edited, delta } = this._costDelta();
    if (!Number.isFinite(delta) || (!planned && !edited)) {
      return `<span class="wi-hint">No plan data to compare against yet.</span>`;
    }
    const cur = this._currency();
    const cls = delta < -0.005 ? "cheaper" : delta > 0.005 ? "dearer" : "";
    const sign = delta > 0 ? "+" : "";
    const verdict =
      cls === "cheaper" ? "cheaper" : cls === "dearer" ? "dearer" : "the same";
    return `
      <span class="delta ${cls}">${sign}${delta.toFixed(2)}&nbsp;${esc(cur)}</span>
      <span class="wi-hint">${verdict} than the saved plan
        (${planned.toFixed(2)} → ${edited.toFixed(2)}&nbsp;${esc(cur)}, estimated)</span>`;
  }

  _updateDelta() {
    const root = this.shadowRoot;
    const box = root && root.querySelector(".wi-delta");
    if (box) box.innerHTML = this._deltaHtml();
  }

  /** Wheel over the chart: pinch to zoom, two fingers sideways to pan.
   *
   * A plain vertical wheel is deliberately left alone. The card sits in a
   * dashboard the user scrolls, and a chart that swallowed the scroll wheel
   * would trap the page the moment the pointer crossed it. Trackpad pinch
   * arrives as a wheel with `ctrlKey` set, which is the gesture people already
   * expect to zoom.
   */
  _onChartWheel(ev) {
    if (!this._viewAdjustable()) return;
    const zooming = ev.ctrlKey || ev.metaKey;
    const sideways = Math.abs(ev.deltaX) > Math.abs(ev.deltaY);
    const panning = !zooming && (ev.shiftKey || sideways);
    if (!zooming && !panning) return;
    if (ev.preventDefault) ev.preventDefault();
    stop(ev);

    if (zooming) {
      const at = this._timeAtClientX(ev.currentTarget, ev.clientX);
      this._zoomView(ev.deltaY > 0 ? VIEW_ZOOM_STEP : 1 / VIEW_ZOOM_STEP, at);
      return;
    }
    const span = this._viewSpan();
    const delta = sideways ? ev.deltaX : ev.deltaY;
    this._panView((delta / 600) * span);
  }

  /** The span currently on screen, view or default. */
  _viewSpan() {
    if (this._view) return this._view.span;
    const lim = this._viewLimits;
    return lim ? lim.defaultEnd - lim.floor : 1;
  }

  /** The window currently on screen, as the zoom and pan maths sees it. */
  _viewCurrent() {
    const lim = this._viewLimits;
    if (this._view) return this._view;
    return { start: lim.floor, span: lim.defaultEnd - lim.floor };
  }

  /** Drag the chart background sideways to pan.
   *
   * Only the background: a pointerdown that landed on a lane belongs to the
   * slot editor, and stealing it would make slots undraggable. The move and up
   * handlers go on `window` rather than the svg because panning re-renders,
   * which replaces the element the gesture started on -- listeners bound to it
   * would stop firing halfway through the drag.
   */
  _onPanDown(ev) {
    if (!this._viewAdjustable()) return;
    if (((ev.target || {}).dataset || {}).channel) return;
    const svg = ev.currentTarget;
    const rect = svg && svg.getBoundingClientRect ? svg.getBoundingClientRect() : null;
    if (!rect || !rect.width) return;
    // `_geom` only exists while the lanes do (what_if enabled). Without it,
    // fall back to the nominal plot width rather than the whole viewBox, or a
    // drag would track noticeably slower than the pointer.
    const plotW = this._geom
      ? this._geom.plotW
      : VIEW_W - MARGIN.left - MARGIN.right;
    const pxPerViewUnit = rect.width / VIEW_W;
    const plotPx = plotW * pxPerViewUnit;
    if (!plotPx) return;

    // Without this the drag selects the axis labels and, on some browsers,
    // starts a native image drag of the svg.
    if (ev.preventDefault) ev.preventDefault();
    const pan = {
      last: ev.clientX,
      perPx: this._viewSpan() / plotPx,
      moved: false,
      move: null,
      up: null,
    };
    pan.move = (moveEv) => {
      const dx = moveEv.clientX - pan.last;
      if (!dx) return;
      pan.last = moveEv.clientX;
      // A drag only counts as a pan once it has actually moved, so a plain
      // click on the chart still opens the expanded view.
      pan.moved = true;
      // Drag left to move forward in time: the content follows the pointer.
      this._panView(-dx * pan.perPx);
    };
    pan.up = () => {
      if (pan.moved) this._suppressClick = true;
      this._pan = null;
      if (typeof window === "undefined") return;
      window.removeEventListener("pointermove", pan.move);
      window.removeEventListener("pointerup", pan.up);
      window.removeEventListener("pointercancel", pan.up);
    };
    this._pan = pan;
    if (typeof window !== "undefined") {
      window.addEventListener("pointermove", pan.move);
      window.addEventListener("pointerup", pan.up);
      window.addEventListener("pointercancel", pan.up);
    }
  }

  /** Zoom and reset buttons: the keyboard- and touch-reachable path.
   *
   * Wheel and drag cover a trackpad, but neither is available to someone on a
   * phone or tabbing through the card, and a zoom that only exists as a gesture
   * is a zoom half the users never find.
   */
  _viewControlsHtml() {
    if (!this._viewAdjustable()) return "";
    const zoomed = this._view !== null;
    return `
      <div class="viewctl">
        <button type="button" class="vc-out" title="Zoom out"
          aria-label="Zoom out">&minus;</button>
        <button type="button" class="vc-in" title="Zoom in"
          aria-label="Zoom in">+</button>
        <button type="button" class="vc-reset" title="Show the whole plan"
          aria-label="Show the whole plan"${zoomed ? "" : " disabled"}>&#8634;</button>
      </div>`;
  }

  _attachViewControls(root) {
    this._chartSvgs(root).forEach((svg) => {
      svg.addEventListener("wheel", this._onChartWheel, { passive: false });
      svg.addEventListener("pointerdown", this._onPanDown);
    });
    const wire = (sel, fn) =>
      root.querySelectorAll(sel).forEach((el) =>
        el.addEventListener("click", (ev) => {
          stop(ev);
          fn();
        })
      );
    wire(".vc-in", () => this._zoomView(1 / VIEW_ZOOM_STEP, null));
    wire(".vc-out", () => this._zoomView(VIEW_ZOOM_STEP, null));
    wire(".vc-reset", () => this._resetView());
  }

  /** Narrow the default window to the panned/zoomed view, and record its limits.
   *
   * Called on every build so the limits track incoming data: the plan's extent
   * moves forward as new forecasts arrive, and a view clamped against the
   * extent of ten minutes ago would slowly drift out of range.
   *
   * Returns the default window untouched while `_view` is null, so a card
   * nobody has interacted with renders exactly as it did before this existed.
   */
  _applyView(defaultStart, defaultEnd, dataEnd) {
    const defaultSpan = Math.max(defaultEnd - defaultStart, 1);
    // Zooming out stops at the plan, not at the configured plot width:
    // `cfg.hours` goes up to a week, while the optimizer's horizon defaults to
    // 24 h, and the difference is empty chart.
    const maxSpan = Math.max(
      Math.min(defaultSpan, Math.max(dataEnd - defaultStart, VIEW_MIN_SPAN_MS)),
      VIEW_MIN_SPAN_MS
    );
    const minSpan = Math.min(VIEW_MIN_SPAN_MS, maxSpan);
    // The right edge the window may not pass: the plan's end, and never beyond
    // the configured plot width.
    const rightBound = Math.max(
      Math.min(dataEnd, defaultEnd),
      defaultStart + minSpan
    );
    // `defaultEnd` is kept as well as `rightBound`: the two differ whenever the
    // configured plot window is wider than the plan, and a zoom that mistook
    // the plan's extent for what is currently on screen would compute its
    // anchor against a window the user is not looking at.
    this._viewLimits = {
      floor: defaultStart,
      defaultEnd,
      rightBound,
      minSpan,
      maxSpan,
    };

    if (!this._view) return { start: defaultStart, end: defaultEnd };

    const span = clampNum(this._view.span, minSpan, maxSpan);
    const maxStart = Math.max(defaultStart, rightBound - span);
    const start = clampNum(this._view.start, defaultStart, maxStart);
    this._view = { start, span };
    return { start, end: start + span };
  }

  /** Whether panning and zooming can do anything at all.
   *
   * With a plan no longer than the minimum span there is nothing to pan across
   * and nothing to zoom out to, and controls that cannot move are worse than
   * no controls.
   */
  _viewAdjustable() {
    const lim = this._viewLimits;
    return !!lim && lim.rightBound - lim.floor > lim.minSpan * 1.05;
  }

  /** Zoom by `factor`, holding the time under `anchorT` still.
   *
   * Anchoring matters: zooming around the window centre walks whatever the user
   * is pointing at off the screen, which makes repeated zooming feel like it is
   * fighting back.
   */
  _zoomView(factor, anchorT) {
    const lim = this._viewLimits;
    if (!lim) return;
    const current = this._viewCurrent();
    const span = clampNum(current.span * factor, lim.minSpan, lim.maxSpan);
    const anchor =
      anchorT === undefined || anchorT === null
        ? current.start + current.span / 2
        : clampNum(anchorT, current.start, current.start + current.span);
    // Keep the anchor at the same fraction across the window.
    const frac = (anchor - current.start) / (current.span || 1);
    this._view = { start: anchor - frac * span, span };
    this._renderView();
  }

  /** Slide the window by `deltaMs`, without changing its span. */
  _panView(deltaMs) {
    const lim = this._viewLimits;
    if (!lim) return;
    const current = this._viewCurrent();
    this._view = { start: current.start + deltaMs, span: current.span };
    this._renderView();
  }

  _resetView() {
    if (!this._view) return;
    this._view = null;
    this._renderView();
  }

  /** Redraw after a view change, at most once per frame.
   *
   * A view change moves every series, not just the lanes, so unlike a slot drag
   * there is nothing narrower to refresh. `_render` replaces the shadow root,
   * which is why the pan gesture listens on the window rather than on the svg:
   * the element under the pointer is gone by the next event.
   */
  _renderView() {
    if (this._viewFrame) return;
    const run = () => {
      this._viewFrame = 0;
      // Deliberately not clearing `_sig`: it is what stops the next data
      // refresh from throwing away an in-progress slot edit, and a view change
      // is not a reason to discard the draft the user is arranging.
      this._render();
    };
    this._viewFrame =
      typeof requestAnimationFrame === "function"
        ? requestAnimationFrame(run)
        : setTimeout(run, 16);
  }

  /** Turn a screen x into a time on the chart's axis.
   *
   * The chart is drawn in a fixed viewBox and stretched to fit, so screen
   * pixels and viewBox units are not interchangeable; the measured width is
   * the only thing that relates them.
   */
  _timeAtClientX(svg, clientX) {
    const geom = this._geom;
    if (!geom || !svg) return null;
    const rect = svg.getBoundingClientRect ? svg.getBoundingClientRect() : null;
    if (!rect || !rect.width) return null;
    const vx = ((clientX - rect.left) / rect.width) * VIEW_W;
    return geom.windowStart + ((vx - geom.plotL) / geom.plotW) *
      (geom.windowEnd - geom.windowStart);
  }

  /** Drag to move a slot, drag its edge to resize, right-click to add or
   * remove. Wired by delegation on the svg, because the chart markup is
   * rebuilt wholesale on every refresh and per-rect listeners would not
   * survive it.
   */
  _attachSlotEditing(root) {
    if (!this._editingEnabled()) return;
    const svgs = this._chartSvgs(root);
    if (!svgs.length) return;

    const onDown = (svg, ev) => {
      const target = ev.target || {};
      const data = target.dataset || {};
      if (!data.channel) return;
      const at = this._timeAtClientX(svg, ev.clientX);
      if (at === null) return;
      const channel = data.channel;
      const runs = this._draftRuns()[channel] || [];
      let index = data.index === undefined ? -1 : Number(data.index);
      if (index < 0) index = SlotModel.indexAt(runs, at);
      if (index < 0) return;
      // A slot outside the editable range -- already run, or beyond the point
      // where the override expires -- must not be draggable.
      const [lo, hi] = this._editBounds();
      const run = runs[index];
      if (run && (run.end <= lo || run.start >= hi)) return;

      this._drag = {
        channel,
        index,
        edge: data.edge || null,
        from: at,
        // Edits apply to the arrangement as it was when the drag began, so a
        // slow drag does not compound its own deltas.
        original: runs.map((r) => ({ ...r })),
      };
      stop(ev);
      if (ev.preventDefault) ev.preventDefault();
    };

    const onMove = (svg, ev) => {
      const drag = this._drag;
      if (!drag) return;
      const at = this._timeAtClientX(svg, ev.clientX);
      if (at === null) return;
      drag.moved = true;
      const delta = at - drag.from;
      const bounds = this._editBounds();
      const next = drag.edge
        ? SlotModel.resize(
            drag.original, drag.index, drag.edge, delta, PLAN_STEP_MS, bounds
          )
        : SlotModel.move(
            drag.original, drag.index, delta, PLAN_STEP_MS, bounds
          );
      this._commitRuns(drag.channel, next);
    };

    const onUp = () => {
      if (!this._drag) return;
      // The browser synthesises a click after pointerup — preventDefault on
      // pointerdown suppresses compatibility mouse events but not click — and
      // on the inline chart that click bubbles to ha-card and pops the
      // expanded dialog open at the end of every drag. Same one-shot
      // suppression the pan gesture uses; a drag ending off-svg spends it on
      // nothing, which the pan path already accepts.
      if (this._drag.moved) this._suppressClick = true;
      this._drag = null;
      this._render();
    };

    const onContext = (svg, ev) => {
      const data = (ev.target || {}).dataset || {};
      if (!data.channel) return;
      const at = this._timeAtClientX(svg, ev.clientX);
      if (at === null) return;
      if (ev.preventDefault) ev.preventDefault();
      stop(ev);
      this._openSlotMenu(data.channel, at, ev.clientX, ev.clientY, svg);
    };

    for (const svg of svgs) {
      svg.addEventListener("pointerdown", (ev) => onDown(svg, ev));
      svg.addEventListener("pointermove", (ev) => onMove(svg, ev));
      svg.addEventListener("pointerup", onUp);
      svg.addEventListener("pointerleave", onUp);
      svg.addEventListener("contextmenu", (ev) => onContext(svg, ev));
    }
  }

  _commitRuns(channel, runs) {
    this._draftRuns();
    this._runs[channel] = runs;
    this._runsDirty = true;
    this._refreshLanes();
  }

  /** Redraw only what a drag changes.
   *
   * A full re-render on every pointer move would rebuild the shadow root
   * dozens of times a second and lose the drag with it.
   */
  _refreshLanes() {
    const root = this.shadowRoot;
    if (!root) return;
    if (this._geom) {
      const inner = this._laneGroupInner();
      root.querySelectorAll(".lanes").forEach((group) => {
        group.innerHTML = inner;
      });
    }
    this._updateDelta();
  }

  /** Whether the on-chart schedule editor is available. */
  _editingEnabled() {
    return !!this._config.what_if;
  }

  /** The two editable channels, in the order they are drawn. */
  _laneSpecs() {
    return [
      { channel: "dhw", label: "Hot water", field: "dhw_power", color: "#e0544e" },
      { channel: "space", label: "Heating", field: "space_power", color: "#4a90e2" },
    ];
  }

  /** Earliest time a slot may be edited.
   *
   * The past cannot be rescheduled, and an override only ever applies from now
   * on, so editing has to stop at the current step boundary rather than at the
   * start of the horizon.
   */
  _editFloor() {
    const start = this._geom ? this._geom.windowStart : Date.now();
    return Math.max(start, SlotModel.snap(Date.now(), PLAN_STEP_MS));
  }

  /** The last instant a hand-arranged slot can reach.
   *
   * Three separate limits, and the smallest wins:
   *
   * 1. **The expiry this card would send if the user applied right now** --
   *    `now + MANUAL_PLAN_WINDOW_HOURS`, published by the integration rather
   *    than copied here so the two cannot drift. Deliberately *not* the expiry
   *    of the override currently in force: an override applied 15 hours ago
   *    expires in 5, but the user editing now is composing a new plan that will
   *    last the full window from this moment. Deriving the ceiling from the
   *    active override would shrink the editable window as the day wore on and
   *    stop the user extending their own plan.
   * 2. **The end of the plan.** Past it there is nothing to pin.
   * 3. **The visible window**, which pan and zoom can narrow. Without this a
   *    slot could be dragged out of the region the pointer can actually reach.
   *
   * Beyond the first of these, `manual_plan.channel_pins` frees every step at or
   * after the expiry, so a slot shown as pinned there would quietly do nothing.
   */
  _editCeiling() {
    const visibleEnd = this._geom ? this._geom.windowEnd : Infinity;
    const windowHours = this._planAttr(
      "manual_plan_window_hours",
      MANUAL_PLAN_WINDOW_FALLBACK_H
    );
    const applyEnd = Date.now() + windowHours * 3600 * 1000;
    const planEnd = this._planEnd();
    return Math.min(visibleEnd, applyEnd, planEnd);
  }

  /** The last timestamp the published plan covers. */
  _planEnd() {
    let end = -Infinity;
    for (const channel of ["space", "dhw"]) {
      const fc = this._forecastOf(channel);
      if (!fc.length) continue;
      const t = Date.parse(fc[fc.length - 1].t);
      if (Number.isFinite(t)) end = Math.max(end, t + PLAN_STEP_MS);
    }
    return end === -Infinity ? Infinity : end;
  }

  _editBounds() {
    return [this._editFloor(), this._editCeiling()];
  }

  /** The arrangement being edited, seeded from the published plan.
   *
   * Held on the instance because a data refresh rebuilds the whole shadow
   * root; without this, an incoming plan update would throw away a drag the
   * user was halfway through.
   */
  _draftRuns() {
    if (!this._runs) {
      this._runs = {};
      for (const spec of this._laneSpecs()) {
        this._runs[spec.channel] = SlotModel.runsFrom(
          this._forecastOf(spec.channel), spec.field, 0.05, PLAN_STEP_MS
        );
      }
      this._runsDirty = false;
    }
    return this._runs;
  }

  /** Discard local edits and follow the published plan again. */
  _resetRuns() {
    this._runs = null;
    this._runsDirty = false;
  }

  _forecastOf(channel) {
    const st = this._stateOf(this._resolveEntity(channel));
    const fc = ((st && st.attributes) || {}).forecast;
    return Array.isArray(fc) ? fc : [];
  }

  /** The lanes, their slots and the grab handles, as SVG.
   *
   * Rebuilt from the recorded geometry rather than from the chart's locals, so
   * a drag can redraw the lanes alone without re-rendering the whole card.
   */
  _laneGroupInner() {
    const geom = this._geom;
    if (!geom) return "";
    const { windowStart, windowEnd, plotL, plotW, plotR, plotB, font } = geom;
    const span = windowEnd - windowStart || 1;
    const scaleX = (t) => plotL + ((t - windowStart) / span) * plotW;
    const runs = this._draftRuns();
    const [lo, hi] = this._editBounds();
    const specs = this._laneSpecs();
    const out = [];
    const clampX = (t) => Math.max(plotL, Math.min(plotR, scaleX(t)));

    specs.forEach((spec, row) => {
      const y =
        plotB - LANE_BOTTOM_INSET - (specs.length - row) * (LANE_H + LANE_GAP);
      // The track, so an empty lane is still an obvious drop target.
      out.push(
        `<rect class="lane" data-channel="${spec.channel}" x="${plotL}" y="${y}" width="${
          plotR - plotL
        }" height="${LANE_H}" rx="2" fill="var(--secondary-text-color,#888)" fill-opacity="0.07"/>`
      );
      out.push(
        `<text class="lane-label" x="${plotL + 4}" y="${
          y + LANE_H - 4
        }" font-size="${font * 0.8}" fill="var(--secondary-text-color,#888)">${esc(
          spec.label
        )}</text>`
      );
      // The parts of the lane that cannot be changed: what has already run,
      // and what lies beyond the point where the override expires.
      const floorX = clampX(lo);
      if (floorX > plotL) {
        out.push(
          `<rect class="lane-past" x="${plotL}" y="${y}" width="${
            floorX - plotL
          }" height="${LANE_H}" fill="var(--secondary-text-color,#888)" fill-opacity="0.12"/>`
        );
      }
      const ceilX = clampX(hi);
      if (ceilX < plotR) {
        out.push(
          `<rect class="lane-past" x="${ceilX}" y="${y}" width="${
            plotR - ceilX
          }" height="${LANE_H}" fill="var(--secondary-text-color,#888)" fill-opacity="0.12"/>`
        );
      }

      (runs[spec.channel] || []).forEach((run, index) => {
        // Zooming can put a run wholly outside the window. Clamping alone would
        // collapse it onto the edge and leave a one-pixel sliver pretending to
        // be a slot, so drop it instead. `index` still refers to its place in
        // the full array, which is what hit-testing and editing use.
        if (run.end <= windowStart || run.start >= windowEnd) return;
        const x1 = clampX(run.start);
        const x2 = clampX(run.end);
        const w = Math.max(1, x2 - x1);
        const locked = run.end <= lo || run.start >= hi;
        out.push(
          `<rect class="slot${locked ? " locked" : ""}" data-channel="${
            spec.channel
          }" data-index="${index}" x="${x1}" y="${y}" width="${w}" height="${LANE_H}" rx="2" fill="${
            spec.color
          }" fill-opacity="${locked ? 0.35 : 0.85}"/>`
        );
        if (locked) return;
        // Explicit edge handles: without them a narrow slot is impossible to
        // resize, because the whole rect reads as "move".
        for (const edge of ["start", "end"]) {
          const ex = edge === "start" ? x1 : x2 - LANE_EDGE_GRAB;
          out.push(
            `<rect class="slot-handle" data-channel="${spec.channel}" data-index="${index}" data-edge="${edge}" x="${ex}" y="${y}" width="${LANE_EDGE_GRAB}" height="${LANE_H}" fill="#fff" fill-opacity="0.001"/>`
          );
        }
      });
    });
    return out.join("");
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
    axis, xBase, plotB, plotH, side, inset, scaleY, axisName, unit, font,
    titleAnchor
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
    // The title sits on the strip above the plot frame, normally running away
    // from the chart like the tick labels do. When that would run it into the
    // next axis out, the caller flips it to the other side of its own axis
    // line, where the strip above the plot is empty.
    const uy = MARGIN.top - 4;
    const ta = titleAnchor || anchor;
    const ux = ta === "end" ? x - 5 : x + 5;
    out.push(
      `<text x="${ux}" y="${uy}" font-size="${size}" text-anchor="${ta}" fill="var(--secondary-text-color,#888)">${esc(
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
    // A pan ends with a click on the chart. Without this, dragging the plan
    // sideways would open the expanded view every time the drag finished.
    if (this._suppressClick) {
      this._suppressClick = false;
      return;
    }
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
    // Reopening should start at the top rather than resuming a scroll position
    // from a session the user has already dismissed.
    this._dialogScroll = 0;
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

  /** The chart svgs, and only those.
   *
   * The expand button carries an inline `<svg>` icon and sits above the chart
   * in the markup, so `querySelector("svg")` returns an 18px icon rather than
   * the plot. Every chart is wrapped in a `.chartwrap`; the icon is not.
   */
  _chartSvgs(root) {
    const scope = root || this.shadowRoot;
    if (!scope) return [];
    return [...scope.querySelectorAll(".chartwrap svg")];
  }

  _cacheRect() {
    const svg = this._chartSvgs()[0];
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
// Exposed so the editing model can be exercised without a browser.
HeatpumpOptimizerCard.slots = SlotModel;

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
