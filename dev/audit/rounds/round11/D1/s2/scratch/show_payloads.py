import sys, json
sys.path.insert(0, "dev/audit/rounds/round11/D1/s2")
import store_fuzz as SF
H = SF.healthy()
for n in ("boost", "away", "pump_duty", "off_restore", "duty_switch", "dhw_legionella", "manual_plan", "notifier", "energy"):
    k, p, v = H[n]
    print(n, v, json.dumps(p)[:600])
