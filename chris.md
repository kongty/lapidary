08/26/2022 -- DPR workshop notes
----------------------------

what you need in the introduction

    - challenge -- given different workload scenarios (multi-tenancy datacenter, edge compute with many different tasks), fixed-function accelerators are desired for efficiency but do not scale with N
        - proposal -- decision to focus on cgras, which have an efficiency edge over fpgas. general purpose compute solutions on the other hand are too inefficient.

    - challenge -- cgras lack scheduler-visible abstractions for hardware resources
        - proposal -- abstractions for three hardware resources (capacity in glb, bandwidth to/from glb, fabric compute)
        - we will show that this abstraction is sufficient to flexibly repartition in a way that achieves system speedup across different use cases (even though we skip the actual scheduler and just hand-schedule instead)

    - challenge -- cgras need fast support for dynamic partial reconfiguration to quickly update the hardware with dynamic scheduler decisions
        - proposal -- amber's fast DPR techniques, in more detail

what you need to evaluate

    - the two classes of scenarios currently look fine
        - 1 -- N tenants with N tasks, time-multiplexing onto the same cgra (N=4)
        - 2 -- camera pipelining + resnet keyframe example

    - we will HAND-SCHEDULE the tasks to the CGRA
        - hand-schedule the baseline -- use all resources
        - hand-schedule the alternative schedule -- use only the partitions you need, and use the remaining partitions to schedule portions of tasks that would otherwise need to wait

    - top-level metric
        - performance (your turnaround time metrics)
            - per-tenant
            - complete system performance

    - study metrics
        - glb capacity utilization
        - glb bandwidth utilization
        - compute utilization

    - results should show the baseline vs hand schedule
        - expectation -- performance is higher in both scenarios
            - why -- flexible partitioning should allow us to FULLY UTILIZE the three types of resources
        - expectation -- study metrics should be higher utilization

future questions

    - what to pre-compile?
        - pre-compiling all versions might be cheap enough that you should always do so?

    - hardware resource abstraction completeness?
        - with the three resources, is this sufficient or do you have to capture other resources too (e.g., some signals might be hardwired to the full CGRA like flush, that is something the scheduler needs to know?)
        - is there a fourth resource that impacts performance?
        - are there other resources that impact correctness

    - how to design scheduler with this abstraction?
        - scheduler needs to be FAST and react quickly
        - to be fast, you want higher level abstraction (i.e., less details) which capture the broad strokes of how to achieve high utilization
        - scheduler will run on host core (M3), so how fast do we need to make decisions, and how to design it to meet this goal?

the way i see it -- value added in this paper

    - value add -- observation that you want to flexibly allocate three things
        - 1 -- capacity in glb
        - 2 -- bandwidth to/from glb
        - 3 -- fabric resources of compute and local memory
        - ^ if you cannot flexibly allocate all three (say you only do one, or two) then you get underutilization in one of these that should be correctable
        - ^ kind of like disaggregated computing

    - value add -- fast dpr mechanism in cgra
        - this is just what is necessary to switch QUICKLY between these allocations
        - to differentiate from amber papers, we must show a bit more detail

    - value add -- compiler stuff for moving between partition configuration
        - observation that you want to pre-compile multiple versions of a task for a different options that have different resource usage (i.e., how many partitions)

    - context in related work
        - cgras don't have much such work
        - related work primarily in dnn accelerators and fpgas

the current proposed techniques in the draft look reasonable

    1. flexible hardware resource partitioning
    2. dynamic partial reconfiguration


dpr wddsa thoughts -- 09/09/2022

Our narrative is about supporting multi-task execution on CGRAs in either the "edge system scenario" (this is like the Amber VLSI autonomous vehicle example with dependent triggered tasks, camera pipe -> ResNet) or a "multi-tenant cloud system scenario" (independent tasks arrive and each tenant desires low latency for their own tasks).

What hardware support enables a workload scheduler to make decisions very quickly? By quickly, I mean a duration much shorter than the duration of a task. So it depends how long tasks are.

    - mark -- I assume that one of the interesting points is to run "short" tasks, right, so we want to have simple information. Or perhaps is the problem that a control processor, which will be running this algorithm, will always be pretty slow compared to the fabric so simpler is better?

