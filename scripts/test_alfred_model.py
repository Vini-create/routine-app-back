"""Run Alfred's real prompt against one model without starting the API."""

from __future__ import annotations

import argparse
import asyncio
import json

from app.ai.models.gateway import (
    LangChainOpenAIModelGateway,
    ModelRole,
    ModelSpec,
)
from app.ai.prompts.alfred import build_alfred_system_prompt
from app.ai.schemas.alfred import AlfredIntervention
from app.core.config import settings


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Test one model with Alfred's production system prompt and "
            "structured response schema."
        )
    )
    parser.add_argument(
        "message",
        help="Message that Alfred should answer.",
    )
    parser.add_argument(
        "--model",
        default=settings.ai_alfred_model,
        help="OpenAI model ID (default: configured AI_ALFRED_MODEL).",
    )
    parser.add_argument(
        "--language",
        default="pt-BR",
        choices=("pt-BR", "en", "es", "fr"),
        help="Expected response language.",
    )
    return parser.parse_args()


def _model_spec(model: str) -> ModelSpec:
    if model.startswith("gpt-5"):
        return ModelSpec(
            model=model,
            use_responses_api=True,
            max_tokens=1_300,
            reasoning_effort="low",
            verbosity="medium",
        )
    return ModelSpec(
        model=model,
        use_responses_api=False,
        temperature=0.3,
        max_tokens=1_300,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )


async def _run(message: str, model: str, language: str) -> None:
    gateway = LangChainOpenAIModelGateway(
        api_key=settings.openai_api_key_value,
        specs={ModelRole.ALFRED: _model_spec(model)},
        timeout_seconds=settings.ai_model_timeout_seconds,
        max_retries=settings.ai_model_max_retries,
    )
    payload = {
        "USER_INPUT": message,
        "selected_strategy": "adaptive_conversation",
        "response_plan": {
            "objective": (
                "Resolve the request with useful reasoning and without forcing "
                "a generic micro-action."
            ),
            "tone": "warm_collaborative_practical",
            "key_points": [],
            "next_steps": [],
            "should_ask_question": False,
        },
        "context_inventory": {},
        "behavioral_state": {},
        "goals": [],
        "habits": [],
        "evidence_pack": {},
        "UNTRUSTED_CONTEXT": {
            "recent_messages": [],
            "memories": [],
            "conversation_summary_en": "",
        },
    }
    result = await gateway.invoke_structured(
        role=ModelRole.ALFRED,
        schema=AlfredIntervention,
        system_prompt=build_alfred_system_prompt(language),
        user_prompt=json.dumps(payload, ensure_ascii=False),
    )
    print(f"model: {result.model}")
    print(f"usage: {result.usage}")
    print()
    print(result.parsed.message)


def main() -> None:
    arguments = _arguments()
    asyncio.run(
        _run(
            message=arguments.message,
            model=arguments.model,
            language=arguments.language,
        )
    )


if __name__ == "__main__":
    main()
