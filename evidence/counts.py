import sys, re, json, collections, pathlib, importlib.util
root = pathlib.Path(sys.argv[1])
sys.path[:0] = [str(root/'tests')]
spec = importlib.util.spec_from_file_location("dc", root/'tests'/'doc_claims.py')
dc = importlib.util.module_from_spec(spec); spec.loader.exec_module(dc)
from heatpump_optimizer import const
ents = dc.entity_census({const.CONF_DHW_TANK_VOLUME: 200.0})
print("entities", len(ents), collections.Counter(e['platform'] for e in ents))
print("entities nodhw", len(dc.entity_census({})))
svc = dc.registered_service_fields(); print("services", len(svc))
import yaml
y = yaml.safe_load((root/'custom_components/heatpump_optimizer/services.yaml').read_text()); print("services.yaml", len(y), set(y)==set(svc))
en = json.loads((root/'custom_components/heatpump_optimizer/translations/en.json').read_text())
print("setup steps", len(en['config']['step']))
titles, pages = dc.options_field_pages(); print("option page titles", len(titles))
import heatpump_optimizer.config_flow as cf
print("_OPTION_PAGES", len(cf._OPTION_PAGES), "_OPTION_FIELDS", len(cf._OPTION_FIELDS))
print("option labels", len(pages))
print("blueprints", len(list((root/'blueprints/automation').glob('*.yaml'))))
src=(root/'custom_components/heatpump_optimizer/notifier.py').read_text()
print("events", re.findall(r'^(EVENT_\w+)\s*=', src, re.M))
card=(root/'custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js').read_text()
print("tabs", sorted(set(re.findall(r'tab\("([^"]+)"', card))))
s=json.loads((root/'custom_components/heatpump_optimizer/strings.json').read_text())
print("issues", len(s.get('issues',{})), "exceptions", len(s.get('exceptions',{})))