My opinion on some of the very interesting bits:

    - Resource information granularity impacts speed -- In order to be relatively fast, the workload scheduler should not reason about individual PE and MEM tiles (e.g., it should not figure out what amoeba of resources to use), since that will take too long and there is too much detailed information to process. Even just reading that much information would take a long time. We must actively try to reduce the amount of information the scheduler reads, and yet still pass enough useful information to retain MOST of the schedule's potential performance impact. Therefore, in Taeyoung's paper, a key contribution is how to choose a higher-level abstraction of hardware resources. For example, the eight PR regions in Amber capture useful granular information, since information about available partitions can be read and analyzed in far fewer bits but you still have many useful schedules. Basically, for the sake of speed, what is the least information the scheduler needs to read in order to make a "good" decision.

        - mark -- Sounds good. I think there is also the issue of independence.  You need to have regions which allow other tasks to operate when a new task is being loaded.  Amoeba regions can't do this either, nor could they support preplaced objects.

    - Scheduler-visible abstraction of hardware -- Going further, which hardware resources really deserve to be in the set of "least information the scheduler needs"? I think we have settled on three in the workshop paper: (1) GLB memory capacity, (2) GLB memory bandwidth, (3) CGRA fabric compute resources. The architecture must allow flexible reallocation of these resources and cannot "just provide" the raw resources. Then we choose to make this resource information scheduler-visible. In the workshop paper, we call this a "flexible-shape hardware resource partitioning" because you could potentially have weird non-rectangular shapes (e.g., many GLB banks for high memory capacity feeding just a few CGRA column slices). But we are NOT DONE here, because ... are these three resources already sufficient as the only scheduler-visible hardware resources or do we need more? Also, the flush signal is broadcasted, right? So the scheduler needs to know this "resource" in order to preserve correctness and not flush a task that is already running on another part of the fabric. What is the set of scheduler-visible hardware resources for both performance and correctness? Then the granularity can scale to tune the scheduler speed.

        - mark -- I think the flush signal is really about independence.  It should be distributed along the columns and can easily be partitioned.  If that is not what is being done, we should talk about this issue.  The other issue is that moving data is expensive in time and energy.  So another question is do you need flexibility in routing between the GB an the partitions to take care of that?

    - Context in related work is promising -- From recent literature, I actually believe we have hit upon an _interesting enabling combination_ with our choice of CGRA and extremely high-frequency parallel DPR because it enables very fast reaction for multi-tasking scenarios where tasks are not known a priori (not known a priori = say a tenant requests a new task and the scheduler must now react). Literature-wise, ChordMap is a 2021 IEEE TCAD paper that is one of the only CGRA multi-tasking papers Taeyoung found, and it is from Tulika Mitra's group (so it is fairly good) and is very recent. As of 2021, they are proposing how to schedule multiple tasks onto a CGRA (just like us) but they are assuming modulo scheduling with spatial-temporal slots when all tasks are KNOWN a priori (this is important in a moment). In modulo scheduling, CGRA PEs have small instruction memories that go round-robin, and they are basically saying you can schedule Task A and Task B instructions over time into the same PE. But interestingly, they explicitly say that this is a CGRA advantage over FPGAs which do not do time-multiplexing. They say the FPGA must then do DPR if it wants to switch between tasks, but DPR is slow. They say on the other hand, a CGRA PE is already rotating through its instructions, so time-multiplexing multiple tasks is almost free. This makes sense. How does it relate to us? Well, we actually assume that tasks are NOT known a priori and that tasks can trigger or be requested any time. As a result, in our scenario, the scheduler  absolutely needs very fast DPR to react and program in new schedule configurations, and there is no way around it. In response, our work is firstly a CGRA (with far fewer config bits than an fpga), and we have also already designed the hardware for parallel, high-frequency DPR. I think this might be an _enabling_ combination for new scenarios with tasks not known a priori, triggered, or requested. When you measure turn-around time for each tenant in the multi-tenancy scenario, DPR time is directly in the critical path when a new task shows up. It becomes a question of how fast can you react?

        - mark -- I don't think this makes sense at all (regarding everything prior to the how it relates to us sentence).  For this to work, you still need to reconfigure the wiring between the PEs to do the next task, and this is more program information.  Essentially you need to double buffer the control state to really do this, right?  Or did I miss the point …

        - mark -- Our fast DPR does allow us to change tasks, or double buffering for instant changes (to a known task)

        - mark -- Completely agree (with how it relates to us).  But getting the data to the compute will still be an issue.  So the scheduler really needs to know when the data is available too …

    - Our pre-computed and relocatable bitstream techniques directly relate to this narrative -- Pre-computing bitstreams trades space for compilation time. Without pre-computed bitstreams, we would have to recompile the task on every scheduler decision for newly allocated hardware resources. In the above narrative, this pre-computation is actually very important. Recall from earlier that if the scheduler reads too much detailed resource information, it is likely to respond very slowly. In a similar way, suppose we allow the creation of schedules on hardware resources that have many many permutations (e.g., amoebas of resources), then in addition to the scheduler getting slower, the number of possible bitstreams also goes up significantly (and so does the number of precomputed bitstreams we must store). If you want to store all possible bitstreams to enable the scheduler to just look it up and deploy quickly, then I am pretty sure we would run out of GLB space, especially if we allowed amoeba-level detail on resource availability. It would also take time to find the right bitstream in a hierarchical lookup among so many. Even if we had a fallback to recompile the bitstream for different amoebas we did not store, that would place compile time on the DPR critical path. What does this mean for our perspective? First, we chose columns as DPR regions instead of amoebas, resulting in much fewer possible schedules. With very few schedules, the number of pre-computed bitstreams per task is actually feasible and gives us faster lookup times and also cheaper storage overhead. Lastly, making the bitstreams relocatable further coalesces where the schedules need to go to find bitstreams by another factor of ~8 at least. The lookup will be very fast. Also, note that choosing columns in the first place made relocation simpler to implement in hardware in practice as well. All of this is connected to enabling faster scheduler decisions and faster DPR to launch the new schedules.

        - mark -- This is a good point but this eats into your dynamic argument a little.  It can't be completely dynamic, since it needs to be on of the kernels you have already downloaded on the accelerator.  And we need a way to shift the columns that the configuration goes down, if you want to allow relocation. 

Chris
