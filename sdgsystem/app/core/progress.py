"""Progress reporters for tracking and broadcasting job progress via SSE."""
import time
from datetime import datetime
from typing import Optional, Dict, Any
from queue import Queue

from ..api.schemas import (
    SDGJob, SDGJobStatus, SDGPhase, SDGPhaseStatus, SDGStep, SDGStepStatus,
    SDGProgress, SDGBatch, SDGCurrentItem, SDGUsage, SDGJobError, SDGJobOutput,
    TrainJob, TrainJobStatus, TrainMethod, TrainJobError
)


class SDGProgressReporter:
    """Reports progress to SSE stream."""

    def __init__(
        self,
        job_id: str,
        task_type: str,
        task_name: str,
        throttle_interval: float = 0.5
    ):
        self.job_id = job_id
        self.task_type = task_type
        self.task_name = task_name
        self.throttle_interval = throttle_interval

        self._event_queue: Queue = Queue()
        self._last_emit_time = 0.0
        self._cancelled = False

        self._job = SDGJob(
            job_id=job_id,
            task_type=task_type,
            task_name=task_name,
            status=SDGJobStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    @property
    def job(self) -> SDGJob:
        return self._job

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

    def get_event_queue(self) -> Queue:
        return self._event_queue

    def reset_for_phase(self) -> Queue:
        """Reset event queue for a new SSE stream (new phase)."""
        self._event_queue = Queue()
        return self._event_queue

    def cancel(self):
        """Mark job as cancelled."""
        self._cancelled = True
        self._job.status = SDGJobStatus.CANCELLED
        if self._job.phase:
            self._job.phase.status = SDGPhaseStatus.FAILED
        self._emit("cancelled", force=True)

    def emit_created(self):
        """Emit created event."""
        self._emit("created", force=True)

    def start_phase(self, phase_id: str, name: str, total_steps: int):
        """Start a new phase."""
        self._job.status = SDGJobStatus.RUNNING
        self._job.phase = SDGPhase(
            id=phase_id,
            name=name,
            status=SDGPhaseStatus.RUNNING,
            current_step_index=0,
            total_steps=total_steps
        )
        self._job.step = None
        self._emit("progress")

    def start_step(
        self,
        step_id: str,
        name: str,
        message: Optional[str] = None,
        total: Optional[int] = None,
        unit: Optional[str] = None
    ):
        """Start a new step within current phase."""
        if self._job.phase:
            self._job.phase.current_step_index += 1

        progress = SDGProgress(completed=0, total=total, unit=unit) if total else None

        self._job.step = SDGStep(
            id=step_id,
            name=name,
            message=message,
            progress=progress
        )
        self._emit("progress", force=True)

    def update_step(
        self,
        message: Optional[str] = None,
        completed: Optional[int] = None,
        batch_current: Optional[int] = None,
        batch_total: Optional[int] = None,
        batch_size: Optional[int] = None,
        current_item_name: Optional[str] = None,
        current_item_index: Optional[int] = None,
        current_item_info: Optional[Dict[str, Any]] = None,
        tokens: Optional[int] = None,
        time_elapsed: Optional[float] = None,
        estimated_remaining_tokens: Optional[int] = None,
        estimated_remaining_time: Optional[float] = None,
        result: Optional[Dict[str, Any]] = None,
        force: bool = False
    ):
        """Update current step progress."""
        if not self._job.step:
            return

        if message is not None:
            self._job.step.message = message

        if completed is not None and self._job.step.progress:
            self._job.step.progress.completed = completed

        if batch_current is not None:
            self._job.step.batch = SDGBatch(
                current=batch_current,
                total=batch_total or 0,
                size=batch_size or 0
            )

        if current_item_name is not None:
            self._job.step.current_item = SDGCurrentItem(
                name=current_item_name,
                index=current_item_index,
                info=current_item_info
            )

        if tokens is not None or time_elapsed is not None:
            self._job.step.usage = SDGUsage(
                tokens=tokens or 0,
                time=time_elapsed or 0.0,
                estimated_remaining_tokens=estimated_remaining_tokens,
                estimated_remaining_time=estimated_remaining_time
            )

        if result is not None:
            self._job.step.result = result

        self._emit("progress", force=force)

    def complete_step(self, result: Optional[Dict[str, Any]] = None):
        """Mark current step as complete."""
        if self._job.step:
            self._job.step.status = SDGStepStatus.COMPLETED
            if result:
                self._job.step.result = result
        self._emit("progress", force=True)

    def complete_phase(self, output: Optional[SDGJobOutput] = None):
        """Mark current phase as complete."""
        if self._job.phase:
            self._job.phase.status = SDGPhaseStatus.COMPLETED

        if output:
            self._job.output = output

        if self._job.phase and self._job.phase.id == "generation":
            self._job.status = SDGJobStatus.GENERATION_COMPLETE
            event_type = "generation_complete"
        else:
            self._job.status = SDGJobStatus.COMPLETED
            event_type = "complete"

        self._job.step = None
        self._emit(event_type, force=True)

    def fail(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Mark job as failed."""
        self._job.status = SDGJobStatus.FAILED
        self._job.error = SDGJobError(code=code, message=message, details=details)
        if self._job.phase:
            self._job.phase.status = SDGPhaseStatus.FAILED
        self._emit("error", force=True)

    def set_output(self, output: SDGJobOutput):
        """Set job output."""
        self._job.output = output

    def _emit(self, event_type: str, force: bool = False):
        """Emit event to queue."""
        now = time.time()

        if not force and (now - self._last_emit_time) < self.throttle_interval:
            return

        self._last_emit_time = now
        self._job.updated_at = datetime.now()
        self._event_queue.put((event_type, self._job.model_dump()))


class TrainProgressReporter:
    """Manages training job state and log streaming."""

    def __init__(self, job_id: str, method: str, config: dict):
        self.job_id = job_id
        self._log_lines: list[str] = []
        self._cancelled = False

        self._job = TrainJob(
            job_id=job_id,
            method=TrainMethod(method),
            status=TrainJobStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            config=config,
            output_dir=config.get("output_dir"),
        )

    @property
    def job(self) -> TrainJob:
        return self._job

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

    def get_logs_from(self, position: int) -> tuple[list[str], int]:
        """Get logs from position. Returns (new_logs, new_position)."""
        logs = self._log_lines[position:]
        return logs, len(self._log_lines)

    def add_log(self, line: str):
        """Add a log line."""
        self._log_lines.append(line)

    def set_running(self):
        """Mark job as running."""
        self._job.status = TrainJobStatus.RUNNING
        self._job.updated_at = datetime.now()

    def complete(self):
        """Mark job as completed."""
        self._job.status = TrainJobStatus.COMPLETED
        self._job.updated_at = datetime.now()

    def fail(self, code: str, message: str):
        """Mark job as failed."""
        self._job.status = TrainJobStatus.FAILED
        self._job.error = TrainJobError(code=code, message=message)
        self._job.updated_at = datetime.now()

    def cancel(self):
        """Mark job as cancelled."""
        self._cancelled = True
        self._job.status = TrainJobStatus.CANCELLED
        self._job.updated_at = datetime.now()
