from simpn.simulator import SimProblem, SimToken
from numpy import random
from simpn.reporters import SimpleReporter
from simpn.visualisation import Visualisation


# Variable Declaration 

lam = 1/30 # Interarrival rate of a student group
mu = 1/10 # Service rate of an instructor

instruction = SimProblem()

student_groups = instruction.add_var('student_group')
instructors = instruction.add_var('instructor')

"""
Initial State -> One instructor and one student group waiting to be assigned
"""

student_groups.put("c1")
instructors.put("i")

# Simulation 

def arrive(a):
    return [SimToken(f'c{str(a)}'), SimToken(a + 1, delay=random.exponential(scale=mu))]

instruction.add_event([student_groups], [student_groups], arrive)

def start(c1, i):
    return [SimToken((c1, i), delay=random.uniform(15, 30))]

instruction.add_event([student_groups, instructors], [student_groups, instructors], start)


def end_service(c1, i):
    return [SimToken(c1), SimToken(i)]

instruction.add_event([student_groups, instructors], [student_groups, instructors], end_service)

# Visualisation

instruction.simulate(10, SimpleReporter())

v = Visualisation(instruction, "test.txt")
v.show()
v.save_layout("test.txt")
