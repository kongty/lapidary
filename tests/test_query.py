import simpy
from lapidary.query import Query
from lapidary.task_queue import TaskQueue


def test_dispatch():
    env = simpy.Environment()
    query_config = {
        'dist': 'fixed',
        'dist_start': 0,
        'dist_interval': 1,
        'dist_size': 5,
        'tasks': {
            'task_0': {
                'app': 'app_0',
                'dependencies': []
            }
        }
    }
    task_queue = TaskQueue(env, maxsize=1000)
    query = Query(env, 'query', query_config)

    def run_dispatch(query):
        yield env.process(query.dispatch(task_queue))

    env.process(run_dispatch(query))

    env.run(until=1)
    assert task_queue.size == 1

    env.run(until=5)
    assert task_queue.size == 5
