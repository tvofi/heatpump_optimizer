import sys, json, inspect; sys.path[:0]=['tests','tests/hastub','tools/replay']
import export
d=export._doc
conf=export.entry_keys(*export.default_const_paths())
ID="sensor.zzz_probe"
ts="2026-01-15T00:00:00+00:00"
def go(name, options):
    rows={"sensor.in":[[ts,"1",None,None]],ID:[[ts,"2",None,None]],"sensor.hpo_out":[[ts,"4",None,None]]}
    kw=dict(time_zone="UTC",window=(ts,"2026-01-16T00:00:00+00:00"),recorder_schema=48,
      entry={"entry_id":"01JX","data":{},"options":options},inputs=["sensor.in",ID],
      published=["sensor.hpo_out"],price_series_entity=None,states=rows)
    if 'conf' in inspect.signature(d.document).parameters: kw['conf']=conf
    raw=d.document(**kw)
    try:
        s=d.seal(raw,conf); print('RESULT',name,'SEALED states',len(s['states']),'leak','zzz_probe' in json.dumps(s))
    except d.Refused as e: print('RESULT',name,'REFUSED',e)
keys=[x for x in sorted(conf) if not d.SECRET_KEY.search(x)]
for key in keys[:3]:
    go(f'list_under_conf_key[{key}]', {key:["abc",ID]})
go('entity_key_off_list', {"legacy_probe_entity":ID})
go('entities_list_off_list', {"room_sensor_entities":["",ID]})
drop=[k for k in keys if d._entry_shape(k, ID) is d._DROP]
print('RESULT conf keys', len(conf), 'non-secret', len(keys), '_entry_shape(key, id) is _DROP for', len(drop))
for key in drop:
    go(f'drop_shaped_id_under_conf_key[{key}]', {key:ID})
    go(f'drop_shaped_id_under_conf_key_plus_role[{key}]', {key:ID, "outdoor_temp_entity":ID})
