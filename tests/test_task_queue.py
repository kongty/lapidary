import pytest
import simpy
from lapidary.task_queue import TaskQueue
from lapidary.task import Task


@pytest.mark.parametrize('maxsize', [5, 10])
@pytest.mark.parametrize('num_tasks', [3, 8])
def test_task_queue_put(maxsize: int, num_tasks: int):
    env = simpy.Environment()
    task_queue = TaskQueue(env, maxsize=maxsize)

    for _ in range(num_tasks):
        task = Task(env, query_name='query', query_id=0, task_name='task', app='app', deps=[])
        env.process(task_queue.put(task))

    env.run(until=100)
    assert task_queue.size == min(num_tasks, maxsize)


def test_task_queue_block():
    env = simpy.Environment()
    maxsize = 2
    task_queue = TaskQueue(env, maxsize=maxsize)
    log = []

    def put(env, task_queue, task, log):
        tasks = yield env.process(task_queue.put(task))
        for task in tasks:
            log.append((task.name, env.now))

    def get(env, task_queue):
        yield env.timeout(5)
        yield env.process(task_queue.get())

    for i in range(maxsize + 1):
        task = Task(env, query_name='query', query_id=0, task_name=i, app='app', deps=[])
        env.process(put(env, task_queue, task, log))

    env.process(get(env, task_queue))
    env.run()

    assert log == [(0, 0), (1, 0), (2, 5)]
