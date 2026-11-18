from .drift import Cusum
class C:
    def __init__(self):
        self._watch = Cusum(threshold=1.0, drift=0.1, side=1)
    def feed(self, now, measured_shortfall):
        self._watch.update(now, measured_shortfall)
    def _learning_frozen(self):
        if self._defrosting:
            return "defrosting"
        return None
