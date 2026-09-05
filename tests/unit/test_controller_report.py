from pathlib import Path

from app.services.controller_report import ControllerReportGenerator
from app.services.finance_controller import FinanceController
from app.services.investigation_service import InvestigationService
from app.services.reconai_service import ReconAIService


def test_controller_report_contains_execution_derived_results(tmp_path: Path) -> None:
    result = FinanceController(
        ReconAIService(investigation_provider=InvestigationService()),
        seed=42,
        record_count=100,
    ).run()
    path = tmp_path / "evaluation.md"

    ControllerReportGenerator().write(result, path)

    report = path.read_text()
    assert "# ReconAI - Finance Controller Evaluation" in report
    assert "| Matched | 96 |" in report
    assert "| Exceptions | 4 |" in report
    assert "| Automatically resolved | 1 |" in report
    assert "| Escalated to human review | 3 |" in report
    assert "| Status accuracy | 100.00% |" in report
    assert "records/second" in report
    assert "Exceptions Requiring Human Review" in report
