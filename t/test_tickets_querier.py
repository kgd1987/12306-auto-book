# -*- coding: utf-8 -*-

import sys

# Manage the search path to include the booker souce
sys.path.insert(0, '..')
from booker.booker import Booker
from booker.tickets_querier import Querier

b = Booker('13588244781', 'vaneyue0802')

q = Querier('杭州东', '徐州东', '2018-12-03')


# b.login()

# res = b.query_tickets('杭州东', '徐州东', '2018-12-01')
# print(res)




