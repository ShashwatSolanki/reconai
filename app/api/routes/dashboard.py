from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.services.container import reconai_service

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> str:
    return DASHBOARD_HTML


@router.get("/dashboard/data")
def dashboard_data() -> dict[str, Any]:
    exceptions = list(reconai_service.exceptions.values())
    investigations = reconai_service.investigations
    actions = reconai_service.actions

    auto_resolved = sum(
        1 for action in actions.values() if action.executed
    )

    human_escalations = sum(
        1 for action in actions.values()
        if action.requires_human_review
    )

    amount_at_risk = sum(
        exception.difference.amount
        for exception in exceptions
        if exception.difference is not None
    )

    exception_rows: list[dict[str, Any]] = []

    for exception in exceptions:
        investigation = investigations.get(exception.exception_id)
        action = actions.get(exception.exception_id)

        exception_rows.append(
            {
                "exception_id": exception.exception_id,
                "transaction_id": exception.transaction_id,
                "settlement_id": exception.settlement_id,
                "category": exception.category.value,
                "severity": exception.severity.value,
                "expected_amount": exception.expected_amount.amount,
                "actual_amount": (
                    exception.actual_amount.amount
                    if exception.actual_amount is not None
                    else None
                ),
                "difference": (
                    exception.difference.amount
                    if exception.difference is not None
                    else None
                ),
                "description": exception.description,
                "investigation": (
                    {
                        "root_cause": investigation.root_cause.value,
                        "explanation": investigation.explanation,
                        "evidence": investigation.evidence,
                        "recommendation": investigation.recommendation.value,
                        "confidence": investigation.confidence,
                        "requires_human_review": (
                            investigation.requires_human_review
                        ),
                    }
                    if investigation is not None
                    else None
                ),
                "action": (
                    {
                        "action": action.action,
                        "executed": action.executed,
                        "requires_human_review": (
                            action.requires_human_review
                        ),
                        "reason": action.reason,
                        "audit_event": {
                            "event_id": action.audit_event.event_id,
                            "actor": action.audit_event.actor,
                            "action": action.audit_event.action,
                            "reason": action.audit_event.reason,
                            "executed": action.audit_event.executed,
                            "timestamp": (
                                action.audit_event.timestamp.isoformat()
                            ),
                        },
                    }
                    if action is not None
                    else None
                ),
            }
        )

    return {
        "metrics": {
            "total_transactions": (
                reconai_service.latest_reconciliation_summary[
                    "total_transactions"
                ]
            ),
            "matched": (
                reconai_service.latest_reconciliation_summary[
                    "matched"
                ]
            ),
            "exceptions": len(exceptions),
            "amount_at_risk": amount_at_risk,
            "auto_resolved": auto_resolved,
            "human_escalations": human_escalations,
        },
        "exceptions": exception_rows,
    }


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >
    <title>ReconAI Control Tower</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: #f5f7fb;
            color: #101828;
            font-family:
                Inter,
                ui-sans-serif,
                system-ui,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }

        .shell {
            max-width: 1500px;
            margin: auto;
            padding: 32px;
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 28px;
        }

        .eyebrow {
            color: #5267f5;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        h1 {
            margin: 6px 0;
            font-size: 32px;
            letter-spacing: -0.04em;
        }

        .subtitle {
            color: #667085;
            font-size: 14px;
        }

        .live {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 14px;
            border: 1px solid #e4e7ec;
            border-radius: 999px;
            background: white;
            font-size: 13px;
            font-weight: 700;
        }

        .live-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #12b76a;
        }

        .metrics {
            display: grid;
            grid-template-columns:
                repeat(6, minmax(0, 1fr));
            gap: 14px;
            margin-bottom: 20px;
        }

        .metric {
            padding: 18px;
            background: white;
            border: 1px solid #e4e7ec;
            border-radius: 16px;
            box-shadow:
                0 8px 24px rgba(16, 24, 40, 0.06);
        }

        .metric-label {
            margin-bottom: 10px;
            color: #667085;
            font-size: 12px;
        }

        .metric-value {
            font-size: 25px;
            font-weight: 800;
            letter-spacing: -0.03em;
        }

        .workspace {
            display: grid;
            grid-template-columns: 1.1fr 0.9fr;
            gap: 18px;
        }

        .panel {
            overflow: hidden;
            background: white;
            border: 1px solid #e4e7ec;
            border-radius: 18px;
            box-shadow:
                0 8px 24px rgba(16, 24, 40, 0.06);
        }

        .panel-header {
            padding: 18px 20px;
            border-bottom: 1px solid #e4e7ec;
        }

        .panel-title {
            font-weight: 800;
        }

        .panel-subtitle {
            margin-top: 4px;
            color: #667085;
            font-size: 12px;
        }

        .queue {
            padding: 10px;
        }

        .exception-row {
            display: grid;
            grid-template-columns:
                80px 1fr 90px 80px;
            gap: 12px;
            align-items: center;
            padding: 15px;
            border-radius: 12px;
            cursor: pointer;
        }

        .exception-row:hover,
        .exception-row.active {
            background: #f8fafc;
        }

        .mono {
            font-family:
                "SFMono-Regular",
                Consolas,
                monospace;
            font-size: 12px;
        }

        .muted {
            color: #667085;
            font-size: 12px;
        }

        .pill {
            display: inline-flex;
            justify-content: center;
            min-width: 64px;
            padding: 5px 8px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 800;
            text-transform: capitalize;
        }

        .high,
        .critical {
            color: #b42318;
            background: #fef3f2;
        }

        .medium {
            color: #b54708;
            background: #fffaeb;
        }

        .low {
            color: #027a48;
            background: #ecfdf3;
        }

        .detail {
            padding: 20px;
        }

        .detail-header {
            display: flex;
            justify-content: space-between;
            gap: 15px;
        }

        .detail-header h2 {
            margin: 0 0 5px;
            font-size: 21px;
        }

        .amount {
            text-align: right;
        }

        .amount strong {
            display: block;
            font-size: 27px;
        }

        .amount span {
            color: #667085;
            font-size: 11px;
        }

        .section {
            margin-top: 20px;
            padding-top: 18px;
            border-top: 1px solid #e4e7ec;
        }

        .section-title {
            margin-bottom: 12px;
            color: #667085;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .facts {
            display: grid;
            grid-template-columns:
                repeat(3, minmax(0, 1fr));
            gap: 10px;
        }

        .fact {
            padding: 12px;
            background: #f8fafc;
            border: 1px solid #e4e7ec;
            border-radius: 10px;
        }

        .fact-label {
            color: #667085;
            font-size: 10px;
        }

        .fact-value {
            margin-top: 5px;
            font-size: 13px;
            font-weight: 700;
        }

        .explanation {
            margin: 12px 0;
            font-size: 13px;
            line-height: 1.6;
        }

        .evidence {
            margin: 0;
            padding-left: 20px;
            color: #344054;
            font-size: 13px;
            line-height: 1.7;
        }

        .decision {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .decision-card {
            padding: 14px;
            background: #f8fafc;
            border: 1px solid #e4e7ec;
            border-radius: 12px;
        }

        .decision-card strong {
            display: block;
            margin-bottom: 5px;
            color: #667085;
            font-size: 10px;
            text-transform: uppercase;
        }

        .decision-card span {
            font-size: 14px;
            font-weight: 750;
        }

        .event {
            padding: 13px 15px;
            border-left: 2px solid #5267f5;
            border-radius: 0 10px 10px 0;
            background: #f8fafc;
        }

        .event-meta {
            margin-bottom: 5px;
            color: #667085;
            font-size: 11px;
        }

        .event-text {
            font-size: 13px;
        }

        .empty {
            padding: 50px 25px;
            color: #667085;
            text-align: center;
            font-size: 13px;
        }

        @media (max-width: 1100px) {
            .metrics {
                grid-template-columns:
                    repeat(3, minmax(0, 1fr));
            }

            .workspace {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 700px) {
            .shell {
                padding: 16px;
            }

            .metrics {
                grid-template-columns:
                    repeat(2, minmax(0, 1fr));
            }

            .topbar {
                align-items: flex-start;
                flex-direction: column;
                gap: 15px;
            }

            .exception-row {
                grid-template-columns: 1fr;
            }

            .facts,
            .decision {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>

<body>

<div class="shell">

    <header class="topbar">
        <div>
            <div class="eyebrow">
                AI Finance Controller
            </div>

            <h1>
                ReconAI Control Tower
            </h1>

            <div class="subtitle">
                Deterministic reconciliation ·
                AI investigation ·
                bounded agent actions ·
                complete audit trail
            </div>
        </div>

        <div class="live">
            <span class="live-dot"></span>
            Live control plane
        </div>
    </header>

    <section
        id="metrics"
        class="metrics"
    ></section>

    <section class="workspace">

        <div class="panel">

            <div class="panel-header">
                <div class="panel-title">
                    Exception Queue
                </div>

                <div class="panel-subtitle">
                    Financial mismatches requiring controller attention
                </div>
            </div>

            <div
                id="queue"
                class="queue"
            ></div>

        </div>

        <div class="panel">

            <div class="panel-header">
                <div class="panel-title">
                    Investigation
                </div>

                <div class="panel-subtitle">
                    Evidence → recommendation → safe execution
                </div>
            </div>

            <div
                id="detail"
                class="detail"
            ></div>

        </div>

    </section>

</div>

<script>
    const money = (paise) => {
        if (paise === null || paise === undefined) {
            return "—";
        }

        return `₹${(paise / 100).toLocaleString(
            "en-IN",
            {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }
        )}`;
    };

    const titleCase = (value) => {
        return value
            .replaceAll("_", " ")
            .replace(
                /\\b\\w/g,
                character => character.toUpperCase()
            );
    };

    let state = {
        exceptions: []
    };

    function renderMetrics(metrics) {
        const cards = [
            [
                "Total Transactions",
                metrics.total_transactions
            ],
            [
                "Matched",
                metrics.matched
            ],
            [
                "Exceptions",
                metrics.exceptions
            ],
            [
                "Amount at Risk",
                money(metrics.amount_at_risk)
            ],
            [
                "Auto-Resolved",
                metrics.auto_resolved
            ],
            [
                "Human Escalations",
                metrics.human_escalations
            ]
        ];

        document.getElementById("metrics").innerHTML =
            cards.map(([label, value]) => `
                <div class="metric">
                    <div class="metric-label">
                        ${label}
                    </div>

                    <div class="metric-value">
                        ${value}
                    </div>
                </div>
            `).join("");
    }

    function renderQueue(exceptions) {
        const queue =
            document.getElementById("queue");

        if (!exceptions.length) {
            queue.innerHTML = `
                <div class="empty">
                    No exceptions yet.<br><br>
                    Run a reconciliation batch
                    to populate the control tower.
                </div>
            `;

            return;
        }

        queue.innerHTML = exceptions.map(
            (item, index) => `
                <div
                    class="exception-row
                        ${index === 0 ? "active" : ""}"
                    data-id="${item.exception_id}"
                >

                    <div>
                        <span
                            class="pill ${item.severity}"
                        >
                            ${item.severity}
                        </span>
                    </div>

                    <div>
                        <div class="mono">
                            ${item.exception_id}
                        </div>

                        <div class="muted">
                            ${titleCase(item.category)}
                            ·
                            ${item.transaction_id}
                        </div>
                    </div>

                    <div>
                        <strong>
                            ${money(item.difference)}
                        </strong>

                        <div class="muted">
                            delta
                        </div>
                    </div>

                    <div>
                        <span class="muted">
                            ${
                                item.investigation
                                ? Math.round(
                                    item.investigation.confidence
                                    * 100
                                ) + "%"
                                : "Pending"
                            }
                        </span>
                    </div>

                </div>
            `
        ).join("");

        queue
            .querySelectorAll(".exception-row")
            .forEach(row => {
                row.addEventListener("click", () => {
                    queue
                        .querySelectorAll(".exception-row")
                        .forEach(
                            item =>
                                item.classList.remove("active")
                        );

                    row.classList.add("active");

                    const selected =
                        state.exceptions.find(
                            item =>
                                item.exception_id ===
                                row.dataset.id
                        );

                    renderDetail(selected);
                });
            });
    }

    function renderDetail(item) {
        const detail =
            document.getElementById("detail");

        if (!item) {
            detail.innerHTML = `
                <div class="empty">
                    Select an exception from the queue.
                </div>
            `;

            return;
        }

        const investigation =
            item.investigation;

        const action =
            item.action;

        detail.innerHTML = `
            <div class="detail-header">

                <div>
                    <h2>
                        ${titleCase(item.category)}
                    </h2>

                    <div class="muted">
                        ${item.exception_id}
                        ·
                        ${item.transaction_id}
                    </div>
                </div>

                <div class="amount">
                    <strong>
                        ${money(item.difference)}
                    </strong>

                    <span>
                        amount at risk
                    </span>
                </div>

            </div>

            <div class="section">

                <div class="section-title">
                    Reconciliation Facts
                </div>

                <div class="facts">

                    <div class="fact">
                        <div class="fact-label">
                            Expected
                        </div>

                        <div class="fact-value">
                            ${money(item.expected_amount)}
                        </div>
                    </div>

                    <div class="fact">
                        <div class="fact-label">
                            Actual
                        </div>

                        <div class="fact-value">
                            ${money(item.actual_amount)}
                        </div>
                    </div>

                    <div class="fact">
                        <div class="fact-label">
                            Settlement
                        </div>

                        <div class="fact-value mono">
                            ${item.settlement_id || "Missing"}
                        </div>
                    </div>

                </div>

            </div>

            <div class="section">

                <div class="section-title">
                    Investigation
                </div>

                ${
                    investigation
                    ? `
                        <div class="facts">

                            <div class="fact">
                                <div class="fact-label">
                                    Root Cause
                                </div>

                                <div class="fact-value">
                                    ${titleCase(
                                        investigation.root_cause
                                    )}
                                </div>
                            </div>

                            <div class="fact">
                                <div class="fact-label">
                                    Recommendation
                                </div>

                                <div class="fact-value">
                                    ${titleCase(
                                        investigation.recommendation
                                    )}
                                </div>
                            </div>

                            <div class="fact">
                                <div class="fact-label">
                                    Confidence
                                </div>

                                <div class="fact-value">
                                    ${Math.round(
                                        investigation.confidence
                                        * 100
                                    )}%
                                </div>
                            </div>

                        </div>

                        <div class="explanation">
                            ${investigation.explanation}
                        </div>

                        <div class="section-title">
                            Verified Evidence
                        </div>

                        <ul class="evidence">
                            ${
                                investigation.evidence
                                    .map(
                                        evidence =>
                                            `<li>${evidence}</li>`
                                    )
                                    .join("")
                            }
                        </ul>
                    `
                    : `
                        <div class="empty">
                            Investigation not run yet.
                        </div>
                    `
                }

            </div>

            <div class="section">

                <div class="section-title">
                    Agent Decision
                </div>

                ${
                    action
                    ? `
                        <div class="decision">

                            <div class="decision-card">
                                <strong>
                                    Action
                                </strong>

                                <span>
                                    ${titleCase(action.action)}
                                    ·
                                    ${
                                        action.executed
                                        ? "Executed"
                                        : "Routed"
                                    }
                                </span>
                            </div>

                            <div class="decision-card">
                                <strong>
                                    Human Review
                                </strong>

                                <span>
                                    ${
                                        action.requires_human_review
                                        ? "Required"
                                        : "Not required"
                                    }
                                </span>
                            </div>

                        </div>
                    `
                    : `
                        <div class="empty">
                            Agent has not acted yet.
                        </div>
                    `
                }

            </div>

            <div class="section">

                <div class="section-title">
                    Audit Timeline
                </div>

                ${
                    action
                    ? `
                        <div class="event">

                            <div class="event-meta">
                                ${
                                    new Date(
                                        action.audit_event.timestamp
                                    ).toLocaleString()
                                }

                                ·

                                ${action.audit_event.actor}
                            </div>

                            <div class="event-text">
                                <strong>
                                    ${titleCase(
                                        action.audit_event.action
                                    )}
                                </strong>

                                —
                                ${action.audit_event.reason}
                            </div>

                        </div>
                    `
                    : `
                        <div class="empty">
                            No audit event yet.
                        </div>
                    `
                }

            </div>
        `;
    }

    async function loadDashboard() {
        const response =
            await fetch("/dashboard/data");

        state =
            await response.json();

        renderMetrics(state.metrics);

        renderQueue(state.exceptions);

        renderDetail(state.exceptions[0]);
    }

    loadDashboard().catch(error => {
        document.getElementById("detail").innerHTML = `
            <div class="empty">
                Unable to load dashboard data.<br><br>
                ${error.message}
            </div>
        `;
    });
</script>

</body>
</html>
"""