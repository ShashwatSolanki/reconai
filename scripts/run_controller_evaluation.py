from pathlib import Path

from app.services.container import create_reconai_service
from app.services.controller_report import ControllerReportGenerator
from app.services.finance_controller import FinanceController


def main() -> None:
    result = FinanceController(
        create_reconai_service(),
        seed=42,
        record_count=100,
    ).run()
    report_path = Path("reports/evaluation.md")
    ControllerReportGenerator().write(result, report_path)
    print(f"Controller evaluation report written to {report_path}")


if __name__ == "__main__":
    main()
