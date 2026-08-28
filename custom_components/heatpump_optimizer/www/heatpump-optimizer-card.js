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
const EDITOR_TAG = "heatpump-optimizer-card-editor";
const CARD_VERSION = "5.1.7";

// ---- i18n ------------------------------------------------------------------
//
// Every user-visible string lives here, keyed, with an English source text and
// a Swedish translation. `L(key, vars)` looks the key up in the active
// language, falls back to English for anything untranslated, and interpolates
// `{name}` placeholders. The active language follows `hass.language`
// ("sv-SE" -> "sv"); anything without a dictionary renders in English.
//
// Deliberately NOT translated: entity ids, config keys, service and attribute
// names, CSS classes, data-* attributes, wire enums (reason codes, place ids,
// channels), and console messages -- those are contracts, not prose.
const STRINGS = {
  en: {
    // header / card chrome
    "header.default_title": "Heat pump plan",
    "header.enlarge": "Enlarge",
    "header.enlarge_chart": "Enlarge chart",
    "header.tab_plan": "Plan",
    "header.tab_setup": "Setup",
    "header.close": "Close",

    // legend / series
    "series.price": "Electricity price",
    "series.dhw_slots": "DHW heating",
    "series.space_slots": "Space heating",
    "series.outdoor": "Outdoor temperature",
    "series.dhw_temp": "DHW tank temperature",
    "series.house_temp": "House temperature",
    "series.solar": "Solar irradiance",
    // The extra traces inside the house-temperature series. They are drawn
    // dashed in the same colour, and before v5.1.7 nothing named them: one
    // legend chip and one tooltip row said "House temperature" for all
    // three, so hovering the upper or lower zone reported the room's value.
    "series.upper_floor": "Upper floor",
    "series.lower_floor": "Lower floor",
    // No lower-floor thermometer: the trace is the model's own prediction,
    // running open-loop with nothing to correct it. Worth saying, because it
    // can drift from the real downstairs over a few hours.
    "series.lower_floor_modelled": "Lower floor (modelled)",

    // chart / plan annotations
    "plan.now": "now",
    "plan.estimated_prices": "estimated prices",
    "plan.zoom_out": "Zoom out",
    "plan.zoom_in": "Zoom in",
    "plan.show_whole_plan": "Show the whole plan",
    "plan.price_estimated": "Price is estimated, not published yet",
    "plan.shared_step_tooltip":
      "Shared step: the pump alternates circuits — hot water first. " +
      "Combined {kw} kW stays under the pump's maximum.",
    "plan.shared_band_title":
      "Space heating and hot water share these quarter hours: the pump " +
      "alternates circuits within each step, hot water first. Their " +
      "combined power never exceeds the heat pump's maximum — this is " +
      "time-sharing, not double-booking.",

    // plan reason codes
    "reasons.comfort_floor": "Holding the minimum temperature",
    "reasons.cheap_price": "Cheapest hours",
    "reasons.preheat_weather": "Pre-heating before colder weather",
    "reasons.scheduled": "Keeping the house at target",
    "reasons.terminal_value": "Leaving the house warm past the horizon",
    "reasons.solar_surplus": "Using solar surplus",
    "reasons.dhw_window": "Hot water needed now",
    "reasons.dhw_ready": "Getting the tank ready for a demand window",
    "reasons.dhw_preheat": "Charging the tank while electricity is cheap",
    "reasons.legionella": "Anti-legionella cycle",
    "reasons.manual_plan": "You scheduled this",
    "reasons.idle": "Not heating",

    // slot lanes and the slot menu
    "slots.lane_dhw": "Hot water",
    "slots.lane_space": "Heating",
    "menu.remove_slot_dhw": "Remove this hot water slot",
    "menu.remove_slot_space": "Remove this heating slot",
    "menu.add_slot_dhw": "Add a hot water slot here",
    "menu.add_slot_space": "Add a heating slot here",
    "slots.no_plan_to_pin": "No plan to pin yet.",
    "slots.applying": "Applying…",
    "slots.until_suffix": " until {expiry}",
    "slots.pinned_result":
      "Pinned{until}. These slots will be kept unless doing so would take " +
      "the house or the tank below its limits.",
    "slots.clearing": "Clearing…",
    "slots.back_to_auto_result": "Back to automatic planning.",
    "slots.released_one":
      "{n} slot was released to protect the house or the tank.",
    "slots.released_other":
      "{n} slots were released to protect the house or the tank.",
    "slots.pinned_status": "Your slots are pinned{until}.",

    // what-if panel
    "whatif.todays_slots": "Today's slots",
    "whatif.slots_hint":
      "Drag a slot along its lane at the bottom of the chart to move it, " +
      "drag either edge to resize it, or right-click a lane to add and " +
      "remove slots. Applying pins them for the next {hours} hours.",
    "whatif.zoom_limit_hint":
      "Zoomed in — editing stops at the visible edge. Drag a slot against " +
      "the edge to pan, or {button}.",
    "whatif.show_whole_plan_button": "show the whole plan",
    "whatif.apply_plan": "Apply this plan",
    "whatif.undo_changes": "Undo my changes",
    "whatif.back_to_auto": "Back to automatic",
    "whatif.usual_schedule": "My usual schedule",
    "whatif.schedule_hint":
      "These are the recurring hours the optimizer plans against every " +
      "day, not just today.",
    "whatif.heating_hours": "Heating hours",
    "whatif.day_from": "Day from",
    "whatif.day_start_aria": "Heating day starts",
    "whatif.day_to": "to",
    "whatif.day_end_aria": "Heating day ends",
    "whatif.setback_hint": "Outside these hours the night setback applies.",
    "whatif.dhw_windows": "Hot water windows",
    "whatif.window_start_aria": "Window {n} start",
    "whatif.window_end_aria": "Window {n} end",
    "whatif.remove": "Remove",
    "whatif.remove_window_aria": "Remove window {n}",
    "whatif.no_windows_hint":
      "No windows: hot water is never required, so the tank is only kept " +
      "above its idle minimum.",
    "whatif.add_window": "+ Add window",
    "whatif.simulate": "Simulate these slots",
    "whatif.save_schedule": "Save as my schedule",
    "whatif.reset": "Reset",
    "whatif.idle_status":
      "Change a setting to see what it would cost. Simulating changes " +
      "nothing; saving replaces your configured schedule.",
    "whatif.temperatures": "Temperatures",
    "whatif.temperatures_hint":
      "How warm the house is kept during the heating day, and how cool " +
      "the hot water tank is allowed to get inside a demand window. Both " +
      "are priced the same way as the schedule above.",
    "whatif.comfort_temp": "Comfort temperature",
    "whatif.dhw_min": "Minimum hot water",
    "whatif.dhw_min_aria": "Minimum hot water temperature",
    "whatif.cap_no_setpoint":
      "Capped at {t}&nbsp;°C, far enough below the hot water setpoint to " +
      "leave the tank a band to work in.",
    "whatif.cap_with_setpoint":
      "Capped at {t}&nbsp;°C: a {band}&nbsp;°C band below the " +
      "{setpoint}&nbsp;°C setpoint, so the tank has room to work in " +
      "instead of chasing its target.",
    "whatif.clamped_warning":
      "Your saved minimum of {a}&nbsp;°C is above that limit, so the " +
      "slider shows {b}&nbsp;°C. Saving will store the lower value.",
    "whatif.confirm_overwrite": "Confirm: overwrite my schedule",
    "whatif.confirm_hint":
      "This replaces your configured heating hours, hot water windows and " +
      "temperatures, and reloads the integration. Press again to confirm.",
    "whatif.saving": "Saving…",
    "whatif.saved_result":
      "Saved. The optimizer is reloading and will plan against the new " +
      "schedule.",
    "whatif.simulating": "Working out what that would cost…",
    "whatif.same_cost": "<b>About the same cost</b> as the current plan.",
    "whatif.cheaper_per_month":
      '<b class="cheaper">{amount} less per month</b> than the current plan.',
    "whatif.dearer_per_month":
      '<b class="dearer">{amount} more per month</b> than the current plan.',
    "whatif.min_room_temp": "Coldest the house gets: {t} °C",
    "whatif.min_dhw_temp": "Lowest tank temperature: {t} °C",
    "whatif.compressor_starts_one": "{n} compressor start",
    "whatif.compressor_starts_other": "{n} compressor starts",
    "whatif.rate_limited":
      "<i>(previous estimate; simulations are rate-limited)</i>",

    // cost delta row
    "stats.no_plan_to_compare": "No plan data to compare against yet.",
    "stats.cheaper": "cheaper",
    "stats.dearer": "dearer",
    "stats.the_same": "the same",
    "stats.delta_detail":
      "{verdict} than the saved plan ({planned} → {edited}&nbsp;{currency}, " +
      "estimated)",

    // expiry prose
    "time.tomorrow": "{time} tomorrow",
    "time.on_weekday": "{time} on {weekday}",

    // setup page
    "setup.not_published":
      "The setup description has not been published yet. It appears with " +
      "the plan sensors after the integration loads.",
    "setup.editing_hint":
      "Drag a box to move it, drag a port to connect two boxes, or click " +
      "a pipe to remove it. Only a drawing that matches a supported " +
      "layout can be saved.",
    "setup.assign_hint":
      "Click any sensor to assign it, or to clear it. An empty slot is a " +
      "sensor this setup could use and does not have; it is shown on " +
      "purpose.",
    "setup.done_editing": "Done editing",
    "setup.edit_layout": "Edit layout",
    "setup.save_layout": "Save layout",
    "setup.undo_layout": "Undo",
    "setup.undo_layout_aria":
      "Undo the changes and go back to the layout in use, staying in the " +
      "editor",
    "setup.verdict_match": "Matches {label}.",
    "setup.verdict_req": "{label} — {requirement}.",
    "setup.verdict_not_modelled":
      "{label} — known but not modelled yet, so it cannot be selected.",
    "setup.verdict_needs": "{label} — needs {requirement}.",
    "setup.verdict_cannot_store":
      "{label} — the current configuration cannot store this layout.",
    "setup.no_catalog": "No layout catalog was published for this system.",
    "setup.verdict_no_match": "No supported layout matches. Closest: {label}.",
    "setup.verdict_extra_edges": "Not in it: {edges}.",
    "setup.verdict_missing_edges": "Missing: {edges}.",
    "setup.saved_reloading": "Saved {label}. Reloading…",
    "setup.svg_aria": "Configured system",

    // place labels (layout editor rejection lines)
    "places.heat_pump": "Heat pump",
    "places.buffer_tank": "Buffer tank",
    "places.mixing_valve": "Mixing valve",
    "places.upper_zone": "Upper floor",
    "places.lower_zone": "Lower floor",
    "places.wood_tank": "Wood tank",
    "places.wood_valve": "Wood mixing valve",
    "places.dhw_tank": "Hot water tank",
    "places.slab_shunt": "Slab shunt",

    // setup diagram boxes and captions
    "setup.box_hp_tank": "Heat pump tank",
    "setup.box_buffer_tank": "Buffer tank",
    "setup.box_4way_valve": "4-way mixing valve",
    "setup.box_mixing_valve": "Mixing valve",
    "setup.box_outside": "Outside",
    "setup.box_heat_pump": "Heat pump",
    "setup.box_wood_tank": "Wood furnace tank ({v} L)",
    "setup.wood_caption": "modelled as heat into the heat-pump tank",
    "setup.buffer_stores": "stores up to {t} °C",
    "setup.buffer_too_small": "too small to store",
    "setup.no_valve_caption": "no mixing valve: delivery is not throttled",
    "setup.box_dhw_tank": "Hot water tank",
    "setup.dhw_coil_caption": "refilled through a wood tank coil",
    "setup.box_upper_floor": "Upper floor",
    "setup.box_house": "House",
    "setup.box_lower_floor": "Lower floor (slab)",

    // setup slot rows / live values
    "setup.unavailable": "unavailable",
    "setup.source_weather": "weather forecast",
    "setup.not_configured": "not configured",
    "setup.click_to_assign_title": "{label} — click to assign",

    // entity picker
    "setup.picker_aria": "Entity for {slot}",
    "setup.picker_none": "(not configured)",
    "setup.assign": "Assign",
    "setup.cancel": "Cancel",
    "setup.picker_count": "{n} matching {domains} entities.",
    "setup.picker_filter_placeholder": "Type to narrow the list…",
    "setup.picker_filter_aria": "Filter entities for {slot}",
    "setup.picker_showing": "Showing {n} of {total} — type to narrow.",
    "setup.picker_no_match": "Nothing matches “{q}”.",
    "setup.picker_missing": "not available right now",
    "setup.confirm_clear": "Confirm: clear this sensor",
    "setup.confirm_clear_hint":
      "This removes {entity} from “{label}” and reloads the integration. " +
      "Press Assign again to confirm.",
    "setup.assigned_reloading": "Assigned {entity}. Reloading…",
    "setup.cleared_reloading": "Cleared. Reloading…",

    // errors and diagnostics
    "errors.not_connected": "Not connected to Home Assistant.",
    "errors.invalid_window_time":
      "One of the hot water windows is not a valid time.",
    "errors.day_start_equals_end":
      "The heating day starts and ends at the same hour, which would " +
      "leave no comfort period at all.",
    "errors.could_not_apply": "Could not apply: {err}",
    "errors.could_not_clear": "Could not clear: {err}",
    "errors.could_not_save": "Could not save: {err}",
    "errors.could_not_simulate": "Could not simulate: {err}",
    "errors.no_answer": "No answer from the optimizer.",
    "errors.could_not_save_layout": "Could not save the layout: {err}",
    "errors.could_not_assign": "Could not assign: {err}",
    "errors.diag_space": "Space heating",
    "errors.diag_dhw": "DHW",
    "errors.no_plan_data": "No plan data available yet.",
    "errors.diag_not_found":
      "{label}: no entity found. Looked for <code>{id}</code>. Check the " +
      "entity id in Developer Tools &gt; States and set " +
      "<code>{kind}_entity</code> in the card config.",
    "errors.diag_unavailable": "{label}: <code>{id}</code> is {state}.",
    "errors.diag_no_forecast":
      "{label}: <code>{id}</code> has no forecast attribute yet. It " +
      "appears after the first optimization run.",
    "errors.diag_empty_forecast":
      "{label}: <code>{id}</code> published an empty forecast.",
    "errors.diag_out_of_window":
      "{label}: <code>{id}</code> has {n} points, but none fall in the " +
      "selected window.",

    // setConfig errors (the literal prefix and quoted config keys are part
    // of the contract and stay untranslated inside each message)
    "errors.cfg_not_object":
      "heatpump-optimizer-card: configuration must be an object",
    "errors.cfg_space_entity":
      "heatpump-optimizer-card: 'space_entity' must be an entity id string",
    "errors.cfg_dhw_entity":
      "heatpump-optimizer-card: 'dhw_entity' must be an entity id string",
    "errors.cfg_solar_entity":
      "heatpump-optimizer-card: 'solar_entity' must be an entity id string",
    "errors.cfg_what_if":
      "heatpump-optimizer-card: 'what_if' must be true or false",
    "errors.cfg_hours":
      "heatpump-optimizer-card: 'hours' must be a number between 1 and 168",
    "errors.cfg_title": "heatpump-optimizer-card: 'title' must be a string",
    "errors.cfg_series": "heatpump-optimizer-card: 'series' must be a map",
    "errors.cfg_series_unknown":
      "heatpump-optimizer-card: unknown series '{k}' in 'series'",
    "errors.cfg_series_visibility":
      "heatpump-optimizer-card: series '{k}' visibility must be true or false",
    "errors.cfg_show_stats":
      "heatpump-optimizer-card: 'show_stats' must be true or false",

    // headline stats row
    "headline.savings": "Projected savings",
    "headline.savings_title":
      "Estimated saving of the current plan against unoptimized heating.",
    "headline.score": "Optimization score",
    "headline.score_title":
      "How well the whole installation is set up and running, 0–100.",
    // The percent is a template because the spacing is orthographic:
    // English sets "(8%)", Swedish "(8 %)".
    "headline.savings_pct": "({pct}%)",

    // keyboard access (aria labels)
    "slots.slot_aria":
      "{lane} {start}–{end}. Press Enter for actions, Delete to remove.",
    "slots.lane_aria": "{lane} lane. Press Enter to add a slot.",

    // visual config editor
    "editor.title": "Title",
    "editor.space_entity": "Space heating plan sensor",
    "editor.dhw_entity": "Hot water plan sensor",
    "editor.solar_entity": "Solar irradiance sensor",
    "editor.hours": "Hours to show",
    "editor.what_if": "Show the schedule editor",
    "editor.show_stats": "Show the headline stats",
    "editor.currency": "Currency",
    "editor.series": "Series shown by default",
  },

  sv: {
    "header.default_title": "Värmepumpsplan",
    "header.enlarge": "Förstora",
    "header.enlarge_chart": "Förstora diagrammet",
    "header.tab_plan": "Plan",
    "header.tab_setup": "Anläggning",
    "header.close": "Stäng",

    "series.price": "Elpris",
    "series.dhw_slots": "Varmvattenberedning",
    "series.space_slots": "Uppvärmning",
    "series.outdoor": "Utetemperatur",
    "series.dhw_temp": "Varmvattentankens temperatur",
    "series.house_temp": "Innetemperatur",
    "series.solar": "Solinstrålning",
    "series.upper_floor": "Övre plan",
    "series.lower_floor": "Nedre plan",
    "series.lower_floor_modelled": "Nedre plan (modellerad)",

    "plan.now": "nu",
    "plan.estimated_prices": "uppskattade priser",
    "plan.zoom_out": "Zooma ut",
    "plan.zoom_in": "Zooma in",
    "plan.show_whole_plan": "Visa hela planen",
    "plan.price_estimated": "Priset är uppskattat, ännu inte publicerat",
    "plan.shared_step_tooltip":
      "Delat steg: pumpen växlar mellan kretsarna — varmvatten först. " +
      "Sammanlagt håller sig {kw} kW under pumpens maxeffekt.",
    "plan.shared_band_title":
      "Uppvärmning och varmvatten delar de här kvartarna: pumpen växlar " +
      "mellan kretsarna inom varje steg, varmvatten först. Deras " +
      "sammanlagda effekt överstiger aldrig värmepumpens maxeffekt — " +
      "tiden delas, inget dubbelbokas.",

    "reasons.comfort_floor": "Håller minimitemperaturen",
    "reasons.cheap_price": "Billigaste timmarna",
    "reasons.preheat_weather": "Förvärmer inför kallare väder",
    "reasons.scheduled": "Håller huset på önskad temperatur",
    "reasons.terminal_value": "Lämnar huset varmt bortom horisonten",
    "reasons.solar_surplus": "Använder solöverskott",
    "reasons.dhw_window": "Varmvatten behövs nu",
    "reasons.dhw_ready": "Gör tanken redo inför ett behovsfönster",
    "reasons.dhw_preheat": "Laddar tanken medan elen är billig",
    "reasons.legionella": "Legionellaskyddscykel",
    "reasons.manual_plan": "Du har schemalagt detta",
    "reasons.idle": "Värmer inte",

    "slots.lane_dhw": "Varmvatten",
    "slots.lane_space": "Värme",
    "menu.remove_slot_dhw": "Ta bort det här varmvattenpasset",
    "menu.remove_slot_space": "Ta bort det här värmepasset",
    "menu.add_slot_dhw": "Lägg till ett varmvattenpass här",
    "menu.add_slot_space": "Lägg till ett värmepass här",
    "slots.no_plan_to_pin": "Ingen plan att låsa ännu.",
    "slots.applying": "Tillämpar…",
    "slots.until_suffix": " till {expiry}",
    "slots.pinned_result":
      "Låst{until}. De här passen behålls så länge det inte tar huset " +
      "eller tanken under sina gränser.",
    "slots.clearing": "Rensar…",
    "slots.back_to_auto_result": "Tillbaka till automatisk planering.",
    "slots.released_one":
      "{n} pass släpptes för att skydda huset eller tanken.",
    "slots.released_other":
      "{n} pass släpptes för att skydda huset eller tanken.",
    "slots.pinned_status": "Dina pass är låsta{until}.",

    "whatif.todays_slots": "Dagens pass",
    "whatif.slots_hint":
      "Dra ett pass längs sin bana längst ner i diagrammet för att " +
      "flytta det, dra i endera kanten för att ändra längden, eller " +
      "högerklicka på en bana för att lägga till och ta bort pass. Att " +
      "tillämpa låser dem de kommande {hours} timmarna.",
    "whatif.zoom_limit_hint":
      "Inzoomad — redigeringen stannar vid den synliga kanten. Dra ett " +
      "pass mot kanten för att panorera, eller {button}.",
    "whatif.show_whole_plan_button": "visa hela planen",
    "whatif.apply_plan": "Tillämpa denna plan",
    "whatif.undo_changes": "Ångra mina ändringar",
    "whatif.back_to_auto": "Tillbaka till automatik",
    "whatif.usual_schedule": "Mitt vanliga schema",
    "whatif.schedule_hint":
      "Det här är de återkommande tider optimeraren planerar efter varje " +
      "dag, inte bara i dag.",
    "whatif.heating_hours": "Värmetider",
    "whatif.day_from": "Dag från",
    "whatif.day_start_aria": "Värmedagen börjar",
    "whatif.day_to": "till",
    "whatif.day_end_aria": "Värmedagen slutar",
    "whatif.setback_hint": "Utanför dessa tider gäller nattsänkningen.",
    "whatif.dhw_windows": "Varmvattenfönster",
    "whatif.window_start_aria": "Fönster {n} start",
    "whatif.window_end_aria": "Fönster {n} slut",
    "whatif.remove": "Ta bort",
    "whatif.remove_window_aria": "Ta bort fönster {n}",
    "whatif.no_windows_hint":
      "Inga fönster: varmvatten krävs aldrig, så tanken hålls bara över " +
      "sitt vilominimum.",
    "whatif.add_window": "+ Lägg till fönster",
    "whatif.simulate": "Simulera dessa pass",
    "whatif.save_schedule": "Spara som mitt schema",
    "whatif.reset": "Återställ",
    "whatif.idle_status":
      "Ändra en inställning för att se vad den skulle kosta. Att " +
      "simulera ändrar ingenting; att spara ersätter ditt konfigurerade " +
      "schema.",
    "whatif.temperatures": "Temperaturer",
    "whatif.temperatures_hint":
      "Hur varmt huset hålls under värmedagen, och hur svalt " +
      "varmvattentanken får bli inom ett behovsfönster. Båda prissätts " +
      "på samma sätt som schemat ovan.",
    "whatif.comfort_temp": "Komforttemperatur",
    "whatif.dhw_min": "Lägsta varmvatten",
    "whatif.dhw_min_aria": "Lägsta varmvattentemperatur",
    "whatif.cap_no_setpoint":
      "Begränsad till {t}&nbsp;°C, tillräckligt långt under varmvattnets " +
      "börvärde för att lämna tanken ett band att arbeta i.",
    "whatif.cap_with_setpoint":
      "Begränsad till {t}&nbsp;°C: ett band på {band}&nbsp;°C under " +
      "börvärdet {setpoint}&nbsp;°C, så att tanken har utrymme att " +
      "arbeta i i stället för att jaga sitt mål.",
    "whatif.clamped_warning":
      "Ditt sparade minimum på {a}&nbsp;°C ligger över den gränsen, så " +
      "reglaget visar {b}&nbsp;°C. Vid sparning lagras det lägre värdet.",
    "whatif.confirm_overwrite": "Bekräfta: skriv över mitt schema",
    "whatif.confirm_hint":
      "Detta ersätter dina konfigurerade värmetider, varmvattenfönster " +
      "och temperaturer, och laddar om integrationen. Tryck igen för att " +
      "bekräfta.",
    "whatif.saving": "Sparar…",
    "whatif.saved_result":
      "Sparat. Optimeraren laddar om och kommer att planera efter det " +
      "nya schemat.",
    "whatif.simulating": "Räknar ut vad det skulle kosta…",
    "whatif.same_cost":
      "<b>Ungefär samma kostnad</b> som den nuvarande planen.",
    "whatif.cheaper_per_month":
      '<b class="cheaper">{amount} mindre per månad</b> än den nuvarande ' +
      "planen.",
    "whatif.dearer_per_month":
      '<b class="dearer">{amount} mer per månad</b> än den nuvarande ' +
      "planen.",
    "whatif.min_room_temp": "Som kallast blir huset {t} °C",
    "whatif.min_dhw_temp": "Lägsta tanktemperatur: {t} °C",
    "whatif.compressor_starts_one": "{n} kompressorstart",
    "whatif.compressor_starts_other": "{n} kompressorstarter",
    "whatif.rate_limited":
      "<i>(föregående uppskattning; antalet simuleringar är begränsat)</i>",

    "stats.no_plan_to_compare": "Ingen plandata att jämföra med ännu.",
    "stats.cheaper": "billigare",
    "stats.dearer": "dyrare",
    "stats.the_same": "oförändrad",
    "stats.delta_detail":
      "{verdict} jämfört med den sparade planen ({planned} → " +
      "{edited}&nbsp;{currency}, uppskattat)",

    "time.tomorrow": "{time} i morgon",
    "time.on_weekday": "{time} på {weekday}",

    "setup.not_published":
      "Anläggningsbeskrivningen har inte publicerats ännu. Den visas " +
      "tillsammans med plansensorerna när integrationen har laddats.",
    "setup.editing_hint":
      "Dra en låda för att flytta den, dra i en port för att koppla ihop " +
      "två lådor, eller klicka på ett rör för att ta bort det. Endast en " +
      "ritning som motsvarar en layout som stöds kan sparas.",
    "setup.assign_hint":
      "Klicka på valfri sensor för att tilldela eller rensa den. En tom " +
      "plats är en sensor som anläggningen skulle kunna använda men " +
      "saknar; den visas med avsikt.",
    "setup.done_editing": "Klar med redigeringen",
    "setup.edit_layout": "Redigera layout",
    "setup.save_layout": "Spara layout",
    "setup.undo_layout": "Ångra",
    "setup.undo_layout_aria":
      "Ångra ändringarna och återgå till den layout som används, utan att " +
      "lämna redigeringsläget",
    "setup.verdict_match": "Motsvarar {label}.",
    "setup.verdict_req": "{label} — {requirement}.",
    "setup.verdict_not_modelled":
      "{label} — känd men ännu inte modellerad, så den kan inte väljas.",
    "setup.verdict_needs": "{label} — kräver {requirement}.",
    "setup.verdict_cannot_store":
      "{label} — den nuvarande konfigurationen kan inte lagra denna layout.",
    "setup.no_catalog":
      "Ingen layoutkatalog har publicerats för det här systemet.",
    "setup.verdict_no_match":
      "Ingen layout som stöds stämmer. Närmast: {label}.",
    "setup.verdict_extra_edges": "Finns inte i den: {edges}.",
    "setup.verdict_missing_edges": "Saknas: {edges}.",
    "setup.saved_reloading": "Sparade {label}. Laddar om…",
    "setup.svg_aria": "Konfigurerad anläggning",

    "places.heat_pump": "Värmepump",
    "places.buffer_tank": "Ackumulatortank",
    "places.mixing_valve": "Shuntventil",
    "places.upper_zone": "Övervåning",
    "places.lower_zone": "Nedervåning",
    "places.wood_tank": "Vedtank",
    "places.wood_valve": "Vedshunt",
    "places.dhw_tank": "Varmvattentank",
    "places.slab_shunt": "Golvshunt",

    "setup.box_hp_tank": "Värmepumpstank",
    "setup.box_buffer_tank": "Ackumulatortank",
    "setup.box_4way_valve": "4-vägs shuntventil",
    "setup.box_mixing_valve": "Shuntventil",
    "setup.box_outside": "Ute",
    "setup.box_heat_pump": "Värmepump",
    "setup.box_wood_tank": "Vedpannetank ({v} L)",
    "setup.wood_caption": "modelleras som värme in i värmepumpstanken",
    "setup.buffer_stores": "lagrar upp till {t} °C",
    "setup.buffer_too_small": "för liten för att lagra",
    "setup.no_valve_caption": "ingen shuntventil: leveransen stryps inte",
    "setup.box_dhw_tank": "Varmvattentank",
    "setup.dhw_coil_caption": "återfylls genom en slinga i vedtanken",
    "setup.box_upper_floor": "Övervåning",
    "setup.box_house": "Hus",
    "setup.box_lower_floor": "Nedervåning (platta)",

    "setup.unavailable": "otillgänglig",
    "setup.source_weather": "väderprognos",
    "setup.not_configured": "inte konfigurerad",
    "setup.click_to_assign_title": "{label} — klicka för att tilldela",

    "setup.picker_aria": "Entitet för {slot}",
    "setup.picker_none": "(inte konfigurerad)",
    "setup.assign": "Tilldela",
    "setup.cancel": "Avbryt",
    "setup.picker_count": "{n} matchande {domains}-entiteter.",
    "setup.picker_filter_placeholder": "Skriv för att filtrera listan…",
    "setup.picker_filter_aria": "Filtrera entiteter för {slot}",
    "setup.picker_showing": "Visar {n} av {total} — skriv för att filtrera.",
    "setup.picker_no_match": "Inget matchar ”{q}”.",
    "setup.picker_missing": "inte tillgänglig just nu",
    "setup.confirm_clear": "Bekräfta: rensa sensorn",
    "setup.confirm_clear_hint":
      "Detta tar bort {entity} från ”{label}” och laddar om integrationen. " +
      "Tryck Tilldela igen för att bekräfta.",
    "setup.assigned_reloading": "Tilldelade {entity}. Laddar om…",
    "setup.cleared_reloading": "Rensat. Laddar om…",

    "errors.not_connected": "Inte ansluten till Home Assistant.",
    "errors.invalid_window_time":
      "Ett av varmvattenfönstren är inte en giltig tid.",
    "errors.day_start_equals_end":
      "Värmedagen börjar och slutar vid samma timme, vilket inte skulle " +
      "lämna någon komfortperiod alls.",
    "errors.could_not_apply": "Kunde inte tillämpa: {err}",
    "errors.could_not_clear": "Kunde inte rensa: {err}",
    "errors.could_not_save": "Kunde inte spara: {err}",
    "errors.could_not_simulate": "Kunde inte simulera: {err}",
    "errors.no_answer": "Inget svar från optimeraren.",
    "errors.could_not_save_layout": "Kunde inte spara layouten: {err}",
    "errors.could_not_assign": "Kunde inte tilldela: {err}",
    "errors.diag_space": "Uppvärmning",
    "errors.diag_dhw": "Varmvatten",
    "errors.no_plan_data": "Ingen plandata tillgänglig ännu.",
    "errors.diag_not_found":
      "{label}: ingen entitet hittades. Letade efter <code>{id}</code>. " +
      "Kontrollera entitets-id:t under Utvecklarverktyg &gt; Tillstånd " +
      "och ange <code>{kind}_entity</code> i kortets konfiguration.",
    "errors.diag_unavailable": "{label}: <code>{id}</code> är {state}.",
    "errors.diag_no_forecast":
      "{label}: <code>{id}</code> har inget forecast-attribut ännu. Det " +
      "visas efter den första optimeringskörningen.",
    "errors.diag_empty_forecast":
      "{label}: <code>{id}</code> publicerade en tom prognos.",
    "errors.diag_out_of_window":
      "{label}: <code>{id}</code> har {n} punkter, men ingen faller inom " +
      "det valda fönstret.",

    "errors.cfg_not_object":
      "heatpump-optimizer-card: konfigurationen måste vara ett objekt",
    "errors.cfg_space_entity":
      "heatpump-optimizer-card: 'space_entity' måste vara en " +
      "entitets-id-sträng",
    "errors.cfg_dhw_entity":
      "heatpump-optimizer-card: 'dhw_entity' måste vara en " +
      "entitets-id-sträng",
    "errors.cfg_solar_entity":
      "heatpump-optimizer-card: 'solar_entity' måste vara en " +
      "entitets-id-sträng",
    "errors.cfg_what_if":
      "heatpump-optimizer-card: 'what_if' måste vara true eller false",
    "errors.cfg_hours":
      "heatpump-optimizer-card: 'hours' måste vara ett tal mellan 1 och 168",
    "errors.cfg_title":
      "heatpump-optimizer-card: 'title' måste vara en sträng",
    "errors.cfg_series":
      "heatpump-optimizer-card: 'series' måste vara en mappning",
    "errors.cfg_series_unknown":
      "heatpump-optimizer-card: okänd serie '{k}' i 'series'",
    "errors.cfg_series_visibility":
      "heatpump-optimizer-card: synligheten för serien '{k}' måste vara " +
      "true eller false",
    "errors.cfg_show_stats":
      "heatpump-optimizer-card: 'show_stats' måste vara true eller false",

    "headline.savings": "Beräknad besparing",
    "headline.savings_title":
      "Uppskattad besparing för nuvarande plan jämfört med ooptimerad drift.",
    "headline.score": "Optimeringsbetyg",
    "headline.score_title":
      "Hur väl hela anläggningen är inställd och fungerar, 0–100.",
    "headline.savings_pct": "({pct} %)",

    "slots.slot_aria":
      "{lane} {start}–{end}. Tryck Enter för åtgärder, Delete för att " +
      "ta bort.",
    "slots.lane_aria": "Raden {lane}. Tryck Enter för att lägga till ett pass.",

    "editor.title": "Rubrik",
    "editor.space_entity": "Sensor för uppvärmningsplan",
    "editor.dhw_entity": "Sensor för varmvattenplan",
    "editor.solar_entity": "Sensor för solinstrålning",
    "editor.hours": "Timmar att visa",
    "editor.what_if": "Visa schemaredigeraren",
    "editor.show_stats": "Visa nyckeltalsraden",
    "editor.currency": "Valuta",
    "editor.series": "Serier som visas som standard",
  },
};

