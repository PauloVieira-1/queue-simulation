```
```

# Queue Simulation

This repository contains a simulation model for evaluating the efficiency of a student-instructor scheduling system at a simulation practical. The simulation examines how changes in student arrival patterns and instructor break schedules affect waiting times, student departures, and instructor availability.

## Problem Description

In the original system:

- Student groups arrive at the practical session following a **negative exponential interarrival distribution** with a mean of **30 minutes**.
- Each student group's **service time** follows a **uniform distribution** between **15 and 30 minutes**.
- If no students are waiting, there is a **70% chance** that the instructor takes a **coffee break**, which lasts a **uniformly distributed** duration between **5 and 35 minutes**.
- If a student group waits for **more than 10 minutes** while the instructor is away, they **leave** immediately.
- If the instructor is present but a student group has waited **more than 10 minutes**, there is a **5% chance** they will **leave** due to frustration.

This results in inefficient operations: **students experience long waits or leave**, while the **instructor often misses their break**.

## Proposed Solution

A **scheduled system** is introduced to improve efficiency:

- **Student interarrival time is fixed at exactly 30 minutes** instead of following an exponential distribution.
- **Instructor coffee breaks are fixed at 20 minutes** instead of a random duration.
- **All other conditions remain unchanged**.

## Objective

The simulation will evaluate whether these adjustments improve the situation by measuring:
1. The **percentage of student groups that leave before being serviced**.
2. The **fraction of time the instructor spends on coffee breaks**.

## Implementation

The simulation models:
- A queue system where students arrive, wait, receive service, or leave.
- The instructor's decision-making regarding breaks.
- Performance metrics to assess the impact of scheduling.

## How to Run

1. Clone this repository:
   ```bash
   git clone https://github.com/PauloVieira-1/queue-simulation.git
   cd queue-simulation
   ```
2. Install required dependencies (if applicable).
3. Run the simulation script:
   ```bash
   python simulation.py
   ```
4. Review the output metrics.

## Expected Results

The experiment will help determine whether:
- **Fewer students leave** due to long waits.
- **The instructor gets more consistent breaks**.

## License

This project is for educational purposes and follows an open-source license.

---

```
```
