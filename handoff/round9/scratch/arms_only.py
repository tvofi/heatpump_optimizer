import runpy,sys
sys.argv=['tests/doc_claims.py']
g=runpy.run_path('tests/doc_claims.py', run_name='arms')
for f in ('check_entity_prose','check_private_mentions','check_unit_typography','check_service_fields'):
    g[f]()
print(g['R'].close("checks") if False else '')
