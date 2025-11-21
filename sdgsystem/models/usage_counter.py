"""
Statistic and estimation for the token and time usage when using models
"""

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



class ModelUsageCounter:
    """Token and Time counter for counting and estimating usage."""
    
    def __init__(self, 
        total: int = 0, 
        name: str = "Model"
    ) -> None:
        """
        Initialize token and time counter

        Args:
            total: Anticipated number of each iteration unit.
            name: The module name used for identification when using logging.info: 
                [{name} Usage]: completed=XXXX, token=XXXX, time=XXXX || remain=XXXX, remain_token_anticipation=XXXX, remain_time_anticipation=XXXX
        """
        self.name = name
        self.total = total

        self.token: int = 0
        self.time: float = 0        # measured in seconds

        self.completed: int = 0    # number of iteration unit
        self.remain: int = self.total - self.completed     # number of remain iteration unit

    def add_usage(self, 
        n_token: int, 
        time: float,
    ):
        """
        add token and time usage to this counter.
        Args: 
            n_token: token cost
            time: time cost
        """
        self.token += n_token
        self.time += time

    def estimate_usage(self, n):
        """
        estimate the token and time usage of n iteration units
        Args:
            n: the number of iteration units
        """
        self.completed += n
        self.remain -= n

        avg_token = self.token / self.completed
        avg_time = self.time / self.completed

        remain_token_anticipation = int(avg_token * self.remain)
        remain_time_anticipation = int(avg_time * self.remain)

        logger.info(f"[{self.name} Usage]: completed={self.completed}, token={self.token}, time={self.time:.2f} || remain={self.remain}, remain_token_anticipation={remain_token_anticipation}, remain_time_anticipatioin={remain_time_anticipation:.2f}")

    def __str__(self) -> str:
        return f"[{self.name} Usage]: completed={self.completed}, remain={self.remain}, token={self.token}, time={self.time:.2f}"
