09/08/2022 -- Random Ideas
----------------------------

- The Research Goal.
Maximum flexibility of CGRA that serves Multi-DNN workloads on both cloud and edge.

Multi-DNN scenario is diverse.
1. multi-tenancy (independent, different requirement)
2. one application with multi-DNN (synchronization, autonomous vehicle)
3. dynamic DNN 

Scheduling can be diverse
1. statically at design time vs dynamically at runtime
2. temporal multiplexing or/and spatial multiplexing
3. software based vs hardware based
thoughts: systems that favors flexibility and dynamism adopt dynamic scheduling.
 pros: random/dynamic DNN task can be served.
systems that favors customization and performance adopt static scheduling. 
 pros: globally optimzed performance (suboptimal mapping of one task can lead global optimization)
 pros2: predictability
 cons: dnn workloads should be known a priori


CGRA can serve both server accelerator and edge system.


- Random Questions
1. When workload is determined in advance, we can pretty much analyze resource usage and statically schedule each task.
   For example, let's say there are DNN1 with computation graph A-B-C, and DNN2 with computation graph D-E-F.
   If we know 
2. For better scheduling, workload needs to be abstracted better than just the number of hardware resource usage.


Another research
CGRA DSE framework.