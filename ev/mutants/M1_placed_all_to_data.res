M1_placed_all_to_data: suite=config_flow_steps rc=1 last=RuntimeWarning: Enable tracemalloc to get the object allocation traceback
      FAIL a new token is written through, the entry reloads, reauth_successful  [{'type': 'abort', 'reason': 'reauth_successful'} token=brand-new-token reloaded=['reauth-1']]
      FAIL reconfigure after options save: the page prefills the value in force, the save takes effect, data holds DATA_ONLY alone  [done={'type': 'abort', 'reason': 'reconfigure_successful'} prefilled='sensor.running_indoor
      FAIL reconfigure with no options save: the page prefills the value in force, the save takes effect, data holds DATA_ONLY alone  [done={'type': 'abort', 'reason': 'reconfigure_successful'} prefilled='sensor.annex_indoor
      FAIL the created entry stores DATA_ONLY in data and every setting in options, the effective mapping unchanged  [data={'name': 'Annex pump', 'tibber_token': 't', 'target_temperature': 21.0} options={'tibber_token': 't',
      FAIL re-submitting this entry's own identity reconfigures it instead of aborting  [{'type': 'abort', 'reason': 'reconfigure_successful'} reloaded=['plant_a']]
      FAIL a rotated token is written through and the entry keeps its other settings  [{'type': 'abort', 'reason': 'reconfigure_successful'} token=tok-fresh reloaded=['plant_a']]
      FAIL a slot the user cleared is dropped, not silently kept  [{'type': 'abort', 'reason': 'reconfigure_successful'} indoor=None]
    7 of 608 checks FAILED
