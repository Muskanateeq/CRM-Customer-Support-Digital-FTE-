"""Focused tests for production channel authentication and idempotency."""

from typing import Any, Dict

import pytest
from fastapi import HTTPException
from twilio.request_validator import RequestValidator

from src.api import channels
from src.channels import email_handler, whatsapp_handler


class FakeRequest:
    def __init__(self, url: str, form_data: Dict[str, str]):
        self.url = url
        self._form_data = form_data

    async def form(self) -> Dict[str, str]:
        return self._form_data


def test_email_poll_secret_rejects_missing_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(channels.settings, "EMAIL_POLL_SECRET", None)

    with pytest.raises(HTTPException) as exc:
        channels._require_email_poll_secret("anything")

    assert exc.value.status_code == 503


def test_email_poll_secret_uses_exact_match(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(channels.settings, "EMAIL_POLL_SECRET", "expected-secret")

    with pytest.raises(HTTPException) as exc:
        channels._require_email_poll_secret("wrong-secret")

    assert exc.value.status_code == 403
    channels._require_email_poll_secret("expected-secret")


@pytest.mark.asyncio
async def test_whatsapp_webhook_rejects_missing_signature(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(channels.settings, "TWILIO_VALIDATE_SIGNATURES", True)
    request = FakeRequest(
        "https://example.com/api/v1/channels/whatsapp/webhook",
        {
            "MessageSid": "SM-security-test",
            "From": "whatsapp:+15550000001",
            "To": "whatsapp:+15550000002",
            "Body": "hello",
            "NumMedia": "0",
        },
    )

    with pytest.raises(HTTPException) as exc:
        await channels.whatsapp_webhook_endpoint(request, x_twilio_signature=None)

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_whatsapp_webhook_accepts_valid_signature_and_queues_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token = "twilio-test-token"
    url = "https://example.com/api/v1/channels/whatsapp/webhook"
    params = {
        "MessageSid": "SM-valid-signature",
        "From": "whatsapp:+15550000001",
        "To": "whatsapp:+15550000002",
        "Body": "hello",
        "NumMedia": "0",
    }
    signature = RequestValidator(token).compute_signature(url, params)

    handler = object.__new__(whatsapp_handler.WhatsAppHandler)
    monkeypatch.setattr(channels.settings, "TWILIO_AUTH_TOKEN", token)
    monkeypatch.setattr(channels.settings, "TWILIO_WEBHOOK_URL", url)
    monkeypatch.setattr(channels.settings, "TWILIO_VALIDATE_SIGNATURES", True)
    monkeypatch.setattr(channels, "get_whatsapp_handler", lambda: handler)

    queued_payload: Dict[str, Any] = {}

    async def fake_enqueue(**kwargs: Any) -> Dict[str, Any]:
        queued_payload.update(kwargs)
        return {"job_id": "job-1", "status": "pending", "created": True}

    monkeypatch.setattr(channels, "enqueue_channel_job", fake_enqueue)

    response = await channels.whatsapp_webhook_endpoint(
        FakeRequest(url, params),
        x_twilio_signature=signature,
    )

    assert response == {"status": "queued", "job_id": "job-1"}
    assert queued_payload["channel"] == "whatsapp"
    assert queued_payload["external_message_id"] == "SM-valid-signature"


@pytest.mark.asyncio
async def test_email_handler_reuses_existing_inbound_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_existing(**_: Any) -> Dict[str, str]:
        return {
            "message_id": "message-1",
            "conversation_id": "conversation-1",
            "customer_id": "customer-1",
        }

    monkeypatch.setattr(email_handler, "get_inbound_message_by_channel_id", fake_existing)
    handler = object.__new__(email_handler.GmailHandler)
    handler.service = None

    result = await handler.process_email(
        {
            "message_id": "gmail-1",
            "from": "customer@example.com",
            "body": "help",
            "subject": "Support",
            "thread_id": "thread-1",
        }
    )

    assert result["duplicate"] is True
    assert result["message_id"] == "message-1"


@pytest.mark.asyncio
async def test_whatsapp_handler_reuses_existing_inbound_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_existing(**_: Any) -> Dict[str, str]:
        return {
            "message_id": "message-2",
            "conversation_id": "conversation-2",
            "customer_id": "customer-2",
        }

    monkeypatch.setattr(whatsapp_handler, "get_inbound_message_by_channel_id", fake_existing)
    handler = object.__new__(whatsapp_handler.WhatsAppHandler)

    result = await handler.process_incoming_message(
        from_number="whatsapp:+15550000001",
        to_number="whatsapp:+15550000002",
        body="help",
        message_sid="SM-duplicate",
    )

    assert result["duplicate"] is True
    assert result["message_id"] == "message-2"
