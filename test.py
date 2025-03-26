from simpn.simulator import SimProblem
from simpn.simulator import SimToken
from random import expovariate as exp
from random import uniform
from simpn.reporters import SimpleReporter
from simpn.visualisation import Visualisation


# Instantiate a simulation problem.
agency = SimProblem()

# Define queues and other 'places' in the process.
arrival = agency.add_var("arrival")
waiting = agency.add_var("waiting")
busy = agency.add_var("busy")

arrival.put(1)

# Define resources.
employee = agency.add_var("employee")
employee.put("e1")

# Define events.

def start(c, r):
  return [SimToken((c, r), delay=uniform(10, 15))]

agency.add_event([waiting, employee], [busy], start)

def complete(b):
  return [SimToken(b[1])]

agency.add_event([busy], [employee], complete)

def arrive(a):
  return [SimToken(a+1, delay=exp(4)*60), SimToken('c' + str(a))]

agency.add_event([arrival], [arrival, waiting], arrive)

# Run the simulation.
agency.simulate(60, SimpleReporter())

v = Visualisation(agency, "test.txt")
v.show()
v.save_layout("test.txt")


"""


def leave_condition(t, g1_queue, left_queue):

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


    for g in g1_queue:
        if t - g.time > 10:
            return True 
    return False 

def leave_queue(t, g1_queue, left_queue):    

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


    for g in g1_queue:
        if t - g.time >= 10:
            g1_queue.remove(g)
            left_queue.append(g)

    return [g1_queue, left_queue]


instruction.add_event([time_var, waiting.queue, left.queue],[waiting.queue, left.queue], leave_queue, guard=leave_condition)


"""