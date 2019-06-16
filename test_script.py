from datetime import datetime
from pprint import pprint

from demo_hospital import demo2
# from solver_googleOR import solver
from solver_with_urgency import solver

print(demo2)

schedule = solver(demo2, datetime.now())

pprint(schedule)
