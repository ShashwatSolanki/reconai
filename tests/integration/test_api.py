from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_reconciliation_endpoint_reconciles_transaction() -> None:
    payload = {
        "transactions": [
            {
                "transaction_id": "pay_0001",
                "merchant_id": "merchant_001",
                "amount": {"amount": 10000, "currency": "INR"},
                "transaction_time": "2026-09-01T10:00:00+00:00",
                "payment_method": "upi",
                "reference_id": "ref_pay_0001",
                "status": "success",
            }
        ],
        "settlements": [
            {
                "settlement_id": "set_0001",
                "merchant_id": "merchant_001",
                "amount": {"amount": 10000, "currency": "INR"},
                "settlement_time": "2026-09-01T12:00:00+00:00",
                "reference_id": "ref_set_0001",
                "transaction_reference": "pay_0001",
                "status": "settled",
            }
        ],
    }

    response = client.post("/reconciliation", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["summary"]["total_transactions"] == 1
    assert body["summary"]["matched"] == 1
    assert body["summary"]["partial_matches"] == 0
    assert body["summary"]["mismatches"] == 0
    assert body["summary"]["missing_settlements"] == 0
    assert body["summary"]["duplicates"] == 0

    assert len(body["results"]) == 1
    assert body["results"][0]["transaction_id"] == "pay_0001"
    assert body["results"][0]["settlement_id"] == "set_0001"
    assert body["results"][0]["status"] == "matched"
    assert body["results"][0]["expected_amount"] == {
        "amount": 10000,
        "currency": "INR",
    }
    assert body["results"][0]["actual_amount"] == {
        "amount": 10000,
        "currency": "INR",
    }
    assert body["results"][0]["difference"] == {
        "amount": 0,
        "currency": "INR",
    }


def test_reconciliation_endpoint_rejects_negative_money() -> None:
    payload = {
        "transactions": [
            {
                "transaction_id": "pay_0001",
                "merchant_id": "merchant_001",
                "amount": {"amount": -100, "currency": "INR"},
                "transaction_time": "2026-09-01T10:00:00+00:00",
                "payment_method": "upi",
                "reference_id": "ref_pay_0001",
                "status": "success",
            }
        ],
        "settlements": [],
    }

    response = client.post("/reconciliation", json=payload)

    assert response.status_code == 422


def test_reconciliation_endpoint_rejects_naive_transaction_timestamp() -> None:
    payload = {
        "transactions": [
            {
                "transaction_id": "pay_0001",
                "merchant_id": "merchant_001",
                "amount": {"amount": 1000, "currency": "INR"},
                "transaction_time": "2026-09-01T10:00:00",
                "payment_method": "upi",
                "reference_id": "ref_pay_0001",
                "status": "success",
            }
        ],
        "settlements": [],
    }

    response = client.post("/reconciliation", json=payload)

    assert response.status_code == 422


def test_reconciliation_endpoint_rejects_empty_transaction_id() -> None:
    payload = {
        "transactions": [
            {
                "transaction_id": "",
                "merchant_id": "merchant_001",
                "amount": {"amount": 1000, "currency": "INR"},
                "transaction_time": "2026-09-01T10:00:00+00:00",
                "payment_method": "upi",
                "reference_id": "ref_pay_0001",
                "status": "success",
            }
        ],
        "settlements": [],
    }

    response = client.post("/reconciliation", json=payload)

    assert response.status_code == 422


def test_reconciliation_endpoint_rejects_negative_settlement_amount() -> None:
    payload = {
        "transactions": [],
        "settlements": [
            {
                "settlement_id": "set_0001",
                "merchant_id": "merchant_001",
                "amount": {"amount": -100, "currency": "INR"},
                "settlement_time": "2026-09-01T10:00:00+00:00",
                "reference_id": "ref_set_0001",
                "transaction_reference": "pay_0001",
                "status": "settled",
            }
        ],
    }

    response = client.post("/reconciliation", json=payload)

    assert response.status_code == 422


def test_reconciliation_endpoint_rejects_naive_settlement_timestamp() -> None:
    payload = {
        "transactions": [],
        "settlements": [
            {
                "settlement_id": "set_0001",
                "merchant_id": "merchant_001",
                "amount": {"amount": 1000, "currency": "INR"},
                "settlement_time": "2026-09-01T10:00:00",
                "reference_id": "ref_set_0001",
                "transaction_reference": "pay_0001",
                "status": "settled",
            }
        ],
    }

    response = client.post("/reconciliation", json=payload)

    assert response.status_code == 422


def test_reconciliation_endpoint_registers_exception() -> None:
    payload = {
        "transactions": [
            {
                "transaction_id": "pay_exc_0001",
                "merchant_id": "merchant_001",
                "amount": {"amount": 10000, "currency": "INR"},
                "transaction_time": "2026-09-01T10:00:00+00:00",
                "payment_method": "upi",
                "reference_id": "ref_pay_exc_0001",
                "status": "success",
            }
        ],
        "settlements": [
            {
                "settlement_id": "set_exc_0001",
                "merchant_id": "merchant_001",
                "amount": {"amount": 10100, "currency": "INR"},
                "settlement_time": "2026-09-01T12:00:00+00:00",
                "reference_id": "ref_set_exc_0001",
                "transaction_reference": "pay_exc_0001",
                "status": "settled",
            }
        ],
    }

    response = client.post("/reconciliation", json=payload)

    assert response.status_code == 200

    exceptions_response = client.get("/exceptions")

    assert exceptions_response.status_code == 200

    exceptions = exceptions_response.json()

    matching = [
        exception
        for exception in exceptions
        if exception["transaction_id"] == "pay_exc_0001"
    ]

    assert len(matching) == 1
    assert matching[0]["category"] == "amount_mismatch"
    assert matching[0]["expected_amount"] == {
        "amount": 10000,
        "currency": "INR",
    }
    assert matching[0]["actual_amount"] == {
        "amount": 10100,
        "currency": "INR",
    }
    assert matching[0]["difference"] == {
        "amount": 100,
        "currency": "INR",
    }


def test_exception_investigation_endpoint_returns_agent_workflow() -> None:
    payload = {
        "transactions": [
            {
                "transaction_id": "pay_exc_0002",
                "merchant_id": "merchant_001",
                "amount": {"amount": 10000, "currency": "INR"},
                "transaction_time": "2026-09-01T10:00:00+00:00",
                "payment_method": "upi",
                "reference_id": "ref_pay_exc_0002",
                "status": "success",
            }
        ],
        "settlements": [
            {
                "settlement_id": "set_exc_0002",
                "merchant_id": "merchant_001",
                "amount": {"amount": 9900, "currency": "INR"},
                "settlement_time": "2026-09-01T12:00:00+00:00",
                "reference_id": "ref_set_exc_0002",
                "transaction_reference": "pay_exc_0002",
                "status": "settled",
            }
        ],
    }

    response = client.post("/reconciliation", json=payload)

    assert response.status_code == 200

    exceptions_response = client.get("/exceptions")

    assert exceptions_response.status_code == 200

    exception = next(
        item
        for item in exceptions_response.json()
        if item["transaction_id"] == "pay_exc_0002"
    )

    investigation_response = client.post(
        f"/exceptions/{exception['exception_id']}/investigate"
    )

    assert investigation_response.status_code == 200

    body = investigation_response.json()

    assert body["investigation"]["root_cause"] == "partial_settlement"
    assert body["investigation"]["recommendation"] == "accept_settlement"
    assert body["investigation"]["confidence"] == 0.95
    assert body["investigation"]["requires_human_review"] is False

    assert body["decision"]["action"] == "resolve"
    assert body["decision"]["requires_human_review"] is False

    assert body["action"]["executed"] is True
    assert body["action"]["audit_event"]["actor"] == "agent"
    assert body["action"]["audit_event"]["executed"] is True


def test_exception_endpoints_return_404_for_unknown_exception() -> None:
    response = client.get("/exceptions/does_not_exist")

    assert response.status_code == 404

    response = client.post("/exceptions/does_not_exist/investigate")

    assert response.status_code == 404