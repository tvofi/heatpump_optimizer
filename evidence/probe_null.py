import runpy, heatpump_optimizer.rooms as r
orig = r._comfort_at
r._comfort_at = lambda config, when: orig(config, when.replace(hour=12, minute=0))  # every step read as noon
runpy.run_path(__import__("os").path.expanduser("~/scratch/probe_dst.py"), run_name="__main__")
