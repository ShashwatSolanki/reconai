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