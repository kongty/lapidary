from lapidary.accelerator import AcceleratorConfigType


query_config = {
    'dist': 'manual',
    'dist_start': 0,
    'dist_interval': [1, 1],
    'tasks': {
        'task_0': {
            'app': 'app',
            'dependencies': ['task_1']
        },
        'task_1': {
            'app': 'app',
            'dependencies': []
        }
    }
}

accelerator_config = AcceleratorConfigType(
    {
        'name': 'accelerator',
        'num_glb_banks': 32,
        'num_prr_height': 4,
        'num_prr_width': 4,
        'prr': {
            'height': 8,
            'width': 8,
            'num_input': 4,
            'num_output': 4
        }
    }
)

task_log = """tag,query,query_id,task,ts_dispatch,ts_queue,ts_schedule,ts_done,prr
query_0_#0_task_0,query_0,0,task_0,0,0,5,105,[(0, 0)]
query_1_#0_task_0,query_1,0,task_0,0,0,5,105,[(1, 0)]
query_2_#0_task_0,query_2,0,task_0,0,0,5,105,[(2, 0)]
query_3_#0_task_0,query_3,0,task_0,0,0,5,105,[(3, 0)]
"""
