## TODO
- [ ] Report SLA metrics
- [x] Add task queue
- [ ] Add offchip bandwidth requirement to kernel
- [ ] Add deadline to each task
- [X] Change terms (app, job, task, kernel)
- [ ] Make `app` and `app_pool` as configuration file
- [ ] Make it DNN specific by changing  `AppConfig` class to reflect input/kernel/output or DNN specific params
- [ ] Implement interrupt for proc_schedule, so that it stops scheduling when new task arrives. 
- [ ] hierarchical logger (task->kernel->instruction)
- [ ] Convert kernel list to kernel graph
- [ ] Take one DNN layer as input, break it down to instructions
- [ ] See how scheduling works in full-flexible scenario with best optimization vs no-flexible with sequential scheduling


## Idea
- From Maestro, generate memory and computation instructions.
- Key idea is to generate instructions independent to 


## Different level of scheduling comparison

### Current version
1. a task arrives
2. put the task into the task queue
3. Run schedule to select kernels to run
4. When kernel finishes, run a schedule again to select next kernels
    > Cons 
    > - Cannot temporarlly holistically optimize  to map multiple kernels as we just run one by one.     
    >
    > Proposal 1: Run optimization algorithm to schedule all kernels in tasks a priori   
    > Proposal 2: Break kernel into instructions to further optimize  
5. Here, the output of the schedule is actually what it executes right away.
    - Components: CGRA, scheduler, task_queue. Scheduler chooses one kernel from task queue


New version
1. new task arrives
2. put task into the task queue
3. Run schedule to schedule all kernels
    Pros - Can decide when to synchronize, when to 
    Cons - if we just schedule kernel, it doesn't overlap memory/computation that well
    => Need to break kernel into memory and computation instructions
4. Here, the output of the schedule is scheduled kernels (let's call it kernel_queue) 
    - Components: CGRA, scheduler, task_queue, kernel queue.
    - Scheduler chooses one kernel from task queue

What to decide  
How do we decide the resource allocation?  
Planaria: Task level resource allocation (Resource allocation is fixed for entire dnn task).  
Ours: Layer level resource allocation. We allocate resources for each layer.  
Syncrhonization point: Point where we reallocate resource partitioning.  
DPR point: Point where we change hardware.  

Benchmark
1. Select DNNs
2. Each DNN has different Poisson distribution, but more frequent one has lower lambda
3. Different combinations
4. Run for certain period of time.
5. Measure the average latency, tail latency, SLO, etc.
How to choose Array size? 
First, choose systolic array and CGRA that has same amount of MAC
Second, Choose small/medium/large NPU, CGRA and comination with different benchmarks

Decisions
1. task arrives
2. Schedule all tasks at coarse-grain instruction level
    - meet requirement
    - memory
        - when to fetch
    - computation
        - when to execute
        - where to execute
        - which dataflow to run
    - Periodically check available DRAM bandwidth
3. When new task arrives
    - discard already scheduled one
    - rerun schedule.
