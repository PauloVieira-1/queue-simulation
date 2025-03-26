from simpn.simulator import SimProblem, SimToken
from random import expovariate as exp, uniform as unif
from simpn.reporters import SimpleReporter
from simpn.visualisation import Visualisation
import simpn.prototypes as prototype

# Variable Declaration 

lam = 1/30 # Interarrival rate of a student group
mu = 1/10 # Service rate of an instructor

instruction = SimProblem()

student_groups = instruction.add_var('student_group')

"""
Initial State -> One instructor and one student group waiting to be assigned
"""

# Simulation -> Student Group Leave Queue 

left = instruction.add_var('left')
waiting = instruction.add_var('waiting')
instructor = instruction.add_var('instructor')
time_var = instruction.add_var("time")

instructor.put("i")

prototype.BPMNStartEvent(instruction, [], [waiting], "arrive", lambda: exp(lam))


def leave_condition(t, g1_queue, left_queue):
    """
    Condition for a student group to leave the queue.

    This function checks whether there is a student group in the queue that has
    been waiting for more than 10 minutes. If so, it returns True; otherwise, it
    returns False.

    Parameters
    ----------
    t : float
        The current time of the simulation.
    g1_queue : list
        The list of student groups currently in the queue.
    left_queue : list
        The list of student groups that have left the queue.
    """

    for g in g1_queue:
        if t - g.time > 10:
            return True 
    return False 

def leave_queue(t, g1_queue, left_queue):    
    """
    Leave the queue event function.

    This function removes the student group g from g1_queue and puts it in
    left_queue. It is called when a student group leaves the queue.

    Parameters
    ----------
    t : float
        The current time of the simulation.
    g1_queue : list
        A list of student groups waiting to be assigned to an instructor.
    left_queue : list
        A list of student groups that have left the queue.
    """

    for g in g1_queue:
        if t - g.time >= 10:
            g1_queue.remove(g)
            left_queue.append(g)

    return [g1_queue, left_queue]


instruction.add_event([time_var, waiting.queue, left.queue],[waiting.queue, left.queue], leave_queue, guard=leave_condition)
     

# Visualisation

instruction.simulate(10, SimpleReporter())

v = Visualisation(instruction, "test.txt")
v.show()
v.save_layout("test.txt")
