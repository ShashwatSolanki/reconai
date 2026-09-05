from pathlib import Path

from app.services.evaluation_report import EvaluationReportGenerator
from app.services.evaluation_runner import EvaluationRunner


def test_report_contains_measured_evaluation_results(tmp_path: Path) -> None:
    result = EvaluationRunner(seed=42, record_count=100).run()

    report_path = tmp_path / "evaluation.md"
    EvaluationReportGenerator().write(result, report_path)

    report = report_path.read_text()

    assert "# ReconAI Evaluation Report" in report
    assert "100" in report
    assert "100.00%" in report
    assert "Controlled synthetic dataset" in report
    assert "Seed: `42`" in report
    assert "Record count: `100`" in report


def test_report_preserves_non_default_evaluation_configuration(
    tmp_path: Path,
) -> None:
    result = EvaluationRunner(seed=123, record_count=50).run()

    report_path = tmp_path / "evaluation.md"
    EvaluationReportGenerator().write(result, report_path)

    report = report_path.read_text()

    assert "Seed: `123`" in report
    assert "Record count: `50`" in report


def test_report_is_reproducible(tmp_path: Path) -> None:
    result = EvaluationRunner(seed=42, record_count=100).run()
    generator = EvaluationReportGenerator()

    first_path = tmp_path / "first.md"
    second_path = tmp_path / "second.md"

    generator.write(result, first_path)
    generator.write(result, second_path)

    assert first_path.read_text() == second_path.read_text()
