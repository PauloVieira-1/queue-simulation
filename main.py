from simpn.simulator import SimProblem, SimToken
from random import expovariate as exp, uniform as unif
from simpn.reporters import SimpleReporter
from simpn.visualisation import Visualisation
import simpn.prototypes as prototype

"""
Variable Declearion 
"""

lam = 1/30 # Interarrival rate of a student group
mu = 10 # Service rate of an instructor

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
served = instruction.add_var("served")
instructor_busy = instruction.add_var("instructor_busy")

# TIMES 

service_times = instruction.add_var("service_times")
waiting_times = instruction.add_var("waiting_times")
service_times.put([])
waiting_times.put([])

# Initilization

instructor.put("Instructor")
arrival.put(1)
busy.put([])
gone.put([])
waiting.put([])
free.put([])
break_i.put([])
time_var.put(0)
served.put([])
instructor_busy.put([])


"""
Simulation
"""

# Guards 

def leave_condition(t, g1_queue, left_queue, i):
    """
    Leave condition function.

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
    i : str
        The id of the instructor.
    """
    return any(t - g.time > 10 and unif(0, 100) <= 5 for g in g1_queue)

def service_guard(g, i, b):
    
    """
    Service guard function.

    This function checks whether there are any student groups in the waiting
    queue that can be assigned to an instructor for service.

    Parameters
    ----------
    g : list
        The list of student groups currently in the waiting queue.
    i : str
        The id of the instructor.
    b : bool
        Whether the instructor is currently busy or not.

    Returns
    -------
    bool
        True if there is at least one student group in the waiting queue;
        otherwise, False.
    """

    return len(g) > 0

# Modal Transitions

def arrive(t, a, w):
    """
    Arrive event function.

    This function generates a new arrival after an exponential time delay and
    adds it to the waiting queue.

    Parameters
    ----------
    t : float
        The current time of the simulation.
    a : int
        The current number of arrivals.
    g : list
        The list of student groups currently in the queue.

    Returns
    -------
    list
        A list of two tokens: the new arrival and the incremented arrival count.
    """
    token = {"id": "g" + str(a), "time": t}
    new_w = w + [token]
    return [SimToken(a + 1, delay=exp(1/8)), SimToken(new_w, delay=0)]

instruction.add_event([time_var, arrival, waiting], [arrival, waiting], arrive, name="arrive")

def reneging_event(t, w, L, instructor_busy):
    """
    Reneging event function.

    Students leave the queue if they have waited more than 10 minutes.  
    - If the instructor is **NOT present**, they **always leave**.  
    - If the instructor **is present**, they leave with a **5% probability**.  

    Parameters
    ----------
    t : float
        The current time of the simulation.
    w : list
        The list of student groups currently in the queue.
    L : list
        The list of student groups that have left the queue.
    instructor_free : bool
        Whether the instructor is currently free.

    Returns
    -------
    list
        A list of two tokens:  
        - Remaining students in the queue  
        - Students that have left  
    """
    
    remaining = []
    leaving = []

    for token in w:
        waited = t - token["time"]
        probability = unif(0, 100)  

        if waited >= 10:
            if not instructor_busy or probability <= 5:  
                leaving.append(token)
            else:
                remaining.append(token)
        else:
            remaining.append(token)

    delay_time = 5 if remaining else 0  
    return [SimToken(remaining, delay=delay_time), SimToken(leaving, delay=0)]


instruction.add_event([time_var, waiting, gone, instructor_busy], 
                      [waiting, gone], 
                      reneging_event, 
                      guard=leave_condition, 
                      name="reneging_event")



def start_service(i, waiting_students, instructor_busy):
    """
    Start service event function.

    This function starts a new service when a student group arrives at the waiting
    queue and there is a free instructor. The student group is removed from the
    waiting queue and the instructor is set to busy. The event is delayed by an
    exponential distribution with rate mu.

    Parameters
    ----------
    i : str
        The id of the instructor.
    waiting_students : list
        The list of student groups currently in the waiting queue.
    instructor_busy : bool
        Whether the instructor is currently available (False) or busy (True).

    Returns
    -------
    list
        A list of two tokens: the remaining students in the waiting queue and the
        student group that is being served.
    """

    if not waiting_students:
        return [SimToken(waiting_students, delay=0), SimToken(i, delay=0)]
    student_group = waiting_students.pop(0)
    delay_time = exp(1/mu) * 60 
    instructor_busy = True
    return [SimToken((waiting_students, i), delay=delay_time), SimToken(student_group, delay=delay_time), SimToken(instructor_busy, delay=delay_time)]

instruction.add_event([free, waiting, instructor_busy], [busy, instructor, instructor_busy], start_service, guard=service_guard, name="start")

def choose_break(i):
    """
    Choose break event function.

    This function decides whether an instructor takes a break or not. The
    probability of taking a break is 70%. If the instructor takes a break, the
    duration of the break is uniformly distributed between 5 and 35 minutes.

    Parameters
    ----------
    i : str
        The id of the instructor.

    Returns
    -------
    list
        A list of two tokens: the instructor (if not taking a break) and the
        break (if taking a break).
    """
    percentage = unif(0, 100)
    if percentage < 70:
        return [SimToken(i, delay=0), None]
    else:
        return [None, SimToken(i, delay=unif(15, 35))]

instruction.add_event([free], [break_i, free], choose_break)

def instructor_return(i):
    """
    Instructor return event function.

    This function simply returns the instructor to the free pool when the break
    is finished.

    Parameters
    ----------
    i : str
        The id of the instructor.

    Returns
    -------
    list
        A list of two tokens: the instructor and None.
    """
    return [SimToken(i, delay=unif(5, 35))]

instruction.add_event([break_i], [free], instructor_return, name="instructor_return")

def end_service(b, i, t, s_times, w_times, instructor_busy):
    """
    End service event function.

    This function removes the student group from the busy queue, calculates the
    service time and adds it to the service times list, and returns the
    instructor to the free queue.

    Parameters
    ----------
    b : list
        The list of student groups currently in the busy queue.
    i : str
        The id of the instructor.
    t : float
        The current time of the simulation.
    s_times : list
        The list of service times.
    w_times : list
        The list of waiting times.

    Returns
    -------
    list
        A list of two tokens: the student group that has been served and the
        instructor that is now free.
    """
    if not b:
        return [SimToken([], delay=0), SimToken(i, delay=0)]
    token_val = b[0].value if hasattr(b[0], 'value') else b[0]
    group = token_val[0] if isinstance(token_val, tuple) else token_val
    service_time = t - group["time"]
    s_times.append(service_time)
    w_times.append(service_time)
    instructor_busy = False
    return [SimToken(group, delay=0), SimToken(i, delay=0), SimToken(s_times, delay=0), SimToken(w_times, delay=0), SimToken(instructor_busy, delay=0)]

instruction.add_event([instructor, busy, time_var, service_times, waiting_times, instructor_busy], [free, served, service_times, waiting_times, instructor_busy], end_service, name="end_service")


"""
Visualisation
"""

instruction.simulate(60, SimpleReporter())

v = Visualisation(instruction, "test.txt")
v.show()
v.save_layout("test.txt")



