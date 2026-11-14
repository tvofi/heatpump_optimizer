"""Service-reachable disinfection temperature above 70 (services.py Range max=75), entity max 80."""
import sys
sys.argv = ["guard_pins"]
import guard_pins as gp
for step in (1, 5, 0.5):
    for everyday, dis in ((55.0, 75.0), (60.0, 72.0), (55.0, 71.0)):
        print(f"step={step} everyday={everyday} disinfection={dis} instant ->", gp._step_notice(everyday, dis, step))
        print(f"step={step} everyday={everyday} disinfection={dis} hold    ->", gp._step_notice(everyday, dis, step, hold=True))
