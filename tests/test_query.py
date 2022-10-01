import simpy
from lapidary.task_generator import TaskGenerator
from lapidary.task_queue import TaskQueue
from .test_configs import query_config


def test_dispatch():
    env = simpy.Environment()
    task_queue = TaskQueue(env, maxsize=1000)
    query = TaskGenerator(env, 'query', query_config)
    query.set_task_queue(task_queue=task_queue)

    def run_dispatch(query):
        yield env.process(query.dispatch())

    env.process(run_dispatch(query))

    env.run(until=2)
    assert task_queue.size == 2

    env.run(until=3)
    assert task_queue.size == 4


def test_topo_sort():
    env = simpy.Environment()
    task_queue = TaskQueue(env, maxsize=10)
    query = TaskGenerator(env, 'query', query_config)
    query.set_task_queue(task_queue=task_queue)

    def run_dispatch(query):
        yield env.process(query.dispatch())

    def get(task_queue):
        task = yield env.process(task_queue.get())
        assert task.name == 'task_1'
        assert env.now == 1

        yield env.timeout(1)
        task = yield env.process(task_queue.get())
        assert task.name == 'task_0'
        assert env.now == 2

    env.process(run_dispatch(query))
    env.process(get(task_queue))

    env.run(until=10)
