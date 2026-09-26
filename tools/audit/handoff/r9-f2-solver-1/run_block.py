import sys, re
sys.path[:0]=['tests','custom_components','tests/hastub']
from datetime import datetime, timedelta, timezone
import numpy as np
from harness import Results
from heatpump_optimizer import pv
R = Results("F2.1 block")
src = open('tests/features.py').read()
start = src.index('# -- R9-F2.1:')
end = src.index('# -- #1524: the experiment identifies')
exec(compile(src[start:end], 'features_block', 'exec'))
sys.exit(R.close("F2.1 BLOCK"))
