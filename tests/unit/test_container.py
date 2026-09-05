from app.core.config import Settings
from app.services.container import create_investigation_provider, create_reconai_service
from app.services.investigation_service import InvestigationService
from app.services.openai_investigation_provider import OpenAIInvestigationProvider


def test_container_selects_deterministic_provider_by_default() -> None:
    provider = create_investigation_provider(Settings())

    assert isinstance(provider, InvestigationService)


def test_container_selects_openai_provider_from_configuration() -> None:
    provider = create_investigation_provider(
        Settings(investigation_provider="openai", openai_api_key="test-key"),
        openai_client=object(),
    )

    assert isinstance(provider, OpenAIInvestigationProvider)


def test_container_injects_selected_provider_into_application_service() -> None:
    service = create_reconai_service(Settings())

    assert isinstance(service._investigation_provider, InvestigationService)
