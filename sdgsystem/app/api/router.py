"""API router aggregating all endpoints."""
from fastapi import APIRouter
from .sdg import router as sdg_router
from .train import router as train_router

router = APIRouter()
router.include_router(sdg_router)
router.include_router(train_router)
