"""Training service for API - thin wrapper around TrainingLauncher."""
import logging
from typing import Optional, Callable

from ...trainer.config import get_config_class
from ...trainer.launcher import TrainingLauncher
from ...trainer.methods.sft import SFTMethod
from ...trainer.methods.grpo import GRPOMethod

logger = logging.getLogger(__name__)


class TrainingService:
    """Service to run training jobs with log streaming."""

    def __init__(self, config_dict: dict, verl_path: Optional[str] = None):
        """
        Initialize training service.

        Args:
            config_dict: Training configuration dictionary
            verl_path: Optional path to verl installation
        """
        if "method" not in config_dict:
            raise ValueError("Config must specify 'method' field")

        self.method = config_dict["method"]

        # Create typed config
        config_class = get_config_class(self.method)
        self.config = config_class(**config_dict)

        # Create launcher
        self._launcher = TrainingLauncher(verl_path=verl_path)

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate the training configuration."""
        if self.method == "sft":
            return SFTMethod.validate_config(self.config)
        elif self.method == "grpo":
            return GRPOMethod.validate_config(self.config)
        return False, f"Unsupported method: {self.method}"

    def run_sft(self, log_callback: Optional[Callable[[str], None]] = None) -> int:
        """Run SFT training with log streaming."""
        return self._launcher.run_sft(self.config, log_callback)

    def run_grpo(self, log_callback: Optional[Callable[[str], None]] = None) -> int:
        """Run GRPO training with log streaming."""
        return self._launcher.run_grpo(self.config, log_callback)

    def cancel(self) -> bool:
        """Cancel the running training process."""
        return self._launcher.cancel()
