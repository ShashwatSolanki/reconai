from __future__ import annotations

from typing import Any

from app.core.config import Settings
from app.services.investigation_provider import InvestigationProvider
from app.services.investigation_service import InvestigationService
from app.services.openai_investigation_provider import OpenAIInvestigationProvider
from app.services.reconai_service import ReconAIService


def create_investigation_provider(
    settings: Settings,
    openai_client: Any | None = None,
) -> InvestigationProvider:
    """Create the configured investigation provider without coupling callers to it."""

    if settings.investigation_provider == "mock":
        return InvestigationService()

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required when INVESTIGATION_PROVIDER=openai.")

    if openai_client is None:
        from openai import OpenAI  # type: ignore[import-not-found]

        openai_client = OpenAI(api_key=settings.openai_api_key)

    return OpenAIInvestigationProvider(
        client=openai_client,
        model=settings.openai_model,
    )


def create_reconai_service(settings: Settings | None = None) -> ReconAIService:
    """Build the application service with the selected investigation provider."""

    application_settings = settings or Settings()
    return ReconAIService(
        investigation_provider=create_investigation_provider(application_settings),
    )


reconai_service = create_reconai_service()
