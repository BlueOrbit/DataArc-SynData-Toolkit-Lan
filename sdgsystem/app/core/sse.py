"""SSE (Server-Sent Events) utilities."""
import json
import asyncio
import logging
from typing import AsyncGenerator, TYPE_CHECKING
from queue import Queue, Empty

if TYPE_CHECKING:
    from .progress import TrainProgressReporter

logger = logging.getLogger(__name__)


async def sdg_event_stream(event_queue: Queue) -> AsyncGenerator[str, None]:
    """
    Generate SSE events from a queue for SDG jobs.

    Args:
        event_queue: Queue containing (event_type, data) tuples

    Yields:
        SSE formatted strings
    """
    logger.info("[SSE] SDG connection opened, starting event stream")
    while True:
        try:
            event_type, data = event_queue.get_nowait()
            logger.info(f"[SSE] Emitting event: {event_type}")
            logger.debug(f"[SSE] Event data: {data}")
            yield format_sse(event_type, data)

            # Stop streaming on terminal events
            if event_type in ("complete", "cancelled", "generation_complete", "error"):
                logger.info(f"[SSE] Terminal event '{event_type}', closing connection")
                break

        except Empty:
            await asyncio.sleep(0.1)
            continue


async def train_event_stream(reporter: "TrainProgressReporter") -> AsyncGenerator[str, None]:
    """
    Generate SSE events for training job by polling log list.

    Args:
        reporter: Training progress reporter with log buffer

    Yields:
        SSE formatted strings
    """
    from ..api.schemas import TrainJobStatus

    log_position = 0
    keepalive_counter = 0

    while True:
        # Get new logs since last position
        new_logs, log_position = reporter.get_logs_from(log_position)
        for line in new_logs:
            if line.strip():  # Skip empty lines
                yield f"event: log\ndata: {json.dumps(line)}\n\n"
                keepalive_counter = 0

        # Check job status for terminal states
        status = reporter.job.status
        if status == TrainJobStatus.COMPLETED:
            yield format_sse("complete", reporter.job.model_dump())
            break
        elif status == TrainJobStatus.FAILED:
            yield format_sse("error", reporter.job.model_dump())
            break
        elif status == TrainJobStatus.CANCELLED:
            yield format_sse("cancelled", reporter.job.model_dump())
            break

        # Wait briefly and send keepalive periodically
        await asyncio.sleep(0.1)
        keepalive_counter += 1
        if keepalive_counter >= 300:  # ~30 seconds
            yield ": keepalive\n\n"
            keepalive_counter = 0


def format_sse(event_type: str, data: dict) -> str:
    """Format data as SSE event string."""
    json_data = json.dumps(data, default=str)
    return f"event: {event_type}\ndata: {json_data}\n\n"
