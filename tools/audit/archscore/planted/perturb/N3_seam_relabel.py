"""N3 (NULL for the code): relabel ONE coordinator method in tests/seam_map.json
(_async_watch_learning_drift: learning -> core). No production byte changes.
Chosen as the single relabel that lowers the cut table most (searched over all
224 methods x 5 alternative labels at baseline: search_relabel.py).
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import seam_set
seam_set("_async_watch_learning_drift", "core")
