M11_migrate_no_place: suite=entities rc=1 last=Accuracy store: ignoring non-list 'samples' field (str); the other learned fields are unaffected
      FAIL a 7.1 entry migrates to 7.2: data holds DATA_ONLY alone, the effective mapping is unchanged and a key in both sides keeps the options value in force  [data={'name': 'Annex', 'tibber_token': 't', 'target_temperatur
      FAIL a3:roster  [1 registered, 82 in the committed collect() roster; missing=['binary_sensor.heat_pump_optimizer_away_mode', 'binary_sensor.heat_pump_optimizer_external_heat_source', 'binary_sensor.heat_pump_optimizer_
      FAIL a3:orjson  [1 failed HA json_bytes; first: ['sensor.x:ValueError:orjson rejects non-finite floats']]
      FAIL a3:finite  [1 non-finite; ['sensor.x.attributes.k=nan']]
      FAIL a3:device_class_state_class  [1 forbidden pair(s): ['sensor.x:energy+measurement']]
      FAIL a3:no_constructor_defaults  [1 constructor default(s) published as available: ['sensor.heat_pump_optimizer_indoor_temperature_optimizer:temperature=21.0']]
      FAIL a3:no_constructor_defaults  [1 constructor default(s) published as available: ['climate.heat_pump_optimizer.current_temperature=21.0']]
      FAIL a3:no_constructor_defaults  [3 constructor default(s) published as available: ['sensor.heat_pump_optimizer_dhw_temperature:temperature=55.0', "sensor.heat_pump_optimizer_dhw_mixed_water:available volume_storage='2
      FAIL a3:no_constructor_defaults  [empty sweep: no published states were judged]
      FAIL a4:bridged  [last_update_success=False price_feed_stale_raised=True unavailable=none]
      FAIL a4:bridged  [last_update_success=True price_feed_stale_raised=False unavailable=none]
      FAIL a4:bridged  [last_update_success=True price_feed_stale_raised=True unavailable=['button.b', 'sensor.a']]
