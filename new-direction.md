09/08/2022 -- Research Notes for ISCA
-------------------------------------

# The Research Goal.
Solve Multi-DNN problems on CGRA

## Components of the problem 

### Application
Multi-DNN scenarios are diverse.
1. multi-tenancy (independent DNNs, different requirements)
2. a single application with multi-DNN (e.g. perception stage in autonomous vehicle, object_detection/segmentation/depth_estimation, but they all need to synchronize before deciding a command. Overall latency matters more than a single latency)
3. ensanble/cascade DNN models. 
4. dynamic DNN (skip region, skip layer, early exit)

### Scheduling
1. statically at design time vs dynamically at runtime
2. software based vs hardware based
thoughts: systems that favors flexibility and dynamism adopt dynamic scheduling.
 pros: random/dynamic DNN task can be served.
systems that favors customization and performance adopt static scheduling. 
 pros: globally optimzed performance (suboptimal mapping of one task can lead global optimization)
 pros2: predictability
 cons: dnn workloads should be known a priori

### CGRA
1. Hardware abstractions of the CGRA are needed to 
CGRA can serve both server accelerator and edge system.


## Ideas

### Application

How to optimize
1. Optimization at computation graph.
    - lower DNN into computation graph and do hardware-agnostic optimization (e.g. layer fusion)
    - Can we do something smart for multi-DNN workloads? (Optimize two disjoint DAGs (DNNS))
2. Hardware-aweare optimization
    - Prepare variants of each task. 


### Scheduler
1. How to statically schedule if workloads are pre-determined.
2. How to abstract task so that CGRA can dynamically schedule each task
3. It would be good if CGRA can do both and choose one depending on the situation.
4. How to synchronize if there is communication between tasks (barriers?)


### Hardware
1. It's hard to abstract CGRA resources 
    - PE/GLB/Bandwidth abstraction with capacity/number is something already used by fixed-function accelerators. e.g. interstellar, matestro. What can be CGRA specific abstraction? Rich routability and interconnect should be abstracted as well.
    - Graph representation of CGRA can be used. (Where each node represents PE, and edge represents connection)
2. How can we exploit flexibility of CGRA to improve performance as much as possible to make it competitive to ASIC (e.g. 5x area, 3x power?)
3. Do we need Instructions

## Related Future Research
Using CGRA abstractions and workload descriptions, we can do DSE to find optimal architecture for multi-dnn complex workload scenarios.
Hierarchical CGRA, multi-length interconnect
graph-analysis based mathmatical optimization approach for DSE
Dataflow overlay vs mapping/pnr
Can we do some polyhedral analysis to map multiple tasks simulatenously on the same memory unit instaed of space sharing it?!
Compute/Reconfig/Compute/Reconfig
Edge case: dynamically change dataflow