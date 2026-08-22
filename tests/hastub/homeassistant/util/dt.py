from datetime import datetime, timezone
def now(): return datetime.now()
def utcnow(): return datetime.now(timezone.utc)
def parse_datetime(v): 
    try: return datetime.fromisoformat(v)
    except Exception: return None
def as_local(v): return v
