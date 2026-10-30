import sys; sys.path.insert(0, sys.argv[1])
from jinja2.nativetypes import NativeEnvironment
from datetime import datetime, timezone
env = NativeEnvironment()
env.globals['as_timestamp'] = lambda s: datetime.fromisoformat(s).timestamp() if isinstance(s,str) else s.timestamp()
now = datetime(2026,10,31,12,0,tzinfo=timezone.utc)
env.globals['now'] = lambda: now
tpl = """{% set old = (from_attrs.get('cheaper_windows') or []) %}{% set ns = namespace(new=false) %}{% for w in windows %}{% if w not in old and as_timestamp(w.start) > as_timestamp(now()) %}{% set ns.new = true %}{% endif %}{% endfor %}{{ ns.new }}"""
old = [{"start":"2026-10-31T14:00:00+00:00","end":"2026-10-31T16:00:00+00:00"}]
cases = {
 "unchanged": old,
 "same window, end moved 15 min": [{"start":"2026-10-31T14:00:00+00:00","end":"2026-10-31T15:45:00+00:00"}],
 "same window, start moved 15 min": [{"start":"2026-10-31T14:15:00+00:00","end":"2026-10-31T16:00:00+00:00"}],
 "one window split in two by one pump-off step": [{"start":"2026-10-31T14:00:00+00:00","end":"2026-10-31T15:00:00+00:00"},{"start":"2026-10-31T15:15:00+00:00","end":"2026-10-31T16:00:00+00:00"}],
}
for k,v in cases.items():
    print(f"follow-up fires={env.from_string(tpl).render(windows=v, from_attrs={'cheaper_windows':old})}  case: {k}")
