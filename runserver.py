import os
os.chdir(os.path.join(os.path.dirname(__file__),"sdv"))

import sys
sys.path.insert(0, './')

from sdv import app
app.run(host="0.0.0.0")