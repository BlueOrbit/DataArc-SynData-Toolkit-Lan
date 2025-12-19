"""SDG (Synthetic Data Generation) API endpoints."""
import os
import json
import shutil
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse

from .schemas import SDGJob
from ..core.job_manager import sdg_job_manager
from ..core.sse import sdg_event_stream
from ..services import SDGService

router = APIRouter(prefix="/api/sdg", tags=["sdg"])

# Fixed directories for uploaded files
UPLOAD_DIR = "./dataset"
DOCUMENTS_DIR = os.path.join(UPLOAD_DIR, "documents")
DEMO_EXAMPLES_PATH = os.path.join(UPLOAD_DIR, "demo_examples.jsonl")
BUFFER_DIR = "./buffer"


def _clear_upload_dir():
    """Clear the upload directory."""
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)


def _clear_buffer_dir():
    """Clear the buffer directory."""
    if os.path.exists(BUFFER_DIR):
        shutil.rmtree(BUFFER_DIR)


def _save_file(file: UploadFile, target_path: str) -> str:
    """Save a single uploaded file to the target path."""
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "wb") as f:
        content = file.file.read()
        f.write(content)
    return target_path


def _inject_document_dir(config: dict, document_dir: str) -> dict:
    """Inject document_dir into config for local task."""
    if "task" not in config:
        config["task"] = {}
    if "local" not in config["task"]:
        config["task"]["local"] = {}
    if "parsing" not in config["task"]["local"]:
        config["task"]["local"]["parsing"] = {}

    config["task"]["local"]["parsing"]["document_dir"] = document_dir
    return config


def _inject_demo_examples_path(config: dict, demo_examples_path: str) -> dict:
    """Inject demo_examples_path into config."""
    if "task" not in config:
        config["task"] = {}
    config["task"]["demo_examples_path"] = demo_examples_path
    return config


@router.post("")
async def create_job(
    config: str = Form(...),
    documents: Optional[List[UploadFile]] = File(default=None),
    demo_examples: Optional[UploadFile] = File(default=None)
):
    """Create a new job with config and optional file uploads.

    Args:
        config: JSON string containing the job configuration
        documents: Optional list of PDF files for local task parsing
        demo_examples: Optional single JSONL file with demo examples

    Returns:
        job_id of the created job
    """
    # Clear buffer directory for fresh start
    _clear_buffer_dir()

    # Parse config JSON
    try:
        config_dict = json.loads(config)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "invalid_json",
                    "message": f"Invalid JSON in config: {str(e)}",
                    "details": {"type": "JSONDecodeError"}
                }
            }
        )

    # Handle file uploads
    if documents or demo_examples:
        _clear_upload_dir()

        # Save PDF documents
        if documents:
            for doc in documents:
                if doc.filename:
                    _save_file(doc, os.path.join(DOCUMENTS_DIR, doc.filename))
            config_dict = _inject_document_dir(config_dict, DOCUMENTS_DIR)

        # Save demo examples
        if demo_examples:
            _save_file(demo_examples, DEMO_EXAMPLES_PATH)
            config_dict = _inject_demo_examples_path(config_dict, DEMO_EXAMPLES_PATH)

    task_config = config_dict.get("task", {})
    task_type = task_config.get("task_type", "local")
    task_name = task_config.get("name", "unnamed")

    reporter = sdg_job_manager.create_job(task_type=task_type, task_name=task_name)

    # Create and store service for later phases
    try:
        sdg_service = SDGService(config_dict)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "invalid_config",
                    "message": str(e),
                    "details": {"type": type(e).__name__}
                }
            }
        )

    sdg_job_manager.set_service(sdg_service)

    return {"job_id": reporter.job_id}


@router.post("/{job_id}/generate", response_class=StreamingResponse)
async def start_generation(job_id: str):
    """Start generation phase and return SSE stream."""
    reporter = sdg_job_manager.get_job(job_id)
    if not reporter:
        raise HTTPException(status_code=404, detail="Job not found")

    if reporter.job.status != "pending":
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "invalid_state",
                    "message": "Job must be in 'pending' status to start generation",
                    "details": {"current_status": reporter.job.status}
                }
            }
        )

    sdg_service = sdg_job_manager.current_service
    if not sdg_service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Start job execution in background
    sdg_job_manager.run_job(reporter, sdg_service.run_generation)

    return StreamingResponse(
        sdg_event_stream(reporter.get_event_queue()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/{job_id}/refine", response_class=StreamingResponse)
async def start_refinement(job_id: str):
    """Start refinement phase after generation completes."""
    reporter = sdg_job_manager.get_job(job_id)
    if not reporter:
        raise HTTPException(status_code=404, detail="Job not found")

    if reporter.job.status != "generation_complete":
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "invalid_state",
                    "message": "Job must be in 'generation_complete' status",
                    "details": {"current_status": reporter.job.status}
                }
            }
        )

    sdg_service = sdg_job_manager.current_service
    if not sdg_service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Reset event queue for fresh SSE stream
    event_queue = reporter.reset_for_phase()

    sdg_job_manager.run_job(reporter, sdg_service.run_refinement)

    return StreamingResponse(
        sdg_event_stream(event_queue),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str) -> SDGJob:
    """Cancel a running job."""
    # TODO
    if not sdg_job_manager.cancel_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found or not running")

    reporter = sdg_job_manager.get_job(job_id)
    return reporter.job


@router.get("/{job_id}/download/{file_type}")
async def download_file(job_id: str, file_type: str):
    """Download result files."""
    reporter = sdg_job_manager.get_job(job_id)
    if not reporter:
        raise HTTPException(status_code=404, detail="Job not found")

    output = reporter.job.output
    if not output:
        raise HTTPException(status_code=404, detail="No output available")

    valid_file_types = ["raw", "solved", "learnable", "unsolved"]
    if file_type not in valid_file_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file_type}")

    file_map = {
        "raw": output.raw_dataset,
        "solved": output.solved,
        "learnable": output.learnable,
        "unsolved": output.unsolved
    }

    file_path = file_map.get(file_type)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not available: {file_type}")

    return FileResponse(
        file_path,
        filename=os.path.basename(file_path),
        media_type="application/octet-stream"
    )
