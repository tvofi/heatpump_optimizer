# direct: the minimal global-binding source, printed at whichever head this runs
src = '''
import os
from pathlib import Path
_G = None
def load():
    global _G
    _G = "dev/audit/rounds/round4/D12/units.py"
_X = open(_G)
'''
print("HEADSELF opens:", _sp_literals(src))
src2 = '''
import os
class C:
    def __init__(self):
        self._p = "dev/audit/rounds/round4/D12/units.py"
    def run(self):
        return open(self._p)
'''
print("SELFATTR opens:", _sp_literals(src2))
