from typing import List

from ..configs.config import SDGSTaskConfig
from ..models import ModelClient
from ..dataset.dataset import Dataset
from .base import BaseTaskExecutor
from .local import LocalTaskExecutor
from .web import WebTaskExecutor
from .distill import DistillTaskExecutor


class TaskExecutor:
    def __init__(self, 
        config: SDGSTaskConfig, 
        llm: ModelClient
    ) -> None:
        self.config = config
        self.executor: BaseTaskExecutor = TaskExecutor.get_executors(llm, self.config)

    @staticmethod
    def get_executors(llm: ModelClient, config: SDGSTaskConfig) -> List[BaseTaskExecutor]:
        executor: BaseTaskExecutor = None

        if config.task_type == "local":
            sub_config = config.local_task_config
            executor = LocalTaskExecutor(sub_config, llm)

        elif config.task_type == "web":
            sub_config = config.web_task_config
            executor = WebTaskExecutor(sub_config, llm)

        elif config.task_type == "distill":
            sub_config = config.distill_task_config
            executor = DistillTaskExecutor(sub_config, llm)

        else:
            raise Exception(f"no task type of {config.task_type}")

        return executor

    def execute(self, parallel_executor=None, reporter=None) -> Dataset:
        dataset = Dataset()

        # WebTaskExecutor doesn't use parallel_executor
        if self.config.task_type == "web":
            dataset.extend(self.executor.execute(reporter=reporter))
        else:
            dataset.extend(self.executor.execute(parallel_executor=parallel_executor, reporter=reporter))

        return dataset