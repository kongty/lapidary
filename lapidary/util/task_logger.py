import pandas as pd
import pathlib
from typing import Union, List, Dict
from lapidary.task import Task
from lapidary.instruction import Instruction
import logging
import yaml
logger = logging.getLogger(__name__)


class TaskLogger:
    def __init__(self, num_prr: int = 16) -> None:
        self.task_list: List[Task] = []
        self.instruction_list: List[Instruction] = []

        self.num_prr = num_prr

        # self.task_df - pd.DataFrame(columns=['tag', ])
        self.kernel_df = pd.DataFrame(columns=['tag', 'query', 'query_id', 'task',
                                               'ts_dispatch', 'ts_queue', 'ts_schedule', 'ts_done', 'prr'])

    def add_task(self, task: Task) -> None:
        self.task_list.append(task)

    def remove_task(self, task: Task) -> None:
        self.task_list.remove(task)

    def load_task_df(self, csv: Union[str, pathlib.Path]) -> None:
        with open(csv) as f:
            # Ignore delimiter in the bracket
            self.kernel_df = pd.read_csv(f, delimiter=',(?![^\[]*[\]])', engine='python')  # noqa
        self.kernel_df.set_index('tag', inplace=True)

    def update_df(self) -> None:
        kernel_dict = {'tag': [task.tag for task in self.task_list],
                       'query': [task.query_name for task in self.task_list],
                       'query_id': [task.query_id for task in self.task_list],
                       'kernel': [task.name for task in self.task_list],
                       'ts_dispatch': [task.ts_dispatch for task in self.task_list],
                       'ts_queue': [task.ts_queue for task in self.task_list],
                       'ts_schedule': [task.ts_schedule for task in self.task_list],
                       'ts_done': [task.ts_done for task in self.task_list]}
        kernel_prr_dict: Dict[str, List[int]] = {}
        for i in range(self.num_prr):
            kernel_prr_dict[f"prr{i}"] = []
        for task in self.task_list:
            for kernel in task.kernels:
                kernel_prr_id = list(map(lambda x: x.id, kernel.prrs))
                for i in range(self.num_prr):
                    if i in kernel_prr_id:
                        kernel_prr_dict[f"prr{i}"].append(1)
                    else:
                        kernel_prr_dict[f"prr{i}"].append(0)

        kernel_dict = {**kernel_dict, **kernel_prr_dict}
        self.kernel_df = pd.DataFrame(data=kernel_dict)
        self.kernel_df.set_index('tag', inplace=True)

    def dump_task_df(self, filename: str) -> None:
        logger.info(f"A task log file was generated: {filename}")
        self.kernel_df.to_csv(filename)

    def calculate_antt(self) -> Dict[str, float]:
        # Turnaround Time (TT) = Waiting Time + Service Time
        # Normalized Turnaround Time (NTT): TT / Service Time
        self.kernel_df['service_time'] = self.kernel_df['ts_done'] - self.kernel_df['ts_schedule']
        self.kernel_df['tt'] = self.kernel_df['ts_done'] - self.kernel_df['ts_queue']
        self.kernel_df['ntt'] = self.kernel_df['tt'] - self.kernel_df['service_time']
        antt_dict = self.kernel_df[['query', 'ntt']].groupby('query').mean()['ntt'].to_dict()
        return antt_dict

    def calculate_stp(self) -> Dict[str, float]:
        df = self.kernel_df.groupby('query')[['query_id', 'ts_done']].agg('max')
        df['stp'] = df['query_id'] / df['ts_done']
        stp_dict = df['stp'].to_dict()
        return stp_dict

    def calculate_utilization(self) -> float:
        prr_utilization = self.calculate_prr_utilization()
        total_utilization = float(sum(prr_utilization.values()) / len(prr_utilization.values()))
        return total_utilization

    def calculate_prr_utilization(self) -> Dict[str, float]:
        result = {}
        start = self.kernel_df['ts_queue'].min()
        end = self.kernel_df['ts_done'].max()
        for i in range(self.num_prr):
            df = self.kernel_df[self.kernel_df[f"prr{i}"] == 1]
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
