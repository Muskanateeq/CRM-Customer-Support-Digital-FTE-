"""Regression tests for production agent provider selection and fallback."""

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
