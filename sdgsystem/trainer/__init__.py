"""
Training module for post-training models using synthetic data.

This module provides a clean interface to launch training jobs (SFT, GRPO)
using the verl framework, with data format conversion from SDG pipeline outputs.
"""

from .config import SFTConfig, GRPOConfig, load_training_config, get_config_class
from .launcher import TrainingLauncher, run_training_from_config
from .data_preprocessing import jsonl_to_parquet, prepare_grpo_data

__all__ = [
    "SFTConfig",
    "GRPOConfig",
    "TrainingLauncher",
    "load_training_config",
    "get_config_class",
    "run_training_from_config",
    "jsonl_to_parquet",
    "prepare_grpo_data",
]
