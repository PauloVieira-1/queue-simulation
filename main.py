from simpn.simulator import SimProblem, SimToken
from random import expovariate as exp, uniform as unif, random
from simpn.reporters import SimpleReporter, Reporter
from simpn.visualisation import Visualisation

"""
Variable Declaration 
"""

# Rates (per minute)
lam = 1/30  # Interarrival rate of student groups (1 every 30 minutes on average)
service_duration =  unif(15, 30)  # Service rate of instructors (15-30 minutes on average)
break_duration = unif(5, 15)  # Break rate of instructors (5-15 minutes on average)
max_sim_time = 60 * 3  # 3 hours

instruction = SimProblem()

# Resources
instructor = instruction.add_var('instructor')
instructor.put("Instructor")

# Places and Queues 
arrival = instruction.add_var('arrival')
arrival.put(1)  # Starting group ID

busy = instruction.add_var('busy')
busy.put([])

gone = instruction.add_var('gone')
gone.put([])

waiting = instruction.add_var('waiting')
waiting.put([])

free = instruction.add_var('free')
free.put("Instructor")  

break_i = instruction.add_var('break')
break_i.put([])

time_var = instruction.add_var("time_var")
time_var.put(0)

served = instruction.add_var("served")
served.put([])

# Statistics collection
service_times = instruction.add_var("service_times")
service_times.put([])

waiting_times = instruction.add_var("waiting_times")
waiting_times.put([])


"""
Simulation Events
"""

def arrive(t, a, w):
    """
    Student group arrival event.
    Generates a new group and schedules the next arrival.
    """
    token = {"id": f"g{a}", "time": t}
    new_w = w + [token]
    return [
        SimToken(a + 1, delay=exp(lam)),
        SimToken(new_w, delay=0)          
    ]

instruction.add_event([time_var, arrival, waiting], [arrival, waiting], arrive, name="arrive")

def leave_condition(t, waiting_groups, left_groups):
    """Check if any group has waited too long and might leave."""
    return any(t - g["time"] > 10 for g in waiting_groups)

def reneging_event(t, waiting_groups, left_groups):
    """
    Handle groups leaving the queue if they've waited too long.
    - 100% leave if instructor is on break
    - 5% chance if instructor is busy
    """
    remaining = []
    leaving = []
    
    for group in waiting_groups:
        waited = t - group["time"]
        if waited > 10:
            if random() <= 0.05:
                leaving.append(group)
                continue
        remaining.append(group)
    
    return [
        SimToken(remaining, delay=0),
        SimToken(left_groups + leaving, delay=0)
    ]

instruction.add_event(
    [time_var, waiting, gone],
    [waiting, gone],
    reneging_event,
    guard=leave_condition,
    name="reneging_event"
)

def service_guard(waiting_groups, busy_groups):
    """Check if service can start (group waiting and instructor free)"""
    return len(waiting_groups) > 0 

def start_service(free_instructor, waiting_groups):
    """Start serving a student group"""
    if free_instructor != "Instructor" or not waiting_groups:
        return [SimToken(free_instructor, delay=0),
                SimToken(waiting_groups, delay=0),
                SimToken([], delay=0)]
    
    group = waiting_groups[0]  
    return [
        SimToken(None, delay=0),  
        SimToken(waiting_groups[1:], delay=0),  
        SimToken([group], delay=service_duration)  
    ]

# Update the event with correct input/output mapping
instruction.add_event(
    [free, waiting],
    [free, waiting, busy],
    start_service,
    guard=lambda f, w: f == "Instructor" and len(w) > 0,
    name="start_service"
)

def end_service(busy_groups, served_groups, free_instructor):
    """Complete service and return instructor"""
    if not busy_groups:
        return [SimToken(busy_groups, delay=0),
                SimToken(served_groups, delay=0),
                SimToken(free_instructor, delay=0)]
    
    group = busy_groups[0]
    return [
        SimToken([], delay=0), 
        SimToken(served_groups + [group], delay=0), 
        SimToken("Instructor", delay=0) 
    ]

# Update the event definition with proper guard
instruction.add_event(
    [busy, served, free],
    [busy, served, free],
    end_service,
    guard=lambda b, s, f: len(b) > 0, 
    name="end_service"
)

def should_take_break(free_instructor, current_time):
    if free_instructor == "Instructor" and random() <= 0.7:  
        print(f"Instructor taking break at {current_time:.2f} for {break_duration:.2f} mins")
        return [SimToken(None, delay=0),
                SimToken("Instructor", delay=break_duration)]
    return [SimToken(free_instructor, delay=0),
            SimToken([], delay=0)]

instruction.add_event(
    [free, time_var],
    [free, break_i],
    should_take_break,
    name="choose_break"
)

def instructor_return(instructor):
    """Instructor returns from break"""
    return [SimToken("Instructor", delay=0)]

instruction.add_event(
    [break_i],
    [free],
    instructor_return,
    name="instructor_return"
)

"""
Simulation Execution
"""

print("Starting simulation...")
# instruction.simulate(max_sim_time, SimpleReporter())

class MyReporter(SimpleReporter):
    def callback(self, timed_binding):
        print(timed_binding)

instruction.simulate(max_sim_time, MyReporter())

"""
Visualization
"""


print("\nGenerating visualization...")
v = Visualisation(instruction, "test.txt")
v.show()
v.save_layout("test.txt")
print("Simulation complete!")