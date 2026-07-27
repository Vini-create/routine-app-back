"""Contracts for Alfred's shared user-facing voice."""

from app.ai.prompts.alfred import build_alfred_system_prompt
from app.ai.prompts.analysis import build_feedbacker_system_prompt
from app.ai.prompts.base import PROMPT_VERSION
from app.ai.prompts.critic import build_critic_system_prompt
from app.ai.prompts.routing import build_routing_system_prompt


def test_user_facing_model_prompts_share_alfreds_friendlier_voice() -> None:
    prompts = (
        build_alfred_system_prompt("pt-BR"),
        build_feedbacker_system_prompt("pt-BR"),
        build_critic_system_prompt("pt-BR"),
    )

    for prompt in prompts:
        normalized = " ".join(prompt.split())
        assert "Alfred's voice:" in normalized
        assert "kind, attentive and capable companion" in normalized
        assert "Keep warmth compact" in normalized
        assert "canned praise or automatic validation" in normalized
        assert "Security and authority:" in prompt
        assert f"Prompt version: {PROMPT_VERSION}" in prompt

    alfred_prompt = " ".join(build_alfred_system_prompt("pt-BR").split())
    assert "current `USER_INPUT` as the primary task" in alfred_prompt
    assert "Never replace a simple greeting" in alfred_prompt
    assert "do not recommend sleep" in alfred_prompt

    feedbacker_prompt = " ".join(build_feedbacker_system_prompt("pt-BR").split())
    assert "every user-visible textual field in the requested response language" in feedbacker_prompt
    assert "`updated_summary_en` is the sole English-only field" in feedbacker_prompt


def test_router_remains_small_and_never_writes_user_facing_prose() -> None:
    prompt = build_routing_system_prompt()

    assert "Alfred's voice:" not in prompt
    assert "Do not answer the user." in prompt
    assert "Security and authority:" in prompt
    assert f"Prompt version: {PROMPT_VERSION}" in prompt
