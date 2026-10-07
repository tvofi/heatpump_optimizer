/* D4 round-4: tests/card_drift.mjs's STATES, driven in real Chromium.
 *
 * card_drift.mjs drives the card inside tests/card_rig.mjs's vm context,
 * whose DOM stub returns a constant 900x400 rect and fires listeners off a
 * private `_listeners` registry. Nothing in it can answer a geometry
 * question. This file is the same 34 states re-expressed against real DOM:
 * real elements, real dispatchEvent, real coordinates taken from real rects.
 *
 * Each driver returns { ok, note } so a vacuous cell (a state that silently
 * did not take) is visible in the results rather than reported as a pass.
 */
(function () {
  const D4 = (window.__D4 = window.__D4 || {});
  const HOUR = 3600000;
  const SOLAR_ID = "sensor.heat_pump_optimizer_solar_irradiance";
  const SPACE = "sensor.heat_pump_optimizer_space_heating_plan";
  const DHW = "sensor.heat_pump_optimizer_dhw_heating_plan";
  D4.IDS = { SOLAR_ID, SPACE, DHW };

  // ---- state builders (ports of tests/card_rig.mjs) ----
  const solarForecastFor = (plan) =>
    plan.space_plan.forecast.map((p, i) => ({
      t: p.t,
      ghi: Math.max(0, 400 * Math.sin((i / plan.space_plan.forecast.length) * Math.PI)),
    }));

  function planStates(plan) {
    return {
      [SOLAR_ID]: { state: "120", attributes: {
        forecast: solarForecastFor(plan), source: "open_meteo",
        friendly_name: "Solar Irradiance", plan_kind: "solar" } },
      [SPACE]: { state: "3 slots planned", attributes: {
        forecast: plan.space_plan.forecast, slots: plan.space_plan.slots,
        total_energy_kwh: plan.space_plan.total_energy_kwh,
        total_cost: plan.space_plan.total_cost,
        active_now: plan.space_plan.active_now,
        friendly_name: "Space Heating Plan", plan_kind: "space" } },
      [DHW]: { state: "4 slots planned", attributes: {
        forecast: plan.dhw_plan.forecast, slots: plan.dhw_plan.slots,
        total_energy_kwh: plan.dhw_plan.total_energy_kwh,
        total_cost: plan.dhw_plan.total_cost,
        active_now: plan.dhw_plan.active_now,
        friendly_name: "DHW Heating Plan", plan_kind: "dhw" } },
    };
  }
  D4.planStates = planStates;

  const setupSensorStates = () => ({
    "sensor.livingroom": { state: "21.3", attributes: { unit_of_measurement: "°C" } },
    "sensor.tank": { state: "47.5", attributes: { unit_of_measurement: "°C" } },
    "sensor.outside": { state: "unavailable", attributes: {} },
  });

  const TEMP_DOMAINS = ["sensor", "number", "input_number"];
  function qaTopologies() {
    const base = {
      two_zone: true, dhw: true, valve_mode: "manual",
      buffer: { volume_l: 750, is_store: true, max_temp: 70 },
      wood: { present: true, volume_l: 500 },
      edges: [["heat_pump", "buffer_tank"], ["buffer_tank", "mixing_valve"],
        ["mixing_valve", "upper_zone"], ["mixing_valve", "lower_zone"],
        ["wood_tank", "buffer_tank"], ["heat_pump", "dhw_tank"]],
      slots: [
        { key: "indoor_temp_entity", label: "Indoor temperature", place: "upper_zone",
          entity: "sensor.livingroom", domains: TEMP_DOMAINS },
        { key: "lower_floor_temp_entity", label: "Lower floor temperature",
          place: "lower_zone", entity: null, domains: TEMP_DOMAINS },
        { key: "buffer_tank_temp_entity", label: "Buffer tank temperature",
          place: "buffer_tank", entity: "sensor.tank", domains: TEMP_DOMAINS },
        { key: "wood_tank_top_entity", label: "Wood tank top", place: "wood_tank",
          entity: null, domains: TEMP_DOMAINS },
        { key: "outdoor_temp_entity", label: "Outdoor temperature", place: "outdoor",
          entity: "sensor.outside", domains: TEMP_DOMAINS },
        { key: "heat_pump_switch_entity", label: "Heat pump switch", place: "heat_pump",
          entity: null, domains: ["switch", "input_boolean", "climate"] },
      ],
    };
    const twoTank = JSON.parse(JSON.stringify(base));
    twoTank.two_tank_modelled = true;
    twoTank.layout = "two_tank_4way";
    twoTank.edges = [["heat_pump", "buffer_tank"], ["buffer_tank", "mixing_valve"],
      ["wood_tank", "mixing_valve"], ["mixing_valve", "upper_zone"],
      ["mixing_valve", "lower_zone"], ["heat_pump", "dhw_tank"]];
    twoTank.slots = base.slots.concat([
      { key: "mixing_valve_target_entity", label: "Valve target", place: "mixing_valve",
        entity: null, domains: TEMP_DOMAINS },
      { key: "valve_outlet_temp_entity", label: "Valve outlet temperature",
        place: "mixing_valve", entity: null, domains: TEMP_DOMAINS },
    ]);
    const coil = JSON.parse(JSON.stringify(twoTank));
    coil.dhw_wood_coil = true;
    coil.edges = twoTank.edges.concat([["wood_tank", "dhw_tank"]]);
    coil.slots.push({ key: "dhw_temp_entity", label: "Hot water temperature",
      place: "dhw_tank", entity: null, domains: TEMP_DOMAINS });
    return { base, twoTank, coil };
  }

  function layoutCatalogTopo() {
    const EDGES = {
      no_valve: [["heat_pump", "buffer_tank"], ["buffer_tank", "upper_zone"], ["buffer_tank", "lower_zone"]],
      single_tank_valve: [["heat_pump", "buffer_tank"], ["buffer_tank", "mixing_valve"],
        ["mixing_valve", "upper_zone"], ["mixing_valve", "lower_zone"]],
      two_tank_4way: [["heat_pump", "buffer_tank"], ["buffer_tank", "mixing_valve"],
        ["wood_tank", "mixing_valve"], ["mixing_valve", "upper_zone"], ["mixing_valve", "lower_zone"]],
      valve_upper_direct_slab: [["heat_pump", "buffer_tank"], ["buffer_tank", "mixing_valve"],
        ["mixing_valve", "upper_zone"], ["buffer_tank", "lower_zone"]],
      slab_shunt: [["heat_pump", "buffer_tank"], ["buffer_tank", "mixing_valve"],
        ["mixing_valve", "upper_zone"], ["buffer_tank", "slab_shunt"], ["slab_shunt", "lower_zone"]],
    };
    const catalog = [
      { key: "no_valve", label: "No mixing valve", description: "",
        requirement: "no throttling mixing valve configured", selectable: true, valid: false, edges: EDGES.no_valve },
      { key: "single_tank_valve", label: "One tank behind a valve", description: "",
        requirement: "a throttling mixing valve", selectable: true, valid: true, edges: EDGES.single_tank_valve },
      { key: "two_tank_4way", label: "Two tanks, one 4-way valve", description: "",
        requirement: "a throttling valve, two zones and a wood-tank top probe",
        selectable: true, valid: false, edges: EDGES.two_tank_4way },
      { key: "valve_upper_direct_slab", label: "Valve on the radiators, slab fed direct",
        description: "", requirement: "a throttling valve, two zones, and no wood-tank probe",
        selectable: true, valid: true, edges: EDGES.valve_upper_direct_slab },
      { key: "slab_shunt", label: "Separate slab shunt", description: "",
        requirement: "not selectable: no model variant exists yet",
        selectable: false, valid: false, edges: EDGES.slab_shunt },
    ];
    return {
      two_zone: true, dhw: false, valve_mode: "manual",
      layout: "valve_upper_direct_slab", two_tank_modelled: false,
      buffer: { volume_l: 500, is_store: true, max_temp: 65 },
      wood: { present: false, volume_l: 0 },
      edges: EDGES.valve_upper_direct_slab.map((e) => [e[0], e[1]]),
      catalog, positions: {},
      slots: [
        { key: "indoor_temp_entity", label: "Indoor temperature", place: "upper_zone",
          entity: "sensor.livingroom", domains: TEMP_DOMAINS },
        { key: "lower_floor_temp_entity", label: "Lower floor temperature",
          place: "lower_zone", entity: null, domains: TEMP_DOMAINS },
        { key: "buffer_tank_temp_entity", label: "Buffer tank temperature",
          place: "buffer_tank", entity: "sensor.tank", domains: TEMP_DOMAINS },
        { key: "mixing_valve_target_entity", label: "Valve target", place: "mixing_valve",
          entity: null, domains: TEMP_DOMAINS },
        { key: "outdoor_temp_entity", label: "Outdoor temperature", place: "outdoor",
          entity: "sensor.outside", domains: TEMP_DOMAINS },
        { key: "heat_pump_switch_entity", label: "Heat pump switch", place: "heat_pump",
          entity: null, domains: ["switch", "input_boolean", "climate"] },
      ],
    };
  }

  const statStates = () => ({
    "sensor.heat_pump_optimizer_predicted_savings": { state: "12.34", attributes: { unit_of_measurement: "SEK" } },
    "sensor.heat_pump_optimizer_savings_percentage": { state: "8.2", attributes: {} },
    "sensor.heat_pump_optimizer_optimization_score": { state: "82", attributes: { envelope: 90, machine: 75 } },
    "sensor.heat_pump_optimizer_plan_narrative": { state: "cheap_price", attributes: {
      lines: ["Most heating is placed in the cheapest hours."], language: "en" } },
  });

  const woodFuelStates = (plan, fuel) => {
    const st = planStates(plan);
    st[SPACE].attributes.wood_fuel = fuel;
    return st;
  };
  const awayPlanStates = (plan, o) => {
    o = o || {};
    const st = planStates(plan);
    st["switch.heat_pump_optimizer_away"] = { state: o.sw ? "on" : "off", attributes: {} };
    st["datetime.heat_pump_optimizer_away_return"] = { state: o.returnIso || "unknown", attributes: {} };
    st["binary_sensor.heat_pump_optimizer_away_mode"] = {
      state: o.resolved ? "on" : "off",
      attributes: { source: o.resolved && !o.sw ? "person.alice" : "none" } };
    return st;
  };
  const scheduleStates = (plan) => {
    const st = planStates(plan);
    st[SPACE].attributes.day_start_hour = 7;
    st[SPACE].attributes.day_end_hour = 22;
    st[DHW].attributes.dhw_windows = "06:00-08:30, 17:00-22:00";
    return st;
  };
  const sharedStepStates = (plan) => {
    const st = planStates(plan);
    const sp = st[SPACE].attributes.forecast;
    const heating = new Set(sp.filter((p) => Number(p.space_power) > 0.05).map((p) => p.t));
    st[DHW].attributes.forecast = st[DHW].attributes.forecast.map((p) =>
      heating.has(p.t) ? Object.assign({}, p, { dhw_power: 1.5 }) : p);
    return st;
  };
  const setupStates = (plan, topo, extra) => {
    const st = Object.assign({}, planStates(plan), setupSensorStates(), extra || {});
    st[SPACE].attributes.setup_topology = topo;
    return st;
  };
  const bigStates = () => {
    const st = {};
    for (let i = 0; i < 400; i++) {
      st["sensor.zz_probe_" + String(i).padStart(3, "0")] = {
        state: "20.0", attributes: { unit_of_measurement: "°C",
          friendly_name: "Probe " + String(i).padStart(3, "0") } };
    }
    st["sensor.vedpanna_temperatur_temperature"] = { state: "71.2",
      attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
    st["sensor.vedpanna_temperatur_temperature_2"] = { state: "48.9",
      attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
    return st;
  };

  // ---- mounting, the way Lovelace does it (setConfig + hass before attach) ----
  const raf = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  D4.mount = async function (states, config, hassExtra, widthPx) {
    document.body.innerHTML = "";
    const host = document.createElement("div");
    host.id = "hpo-host";
    host.style.width = widthPx ? widthPx + "px" : "100%";
    document.body.appendChild(host);
    const card = document.createElement("heatpump-optimizer-card");
    card.style.display = "block";
    card.setConfig(Object.assign({ type: "custom:heatpump-optimizer-card" }, config || {}));
    card.hass = Object.assign({ states: states }, hassExtra || {});
    host.appendChild(card);
    window.__card = card;
    await raf();
    card.hass = Object.assign({ states: states }, hassExtra || {});
    await raf();
    await sleep(40);
    return card;
  };

  const click = (el) => el.dispatchEvent(new MouseEvent("click", { bubbles: true, composed: true, cancelable: true }));
  const q = (c, s) => c.shadowRoot && c.shadowRoot.querySelector(s);
  const qa = (c, s) => (c.shadowRoot ? [...c.shadowRoot.querySelectorAll(s)] : []);
  const svgOf = (c) => q(c, ".chartwrap svg");

  async function openDialog(c) { c.dialog.open(); await raf(); await sleep(60); }
  async function setupPage(c) {
    c._onCardClick({});
    await raf();
    c.dialog.page = "setup";
    c._render();
    await raf();
    await sleep(60);
  }

  // a pointer event at real client coordinates, from a real element
  function pev(type, el, x, y) {
    const e = new PointerEvent(type, { bubbles: true, composed: true, cancelable: true,
      clientX: x, clientY: y, pointerId: 1, isPrimary: true, buttons: type === "pointerup" ? 0 : 1 });
    el.dispatchEvent(e);
    return e;
  }

  // ---- the 34 states ----
  D4.STATES = {
    no_plan: async (plan) => { await D4.mount({}, {}, {}); return { ok: true }; },
    no_plan_expanded: async (plan) => {
      const c = await D4.mount({}, {}, {});
      await openDialog(c);
      return { ok: !!q(c, ".hpo-dialog, .dlg, dialog") || !!c.dialog.isOpen };
    },
    plan_inline: async (plan) => { await D4.mount(planStates(plan), {}, {}); return { ok: !!svgOf(window.__card) }; },
    plan_inline_sv: async (plan) => {
      await D4.mount(planStates(plan), {}, { language: "sv-SE" });
      return { ok: !!svgOf(window.__card) };
    },
    plan_short_window: async (plan) => { await D4.mount(planStates(plan), { hours: 6 }, {}); return { ok: !!svgOf(window.__card) }; },
    custom_title_currency: async (plan) => {
      await D4.mount(planStates(plan), { title: "Värme", currency: "EUR", hours: 48 }, {});
      return { ok: !!svgOf(window.__card) };
    },
    hidden_series: async (plan) => {
      const c = await D4.mount(planStates(plan), { series: { outdoor: false, solar: false } }, {});
      const chip = qa(c, ".chip").find((el) => el.getAttribute("data-key") === "price");
      if (chip) { click(chip); await raf(); await sleep(40); }
      return { ok: !!chip, note: chip ? "" : "no price chip" };
    },
    score_open: async (plan) => {
      const c = await D4.mount(Object.assign({}, planStates(plan), statStates()), {}, {});
      const stat = q(c, '[data-stat="score"]');
      if (stat) { click(stat); await raf(); await sleep(40); }
      return { ok: !!stat, note: stat ? "" : "no score stat" };
    },
    expanded_plan: async (plan) => {
      const c = await D4.mount(planStates(plan), {}, {});
      c._onCardClick({}); await raf(); await sleep(60);
      return { ok: qa(c, ".chartwrap svg").length >= 2 };
    },
    what_if_off: async (plan) => {
      const c = await D4.mount(planStates(plan), { what_if: false }, {});
      c._onCardClick({}); await raf(); await sleep(60);
      return { ok: qa(c, ".chartwrap svg").length >= 2 };
    },
    expanded_zoomed: async (plan) => {
      const c = await D4.mount(planStates(plan), {}, {});
      c._onCardClick({}); await raf(); await sleep(60);
      c.view.zoom(0.25); await raf(); await sleep(60);
      return { ok: qa(c, ".chartwrap svg").length >= 2 };
    },
    draft_dirty_menu_open: async (plan) => {
      const c = await D4.mount(planStates(plan), { what_if: true }, {});
      c._onCardClick({}); await raf(); await sleep(60);
      const svg = qa(c, ".chartwrap svg").pop();
      const hits = svg ? [...svg.querySelectorAll("rect.slot-hit")] : [];
      const hit = hits.find((h) => (h.dataset.channel || "") === "dhw") || hits[0];
      let note = "";
      if (hit) {
        const b = hit.getBoundingClientRect();
        pev("pointerdown", hit, b.left + 2, b.top + b.height / 2);
        pev("pointermove", svg, b.left + 2 + b.width, b.top + b.height / 2);
        pev("pointerup", svg, b.left + 2 + b.width, b.top + b.height / 2);
        await raf(); await sleep(40);
      } else note = "no slot-hit";
      const geom = c._geom || (c.view && c.view.geom);
      try {
        c.lanes.openMenu("space", (c._plot || {}).windowStart + 2 * HOUR, 120, 40, svg, false);
      } catch (e) { note += " menu:" + e.message; }
      await raf(); await sleep(40);
      return { ok: !!hit, note };
    },
    draft_mid_drag: async (plan) => {
      const c = await D4.mount(planStates(plan), { what_if: true }, {});
      c._onCardClick({}); await raf(); await sleep(60);
      const svg = qa(c, ".chartwrap svg").pop();
      const hits = svg ? [...svg.querySelectorAll("rect.slot-hit")] : [];
      const hit = hits.find((h) => (h.dataset.channel || "") === "dhw") || hits[0];
      if (hit) {
        const b = hit.getBoundingClientRect();
        pev("pointerdown", hit, b.left + 2, b.top + b.height / 2);
        pev("pointermove", svg, b.left + 2 + b.width, b.top + b.height / 2);
        await raf(); await sleep(40);
      }
      return { ok: !!hit, note: hit ? "" : "no slot-hit" };
    },
    whatif_edited: async (plan) => {
      const c = await D4.mount(scheduleStates(plan), { what_if: true }, {});
      c._hass = { states: c._hass.states, callService: async () => ({ response: { results: {} } }) };
      c._onCardClick({}); await raf(); await sleep(60);
      let note = "";
      try {
        c.whatIf.onInput({ stopPropagation() {}, preventDefault() {},
          target: { value: "42", classList: { contains: (x) => x === "wi-dhw-min" } } });
        clearTimeout(c.whatIf.timer); c.whatIf.timer = null;
        c.whatIf.onAddWindow({ stopPropagation() {}, preventDefault() {} });
      } catch (e) { note = e.message; }
      await raf(); await sleep(60);
      return { ok: !note, note };
    },
    whatif_weekly: async (plan) => {
      const st = planStates(plan);
      st[DHW].attributes.dhw_windows = "06:00-08:30";
      st[DHW].attributes.dhw_windows_spec = "weekdays 06:00-08:30, weekend 08:00-09:30";
      const c = await D4.mount(st, { what_if: true }, {});
      c._onCardClick({}); await raf(); await sleep(60);
      return { ok: qa(c, ".chartwrap svg").length >= 2 };
    },
    override_active: async (plan) => {
      const st = planStates(plan);
      const info = { active: true,
        expires_at: new Date(Date.now() + 5 * HOUR).toISOString(),
        space_slots: [], dhw_slots: [], released_space: [], released_dhw: [] };
      st[SPACE].attributes.manual_override = info;
      st[DHW].attributes.manual_override = info;
      const c = await D4.mount(st, { what_if: true }, {});
      await openDialog(c);
      return { ok: qa(c, ".chartwrap svg").length >= 2 };
    },
    shared_steps: async (plan) => {
      const c = await D4.mount(sharedStepStates(plan), {}, {});
      c._onCardClick({}); await raf(); await sleep(60);
      return { ok: qa(c, ".chartwrap svg").length >= 2 };
    },
    shared_steps_hover: async (plan) => {
      const c = await D4.mount(sharedStepStates(plan), {}, {});
      c._onCardClick({}); await raf(); await sleep(60);
      const svg = qa(c, ".chartwrap svg").pop();
      const plot = c._plot;
      let note = "";
      if (svg && plot && plot.scaleX) {
        const sp = sharedStepStates(plan)[SPACE].attributes.forecast;
        const first = sp.find((p) => Number(p.space_power) > 0.05 && Date.parse(p.t) >= plot.windowStart);
        const t = first ? Date.parse(first.t) : plot.windowStart + 5 * HOUR;
        c._onPointerMove({ currentTarget: svg, clientX: plot.scaleX(t) });
        await raf(); await sleep(40);
      } else note = "no plot";
      return { ok: !note, note };
    },
    tooltip_hover: async (plan) => {
      const c = await D4.mount(planStates(plan), {}, {});
      c._onCardClick({}); await raf(); await sleep(60);
      const svg = qa(c, ".chartwrap svg").pop();
      const plot = c._plot;
      if (svg && plot && plot.scaleX) {
        c._onPointerMove({ currentTarget: svg, clientX: plot.scaleX(plot.windowStart + 5 * HOUR) });
        await raf(); await sleep(40);
        return { ok: true };
      }
      return { ok: false, note: "no plot" };
    },
    coarse_pointer: async (plan) => {
      const c = await D4.mount(planStates(plan), {}, {});
      c._onCardClick({}); await raf(); await sleep(60);
      return { ok: qa(c, ".chartwrap svg").length >= 2 };
    },
    reduced_motion: async (plan) => { await D4.mount(planStates(plan), {}, {}); return { ok: !!svgOf(window.__card) }; },
    setup_single_buffer: async (plan) => {
      const c = await D4.mount(setupStates(plan, qaTopologies().base), {}, {});
      await setupPage(c);
      return { ok: !!q(c, "svg.setup-svg") };
    },
    setup_two_tank: async (plan) => {
      const c = await D4.mount(setupStates(plan, qaTopologies().twoTank), {}, {});
      await setupPage(c);
      return { ok: !!q(c, "svg.setup-svg") };
    },
    setup_coil: async (plan) => {
      const c = await D4.mount(setupStates(plan, qaTopologies().coil), {}, {});
      await setupPage(c);
      return { ok: !!q(c, "svg.setup-svg") };
    },
    layout_editing_dragged: async (plan) => {
      const c = await D4.mount(setupStates(plan, layoutCatalogTopo()), {}, {});
      await setupPage(c);
      const toggle = q(c, ".layout-edit-toggle");
      if (toggle) { click(toggle); await raf(); await sleep(40); }
      const L = c.layoutEditor || c.layout;
      const svg = q(c, "svg.setup-svg");
      let note = toggle ? "" : "no toggle";
      if (L && svg) {
        const box = (L.boxes || []).find((b) => b.place === "buffer_tank");
        const r = svg.getBoundingClientRect();
        const vb = svg.viewBox.baseVal;
        const sx = r.width / (vb.width || 720);
        if (box) {
          const cx = r.left + (box.x + box.w / 2) * sx, cy = r.top + (box.y + box.h / 2) * sx;
          try {
            L.onDown({ clientX: cx, clientY: cy, target: { dataset: {} }, stopPropagation() {}, preventDefault() {} });
            L.onMove({ clientX: cx + 20, clientY: cy + 15, stopPropagation() {}, preventDefault() {} });
            L.onUp({ clientX: cx + 40, clientY: cy + 30, stopPropagation() {}, preventDefault() {} });
          } catch (e) { note += " drag:" + e.message; }
          await raf(); await sleep(40);
        } else note += " no buffer box";
      } else note += " no layout editor";
      return { ok: !!q(c, "svg.setup-svg"), note };
    },
    layout_editing_tidy: async (plan) => {
      const r = await D4.STATES.layout_editing_dragged(plan);
      const c = window.__card;
      const tidy = q(c, ".layout-tidy");
      if (tidy) { click(tidy); await raf(); await sleep(40); }
      return { ok: r.ok, note: (r.note || "") + (tidy ? "" : " no tidy") };
    },
    picker_open_filtered: async (plan) => {
      const c = await D4.mount(setupStates(plan, qaTopologies().base, bigStates()), {}, {});
      await setupPage(c);
      const hit = qa(c, ".setup-hit").find((h) => h.dataset.key === "wood_tank_top_entity");
      if (hit) { click(hit); await raf(); await sleep(60); }
      const box = q(c, ".sp-filter");
      if (box) {
        box.value = "vedpanna";
        box.dispatchEvent(new Event("input", { bubbles: true, composed: true }));
        await raf(); await sleep(60);
      }
      return { ok: !!box, note: (hit ? "" : "no hit;") + (box ? "" : "no filter") };
    },
    wood_alert: async (plan) => {
      await D4.mount(woodFuelStates(plan, { cheaper: true, show_whatif: true, ready: true, slots: [] }), {}, {});
      return { ok: !!svgOf(window.__card) };
    },
    wood_lane: async (plan) => {
      const t0 = plan.space_plan.forecast[0].t;
      const t1 = plan.space_plan.forecast[Math.min(4, plan.space_plan.forecast.length - 1)].t;
      await D4.mount(woodFuelStates(plan, { cheaper: false, show_whatif: true, ready: true,
        slots: [{ start: t0, end: t1, source: "detected" }] }), {}, {});
      return { ok: !!svgOf(window.__card) };
    },
    wood_whatif: async (plan) => {
      const c = await D4.mount(woodFuelStates(plan, { cheaper: false, show_whatif: true, ready: true, slots: [] }),
        { what_if: true }, {});
      c._onCardClick({}); await raf(); await sleep(60);
      return { ok: qa(c, ".chartwrap svg").length >= 2 };
    },
    away_toggle: async (plan) => {
      const c = await D4.mount(awayPlanStates(plan), {}, {});
      c._onCardClick({}); await raf(); await sleep(60);
      return { ok: qa(c, ".chartwrap svg").length >= 2 };
    },
    away_return: async (plan) => {
      const c = await D4.mount(awayPlanStates(plan, { sw: true }), {}, {});
      c._onCardClick({}); await raf(); await sleep(60);
      return { ok: qa(c, ".chartwrap svg").length >= 2 };
    },
    away_status: async (plan) => {
      const c = await D4.mount(awayPlanStates(plan, { resolved: true }), {}, {});
      c._onCardClick({}); await raf(); await sleep(60);
      return { ok: qa(c, ".chartwrap svg").length >= 2 };
    },
    editor_schema: async (plan) => {
      document.body.innerHTML = "";
      const host = document.createElement("div");
      document.body.appendChild(host);
      const e = document.createElement("heatpump-optimizer-card-editor");
      e.setConfig({ type: "custom:heatpump-optimizer-card", hours: 12, series: { solar: false } });
      e.hass = { states: {}, language: "en" };
      host.appendChild(e);
      window.__card = e;
      await raf(); await sleep(60);
      return { ok: true, note: "no ha-form element locally; editor renders its host only" };
    },
  };
})();
