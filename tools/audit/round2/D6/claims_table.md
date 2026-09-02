| id | source | claim | observed | verdict | true statement |
|---|---|---|---|---|---|
| C001 | VERSION / manifest.json | VERSION and manifest.json carry the same version | observed='6.2.14' expected='6.2.14' | true |  |
| C002 | README:10,140 / hacs.json | Home Assistant 2024.1.0 or newer (badge and Requirements) matches hacs.json | observed='2024.1.0' expected='2024.1.0' | true |  |
| C003 | README:143 / manifest.json | numpy and scipy are installed from the manifest | requirements=['numpy>=1.24.0', 'scipy>=1.10.0', 'threadpoolctl>=3.5.0'] (threadpoolctl is a third requirement the README does not name) | true |  |
| C004 | hacs.json / manifest.json | hacs.json name equals manifest name | observed='Heat Pump Cost Optimizer' expected='Heat Pump Cost Optimizer' | true |  |
| C005 | manifest.json | documentation URL is reachable | https://github.com/tvofi/heatpump_optimizer: HTTP 200 | true |  |
| C006 | manifest.json | issue_tracker URL is reachable | https://github.com/tvofi/heatpump_optimizer/issues: HTTP 200 | true |  |
| C007 | manifest.json / const.py:8 | the five platforms sensor, binary_sensor, button, climate, switch are the PLATFORMS | observed=['binary_sensor', 'button', 'climate', 'sensor', 'switch'] expected=['binary_sensor', 'button', 'climate', 'sensor', 'switch'] | true |  |
| C008 | README:19 | strutsfarm/heatpump_optimizer link | https://github.com/strutsfarm/heatpump_optimizer: HTTP 200 | true |  |
| C009 | README:23 | strutsfarm/ecl110 link | https://github.com/strutsfarm/ecl110: HTTP 200 | true |  |
| C010 | README:9 | hacs.xyz link | https://hacs.xyz: HTTP 200 | true |  |
| C011 | README:10 | home-assistant.io link | https://www.home-assistant.io: HTTP 200 | true |  |
| C012 | README:141 | developer.tibber.com link | https://developer.tibber.com: HTTP 200 | true |  |
| C013 | README:9-11 | shields.io badge images resolve | https://img.shields.io/badge/HACS-custom-41BDF5.svg: HTTP 200 | true |  |
| C014 | README:26,629,640 | NOTICE, LICENSE and DISCLAIMER.md exist | all three exist | true |  |
| C015 | README:26 | LICENSE is the verbatim MIT text | MIT header and grant present | true |  |
| C016 | README:26 / NOTICE | the upstream (strutsfarm) attribution is recorded in NOTICE | NOTICE names strutsfarm | true |  |
| C017 | README:623-627 | docs/how-it-works.md exists | docs/how-it-works.md: exists=True | true |  |
| C018 | README:623-627 | docs/configuration.md exists | docs/configuration.md: exists=True | true |  |
| C019 | README:623-627 | docs/dashboard-card.md exists | docs/dashboard-card.md: exists=True | true |  |
| C020 | README:623-627 | docs/architecture.md exists | docs/architecture.md: exists=True | true |  |
| C021 | README:623-627 | docs/ecl110.md exists | docs/ecl110.md: exists=True | true |  |
| C022 | README:610,617,628 / how-it-works.md:1279 | docs/backlog.md exists (linked four times) | docs/backlog.md: absent from the export by design (audit-era file removed) | unverifiable |  |
| C023 | const.py:49 / how-it-works.md:647 | api.open-meteo.com/v1/forecast is reachable | https://api.open-meteo.com/v1/forecast: HTTP 200 | true |  |
| C024 | README:134,258 | entity names are translated: en.json equals strings.json byte for byte | observed=b'{\n  "config": {\n    "step": {\n      "user": {\n        "title": "Heat Pump Optimizer Setup",\n        "description": "Choose which Home Assistant entities the optimizer reads. Clear a field to stop using th | true |  |
| C025 | README:134,258 | Swedish translation carries every key the English one has | en keys=866 sv keys=866 en-only=0 sv-only=0 | true |  |
| C030 | README:53,234 / architecture.md:36 / configuration.md:186 | 65 entities in total | observed=65 expected=65 | true |  |
| C031 | README:262 / architecture.md:36,146 | 55 sensors | observed=55 expected=55 | true |  |
| C032 | README:329 | 4 binary sensors | observed=4 expected=4 | true |  |
| C033 | README:338 | 4 buttons | observed=4 expected=4 | true |  |
| C034 | README:53 / architecture.md:36 | 1 switch and 1 climate entity | observed=(1, 1) expected=(1, 1) | true |  |
| C035 | README:262-323 | the README sensor table has 55 rows | observed=55 expected=55 | true |  |
| C036 | README:329-336 | the README binary-sensor table has 4 rows and matches the roster names | observed=['Away Mode', 'External Heat Source', 'Input Problem', 'Open Window Detected'] expected=['Away Mode', 'External Heat Source', 'Input Problem', 'Open Window Detected'] | true |  |
| C037 | README:338-345 | the README button table has 4 rows and matches the roster names | observed=['Diagnose Last Interval', 'Optimize Now', 'Reset Learned Comfort Weight', 'Run System Identification'] expected=['Diagnose Last Interval', 'Optimize Now', 'Reset Learned Comfort Weight', 'Run System Identificat | true |  |
| C038 | README:349 / strings.json | the switch is named Optimizer Active | observed='Optimizer Active' expected='Optimizer Active' | true |  |
| C039 | README:255,325-327 | six sensors are disabled by default: the six named | observed=['Compressor Frequency Advisor', 'Contract Comparison', 'DHW Heavy Day Demand', 'ECL110 Displace', 'ECL110 Effective Displace', 'Valve Target Recommendation'] expected=['Compressor Frequency Advisor', 'Contract  | true |  |
| C040 | README:259 'the tables below show the English names' | every README sensor name is the strings.json English name | 9 README names differ from strings.json: ['DHW Heating Cost', 'Space Heating Plan', 'DHW Heating Plan', 'Space Heating Energy', 'Hot Water Energy', 'Total Energy', 'Space Heating Cost', 'Hot Water Cost', 'Total Heating C | stale | strings.json names carry '(lifetime)' / '(next 24 h)' qualifiers the README table omits: DHW Heating Cost -> DHW Heating Cost (next 24 h), Space Heating Plan -> Space Heating Plan (next 24 h), DHW Heating Plan -> DHW Hea |
| C041 | README:267-323 Unit column | every sensor's unit is as the table says (CUR=SEK on a SEK instance) | 55 units agree; mismatches=[] | true |  |
| C042 | README Notes 'Diagnostic' | every sensor/binary sensor marked Diagnostic has EntityCategory.DIAGNOSTIC and no other does | diagnostic flags agree for all rows; mismatches=[] | true |  |
| C043 | README Notes 'Disabled by default' | the Notes column's disabled-by-default marks match entity_registry_enabled_default | mismatches=[] | true |  |
| C044 | README Notes 'Not recorded' / 'forecast not recorded' | every sensor marked not-recorded declares _unrecorded_attributes | every marked sensor declares _unrecorded_attributes; marked-but-recorded=[]; unrecorded-but-unmarked (omission, not a false claim)=[('Solar Irradiance', ['forecast'])] | true |  |
| C045 | README:283-284 'Timestamp' | Next/Last Optimization are timestamp sensors | observed=['timestamp', 'timestamp'] expected=['timestamp', 'timestamp'] | true |  |
| C046 | README:302-307 'Accumulating, for the Energy dashboard' | the three energy sensors are TOTAL_INCREASING kWh with the ENERGY device class | observed=[('total_increasing', 'energy'), ('total_increasing', 'energy'), ('total_increasing', 'energy')] expected=[('total_increasing', 'energy'), ('total_increasing', 'energy'), ('total_increasing', 'energy')] | true |  |
| C047 | README:305-307 | the three cost sensors are accumulating (TOTAL, MONETARY) | observed=[('total', 'monetary'), ('total', 'monetary'), ('total', 'monetary')] expected=[('total', 'monetary'), ('total', 'monetary'), ('total', 'monetary')] | true |  |
| C048 | README:281 / __init__.py RETIRED_ENTITIES | Solar Irradiance absorbed the former Solar Radiation sensor in v5.0.0 | observed=(('sensor', 'solar_radiation'),) expected=(('sensor', 'solar_radiation'),) | true |  |
| C049 | README:264 / currency.py | CUR is the instance currency, SEK when the instance has none | observed=('SEK', 'SEK') expected=('SEK', 'SEK') | true |  |
| C050 | README:582-586 | DHW Temperature exposes dhw_in_demand_window, dhw_next_window_in_hours, dhw_required_temperature, dhw_cooling_rate, dhw_cooling_rate_learned, dhw_cooling_samples, dhw_hold_hours | DHW Temperature attributes=['dhw_cooling_rate', 'dhw_cooling_rate_learned', 'dhw_cooling_samples', 'dhw_enabled', 'dhw_heating_active', 'dhw_hold_hours', 'dhw_idle_min_temperature', 'dhw_in_demand_window', 'dhw_legionell | true |  |
| C051 | README:416 / dashboard-card.md:208 | the plan sensors publish manual_override and manual_plan_window_hours=20 | observed=(20, True) expected=(20, True) | true |  |
| C052 | dashboard-card.md:527 / README:298 | the plan/solar sensors publish plan_kind space, dhw, solar | observed=['space', 'dhw', 'solar'] expected=['space', 'dhw', 'solar'] | true |  |
| C053 | README:281 | Solar Irradiance carries the forecast horizon in attributes | Solar Irradiance attributes=['forecast', 'plan_kind', 'solar_heat_gain_kw', 'source']... missing=[] | true |  |
| C054 | README:300 | Measured Power carries the commanded power alongside | Measured Power attributes=['energy_meter', 'house_power', 'recommended_power']... missing=[] | true |  |
| C055 | README:308,345 | Prediction Accuracy carries the signed bias and the last diagnosis | Prediction Accuracy attributes=['last_diagnosis', 'temperature_bias', 'temperature_mae', 'trust']... missing=[] | true |  |
| C056 | README:374 | the frequency view publishes an evidence_exhausted attribute (Compressor Frequency Advisor) | _freq_view keys=['commanded_hz', 'evidence_exhausted', 'fallback_active', 'map', 'mode', 'range_hz', 'recommended_hz', 'reported_hz'] | true |  |
| C057 | README:333 | Input Problem carries the evidence and which learners are frozen | attrs=['input_ages_minutes', 'learner_freeze_reason', 'learners_frozen', 'problems', 'stale_inputs', 'summary'] | true |  |
| C058 | README:336 | Away Mode carries the return time and recovery state | attrs=['away_dhw_min_temperature', 'away_target_temperature', 'hours_until_return', 'recovery_active', 'return_time', 'source'] | true |  |
| C059 | README:335 | External Heat Source carries evidence | attrs=['buffer_rise_c_per_h', 'confidence', 'dhw_rise_c_per_h', 'evidence', 'fading', 'since', 'source', 'suppressing_electric_dhw'] | true |  |
| C060 | README:309 | Monthly Peak Power is unavailable unless the capacity tariff is enabled | Monthly Peak Power: available(full)=True available(feature off)=False | true |  |
| C061 | README:310 | Solar Surplus Forecast is unavailable unless PV is enabled | Solar Surplus Forecast: available(full)=True available(feature off)=False | true |  |
| C062 | README:300 | Measured Power is unavailable until a power or energy entity is configured | Measured Power: available(full)=True available(feature off)=False | true |  |
| C063 | README:301 | Observed COP needs measured power | Observed COP: available(full)=True available(feature off)=False | true |  |
| C064 | README:314 | Contract Comparison needs a configured contract comparison | Contract Comparison: available(full)=True available(feature off)=False | true |  |
| C065 | README:315 | Power Headroom is unavailable until it can be computed | Power Headroom: available(full)=True available(feature off)=False | true |  |
| C066 | README:316 | DHW Setpoint Advisor is unavailable until there is a recommendation | DHW Setpoint Advisor: available(full)=True available(feature off)=False | true |  |
| C067 | README:317 | Mixed Hot Water is unavailable without mixed-water data | Mixed Hot Water: available(full)=True available(feature off)=False | true |  |
| C068 | README:318 | DHW Heavy Day Demand needs draw statistics | DHW Heavy Day Demand: available(full)=True available(feature off)=False | true |  |
| C069 | README:321 | Optimization Score is unavailable until the scores have evidence | Optimization Score: available(full)=True available(feature off)=False | true |  |
| C070 | README:323 | Compressor Frequency Advisor needs a compressor frequency entity | Compressor Frequency Advisor: available(full)=True available(feature off)=False | true |  |
| C071 | README:253-254 | every entity exists on a bare payload (unconfigured features report unavailable, not absent) | observed=55 expected=55 | true |  |
| C072 | README:342 | Optimize Now is unavailable while a run is in flight | observed=[False] expected=[False] | true |  |
| C073 | README:343 / coordinator.py:10538 | Run System Identification: arming reads the sysid option, off by default | DEFAULT_SYSID_ENABLED=False; arm() re-reads the option | true |  |
| C074 | README:285 | Heat Pump Action values are off, eco, normal, pre_heat, boost (+ comfort while comfort mode holds) | all six mode strings present in the mode mapper | true |  |
| C075 | README:349-350 | Optimizer Active turning on only acts from off | observed=([], ['auto']) expected=([], ['auto']) | true |  |
| C076 | README:352-353 | climate HVAC modes are off, heat, auto and presets auto, comfort, economy, boost | observed=(['auto', 'heat', 'off'], ['auto', 'comfort', 'economy', 'boost']) expected=(['auto', 'heat', 'off'], ['auto', 'comfort', 'economy', 'boost']) | true |  |
| C077 | README:354-355 | setting the climate target records a comfort-weight observation | pressed=['override:21.5'] target=21.5 | true |  |
| C078 | README:352 | the climate target is the comfort target (coordinator.target_temperature), not the per-step setpoint | observed=21.0 expected=21.0 | true |  |
| C080 | README:389 / configuration.md:535 / architecture.md | eleven services are registered | observed=11 expected=11 | true |  |
| C081 | README:395-405 | the README service table lists exactly the registered services | observed=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'diagnose_interval', 'restore_learned_snapshot', 'run_optimization', 'set_mode', 'set_thermal_parameters', 'simulat | true |  |
| C082 | services.yaml | services.yaml describes exactly the registered services | observed=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'diagnose_interval', 'restore_learned_snapshot', 'run_optimization', 'set_mode', 'set_thermal_parameters', 'simulat | true |  |
| C083 | README:390 / configuration.md:547,565 | set_thermal_parameters has 28 fields | observed=28 expected=28 | true |  |
| C084 | configuration.md:548,592-595 | simulate_plan has 11 optional fields | observed=(11, True) expected=(11, True) | true |  |
| C085 | configuration.md:549,600 | apply_schedule has 5 schedule fields + entry_id | observed=['comfort_temp_day', 'day_end_hour', 'day_start_hour', 'dhw_min_temperature', 'dhw_windows', 'entry_id'] expected=['comfort_temp_day', 'day_end_hour', 'day_start_hour', 'dhw_min_temperature', 'dhw_windows', 'ent | true |  |
| C086 | configuration.md:535-541 | seven services accept entry_id; the other four act on every entry | observed=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'diagnose_interval', 'restore_learned_snapshot'] expected=['apply_manual_plan', 'apply_schedule', 'apply_topology', | true |  |
| C087 | README Returns column / configuration.md:543-555 | Returns: simulate_plan always, run/set_mode/set_thermal none, the rest optional | README Returns column vs supports_response: mismatches={} | true |  |
| C088 | README:396 / services.yaml set_mode / const.OPERATION_MODES | set_mode accepts auto, comfort, economy, boost, off | observed=(['auto', 'boost', 'comfort', 'economy', 'off'], ['auto', 'boost', 'comfort', 'economy', 'off'], True, False) expected=(['auto', 'boost', 'comfort', 'economy', 'off'], ['auto', 'boost', 'comfort', 'economy', 'of | true |  |
| C089 | services.yaml fields | every services.yaml field is a schema key and vice versa | field sets agree for all services; mismatches={} | true |  |
| C090 | services.yaml required: | the required flags match vol.Required in the schemas | required flags agree; mismatches=[] | true |  |
| C091 | services.yaml examples | every services.yaml example validates through its voluptuous schema | 35 examples validated; rejected=[] | true |  |
| C092 | services.yaml selectors | every number selector's min and max are accepted by the schema | 39 number selectors; bounds rejected by schema: [('set_thermal_parameters', 'inter_zone_heat_transfer', 'min', 0.0), ('set_thermal_parameters', 'window_area', 'min', 0)] | false | selector bound outside schema: [('set_thermal_parameters', 'inter_zone_heat_transfer', 'min', 0.0), ('set_thermal_parameters', 'window_area', 'min', 0)] |
| C093 | services.yaml wind_sensitivity_factor (example 0.15, '0.15 means 15% more heat loss per m/s') | the wind example/description matches the shipped default | observed=0.15 expected=0.03 | stale | default is 0.03 (3 %/m/s) since the 0.15 default was replaced; the example still shows the old value |
| C094 | configuration.md:571-588 | the 25 documented set_thermal_parameters ranges are the schema's bounds | 25 documented ranges checked at both bounds; wrong=[] | true |  |
| C095 | configuration.md:607-616 | assign_entity accepts exactly the 21 documented keys | observed=['buffer_tank_temp_entity', 'dhw_temp_entity', 'external_heat_entity', 'floor_return_temp_entity', 'heat_pump_defrost_entity', 'heat_pump_energy_entity', 'heat_pump_fault_entity', 'heat_pump_mode_entity', 'heat_ | true |  |
| C096 | configuration.md:523-529,622 | four selectable layouts; slab_shunt is recorded but not selectable | observed=(['no_valve', 'single_tank_valve', 'two_tank_4way', 'valve_upper_direct_slab'], True, False) expected=(['no_valve', 'single_tank_valve', 'two_tank_4way', 'valve_upper_direct_slab'], True, False) | true |  |
| C097 | README:400 / services.yaml apply_manual_plan / const.py | manual plans pin up to 20 hours | observed=20 expected=20 | true |  |
| C098 | README:411-413 | apply_manual_plan: an omitted channel stays automatic, an explicit [] arrives as [] | observed=('absent', []) expected=('absent', []) | true |  |
| C099 | services.yaml set_mode economy / configuration.md:561-562 | economy widens the floor by 1.5 K, never below 15 °C | observed=(1.5, 15.0) expected=(1.5, 15.0) | true |  |
| C100 | README:398 / const.py:482 | simulate_plan is rate-limited (3 s minimum interval) | observed=3.0 expected=3.0 | true |  |
| C101 | configuration.md:594 | simulate_plan day_start_hour 0–23 and day_end_hour 0–24 | observed=(True, False, True, False) expected=(True, False, True, False) | true |  |
| C102 | strings.json | strings.json carries no services section (service names come from services.yaml) | observed=False expected=False | true |  |
| C110 | README:192 / configuration.md:79 | target 21 °C | observed=21.0 expected=21.0 | true |  |
| C111 | configuration.md:80-81 | min 19 / max 23 °C | observed=(19.0, 23.0) expected=(19.0, 23.0) | true |  |
| C112 | README:193 / configuration.md:82-83 | day 21 °C, night 19.5 °C | observed=(21.0, 19.5) expected=(21.0, 19.5) | true |  |
| C113 | README:194 / configuration.md:84-85 | day runs 07:00–22:00 | observed=(7, 22) expected=(7, 22) | true |  |
| C114 | README:218 / configuration.md:173 | DHW windows default 06:00-08:30, 17:00-22:00 | observed='06:00-08:30, 17:00-22:00' expected='06:00-08:30, 17:00-22:00' | true |  |
| C115 | README:222 / how-it-works.md:575 | anti-legionella on by default, 60 °C every 7 days | observed=(True, 60.0, 7.0) expected=(True, 60.0, 7.0) | true |  |
| C116 | README:227 / configuration.md:183-184 / how-it-works.md:291-295 | wind 3 %/(m/s), rain +15 % | observed=(0.03, 1.15) expected=(0.03, 1.15) | true |  |
| C117 | README:235,431 / how-it-works.md:47 | optimization interval 30 min | observed=30 expected=30 | true |  |
| C118 | README:526 / configuration.md:136 / how-it-works.md:130 | comfort_weight default 5, price weight 1.0 | observed=(5.0, 1.0) expected=(5.0, 1.0) | true |  |
| C119 | README:49,86 / architecture.md / how-it-works.md:1154 | weekly snapshots, last 8 kept | observed=(8, 7.0) expected=(8, 7.0) | true |  |
| C120 | how-it-works.md:1157 | drift alarm after five consecutive days out of band | observed=5 expected=5 | true |  |
| C121 | how-it-works.md:1176 | the CUSUM statistic is capped at 1.5× the threshold | observed=1.5 expected=1.5 | true |  |
| C122 | README:85 / configuration.md:453 / ecl110.md:39 / how-it-works.md:1117 | heat-curve correction cool-only, at most 0.5 K per week, clamped [−4, 0] | observed=(0.5, -4.0, 0.0) expected=(0.5, -4.0, 0.0) | true |  |
| C123 | README:368 / configuration.md:341 | frequency control writes at most once per five minutes | observed=300.0 expected=300.0 | true |  |
| C124 | README:369 / configuration.md:341 | three divergent ticks stand the controller down | observed=3 expected=3 | true |  |
| C125 | README:444,478 / how-it-works.md:78,758 | peak guard: two agreeing samples engage, two clear | observed=2 expected=2 | true |  |
| C126 | configuration.md:167-170 / how-it-works.md:439 | DHW tank 200 L, setpoint 55, minimum 45, 150 L/day | observed=(200.0, 55.0, 45.0, 150.0) expected=(200.0, 55.0, 45.0, 150.0) | true |  |
| C127 | configuration.md:171,174 / how-it-works.md:543,557 | tank cooling 0.3 °C/h clamped 0.05–3.0; idle minimum 20 °C | observed=(0.3, 0.05, 3.0, 20.0) expected=(0.3, 0.05, 3.0, 20.0) | true |  |
| C128 | configuration.md:169 | the DHW minimum must sit 5 °C below the setpoint | observed=5.0 expected=5.0 | true |  |
| C129 | configuration.md:127-133 / how-it-works.md:276 | house 10 kWh/°C, 0.15 kW/°C, slab 5 / 0.8, COP 3.5, 5 kW / 1 kW | observed=(10.0, 0.15, 5.0, 0.8, 3.5, 5.0, 1.0) expected=(10.0, 0.15, 5.0, 0.8, 3.5, 5.0, 1.0) | true |  |
| C130 | configuration.md:142-149 / how-it-works.md:274-276 | two-zone 3/8 kWh/°C, 0.08/0.07 kW/°C, 0.5 inter-zone, 0.4 radiator share, 0.5 area ratio, 35 L buffer | observed=(3.0, 8.0, 0.08, 0.07, 0.5, 0.4, 0.5, 35.0) expected=(3.0, 8.0, 0.08, 0.07, 0.5, 0.4, 0.5, 35.0) | true |  |
| C131 | configuration.md:150-152 / how-it-works.md:310-313 | solar: 10 m², orientation 0.7, SHGC 0.7, 40 % upper | observed=(10.0, 0.7, 0.7, 0.4) expected=(10.0, 0.7, 0.7, 0.4) | true |  |
| C132 | configuration.md:149,355-356 / how-it-works.md:419 | buffer store threshold 100 L, max buffer temperature 70 °C | observed=(100.0, 70.0) expected=(100.0, 70.0) | true |  |
| C133 | configuration.md:285-287 | capacity tariff 45 per kW, 3 peaks, 60-minute window, off by default | observed=(45.0, 3, 60, False) expected=(45.0, 3, 60, False) | true |  |
| C134 | configuration.md:292-296 | main fuse 0 A (unconfigured), 3 phases, guards off, margin 0.5 kW | observed=(0, 3, False, False, 0.5) expected=(0, 3, False, False, 0.5) | true |  |
| C135 | configuration.md:314-318 | away mode off, 16 °C, DHW minimum 20 °C | observed=(False, 16.0, 20.0) expected=(False, 16.0, 20.0) | true |  |
| C136 | configuration.md:438-441 | external heat detection off, 1.5 °C/h, 90 min decay | observed=(False, 1.5, 90.0) expected=(False, 1.5, 90.0) | true |  |
| C137 | configuration.md:445 / how-it-works.md:771-773 | outage: gap > 90 min, 2-hour recovery, hot water queues 45 min | observed=(90.0, 2.0, 45.0, False) expected=(90.0, 2.0, 45.0, False) | true |  |
| C138 | configuration.md:232-234,270 / how-it-works.md:1137,1143 | confidence margin cap 0.8 °C; mould guard 80 % RH, fRsi 0.75 | observed=(0.8, 0.8, 0.75, False) expected=(0.8, 0.8, 0.75, False) | true |  |
| C139 | configuration.md:446,450-451 / how-it-works.md:1114-1115,1128 | open-window relax 1 °C; capacity floor 60 %; solar aperture [0.3, 2.0] | observed=(1.0, 0.6, 0.3, 2.0) expected=(1.0, 0.6, 0.3, 2.0) | true |  |
| C140 | configuration.md:449 / how-it-works.md:301 | snow halves solar gain for two days | observed=(0.5, 2.0) expected=(0.5, 2.0) | true |  |
| C141 | configuration.md:268,271-273 | cycling cost 0, replacement cost 0, rated starts 100 000, wear autotune off | observed=(0.0, 0.0, 100000, False) expected=(0.0, 0.0, 100000, False) | true |  |
| C142 | configuration.md:421-424 | PV off, 0 kWp, efficiency 0.80, export price 0 | observed=(False, 0.0, 0.8, 0.0) expected=(False, 0.0, 0.8, 0.0) | true |  |
| C143 | configuration.md:243-253 / how-it-works.md:534,587,612 | inlet 10 °C, amplitude 0, greywater 0, legionella min interval 5 d, shower 8 L/min, VVC lead 20 min | observed=(10.0, 0.0, 0.0, 5.0, 8.0, 20) expected=(10.0, 0.0, 0.0, 5.0, 8.0, 20) | true |  |
| C144 | how-it-works.md:988,1047 | COP scale bounded [0.5, 1.6]; tracking-error gate 30 % | observed=(0.5, 1.6, 0.3) expected=(0.5, 1.6, 0.3) | true |  |
| C145 | configuration.md:436-437 / how-it-works.md:909-910 | staleness on by default, slack 0.5–10; ages 60 indoor/tank, 180 outdoor, 30 power | observed=(True, 0.5, 10.0) expected=(True, 0.5, 10.0) | true |  |
| C146 | configuration.md:444 | price prior on by default | observed=True expected=True | true |  |
| C147 | configuration.md:442-443 / README:239 | comfort learning and system identification off by default | observed=(False, False) expected=(False, False) | true |  |
| C148 | ecl110.md:83-90 / configuration.md:462-469 | ECL110 defaults: set/command/state topics, QoS 1, retain off, ±20, 1.5 h | observed=('ecl110/flow_temp_control/displace/set', 'ecl110/command', 'ecl110/flow_temp_control/displace', 1, False, -20.0, 20.0, 1.5) expected=('ecl110/flow_temp_control/displace/set', 'ecl110/command', 'ecl110/flow_temp | true |  |
| C149 | ecl110.md:33-35 | the peak guard lowers the displace by 2 °C while suppressing | observed=2.0 expected=2.0 | true |  |
| C150 | how-it-works.md:827,850 / README:98 | external heat promised at most two hours ahead; wood tank settled up to 95 °C | observed=(2.0, 95.0) expected=(2.0, 95.0) | true |  |
| C151 | how-it-works.md:686-687 | price shape damped below five days, factors guard-railed to [0.2, 3.0] | observed=(5, 0.2, 3.0) expected=(5, 0.2, 3.0) | true |  |
| C152 | how-it-works.md:1007,1025 | defrost derate = 1 − duty × 1.5, clamped at 1.0 | observed=(1.5, 1.0) expected=(1.5, 1.0) | true |  |
| C153 | how-it-works.md:706 | a fee component above 10 SEK/kWh is flagged | observed=10.0 expected=10.0 | true |  |
| C154 | how-it-works.md:886-888 | recovery starts a full duration plus an hour before return, capped at 24 h | observed=(1.0, 24.0) expected=(1.0, 24.0) | true |  |
| C155 | how-it-works.md:97 / optimizer.py:91 | the congestion premium searches a 6-hour window | observed=6.0 expected=6.0 | true |  |
| C156 | how-it-works.md:108-110 | the space solve keeps two starts | observed=2 expected=2 | true |  |
| C159 | configuration.md:632-633 / how-it-works.md:585 / const.py:636 | legionella credit is hold-verified (20 minutes) | observed=20.0 expected=20.0 | true |  |
| C160 | README:99 / const.py:225 | the DHW coil is off by default with a fixed 0.5 effectiveness | observed=(False, 0.5) expected=(False, 0.5) | true |  |
| C157 | how-it-works.md:48,72 | 24-hour horizon on a 15-minute grid | observed=(24.0, 15.0, 96) expected=(24.0, 15.0, 96) | true |  |
| C158 | how-it-works.md:598-601 / README:106 | heavy-day target is the 90th percentile per window | observed=0.9 expected=0.9 | true |  |
| C161 | how-it-works.md:909-910 | input ages: indoor 60, DHW 60, outdoor 180, power 30 minutes | observed=(60.0, 60.0, 180.0, 30.0) expected=(60.0, 60.0, 180.0, 30.0) | true |  |
| C170 | README:368-371 | the watchdog trips on the third consecutive active divergent tick; idle ticks are not divergence | trip sequence=[False, False, False, True] (grace, strike, strike, trip); idle tick reset strikes 2->0 | true |  |
| C171 | README:444,478 / how-it-works.md:758 | the peak guard engages on the second crossing sample and releases on the second clear one | observed=[False, True, True, False] expected=[False, True, True, False] | true |  |
| C172 | README:85 / how-it-works.md:1117 | the curve bias moves at most 0.5 K per week and resets to 0 on a comfort miss | bias after 7 comfortable days=-0.40 K (≥ −0.5); after one miss=0.0 resets=1 | true |  |
| C173 | README:86 / how-it-works.md:1154 | the snapshot ring keeps the last eight | observed=(8, 11) expected=(8, 11) | true |  |
| C174 | README:389 / architecture.md | 13 options pages: 6 on the first menu and 7 behind Advanced settings, one read-only | observed=(13, 6, 7, []) expected=(13, 6, 7, []) | true |  |
| C175 | README:500-517 / configuration.md:200-217 | the README/configuration page names are the menu labels | observed=['Away and holiday mode', 'Building type and emitters', 'Comfort and temperatures', 'Grid costs', 'Heat curve control (ECL110)', 'Heating system and heat storage', 'Hot water', 'Savings vs comfort', 'Self-learni | true |  |
| C176 | ecl110.md:76 / configuration.md:68 | all eight ECL110 settings live on the Heat curve page | observed=8 expected=8 | true |  |
| C177 | configuration.md:322-325 | Sensors and entities has 22 fields | observed=22 expected=22 | true |  |
| C178 | configuration.md:227-228 | Comfort and temperatures has the seven setup fields plus three more (10) | observed=10 expected=10 | true |  |
| C179 | configuration.md:238-239 | Hot water has the eleven setup fields plus twelve more (23) | observed=23 expected=23 | true |  |
| C180 | configuration.md:13,51-52 / README:185 | only the Tibber token and the weather entity are required without a default | observed=['tibber_token', 'weather_entity'] expected=['tibber_token', 'weather_entity'] | true |  |
| C181 | configuration.md:68-70 / README:603 / ecl110.md:77 | no ECL110 field is asked at initial setup | observed=[] expected=[] | true |  |
| C182 | configuration.md:77-85 | temperature ranges: target 15–28/0.5, min 14–25, max 18–28, day 16–26, night 15–24, start 0–12, end 18–23 | {'target_temperature': {'setup:temperature': (15, 28, 0.5), 'options:comfort': (15, 28, 0.5)}, 'min_temperature': {'setup:temperature': (14, 25, 0.5), 'options:comfort': (14, 25, 0.5)}, 'max_temperature': {'setup:tempera | true |  |
| C183 | configuration.md:104 | heated_area_m2 range 20–1000 step 5 | heated_area_m2: {'setup:building_describe': (20, 1000, 5), 'options:building_preset': (20, 1000, 5)} | true |  |
| C184 | configuration.md:112-114 | heat_pump_cop_nominal range 1.5–6.0 step 0.1 | heat_pump_cop_nominal: {'setup:building_extras': (1.5, 6.0, 0.1), 'setup:thermal': (1.5, 6.0, 0.1), 'options:thermal_model': (1.5, 6.0, 0.1)} | true |  |
| C185 | configuration.md:113 | heat_pump_max_power range 1–20 step 0.5 | heat_pump_max_power: {'setup:building_extras': (1, 20, 0.5), 'setup:thermal': (1, 20, 0.5), 'options:thermal_model': (1, 20, 0.5)} | true |  |
| C186 | configuration.md:114 | heat_pump_min_power range 0–10 step 0.5 | heat_pump_min_power: {'setup:building_extras': (0, 10, 0.5), 'setup:thermal': (0, 10, 0.5), 'options:thermal_model': (0, 10, 0.5)} | true |  |
| C187 | configuration.md:127 | house_thermal_mass range 0.5–80 step 0.5 | house_thermal_mass: {'setup:thermal': (0.5, 80.0, 0.5), 'options:thermal_model': (0.5, 80.0, 0.5)} | true |  |
| C188 | configuration.md:128 | house_heat_loss_coefficient range 0.01–1.0 step 0.01 | house_heat_loss_coefficient: {'setup:thermal': (0.01, 1.0, 0.01), 'options:thermal_model': (0.01, 1.0, 0.01)} | true |  |
| C189 | configuration.md:129 | slab_thermal_mass range 0.1–60 step 0.5 | slab_thermal_mass: {'setup:thermal': (0.1, 60.0, 0.5), 'options:thermal_model': (0.1, 60.0, 0.5)} | true |  |
| C190 | configuration.md:130 | slab_heat_transfer range 0.02–5.0 step 0.1 | slab_heat_transfer: {'setup:thermal': (0.02, 5.0, 0.1), 'options:thermal_model': (0.02, 5.0, 0.1)} | true |  |
| C191 | configuration.md:134,267 | optimization_interval range 10–120 step 5 | optimization_interval: {'setup:thermal': (10, 120, 5), 'options:tuning': (10, 120, 5)} | true |  |
| C192 | configuration.md:135,265 | price_weight range 0.1–10 step 0.1 | price_weight: {'setup:thermal': (0.1, 10, 0.1), 'options:tuning': (0.1, 10, 0.1)} | true |  |
| C193 | configuration.md:136,266 | comfort_weight range 0.1–20 step 0.1 | comfort_weight: {'setup:thermal': (0.1, 20, 0.1), 'options:tuning': (0.1, 20, 0.1)} | true |  |
| C194 | configuration.md:142-143 | upper_floor_thermal_mass range 0.25–60 | upper_floor_thermal_mass: {'setup:zones': (0.25, 60.0, 0.5), 'options:thermal_model': (0.25, 60.0, 0.5)} | true |  |
| C195 | configuration.md:144-145 | upper_floor_heat_loss range 0.001–1.0 | upper_floor_heat_loss: {'setup:zones': (0.001, 1.0, 0.01), 'options:thermal_model': (0.001, 1.0, 0.01)} | true |  |
| C196 | configuration.md:146 | inter_zone_heat_transfer range 0.0–3.0 | inter_zone_heat_transfer: {'setup:zones': (0.0, 3.0, 0.1), 'options:thermal_model': (0.0, 3.0, 0.1)} | true |  |
| C197 | configuration.md:147 | radiator_power_fraction range 0.0–1.0 step 0.05 | radiator_power_fraction: {'setup:zones': (0.0, 1.0, 0.05), 'options:thermal_model': (0.0, 1.0, 0.05)} | true |  |
| C198 | configuration.md:148 | upper_floor_area_ratio range 0.1–0.9 | upper_floor_area_ratio: {'setup:zones': (0.1, 0.9, 0.05), 'options:thermal_model': (0.1, 0.9, 0.05)} | true |  |
| C199 | configuration.md:149,355 | buffer_tank_volume range 10–1500 step 5 | buffer_tank_volume: {'setup:zones': (10, 1500, 5), 'options:building': (10, 1500, 5)} | true |  |
| C200 | configuration.md:150,373 | window_area range 0–50 step 0.5 | window_area: {'setup:zones': (0, 50, 0.5), 'options:building_preset': (0, 50, 0.5)} | true |  |
| C201 | configuration.md:151 | solar_orientation_factor range 0.0–1.0 | solar_orientation_factor: {'setup:zones': (0.0, 1.0, 0.05), 'options:thermal_model': (0.0, 1.0, 0.05)} | true |  |
| C202 | configuration.md:152,374 | solar_heat_gain_coefficient range 0.1–1.0 | solar_heat_gain_coefficient: {'setup:zones': (0.1, 1.0, 0.05), 'options:building_preset': (0.1, 1.0, 0.05)} | true |  |
| C203 | configuration.md:167 | dhw_tank_volume range 50–1500 step 10 | dhw_tank_volume: {'setup:dhw': (50, 1500, 10), 'options:hot_water': (50, 1500, 10)} | true |  |
| C204 | configuration.md:168 | dhw_setpoint range 40–65 | dhw_setpoint: {'setup:dhw': (40, 65, 1), 'options:hot_water': (40, 65, 1)} | true |  |
| C205 | configuration.md:169 | dhw_min_temperature range 35–55 | dhw_min_temperature: {'setup:dhw': (35, 55, 1), 'options:hot_water': (35, 55, 1)} | true |  |
| C206 | configuration.md:170 | dhw_daily_consumption range 50–1500 | dhw_daily_consumption: {'setup:dhw': (50, 1500, 10), 'options:hot_water': (50, 1500, 10)} | true |  |
| C207 | configuration.md:171 | dhw_cooling_rate range 0.05–3.0 step 0.05 | dhw_cooling_rate: {'setup:dhw': (0.05, 3.0, 0.05), 'options:hot_water': (0.05, 3.0, 0.05)} | true |  |
| C208 | configuration.md:174 | dhw_idle_min_temperature range 10–55 | dhw_idle_min_temperature: {'setup:dhw': (10, 55, 1), 'options:hot_water': (10, 55, 1)} | true |  |
| C209 | configuration.md:176 | dhw_legionella_temperature range 55–70 | dhw_legionella_temperature: {'setup:dhw': (55, 70, 1), 'options:hot_water': (55, 70, 1)} | true |  |
| C210 | configuration.md:177 | dhw_legionella_interval_days range 1–30 | dhw_legionella_interval_days: {'setup:dhw': (1, 30, 1), 'options:hot_water': (1, 30, 1)} | true |  |
| C211 | configuration.md:183,375 | wind_sensitivity_factor range 0.0–0.5 step 0.01 | wind_sensitivity_factor: {'setup:weather_sensitivity': (0.0, 0.5, 0.01), 'options:building_preset': (0.0, 0.5, 0.01)} | true |  |
| C212 | configuration.md:184,376 | rain_heat_loss_multiplier range 1.0–1.5 step 0.01 | rain_heat_loss_multiplier: {'setup:weather_sensitivity': (1.0, 1.5, 0.01), 'options:building_preset': (1.0, 1.5, 0.01)} | true |  |
| C213 | configuration.md:234 | thermal_bridge_frsi range 0.3–0.98 step 0.01 | thermal_bridge_frsi: {'options:comfort': (0.3, 0.98, 0.01)} | true |  |
| C214 | configuration.md:243-244 | dhw_inlet_temp range 2–25 step 0.5 | dhw_inlet_temp: {'options:hot_water': (2, 25, 0.5)} | true |  |
| C215 | configuration.md:244 | dhw_inlet_seasonal_amplitude range 0–8 step 0.5 | dhw_inlet_seasonal_amplitude: {'options:hot_water': (0, 8, 0.5)} | true |  |
| C216 | configuration.md:246 | greywater_recovery_effectiveness range 0–0.9 step 0.05 | greywater_recovery_effectiveness: {'options:hot_water': (0, 0.9, 0.05)} | true |  |
| C217 | configuration.md:250 | dhw_legionella_min_interval_days range 1–14 | dhw_legionella_min_interval_days: {'options:hot_water': (1, 14, 1)} | true |  |
| C218 | configuration.md:251 | shower_flow_lpm range 4–20 step 0.5 | shower_flow_lpm: {'options:hot_water': (4, 20, 0.5)} | true |  |
| C219 | configuration.md:253 | vvc_lead_minutes range 0–120 step 5 | vvc_lead_minutes: {'options:hot_water': (0, 120, 5)} | true |  |
| C220 | configuration.md:268 | compressor_cycling_cost range 0–10 step 0.05 | compressor_cycling_cost: {'options:tuning': (0, 10, 0.05)} | true |  |
| C221 | configuration.md:269 | price_risk_lambda range 0.0–2.0 step 0.05 | price_risk_lambda: {'options:tuning': (0.0, 2.0, 0.05)} | true |  |
| C222 | configuration.md:271 | compressor_replacement_cost range 0–100000 step 100 | compressor_replacement_cost: {'options:tuning': (0, 100000, 100)} | true |  |
| C223 | configuration.md:272 | compressor_rated_starts range 1000–1000000 | compressor_rated_starts: {'options:tuning': (1000, 1000000, 1000)} | true |  |
| C224 | configuration.md:285 | peak_tariff_price_per_kw range 0–500 | peak_tariff_price_per_kw: {'options:grid': (0, 500, 1)} | true |  |
| C225 | configuration.md:286 | peak_tariff_peaks_averaged range 1–10 | peak_tariff_peaks_averaged: {'options:grid': (1, 10, 1)} | true |  |
| C226 | configuration.md:291 | peak_tariff_offpeak_factor range 0.0–1.0 step 0.05 | peak_tariff_offpeak_factor: {'options:grid': (0.0, 1.0, 0.05)} | true |  |
| C227 | configuration.md:292 | main_fuse_amperes range 0–125 | main_fuse_amperes: {'options:grid': (0, 125, 1)} | true |  |
| C228 | configuration.md:293 | main_fuse_phases range 1–3 | main_fuse_phases: {'options:grid': (1, 3, 1)} | true |  |
| C229 | configuration.md:296 | peak_guard_margin_kw range 0.0–3.0 step 0.1 | peak_guard_margin_kw: {'options:grid': (0.0, 3.0, 0.1)} | true |  |
| C230 | configuration.md:298 | grid_fee_fixed range 0–5 step 0.01 | grid_fee_fixed: {'options:grid': (0, 5, 0.01)} | true |  |
| C231 | configuration.md:301 | contract_fixed_price range 0–10 step 0.01 | contract_fixed_price: {'options:grid': (0, 10, 0.01)} | true |  |
| C232 | configuration.md:317 | away_temperature range 5–21 step 0.5 | away_temperature: {'options:away': (5, 21, 0.5)} | true |  |
| C233 | configuration.md:318 | away_dhw_min_temperature range 10–55 | away_dhw_min_temperature: {'options:away': (10, 55, 1)} | true |  |
| C234 | configuration.md:352 | mixing_valve_target range 0–30 step 0.5 | mixing_valve_target: {'options:building': (0, 30, 0.5)} | true |  |
| C235 | configuration.md:356 | buffer_max_temperature range 40–90 | buffer_max_temperature: {'options:building': (40, 90, 1)} | true |  |
| C236 | configuration.md:360 | wood_tank_volume range 50–3000 step 50 | wood_tank_volume: {'options:building': (50, 3000, 50)} | true |  |
| C237 | configuration.md:422 | pv_peak_kw range 0–100 step 0.1 | pv_peak_kw: {'options:solar_pv': (0, 100, 0.1)} | true |  |
| C238 | configuration.md:423 | pv_system_efficiency range 0.3–1.0 step 0.01 | pv_system_efficiency: {'options:solar_pv': (0.3, 1.0, 0.01)} | true |  |
| C239 | configuration.md:424 | pv_export_price range 0–10 step 0.01 | pv_export_price: {'options:solar_pv': (0, 10, 0.01)} | true |  |
| C240 | configuration.md:437 | staleness_max_age_scale range 0.5–10.0 step 0.5 | staleness_max_age_scale: {'options:learning': (0.5, 10.0, 0.5)} | true |  |
| C241 | configuration.md:440 | external_heat_min_rise range 0.5–10 step 0.1 | external_heat_min_rise: {'options:learning': (0.5, 10, 0.1)} | true |  |
| C242 | configuration.md:441 | external_heat_decay_minutes range 15–360 step 15 | external_heat_decay_minutes: {'options:learning': (15, 360, 15)} | true |  |
| C243 | configuration.md:465-469 / ecl110.md:87-90 | ecl110_mqtt_qos range 0–2 step 1 | ecl110_mqtt_qos: {'options:heat_curve': (0, 2, 1)} | true |  |
| C244 | configuration.md:467 / ecl110.md:88 | ecl110_displace_min range -30–0 step 0.5 | ecl110_displace_min: {'options:heat_curve': (-30, 0, 0.5)} | true |  |
| C245 | configuration.md:468 / ecl110.md:89 | ecl110_displace_max range 0–30 step 0.5 | ecl110_displace_max: {'options:heat_curve': (0, 30, 0.5)} | true |  |
| C246 | configuration.md:469 / ecl110.md:90 | ecl110_pid_time_constant_hours range 0.25–6.0 step 0.25 | ecl110_pid_time_constant_hours: {'options:heat_curve': (0.25, 6.0, 0.25)} | true |  |
| C250 | ecl110.md:17-18 / optimizer.py:5568 | heat_pump_on threshold is half the modulation floor, at least 0.1 kW | optimizer.py: max(0.1, p.min_electrical_power * 0.5) | true |  |
| C251 | ecl110.md:22-25 / optimizer.py:5541 | the anticipation bias applies over the first eight hours of the displace schedule | optimizer.py: i < 8 / dt_hours | true |  |
| C252 | ecl110.md:27-30 / coordinator.py:6357 | the published displace is rounded to a whole number | coordinator.py: int(round(displace)) | true |  |
| C253 | ecl110.md:31-32 / coordinator.py:4379-4395 | comfort commands +4 °C (or the maximum), boost the maximum, off the minimum | coordinator.py fixed-mode displace values | true |  |
| C254 | how-it-works.md:324-329 / thermal_model.py:2833-2836 | T_slab = 0.7 × (T_return + 1 °C) + 0.3 × T_slab_model | thermal_model.py update_slab_from_return_temp | true |  |
| C255 | how-it-works.md:491-493 | the floor repair is bounded at 48 rounds | optimizer.py: range(48) | true |  |
| C256 | how-it-works.md:503 | the tank is never planned above min(70 °C, max(setpoint, legionella)) | optimizer.py: boost_top = min(70.0, dhw_hard_max_temp) | true |  |
| C257 | how-it-works.md:634-641 / README:457-460 | irradiance precedence: local sensor, then Open-Meteo, else the weather entity | coordinator.py: sensor wins, Open-Meteo fills, weather forecast is the default source | true |  |
| C258 | how-it-works.md:989 | a COP sample only counts above a third of nameplate | coordinator.py: floor = max(0.3 × nameplate, 0.2 kW) | true |  |
| C259 | how-it-works.md:1094-1099 | sysid guards: gains −0.5..2.0 kW, tau 0.1–200 h, UA 0.01–5 | sysid.py bounds present | true |  |
| C260 | how-it-works.md:278-279 / thermal_model.py:935 | hot water activates when any of a DHW sensor, a tank volume or demand windows is configured | thermal_model.py: dhw_enabled = any(presence trio) | true |  |
| C261 | README:126-127 / how-it-works.md:906-907 | an over-age input is treated as missing and freezes the learners | coordinator publishes learners_frozen / learner_freeze_reason | true |  |
| C262 | dashboard-card.md:24-25 / architecture.md | the card is one self-contained file with no Chart.js/ApexCharts/CDN dependency | observed=(['heatpump-optimizer-card.js'], False) expected=(['heatpump-optimizer-card.js'], False) | true |  |
| C263 | dashboard-card.md:385,405 / frontend.py | the card is served at /heatpump_optimizer_static/heatpump-optimizer-card.js | observed='/heatpump_optimizer_static/heatpump-optimizer-card.js' expected='/heatpump_optimizer_static/heatpump-optimizer-card.js' | true |  |
| C264 | dashboard-card.md:153 | the chart is drawn in a fixed 900x380 coordinate system | VIEW_W=900 VIEW_H=380 | true |  |
| C265 | dashboard-card.md:141-143 | labelled gridlines snap to 1, 2, 3, 4, 6, 8, 12 or 24 hours | TIME_LABEL_STEPS present | true |  |
| C266 | dashboard-card.md:461,510 | hours must be > 0 and at most 168 | card rejects hours <= 0 or > 168 | true |  |
| C267 | dashboard-card.md:514 | series keys are price, dhw_slots, space_slots, outdoor, dhw_temp, house_temp, solar (seven) | observed=['dhw_slots', 'dhw_temp', 'house_temp', 'outdoor', 'price', 'solar', 'space_slots'] expected=['dhw_slots', 'dhw_temp', 'house_temp', 'outdoor', 'price', 'solar', 'space_slots'] | true |  |
| C268 | dashboard-card.md:108-109 | about 200 card strings in English and Swedish, with no Swedish entry missing | en=232 sv=232 en-only=[] sv-only=[] | true |  |
| C269 | dashboard-card.md:428-435 | the card prints its own version on load (CARD_VERSION, separate from the integration version) | CARD_VERSION=5.4.17 vs integration 6.2.14 | true |  |
| C270 | dashboard-card.md:207-209 / 527 | the card reads manual_plan_window_hours from the plan sensors and discovers them by plan_kind | both lookups present in the card | true |  |
| C271 | dashboard-card.md:541-543 | a pre-v4.2.0 localStorage key is still read as a fallback | storageKeyLegacy read present | true |  |
| C272 | README:552-554 / dashboard-card.md:272 | what_if: false hides the editor and the lanes | what_if option handled | true |  |
| C280 | architecture.md:8 | 45 modules | observed=45 expected=45 | true |  |
| C281 | architecture.md:8,99-102 | exactly ten modules import homeassistant at module level: __init__, config_flow, coordinator, open_meteo, frontend and the five platforms | observed=['__init__', 'binary_sensor', 'button', 'climate', 'config_flow', 'coordinator', 'frontend', 'open_meteo', 'sensor', 'switch'] expected=['__init__', 'binary_sensor', 'button', 'climate', 'config_flow', 'coordina | true |  |
| C282 | architecture.md:102-104 | inputs reaches for homeassistant.util.dt inside a function only | indented import present, no module-level one | true |  |
| C283 | architecture.md:66-140 | the module map names every module and nothing else | observed=([], []) expected=([], []) | true |  |
| C284 | architecture.md:70,138 / README:389 | __init__ registers 11 services; services.yaml has 11 definitions; config_flow has 13 option pages | observed=(11, 11, 13) expected=(11, 11, 13) | true |  |
| C290 | README:483-485 / how-it-works.md:1229-1231 | the learning test uses a house losing 35 % more heat (plant_error 1.35) over three days with a 4.25 kW pump | rolling.py constants present | true |  |
| C291 | how-it-works.md:1233-1240 | asserted: >10 samples, moves toward truth, overshoot ≤ 0.15, last-quarter spread < 0.05, correct model drift < 0.12 over two days | all five assertions present verbatim | true |  |
| C292 | how-it-works.md:1215-1227 | stability arm: 25 % model error, 5–35 °C, < 3 degree-hours, worst day < 1.6× best | rolling.py thresholds present | true |  |
| C293 | README:486-487 / how-it-works.md:1237-1238 | in the reference run the breach goes from 6.7 degree-hours to zero | breach_uncorrected=9.634 breach_learned=0.044 scale_end=1.3312 drift=0.0167 (re-executed on this box) | stale | re-executed numbers are 9.634 -> 0.044 degree-hours; the asserted property (learning cuts the breach) holds, the quoted figures do not reproduce |
| C294 | README:487-488 | a model that is already correct is left alone within ±12 % | rolling.py asserts drift < 0.12 (the README's ±12 %) | true |  |
| C295 | how-it-works.md:105-106 | hot water displaced 2.6–4.7 kWh of space heating without the premium (validation scenarios) | historical measurement / removed document; not re-measured in this round (would need a quiet-box harness) | unverifiable |  |
| C296 | how-it-works.md:110-112 | two starts were 2.2 % cheaper; a third bought 0.2 % | historical measurement / removed document; not re-measured in this round (would need a quiet-box harness) | unverifiable |  |
| C297 | how-it-works.md:142-147 | halving the target pull: 28.55 vs 23.28 SEK, 18 % of the bill, 0.32 K | historical measurement / removed document; not re-measured in this round (would need a quiet-box harness) | unverifiable |  |
| C298 | how-it-works.md:154-157,174 | the removed smoothness term cost ~5 %; removing anticipation terms made shoulder plans 4–6 % cheaper | historical measurement / removed document; not re-measured in this round (would need a quiet-box harness) | unverifiable |  |
| C299 | how-it-works.md:399-401 | a commanded valve is worth 1–2 SEK/day on the author's winter curve | historical measurement / removed document; not re-measured in this round (would need a quiet-box harness) | unverifiable |  |
| C300 | how-it-works.md:1252-1262 | comfort-weight table: 19.4 °C/53 % … 20.4 °C/47 % on the author's house | historical measurement / removed document; not re-measured in this round (would need a quiet-box harness) | unverifiable |  |
| C301 | README:610 / docs/backlog.md | backlog items 1–33 are all delivered | historical measurement / removed document; not re-measured in this round (would need a quiet-box harness) | unverifiable |  |
| C302 | dashboard-card.md:436-437 | v5.0.0 shipped card 4.3.0 unchanged | historical measurement / removed document; not re-measured in this round (would need a quiet-box harness) | unverifiable |  |
| C303 | README:271 | only the hot-water half of the savings baseline is always-on; the space half follows the comfort schedule | optimizer.py:4786 always-hot DHW baseline; optimizer.py:5177 space baseline tracks the per-step comfort targets | true |  |
| C304 | README:612-614 / plan-v4.0.0-program.md:1,11,155-1138 | 36 selected proposals delivered as tranches T0 through T8 | 36 proposals and T0..T8 headers present | true |  |
| C305 | DISCLAIMER.md:71-72 | the savings baseline is 'a simulated always-on thermostat' | optimizer.py:5177 'Simulate a conventional thermostat following the comfort schedule'; README:271 says only the hot-water half is always-on | stale | the space-heating baseline follows the comfort schedule (day/night targets); only the hot-water baseline is kept permanently hot |
| C306 | README:281 / const.py | irradiance sources: local sensor, Open-Meteo (opt-in), weather entity default | observed=('weather', ('weather', 'open_meteo')) expected=('weather', ('weather', 'open_meteo')) | true |  |
| C307 | README:76 / how-it-works.md:47 | the plan is re-solved every interval; first refresh skips the solve (README: first plan within one interval) | __init__.py sets _skip_solve_once before the first refresh | true |  |
| C308 | README:24 'Versions 2.3.0 onward were developed in this fork' | the fork point is upstream 2.2.0 | no upstream history in the export | unverifiable |  |

RESULT claims_extracted=273 count
RESULT claims_checked=263 count
RESULT claims_true=258 count
RESULT claims_false=1 count
RESULT claims_stale=4 count
RESULT claims_unverifiable=10 count
RESULT thread_factor=1.000
RESULT load1=1.86
RESULT swapins=0
