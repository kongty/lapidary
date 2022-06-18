import pandas as pd
import pathlib
from typing import Union, List, Tuple, Dict
from vault.task import Task
import logging
import yaml
logger = logging.getLogger(__name__)


class Logger:
    def __init__(self, num_prr: int = 16) -> None:
        self.task_list: List[Task] = []
        self.num_prr = num_prr
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

    def update_df(self) -> None:
        task_dict = {'tag': [task.tag for task in self.task_list],
                     'query': [task.query_name for task in self.task_list],
                     'query_id': [task.query_id for task in self.task_list],
                     'task': [task.name for task in self.task_list],
                     'ts_dispatch': [task.ts_dispatch for task in self.task_list],
                     'ts_queue': [task.ts_queue for task in self.task_list],
                     'ts_schedule': [task.ts_schedule for task in self.task_list],
                     'ts_done': [task.ts_done for task in self.task_list]}
        task_prr_dict: Dict[str, List[int]] = {}
        for i in range(self.num_prr):
            task_prr_dict[f"prr{i}"] = []
        for task in self.task_list:
            task_prr_id = list(map(lambda x: x.id, task.prrs))
            for i in range(self.num_prr):
                if i in task_prr_id:
                    task_prr_dict[f"prr{i}"].append(1)
                else:
                    task_prr_dict[f"prr{i}"].append(0)

        task_dict = {**task_dict, **task_prr_dict}
        self.task_df = pd.DataFrame(data=task_dict)
        self.task_df.set_index('tag', inplace=True)

    def dump_task_df(self, filename: str) -> None:
        logger.info(f"A task log file was generated: {filename}")
        self.task_df.to_csv(filename)

    def calculate_utilization(self) -> float:
        prr_utilization = self.calculate_prr_utilization()
        total_utilization = float(sum(prr_utilization.values()) / len(prr_utilization.values()))
        return total_utilization

    def calculate_prr_utilization(self) -> Dict[str, float]:
        result = {}
        start = self.task_df['ts_queue'].min()
        end = self.task_df['ts_done'].max()
        for i in range(self.num_prr):
            df = self.task_df[self.task_df[f"prr{i}"] == 1]
            runtime_col = df['ts_done'] - df['ts_schedule']
            total_runtime = runtime_col.sum()
            utilization = float(total_runtime / (end - start))
            result[f"prr{i}"] = utilization

        return result

    def dump_perf(self, filename: str) -> None:
        logger.info(f"A perf file was generated: {filename}")
        log = {}
        log['utilization'] = self.calculate_utilization()
        log = {**log, **self.calculate_prr_utilization()}
        with open(filename, 'w') as f:
            yaml.dump(log, f, default_flow_style=False)
