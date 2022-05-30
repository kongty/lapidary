from re import T
import pandas as pd
import pathlib
import os
from typing import Union, List
from lapidary.task import Task
import logging
logger = logging.getLogger(__name__)


class Logger:
    def __init__(self) -> None:
        self.task_list: List[Task] = []
        self.task_df = pd.DataFrame(columns=['tag', 'query', 'query_id', 'task',
                                    'ts_dispatch', 'ts_queue', 'ts_schedule', 'ts_done', 'prr'])

    def add_task(self, task: Task) -> None:
        self.task_list.append(task)

    def remove_task(self, task: Task) -> None:
        self.task_list.remove(task)

    def load_task_df(self, csv: Union[str, pathlib.Path]) -> None:
        with open(csv) as f:
            # Ignore delimiter in the bracket
            self.task_df = pd.read_csv(f, delimiter=',(?![^\[]*[\]])', engine='python')  # noqa
        self.task_df.set_index('tag', inplace=True)
        prr_to_list = self.task_df['prr'].map(eval)
        self.task_df['prr'] = prr_to_list

    def update_df(self) -> None:
        task_dict = {'tag': [task.tag for task in self.task_list],
                     'query': [task.query_name for task in self.task_list],
                     'query_id': [task.query_id for task in self.task_list],
                     'task': [task.name for task in self.task_list],
                     'ts_dispatch': [task.ts_dispatch for task in self.task_list],
                     'ts_queue': [task.ts_queue for task in self.task_list],
                     'ts_schedule': [task.ts_schedule for task in self.task_list],
                     'ts_done': [task.ts_done for task in self.task_list],
                     'prr': [[prr.id for prr in task.prrs] for task in self.task_list]}
        self.task_df = pd.DataFrame(data=task_dict)
        self.task_df.set_index('tag', inplace=True)

    def dump_task_df(self, filename: str) -> None:
        self.update_df()
        filename = os.path.realpath(filename)
        logger.info(f"A log file was generated: {filename}")
        self.task_df.to_csv(filename)

    def calculate_utilization(self) -> float:
        pass
