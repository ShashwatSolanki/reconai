from __future__ import annotations

from dataclasses import asdict
from typing import Any, cast

from fastapi import APIRouter, HTTPException

from app.services.container import reconai_service

router = APIRouter(prefix="/exceptions", tags=["exceptions"])


def _serialize(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value

    if isinstance(value, list):
        return [_serialize(item) for item in value]

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _serialize(item)
            for key, item in asdict(value).items()
        }

    if isinstance(value, dict):
        return {
            key: _serialize(item)
            for key, item in value.items()
        }

    return value


@router.get("")
def list_exceptions() -> list[dict[str, Any]]:
    return [
        _serialize(exception)
        for exception in reconai_service.exceptions.values()
    ]


@router.get("/{exception_id}")
def get_exception(exception_id: str) -> dict[str, Any]:
    exception = reconai_service.exceptions.get(exception_id)

    if exception is None:
        raise HTTPException(
            status_code=404,
            detail="Exception not found.",
        )

    return cast(dict[str, Any], _serialize(exception))


@router.post("/{exception_id}/investigate")
def investigate_exception(exception_id: str) -> dict[str, Any]:
    if exception_id not in reconai_service.exceptions:
        raise HTTPException(
            status_code=404,
            detail="Exception not found.",
        )

    return cast(dict[str, Any], _serialize(reconai_service.investigate(exception_id)))