from simpn.simulator import SimProblem, SimToken
from random import expovariate as exp, uniform as unif, random
from simpn.reporters import SimpleReporter, Reporter
from simpn.visualisation import Visualisation

"""
Variable Declaration 
"""

# Rates (per minute)
lam = 1/30  # Interarrival rate of student groups (1 every 30 minutes on average)
mu = 1/10   # Service rate (10 minutes per group on average)
max_sim_time = 60 * 3  # 8 hours simulation (in minutes)

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
        SimToken(a + 1, delay=exp(lam)),  # Next arrival
        SimToken(new_w, delay=0)          # Updated waiting queue
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
    if not waiting_groups:
        return [
            SimToken(free_instructor, delay=0),
            SimToken(waiting_groups, delay=0),
            SimToken([], delay=0)
        ]
    
    group = waiting_groups.pop(0)
    service_duration = exp(mu)

    return [
        SimToken([], delay=0),  # Instructor is now busy, remove from `free`
        SimToken(waiting_groups, delay=0),  # Updated waiting queue
        SimToken([group], delay=service_duration)  # Busy queue
    ]


instruction.add_event(
    [free, waiting],
    [free, waiting, busy],
    start_service,
    guard=service_guard,
    name="start_service"
)

def end_service(busy_groups, time_var, s_times, w_times, served_groups):
    if not busy_groups:  
        return [SimToken([], delay=0)]  # Return empty if no busy groups

    group = busy_groups[0]  

    service_time = time_var - group["time"]  

    updated_served = served_groups + [group]  

    return [
        SimToken([], delay=0),  # Empty busy queue
        SimToken(s_times + [service_time], delay=0),
        SimToken(w_times + [service_time], delay=0),
        SimToken(updated_served, delay=0),  # ✅ Correctly update served
        SimToken("Instructor", delay=0)
    ]


instruction.add_event(
    [busy, time_var, service_times, waiting_times, served],
    [free, service_times, waiting_times, served],
    end_service,
    name="end_service"
)

# def complete_service_A_event(busy):
#     if not busy:
#         return [SimToken([], delay=0)]
#     token_val = busy[0].value if hasattr(busy[0], 'value') else busy[0]
#     try:
#         cust = token_val[0]
#     except Exception:
#         cust = token_val
#     return [SimToken(cust, delay=0)]
# helpdesk_sim.add_event([busy_a], [served], complete_service_A_event, name="complete_service_A_event")




def should_take_break(instructor):
    """70% chance to take a break"""
    if random() <= 0.7:
        break_duration = unif(15, 35)
        return [None, SimToken(instructor, delay=break_duration)]
    return [SimToken(instructor, delay=0), None]

instruction.add_event(
    [free],
    [free, break_i],
    should_take_break,
    name="choose_break"
)

def instructor_return(instructor):
    """Instructor returns from break"""
    return [SimToken(instructor, delay=0)]

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