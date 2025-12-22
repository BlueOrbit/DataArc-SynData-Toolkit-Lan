"""Training API endpoints."""
import os
import json
import shutil
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse

from .schemas import TrainJobStatus, HuggingFaceUploadRequest, HuggingFaceUploadResponse
from ..core.job_manager import train_job_manager
from ..core.sse import train_event_stream
from ..services.training_service import TrainingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/train", tags=["training"])

# Fixed directories
TRAIN_UPLOAD_DIR = "./dataset/train"
TRAIN_DATASET_PATH = os.path.join(TRAIN_UPLOAD_DIR, "train.jsonl")
VAL_DATASET_PATH = os.path.join(TRAIN_UPLOAD_DIR, "val.jsonl")
CHECKPOINT_DIR = "./checkpoints"
MERGED_MODEL_DIR = "./checkpoints/merged"


def _clear_train_upload_dir():
    """Clear the training upload directory."""
    if os.path.exists(TRAIN_UPLOAD_DIR):
        shutil.rmtree(TRAIN_UPLOAD_DIR)
    os.makedirs(TRAIN_UPLOAD_DIR, exist_ok=True)


def _clear_checkpoint_dir():
    """Clear the checkpoint directory to avoid reloading old checkpoints."""
    if os.path.exists(CHECKPOINT_DIR):
        shutil.rmtree(CHECKPOINT_DIR)
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)


def _save_upload_file(file: UploadFile, target_path: str) -> str:
    """Save an uploaded file to the target path."""
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "wb") as f:
        content = file.file.read()
        f.write(content)
    return target_path


