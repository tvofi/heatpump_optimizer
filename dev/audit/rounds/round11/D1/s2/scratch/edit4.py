p = "dev/audit/rounds/round11/D1/s2/weather_stuck.py"
s = open(p).read()
s = s.replace("""        cut = L.dtu.now() - timedelta(hours=1)
        keep = []
        for r in out:
            when = L.dtu.parse_datetime(str(r.get("datetime") or ""))
            if when is None or when >= cut:""", """        now = L.dtu.now()
        keep = []
        for r in out:
            when = L.dtu.parse_datetime(str(r.get("datetime") or ""))
            if when is None or when + timedelta(hours=1) > now:  # the row's hour has not ended""")
s = s.replace("row whose ``datetime`` lies over an hour in the past", "row whose hour (``datetime`` + 1 h) has ended")
open(p, "w").write(s)
