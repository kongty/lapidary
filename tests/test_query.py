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
                'app': 'app',
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


def test_topo_sort():
    env = simpy.Environment()
    query_config = {
        'dist': 'manual',
        'dist_start': 0,
        'dist_interval': [1],
        'tasks': {
            'task_0': {
                'app': 'app',
                'dependencies': ['task_1']
            },
            'task_1': {
                'app': 'app',
                'dependencies': ['task_2']
            },
            'task_2': {
                'app': 'app',
                'dependencies': []
            }
        }
    }
    task_queue = TaskQueue(env, maxsize=10)
    query = Query(env, 'query', query_config)

    def run_dispatch(query):
        yield env.process(query.dispatch(task_queue))

    def get(task_queue):
        task = yield env.process(task_queue.get())
        assert task.name == 'task_2'
        assert env.now == 1

        yield env.timeout(1)
        task = yield env.process(task_queue.get())
        assert task.name == 'task_1'
        assert env.now == 2

        yield env.timeout(1)
        task = yield env.process(task_queue.get())
        assert task.name == 'task_0'
        assert env.now == 3

    env.process(run_dispatch(query))
    env.process(get(task_queue))

    env.run(until=10)
