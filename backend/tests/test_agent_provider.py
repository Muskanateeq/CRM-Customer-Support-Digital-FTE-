"""Regression tests for production agent provider selection and fallback."""

from types import SimpleNamespace
from typing import Any, Dict

import pytest

from src.agent.classifier import QueryClassifier
from src.agent.dual_mode_router import DualModeAgentRouter
from src.agent.groq_agent import GroqAgentWithTools
from src.agent.response_generator import ResponseGenerator
from src.config import settings


def test_all_groq_components_use_configured_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "GROQ_API_KEY", "test-key")
    monkeypatch.setattr(settings, "GROQ_MODEL", "openai/gpt-oss-120b")

    assert QueryClassifier().model == "openai/gpt-oss-120b"
    assert ResponseGenerator().model == "openai/gpt-oss-120b"
    assert GroqAgentWithTools().model == "openai/gpt-oss-120b"


@pytest.mark.asyncio
async def test_router_falls_back_when_groq_returns_an_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailedGroqAgent:
        async def run(self, **_: Any) -> Dict[str, Any]:
            return {"final_output": "hidden fallback", "error": "model unavailable"}

    class SuccessfulSmartAgent:
        async def run(self, **_: Any) -> Dict[str, Any]:
            return {"final_output": "Helpful answer", "execution_time": 0.1}

    router = object.__new__(DualModeAgentRouter)
    router.groq_agent = FailedGroqAgent()
    router.smart_agent = SuccessfulSmartAgent()
    monkeypatch.setattr(settings, "USE_GROQ", True)

    result = await router.run(
        user_input="Where is my order?",
        customer_id="customer-1",
        conversation_id="conversation-1",
    )

    assert result["final_output"] == "Helpful answer"


@pytest.mark.asyncio
async def test_response_generator_does_not_hide_provider_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "GROQ_API_KEY", "test-key")
    generator = ResponseGenerator()

    async def failed_generation(*_: Any, **__: Any) -> str:
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(
        generator,
        "_generate_scenario_2_response",
        failed_generation,
    )

    with pytest.raises(RuntimeError, match="provider unavailable"):
        await generator.generate_response(
            scenario="SCENARIO_2_OUT_OF_SCOPE",
            user_query="What is Python?",
            conversation_id="conversation-1",
        )


@pytest.mark.asyncio
async def test_response_generator_retries_truncated_completion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "GROQ_API_KEY", "test-key")
    monkeypatch.setattr(settings, "GROQ_MAX_COMPLETION_TOKENS", 1024)
    generator = ResponseGenerator()
    calls = []

    async def fake_create(**kwargs: Any) -> Any:
        calls.append(kwargs)
        if len(calls) == 1:
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        finish_reason="length",
                        message=SimpleNamespace(content="Incomplete answer"),
                    )
                ]
            )
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    finish_reason="stop",
                    message=SimpleNamespace(content="Complete answer."),
                )
            ]
        )

    monkeypatch.setattr(generator.client.chat.completions, "create", fake_create)

    result = await generator._create_completion(
        [{"role": "user", "content": "Answer completely"}]
    )

    assert result == "Complete answer."
    assert calls[0]["max_completion_tokens"] == 1024
    assert calls[1]["max_completion_tokens"] == 2048


@pytest.mark.asyncio
async def test_streaming_agent_continues_after_length_finish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "GROQ_MAX_COMPLETION_TOKENS", 1024)

    def stream_chunk(content: str, finish_reason: str | None = None) -> Any:
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    delta=SimpleNamespace(content=content, tool_calls=None),
                    finish_reason=finish_reason,
                )
            ]
        )

    async def first_stream():
        yield stream_chunk("First half ")
        yield stream_chunk("", "length")

    async def second_stream():
        yield stream_chunk("second half.")
        yield stream_chunk("", "stop")

    streams = [first_stream(), second_stream()]

    async def fake_create(**_: Any) -> Any:
        return streams.pop(0)

    agent = object.__new__(GroqAgentWithTools)
    agent.model = "openai/gpt-oss-120b"
    agent.tools = []
    agent.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=fake_create),
        )
    )

    events = [
        event
        async for event in agent.run_streamed(
            user_input="Help me",
            customer_id="customer-1",
            conversation_id="conversation-1",
        )
    ]

    final_event = next(event for event in events if event["type"] == "final")
    assert final_event["data"]["final_output"] == "First half second half."