def _validate_jsonl_file(
    file_path: str,
    prompt_key: str,
    response_key: str | None,
    file_label: str = "file"
) -> tuple[bool, str | None]:
    """
    Validate a JSONL file contains required keys.

    Args:
        file_path: Path to the JSONL file
        prompt_key: Required key for prompts
        response_key: Required key for responses (None to skip validation)
        file_label: Label for error messages (e.g., "train_file", "val_file")

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            line_num = 0
            for line in f:
                line = line.strip()
                if not line:
                    continue
                line_num += 1

                try:
                    sample = json.loads(line)
                except json.JSONDecodeError as e:
                    return False, f"{file_label} line {line_num}: Invalid JSON - {e}"

                if not isinstance(sample, dict):
                    return False, f"{file_label} line {line_num}: Expected JSON object, got {type(sample).__name__}"

                if prompt_key not in sample:
                    return False, f"{file_label} line {line_num}: Missing required key '{prompt_key}'"

                if response_key and response_key not in sample:
                    return False, f"{file_label} line {line_num}: Missing required key '{response_key}'"

            if line_num == 0:
                return False, f"{file_label}: File is empty"

        return True, None

    except FileNotFoundError:
        return False, f"{file_label}: File not found"
    except Exception as e:
        return False, f"{file_label}: Failed to read file - {e}"


@router.post("")
async def create_train_job(
    config: str = Form(...),
    train_file: UploadFile = File(...),
    val_file: UploadFile = File(...)
):
    """Create a new training job with config and dataset uploads.

    Args:
        config: JSON string containing the training configuration
        train_file: Training dataset file (.jsonl)
        val_file: Validation dataset file (.jsonl)

    Returns:
        job_id of the created training job
    """
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
                }
            }
        )
    
    # Validate method is present
    if "method" not in config_dict:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "missing_method",
                    "message": "Config must specify 'method' field (sft or grpo)",
                }
            }
        )

    method = config_dict["method"]
    if method not in ["sft", "grpo"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "invalid_method",
                    "message": f"Invalid method: {method}. Supported: sft, grpo",
                }
            }
        )

    # Clear directories and save uploaded files
    _clear_train_upload_dir()
    _clear_checkpoint_dir()
    _save_upload_file(train_file, TRAIN_DATASET_PATH)
    _save_upload_file(val_file, VAL_DATASET_PATH)

    # Get keys from config (with defaults)
    data_config = config_dict.get("data", {})
    prompt_key = data_config.get("prompt_key", "input")
    response_key = data_config.get("response_key", "output")

    # For GRPO with reward model, response_key validation is optional
    method = config_dict.get("method")
    reward_config = config_dict.get("reward", {})
    reward_model_config = reward_config.get("reward_model", {})
    use_reward_model = reward_model_config.get("enable", False)
    validate_response_key = response_key if not use_reward_model else None

    # Validate uploaded JSONL files contain required keys
    is_valid, error = _validate_jsonl_file(
        TRAIN_DATASET_PATH, prompt_key, validate_response_key, "train_file"
    )
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "invalid_dataset",
                    "message": error,
                }
            }
        )

    is_valid, error = _validate_jsonl_file(
        VAL_DATASET_PATH, prompt_key, validate_response_key, "val_file"
    )
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "invalid_dataset",
                    "message": error,
                }
            }
        )

    # Inject dataset paths into config (nested under data)
    if "data" not in config_dict:
        config_dict["data"] = {}
    config_dict["data"]["train_files"] = TRAIN_DATASET_PATH
    config_dict["data"]["val_files"] = VAL_DATASET_PATH

    # Inject fixed checkpoint directory
    if "trainer" not in config_dict:
        config_dict["trainer"] = {}
    config_dict["trainer"]["default_local_dir"] = CHECKPOINT_DIR

    # Create training service and validate config
    try:
        training_service = TrainingService(config_dict)
        is_valid, error = training_service.validate()
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "invalid_config",
                        "message": error,
                    }
                }
            )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "invalid_config",
                    "message": str(e),
                }
            }
        )

    # Create job
    reporter = train_job_manager.create_job(method=method, config=config_dict)
    train_job_manager.set_service(training_service)

    return {"job_id": reporter.job_id}


@router.post("/{job_id}/start", response_class=StreamingResponse)
async def start_training(job_id: str):
    """Start training and return SSE stream.

    If job is pending, starts training and streams logs.
    If job is already running, reconnects and replays all logs then continues streaming.
    """
    reporter = train_job_manager.get_job(job_id)
    if not reporter:
        raise HTTPException(status_code=404, detail="Training job not found")

    status = reporter.job.status

    # Job already completed - return success with status
    if status == TrainJobStatus.COMPLETED:
        return JSONResponse(
            content={"job_id": job_id, "status": "completed", "message": "Job already completed successfully"}
        )

    # Job failed or cancelled - return error
    if status in (TrainJobStatus.FAILED, TrainJobStatus.CANCELLED):
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "job_finished",
                    "message": f"Job already finished with status: {status}",
                }
            }
        )

    # Job is running - reconnect (polling will replay logs automatically)
    if status == TrainJobStatus.RUNNING:
        return StreamingResponse(
            train_event_stream(reporter),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )

    # Job is pending - start training
    training_service = train_job_manager.current_service
    if not training_service:
        raise HTTPException(status_code=404, detail="Training service not found")

    train_job_manager.run_job(reporter, training_service)

    return StreamingResponse(
        train_event_stream(reporter),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.post("/{job_id}/cancel")
async def cancel_training(job_id: str):
    """Cancel a running training job.

    Terminates the training subprocess if running.
    """
    reporter = train_job_manager.get_job(job_id)
    if not reporter:
        raise HTTPException(status_code=404, detail="Training job not found")

    status = reporter.job.status

    # Can only cancel pending or running jobs
    if status not in (TrainJobStatus.PENDING, TrainJobStatus.RUNNING):
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "cannot_cancel",
                    "message": f"Cannot cancel job with status: {status}",
                }
            }
        )

    cancelled = train_job_manager.cancel_job(job_id)
    if not cancelled:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "cancel_failed",
                    "message": "Failed to cancel training job",
                }
            }
        )

    return {"job_id": job_id, "status": "cancelled"}


def _find_latest_checkpoint(checkpoint_dir: str) -> str | None:
    """
    Find the latest checkpoint folder for model merging.

    verl checkpoint structures:

    SFT:
        ./checkpoints/global_step_X/
        ├── model_world_size_1_rank_0.pt
        ├── fsdp_config.json
        └── huggingface/

    GRPO:
        ./checkpoints/global_step_X/
        └── actor/
            ├── model_world_size_1_rank_0.pt
            ├── fsdp_config.json
            └── huggingface/

    Returns:
        Path to the checkpoint folder containing .pt files and huggingface/ subfolder
        (for SFT: global_step_X, for GRPO: global_step_X/actor)
    """
    checkpoint_path = Path(checkpoint_dir)
    if not checkpoint_path.exists():
        return None

    # Find global_step_* folders
    step_folders = list(checkpoint_path.glob("global_step_*"))
    if not step_folders:
        return None

    # Get the latest step folder (by step number)
    def get_step_number(p: Path) -> int:
        try:
            return int(p.name.split("_")[-1])
        except ValueError:
            return 0

    latest_step = max(step_folders, key=get_step_number)

    # Check for GRPO structure (has actor/ subfolder with huggingface/)
    actor_path = latest_step / "actor"
    if actor_path.exists() and (actor_path / "huggingface").exists():
        return str(actor_path)

    # Check for SFT structure (huggingface/ directly in step folder)
    if (latest_step / "huggingface").exists():
        return str(latest_step)

    return None


@router.post("/{job_id}/upload", response_model=HuggingFaceUploadResponse)
async def upload_to_huggingface(job_id: str, request: HuggingFaceUploadRequest):
    """Upload trained model to HuggingFace Hub.

    This endpoint:
    1. Finds the latest checkpoint
    2. Runs verl model merger to convert .pt files to HuggingFace safetensors format
    3. Uploads the merged model to HuggingFace Hub

    Original .pt checkpoint files are preserved.
    Only works for completed training jobs.
    """
    reporter = train_job_manager.get_job(job_id)
    if not reporter:
        raise HTTPException(status_code=404, detail="Training job not found")

    status = reporter.job.status

    # Only allow upload for completed jobs
    if status != TrainJobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "job_not_completed",
                    "message": f"Cannot upload model. Job status: {status}. Only completed jobs can be uploaded.",
                }
            }
        )

    # Find the checkpoint to merge
    checkpoint_path = _find_latest_checkpoint(CHECKPOINT_DIR)
    if not checkpoint_path:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "checkpoint_not_found",
                    "message": f"No valid checkpoint found in {CHECKPOINT_DIR}",
                }
            }
        )

    logger.info(f"Found checkpoint at {checkpoint_path}")

    # Step 1: Run model merger to convert checkpoint to HuggingFace format
    try:
        from verl.model_merger.base_model_merger import ModelMergerConfig
        from verl.model_merger.fsdp_model_merger import FSDPModelMerger

        # Clear and create merged model directory
        merged_path = Path(MERGED_MODEL_DIR)
        if merged_path.exists():
            shutil.rmtree(merged_path)
        merged_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Merging checkpoint to {MERGED_MODEL_DIR}...")

        # Create merger config
        config = ModelMergerConfig(
            operation="merge",
            backend="fsdp",
            local_dir=checkpoint_path,
            target_dir=MERGED_MODEL_DIR,
            hf_model_config_path=os.path.join(checkpoint_path, "huggingface"),
        )

        # Run merger
        merger = FSDPModelMerger(config)
        merger.merge_and_save()
        merger.cleanup()

        logger.info("Model merge completed successfully")

    except ImportError as e:
        logger.error(f"Failed to import model merger: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "merger_import_error",
                    "message": f"Failed to import verl model merger: {e}",
                }
            }
        )
    except Exception as e:
        logger.error(f"Failed to merge checkpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "merge_failed",
                    "message": f"Failed to merge checkpoint: {e}",
                }
            }
        )

    # Step 2: Upload merged model to HuggingFace
    try:
        from huggingface_hub import HfApi

        api = HfApi()

        # Create repo if it doesn't exist
        api.create_repo(
            repo_id=request.repo_id,
            token=request.hf_token,
            private=request.private,
            exist_ok=True,
        )

        # Upload the merged model folder
        commit_message = request.commit_message or "Upload fine-tuned model"
        logger.info(f"Uploading merged model to {request.repo_id}...")

        api.upload_folder(
            folder_path=MERGED_MODEL_DIR,
            repo_id=request.repo_id,
            repo_type="model",
            token=request.hf_token,
            commit_message=commit_message,
        )

        repo_url = f"https://huggingface.co/{request.repo_id}"
        logger.info(f"Successfully uploaded model to {repo_url}")

        return HuggingFaceUploadResponse(
            job_id=job_id,
            repo_id=request.repo_id,
            repo_url=repo_url,
        )

    except ImportError:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "missing_dependency",
                    "message": "huggingface_hub is not installed. Run: pip install huggingface_hub",
                }
            }
        )
    except Exception as e:
        logger.error(f"Failed to upload to HuggingFace: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "upload_failed",
                    "message": str(e),
                }
            }
        )