// The active language. Module-level rather than per-instance because Home
// Assistant has exactly one frontend language per session, and helpers
// outside the class (fmtExpiry, edgeLabel) need it too.
let ACTIVE_LANG = "en";

/** "sv-SE" -> "sv"; anything without a dictionary falls back to English. */
function setLanguage(raw) {
  const code = String(raw || "en").toLowerCase().split(/[-_]/)[0];
  ACTIVE_LANG = STRINGS[code] ? code : "en";
}

/** The translation for `key`, with `{name}` placeholders interpolated.
 *
 * Missing keys fall back to English, then to the key itself -- a visible
 * key on screen beats a silently blank label.
 */
function L(key, vars) {
  const dict = STRINGS[ACTIVE_LANG] || STRINGS.en;
  let text = dict[key];
  if (text === undefined) text = STRINGS.en[key];
  if (text === undefined) return key;
  if (vars) {
    text = text.replace(/\{(\w+)\}/g, (match, name) =>
      vars[name] === undefined ? match : String(vars[name])
    );
  }
  return text;
}

const DEFAULTS = {
  // No default title here: the default is localized, so it is resolved at
  // render time (`_title`) rather than baked into the config at setConfig
  // time, where the language is not yet known.
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
  // The headline stats row under the title: projected savings, optimization
  // score and the plan narrative, when the integration publishes them. It
  // costs nothing when the sensors are absent (the row simply is not
  // rendered), so it is on by default.
  show_stats: true,
};

