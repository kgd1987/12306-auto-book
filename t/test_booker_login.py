# -*- coding: utf-8 -*-

import sys

# Manage the search path to include the booker souce
sys.path.insert(0, '..')
from booker.booker import Booker

b = Booker('13588244781', 'vaneyue0802')
b.login()






