from simpn.simulator import SimProblem, SimToken
from random import expovariate as exp, uniform as unif
from simpn.reporters import SimpleReporter
from simpn.visualisation import Visualisation
import simpn.prototypes as prototype

"""
Variable Declearion 
"""

lam = 1/30 # Interarrival rate of a student group
mu = 1/10 # Service rate of an instructor

instruction = SimProblem()
instructor = instruction.add_var('instructor')

# Places and Queues 

arrival = instruction.add_var('arrival')
busy = instruction.add_var('busy')
gone = instruction.add_var('gone')
waiting = instruction.add_var('waiting')
free = instruction.add_var('free')
break_i = instruction.add_var('break')
time_var = instruction.add_var("time_var")

instructor.put("i")

"""
Simulation
"""

def arrive(g):
    return [SimToken("g" + str(time_var)), SimToken(g+1, delay=exp(lam))]

instruction.add_event([arrival], [arrival, waiting], arrive)

def start(g, i):
    return [SimToken((g, i), delay=unif(10, 15))]

instruction.add_event([free, waiting], [busy, instructor], start)

def instructor_break(i):
    return [SimToken(i, delay=unif(5, 35))]

instruction.add_event([free], [break_i], instructor_break)

def instructor_return(i):
    return [SimToken(i)]

instruction.add_event([break_i], [free], instructor_return)


def complete(b):
    return [SimToken(b[1])]

instruction.add_event([instructor,busy], [], complete)

def leave_queue(g):
    return [SimToken(g)]

instruction.add_event([waiting], [gone], leave_queue)

"""
Visualisation
"""

instruction.simulate(10, SimpleReporter())

v = Visualisation(instruction, "test.txt")
v.show()
v.save_layout("test.txt")
