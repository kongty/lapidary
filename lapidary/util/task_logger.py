import pandas as pd
import pathlib
from typing import Union, List, Dict, Tuple
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

        self.task_df = pd.DataFrame(columns=['tag', 'task', 'id', 'ts_generate',
                                    'ts_queue', 'ts_done', 'antt', 'latency'])

        self.kernel_df = pd.DataFrame(columns=['tag', 'kernel', 'task', 'task_id',
                                               'ts_generate', 'ts_queue', 'ts_schedule', 'ts_done', 'prr'])

        self.latency: Dict[str, float] = {}
        self.tail_latency: Dict[str, Dict[float, float]] = {}
        # self.stp: float = 0.
        # self.antt: Dict[str, float] = {}
        # self.utilization: Tuple[float, float]

    def add_task(self, task: Task) -> None:
        self.task_list.append(task)

    def remove_task(self, task: Task) -> None:
        self.task_list.remove(task)

    def load_task_df(self, csv: Union[str, pathlib.Path]) -> None:
        raise NotImplementedError("load task not implemented yet")
        # with open(csv) as f:
        #     # Ignore delimiter in the bracket
        #     self.kernel_df = pd.read_csv(f, delimiter=',(?![^\[]*[\]])', engine='python')  # noqa
        # self.kernel_df.set_index('tag', inplace=True)

    def post_process(self) -> None:
        # TODO: Need to change kernel dict and task dict. Need to decide what to store
        # TODO: For now, we just flatten all kernels
        self._generate_task_df()
        self._generate_kernel_df()

        self.update_latency()
        self.update_tail_latency()
        # self.update_antt()
        # self.update_stp()
        # self.update_utilization()

    def _generate_task_df(self) -> None:
        task_dict = {'tag': [task.tag for task in self.task_list],
                     'task': [task.name for task in self.task_list],
                     'id': [task.id for task in self.task_list],
                     'ts_generate': [task.timestamp.generate for task in self.task_list],
                     'ts_queue': [task.timestamp.queue for task in self.task_list],
                     'ts_done': [task.timestamp.done for task in self.task_list]}

        self.task_df = pd.DataFrame(data=task_dict)
        self.task_df.set_index('tag', inplace=True)
        self.task_df['latency'] = self.task_df['ts_done'] - self.task_df['ts_queue']

    def _generate_kernel_df(self) -> None:
        kernel_list = []
        for task in self.task_list:
            kernel_list += task.kernels
        kernel_dict = {'tag': [kernel.tag for kernel in kernel_list],
                       'kernel': [kernel.name for kernel in kernel_list],
                       'task': [kernel.task.name for kernel in kernel_list],
                       'task_id': [kernel.task.id for kernel in kernel_list],
                       'ts_queue': [kernel.task.timestamp.queue for kernel in kernel_list],
                       'ts_schedule': [kernel.timestamp.schedule for kernel in kernel_list],
                       'ts_done': [kernel.timestamp.done for kernel in kernel_list]}

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
        self.task_df.to_csv(filename)

    def dump_kernel_df(self, filename: str) -> None:
        logger.info(f"A kernel log file was generated: {filename}")
        self.kernel_df.to_csv(filename)

    def update_latency(self) -> None:
        for task in self.task_df['task'].unique():
            self.latency[task] = self.task_df.loc[self.task_df['task']
                                                  == task]['latency'].mean()

    def update_tail_latency(self) -> None:
        for task in self.task_df['task'].unique():
            self.tail_latency[task] = self.task_df.loc[self.task_df['task']
                                                       == task]['latency'].quantile([0.95, 0.99]).to_dict()

    # def update_antt(self) -> None:
    #     # Turnaround Time (TT) = Waiting Time + Service Time
    #     # Normalized Turnaround Time (NTT): TT / Service Time
    #     self.kernel_df['service_time'] = self.kernel_df['ts_done'] - self.kernel_df['ts_schedule']
    #     self.kernel_df['tt'] = self.kernel_df['ts_done'] - self.kernel_df['ts_queue']
    #     self.kernel_df['ntt'] = self.kernel_df['tt'] - self.kernel_df['service_time']
    #     antt_dict = self.kernel_df[['query', 'ntt']].groupby('query').mean()['ntt'].to_dict()
    #     self.antt = antt_dict

    # def update_stp(self) -> None:
    #     df = self.kernel_df.groupby('query')[['query_id', 'ts_done']].agg('max')
    #     df['stp'] = df['query_id'] / df['ts_done']
    #     stp_dict = df['stp'].to_dict()

    # def update_utilization(self) -> float:
    #     prr_utilization = self.calculate_prr_utilization()
    #     total_utilization = float(sum(prr_utilization.values()) / len(prr_utilization.values()))
    #     return total_utilization

    # def calculate_prr_utilization(self) -> Dict[str, float]:
    #     result = {}
    #     start = self.kernel_df['ts_queue'].min()
    #     end = self.kernel_df['ts_done'].max()
    #     for i in range(self.num_prr):
    #         df = self.kernel_df[self.kernel_df[f"prr{i}"] == 1]
    #         runtime_col = df['ts_done'] - df['ts_schedule']
    #         total_runtime = runtime_col.sum()
    #         utilization = float(total_runtime / (end - start))
    #         result[f"prr{i}"] = utilization

    #     return result

    def dump_perf(self, filename: str) -> None:
        logger.info(f"A perf file was generated: {filename}")
        log = {}
        log['tail latency'] = self.tail_latency
        # log['utilization'] = self.update_utilization()
        # log = {**log, **self.calculate_prr_utilization()}
        with open(filename, 'w') as f:
            yaml.dump(log, f, default_flow_style=False)
