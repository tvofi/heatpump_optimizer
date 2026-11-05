import sys, json, inspect; sys.path[:0]=['tests','tests/hastub','tools/replay']
import export
d=export._doc
base_conf=export.entry_keys(*export.default_const_paths())
ID="sensor.zzz_probe"
ts="2026-01-15T00:00:00+00:00"
def go(name, options, extra=()):
    conf=base_conf|frozenset(extra)
    rows={"sensor.in":[[ts,"1",None,None]],ID:[[ts,"2",None,None]],"sensor.hpo_out":[[ts,"4",None,None]]}
    kw=dict(time_zone="UTC",window=(ts,"2026-01-16T00:00:00+00:00"),recorder_schema=48,
      entry={"entry_id":"01JX","data":{},"options":options},inputs=["sensor.in",ID],
      published=["sensor.hpo_out"],price_series_entity=None,states=rows)
    if 'conf' in inspect.signature(d.document).parameters: kw['conf']=conf
    raw=d.document(**kw)
    shaped={k:(('_DROP' if d._entry_shape(k,v) is d._DROP else 'kept')) for k,v in options.items()}
    try:
        s=d.seal(raw,conf); print('RESULT',name,shaped,'SEALED states',len(s['states']),'leak','zzz_probe' in json.dumps(s))
    except d.Refused as e: print('RESULT',name,shaped,'REFUSED',e)
go('scalar_id_under_entities_key_in_conf', {"zone_entities":ID}, ("zone_entities",))
go('scalar_id_under_entities_key_in_conf_plus_kept_role', {"zone_entities":ID, "outdoor_temp_entity":ID}, ("zone_entities",))
go('scalar_id_under_entities_key_in_conf_plus_later_role', {"zone_entities":ID, "zz_entity":ID}, ("zone_entities","zz_entity"))
k=[x for x in sorted(base_conf) if not x.endswith(('_entity','_entities')) and not d.SECRET_KEY.search(x)][0]
go(f'id_with_whitespace_under_kept_key[{k}]', {k:ID+" two words"})
go(f'id_with_whitespace_under_kept_key_plus_role[{k}]', {k:ID+" two words", "outdoor_temp_entity":ID})
