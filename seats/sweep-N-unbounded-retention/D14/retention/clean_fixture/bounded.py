"""Null-control fixture: every grown container is bounded."""
from collections import deque
from dataclasses import dataclass, field


@dataclass
class Ring:
    rows: deque = field(default_factory=lambda: deque(maxlen=48))
    log: list = field(default_factory=list)
    by_day: dict = field(default_factory=dict)

    def add(self, row, day):
        self.rows.append(row)
        self.log.append(row)
        del self.log[:-48]
        self.by_day[day] = row
        for old in sorted(self.by_day)[:-2]:
            del self.by_day[old]
