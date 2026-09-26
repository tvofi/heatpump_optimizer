import sys, json
sys.path.insert(0, '/tmp/claude-0/scope3/tests')
import stress
labels=["flat/2z/dhw","flat/2z/space","winter/2z/dhw","winter/2z/space","winter/cycle","winter/pv","winter/pv+cycle","winter/tariff","winter/tariff+cycle","winter/tariff+pv","winter/tariff+pv+cycle","winter_extreme/2z/dhw","winter_extreme/2z/space","winter_mild/2z/dhw","winter_mild/2z/space"]
rows,note=stress.capture_work_rows(sys.argv[1], sys.argv[2], labels)
print(note)
for k in labels: print(k, rows[k]["objective"] if rows and k in rows else None)
