from util.logger import Logger
import tempfile
from .test_configs import task_log


def test_parse_csv():
    task_logger = Logger()
    with tempfile.NamedTemporaryFile(mode='w+t') as tmp:
        tmp.writelines(task_log)
        tmp.seek(0)
        task_logger.load_task_df(tmp.name)

        assert task_logger.task_df.loc['query_0_#0_task_0']['query'] == 'query_0'
        assert task_logger.task_df.loc['query_0_#0_task_0']['prr0'] == 1
        assert task_logger.task_df.loc['query_0_#0_task_0']['prr1'] == 0
        assert task_logger.task_df.loc['query_3_#0_task_0']['query'] == 'query_3'
        assert task_logger.task_df.loc['query_3_#0_task_0']['prr2'] == 0
        assert task_logger.task_df.loc['query_3_#0_task_0']['prr3'] == 1
