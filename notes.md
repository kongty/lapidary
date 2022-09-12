dpr wddsa contribution

Highly concurrent execution, spatially multiplexed CGRA.
In edge scenario, there are so many dependent tasks that are dynamically generated.
In cloud scenario, independent tasks arrive at node with different throughput.

- Dynamic scheduler is needed to support multi-task execution.
    - Different shape
    - Instructions: RC instruction, addr, data, dest

scheduler decide:
    - Which task to run
    - Synchronize

Chordmap:
    - It only applies for streaming application where all tasks are known a priori.

2. How to abstract task so that CGRA can dynamically schedule each task
3. It would be good if CGRA can do both and choose one depending on the situation.
4. How to synchronize if there is communication between tasks (barriers?)

How to get over tall/thin region? Can we have unbalanced horizontal/vertical routing track?

System support (resource management)
Scheduling algorithms do not account for characteristics of CGRAs, leading to infeasible or inefficient allocations.

Average throughput, average utilization

Virtualization: spatial sharing
Partial reconfiguration: temporal sharing (In order to reduce time to save intermediate state, only switch at specific time point)
System's desired target allocations. Max/min fariness. Priority based.

Autnonomous system has strict requirements on the response time of the task.

CGRA / FPGA reconfigurable architectures: slots. However, the size is static. When multiple slots are needed, you need to partition the graph and need communication. Merge is not easily supported by EDA tools, and complicates fpga mappings.
CGRA is coarse, so we can  easily control this.
FPGA config space too big. even ICAP is slow.

virtualization and fast-DPR provides mechanisms for sharing CGRAs but not managing them.



Host to manage task parallelism and task launches: It's hard.
on-chip task scheduling and launching capabiliteis . low-latency dynamic task parallelism.. on-chip exchange of values.



preliminary prototype. speedup compared to.
SLO: tail-latency
ASSUME REQUEST QUEUES ARE ALWAYS SATURATED, THEREBY ISOLATING MODEL SERVICE LATENCY FROM REQUEST QUEUING LATENCY.
Two-level schedule (instruction, task) 
Monitor latency per-kernel. Reallocating resources between tenants on the fly.
resource-efficiency, latency predictability, isolation
application level graph! vs kernel level graph.


Batch mode scheduling vs immediate mode scheduling.

RMS receive task with QoS and SLA requirements from IoT devices and users.
It schedules the new task and also periodically decides migration.
PRR, MEM, Bandwidth, Completion time, Deadline.


kernel = layer
job = frame
model = user

To optimize concurrency for workloads exhibiting staged computation demand.

Full stack: Batch (data fusion in autonomous driving when multiple cameras frames)
