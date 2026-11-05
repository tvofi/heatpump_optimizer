import sys, json, inspect; sys.path[:0]=['tests','tests/hastub','tools/replay']
import export
d=export._doc
conf=export.entry_keys(*export.default_const_paths())
print('conf keys:', len(conf), sorted(conf)[:80])
ts="2026-01-15T00:00:00+00:00"
def go(name, options):
    rows={"sensor.in":[[ts,"1",None,None]],"sensor.zzz_probe":[[ts,"2",None,None]],"sensor.hpo_out":[[ts,"4",None,None]]}
    kw=dict(time_zone="UTC",window=(ts,"2026-01-16T00:00:00+00:00"),recorder_schema=48,
      entry={"entry_id":"01JX","data":{},"options":options},inputs=["sensor.in","sensor.zzz_probe"],
      published=["sensor.hpo_out"],price_series_entity=None,states=rows)
    if 'conf' in inspect.signature(d.document).parameters: kw['conf']=conf
    raw=d.document(**kw)
    try:
        s=d.seal(raw,conf); print('RESULT',name,'SEALED states',len(s['states']),'leak','zzz_probe' in json.dumps(s))
    except d.Refused as e: print('RESULT',name,'REFUSED',e)
k=sorted(conf)
for key in [x for x in k if not d.SECRET_KEY.search(x)][:3]:
    go(f'list_under_conf_key[{key}]', {key:["abc","sensor.zzz_probe"]})
    go(f'list_under_conf_key_ids_only[{key}]', {key:["sensor.zzz_probe"]})
go('entity_key_off_list', {"legacy_probe_entity":"sensor.zzz_probe"})
go('entities_list_off_list', {"room_sensor_entities":["","sensor.zzz_probe"]})
