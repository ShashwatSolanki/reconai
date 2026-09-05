from pathlib import Path

from app.services.evaluation_report import EvaluationReportGenerator
from app.services.evaluation_runner import EvaluationRunner


def main() -> None:
    result = EvaluationRunner(seed=42, record_count=100).run()
    report_path = Path("reports/evaluation.md")
    EvaluationReportGenerator().write(result, report_path)
    print(f"Evaluation report written to {report_path}")


if __name__ == "__main__":
    main()
