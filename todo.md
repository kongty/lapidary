## TODO
- Report SLA metrics
- Add app queue
- Add offchip bandwidth requirement to kernel
- Add deadline to each task
- Change terms (app, job, task, kernel)
- Make app as configuration file
- Make it DNN specific by changing  AppConfig class to reflect input/kernel/output or DNN specific params

- Implement interrupt for proc_schedule, so that it stops scheduling when new task arrives. 
- hierarchical logger (task->kernel->instruction)
- Convert kernel list to kernel graph