// Series metadata. `axis` selects one of four value axes: temp / power / price
// / solar. `sensor` selects which forecast the values come from ("space",
// "dhw", "solar", or "either" meaning prefer space then fall back to dhw).
// `field` is the forecast attribute key. Colours are fixed and chosen to read
// on light + dark themes.
const SERIES_DEFS = [
  {
    key: "price",
    labelKey: "series.price",
    axis: "price",
    // The rendered unit is dynamic (`_seriesUnit`): the currency comes from
    // the card config, the plan sensor or Home Assistant. This is only the
    // fallback shape.
    unit: "SEK/kWh",
    color: "#f5a623",
    sensor: "either",
    field: "price",
    style: "stepArea",
  },
  {
    key: "dhw_slots",
    labelKey: "series.dhw_slots",
    axis: "power",
    unit: "kW",
    color: "#e0544e",
    sensor: "dhw",
    field: "dhw_power",
    style: "stepBars",
  },
  {
    key: "space_slots",
    labelKey: "series.space_slots",
    axis: "power",
    unit: "kW",
    color: "#4a90e2",
    sensor: "space",
    field: "space_power",
    style: "stepBars",
  },
  {
    key: "outdoor",
    labelKey: "series.outdoor",
    axis: "temp",
    unit: "\u00b0C",
    color: "#7d8794",
    sensor: "either",
    field: "outdoor",
    style: "smooth",
  },
  {
    key: "dhw_temp",
    labelKey: "series.dhw_temp",
    axis: "temp",
    unit: "\u00b0C",
    color: "#c264d0",
    sensor: "dhw",
    field: "dhw_temp",
    style: "smooth",
  },
  {
    key: "house_temp",
    labelKey: "series.house_temp",
    axis: "temp",
    unit: "\u00b0C",
    color: "#2fae7a",
    sensor: "space",
    field: "room",
    extra: ["upper", "lower"],
    // What each extra trace is called. Without this the zones inherit the
    // series label and the chart claims three different temperatures are all
    // "House temperature".
    extraLabels: {
      upper: "series.upper_floor",
      lower: "series.lower_floor",
    },
    style: "smooth",
  },
  {
    // W/m² is a fourth unit, and both plot edges were already occupied, so it
    // gets an inner right-hand axis that only appears when the series is on.
    // Scaling it into the power axis as kW/m² was the alternative, but a
    // 0.8 kW/m² line sharing a scale with a 5 kW compressor is unreadable.
    key: "solar",
    labelKey: "series.solar",
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
// How close to an edge a grab counts as a resize rather than a move. Under
// a coarse pointer (touch) the hit zone widens to something a finger can
// actually land on; the drawn geometry is unchanged.
const LANE_EDGE_GRAB = 6;
const LANE_EDGE_GRAB_COARSE = 16;
const _coarsePointer = () => {
  try {
    return !!(
      typeof window !== "undefined" &&
      window.matchMedia &&
      window.matchMedia("(pointer: coarse)").matches
    );
  } catch (err) {
    return false;
  }
};
// The card's only animation is a decorative fade on the zoom controls; a user
// who asked the OS for reduced motion gets none of it. Read at render time
// (the style block is rebuilt on every render), with a CSS media query as the
// belt to this suspender for changes between renders.
const _reducedMotion = () => {
  try {
    return !!(
      typeof window !== "undefined" &&
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    );
  } catch (err) {
    return false;
  }
};
const PLAN_STEP_MS = 15 * 60000;

// The headline row's sensors, found by entity-id suffix. Unlike the plan
// sensors these publish no `plan_kind`-style marker to discover them by, so
// the id suffix — stable under has_entity_name for any device name — is the
// contract. Order matters only to the re-render signature.
const HEADLINE_SUFFIXES = [
  "_predicted_savings",
  "_savings_percentage",
  "_optimization_score",
  "_plan_narrative",
];
// Slot-drag edge auto-pan: how close to the plot edge (screen px) engages it,
// and how often the parked pointer advances the view.
const AUTOPAN_MARGIN_PX = 28;
const AUTOPAN_INTERVAL_MS = 90;

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

// How many entities the setup page's picker will RENDER at once. A large
// installation has thousands, and a select with thousands of options is both
// slow to build and useless to scroll. Since v5.1.4 this is a render bound
// and nothing else: it is applied after the picker's text filter, so any
// entity on the install is reachable by typing a few characters of its name
// or its id, and the footnote says when the list is standing on more than it
// shows.
const PICKER_MAX_OPTIONS = 200;

// What a slot is asking for, where the answer is narrower than its accepted
// domains. `sensor` covers every reading a house produces, so on an install
// with hundreds of them the temperature probes are ranked to the top of the
// picker for the slots that want one. Ranking only -- nothing is hidden,
// because plenty of working sensors carry no device class at all. Keyed by
// slot id, and superseded by a `device_class` the backend publishes on the
// slot itself if a later version ever does.
const SLOT_DEVICE_CLASS = {
  outdoor_temp_entity: "temperature",
  indoor_temp_entity: "temperature",
  lower_floor_temp_entity: "temperature",
  floor_return_temp_entity: "temperature",
  buffer_tank_temp_entity: "temperature",
  dhw_temp_entity: "temperature",
  wood_tank_top_entity: "temperature",
  wood_tank_bottom_entity: "temperature",
  valve_outlet_temp_entity: "temperature",
  mixing_valve_target_entity: "temperature",
  power_entity: "power",
  house_power_entity: "power",
  energy_entity: "energy",
  pv_production_entity: "power",
  solar_radiation_entity: "irradiance",
};

// The setup diagram's viewBox width, and how far down a dragged box may be
// parked. Both are needed outside the drawing itself: the layout editor turns
// pointer coordinates into viewBox units, which only works against the same
// width the drawing used.
const SETUP_W = 720;
const SETUP_MAX_Y = 2000;
// One box's width. Module-level because the caption wrapper needs it before
// the layout below has run.
const SETUP_COL_W = 200;

// How far the drawing's text sits inside a box's bounding rect, and how far
// that keeps it off the contour the box is painted with.
//
// v5.1.4: this was 10, against contour walls at x+2 and x+w-2 -- eight
// viewBox units of air, which on a desktop-width dialog reads as text
// pressed against the wall it is inside. 16 leaves 14 units of margin on
// both sides. The box width (200), the column abscissae and the row
// arithmetic are all untouched: only the text moved inward.
const SETUP_PAD = 16;
// The gutter kept between a row's label and its right-anchored value, and
// the narrowest label worth keeping whole-ish. Below `SETUP_MIN_LABEL_W` the
// row stops squeezing the label and shortens the VALUE instead -- see
// `fitSlotRow`.
const SETUP_ROW_GAP = 8;
const SETUP_MIN_LABEL_W = 78;

// ---- Text metrics for the setup drawing -----------------------------------
//
// SVG text neither wraps nor measures itself before it is on screen, so the
// layout has to know how wide a string will render BEFORE it writes it.
// `getComputedTextLength` needs a live, laid-out element; this is the cheap
// substitute: per-glyph advance widths for the sans-serif face the diagram
// is drawn in, as a fraction of the font size, from Helvetica/Arial metrics
// (the faces every platform this runs on falls back to agree within a few
// percent, and the layout only needs to know "does this fit").
//
// The estimate this replaces was a character COUNT -- "a label longer than
// 15 characters is too long" -- which prices an "i" and a "W" the same. It
// under-measured `123 W/m² · Open-Meteo` (proportional digits, a middot, a
// superscript two) badly enough that the right-anchored value ran straight
// through the label beside it on the reporter's install.
const GLYPH_W = (() => {
  const m = new Map();
  const put = (chars, w) => {
    for (const c of chars) m.set(c, w);
  };
  put("ijl", 0.22);
  put(" .,:;!'", 0.28);
  put("ft/I()[]|", 0.3);
  put("r-·²\u00ad", 0.34);
  put("°", 0.4);
  put("ckvxyzsJ", 0.51);
  put("abdeghnopqu0123456789$?L", 0.56);
  put("åäöéèüáà", 0.56);
  put("w", 0.72);
  put("ABEFKPSTVXYZ&", 0.68);
  put("CDGHNOQRU+=<>", 0.74);
  put("mM%@", 0.86);
  put("W", 0.94);
  put("…—", 1.0);
  return m;
})();
const GLYPH_W_DEFAULT = 0.58;
// Semibold text (the values and the titles) sets a few percent wider than
// the regular face at the same size.
const GLYPH_BOLD_FACTOR = 1.06;

/** Rendered width of `s` at `size` px, in viewBox units.
 *
 * Deliberately NOT called `textWidth`: the chart already has a function of
 * that name (a flat `length * CHAR_WIDTH_EM`, good enough for axis units),
 * and function declarations hoist, so the later one would silently win and
 * this whole table would go unused.
 */
function setupTextW(s, size, bold) {
  let em = 0;
  for (const c of String(s)) em += GLYPH_W.has(c) ? GLYPH_W.get(c) : GLYPH_W_DEFAULT;
  return em * size * (bold ? GLYPH_BOLD_FACTOR : 1);
}

/** `s` shortened with an ellipsis until it fits `width`, or "" if nothing does.
 *
 * Trailing spaces are dropped before the ellipsis is added: "Lower floor …"
 * reads as a typo, "Lower floor…" reads as a name that continues.
 */
function ellipsize(s, width, size, bold) {
  const full = String(s);
  if (setupTextW(full, size, bold) <= width) return full;
  const dots = setupTextW("…", size, bold);
  let out = "";
  let w = dots;
  for (const c of full) {
    const cw = setupTextW(c, size, bold);
    if (w + cw > width) break;
    out += c;
    w += cw;
  }
  out = out.replace(/[\s·-]+$/, "");
  return out ? `${out}…` : "";
}

/** Fit one slot row's label and right-anchored value into `inner` units.
 *
 * The two share a single 200-unit row and SVG text does not wrap, so one of
 * them has to give when they do not both fit. The label gives first: it is
 * ellipsized down to whatever the value leaves it, and the row's tooltip
 * still carries the whole thing. Only once the label would drop below
 * `SETUP_MIN_LABEL_W` does the VALUE shorten, and then never by cutting the
 * reading itself: `values` is the ladder of acceptable spellings, longest
 * first ("123 W/m² · Open-Meteo", then "123 W/m²"), and the longest one that
 * leaves the label its minimum wins.
 */
function fitSlotRow(label, values, inner, size) {
  const alts = (Array.isArray(values) ? values : [values]).filter(
    (v) => v !== undefined && v !== null
  );
  const labelW = setupTextW(label, size, false);
  // The label never demands more room than it actually needs, so a short
  // label ("Valve target") can keep a long value whole.
  const reserve = Math.min(labelW, SETUP_MIN_LABEL_W);
  let value = alts[alts.length - 1];
  for (const alt of alts) {
    if (setupTextW(alt, size, true) <= inner - SETUP_ROW_GAP - reserve) {
      value = alt;
      break;
    }
  }
  // A single value so long that even the shortest spelling swamps the row
  // (a sensor whose state is a sentence) is cut as a last resort: an
  // unreadable row still beats two overlapping strings.
  let valueW = setupTextW(value, size, true);
  if (valueW > inner - SETUP_ROW_GAP - 20) {
    value = ellipsize(value, inner - SETUP_ROW_GAP - 20, size, true);
    valueW = setupTextW(value, size, true);
  }
  return {
    value,
    label: ellipsize(label, inner - SETUP_ROW_GAP - valueW, size, false),
    // What the row would have said with unlimited room, for the tooltip.
    full: alts[0],
    shortened: value !== alts[0],
  };
}

// The setup drawing's visual vocabulary (v4.3.0). Each place is drawn as the
// piece of equipment it is instead of a plain rectangle. The geometry carrier
// stays the (now invisible) `setup-box` rect -- the drag editor and the tests
// read it -- and one of these generators paints the visible silhouette over
// it. Every generator is written against the box's own (x, y, w, h), so a box
// that grows a row, or is dragged, keeps its shape: the walls are the only
// vertical segments, and everything else hugs the top or bottom band.
//
// Two stroke weights only: primary 2 (`setup-contour`), detail 1.25
// (`setup-accent`). `inset` is how far a pipe endpoint pulls inside the
// bounding box so pipes meet ink rather than the invisible rect.
const PLACE_KIND = {
  outdoor: "cloud",
  heat_pump: "hp",
  wood_tank: "tank",
  buffer_tank: "tank",
  dhw_tank: "tank",
  mixing_valve: "valve",
  upper_zone: "house",
  lower_zone: "slab",
};
// The hairline between the title and the first slot row, shared by every
// closed shape. It sits between the title's descenders and the first hit
// rect, which is what lets each silhouette shape only the header band.
// A row-less box (h = 32: title only, nothing under the line) gets no
// divider at all -- it would separate the title from nothing, and on the
// valve it grazes the bowtie's top edge. `rightPad` lets a shape whose
// header band is already occupied (the heat pump's fan) stop the line
// short of its own furniture. Both ends follow `SETUP_PAD`, so the rule
// under a title starts where the title starts.
const shapeDivider = (x, y, w, h, rightPad = SETUP_PAD) =>
  h < 49
    ? null
    : {
        d: `M ${x + SETUP_PAD} ${y + 21.5} L ${x + w - rightPad} ${y + 21.5}`,
        cls: "setup-accent divider",
      };
const NODE_SHAPES = {
  // Vertical cylinder: domed top and bottom, straight walls. All three tanks
  // share the silhouette deliberately -- they are the same object class --
  // and identity comes from titles, captions and the wood tank's coil.
  tank: {
    contour: (x, y, w, h) =>
      `M ${x + 2} ${y + 9} ` +
      `A ${(w - 4) / 2} 7 0 0 1 ${x + w - 2} ${y + 9} ` +
      `L ${x + w - 2} ${y + h - 9} ` +
      `A ${(w - 4) / 2} 7 0 0 1 ${x + 2} ${y + h - 9} Z`,
    accents: (x, y, w, h) => [shapeDivider(x, y, w, h)],
    inset: { t: 4.5, r: 2, b: 4.5, l: 2 },
  },
  // Shallow gable over walls, with a chimney. The pitch is capped by the
  // title geometry: the roofline at the title's x must clear the cap
  // height -- at x+16 (v5.1.4's padding) the roof has risen to y+6.7,
  // 2.3 units above the 13px title's cap line, so the wider padding
  // relaxed this constraint rather than tightening it.
  house: {
    contour: (x, y, w, h) =>
      `M ${x + 2} ${y + 7.5} ` +
      `L ${x + w / 2 - 4} ${y + 1.9} ` +
      // r=30 over an 8-unit chord: apex ~y+1.63, a near-smooth knuckle.
      // (r=4 made chord = diameter -- a full semicircle bulging to y-2.1,
      // above the bounding box.)
      `A 30 30 0 0 1 ${x + w / 2 + 4} ${y + 1.9} ` +
      `L ${x + w - 2} ${y + 7.5} ` +
      `L ${x + w - 2} ${y + h - 8} ` +
      `A 6 6 0 0 1 ${x + w - 8} ${y + h - 2} ` +
      `L ${x + 8} ${y + h - 2} ` +
      `A 6 6 0 0 1 ${x + 2} ${y + h - 8} Z`,
    accents: (x, y, w, h) => [
      {
        d: `M ${x + w - 52} ${y + 4.7} V ${y + 1} ` +
          `H ${x + w - 45} V ${y + 5.1}`,
        cls: "setup-contour",
      },
      shapeDivider(x, y, w, h),
    ],
    inset: { t: 6, r: 2, b: 2, l: 2 },
  },
  // The slab: a flat plate with ground hatching under it. The ticks end at
  // y+h+4 exactly -- the deepest overhang the viewBox margin never clips.
  slab: {
    contour: (x, y, w, h) =>
      `M ${x + 6} ${y + 2} H ${x + w - 6} ` +
      `A 4 4 0 0 1 ${x + w - 2} ${y + 6} V ${y + h - 6} ` +
      `A 4 4 0 0 1 ${x + w - 6} ${y + h - 2} H ${x + 6} ` +
      `A 4 4 0 0 1 ${x + 2} ${y + h - 6} V ${y + 6} ` +
      `A 4 4 0 0 1 ${x + 6} ${y + 2} Z`,
    accents: (x, y, w, h) => {
      const out = [shapeDivider(x, y, w, h)];
      for (let i = 0; i < 7; i++) {
        out.push({
          d: `M ${x + 34 + i * 22} ${y + h - 2} ` +
            `L ${x + 28 + i * 22} ${y + h + 4}`,
        });
      }
      return out;
    },
    inset: { t: 2, r: 2, b: 2, l: 2 },
  },
  // The machine: rounded cabinet with the fan in the header's free right
  // corner. Two louvre strokes used to sit in the bottom-left band; from a
  // step back they did not read as vents but as two stray lines in the
  // corner of a box, so v5.1.4 removed them. The fan, its blades and its
  // hub already say "heat pump", and ink that has to be explained is ink
  // the drawing is better without.
  hp: {
    contour: (x, y, w, h) =>
      `M ${x + 12} ${y + 2} H ${x + w - 12} ` +
      `A 10 10 0 0 1 ${x + w - 2} ${y + 12} V ${y + h - 12} ` +
      `A 10 10 0 0 1 ${x + w - 12} ${y + h - 2} H ${x + 12} ` +
      `A 10 10 0 0 1 ${x + 2} ${y + h - 12} V ${y + 12} ` +
      `A 10 10 0 0 1 ${x + 12} ${y + 2} Z`,
    accents: (x, y, w, h) => [
      {
        d: `M ${x + w - 26} ${y + 13} ` +
          `A 8 8 0 1 1 ${x + w - 10} ${y + 13} ` +
          `A 8 8 0 1 1 ${x + w - 26} ${y + 13}`,
      },
      { cx: x + w - 18, cy: y + 13, r: 1.6, cls: "setup-accent hub" },
      {
        d: `M ${x + w - 18} ${y + 10.5} ` +
          `A 5 5 0 0 1 ${x + w - 13.8} ${y + 8} ` +
          `M ${x + w - 15.8} ${y + 14.3} ` +
          `A 5 5 0 0 1 ${x + w - 15.8} ${y + 19.1} ` +
          `M ${x + w - 20.2} ${y + 14.3} ` +
          `A 5 5 0 0 1 ${x + w - 24.4} ${y + 11.9}`,
      },
      // The fan shroud's bottom is y+21, tangent to the divider's y+21.5:
      // the line stops at x+w-30, clear of the shroud's left edge at x+w-26.
      shapeDivider(x, y, w, h, 30),
    ],
    inset: { t: 2, r: 2, b: 2, l: 2 },
  },
  // Chamfered block, with the bowtie valve symbol straddling the bottom edge
  // at the same-column pipe abscissa x+24 -- on its own pipe, the way a
  // hydronic schematic marks a valve. No glyph in the header: valve titles
  // are the longest on the page.
  valve: {
    contour: (x, y, w, h) =>
      `M ${x + 12} ${y + 2} H ${x + w - 12} ` +
      `L ${x + w - 2} ${y + 12} V ${y + h - 12} ` +
      `L ${x + w - 12} ${y + h - 2} H ${x + 12} ` +
      `L ${x + 2} ${y + h - 12} V ${y + 12} Z`,
    accents: (x, y, w, h) => [
      {
        d: `M ${x + 18} ${y + h - 10} H ${x + 30} ` +
          `L ${x + 24} ${y + h - 2} Z ` +
          `M ${x + 24} ${y + h - 2} ` +
          `L ${x + 18} ${y + h + 6} H ${x + 30} Z`,
        cls: "setup-contour",
      },
      shapeDivider(x, y, w, h),
    ],
    inset: { t: 2, r: 2, b: 2, l: 2 },
  },
  // Outside air is unbounded, so it gets no walls: an open tray baseline the
  // rows hang over, and a cloud glyph in the header's right corner. No
  // header divider either -- the composition is open.
  cloud: {
    contour: (x, y, w, h) =>
      `M ${x + 2} ${y + h - 8} ` +
      `A 6 6 0 0 0 ${x + 8} ${y + h - 2} H ${x + w - 8} ` +
      `A 6 6 0 0 0 ${x + w - 2} ${y + h - 8}`,
    accents: (x, y, w) => [
      {
        d: `M ${x + w - 46} ${y + 19} ` +
          `A 5.5 5.5 0 0 1 ${x + w - 43} ${y + 9.5} ` +
          `A 7 7 0 0 1 ${x + w - 30} ${y + 6.5} ` +
          `A 6 6 0 0 1 ${x + w - 19} ${y + 9} ` +
          // r=6, not 5.5: this chord is sqrt(6^2+10^2) ~ 11.66, and a radius
          // under chord/2 would be auto-scaled to an exact semicircle.
          `A 6 6 0 0 1 ${x + w - 13} ${y + 19} Z`,
        cls: "setup-contour",
      },
    ],
    inset: { t: 0, r: 0, b: 2, l: 0 },
  },
};

// Human names for the places pipes connect, mirroring `topology.PLACE_LABELS`.
// Only the layout editor's rejection line uses them -- every box already
// carries its own title -- so a place added on the backend without a label
// here degrades to its id rather than disappearing.
const PLACE_LABELS = {
  heat_pump: "places.heat_pump",
  buffer_tank: "places.buffer_tank",
  mixing_valve: "places.mixing_valve",
  upper_zone: "places.upper_zone",
  lower_zone: "places.lower_zone",
  wood_tank: "places.wood_tank",
  wood_valve: "places.wood_valve",
  dhw_tank: "places.dhw_tank",
  slab_shunt: "places.slab_shunt",
};

/** A place id as something a person can read; unknown ids stay as-is. */
function placeLabel(id) {
  return PLACE_LABELS[id] ? L(PLACE_LABELS[id]) : id;
}

/** "mixing_valve>lower_zone" as something a person can read. */
function edgeLabel(name) {
  const [a, b] = String(name).split(">");
  return `${placeLabel(a)} → ${placeLabel(b)}`;
}

// Human-readable labels for the plan reason codes the optimizer publishes.
// Without these an unexpected slot is indistinguishable from a bug.
const REASON_LABELS = {
  comfort_floor: "reasons.comfort_floor",
  cheap_price: "reasons.cheap_price",
  preheat_weather: "reasons.preheat_weather",
  scheduled: "reasons.scheduled",
  terminal_value: "reasons.terminal_value",
  solar_surplus: "reasons.solar_surplus",
  dhw_window: "reasons.dhw_window",
  dhw_ready: "reasons.dhw_ready",
  dhw_preheat: "reasons.dhw_preheat",
  legionella: "reasons.legionella",
  manual_plan: "reasons.manual_plan",
  idle: "reasons.idle",
};

/** Whether two point series are the same curve, to the plotted precision.
 *
 * Values arrive rounded to two decimals from the integration, so an exact
 * comparison is the right one: a genuinely separate zone differs by far more
 * than that, and a copy differs by nothing at all.
 */
function samePoints(a, b) {
  if (!a || !b || a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) {
    if (a[i].t !== b[i].t || a[i].v !== b[i].v) return false;
  }
  return true;
}

/** The swatch for one trace: solid for a primary line, dashed for an extra.
 *
 * The chart already distinguishes them by stroke, so the legend chip and the
 * tooltip dot have to as well — otherwise two rows in the same colour look
 * like the same line reported twice.
 */
function dotStyle(color, dashed) {
  return dashed
    ? `background:repeating-linear-gradient(90deg,${color} 0 3px,transparent 3px 6px)`
    : `background:${color}`;
}

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
 *
 * Dates are formatted in ACTIVE_LANG, not the browser locale: this string is
 * embedded in prose translated per hass.language, and a browser set to
 * another language would otherwise yield "Låst till 17:00 på Friday".
 */
function fmtExpiry(when) {
  const time = when.toLocaleTimeString(ACTIVE_LANG, {
    hour: "2-digit",
    minute: "2-digit",
  });
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
  if (isTomorrow) return L("time.tomorrow", { time });
  return L("time.on_weekday", {
    time,
    weekday: when.toLocaleDateString(ACTIVE_LANG, { weekday: "long" }),
  });
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
    // The entity picker's per-visit state: which slot is open, what has been
    // typed into its filter, which entity is chosen (null = "whatever the
    // slot already holds") and whether an Assign that would CLEAR the slot
    // has been armed.
    this._pickerKey = null;
    this._pickerSlot = null;
    this._pickerFilter = "";
    this._pickerChoice = null;
    this._pendingClear = false;
    this._clearTimer = null;
    this._dialogFontPx = 0;
    this._dialogScroll = 0;
    // Pan/zoom window (item 23). `null` means "the default window", so an
    // untouched card behaves exactly as it did before this existed.
    this._view = null;
    this._viewLimits = null;
    this._viewFrame = 0;
    this._pan = null;
    this._suppressClick = false;
    // The layout editor (v3.16.0, issue #40). Instance state, like the what-if
    // draft and for the same reason: `_render` rebuilds the shadow root on the
    // coordinator's schedule, and a half-drawn layout that vanished on a plan
    // refresh would be worse than no editor. `null` means "not editing", so an
    // untouched setup page behaves exactly as it did before this existed.
    this._layoutEdit = null;
    // Where the last drawing put each box, in viewBox units, so a drop can be
    // tested against real geometry instead of guessing from the event target.
    this._layoutBoxes = [];
    this._onLayoutDown = this._onLayoutDown.bind(this);
    this._onLayoutMove = this._onLayoutMove.bind(this);
    this._onLayoutUp = this._onLayoutUp.bind(this);
    this._onLayoutClick = this._onLayoutClick.bind(this);
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
      throw new Error(L("errors.cfg_not_object"));
    }
    const cfg = { ...DEFAULTS, ...config };

    if (typeof cfg.space_entity !== "string" || !cfg.space_entity.includes(".")) {
      throw new Error(L("errors.cfg_space_entity"));
    }
    if (typeof cfg.dhw_entity !== "string" || !cfg.dhw_entity.includes(".")) {
      throw new Error(L("errors.cfg_dhw_entity"));
    }
    if (typeof cfg.solar_entity !== "string" || !cfg.solar_entity.includes(".")) {
      throw new Error(L("errors.cfg_solar_entity"));
    }
    if (typeof cfg.what_if !== "boolean") {
      throw new Error(L("errors.cfg_what_if"));
    }
    if (typeof cfg.show_stats !== "boolean") {
      throw new Error(L("errors.cfg_show_stats"));
    }
    const hours = Number(cfg.hours);
    if (!Number.isFinite(hours) || hours <= 0 || hours > 168) {
      throw new Error(L("errors.cfg_hours"));
    }
    cfg.hours = hours;
    if (cfg.title !== undefined && typeof cfg.title !== "string") {
      throw new Error(L("errors.cfg_title"));
    }
    if (cfg.series !== undefined) {
      if (typeof cfg.series !== "object" || cfg.series === null) {
        throw new Error(L("errors.cfg_series"));
      }
      for (const k of Object.keys(cfg.series)) {
        if (!SERIES_DEFS.some((s) => s.key === k)) {
          throw new Error(L("errors.cfg_series_unknown", { k }));
        }
        if (typeof cfg.series[k] !== "boolean") {
          throw new Error(L("errors.cfg_series_visibility", { k }));
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
    // The frontend's language rides on the hass object; keep the dictionary
    // in step before anything renders. `_signature` includes the language,
    // so a switch re-renders even when the data has not changed.
    setLanguage(hass && hass.language);
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

  /** The visual editor, defined in this same file (no build step, no lazy
   * chunk to fetch). Home Assistant awaits the return value, so returning
   * the element directly is part of the contract. */
  static getConfigElement() {
    return document.createElement(EDITOR_TAG);
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
    // Nor an armed "clear this slot" confirmation in the entity picker.
    this._cancelPendingClear();
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

  // Two cards can plot the same entities — a 24 h card on the wall panel
  // dashboard and a 48 h card with its own title on another — so the key
  // carries the card's config identity (title + hours), not just its data
  // sources. Otherwise a series toggled off on one card silently disappears
  // from the other.
  _storageKey(cfg) {
    const title = cfg.title !== undefined ? cfg.title : "";
    return `${CARD_TAG}:${cfg.space_entity}:${cfg.dhw_entity}:${title}:${cfg.hours}`;
  }

  /** The pre-v4.2.0 key, read as a fallback so an upgrade does not silently
   * drop every saved series toggle. Writes always go to the new key. */
  _storageKeyLegacy(cfg) {
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
        const raw =
          localStorage.getItem(this._storageKey(cfg)) ||
          localStorage.getItem(this._storageKeyLegacy(cfg));
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
      // A language switch or a currency change redraws text without any
      // plan data changing, so both belong in the signature.
      ACTIVE_LANG,
      this._currency(),
      // The headline reads its own sensors; leaving them out would freeze
      // the row at whatever the first render saw.
      this._headlineSignature(),
    ].join("|");
  }

  /** The headline sensors' contribution to the re-render signature. */
  _headlineSignature() {
    if (!this._config.show_stats) return "off";
    return HEADLINE_SUFFIXES.map((sfx) => {
      const st = this._statEntity(sfx);
      return st ? `${st.state}@${st.last_updated || ""}` : "-";
    }).join("~");
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
      let primaryPts = null;
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
          const primary = field === def.field;
          // A single-zone house still publishes `upper` and `lower`: the
          // one-zone dynamics set both to the room temperature step by step,
          // so the extras are exact copies of the primary. Drawing them put
          // two dashed lines under the solid one, and naming them would put
          // two more chips in the legend and two more rows in the tooltip for
          // a house that has one zone. Drop a duplicate rather than label it.
          if (!primary && samePoints(pts, primaryPts)) continue;
          if (primary) primaryPts = pts;
          lines.push({
            field,
            points: pts,
            primary,
            // Named per line, not per series: `_lineLabel` resolves the
            // dictionary key so the tooltip and the legend cannot disagree
            // about what a trace is called.
            labelKey: primary
              ? def.labelKey
              : (def.extraLabels || {})[field] || def.labelKey,
          });
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
    const label = L(kind === "space" ? "errors.diag_space" : "errors.diag_dhw");
    const st = this._stateOf(id);
    if (!st) {
      return L("errors.diag_not_found", { label, id: esc(id), kind });
    }
    if (st.state === "unavailable" || st.state === "unknown") {
      return L("errors.diag_unavailable", {
        label,
        id: esc(id),
        state: esc(st.state),
      });
    }
    const fc = this._forecast(id);
    if (!fc) {
      return L("errors.diag_no_forecast", { label, id: esc(id) });
    }
    if (!fc.length) {
      return L("errors.diag_empty_forecast", { label, id: esc(id) });
    }
    return L("errors.diag_out_of_window", {
      label,
      id: esc(id),
      n: fc.length,
    });
  }

  /** The card's display title: the configured one, or the localized default. */
  _title() {
    const t = this._config && this._config.title;
    return t !== undefined ? t : L("header.default_title");
  }

  // ---- headline stats ----------------------------------------------------

  /** The state object of a headline sensor, found by id suffix and cached.
   *
   * The savings/score/narrative sensors publish no `plan_kind`-style marker,
   * so the suffix — which has_entity_name keeps stable under any device
   * name — is the discovery contract.
   *
   * They also share a device with the plan sensors, which means they share
   * an entity-id prefix. Deriving the stat id from the RESOLVED plan sensor
   * (config first, then plan_kind discovery — `_resolveEntity` already owns
   * that) is both cheap and scoped to this card's config entry; a global
   * scan could bind the headline to another entry's — or a foreign
   * integration's — sensors. The scan survives only as a fallback for
   * hand-renamed stat entities, and its result is cached even when it is a
   * miss: the negative cache is keyed to the number of `sensor.` ids, so a
   * late-arriving backend is still found without rescanning every state
   * batch.
   */
  _statEntity(suffix) {
    const states = this._hass && this._hass.states;
    if (!states) return null;
    if (!this._statCache) this._statCache = {};
    if (!this._statMissAt) this._statMissAt = {};
    const cached = this._statCache[suffix];
    if (cached && states[cached]) return states[cached];

    for (const [kind, planSuffix] of [
      ["space", "_space_heating_plan"],
      ["dhw", "_dhw_heating_plan"],
    ]) {
      const planId = this._resolveEntity(kind);
      if (!planId || !states[planId] || !planId.endsWith(planSuffix)) {
        continue;
      }
      const candidate = planId.slice(0, -planSuffix.length) + suffix;
      if (states[candidate]) {
        this._statCache[suffix] = candidate;
        delete this._statMissAt[suffix];
        return states[candidate];
      }
    }

    const count = this._sensorCount(states);
    if (this._statMissAt[suffix] === count) return null;
    // Sorted iteration makes a tie deterministic, the same choice
    // `_resolveEntity` makes.
    for (const id of Object.keys(states).sort()) {
      if (!id.startsWith("sensor.") || !id.endsWith(suffix)) continue;
      this._statCache[suffix] = id;
      delete this._statMissAt[suffix];
      return states[id];
    }
    this._statMissAt[suffix] = count;
    return null;
  }

  /** How many `sensor.` entity ids this state batch holds.
   *
   * Memoized per batch object — hass replaces `states` wholesale on every
   * update, so object identity is the batch's identity. This is what the
   * negative cache above is keyed to.
   */
  _sensorCount(states) {
    if (this._sensorCountFor !== states) {
      let n = 0;
      for (const id of Object.keys(states)) {
        if (id.startsWith("sensor.")) n++;
      }
      this._sensorCountFor = states;
      this._sensorCountN = n;
    }
    return this._sensorCountN;
  }

  /** A headline sensor's state as a finite number, or null. */
  _statNumber(suffix) {
    const st = this._statEntity(suffix);
    if (!st || st.state === "unavailable" || st.state === "unknown") {
      return null;
    }
    const v = Number(st.state);
    return Number.isFinite(v) ? v : null;
  }

  /** The compact stats row under the header, or nothing at all.
   *
   * Every part is optional because every source sensor is: the score sensor
   * is unavailable until enough history exists, the savings sensors null out
   * between optimizer runs, and old integrations publish none of them. A row
   * with nothing to say renders no chrome rather than an empty strip.
   */
  _headlineHtml() {
    if (!this._config.show_stats) return "";
    const items = [];

    const savings = this._statNumber("_predicted_savings");
    if (savings !== null) {
      const pct = this._statNumber("_savings_percentage");
      // The savings sensor declares the unit its value is denominated in;
      // nothing here converts, so a card-config `currency:` must not relabel
      // it. `_currency()` only fills in when the sensor declares no unit.
      const savingsSt = this._statEntity("_predicted_savings");
      const unit =
        (savingsSt &&
          savingsSt.attributes &&
          savingsSt.attributes.unit_of_measurement) ||
        this._currency();
      const value =
        `${savings.toFixed(2)} ${unit}` +
        (pct !== null
          ? ` ${L("headline.savings_pct", { pct: pct.toFixed(0) })}`
          : "");
      items.push({
        cls: "savings",
        title: L("headline.savings_title"),
        label: L("headline.savings"),
        value,
      });
    }

    const score = this._statNumber("_optimization_score");
    if (score !== null) {
      items.push({
        cls: "score",
        title: L("headline.score_title"),
        label: L("headline.score"),
        value: `${Math.round(score)}/100`,
      });
    }

    // The narrative arrives already rendered in Home Assistant's language
    // (the coordinator owns those templates), so the first line is shown
    // verbatim rather than re-keyed here.
    const narrative = this._statEntity("_plan_narrative");
    const lines =
      narrative && narrative.attributes && narrative.attributes.lines;
    const line =
      Array.isArray(lines) && typeof lines[0] === "string" && lines[0]
        ? lines[0]
        : null;

    if (!items.length && !line) return "";
    const stats = items
      .map(
        (it) =>
          `<span class="hl-stat hl-${it.cls}" title="${esc(it.title)}">` +
          `<span class="hl-label">${esc(it.label)}</span> ` +
          `<span class="hl-value">${esc(it.value)}</span></span>`
      )
      .join("");
    return `<div class="headline">
      ${stats ? `<div class="hl-stats">${stats}</div>` : ""}
      ${line ? `<div class="hl-narrative">${esc(line)}</div>` : ""}
    </div>`;
  }

  _render() {
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
      body = `<div class="empty">${L("errors.no_plan_data")}<br>
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
          <span class="title">${esc(this._title())}</span>
          ${
            anyData
              ? `<button type="button" class="expand" title="${esc(
                  L("header.enlarge")
                )}"
                   aria-label="${esc(L("header.enlarge_chart"))}">${EXPAND_ICON}</button>`
              : ""
          }
        </div>
        ${this._headlineHtml()}
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
    // Which page the dialog shows is instance state on purpose: `_render`
    // rebuilds the shadow root on every plan refresh, on the coordinator's
    // schedule, and a refresh must not yank the user off the setup page they
    // are reading (the `_runs` memoisation bug class from v3.2.0).
    const page = this._dialogPage === "setup" ? "setup" : "plan";
    // The hidden page is genuinely unrendered, not `display: none`:
    // `getBoundingClientRect()` returns zeroes for a hidden element, so
    // `_timeAtClientX` would compute garbage drag times rather than fail.
    const body =
      page === "setup"
        ? this._setupPageHtml()
        : `${this._chartBlock(built, true)}${this._whatIfHtml()}`;
    const tab = (id, label) =>
      `<button type="button" class="dlg-tab${page === id ? " active" : ""}"
         data-page="${id}" role="tab"
         aria-selected="${page === id}">${label}</button>`;
    return `
      <dialog class="expanded" aria-label="${esc(this._title())}">
        <div class="dlg-head">
          <span class="title">${esc(this._title())}</span>
          <div class="dlg-tabs" role="tablist">
            ${tab("plan", esc(L("header.tab_plan")))}
            ${tab("setup", esc(L("header.tab_setup")))}
          </div>
          <button type="button" class="close" title="${esc(L("header.close"))}"
            aria-label="${esc(L("header.close"))}">${CLOSE_ICON}</button>
        </div>
        ${page === "plan" ? this._legendHtml() : ""}
        <div class="dlg-body">
          ${body}
        </div>
      </dialog>
    `;
  }

  /** Item 33: the configured system as a picture, with live values in place.
   *
   * Drawn from the `setup_topology` attribute the plan sensors publish --
   * the same description the options flow's overview renders, emitted by the
   * coordinator so the two can never disagree. Live readings come straight
   * from `hass.states`, which is fresher than anything routed through the
   * coordinator and free.
   *
   * Static inline SVG, hand-written like the rest of the card: no build
   * step, no dependencies, and nothing interactive to begin with.
   */
  _setupPageHtml() {
    const topo = this._planAttrRaw("setup_topology", null);
    if (!topo || !Array.isArray(topo.slots)) {
      return `<div class="setup-page"><div class="empty">
        ${L("setup.not_published")}</div></div>`;
    }
    const editing = this._layoutEditing();
    // The svg lives in a wrapper of its own so an edit can redraw the diagram
    // without rebuilding the page around it: the pointer handlers are attached
    // to the wrapper, and a drag that replaced its own listeners mid-gesture
    // would drop the pointer.
    return `<div class="setup-page${editing ? " editing" : ""}">
      ${this._layoutBarHtml(topo)}
      <div class="setup-canvas">${this._setupSvg(topo)}</div>
      ${this._setupPickerHtml(topo)}
      <div class="setup-hint">${
        editing ? L("setup.editing_hint") : L("setup.assign_hint")
      }</div>
      <div class="setup-result" role="status"></div></div>`;
  }

  /** True while the layout editor is open. */
  _layoutEditing() {
    return !!(this._layoutEdit && this._layoutEdit.active);
  }

  /** True when there is an edit worth writing: a change, and a layout to
   * name it. Either alone is not something to offer to save. */
  _layoutSaveable() {
    const ed = this._layoutEdit;
    return !!(ed && ed.active && ed.match && ed.dirty);
  }

  /** True when there is something to take back: a change made since the
   * editor opened. An untouched drawing already IS the layout in use, so
   * Undo would do nothing and must not pretend otherwise. */
  _layoutUndoable() {
    const ed = this._layoutEdit;
    return !!(ed && ed.active && ed.dirty && ed.baseline);
  }

  /** A position map copied down to its coordinate pairs. */
  _copyPositions(positions) {
    const out = {};
    for (const key of Object.keys(positions || {})) {
      const at = positions[key];
      out[key] = Array.isArray(at) ? at.slice() : at;
    }
    return out;
  }

  /** The editor's own controls: the toggle, Save, and the verdict line.
   *
   * Offered only when the coordinator publishes a catalog. Without one there
   * is nothing to validate a drawing against, and an editor that could not
   * tell a supported layout from an invented one is exactly the "diagram that
   * lies about the physics" this feature exists to end.
   */
  _layoutBarHtml(topo) {
    // An editor already open keeps its toggle even if the catalog goes away
    // under it (an integration downgrade mid-session); a bar that vanished
    // would leave the editor open with no way out of it.
    if (
      (!Array.isArray(topo.catalog) || !topo.catalog.length) &&
      !this._layoutEditing()
    ) {
      return "";
    }
    const ed = this._layoutEdit;
    const active = this._layoutEditing();
    const match = active && ed.match ? ed.match : null;
    return `
      <div class="layout-bar">
        <button type="button" class="layout-edit-toggle${active ? " on" : ""}"
          aria-pressed="${active}">${
            active ? esc(L("setup.done_editing")) : esc(L("setup.edit_layout"))
          }</button>
        ${
          active
            ? `<button type="button" class="layout-save"${
                this._layoutSaveable() ? "" : ` disabled="disabled"`
              }>${esc(L("setup.save_layout"))}</button>`
            : ""
        }
        ${
          active
            ? `<button type="button" class="layout-undo"${
                this._layoutUndoable() ? "" : ` disabled="disabled"`
              } title="${esc(L("setup.undo_layout_aria"))}"
              aria-label="${esc(L("setup.undo_layout_aria"))}">${
                esc(L("setup.undo_layout"))
              }</button>`
            : ""
        }
        ${
          active
            ? `<span class="layout-verdict${match ? " match" : ""}"
                 role="status">${esc((ed && ed.verdict) || "")}</span>`
            : ""
        }
      </div>`;
  }

  /** The entity picker for one slot, or nothing when none is open.
   *
   * Item 32's click-to-assign, on the card rather than in a custom panel: the
   * card is already authenticated, already draws the diagram and already has
   * `hass`, so this needs one validated service instead of a second frontend
   * with its own hand-rolled config-write path.
   *
   * Candidates come from `hass.states`, filtered to the domains the slot
   * accepts -- the same list the service validates against, published on the
   * slot itself so the picker cannot offer what the service would refuse.
   */
  _setupPickerHtml(topo) {
    const key = this._pickerKey;
    if (!key) return "";
    const slot = (topo.slots || []).find((s) => s.key === key);
    if (!slot) return "";
    // The open picker's slot, for the handlers: the filter box rebuilds the
    // option list without re-rendering the page (which would take the focus
    // out of the input the user is typing into), and needs the same slot
    // this render used.
    this._pickerSlot = slot;
    const model = this._pickerModel(slot);
    const filter = this._pickerFilter || "";
    return `
      <div class="setup-picker">
        <div class="sp-title">${esc(slot.label)}</div>
        <input class="sp-filter" type="text" value="${esc(filter)}"
          placeholder="${esc(L("setup.picker_filter_placeholder"))}"
          aria-label="${esc(
            L("setup.picker_filter_aria", { slot: slot.label })
          )}" />
        <select class="sp-select" size="8" aria-label="${esc(
          L("setup.picker_aria", { slot: slot.label })
        )}">${model.options}</select>
        <div class="sp-actions">
          <button type="button" class="sp-save">${esc(L("setup.assign"))}</button>
          <button type="button" class="sp-cancel">${esc(L("setup.cancel"))}</button>
        </div>
        <div class="sp-note">${esc(model.note)}</div>
      </div>`;
  }

  /** The picker's option list and its footnote, for one slot.
   *
   * Three rules this had wrong before v5.1.4, each of them destructive:
   *
   *  - The entity the slot ALREADY holds is always an option, and always the
   *    selected one. It used to be offered only if it happened to fall
   *    inside the candidate list; when it did not -- a renamed entity, one
   *    past the cap, one whose domain the slot no longer lists -- the
   *    `<select>` fell back to "(not configured)", and pressing Assign
   *    wrote that emptiness back and reloaded the integration. The user was
   *    shown a cleared slot and a destructive default in the same control.
   *  - The cap applies AFTER the filter, so every entity on the install is
   *    reachable by typing. It used to truncate the alphabetical candidate
   *    list, which on a large install simply hid the user's own probe with
   *    no way to reach it.
   *  - Every option shows the entity id next to the friendly name.
   *    Auto-generated names collide ("Vedpanna temperatur" twice, one of
   *    them silently `..._2`), and a list of identical labels is a list
   *    nobody can choose from.
   */
  _pickerModel(slot) {
    const domains = slot.domains || [];
    const states = (this._hass && this._hass.states) || {};
    const nameOf = (id) => {
      const st = states[id];
      return (st && st.attributes && st.attributes.friendly_name) || id;
    };
    const labelOf = (id) => {
      if (!states[id]) return `${id} — ${L("setup.picker_missing")}`;
      const friendly = nameOf(id);
      return friendly === id ? id : `${friendly} — ${id}`;
    };
    // A slot that wants a temperature says so; a matching device class is
    // ranked first so the probe the slot is for is near the top before a
    // single character is typed. Ranking only -- nothing is hidden by it,
    // because a house full of unclassified sensors is normal.
    const want = slot.device_class || SLOT_DEVICE_CLASS[slot.key] || null;
    const classOf = (id) => {
      const st = states[id];
      return (st && st.attributes && st.attributes.device_class) || "";
    };
    const all = Object.keys(states).filter((id) =>
      domains.includes(id.split(".")[0])
    );
    const q = String(this._pickerFilter || "").trim().toLowerCase();
    const matching = q
      ? all.filter((id) => labelOf(id).toLowerCase().includes(q))
      : all;
    matching.sort((a, b) => {
      if (want) {
        const ra = classOf(a) === want ? 0 : 1;
        const rb = classOf(b) === want ? 0 : 1;
        if (ra !== rb) return ra - rb;
      }
      return a < b ? -1 : a > b ? 1 : 0;
    });
    const shown = matching.slice(0, PICKER_MAX_OPTIONS);
    // What the select must come up on: the user's own pick this time round,
    // otherwise whatever the slot is configured with.
    const chosen =
      this._pickerChoice === null || this._pickerChoice === undefined
        ? slot.entity || ""
        : this._pickerChoice;
    const listed = new Set(shown);
    const options = [
      `<option value=""${chosen ? "" : " selected"}>${esc(
        L("setup.picker_none")
      )}</option>`,
    ];
    // The current entity rides at the top of the list, outside the filter
    // and outside the cap: it is the one option whose absence would rewrite
    // the configuration.
    if (chosen && !listed.has(chosen)) {
      options.push(
        `<option value="${esc(chosen)}" selected>${esc(labelOf(chosen))}</option>`
      );
    }
    for (const id of shown) {
      options.push(
        `<option value="${esc(id)}"${id === chosen ? " selected" : ""}>${esc(
          labelOf(id)
        )}</option>`
      );
    }
    let note;
    if (matching.length > shown.length) {
      note = L("setup.picker_showing", {
        n: shown.length,
        total: matching.length,
      });
    } else if (q && !matching.length) {
      note = L("setup.picker_no_match", { q });
    } else {
      note = L("setup.picker_count", {
        n: matching.length,
        domains: domains.join("/"),
      });
    }
    return { options: options.join(""), note, total: matching.length,
      shown: shown.length };
  }

  /** Close the picker, dropping everything that belonged to that visit. */
  _closePicker() {
    this._pickerKey = null;
    this._pickerSlot = null;
    this._pickerViaKeyboard = false;
    this._pickerFilter = "";
    this._pickerChoice = null;
    this._cancelPendingClear();
  }

  /** Disarm the "this would clear the slot" confirmation. */
  _cancelPendingClear() {
    if (this._clearTimer) {
      clearTimeout(this._clearTimer);
      this._clearTimer = null;
    }
    this._pendingClear = false;
  }

  /** Disarm it and put the Assign button back the way it was. */
  _disarmClear(picker) {
    this._cancelPendingClear();
    const root = picker || (this.shadowRoot && this.shadowRoot.querySelector(
      ".setup-picker"));
    const save = root && root.querySelector(".sp-save");
    if (save) {
      save.textContent = L("setup.assign");
      save.classList.remove("confirm");
    }
  }

  /** Wire the setup page's clickable slots and its picker. */
  _attachSetupEvents(root) {
    this._attachLayoutEditor(root);
    const openPicker = (key, viaKeyboard) => {
      // While the layout editor is open a click on a box is the start of a
      // drag, not a request to assign a sensor. Opening the picker over the
      // diagram being edited would put a dialog on top of the drag.
      if (this._layoutEditing()) return;
      // A fresh visit: no filter, no half-made choice, no armed clear left
      // over from the row before this one.
      this._closePicker();
      this._pickerKey = key;
      // Opened from the keyboard, focus must land in the picker: the hit
      // target that had it is rebuilt by the render below, so without this
      // the keyboard user is dropped back at the top of the dialog.
      this._pickerFocus = !!viaKeyboard;
      // ...and remembered for the way back out. Handing focus to a row a
      // MOUSE user is no longer looking at is what left a focus ring stuck
      // on the sensor field after Cancel (v5.1.4).
      this._pickerViaKeyboard = !!viaKeyboard;
      this._render();
    };
    // Any pointer gesture that is not on a row takes focus off whichever row
    // has it. Without this a ring can outlive the gesture that caused it --
    // the reported "thin blue line beside the sensor field" after cancelling
    // the picker and clicking away.
    root.addEventListener("pointerdown", (ev) => {
      const t = ev && ev.target;
      if (t && t.classList && t.classList.contains("setup-hit")) return;
      this._blurSetupRow();
    });
    for (const hit of root.querySelectorAll(".setup-hit")) {
      hit.addEventListener("click", (ev) => {
        ev.stopPropagation();
        openPicker(ev.currentTarget.dataset.key, false);
      });
      // The hits are focusable buttons (role="button"), so Enter and Space
      // must do what a click does.
      hit.addEventListener("keydown", (ev) => {
        if (ev.key !== "Enter" && ev.key !== " ") return;
        if (ev.preventDefault) ev.preventDefault();
        stop(ev);
        openPicker(ev.currentTarget.dataset.key, true);
      });
    }
    const picker = root.querySelector(".setup-picker");
    if (!picker) return;
    // Every control stops propagation: the dialog closes on a click that
    // lands on its backdrop, and a click inside the picker is not that.
    picker.addEventListener("click", (ev) => ev.stopPropagation());
    // Escape backs out of the picker without assigning, from any of its
    // controls — the keyboard twin of the Cancel button. Closing re-renders,
    // which destroys whichever picker control held focus, so focus is
    // walked back to the setup row the picker was opened from.
    picker.addEventListener("keydown", (ev) => {
      if (ev.key !== "Escape") return;
      stop(ev);
      const key = this._pickerKey;
      this._closePicker();
      this._render();
      this._restoreSetupFocus(key);
    });
    const select = picker.querySelector(".sp-select");
    if (select && this._pickerFocus) {
      this._pickerFocus = false;
      if (typeof select.focus === "function") select.focus();
    }
    // Typing narrows the list in place. A full `_render()` would rebuild the
    // input and take the caret with it, so only the options and the footnote
    // are replaced; the select keeps whatever the user had highlighted when
    // that entity is still on the list.
    const filterBox = picker.querySelector(".sp-filter");
    if (filterBox) {
      filterBox.addEventListener("input", (ev) => {
        const target = ev.currentTarget || ev.target;
        this._pickerFilter = (target && target.value) || "";
        const slot = this._pickerSlot;
        if (!slot) return;
        const model = this._pickerModel(slot);
        const list = picker.querySelector(".sp-select");
        if (list) list.innerHTML = model.options;
        const foot = picker.querySelector(".sp-note");
        if (foot) foot.textContent = model.note;
      });
    }
    // The chosen entity is remembered on the card, not only in the DOM: the
    // list is rebuilt on every keystroke, and a choice that lived only in
    // the `<select>` would be forgotten by the next one.
    if (select) {
      select.addEventListener("change", (ev) => {
        const target = ev.currentTarget || ev.target;
        this._pickerChoice = (target && target.value) || "";
        // Choosing again disarms a clear that was armed for a different
        // answer than the one now selected.
        if (this._pendingClear) this._disarmClear(picker);
      });
    }
    const cancel = picker.querySelector(".sp-cancel");
    if (cancel) {
      cancel.addEventListener("click", (ev) => {
        ev.stopPropagation();
        const key = this._pickerKey;
        const viaKeyboard = this._pickerViaKeyboard;
        this._closePicker();
        this._render();
        // A keyboard user must land back on the row they came from, or they
        // are dropped at the top of the dialog. A mouse user must NOT: the
        // row would light up with a focus ring around a field they have
        // just backed out of, and clicking elsewhere does not always take
        // it off an SVG element again.
        if (viaKeyboard) this._restoreSetupFocus(key);
        else this._blurSetupRow();
      });
    }
    const save = picker.querySelector(".sp-save");
    if (save) {
      const assign = async (ev) => {
        ev.stopPropagation();
        const select = picker.querySelector(".sp-select");
        const key = this._pickerKey;
        const slot = this._pickerSlot;
        // What Assign will write is the choice the card remembered, not
        // whatever the `<select>` reports. That element is rebuilt on every
        // keystroke of the filter, and reading an answer back out of a
        // control that has just been replaced is the same class of mistake
        // as the one this whole item is about: a slot with a perfectly good
        // sensor in it must never be emptied by the UI's own bookkeeping.
        // `null` means "the user did not choose anything this visit", which
        // is a request to keep what the slot already has.
        const chose = this._pickerChoice;
        const picked = chose === null || chose === undefined ? null : chose;
        const fromDom =
          select && typeof select.value === "string" && select.value
            ? select.value
            : null;
        // An empty `<select>` that the user never touched is the control's
        // own default, not a decision -- and acting on it is precisely the
        // reported bug -- so it degrades to what the slot already holds.
        // Choosing "(not configured)" deliberately still clears, through
        // the confirmation below.
        const entityId =
          picked !== null ? picked
            : fromDom !== null ? fromDom
              : (slot && slot.entity) || "";
        const note = this.shadowRoot.querySelector(".setup-result");
        // Assigning nothing to a slot that HAS something is a deletion: it
        // writes the config entry and reloads the integration, and the user
        // usually got here believing they were fixing a slot rather than
        // emptying one. Same pattern as the what-if save -- the button
        // itself becomes the confirmation, since a nested browser prompt
        // inside this modal is easy to miss behind the backdrop.
        if (!entityId && slot && slot.entity && !this._pendingClear) {
          this._pendingClear = true;
          save.textContent = L("setup.confirm_clear");
          save.classList.add("confirm");
          this._setupNote = L("setup.confirm_clear_hint", {
            entity: slot.entity,
            label: slot.label,
          });
          if (note) note.textContent = this._setupNote;
          const foot = picker.querySelector(".sp-note");
          if (foot) foot.textContent = this._setupNote;
          // Let the decision lapse rather than sit armed: a stray second
          // click minutes later must not empty a slot.
          clearTimeout(this._clearTimer);
          this._clearTimer = setTimeout(() => this._disarmClear(picker), 8000);
          return;
        }
        this._cancelPendingClear();
        try {
          await this._hass.callService(
            "heatpump_optimizer",
            "assign_entity",
            { key, entity_id: entityId }
          );
          this._closePicker();
          // The write reloads the integration, so the topology the card is
          // drawn from is replaced a moment later. Say what happened rather
          // than leaving a diagram that has not caught up yet looking wrong.
          this._setupNote = entityId
            ? L("setup.assigned_reloading", { entity: entityId })
            : L("setup.cleared_reloading");
        } catch (err) {
          this._setupNote = L("errors.could_not_assign", {
            err: (err && err.message) || err,
          });
        }
        this._render();
        if (note) note.textContent = this._setupNote || "";
        // Success closed the picker (and the render destroyed the control
        // that had focus): return focus to the row that was assigned. A
        // failure keeps the picker open, and focus with it.
        if (this._pickerKey === null) this._restoreSetupFocus(key);
      };
      save.addEventListener("click", assign);
      // Enter on the select assigns the chosen entity — the picker's one
      // "submit" action, without a Tab trip to the button.
      if (select) {
        select.addEventListener("keydown", (ev) => {
          if (ev.key !== "Enter") return;
          if (ev.preventDefault) ev.preventDefault();
          assign(ev);
        });
      }
    }
  }

  // ---- The layout editor (v3.16.0, issue #40) ----------------------------
  //
  // Free-form graphs are never stored. The editor is a drawing surface whose
  // only output is a catalog KEY: after every change the working edge set is
  // matched against the catalog the coordinator published for THIS
  // configuration, and Save is enabled only when it equals an entry the
  // configuration could actually run. Anything else is drawn as a rejection
  // with the reason on the page, which is the whole point -- a diagram that
  // cannot be wrong about the physics.

  /** Wire the editor's controls and the diagram's pointer gestures.
   *
   * The buttons take listeners directly because `_refreshLayout` never
   * rebuilds them; only the canvas's contents are replaced mid-edit, and its
   * listeners live on the wrapper, which survives.
   */
  _attachLayoutEditor(root) {
    const toggle = root.querySelector(".layout-edit-toggle");
    if (toggle) {
      toggle.addEventListener("click", (ev) => {
        stop(ev);
        this._toggleLayoutEdit();
      });
    }
    const save = root.querySelector(".layout-save");
    if (save) {
      // Returns the promise so a caller (and the tests) can await the call.
      save.addEventListener("click", (ev) => {
        stop(ev);
        return this._saveLayout();
      });
    }
    const undo = root.querySelector(".layout-undo");
    if (undo) {
      // A plain <button>, so the browser already turns Enter and Space into
      // this same click; nothing keyboard-specific is needed here.
      undo.addEventListener("click", (ev) => {
        stop(ev);
        this._undoLayout();
      });
    }
    const canvas = root.querySelector(".setup-canvas");
    if (!canvas) return;
    canvas.addEventListener("pointerdown", this._onLayoutDown);
    canvas.addEventListener("pointermove", this._onLayoutMove);
    canvas.addEventListener("pointerup", this._onLayoutUp);
    canvas.addEventListener("pointerleave", this._onLayoutUp);
    canvas.addEventListener("click", this._onLayoutClick);
  }

  /** Open the editor on the published layout, or close it, discarding. */
  _toggleLayoutEdit() {
    if (this._layoutEditing()) {
      // Cancel discards. Nothing was written, so keeping the working set on
      // screen would show a system that does not exist.
      this._layoutEdit = null;
    } else {
      const topo = this._planAttrRaw("setup_topology", null) || {};
      const positions =
        topo.positions && typeof topo.positions === "object"
          ? topo.positions
          : {};
      // One reading of the published layout, copied out twice: the working
      // set the user draws on, and the baseline Undo goes back to. Both are
      // deep copies down to the individual edge and position pairs, so no
      // edit can reach through a shared array into the other copy.
      const snapshot = () => ({
        edges: (Array.isArray(topo.edges) ? topo.edges : []).map((e) => [
          e[0],
          e[1],
        ]),
        positions: this._copyPositions(positions),
      });
      const working = snapshot();
      this._layoutEdit = {
        active: true,
        edges: working.edges,
        positions: working.positions,
        // The layout Undo restores: the one in force when the editor opened,
        // taken now rather than re-read from `setup_topology` at undo time.
        // The integration republishes the topology on its own schedule, so a
        // late read could hand back a different layout than the one the user
        // started from -- and "back to where I was" is the whole promise of
        // the button. A snapshot cannot be swapped underneath them.
        baseline: snapshot(),
        drag: null,
        match: null,
        invalid: [],
        verdict: "",
        // Nothing has been drawn yet, so there is nothing to save. Without
        // this, Save is lit the moment the editor opens and offers to write
        // the layout the system already has.
        dirty: false,
      };
      this._layoutEvaluate();
    }
    // Editing suppresses click-to-assign, so a picker left open would be
    // unreachable behind the diagram.
    this._closePicker();
    this._render();
  }

  /** Match the working edge set against the catalog, and say what it is.
   *
   * Sets `match` (the entry Save would store, or null), `invalid` (the drawn
   * edges no near layout has, drawn as rejected pipes) and `verdict` (one
   * line for the page). Matching is exact: a nearly-right graph is a graph
   * the model would nearly honour.
   */
  _layoutEvaluate() {
    const ed = this._layoutEdit;
    if (!ed) return;
    const topo = this._planAttrRaw("setup_topology", null) || {};
    const catalog = Array.isArray(topo.catalog) ? topo.catalog : [];
    const name = (e) => `${e[0]}>${e[1]}`;
    const drawn = new Set(ed.edges.map(name));
    const equals = (set) =>
      set.size === drawn.size && [...drawn].every((k) => set.has(k));

    let match = null;
    let sameButUnusable = null;
    let nearest = null;
    let nearestSet = null;
    let nearestDiff = null;
    for (const entry of catalog) {
      const set = new Set((entry.edges || []).map(name));
      if (equals(set)) {
        if (entry.valid) match = match || entry;
        else sameButUnusable = sameButUnusable || entry;
      }
      let diff = 0;
      for (const k of set) if (!drawn.has(k)) diff++;
      for (const k of drawn) if (!set.has(k)) diff++;
      // Ties go to the earlier catalog entry, which is the order the
      // integration lists them in -- stable, so the same drawing always gets
      // the same explanation.
      if (nearestDiff === null || diff < nearestDiff) {
        nearest = entry;
        nearestSet = set;
        nearestDiff = diff;
      }
    }

    if (match) {
      ed.match = match;
      ed.invalid = [];
      ed.verdict = L("setup.verdict_match", { label: match.label });
      return;
    }
    ed.match = null;
    if (sameButUnusable) {
      // The drawing IS a known layout; what fails is the configuration, so
      // the requirement is the only useful thing to say. No pipe is at
      // fault, so none is marked. A catalog from before the field existed
      // ships no requirement, and interpolating undefined here is exactly
      // the "needs: undefined" bug from the user's #40 report — degrade to
      // a sentence that at least says which side is at fault.
      ed.invalid = [];
      const req = sameButUnusable.requirement;
      const label = sameButUnusable.label;
      ed.verdict =
        sameButUnusable.selectable === false
          ? req
            ? L("setup.verdict_req", { label, requirement: req })
            : L("setup.verdict_not_modelled", { label })
          : req
            ? L("setup.verdict_needs", { label, requirement: req })
            : L("setup.verdict_cannot_store", { label });
      return;
    }
    if (!nearest) {
      ed.invalid = [];
      ed.verdict = L("setup.no_catalog");
      return;
    }
    const extra = [...drawn].filter((k) => !nearestSet.has(k));
    const missing = [...nearestSet].filter((k) => !drawn.has(k));
    ed.invalid = extra;
    const parts = [L("setup.verdict_no_match", { label: nearest.label })];
    if (extra.length) {
      parts.push(
        L("setup.verdict_extra_edges", {
          edges: extra.map(edgeLabel).join("; "),
        })
      );
    }
    if (missing.length) {
      parts.push(
        L("setup.verdict_missing_edges", {
          edges: missing.map(edgeLabel).join("; "),
        })
      );
    }
    ed.verdict = parts.join(" ");
  }

  /** Redraw only what an edit changes.
   *
   * A full `_render` per pointer move would rebuild the shadow root dozens of
   * times a second and take the drag's own listeners with it -- the same
   * reason the plan lanes refresh in place.
   */
  _refreshLayout() {
    const root = this.shadowRoot;
    if (!root) return;
    const topo = this._planAttrRaw("setup_topology", null);
    const canvas = root.querySelector(".setup-canvas");
    if (canvas && topo && Array.isArray(topo.slots)) {
      canvas.innerHTML = this._setupSvg(topo);
    }
    const ed = this._layoutEdit;
    const verdict = root.querySelector(".layout-verdict");
    if (verdict) {
      verdict.textContent = (ed && ed.verdict) || "";
      if (verdict.classList) {
        verdict.classList.toggle("match", !!(ed && ed.match));
      }
    }
    const save = root.querySelector(".layout-save");
    if (save) save.disabled = !this._layoutSaveable();
    const undo = root.querySelector(".layout-undo");
    if (undo) undo.disabled = !this._layoutUndoable();
  }

  /** Pointer client coordinates as viewBox units on the setup diagram. */
  _layoutPoint(ev) {
    const root = this.shadowRoot;
    const svg = root && root.querySelector(".setup-svg");
    if (!svg || !svg.getBoundingClientRect || !ev) return null;
    const rect = svg.getBoundingClientRect();
    if (!rect || !rect.width) return null;
    // The diagram keeps its aspect ratio (`width: 100%; height: auto`), so a
    // single scale relates both axes; measuring y against the measured height
    // would skew every drop test further down the page.
    const scale = SETUP_W / rect.width;
    return {
      x: (ev.clientX - rect.left) * scale,
      y: (ev.clientY - rect.top) * scale,
    };
  }

  /** The box under a point, in viewBox units, or null. */
  _layoutBoxAt(x, y) {
    const boxes = this._layoutBoxes || [];
    for (let i = boxes.length - 1; i >= 0; i--) {
      const b = boxes[i];
      if (x >= b.x && x <= b.x + b.w && y >= b.y && y <= b.y + b.h) return b;
    }
    return null;
  }

  _onLayoutDown(ev) {
    const ed = this._layoutEdit;
    if (!ed || !ed.active) return;
    const pt = this._layoutPoint(ev);
    if (!pt) return;
    // A new gesture cancels any click still owed from the last one. The click
    // after a drag that ended on a slot row is stopped by the row's own
    // handler, so the flag would otherwise survive and eat the next real
    // click -- the one asking for a pipe to be removed.
    ed.suppressClick = false;
    let data = (ev.target && ev.target.dataset) || {};
    if (!data.port && this.shadowRoot.elementFromPoint) {
      // Browser input routing can hit-test a pointerdown against a
      // frame-old layout (observed with synthesized input; touch rides the
      // same compositor path), so a down that claims the bare svg at a
      // port's coordinates would silently become a box drag. Re-test
      // against the live DOM before deciding what the gesture is.
      const live = this.shadowRoot.elementFromPoint(ev.clientX, ev.clientY);
      if (live && live.dataset && live.dataset.port) data = live.dataset;
    }
    if (data.port && data.place) {
      // A connection in the making. It is only a proposal until it lands on
      // another box, so nothing is added here.
      ed.drag = { kind: "edge", from: data.place, x: pt.x, y: pt.y };
    } else {
      const box = this._layoutBoxAt(pt.x, pt.y);
      if (!box) return;
      ed.drag = {
        kind: "box",
        place: box.place,
        dx: pt.x - box.x,
        dy: pt.y - box.y,
      };
    }
    stop(ev);
    if (ev.preventDefault) ev.preventDefault();
  }

  _onLayoutMove(ev) {
    const ed = this._layoutEdit;
    if (!ed || !ed.active || !ed.drag) return;
    const pt = this._layoutPoint(ev);
    if (!pt) return;
    ed.drag.moved = true;
    if (ed.drag.kind === "box") {
      // Cosmetic only: a position never changes an edge, and therefore never
      // changes which layout the drawing matches.
      ed.positions[ed.drag.place] = [
        Math.round(pt.x - ed.drag.dx),
        Math.round(pt.y - ed.drag.dy),
      ];
      ed.dirty = true;
    } else {
      ed.drag.x = pt.x;
      ed.drag.y = pt.y;
    }
    this._refreshLayout();
  }

  _onLayoutUp(ev) {
    const ed = this._layoutEdit;
    if (!ed || !ed.active || !ed.drag) return;
    const drag = ed.drag;
    ed.drag = null;
    if (drag.kind === "edge") {
      const pt = this._layoutPoint(ev) || { x: drag.x, y: drag.y };
      const box = this._layoutBoxAt(pt.x, pt.y);
      // A pipe from a box to itself is not a pipe; a release over nothing
      // abandons the proposal, which is how a drag is cancelled.
      if (box && box.place !== drag.from) {
        this._layoutAddEdge(drag.from, box.place);
      }
    }
    // The browser synthesises a click after pointerup, and on the diagram
    // that click would land on whatever the drag ended over -- removing the
    // pipe the user just drew.
    if (drag.moved) ed.suppressClick = true;
    this._layoutEvaluate();
    this._refreshLayout();
  }

  _onLayoutClick(ev) {
    const ed = this._layoutEdit;
    if (!ed || !ed.active) return;
    if (ed.suppressClick) {
      ed.suppressClick = false;
      stop(ev);
      return;
    }
    const data = (ev.target && ev.target.dataset) || {};
    if (!data.edge) return;
    stop(ev);
    this._layoutRemoveEdge(data.edge);
  }

  _layoutAddEdge(from, to) {
    const ed = this._layoutEdit;
    if (!ed) return;
    if (ed.edges.some((e) => e[0] === from && e[1] === to)) return;
    // The same pipe drawn backwards is the same pipe. Keeping both would
    // match no catalog entry and read as a bug in the editor rather than a
    // second connection.
    ed.edges = ed.edges.filter((e) => !(e[0] === to && e[1] === from));
    ed.edges.push([from, to]);
    ed.dirty = true;
  }

  _layoutRemoveEdge(name) {
    const ed = this._layoutEdit;
    if (!ed) return;
    const before = ed.edges.length;
    ed.edges = ed.edges.filter((e) => `${e[0]}>${e[1]}` !== name);
    if (ed.edges.length !== before) ed.dirty = true;
    this._layoutEvaluate();
    this._refreshLayout();
  }

  /** Take the drawing back to the layout the editor opened on.
   *
   * The way out of a half-finished rearrangement that is not worth saving.
   * Cancel already discards, but it also closes the editor, so starting
   * over meant reopening it; this restores the same starting point and
   * leaves the user where they are, still editing.
   *
   * Restoring is a revert to the baseline, not a step backwards through a
   * history: what was asked for is the layout in force, and one button that
   * always lands there is worth more here than a stack that has to be
   * unwound to reach it.
   */
  _undoLayout() {
    const ed = this._layoutEdit;
    if (!this._layoutUndoable()) return;
    // Copied out of the baseline rather than handed over: a later drag
    // writes into these, and the baseline has to survive to serve a second
    // Undo.
    ed.edges = ed.baseline.edges.map((e) => [e[0], e[1]]);
    ed.positions = this._copyPositions(ed.baseline.positions);
    // A gesture still in flight belongs to the drawing that just went away:
    // its pointerup would land an edge nobody asked for, or drop a box at a
    // position the restore had already taken back.
    ed.drag = null;
    ed.suppressClick = false;
    ed.dirty = false;
    this._layoutEvaluate();
    // The in-place redraw, not `_render`: a full rebuild would replace the
    // bar and take the focus off the Undo button the keyboard just pressed.
    this._refreshLayout();
  }

  /** Store the matched layout key and the box positions.
   *
   * Only the key travels: the service re-derives the edges from it, so a
   * drawing can never smuggle in physics the model does not implement. A
   * rejection is reported on the page and leaves the editor open, because
   * the drawing is the user's work and losing it is not a way to say no.
   */
  async _saveLayout() {
    const ed = this._layoutEdit;
    if (!this._layoutSaveable()) return;
    if (!this._hass || typeof this._hass.callService !== "function") return;
    const note = this.shadowRoot.querySelector(".setup-result");
    const label = ed.match.label;
    try {
      await this._hass.callService("heatpump_optimizer", "apply_topology", {
        layout: ed.match.key,
        positions: ed.positions,
      });
      // The write reloads the integration, so the topology the card draws
      // from is replaced a moment later; say so rather than leaving a
      // diagram that has not caught up looking wrong.
      this._setupNote = L("setup.saved_reloading", { label });
      this._layoutEdit = null;
    } catch (err) {
      this._setupNote = L("errors.could_not_save_layout", {
        err: (err && err.message) || err,
      });
    }
    this._render();
    if (note) note.textContent = this._setupNote || "";
  }

  /** One live reading, formatted, or null for an empty slot. */
  _slotLive(slot) {
    if (!slot.entity) return null;
    const st = this._hass && this._hass.states
      ? this._hass.states[slot.entity]
      : null;
    if (!st || st.state === "unavailable" || st.state === "unknown") {
      return L("setup.unavailable");
    }
    // HA's own formatter applies the user's unit system and any per-entity
    // display override, so a natively-°F probe reads in °C on a metric
    // install here exactly as it does everywhere else in the frontend.
    // Raw state + unit stays as the fallback for older frontends.
    if (this._hass && typeof this._hass.formatEntityState === "function") {
      try {
        const formatted = this._hass.formatEntityState(st);
        if (formatted) return formatted;
      } catch (e) {
        // fall through to the raw concatenation
      }
    }
    const unit =
      (st.attributes && st.attributes.unit_of_measurement) || "";
    return `${st.state}${unit ? " " + unit : ""}`;
  }

  /** The irradiance the plan actually runs on when no sensor is configured.
   *
   * The Outside box used to say "not configured" while the plan solved
   * against Open-Meteo or weather-derived irradiance every cycle — a value
   * in active use displayed as absent. The solar plan sensor carries both
   * the number and its source, so show them, tagged so nobody mistakes a
   * forecast for a roof sensor.
   */
  _solarFallback() {
    const st = this._stateOf(this._resolveEntity("solar"));
    if (!st) return null;
    const v = Number(st.state);
    if (!Number.isFinite(v)) return null;
    const source = (st.attributes || {}).source;
    if (!source) return null;
    const label =
      source === "open_meteo" ? "Open-Meteo" : L("setup.source_weather");
    return `${Math.round(v)} W/m² · ${label}`;
  }

  _setupSvg(topo) {
    const W = SETUP_W;
    // Whether the model runs the wood tank as its own store (issue #40).
    // Published by `describe_setup`; absent on older descriptions, where
    // false is the right answer because that is the model they ran.
    const twoTank = !!topo.two_tank_modelled;
    // The wood valve stopped being a box in v4.0.0 (#40 feedback, item 3):
    // its one slot lives on the 4-way valve or the wood tank now. An old
    // coordinator can still publish the slot at the removed place, so the
    // same re-homing is applied here rather than letting the slot vanish.
    const normPlace = (p) =>
      p === "wood_valve" ? (twoTank ? "mixing_valve" : "wood_tank") : p;
    const slotsAt = (place) =>
      topo.slots.filter((s) => normPlace(s.place) === place);
    const boxes = [];
    // SVG text does not wrap, and a caption longer than the box runs
    // straight past its border — measured in a real browser, the no-valve
    // caption overflowed by 19 viewBox units. Captions are therefore
    // wrapped here, before layout, where the box height still follows the
    // line count. The rule is the measured width of the row's text area
    // (v5.1.4 -- it was a 34-character count, which cannot tell "iiii"
    // from "WWWW" and had to be re-guessed every time the padding moved).
    // A caption is one line of prose and reads badly broken mid-phrase, so
    // it is allowed to lean into the right padding before it wraps: what it
    // must not do is reach the contour. Eight units clear of the wall.
    const captionW = SETUP_COL_W - SETUP_PAD - 8;
    const wrapExtra = (s) => {
      const lines = [];
      let cur = "";
      for (const w of String(s).split(/\s+/)) {
        const next = cur ? `${cur} ${w}` : w;
        if (setupTextW(next, 12, false) > captionW && cur) {
          lines.push(cur);
          cur = w;
        } else cur = next;
      }
      if (cur) lines.push(cur);
      return lines;
    };
    // A box is a titled list of slot rows; its height follows its contents.
    // The first place is the box's identity -- the id edges and saved
    // positions name it by -- and any others are slots that live on the same
    // physical thing (the floor loop's return probe is on the slab).
    const box = (col, title, places, extra) => {
      const rows = [];
      for (const p of places) {
        for (const s of slotsAt(p)) rows.push(s);
      }
      boxes.push({
        col, title, rows, place: places[0],
        extra: (extra || []).flatMap(wrapExtra),
      });
    };

    const valve =
      topo.valve_mode && topo.valve_mode !== "none";
    // The hot water tank refills through a coil in the wood tank (v3.15.1).
    // `describe_setup` only sets this when the coil can actually preheat
    // anything, so the drawing follows the flag rather than re-deriving the
    // conditions and risking a picture the model disagrees with.
    const dhwCoil = !!topo.dhw_wood_coil;
    // With two modelled stores the names have to say which tank is which,
    // and the one valve is the physical 4-way device the wood tank, the
    // heat-pump tank and both floors all meet at.
    const tankTitle = L(twoTank ? "setup.box_hp_tank" : "setup.box_buffer_tank");
    const valveTitle = L(
      twoTank ? "setup.box_4way_valve" : "setup.box_mixing_valve"
    );
    box(0, L("setup.box_outside"), ["outdoor"]);
    box(0, L("setup.box_heat_pump"), ["heat_pump"]);
    if (topo.wood && topo.wood.present) {
      // Honest caption: while wood heat is a single-tank abstraction the
      // drawing must say so rather than let the separate box imply
      // separately modelled physics. Under the two-tank model the box is
      // the physics, so the caption comes off (issue #40).
      box(0, L("setup.box_wood_tank", { v: Math.round(topo.wood.volume_l) }),
        ["wood_tank"],
        twoTank ? [] : [L("setup.wood_caption")]);
    }
    const buf = topo.buffer || {};
    const bufExtra = valve
      ? [buf.is_store
          ? L("setup.buffer_stores", { t: Math.round(buf.max_temp) })
          : L("setup.buffer_too_small")]
      : [L("setup.no_valve_caption")];
    if (valve) {
      box(1, `${valveTitle} (${esc(String(topo.valve_mode))})`,
        ["mixing_valve"]);
    }
    box(1, `${tankTitle} (${Math.round(buf.volume_l || 0)} L)`,
      ["buffer_tank"], bufExtra);
    if (topo.dhw) box(1, L("setup.box_dhw_tank"), ["dhw_tank"],
      dhwCoil ? [L("setup.dhw_coil_caption")] : []);
    box(2, L(topo.two_zone ? "setup.box_upper_floor" : "setup.box_house"),
      ["upper_zone"]);
    if (topo.two_zone) {
      box(2, L("setup.box_lower_floor"), ["lower_zone", "floor_loop"]);
    }

    // Lay the columns out top to bottom, then draw. All sizes in viewBox
    // units; the SVG scales to the dialog like the chart does.
    const colX = [16, 260, 504];
    const colW = SETUP_COL_W;
    const rowH = 17;
    const pad = 8;
    const colY = [16, 16, 16];
    for (const b of boxes) {
      b.x = colX[b.col];
      b.y = colY[b.col];
      b.h = 24 + (b.rows.length + b.extra.length) * rowH + pad;
      colY[b.col] = b.y + b.h + 14;
    }
    let H = Math.max(...colY) + 4;

    // Cosmetic positions (v3.16.0): the column layout above still runs, so a
    // position for one box leaves every other box where it was, and a place
    // that no longer has a box is simply ignored rather than erroring. The
    // editor's own working positions win over the stored ones while it is
    // open, which is what makes a drag visible.
    const editing = this._layoutEditing();
    const stored =
      topo.positions && typeof topo.positions === "object" ? topo.positions : {};
    const placed = editing
      ? { ...stored, ...(this._layoutEdit.positions || {}) }
      : stored;
    for (const b of boxes) {
      const at = placed[b.place];
      if (!Array.isArray(at) || at.length < 2) continue;
      const x = Number(at[0]);
      const y = Number(at[1]);
      if (!Number.isFinite(x) || !Number.isFinite(y)) continue;
      // Clamped to the drawing: a box parked outside the viewBox is a box
      // nobody can drag back.
      b.x = Math.max(0, Math.min(W - colW, x));
      b.y = Math.max(0, Math.min(SETUP_MAX_Y, y));
      H = Math.max(H, b.y + b.h + 4);
    }
    // Where the boxes ended up, for the editor's drop tests.
    this._layoutBoxes = boxes.map((b) => ({
      place: b.place, x: b.x, y: b.y, w: colW, h: b.h,
    }));

    const parts = [];
    // Connections first, under the boxes: pump and furnace feed the buffer
    // column, which feeds the house column.
    const anchor = (b) => ({ x: b.x + colW, y: b.y + b.h / 2 });
    const to = (b) => ({ x: b.x, y: b.y + b.h / 2 });
    // Boxes are found by their place id, never by their (localized) title:
    // matching on display text is exactly what would silently drop pipes the
    // moment a title is translated.
    const findPlace = (p) => boxes.find((b) => b.place === p);
    // Boxes in the same column stack vertically, so their connection is a
    // short vertical pipe; a right-to-left curve between them crosses every
    // box in between and reads as spaghetti. `edge` names the connection so
    // tests can assert the drawn topology instead of path coordinates.
    // Same-column is asked as "same x" so a box the user has dragged still
    // gets the pipe its new position deserves; with nothing dragged the two
    // questions have identical answers, because a column is one x.
    // The silhouette each box wears (unknown places fall back to the plain
    // cabinet), consulted for how far a pipe endpoint pulls inside the
    // bounding box so pipes meet ink rather than the invisible rect.
    const KIND = (b) => NODE_SHAPES[PLACE_KIND[b.place]] || NODE_SHAPES.hp;
    // One pipe departs somewhere other than a wall midpoint: the DHW
    // pre-heating coil hangs on the wood tank's upper-right wall, and its
    // pipe must leave from the coil's bulge -- in every branch, including
    // the same-column one a drag can create -- or the helix reads as
    // ornament next to a pipe that ignores it. Keyed by place pair so the
    // published edge and the legacy `wood-dhw` name both hit it.
    // The pipe leaves from the midpoint of the helix's stub pair, which is
    // height-dependent: a row-less wood tank (h < 49) wears the single-loop
    // coil (stubs y+13/y+20), a taller one the two-loop coil (y+16/y+30).
    const ANCHOR_OVERRIDES = {
      "wood_tank>dhw_tank": {
        from: (bb) => ({
          x: bb.x + colW + 13,
          y: bb.y + (bb.h < 49 ? 16.5 : 23),
        }),
      },
    };
    // Endpoint dots weld pipe to silhouette, and one midpoint chevron says
    // which way the water flows (skipped on rejected pipes -- an arrow on a
    // connection that cannot exist would endorse it). None of these carry
    // `data-edge`: the tests scrape it to read the drawn topology, and must
    // keep seeing exactly one occurrence per pipe.
    const pipeDeco = (fx, fy, tx, ty, vertical, s, invalid) => {
      const dots =
        `<circle class="setup-pipe-dot" cx="${fx}" cy="${fy}" r="2" />` +
        `<circle class="setup-pipe-dot" cx="${tx}" cy="${ty}" r="2" />`;
      if (invalid) return dots;
      // The chevron sits at the pipe's midpoint and must lie ALONG it.
      // Both branches used to draw an axis-aligned glyph -- horizontal for
      // every cross-column pipe, vertical for every stacked one -- so on
      // the many pipes whose ends differ in height the arrow crossed the
      // pipe at right angles instead of pointing down it.
      //
      // A cross-column pipe is the cubic `M f C f+40 fy, tx-40 ty, t`, and
      // for it both the midpoint and the direction are exact:
      //   B(0.5)  = (P0 + 3P1 + 3P2 + P3) / 8 = ((fx+tx)/2, (fy+ty)/2)
      //             -- the control handles cancel, so the midpoint is the
      //             chord's midpoint, which is where the glyph already was.
      //   B'(0.5) = 3[(P1-P0)/4 + (P2-P1)/2 + (P3-P2)/4]
      //           ∝ (dx/2 - 20, dy/2)
      //             -- horizontal only when dy is 0. The -20 is the two
      //             40-unit handles pulling back against the run.
      // A stacked pipe is a straight segment, so its direction is simply
      // the flow: `s` is +1 when the box the water leaves is the upper one.
      const mx = (fx + tx) / 2;
      const my = (fy + ty) / 2;
      let ux = 0;
      let uy = s;
      if (!vertical) {
        const vx = (tx - fx) / 2 - 20;
        const vy = (ty - fy) / 2;
        const len = Math.hypot(vx, vy);
        // A tangent of zero length has no direction to draw along; fall
        // back to the caller's left/right hint rather than dividing by 0.
        if (len < 1e-6) {
          ux = s;
          uy = 0;
        } else {
          ux = vx / len;
          uy = vy / len;
        }
      }
      // Apex 2 units ahead of the midpoint, tails 3 behind and 3 to each
      // side: the same glyph as before, now in the pipe's own frame.
      const nx = -uy;
      const ny = ux;
      const r = (n) => Math.round(n * 1000) / 1000;
      const flow =
        `M ${r(mx - 3 * ux + 3 * nx)} ${r(my - 3 * uy + 3 * ny)} ` +
        `L ${r(mx + 2 * ux)} ${r(my + 2 * uy)} ` +
        `L ${r(mx - 3 * ux - 3 * nx)} ${r(my - 3 * uy - 3 * ny)}`;
      return `${dots}<path class="setup-flow" d="${flow}" />`;
    };
    const line = (a, b, edge, cls) => {
      if (!a || !b) return "";
      const extra = cls || "";
      const invalid = extra === " invalid";
      const over = ANCHOR_OVERRIDES[`${a.place}>${b.place}`];
      if (!over && a.x === b.x) {
        const upper = a.y < b.y ? a : b;
        const lower = a.y < b.y ? b : a;
        const x = a.x + 24;
        const yTop = upper.y + upper.h - KIND(upper).inset.b;
        const yBot = lower.y + KIND(lower).inset.t;
        // The valve's bowtie accent straddles its bottom edge at this same
        // abscissa, and the chevron's apex would land close enough to merge
        // ink with it -- so the pipe into the valve keeps its dots but
        // drops the chevron (pipeDeco's `invalid` path is exactly that).
        const noFlow = invalid || b.place === "mixing_valve";
        return `<path class="setup-pipe${extra}" data-edge="${edge}"
          d="M ${x} ${yTop}
          L ${x} ${yBot}" />` +
          pipeDeco(x, yTop, x, yBot, true, a === upper ? 1 : -1, noFlow);
      }
      const f = over
        ? over.from(a)
        : { x: anchor(a).x - KIND(a).inset.r, y: anchor(a).y };
      const t = { x: to(b).x + KIND(b).inset.l, y: to(b).y };
      return `<path class="setup-pipe${extra}" data-edge="${edge}"
        d="M ${f.x} ${f.y}
        C ${f.x + 40} ${f.y},
          ${t.x - 40} ${t.y}, ${t.x} ${t.y}" />` +
        pipeDeco(f.x, f.y, t.x, t.y, false, t.x > f.x ? 1 : -1, invalid);
    };
    const bufferBox = findPlace("buffer_tank");
    const houseBox = findPlace("upper_zone");
    // One shared flow serves every circuit: whatever regulates the supply —
    // the mixing valve when one exists, the raw tank when not — feeds BOTH
    // floors in parallel. Drawing the lower floor from the tank while a
    // valve throttled the upper one contradicted the model, which computes
    // one t_mix and delivers both circuits from it (issue #40).
    const supplyBox = valve ? findPlace("mixing_valve") : bufferBox;
    const supplyName = valve ? "valve" : "buffer";

    // The place each edge endpoint is drawn at. Two places fold: the
    // two-tank layout has no separate wood valve (its outlet probe is a slot
    // on the one 4-way device), and the lower floor's box carries the floor
    // loop. A place with no box drops its pipes rather than drawing them
    // into empty space -- `slab_shunt` has no box on any modelled layout.
    const byPlace = new Map();
    for (const b of boxes) if (b.place) byPlace.set(b.place, b);
    // An old coordinator's edge list can still name the removed wood-valve
    // place; anchor those pipes where the slot went, so a stale payload
    // degrades to the new drawing instead of dropping its wood chain.
    if (!byPlace.has("wood_valve")) {
      const home = byPlace.get(twoTank ? "mixing_valve" : "wood_tank");
      if (home) byPlace.set("wood_valve", home);
    }

    // v3.16.0: the pipes are the coordinator's edge list, drawn as published.
    // Hardcoding them here is what let the drawing and the physics drift
    // apart in the first place. `topo.edges` is absent on a coordinator from
    // before this release, and that fallback is the old drawing exactly.
    const drawnEdges = editing
      ? this._layoutEdit.edges
      : Array.isArray(topo.edges)
        ? topo.edges
        : null;
    // The coil helix (drawn on the wood tank below) follows the drawing, not
    // the flag: while the editor is open the wood>DHW pipe is what claims a
    // coil, so the helix must appear and vanish with it live. Without an
    // edge list the flag is all there is, exactly like the legacy pipe
    // branch below.
    const coilDrawn = drawnEdges
      ? drawnEdges.some((e) => e[0] === "wood_tank" && e[1] === "dhw_tank")
      : dhwCoil && !!findPlace("dhw_tank");
    if (drawnEdges) {
      const rejected = new Set(
        editing && Array.isArray(this._layoutEdit.invalid)
          ? this._layoutEdit.invalid
          : []
      );
      const matched = editing && this._layoutEdit.match ? " layout-match" : "";
      for (const e of drawnEdges) {
        const edge = `${e[0]}>${e[1]}`;
        parts.push(line(byPlace.get(e[0]), byPlace.get(e[1]), edge,
          rejected.has(edge) ? " invalid" : matched));
      }
      // The connection being dragged, from its box to the pointer.
      const drag = editing ? this._layoutEdit.drag : null;
      if (drag && drag.kind === "edge" && byPlace.has(drag.from)) {
        const src = byPlace.get(drag.from);
        parts.push(`<path class="layout-ghost"
          d="M ${src.x + colW / 2} ${src.y + src.h / 2}
          L ${drag.x} ${drag.y}" />`);
      }
    } else {
      parts.push(line(findPlace("heat_pump"), bufferBox, "hp-buffer"));
      if (twoTank) {
        // Both stores feed the same 4-way valve; there is no wood-side valve
        // and no path that pours the wood tank into the heat-pump tank.
        parts.push(line(findPlace("wood_tank"), supplyBox, "wood-valve"));
      } else {
        // Tank to tank: the wood-side blending valve stopped being a box of
        // its own in v4.0.0 (#40 feedback, item 3).
        parts.push(line(findPlace("wood_tank"), bufferBox, "wood-buffer"));
      }
      // A second, separate path out of the wood tank: mains water on its way
      // into the hot water tank, not heating water on its way to the house.
      // No other edge stands for it, so without this pipe the diagram shows a
      // hot water tank that the wood tank cannot reach.
      if (dhwCoil) {
        parts.push(line(findPlace("wood_tank"), findPlace("dhw_tank"),
          "wood-dhw"));
      }
      parts.push(line(supplyBox, houseBox, `${supplyName}-upper`));
      if (valve) parts.push(line(bufferBox, supplyBox, "buffer-valve"));
      if (topo.two_zone) parts.push(line(supplyBox, findPlace("lower_zone"),
        `${supplyName}-lower`));
      // Electric hot water: the pump heats the DHW tank on every layout
      // (#40 feedback, item 2) — stale payloads deserve the pipe too.
      if (topo.dhw) {
        parts.push(line(findPlace("heat_pump"), findPlace("dhw_tank"),
          "hp-dhw"));
      }
    }

    for (const b of boxes) {
      const rows = [];
      let y = b.y + 20 + rowH;
      for (const s of b.rows) {
        const live = this._slotLive(s);
        let cls = s.entity ? "setup-slot" : "setup-slot empty";
        let value = live === null ? L("setup.not_configured") : live;
        // A value the plan actively uses must never read as absent: with no
        // radiation sensor the irradiance still comes from Open-Meteo or
        // the weather forecast, and the box says which.
        if (live === null && s.key === "solar_radiation_entity") {
          const fallback = this._solarFallback();
          if (fallback) {
            value = fallback;
            cls = "setup-slot";
          }
        }
        // Spellings of this value from longest to shortest, for the row to
        // choose between. Anything tagged with its provenance after a
        // middot ("123 W/m² · Open-Meteo") can fall back to the reading on
        // its own; the tag then rides in the row's tooltip, where it is
        // still one hover away, instead of overwriting the label.
        const valueAlts = value.includes(" · ")
          ? [value, value.split(" · ")[0]]
          : [value];
        // The label and the right-anchored value share one 200-unit row;
        // SVG text does not wrap, so whatever does not fit collides. Both
        // strings are MEASURED (`fitSlotRow`) and the value is given its
        // room first: the label is ellipsized into what is left, and only a
        // value that would squeeze the label below readability is itself
        // shortened -- never by cutting the reading, only by dropping the
        // provenance tag after the middot. The old rule counted characters
        // and let "123 W/m² · Open-Meteo" run through the label beside it.
        //
        // A row whose text was shortened says the whole thing in its
        // tooltip and its accessible name, so nothing is only visible to
        // someone with a wide screen.
        const fit = fitSlotRow(s.label, valueAlts, colW - 2 * SETUP_PAD, 12);
        // The tooltip and the accessible name always carry the whole label
        // (they are built from it), and additionally the whole value when
        // the row had to shorten it.
        const title = L("setup.click_to_assign_title", { label: s.label });
        const full = fit.shortened ? `${title} — ${fit.full}` : title;
        rows.push(`<text class="${cls}" x="${b.x + SETUP_PAD}" y="${y}">
          <tspan>${esc(fit.label)}</tspan>
          <tspan class="setup-value" x="${b.x + colW - SETUP_PAD}"
            text-anchor="end">${esc(fit.value)}</tspan></text>`);
        // A transparent rect over the row, not a handler on the text: text
        // is a thin target, and the gap between label and value would not
        // respond at all -- which reads as a diagram that is only sometimes
        // clickable.
        rows.push(`<rect class="setup-hit" data-key="${esc(s.key)}"
          tabindex="0" role="button" aria-label="${esc(full)}"
          x="${b.x + 4}" y="${y - rowH + 5}" width="${colW - 8}"
          height="${rowH - 2}" rx="3">
          <title>${esc(full)}</title></rect>`);
        y += rowH;
      }
      for (const ex of b.extra) {
        rows.push(`<text class="setup-slot extra" x="${b.x + SETUP_PAD}"
          y="${y}">${esc(ex)}</text>`);
        y += rowH;
      }
      // One port per edge midpoint, drawn only while editing: they are drag
      // handles for connections, and a diagram nobody is editing should not
      // sprout handles that do nothing.
      // Each port is two circles: the visible 5-unit dot, and a much larger
      // invisible twin that actually takes the pointer. Measured in a real
      // browser, the dot alone renders around two CSS pixels — a drag aimed
      // at its exact center landed on the box instead, and no fingertip
      // would ever fare better. The twin is painted after the dot so hit
      // testing prefers it, and carries the same data attributes so the
      // handler cannot tell them apart.
      const ports = editing
        ? [
            [b.x + colW / 2, b.y, "top"],
            [b.x + colW / 2, b.y + b.h, "bottom"],
            [b.x, b.y + b.h / 2, "left"],
            [b.x + colW, b.y + b.h / 2, "right"],
          ]
          .map(([px, py, side]) =>
            `<circle class="layout-port" data-place="${esc(b.place || "")}"
              data-port="${side}" cx="${px}" cy="${py}" r="5" />
            <circle class="layout-port-hit" data-place="${esc(b.place || "")}"
              data-port="${side}" cx="${px}" cy="${py}" r="16" />`)
          .join("")
        : "";
      // The place id rides on the box only while editing: outside the editor
      // nothing reads it, and a drawing that is byte-identical to the one
      // before this feature is the cheapest possible proof it changed nothing.
      const at = editing ? ` data-place="${esc(b.place || "")}"` : "";
      // The visible silhouette, painted right after the invisible carrier
      // rect. Everything here is inert (`pointer-events: none`), so the hit
      // rects, pipe clicks and drags behave exactly as before; the per-kind
      // class rides on the contour path because the `<g>` must stay bare --
      // three tests split the page on the literal "<g>".
      const kindKey = PLACE_KIND[b.place];
      const shape = NODE_SHAPES[kindKey] || NODE_SHAPES.hp;
      const deco = [
        `<path class="setup-contour kind-${esc(b.place || "")}"
          d="${shape.contour(b.x, b.y, colW, b.h)}" />`,
      ];
      // An unknown place keeps the plain cabinet outline but none of the
      // hp accents -- a fan on a box nobody named would be a claim.
      if (kindKey) {
        for (const acc of shape.accents(b.x, b.y, colW, b.h)) {
          // The divider returns null for a row-less box; skip it.
          if (!acc) continue;
          deco.push(
            acc.d
              ? `<path class="${acc.cls || "setup-accent"}" d="${acc.d}" />`
              : `<circle class="${acc.cls || "setup-accent"}" cx="${acc.cx}"
                  cy="${acc.cy}" r="${acc.r}" />`
          );
        }
      }
      // The DHW pre-heating helix on the wood tank's upper-right wall: two
      // overlapping loops whose stubs pierce the straight wall below the
      // dome. Part of the tank's own markup so it moves with the box during
      // drags and survives `_refreshLayout`'s innerHTML rebuild.
      if (b.place === "wood_tank" && coilDrawn) {
        // A row-less tank (h = 32, two-tank mode with the caption re-homed)
        // only has straight wall from y+9 to y+23, so the two-loop coil's
        // lower stub at y+30 would pierce empty air below the dome. It gets
        // one loop, stubs at y+13 and y+20; anything taller keeps the
        // two-loop helix, byte for byte. ANCHOR_OVERRIDES above computes
        // the pipe's departure from the same stub pair.
        deco.push(b.h < 49
          ? `<path class="setup-coil"
          d="M ${b.x + colW - 2} ${b.y + 13} H ${b.x + colW + 6}
          A 4.5 4.5 0 1 1 ${b.x + colW + 6} ${b.y + 20}
          H ${b.x + colW - 2}" />`
          : `<path class="setup-coil"
          d="M ${b.x + colW - 2} ${b.y + 16} H ${b.x + colW + 6}
          A 4.5 4.5 0 1 1 ${b.x + colW + 6} ${b.y + 23}
          A 4.5 4.5 0 1 1 ${b.x + colW + 6} ${b.y + 30}
          H ${b.x + colW - 2}" />`);
      }
      parts.push(`
        <g>
          <rect class="setup-box"${at} x="${b.x}" y="${b.y}" width="${colW}"
            height="${b.h}" rx="8" />
          ${deco.join("")}
          <text class="setup-title" x="${b.x + SETUP_PAD}"
            y="${b.y + 17}">${esc(b.title)}</text>
          ${rows.join("")}${ports}
        </g>`);
    }

    // role="group", not "img": the assignment hit targets inside are
    // focusable buttons, and "img" would flatten them out of the
    // accessibility tree.
    return `<svg class="setup-svg${editing ? " editing" : ""}" viewBox="0 0 ${W} ${H}"
      xmlns="http://www.w3.org/2000/svg" role="group"
      aria-label="${esc(L("setup.svg_aria"))}">${parts.join("")}</svg>`;
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
    const windowHours = this._planAttr(
      "manual_plan_window_hours",
      MANUAL_PLAN_WINDOW_FALLBACK_H
    );
    return `
      <div class="whatif">
        <div class="wi-section">
          <div class="wi-group-title">${esc(L("whatif.todays_slots"))}</div>
          <div class="wi-hint">
            ${L("whatif.slots_hint", { hours: windowHours })}
          </div>
          ${
            this._viewLimitsEditing()
              ? `<div class="wi-viewlimit">${L("whatif.zoom_limit_hint", {
                  button:
                    `<button type="button" class="wi-viewreset">` +
                    `${esc(L("whatif.show_whole_plan_button"))}</button>`,
                })}</div>`
              : ""
          }
          ${this._overrideHtml()}
          <div class="wi-row wi-delta">${this._deltaHtml()}</div>
          <div class="wi-row wi-actions">
            <button type="button" class="wi-pin">${esc(
              L("whatif.apply_plan")
            )}</button>
            <button type="button" class="wi-revert">${esc(
              L("whatif.undo_changes")
            )}</button>
            ${
              this._manualOverride()
                ? `<button type="button" class="wi-auto">${esc(
                    L("whatif.back_to_auto")
                  )}</button>`
                : ""
            }
          </div>
          <div class="wi-pin-result" role="status"></div>
        </div>

        <div class="wi-section">
          <div class="wi-group-title">${esc(L("whatif.usual_schedule"))}</div>
          <div class="wi-hint">
            ${L("whatif.schedule_hint")}
          </div>
        <div class="wi-row wi-slots">
          <div class="wi-group">
            <div class="wi-group-title">${esc(L("whatif.heating_hours"))}</div>
            <label class="wi-field">
              <span>${esc(L("whatif.day_from"))}</span>
              <input type="time" class="wi-day-start" step="3600"
                value="${hhmm(draft.dayStart)}" aria-label="${esc(
                  L("whatif.day_start_aria")
                )}">
            </label>
            <label class="wi-field">
              <span>${esc(L("whatif.day_to"))}</span>
              <input type="time" class="wi-day-end" step="3600"
                value="${hhmm(draft.dayEnd)}" aria-label="${esc(
                  L("whatif.day_end_aria")
                )}">
            </label>
            <div class="wi-hint">${L("whatif.setback_hint")}</div>
          </div>

          <div class="wi-group">
            <div class="wi-group-title">${esc(L("whatif.dhw_windows"))}</div>
            <div class="wi-windows">
              ${windows.length
                ? windows
                    .map(
                      (w, i) => `
                <div class="wi-window" data-index="${i}">
                  <input type="time" class="wi-win-start" step="900"
                    value="${esc(w.start)}" aria-label="${esc(
                      L("whatif.window_start_aria", { n: i + 1 })
                    )}">
                  <span>–</span>
                  <input type="time" class="wi-win-end" step="900"
                    value="${esc(w.end)}" aria-label="${esc(
                      L("whatif.window_end_aria", { n: i + 1 })
                    )}">
                  <button type="button" class="wi-remove" data-index="${i}"
                    title="${esc(L("whatif.remove"))}" aria-label="${esc(
                      L("whatif.remove_window_aria", { n: i + 1 })
                    )}">×</button>
                </div>`
                    )
                    .join("")
                : `<div class="wi-hint">${L("whatif.no_windows_hint")}</div>`}
            </div>
            <button type="button" class="wi-add">${esc(
              L("whatif.add_window")
            )}</button>
          </div>
        </div>

        <div class="wi-row wi-actions">
          <button type="button" class="wi-apply">${esc(
            L("whatif.simulate")
          )}</button>
          <button type="button" class="wi-save">${esc(
            L("whatif.save_schedule")
          )}</button>
          <button type="button" class="wi-reset">${esc(
            L("whatif.reset")
          )}</button>
        </div>

        <div class="wi-result" role="status">
          ${L("whatif.idle_status")}
        </div>
        </div>

        <div class="wi-section">
          <div class="wi-group-title">${esc(L("whatif.temperatures"))}</div>
          <div class="wi-hint">
            ${L("whatif.temperatures_hint")}
          </div>
          <div class="wi-row">
            <label class="wi-field">
              <span>${esc(L("whatif.comfort_temp"))}</span>
              <input type="range" class="wi-temp" min="16" max="24" step="0.5"
                value="${draft.comfort}" aria-label="${esc(
                  L("whatif.comfort_temp")
                )}">
              <span class="wi-value wi-comfort-value">${draft.comfort.toFixed(1)}&nbsp;°C</span>
            </label>
          </div>
          <div class="wi-row">
            <label class="wi-field">
              <span>${esc(L("whatif.dhw_min"))}</span>
              <input type="range" class="wi-dhw-min" min="${DHW_MIN_FLOOR}"
                max="${ceiling}" step="0.5" value="${draft.dhwMin}"
                aria-label="${esc(L("whatif.dhw_min_aria"))}">
              <span class="wi-value wi-dhw-value">${draft.dhwMin.toFixed(1)}&nbsp;°C</span>
            </label>
          </div>
          <div class="wi-hint">
            ${
              setpoint === null
                ? L("whatif.cap_no_setpoint", { t: fmtTemp(ceiling) })
                : L("whatif.cap_with_setpoint", {
                    t: fmtTemp(ceiling),
                    band: fmtTemp(setpoint - ceiling),
                    setpoint: fmtTemp(setpoint),
                  })
            }
          </div>
          ${
            clamped
              ? `<div class="wi-hint wi-warn">${L("whatif.clamped_warning", {
                  a: fmtTemp(clamped),
                  b: fmtTemp(draft.dhwMin),
                })}</div>`
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

  /** A plan-sensor attribute as-is, for the ones that are not numbers. */
  _planAttrRaw(name, fallback) {
    const st = this._stateOf(this._resolveEntity("space"));
    const raw = ((st && st.attributes) || {})[name];
    return raw === null || raw === undefined ? fallback : raw;
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
        ? L("slots.until_suffix", { expiry: fmtExpiry(until) })
        : "";
    const released =
      (info.released_space || []).length + (info.released_dhw || []).length;
    const note = released
      ? ` <span class="dearer">${esc(
          L(
            released === 1 ? "slots.released_one" : "slots.released_other",
            { n: released }
          )
        )}</span>`
      : "";
    return `<div class="wi-row wi-override" role="status">${L(
      "slots.pinned_status",
      { until: esc(when) }
    )}${note}</div>`;
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
      this._slotResult(L("slots.no_plan_to_pin"), "dearer");
      return;
    }
    this._slotResult(L("slots.applying"));
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
            ? L("slots.until_suffix", { expiry: fmtExpiry(until) })
            : "";
        // Deliberately not a promise that these slots will run: the optimizer
        // releases a pin that would take the house or the tank below its
        // limits, and saying otherwise would be a lie the user acts on.
        this._slotResult(L("slots.pinned_result", { until: when }), "cheaper");
      })
      .catch((err) => {
        this._slotResult(
          L("errors.could_not_apply", { err: (err && err.message) || err }),
          "dearer"
        );
      });
  }

  _clearManualPlan() {
    if (!this._hass || !this._hass.callService) return;
    this._slotResult(L("slots.clearing"));
    Promise.resolve(
      this._hass.callService("heatpump_optimizer", "clear_manual_plan", {})
    )
      .then(() => {
        this._resetRuns();
        this._slotResult(L("slots.back_to_auto_result"));
        this._render();
      })
      .catch((err) => {
        this._slotResult(
          L("errors.could_not_clear", { err: (err && err.message) || err }),
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
    const viewReset = root.querySelector(".wi-viewreset");
    if (viewReset) viewReset.addEventListener("click", () => this._resetView());
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
      out.textContent = L("errors.not_connected");
      return;
    }

    const draft = this._whatIfDraft();
    const invalid = draft.dhwWindows.find(
      (w) => hourOf(w.start, null) === null || hourOf(w.end, null) === null
    );
    if (invalid) {
      out.className = "wi-result dearer";
      out.textContent = L("errors.invalid_window_time");
      return;
    }
    if (draft.dayStart === draft.dayEnd) {
      out.className = "wi-result dearer";
      out.textContent = L("errors.day_start_equals_end");
      return;
    }

    if (!this._pendingSave) {
      this._pendingSave = true;
      button.textContent = L("whatif.confirm_overwrite");
      button.classList.add("confirm");
      out.className = "wi-result";
      out.textContent = L("whatif.confirm_hint");
      // Let the decision lapse rather than sit armed indefinitely: a stray
      // click minutes later should not rewrite the configuration.
      clearTimeout(this._saveTimer);
      this._saveTimer = setTimeout(() => this._cancelPendingSave(), 8000);
      return;
    }

    this._cancelPendingSave();
    out.className = "wi-result";
    out.textContent = L("whatif.saving");
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
      out.textContent = L("whatif.saved_result");
      // The draft has become the configuration, so drop it: keeping it would
      // leave the editor showing an "unsaved" copy of what is now saved.
      this._whatIf = null;
    } catch (err) {
      out.className = "wi-result dearer";
      out.textContent = L("errors.could_not_save", {
        err: (err && err.message) || err,
      });
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
      button.textContent = L("whatif.save_schedule");
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
      out.textContent = L("errors.invalid_window_time");
      return;
    }

    out.className = "wi-result";
    out.textContent = L("whatif.simulating");
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
          ? L("errors.could_not_simulate", { err: first.error })
          : L("errors.no_answer");
        return;
      }
      out.className = "wi-result";
      out.innerHTML = this._whatIfSummary(first);
    } catch (err) {
      out.className = "wi-result dearer";
      out.textContent = L("errors.could_not_simulate", {
        err: err && err.message ? err.message : err,
      });
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
      return L("errors.no_answer");
    }
    if (Math.abs(delta) < 0.5) {
      parts.push(L("whatif.same_cost"));
    } else {
      const cheaper = delta < 0;
      parts.push(
        L(cheaper ? "whatif.cheaper_per_month" : "whatif.dearer_per_month", {
          amount: Math.abs(delta).toFixed(0),
        })
      );
    }

    const room = Number(result.min_room_temperature);
    const roomBase = Number(result.baseline_min_room_temperature);
    if (Number.isFinite(room)) {
      const drop = Number.isFinite(roomBase) ? room - roomBase : null;
      parts.push(
        L("whatif.min_room_temp", { t: room.toFixed(1) }) +
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
        L("whatif.min_dhw_temp", { t: dhw.toFixed(1) }) +
          (drop !== null && Math.abs(drop) >= 0.1
            ? ` (${drop > 0 ? "+" : ""}${drop.toFixed(1)})`
            : "")
      );
    }

    if (Number.isFinite(Number(result.compressor_starts))) {
      parts.push(
        L(
          Number(result.compressor_starts) === 1
            ? "whatif.compressor_starts_one"
            : "whatif.compressor_starts_other",
          { n: result.compressor_starts }
        )
      );
    }
    if (result.rate_limited) {
      parts.push(L("whatif.rate_limited"));
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

    // Page tabs. Switching re-renders so the hidden page is genuinely gone
    // from the DOM, and the scroll offset is reset because carrying the plan
    // page's position into a differently sized setup page lands nowhere.
    for (const tab of dlg.querySelectorAll(".dlg-tab")) {
      tab.addEventListener("click", (ev) => {
        ev.stopPropagation();
        const page = ev.currentTarget.dataset.page;
        if (page && page !== this._dialogPage) {
          this._dialogPage = page;
          this._dialogScroll = 0;
          // Leaving the setup page abandons a half-made assignment rather
          // than keeping a picker open behind the chart.
          this._closePicker();
          this._render();
        }
      });
    }

    this._attachSetupEvents(dlg);
    const note = dlg.querySelector(".setup-result");
    if (note && this._setupNote) note.textContent = this._setupNote;

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
        /* The SVG's keyboard-reachable parts: slots and lanes. */
        .slot:focus-visible, .lane:focus-visible {
          outline: 2px solid var(--primary-color, #03a9f4); outline-offset: 1px;
        }
        /* The setup rows ring themselves with their own stroke rather than
           an outline. An outline on an SVG rect is painted around the
           element's box in the viewport, where the row's neighbours and the
           diagram's edges cut it: the reporter saw a ring with only its top
           and left sides left. A stroke is part of the drawing, so all four
           sides are visible, and the rect is inset far enough to keep them
           so: it starts 4 units inside the box, which is 2 clear of the
           contour at x+2, and is 2 units shorter than the 17-unit row
           pitch, which leaves 1 unit of air above and below. At
           stroke-width 2, centred on the path, the ring needs exactly 1 of
           those units on each side and touches nothing.
           It is a :focus-visible rule, not :focus, so a mouse click leaves
           no ring behind while a keyboard user keeps one. */
        .setup-hit:focus-visible {
          outline: none;
          fill: var(--primary-color, #03a9f4); fill-opacity: 0.12;
          stroke: var(--primary-color, #03a9f4); stroke-width: 2;
        }
        .headline {
          display: flex; flex-direction: column; gap: 2px;
          padding: 0 4px 8px 4px;
        }
        .hl-stats {
          display: flex; flex-wrap: wrap; gap: 2px 16px; font-size: 0.85em;
        }
        .hl-label { color: var(--secondary-text-color); }
        .hl-value { font-weight: 600; color: var(--primary-text-color); }
        .hl-narrative {
          font-size: 0.82em; font-style: italic;
          color: var(--secondary-text-color);
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
          opacity: 0;${
            /* The fade is the card's only animation, and it is decorative:
               reduced-motion users get an instant show/hide instead. Checked
               here because the style block is rebuilt per render, with the
               media query below as the live fallback between renders. */
            _reducedMotion() ? "" : " transition: opacity 120ms ease-in-out;"
          }
        }
        @media (prefers-reduced-motion: reduce) {
          .viewctl { transition: none; }
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
        svg { width: 100%; height: auto; display: block; }
        /* Only the chart claims raw touch input — a horizontal drag on it is
           a pan, not a scroll. Claiming it on every svg also swallowed touch
           on the setup diagram, where nothing consumes the gesture outside
           the editor: on a phone the diagram fills the dialog, so a finger
           landing on it could not scroll the page at all, which read as a
           setup page that cannot be seen (#40 feedback, item 1). The editor
           re-claims the diagram while a drag must move a box, below. */
        .chartwrap svg { touch-action: none; }
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
        /* The value rows keep the tooltip's nowrap: "House temperature:
           22 °C" broken across two lines is worse than a wider box, and these
           rows are short by construction.

           The prose blocks below must NOT. tt-shared carried a
           max-width of 180px that could never do anything, because it
           inherited white-space: nowrap from .tooltip and never overrode
           it: a ~110-character sentence rendered as one unbroken ~500 px line
           inside a box told to be 180 px wide, and spilled out of it and over
           whatever sat beside the chart. tt-reason is prose too and had no
           width bound at all. Both now wrap, and both carry a width. */
        .tooltip .tt-row { display: flex; align-items: center; gap: 6px; }
        .tooltip .tt-time { font-weight: 600; margin-bottom: 3px; }
        .tooltip .tt-shared {
          margin-top: 3px;
          font-size: 0.85em;
          font-style: italic;
          color: var(--secondary-text-color, #888);
          white-space: normal;
          max-width: 220px;
        }
        .tooltip .tt-reason {
          margin-top: 4px; padding-top: 4px; font-style: italic;
          border-top: 1px solid var(--divider-color, #eee);
          color: var(--secondary-text-color);
          white-space: normal;
          max-width: 220px;
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

        /* Dialog page tabs and the setup page (item 33) */
        .dlg-tabs { display: flex; gap: 0.3em; flex: 0 0 auto; }
        .dlg-tab {
          border: 1px solid var(--divider-color, #e0e0e0);
          background: transparent; color: var(--secondary-text-color);
          border-radius: 1em; padding: 0.2em 0.9em; cursor: pointer;
          font: inherit; font-size: 0.85em;
        }
        .dlg-tab.active {
          color: var(--primary-text-color);
          border-color: var(--primary-color, #03a9f4);
        }
        .dlg-tab:focus-visible {
          outline: 2px solid var(--primary-color, #03a9f4);
          outline-offset: 2px;
        }
        .setup-page { padding: 0.5em 0.25em; }
        .setup-svg { width: 100%; height: auto; display: block; }
        /* The rect stays in the markup as the geometry carrier the tests
           and the drag editor read; the contour paths draw the visible
           outline (v4.3.0). */
        .setup-box { fill: none; stroke: none; }
        .setup-contour {
          fill: none; stroke: var(--primary-text-color, #212121);
          stroke-width: 2; opacity: 0.75;
          stroke-linecap: round; stroke-linejoin: round;
          pointer-events: none;
        }
        .setup-accent {
          fill: none; stroke: var(--secondary-text-color, #757575);
          stroke-width: 1.25; opacity: 0.6;
          stroke-linecap: round; pointer-events: none;
        }
        .setup-accent.divider { opacity: 0.5; }
        .setup-accent.hub {
          stroke: var(--primary-color, #03a9f4); opacity: 0.9;
        }
        .setup-coil {
          fill: none; stroke: var(--primary-color, #03a9f4);
          stroke-width: 2; opacity: 0.85;
          stroke-linecap: round; pointer-events: none;
        }
        .setup-pipe-dot {
          fill: var(--card-background-color, #fff);
          stroke: var(--secondary-text-color, #888);
          stroke-width: 1.5; opacity: 0.8; pointer-events: none;
        }
        .setup-flow {
          fill: none; stroke: var(--secondary-text-color, #888);
          stroke-width: 1.5; opacity: 0.55; pointer-events: none;
        }
        .setup-pipe {
          fill: none; stroke: var(--secondary-text-color, #888);
          stroke-width: 1.5; opacity: 0.55;
        }
        .setup-title {
          font-size: 13px; font-weight: 600;
          fill: var(--primary-text-color, #222);
        }
        .setup-slot { font-size: 12px; fill: var(--primary-text-color, #222); }
        .setup-slot.empty {
          fill: var(--secondary-text-color, #888);
          opacity: 0.75; font-style: italic;
        }
        .setup-slot.extra { fill: var(--secondary-text-color, #888); }
        .setup-value { font-weight: 600; }
        .setup-hint {
          color: var(--secondary-text-color);
          font-size: 0.85em; padding: 0.5em 0.25em;
        }
        .setup-result {
          color: var(--secondary-text-color);
          font-size: 0.85em; padding: 0 0.25em 0.5em 0.25em;
        }
        .setup-hit { fill: transparent; cursor: pointer; }
        /* fill-opacity, not opacity: element opacity would fade the focus
           ring stroked on this same rect down to 12% as soon as the pointer
           crossed a keyboard-focused row -- and :hover and :focus-visible
           have equal specificity, so the later rule would win. Tinting only
           the fill leaves the ring alone. */
        .setup-hit:hover {
          fill: var(--primary-color, #03a9f4); fill-opacity: 0.12;
        }

        /* The layout editor (v3.16.0, issue #40) */
        .layout-bar {
          display: flex; align-items: center; gap: 0.5em;
          flex-wrap: wrap; padding: 0 0.25em 0.4em 0.25em;
        }
        .layout-bar button {
          font: inherit; font-size: 0.85em; cursor: pointer;
          border: 1px solid var(--divider-color, #e0e0e0);
          background: transparent; color: var(--primary-text-color);
          border-radius: 1em; padding: 0.2em 0.9em;
        }
        .layout-bar button:focus-visible {
          outline: 2px solid var(--primary-color, #03a9f4);
          outline-offset: 2px;
        }
        .layout-edit-toggle.on { border-color: var(--primary-color, #03a9f4); }
        .layout-bar button[disabled] { opacity: 0.45; cursor: default; }
        .layout-verdict {
          flex: 1 1 100%; font-size: 0.85em;
          color: var(--secondary-text-color);
        }
        .layout-verdict.match { color: var(--primary-color, #03a9f4); }
        /* Editing widens the pipes: a 1.5-unit stroke is a hopeless click
           target, and clicking a pipe is how one is removed. */
        .setup-svg.editing .setup-pipe { stroke-width: 3.5; cursor: pointer; }
        /* With stroke: none an unfilled rect catches no pointer, so the
           move cursor needs pointer-events back on the surface; hit rects
           painted later still win over their own rows, and drags themselves
           are geometric via _layoutBoxAt either way. */
        .setup-svg.editing .setup-box { cursor: move; pointer-events: all; }
        /* Ornament off while editing: pipes widen into click targets and
           ports appear, and dots or chevrons under the pointer would only
           lie about what is clickable. */
        .setup-svg.editing .setup-pipe-dot,
        .setup-svg.editing .setup-flow { display: none; }
        /* A drag on a touch screen must move the box, not scroll the page. */
        .setup-svg.editing { touch-action: none; }
        .setup-pipe.layout-match {
          stroke: var(--primary-color, #03a9f4); opacity: 0.9;
        }
        .setup-pipe.invalid {
          stroke: var(--error-color, #db4437); opacity: 0.95;
          stroke-dasharray: 6 4;
        }
        .layout-port {
          fill: var(--card-background-color, #fff);
          stroke: var(--primary-color, #03a9f4); stroke-width: 1.5;
          cursor: crosshair;
        }
        .layout-port-hit {
          fill: #fff; fill-opacity: 0.001; stroke: none;
          cursor: crosshair;
        }
        .layout-ghost {
          fill: none; stroke: var(--primary-color, #03a9f4);
          stroke-width: 1.5; stroke-dasharray: 4 3;
        }
        .setup-page { position: relative; }
        .setup-picker {
          position: absolute; left: 50%; top: 1em;
          transform: translateX(-50%); z-index: 6;
          background: var(--card-background-color, #fff);
          border: 1px solid var(--divider-color, #ccc);
          border-radius: 0.5em; padding: 0.7em 0.8em;
          box-shadow: 0 2px 12px rgba(0,0,0,0.25);
          min-width: 16em; max-width: 90%;
        }
        .sp-title { font-weight: 600; padding-bottom: 0.4em; }
        /* The filter and the list it narrows are one control, so they are
           built out of one rule: an input that did not inherit the card's
           colours would be unreadable on a dark theme, which is the sort of
           thing that only shows up on somebody else's screen. */
        .sp-filter, .sp-select {
          width: 100%; font: inherit; padding: 0.3em;
          color: var(--primary-text-color);
          background: var(--card-background-color, #fff);
          border: 1px solid var(--divider-color, #ccc);
          border-radius: 0.3em;
        }
        .sp-filter {
          box-sizing: border-box; margin-bottom: 0.4em;
        }
        .sp-filter:focus-visible, .sp-select:focus-visible {
          outline: 2px solid var(--primary-color, #03a9f4);
          outline-offset: 1px;
        }
        .sp-actions {
          display: flex; gap: 0.4em; padding-top: 0.5em;
        }
        .sp-actions button {
          font: inherit; cursor: pointer; border-radius: 0.3em;
          border: 1px solid var(--divider-color, #ccc);
          background: transparent; color: var(--primary-text-color);
          padding: 0.25em 0.8em;
        }
        .sp-save { border-color: var(--primary-color, #03a9f4) !important; }
        /* An Assign that is armed to CLEAR the slot is not the same button
           any more, and it should not look like it. Same treatment as the
           what-if save's confirmation, which this flow is modelled on. */
        .sp-save.confirm {
          border-color: var(--error-color, #e0544e) !important;
          background: var(--error-color, #e0544e);
          color: var(--text-primary-color, #fff); font-weight: 600;
        }
        .sp-note {
          color: var(--secondary-text-color);
          font-size: 0.8em; padding-top: 0.4em;
        }

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
        .whatif .wi-viewlimit {
          font-size: 12px;
          color: var(--secondary-text-color, #888);
          margin: 4px 0 6px;
        }
        .whatif .wi-viewreset {
          font-size: 12px;
          padding: 1px 8px;
          border: 1px solid var(--divider-color, #e0e0e0);
          border-radius: 10px;
          background: none;
          color: var(--primary-color, #03a9f4);
          cursor: pointer;
        }
        .lane-more { pointer-events: none; font-weight: 700; }
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
          /* Phone-width dialogs (#40 feedback, item 1): the header must be
             allowed to wrap, or the Plan/Setup tabs are pushed out of reach
             by the title; and the setup diagram scrolls sideways at a
             readable, tappable size instead of shrinking every slot row to
             fingernail height. */
          .dlg-head { flex-wrap: wrap; row-gap: 6px; }
          .setup-canvas { overflow-x: auto; -webkit-overflow-scrolling: touch; }
          .setup-canvas svg { min-width: 560px; }
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
      const unit = esc(this._seriesUnit(def));
      const chip = (label, dashed) =>
        `<button type="button" class="${cls}" data-key="${def.key}" title="${esc(
          label
        )} (${unit})">
        <span class="dot" style="${dotStyle(def.color, dashed)}"></span>${esc(
          label
        )}
      </button>`;
      // The extra traces of a multi-line series get chips of their own, named
      // and drawn dashed like the lines they stand for. They carry the same
      // data-key, so clicking any of them toggles the series as a whole —
      // which is the only granularity the visibility model has.
      const extras = (s ? s.lines : [])
        .filter((line) => !line.primary)
        .map((line) => chip(this._lineLabel(def, line), true))
        .join("");
      return chip(L(def.labelKey), false) + extras;
    }).join("");
    return `<div class="legend">${chips}</div>`;
  }

  /** What one trace inside a series is called.
   *
   * A series can carry several lines — the house-temperature series draws the
   * whole-house room average solid and the two zones dashed — and every one of
   * them needs its own name. The lower zone gets a second name when nothing
   * measures it, so a modelled trace is never mistaken for a reading.
   */
  _lineLabel(def, line) {
    if (!line || line.primary) return L(def.labelKey);
    if (line.field === "lower" && this._lowerFloorModelled()) {
      return L("series.lower_floor_modelled");
    }
    return L(line.labelKey || def.labelKey);
  }

  /** True when the lower zone has no thermometer of its own.
   *
   * Read from the published `setup_topology` slots rather than guessed: the
   * integration already says there which sensor slots are filled, so the
   * chart's label and the setup page cannot disagree. Unknown topology
   * claims nothing — a missing attribute is not evidence of a missing
   * sensor.
   */
  _lowerFloorModelled() {
    const topo = this._planAttrRaw("setup_topology", null);
    const slots = topo && Array.isArray(topo.slots) ? topo.slots : null;
    if (!slots) return false;
    const slot = slots.find(
      (x) => x && x.key === "lower_floor_temp_entity"
    );
    return !!slot && !slot.entity;
  }

  /** The unit a series renders with. Only the price unit is dynamic: its
   * currency comes from the config, the plan sensor or Home Assistant. */
  _seriesUnit(def) {
    return def.axis === "price" ? this._priceUnit() : def.unit;
  }

  /** "SEK/kWh", "EUR/kWh", ... from the resolved currency. */
  _priceUnit() {
    return `${this._currency()}/kWh`;
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
    // The price axis title carries the resolved currency, so the measured
    // string and the drawn string must be the same value.
    const priceUnit = this._priceUnit();
    const tempAnchor =
      axes.power && !titleFits("\u00b0C", powerTitleInset) ? "start" : "end";
    const priceAnchor =
      axes.solar && !titleFits(priceUnit, SOLAR_AXIS_INSET) ? "end" : "start";

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
          scaleY, "price", priceUnit, font, priceAnchor
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
        `<text x="${nx + 3}" y="${plotT + font + 1}" font-size="${font}" fill="var(--primary-color,#03a9f4)">${esc(
          L("plan.now")
        )}</text>`
      );
    }

    // Shade the stretch of the horizon whose prices are the learned diurnal
    // prior rather than published market data. A plan that looks identical
    // whether or not it rests on real prices cannot be audited.
    const estimatedFrom = this._estimatedPricesFrom();
    if (estimatedFrom !== null && estimatedFrom < windowEnd) {
      const ex = Math.max(plotL, scaleX(Math.max(estimatedFrom, windowStart)));
      parts.push(
        `<rect class="estimated" pointer-events="none" x="${ex}" y="${plotT}" width="${Math.max(
          0,
          plotR - ex
        )}" height="${plotH}" fill="var(--secondary-text-color,#888)" fill-opacity="0.07"/>`
      );
      parts.push(
        `<text x="${ex + 4}" y="${plotB - 5}" font-size="${font}" fill="var(--secondary-text-color,#888)">${esc(
          L("plan.estimated_prices")
        )}</text>`
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

    // Where BOTH circuits are planned in the same quarter hour the pump is
    // time-sharing the step — hot water first, then heating. That is a
    // deliberate relaxation (space + hot water ≤ nameplate per step), not
    // double-booking, and two full-height bars with nothing said implied
    // the impossible. Drawn under the bars so the bars stay readable.
    // The list is passed in rather than read from this._series so the
    // helper stays a pure function of its inputs.
    parts.push(
      this._sharedSpanBands(visible, scaleX, plotT, plotB, plotL, plotR)
    );

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
      `<line class="crosshair" pointer-events="none" x1="0" y1="${plotT}" x2="0" y2="${plotB}" stroke="var(--secondary-text-color,#888)" stroke-width="1" visibility="hidden"/>`
    );

    // role="img" flattens every descendant for assistive tech, which is
    // right for a pure picture but wrong the moment the lanes put focusable
    // slots inside it — those need "group" so they stay in the tree. The
    // editable chart also takes tabindex="-1": it is the last-resort home
    // for restored focus (`_restoreSlotFocus`), and an svg without a
    // tabindex refuses programmatic focus.
    const editing = this._editingEnabled();
    return `<svg viewBox="0 0 ${VIEW_W} ${VIEW_H}" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" role="${
      editing ? "group" : "img"
    }"${editing ? ' tabindex="-1"' : ""} aria-label="${esc(
      this._title()
    )}">${parts.join("")}</svg>`;
  }

  /** The right-click menu for a lane.
   *
   * Rendered as plain HTML positioned over the card rather than as SVG, so it
   * is not clipped by the chart and inherits the dialog's font.
   */
  _openSlotMenu(channel, at, clientX, clientY, svg, focusMenu) {
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
    // Whole sentences per channel rather than an interpolated noun: gendered
    // articles and compound nouns make "Remove this {channel} slot" untranslatable.
    const dhw = channel === "dhw";
    menu.innerHTML = editable
      ? `<button type="button" data-act="remove">${esc(
          L(dhw ? "menu.remove_slot_dhw" : "menu.remove_slot_space")
        )}</button>`
      : `<button type="button" data-act="add">${esc(
          L(dhw ? "menu.add_slot_dhw" : "menu.add_slot_space")
        )}</button>`;

    const svgIndex = this._chartSvgs().indexOf(svg);
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
      // The render just destroyed the element that had focus (the menu's
      // button, or the slot). Falling to document.body strands a keyboard
      // user; the lane the action happened in is the logical successor —
      // the acted-on slot itself no longer exists (removed) or has a new
      // index (added).
      this._restoreSlotFocus(channel, null, svgIndex);
    });
    // Escape dismisses the menu whichever way it was opened. The menu's own
    // listener covers the keyboard-opened case, where its button holds
    // focus; a MOUSE-opened menu leaves focus on the chart, so Escape must
    // also be caught at the document (registered below, removed on close).
    const onEscape = (ev) => {
      if (ev.key !== "Escape") return;
      stop(ev);
      const origin = this._menuOrigin;
      this._closeSlotMenu();
      // Nothing re-rendered, but a keyboard-opened menu moved focus into
      // its button, which is now gone: send it back where the menu came
      // from.
      if (origin) {
        this._restoreSlotFocus(origin.channel, origin.index, origin.svgIndex);
      }
    };
    menu.addEventListener("keydown", onEscape);
    host.appendChild(menu);
    this._slotMenu = menu;
    this._menuOrigin = { channel, index: editable ? index : null, svgIndex };
    const escTarget = this._globalKeyTarget();
    if (escTarget) {
      this._menuEscape = onEscape;
      this._menuEscapeTarget = escTarget;
      escTarget.addEventListener("keydown", onEscape);
    }
    if (focusMenu) {
      const btn = menu.querySelector("button");
      if (btn && typeof btn.focus === "function") btn.focus();
    }
  }

  _closeSlotMenu() {
    const menu = this._slotMenu;
    if (menu && menu.parentNode && menu.parentNode.removeChild) {
      menu.parentNode.removeChild(menu);
    }
    this._slotMenu = null;
    this._menuOrigin = null;
    if (this._menuEscapeTarget && this._menuEscape) {
      this._menuEscapeTarget.removeEventListener("keydown", this._menuEscape);
    }
    this._menuEscape = null;
    this._menuEscapeTarget = null;
  }

  /** Where a while-the-menu-is-open key listener can live: keydown events
   * are composed, so they bubble out of the shadow root to the document. */
  _globalKeyTarget() {
    if (typeof document !== "undefined" && document.addEventListener) {
      return document;
    }
    if (typeof window !== "undefined" && window.addEventListener) {
      return window;
    }
    return null;
  }

  /** Put keyboard focus back near a slot action after the DOM it happened
   * in was rebuilt (or its menu closed): the same slot re-located by its
   * channel and index in the fresh chart, else that channel's lane, else
   * the chart svg itself — never document.body.
   */
  _restoreSlotFocus(channel, index, svgIndex) {
    const svgs = this._chartSvgs(this.shadowRoot);
    const svg = svgs[svgIndex] || svgs[svgs.length - 1];
    if (!svg) return;
    const focus = (el) =>
      !!(el && typeof el.focus === "function" && (el.focus(), true));
    if (index !== null && index !== undefined && index >= 0) {
      for (const slot of svg.querySelectorAll(".slot")) {
        const d = slot.dataset || {};
        if (
          d.channel === channel &&
          Number(d.index) === Number(index) &&
          !slot.classList.contains("locked")
        ) {
          if (focus(slot)) return;
        }
      }
    }
    for (const lane of svg.querySelectorAll(".lane")) {
      if ((lane.dataset || {}).channel === channel) {
        if (focus(lane)) return;
      }
    }
    focus(svg);
  }

  /** Take focus off a setup row that no longer deserves it.
   *
   * The rows are focusable (`tabindex="0"`, `role="button"`) so the diagram
   * can be assigned from the keyboard. The cost is that a pointer gesture
   * can leave one focused with nothing on screen explaining why, and a
   * click on the diagram's empty space does not reliably move focus off an
   * SVG element -- which is how a ring survived a cancelled picker.
   */
  _blurSetupRow() {
    const root = this.shadowRoot;
    const active =
      (root && root.activeElement) ||
      (typeof document !== "undefined" ? document.activeElement : null);
    if (!active || !active.classList || !active.classList.contains("setup-hit")) {
      return;
    }
    if (typeof active.blur === "function") active.blur();
  }

  /** Focus the setup row the entity picker was opened from, once the picker
   * has closed and the render that removed it has finished. The row is
   * re-located by its data-key: the element that had focus was rebuilt. */
  _restoreSetupFocus(key) {
    if (!key || !this.shadowRoot) return;
    for (const hit of this.shadowRoot.querySelectorAll(".setup-hit")) {
      if ((hit.dataset || {}).key === key) {
        if (typeof hit.focus === "function") hit.focus();
        return;
      }
    }
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
      // v4.1.0+: the integration publishes the currency its prices are in on
      // the plan sensors. That beats Home Assistant's global currency, which
      // describes the install, not the price feed.
      this._planAttrRaw("currency", null) ||
      (hass.config && hass.config.currency) ||
      "SEK"
    );
  }

  _deltaHtml() {
    const { planned, edited, delta } = this._costDelta();
    if (!Number.isFinite(delta) || (!planned && !edited)) {
      return `<span class="wi-hint">${L("stats.no_plan_to_compare")}</span>`;
    }
    const cur = this._currency();
    const cls = delta < -0.005 ? "cheaper" : delta > 0.005 ? "dearer" : "";
    const sign = delta > 0 ? "+" : "";
    const verdict = L(
      cls === "cheaper"
        ? "stats.cheaper"
        : cls === "dearer"
          ? "stats.dearer"
          : "stats.the_same"
    );
    return `
      <span class="delta ${cls}">${sign}${delta.toFixed(2)}&nbsp;${esc(cur)}</span>
      <span class="wi-hint">${L("stats.delta_detail", {
        verdict,
        planned: planned.toFixed(2),
        edited: edited.toFixed(2),
        currency: esc(cur),
      })}</span>`;
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
        <button type="button" class="vc-out" title="${esc(L("plan.zoom_out"))}"
          aria-label="${esc(L("plan.zoom_out"))}">&minus;</button>
        <button type="button" class="vc-in" title="${esc(L("plan.zoom_in"))}"
          aria-label="${esc(L("plan.zoom_in"))}">+</button>
        <button type="button" class="vc-reset" title="${esc(
          L("plan.show_whole_plan")
        )}"
          aria-label="${esc(L("plan.show_whole_plan"))}"${zoomed ? "" : " disabled"}>&#8634;</button>
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
      // No slot under the press: not draggable, but a press RELEASED here
      // without movement must still open the add-slot menu — on touch it
      // is the only way to reach it. menuOnly presses ignore movement.
      let menuOnly = index < 0;
      if (!menuOnly) {
        // A slot outside the editable range -- already run, or beyond the
        // point where the override expires -- must not be draggable.
        const [lo, hi] = this._editBounds();
        const run = runs[index];
        if (run && (run.end <= lo || run.start >= hi)) menuOnly = true;
      }

      this._drag = {
        channel,
        index,
        menuOnly,
        edge: data.edge || null,
        from: at,
        svgIndex: svgs.indexOf(svg),
        lastClientX: ev.clientX,
        lastClientY: ev.clientY,
        // Edits apply to the arrangement as it was when the drag began, so a
        // slow drag does not compound its own deltas.
        original: runs.map((r) => ({ ...r })),
      };
      // The svg-bound listeners below serve the common case, but an auto-pan
      // re-render replaces the svg mid-gesture and its listeners with it, so
      // the gesture's continuation also lives on `window` for the duration —
      // the same survival trick the chart's pan drag uses. Both firing for
      // one event is harmless: the second apply lands on identical state.
      const winMove = (e) => {
        const d = this._drag;
        if (!d) return;
        d.lastClientX = e.clientX;
        const cur = svgAt(d.svgIndex);
        if (cur) applyDragAt(cur, e.clientX);
        maybeAutoPan(d.svgIndex, e.clientX);
      };
      const winUp = () => {
        window.removeEventListener("pointermove", winMove);
        window.removeEventListener("pointerup", winUp);
        window.removeEventListener("pointercancel", winUp);
        stopAutoPan();
        onUp();
      };
      window.addEventListener("pointermove", winMove);
      window.addEventListener("pointerup", winUp);
      window.addEventListener("pointercancel", winUp);
      stop(ev);
      if (ev.preventDefault) ev.preventDefault();
    };

    const svgAt = (index) => {
      // Auto-pan re-renders, replacing the svg the gesture started on; the
      // chart at the same position in the fresh shadow root is its heir.
      const current = this._chartSvgs(this.shadowRoot || root);
      return current[index] || current[current.length - 1] || null;
    };

    const applyDragAt = (svg, clientX) => {
      const drag = this._drag;
      if (!drag || drag.menuOnly) return;
      const at = this._timeAtClientX(svg, clientX);
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

    const onMove = (svg, ev) => {
      if (this._drag) this._drag.lastClientX = ev.clientX;
      applyDragAt(svg, ev.clientX);
    };

    const stopAutoPan = () => {
      if (this._dragPan) {
        clearInterval(this._dragPan);
        this._dragPan = null;
      }
    };

    // Holding a dragged slot against the plot's edge pans the view under it.
    // Without this, a zoomed-in view is a wall: the edit ceiling clamps to
    // the visible window (a slot must not land where the pointer cannot
    // reach), so a user who zoomed — often accidentally, by pinch or
    // ctrl-wheel — finds editing "stops" at an arbitrary-looking time.
    const maybeAutoPan = (index, clientX) => {
      if (!this._drag || this._drag.menuOnly || !this._viewAdjustable()) {
        stopAutoPan();
        return;
      }
      const svg = svgAt(index);
      const rect =
        svg && svg.getBoundingClientRect ? svg.getBoundingClientRect() : null;
      if (!rect || !rect.width) {
        stopAutoPan();
        return;
      }
      const dir =
        clientX > rect.left + rect.width - AUTOPAN_MARGIN_PX
          ? 1
          : clientX < rect.left + AUTOPAN_MARGIN_PX
            ? -1
            : 0;
      if (!dir) {
        stopAutoPan();
        return;
      }
      if (this._dragPan) return;
      this._dragPan = setInterval(() => {
        const drag = this._drag;
        const lim = this._viewLimits;
        if (!drag || !lim) {
          stopAutoPan();
          return;
        }
        const cur = this._viewCurrent();
        const step = dir * Math.max(PLAN_STEP_MS, cur.span * 0.04);
        const maxStart = Math.max(lim.floor, lim.rightBound - cur.span);
        const start = clampNum(cur.start + step, lim.floor, maxStart);
        if (start === cur.start) {
          stopAutoPan();
          return;
        }
        this._view = { start, span: cur.span };
        // A full render: the gesture survives it because move/up also live
        // on `window` (registered per drag below), exactly as the pan
        // gesture does and for the same reason.
        this._render();
        const fresh = svgAt(drag.svgIndex);
        if (fresh && drag.lastClientX !== undefined) {
          applyDragAt(fresh, drag.lastClientX);
        }
      }, AUTOPAN_INTERVAL_MS);
    };

    const onUp = () => {
      if (!this._drag) return;
      const drag = this._drag;
      // The browser synthesises a click after pointerup — preventDefault on
      // pointerdown suppresses compatibility mouse events but not click — and
      // on the inline chart that click bubbles to ha-card and pops the
      // expanded dialog open at the end of every drag. Same one-shot
      // suppression the pan gesture uses; a drag ending off-svg spends it on
      // nothing, which the pan path already accepts.
      if (drag.moved) this._suppressClick = true;
      this._drag = null;
      this._render();
      // A press released without movement is a tap: open the slot menu the
      // desktop reaches by right-click. iOS Safari never synthesises
      // contextmenu (no long-press equivalent), so before this a touch
      // user could not add or remove a slot at all. Desktop gains the
      // same affordance — a menu on plain click is more discoverable than
      // one hidden behind the right button. After _render so the menu
      // attaches to the fresh shadow root, and suppressClick still spends
      // the synthetic click before it can pop the dialog.
      if (
        !drag.moved &&
        drag.lastClientX !== undefined &&
        drag.lastClientY !== undefined
      ) {
        this._suppressClick = true;
        const fresh = svgAt(drag.svgIndex);
        if (fresh) {
          const at = this._timeAtClientX(fresh, drag.lastClientX);
          if (at !== null) {
            this._openSlotMenu(
              drag.channel, at, drag.lastClientX, drag.lastClientY, fresh
            );
          }
        }
      }
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

    // The keyboard equivalent of the pointer gestures, delegated on the svg
    // like everything else here (the rects are rebuilt on every refresh).
    // Enter/Space on a focused slot or lane opens the same menu a
    // right-click does; Delete removes the focused slot outright. Dragging
    // has no keyboard form — the menu's add/remove covers the same edits,
    // just in more steps.
    const onKeydown = (svg, ev) => {
      const data = (ev.target || {}).dataset || {};
      if (!data.channel) return;
      const key = ev.key;
      const wantsMenu =
        key === "Enter" || key === " " || key === "ContextMenu";
      const wantsRemove = key === "Delete" || key === "Backspace";
      if (!wantsMenu && !wantsRemove) return;
      const geom = this._geom;
      if (!geom) return;
      if (ev.preventDefault) ev.preventDefault();
      stop(ev);

      const channel = data.channel;
      const runs = this._draftRuns()[channel] || [];
      const index = data.index === undefined ? -1 : Number(data.index);
      const run = index >= 0 ? runs[index] : null;
      const [lo, hi] = this._editBounds();

      if (wantsRemove) {
        if (run && run.end > lo && run.start < hi) {
          this._commitRuns(channel, SlotModel.remove(runs, index));
          this._render();
          // The focused slot is gone and the render rebuilt everything
          // around it; without this, focus drops to document.body and a
          // keyboard user restarts from the top. Its lane is the successor.
          this._restoreSlotFocus(channel, null, svgs.indexOf(svg));
        }
        return;
      }

      // The menu asks "what is at this time?", so aim it at the middle of
      // the focused slot — or, from a lane, at the middle of the editable
      // stretch of the visible window.
      let at;
      if (run) {
        at = (run.start + run.end) / 2;
      } else {
        const s = Math.max(lo, geom.windowStart);
        const e = Math.min(hi, geom.windowEnd);
        if (e <= s) return;
        at = (s + e) / 2;
      }
      // Anchor the menu where that time is drawn. The pointer paths get
      // client coordinates for free; here they are reconstructed from the
      // viewBox geometry, and degrade to the svg's own corner when the
      // element cannot be measured.
      const rect = svg.getBoundingClientRect
        ? svg.getBoundingClientRect()
        : null;
      let clientX = rect ? rect.left : 0;
      let clientY = rect ? rect.top : 0;
      if (rect && rect.width) {
        const span = geom.windowEnd - geom.windowStart || 1;
        const vx =
          geom.plotL + ((at - geom.windowStart) / span) * geom.plotW;
        clientX = rect.left + (vx / VIEW_W) * rect.width;
        clientY =
          rect.top + ((geom.plotB - LANE_H) / VIEW_H) * (rect.height || 0);
      }
      this._openSlotMenu(channel, at, clientX, clientY, svg, true);
    };

    for (const svg of svgs) {
      svg.addEventListener("pointerdown", (ev) => onDown(svg, ev));
      svg.addEventListener("pointermove", (ev) => onMove(svg, ev));
      svg.addEventListener("pointerup", onUp);
      svg.addEventListener("pointerleave", onUp);
      svg.addEventListener("contextmenu", (ev) => onContext(svg, ev));
      svg.addEventListener("keydown", (ev) => onKeydown(svg, ev));
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
      {
        channel: "dhw",
        label: L("slots.lane_dhw"),
        field: "dhw_power",
        color: "#e0544e",
      },
      {
        channel: "space",
        label: L("slots.lane_space"),
        field: "space_power",
        color: "#4a90e2",
      },
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
    const p = this._editCeilingParts();
    return Math.min(p.visibleEnd, p.applyEnd, p.planEnd);
  }

  /** The ceiling's three inputs, separately, so the lanes can say WHICH one
   * is in charge. When the visible window is the binding limit the user is
   * zoomed in, and an edit stopping there reads as an arbitrary rule unless
   * the card says so — a real user diagnosed it as "slots end at midnight".
   */
  _editCeilingParts() {
    const visibleEnd = this._geom ? this._geom.windowEnd : Infinity;
    const windowHours = this._planAttr(
      "manual_plan_window_hours",
      MANUAL_PLAN_WINDOW_FALLBACK_H
    );
    return {
      visibleEnd,
      applyEnd: Date.now() + windowHours * 3600 * 1000,
      planEnd: this._planEnd(),
    };
  }

  /** Whether the zoomed-in view, not the plan or the 20 h window, is what
   * currently stops editing. The one-second slack keeps float noise from
   * flickering the hint on an unzoomed card whose window ends at the plan.
   */
  _viewLimitsEditing() {
    const p = this._editCeilingParts();
    return p.visibleEnd < Math.min(p.applyEnd, p.planEnd) - 1000;
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
      // The track, so an empty lane is still an obvious drop target. Also a
      // tab stop: Enter on it opens the same add-slot menu a right-click
      // does, which is the whole editor without a pointer.
      out.push(
        `<rect class="lane" data-channel="${spec.channel}" tabindex="0" role="button" aria-label="${esc(
          L("slots.lane_aria", { lane: spec.label })
        )}" x="${plotL}" y="${y}" width="${
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
      // The lane runs out at the zoomed window, not at any rule of the
      // plan's: mark it, or the invisible remainder reads as a hard limit.
      if (this._viewLimitsEditing()) {
        out.push(
          `<text class="lane-more" x="${plotR - 3}" y="${
            y + LANE_H - 3
          }" font-size="${font}" text-anchor="end" fill="var(--primary-color,#03a9f4)">»</text>`
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
        // Editable slots are tab stops with the keyboard menu (Enter) and
        // removal (Delete) announced; locked ones stay presentational.
        const fmtT = (t) =>
          new Date(t).toLocaleTimeString(ACTIVE_LANG, {
            hour: "2-digit",
            minute: "2-digit",
          });
        const kbd = locked
          ? ""
          : ` tabindex="0" role="button" aria-label="${esc(
              L("slots.slot_aria", {
                lane: spec.label,
                start: fmtT(run.start),
                end: fmtT(run.end),
              })
            )}"`;
        out.push(
          `<rect class="slot${locked ? " locked" : ""}" data-channel="${
            spec.channel
          }" data-index="${index}"${kbd} x="${x1}" y="${y}" width="${w}" height="${LANE_H}" rx="2" fill="${
            spec.color
          }" fill-opacity="${locked ? 0.35 : 0.85}"/>`
        );
        if (locked) return;
        // Explicit edge handles: without them a narrow slot is impossible to
        // resize, because the whole rect reads as "move".
        const grab = _coarsePointer() ? LANE_EDGE_GRAB_COARSE : LANE_EDGE_GRAB;
        for (const edge of ["start", "end"]) {
          const ex = edge === "start" ? x1 : x2 - grab;
          out.push(
            `<rect class="slot-handle" data-channel="${spec.channel}" data-index="${index}" data-edge="${edge}" x="${ex}" y="${y}" width="${grab}" height="${LANE_H}" fill="#fff" fill-opacity="0.001"/>`
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
        label: d.toLocaleTimeString(ACTIVE_LANG, {
          hour: "2-digit",
          minute: "2-digit",
        }),
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
          `<path class="series" data-key="${s.key}" pointer-events="none" d="${areaD}" fill="${s.color}" fill-opacity="${fillOpacity}" stroke="none"/>`
        );
        out.push(
          `<path class="series" data-key="${s.key}" pointer-events="none" d="${stepD}" fill="none" stroke="${s.color}" stroke-width="1.5"/>`
        );
      } else {
        const d = this._smoothLine(pts);
        const dash = line.primary
          ? ""
          : ` stroke-dasharray="3 3" stroke-opacity="0.7"`;
        out.push(
          `<path class="series" data-key="${s.key}" pointer-events="none" d="${d}" fill="none" stroke="${s.color}" stroke-width="1.8"${dash}/>`
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
    // The pan/zoom view dies with the session it belonged to. It used to
    // persist for the lifetime of the card element — on a wall-mounted
    // dashboard, indefinitely — so one accidental trackpad pinch or
    // two-finger swipe over the chart quietly capped slot editing at the
    // narrowed window's edge for days, while re-anchoring itself to "now"
    // so it never scrolled out of relevance. A dismissed dialog is a
    // finished session; the next open shows the whole plan.
    this._view = null;
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
      const label = REASON_LABELS[r.reason]
        ? L(REASON_LABELS[r.reason])
        : r.reason;
      out.push(`<div class="tt-reason">${esc(label)}</div>`);
    }
    if (rows.some((r) => r.priceKnown === false)) {
      out.push(
        `<div class="tt-reason">${esc(L("plan.price_estimated"))}</div>`
      );
    }
    return out.join("");
  }

  /** Hatched bands over every span where space and hot water share steps.
   *
   * Only when both power series are visible — hiding a channel hides its
   * half of the story, and a band explaining an invisible series would be
   * noise. The native <title> answers the "is this double-booking?"
   * question right where it is asked.
   */
  _sharedSpanBands(seriesList, scaleX, plotT, plotB, plotL, plotR) {
    const powerSeries = (field) =>
      (seriesList || []).find(
        (s) => s.field === field && s.visible && s.hasData
      );
    const space = powerSeries("space_power");
    const dhw = powerSeries("dhw_power");
    if (!space || !dhw) return "";
    const pointsOf = (s) => {
      const line = s.lines.find((l) => l.primary) || s.lines[0];
      return line ? line.points : [];
    };
    const spacePts = pointsOf(space);
    const dhwPts = pointsOf(dhw);
    if (spacePts.length < 2 || dhwPts.length < 2) return "";
    const spaceAt = new Map(spacePts.map((p) => [p.t, p.v]));
    let step = Infinity;
    for (let i = 1; i < dhwPts.length; i++) {
      step = Math.min(step, dhwPts[i].t - dhwPts[i - 1].t);
    }
    if (!Number.isFinite(step) || step <= 0) return "";
    const spans = [];
    for (const p of dhwPts) {
      const sv = spaceAt.get(p.t);
      if (p.v > 0.05 && sv !== undefined && sv > 0.05) {
        const last = spans[spans.length - 1];
        if (last && p.t <= last.end + step / 2) last.end = p.t + step;
        else spans.push({ start: p.t, end: p.t + step });
      }
    }
    if (!spans.length) return "";
    // The pattern id must be unique per chart: with the dialog open the
    // inline and expanded charts render into one shadow root, and two
    // <pattern> elements sharing an id is invalid markup that would
    // silently couple them.
    const pid = `hpoShared${++HeatpumpOptimizerCard._sharedPatternSeq}`;
    const out = [
      `<defs><pattern id="${pid}" width="6" height="6"
        patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <line x1="0" y1="0" x2="0" y2="6"
          stroke="var(--secondary-text-color,#888)" stroke-width="1.4"/>
      </pattern></defs>`,
    ];
    for (const span of spans) {
      const x1 = Math.max(plotL, scaleX(span.start));
      const x2 = Math.min(plotR, scaleX(span.end));
      if (x2 <= x1) continue;
      // pointer-events none is load-bearing: the band spans the full plot
      // and paints after the what-if lanes, so without it a low-power
      // shared span would swallow the slot editor's drags and clicks.
      out.push(`<rect class="shared-band" pointer-events="none" x="${x1}" y="${plotT}" width="${
        x2 - x1
      }" height="${plotB - plotT}" fill="url(#${pid})" fill-opacity="0.18">
        <title>${esc(L("plan.shared_band_title"))}</title>
      </rect>`);
    }
    return out.join("");
  }

  /** The tooltip's shared-step line, or "" when this step is not shared.
   *
   * A step carrying both circuits is the pump splitting the quarter hour,
   * and the hover tooltip is where that question is actually asked. Both
   * rows must come from the SAME timestamp: each series snaps to its own
   * nearest point, and with mismatched grids (a stale third-party sensor)
   * the two nearest points can be hours apart — pairing those would claim
   * sharing the band correctly refuses to draw.
   */
  _sharedTooltipHtml(rows) {
    const rowByField = (f) => (rows || []).find((r) => r.field === f);
    const spaceRow = rowByField("space_power");
    const dhwRow = rowByField("dhw_power");
    if (
      !spaceRow ||
      !dhwRow ||
      spaceRow.t !== dhwRow.t ||
      !(spaceRow.value > 0.05) ||
      !(dhwRow.value > 0.05)
    ) {
      return "";
    }
    return `<div class="tt-shared">${L("plan.shared_step_tooltip", {
      kw: esc(fmtTick(spaceRow.value + dhwRow.value)),
    })}</div>`;
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
      // Every line, not just the primary one. The house-temperature series
      // draws three traces and the tooltip used to report the room's value
      // for all of them, so hovering a 28 C zone line showed 21 C.
      for (const line of s.lines) {
        let best = null;
        let bestDt = Infinity;
        for (const p of line.points) {
          const dt = Math.abs(p.t - t);
          if (dt < bestDt) {
            bestDt = dt;
            best = p;
          }
        }
        if (!best) continue;
        if (!snapped) {
          snapX = scaleX(best.t);
          snapped = true;
        }
        rows.push({
          color: s.color,
          label: this._lineLabel(s, line),
          dashed: !line.primary,
          value: best.v,
          unit: this._seriesUnit(s),
          t: best.t,
          field: line.field,
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
      const time = new Date(rows[0].t).toLocaleString(ACTIVE_LANG, {
        hour: "2-digit",
        minute: "2-digit",
      });
      const sharedHtml = this._sharedTooltipHtml(rows);
      const bodyHtml =
        `<div class="tt-time">${esc(time)}</div>` +
        rows
          .map(
            (r) =>
              `<div class="tt-row"><span class="dot" style="${dotStyle(
                r.color,
                r.dashed
              )}"></span>${esc(r.label)}: ${esc(fmtTick(r.value))} ${esc(
                r.unit
              )}</div>`
          )
          .join("") +
        sharedHtml +
        this._reasonHtml(rows);
      tt.innerHTML = bodyHtml;
      tt.hidden = false;
      const leftPx = clientX - rect.left;
      const place = leftPx > rect.width * 0.6 ? leftPx - 160 : leftPx + 14;
      // Clamped to the chart, both edges. Flipping to the left of the pointer
      // past 60 % of the width assumed a 160 px box; a wider one (a long
      // reason line, a shared-step sentence, a chart in the expanded dialog)
      // still ran off the right-hand side and over the card beside it. Measure
      // the box that actually exists, and keep its right edge inside the plot.
      // `offsetWidth` is 0 before layout and absent in the test DOM, hence the
      // fallback to the width this placement was originally written for.
      const ttWidth = tt.offsetWidth || 160;
      const rightLimit = Math.max(0, rect.width - ttWidth - 4);
      tt.style.left = `${Math.min(Math.max(0, place), rightLimit)}px`;
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
// Per-render sequence for the shared-band pattern ids (see _sharedSpanBands).
HeatpumpOptimizerCard._sharedPatternSeq = 0;

// ---- The visual config editor ---------------------------------------------
//
// Returned by `getConfigElement`. Built on Home Assistant's own `ha-form`,
// which supplies the selectors (entity pickers, toggles, number boxes) and the
// theming for free; this element only owns the schema, the current values and
// the `config-changed` contract. Same file as the card on purpose: one
// resource, no build step, no lazy chunk that can 404 independently.

// Currencies offered by the dropdown; `custom_value` keeps any other ISO code
// typeable, so the list only needs to cover the likely ones.
const EDITOR_CURRENCIES = [
  "SEK", "EUR", "NOK", "DKK", "GBP", "USD", "PLN", "CZK", "CHF",
];

class HeatpumpOptimizerCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = { ...(config || {}) };
    this._upgrade();
  }

  set hass(hass) {
    this._hass = hass;
    // The editor can receive hass before setConfig (Lovelace sets both in
    // either order), so it must render from whichever arrives last.
    setLanguage(hass && hass.language);
    this._upgrade();
  }

  get hass() {
    return this._hass;
  }

  /** The form's schema: every documented config key, as selectors. */
  _schema() {
    // The three data sources are sensors of this integration, so the picker
    // is filtered to exactly those rather than every sensor in the house.
    const planEntity = {
      entity: { integration: "heatpump_optimizer", domain: "sensor" },
    };
    return [
      { name: "title", selector: { text: {} } },
      { name: "space_entity", selector: planEntity },
      { name: "dhw_entity", selector: planEntity },
      { name: "solar_entity", selector: planEntity },
      {
        name: "hours",
        selector: {
          number: {
            min: 1, max: 168, step: 1, mode: "box",
            unit_of_measurement: "h",
          },
        },
      },
      { name: "what_if", selector: { boolean: {} } },
      { name: "show_stats", selector: { boolean: {} } },
      {
        name: "currency",
        selector: {
          select: {
            mode: "dropdown",
            custom_value: true,
            options: EDITOR_CURRENCIES,
          },
        },
      },
      {
        name: "series",
        type: "expandable",
        schema: SERIES_DEFS.map((d) => ({
          name: d.key,
          selector: { boolean: {} },
        })),
      },
    ];
  }

  /** What the form shows: the config with every default filled in, so a
   * toggle reads as its effective value rather than as blank. */
  _data() {
    const cfg = this._config || {};
    const series = {};
    for (const d of SERIES_DEFS) {
      series[d.key] = !(cfg.series && cfg.series[d.key] === false);
    }
    return { ...DEFAULTS, ...cfg, series };
  }

  /** Create the form once, then keep its inputs current. */
  _upgrade() {
    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.addEventListener("value-changed", (ev) =>
        this._onValueChanged(ev)
      );
      this.appendChild(this._form);
    }
    this._form.hass = this._hass;
    this._form.data = this._data();
    this._form.schema = this._schema();
    this._form.computeLabel = (s) => {
      // The series toggles reuse the legend's own labels; everything else
      // has an editor.* key.
      const def = SERIES_DEFS.find((d) => d.key === s.name);
      return def ? L(def.labelKey) : L(`editor.${s.name}`);
    };
  }

  /** Turn the form's value back into the leanest equivalent config.
   *
   * The form pre-fills every default (`_data`), so the value it emits
   * carries space_entity/hours/what_if/… even when the user never touched
   * them. Storing those verbatim would bake the defaults into the YAML on
   * the first GUI edit; instead any key whose value merely restates its
   * default is dropped, alongside emptied fields.
   */
  _onValueChanged(ev) {
    stop(ev);
    const v = (ev.detail && ev.detail.value) || {};
    const prior = this._config || {};
    const config = { ...prior };
    config.type = config.type || `custom:${CARD_TAG}`;
    for (const key of [
      "title", "space_entity", "dhw_entity", "solar_entity",
      "hours", "what_if", "show_stats", "currency",
    ]) {
      // `title` is the one key where "" is a legitimate stored value (it
      // renders no header text), so an explicitly configured empty title
      // survives unrelated edits. Only a title that was absent before and
      // comes back empty is treated as "no title configured".
      if (key === "title") {
        const had = Object.prototype.hasOwnProperty.call(prior, "title");
        if (v.title === undefined || (v.title === "" && !had)) {
          delete config.title;
        } else {
          config.title = v.title;
        }
        continue;
      }
      // An emptied or default-restating field means "back to the default",
      // and the stored config stays free of keys that merely restate it.
      if (
        v[key] === undefined ||
        v[key] === "" ||
        (key in DEFAULTS && v[key] === DEFAULTS[key])
      ) {
        delete config[key];
      } else {
        config[key] = v[key];
      }
    }
    // Series: only "start hidden" is worth storing; `true` is the default.
    const series = {};
    for (const d of SERIES_DEFS) {
      if (v.series && v.series[d.key] === false) series[d.key] = false;
    }
    if (Object.keys(series).length) config.series = series;
    else delete config.series;
    this._config = config;
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config },
        bubbles: true,
        composed: true,
      })
    );
  }
}

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
// The editor rides the same guard logic but its own registration: a stale
// duplicate card may predate the editor entirely, and defining ours anyway
// gives that card's getConfigElement something to create.
if (!customElements.get(EDITOR_TAG)) {
  customElements.define(EDITOR_TAG, HeatpumpOptimizerCardEditor);
}

window.customCards = window.customCards || [];
window.customCards.push({
  type: CARD_TAG,
  name: "Heat Pump Optimizer Card",
  description:
    "Plots heat-pump price, power and temperature plans on one shared time axis with per-series toggles.",
  // The preview renders from getStubConfig; with no plan sensors in the
  // dashboard picker's context it shows the card's own diagnostic empty
  // state, which is honest and harmless.
  preview: true,
});

// eslint-disable-next-line no-console
console.info(
  `%c ${CARD_TAG} %c v${CARD_VERSION} `,
  "color:#fff;background:#2fae7a;border-radius:3px 0 0 3px;padding:2px 4px;",
  "color:#2fae7a;background:#222;border-radius:0 3px 3px 0;padding:2px 4px;"
);
