"""Pydantic schemas for the SDG API."""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel


# =============================================================================
# SDG Job Schemas
# =============================================================================

class SDGTaskType(str, Enum):
    LOCAL = "local"
    WEB = "web"
    DISTILL = "distill"

class SDGJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    GENERATION_COMPLETE = "generation_complete"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SDGPhaseStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SDGStepStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"


class SDGProgress(BaseModel):
    completed: int
    total: int
    unit: str


class SDGBatch(BaseModel):
    current: int
    total: int
    size: int


class SDGCurrentItem(BaseModel):
    name: str
    index: Optional[int] = None
    info: Optional[Dict[str, Any]] = None


class SDGUsage(BaseModel):
    tokens: int
    time: float
    estimated_remaining_tokens: Optional[int] = None
    estimated_remaining_time: Optional[float] = None


class SDGJobError(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class SDGJobOutputCounts(BaseModel):
    raw: Optional[int] = None
    solved: Optional[int] = None
    learnable: Optional[int] = None
    unsolved: Optional[int] = None


class SDGJobOutput(BaseModel):
    raw_dataset: Optional[str] = None
    solved: Optional[str] = None
    learnable: Optional[str] = None
    unsolved: Optional[str] = None
    counts: Optional[SDGJobOutputCounts] = None


class SDGPhase(BaseModel):
    id: str  # "generation" | "refinement"
    name: str
    status: SDGPhaseStatus
    current_step_index: int
    total_steps: int


class SDGStep(BaseModel):
    id: str
    name: str
    status: SDGStepStatus = SDGStepStatus.RUNNING
    message: Optional[str] = None
    progress: Optional[SDGProgress] = None
    batch: Optional[SDGBatch] = None
    current_item: Optional[SDGCurrentItem] = None
    usage: Optional[SDGUsage] = None
    result: Optional[Dict[str, Any]] = None


class SDGJob(BaseModel):
    job_id: str
    task_type: SDGTaskType
    task_name: str
    status: SDGJobStatus
    created_at: datetime
    updated_at: datetime
    phase: Optional[SDGPhase] = None
    step: Optional[SDGStep] = None
    error: Optional[SDGJobError] = None
    output: Optional[SDGJobOutput] = None


# =============================================================================
# Training Schemas
# =============================================================================

class TrainMethod(str, Enum):
    SFT = "sft"
    GRPO = "grpo"


class TrainJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TrainJobError(BaseModel):
    code: str
    message: str


class TrainJob(BaseModel):
    """Training job model."""
    job_id: str
    method: TrainMethod
    status: TrainJobStatus
    created_at: datetime
    updated_at: datetime
    config: Dict[str, Any]
    error: Optional[TrainJobError] = None
    output_dir: Optional[str] = None
    wandb_url: Optional[str] = None


class HuggingFaceUploadRequest(BaseModel):
    """Request schema for uploading model to HuggingFace."""
    hf_token: str
    repo_id: str  # e.g., "username/model-name"
    private: bool = False
    commit_message: Optional[str] = None  # Custom commit message


class HuggingFaceUploadResponse(BaseModel):
    """Response schema for HuggingFace upload."""
    job_id: str
    repo_id: str
    repo_url: str

