"""LangChain model gateway with role-aware cost and reasoning settings."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Generic, Protocol, TypeVar, cast

from langchain_core.callbacks import UsageMetadataCallbackHandler
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, SecretStr

from app.ai.domain.errors import AIApplicationError, AIErrorCode

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class ModelRole(StrEnum):
    ROUTER = "router"
    ALFRED = "alfred"
    FEEDBACKER = "feedbacker"
    CRITIC = "critic"


@dataclass(frozen=True, slots=True)
class ModelSpec:
    """Endpoint and inference defaults for one graph role.

    ``None`` means that the parameter is intentionally omitted from the
    provider request, which is required for parameters unsupported by a model
    or API endpoint.
    """

    model: str
    use_responses_api: bool
    temperature: float | None = None
    max_tokens: int | None = None
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    reasoning_effort: str | None = None
    verbosity: str | None = None

    def __post_init__(self) -> None:
        if self.temperature is not None and not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2.")
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("max_tokens must be greater than zero.")
        if self.top_p is not None and not 0.0 <= self.top_p <= 1.0:
            raise ValueError("top_p must be between 0 and 1.")
        for name, value in (
            ("frequency_penalty", self.frequency_penalty),
            ("presence_penalty", self.presence_penalty),
        ):
            if value is not None and not -2.0 <= value <= 2.0:
                raise ValueError(f"{name} must be between -2 and 2.")
        if self.use_responses_api and (
            self.frequency_penalty is not None
            or self.presence_penalty is not None
        ):
            raise ValueError(
                "frequency_penalty and presence_penalty are not supported "
                "by the Responses API."
            )


@dataclass(frozen=True, slots=True)
class ModelInvocationResult(Generic[SchemaT]):
    parsed: SchemaT
    model: str
    usage: dict[str, int]


class AIModelGateway(Protocol):
    async def invoke_structured(
        self,
        *,
        role: ModelRole,
        schema: type[SchemaT],
        system_prompt: str,
        user_prompt: str,
    ) -> ModelInvocationResult[SchemaT]: ...


class LangChainOpenAIModelGateway:
    """Production adapter using role-aware OpenAI APIs and structured output."""

    def __init__(
        self,
        *,
        api_key: str,
        specs: dict[ModelRole, ModelSpec],
        timeout_seconds: float,
        max_retries: int,
    ) -> None:
        self._api_key = SecretStr(api_key)
        self._specs = dict(specs)
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._clients: dict[ModelRole, ChatOpenAI] = {}

    def _client(self, role: ModelRole) -> ChatOpenAI:
        if role not in self._clients:
            spec = self._specs[role]
            client_options: dict[str, Any] = {
                "model": spec.model,
                "api_key": self._api_key,
                "use_responses_api": spec.use_responses_api,
                "timeout": self._timeout_seconds,
                "max_retries": self._max_retries,
                "store": False,
            }
            optional_parameters = {
                "temperature": spec.temperature,
                "max_tokens": spec.max_tokens,
                "top_p": spec.top_p,
                "frequency_penalty": spec.frequency_penalty,
                "presence_penalty": spec.presence_penalty,
                "reasoning_effort": spec.reasoning_effort,
                "verbosity": spec.verbosity,
            }
            client_options.update(
                {
                    name: value
                    for name, value in optional_parameters.items()
                    if value is not None
                }
            )

            self._clients[role] = ChatOpenAI(**client_options)
        return self._clients[role]

    async def invoke_structured(
        self,
        *,
        role: ModelRole,
        schema: type[SchemaT],
        system_prompt: str,
        user_prompt: str,
    ) -> ModelInvocationResult[SchemaT]:
        client = self._client(role)
        runnable = client.with_structured_output(
            schema,
            method="json_schema",
            include_raw=False,
            strict=True,
        )
        usage_callback = UsageMetadataCallbackHandler()
        try:
            parsed = await runnable.ainvoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ],
                config={"callbacks": [usage_callback]},
            )
        except Exception as exc:
            raise AIApplicationError(
                AIErrorCode.MODEL_UNAVAILABLE,
                f"The {role.value} model call failed.",
            ) from exc

        if not isinstance(parsed, schema):
            raise AIApplicationError(
                AIErrorCode.MODEL_INVALID_OUTPUT,
                f"The {role.value} model returned an invalid structured output.",
            )

        usage_metadata: dict[str, Any] = {}
        for item in usage_callback.usage_metadata.values():
            usage_metadata["input_tokens"] = int(
                usage_metadata.get("input_tokens", 0)
            ) + int(item.get("input_tokens", 0))
            usage_metadata["output_tokens"] = int(
                usage_metadata.get("output_tokens", 0)
            ) + int(item.get("output_tokens", 0))
            usage_metadata["total_tokens"] = int(
                usage_metadata.get("total_tokens", 0)
            ) + int(item.get("total_tokens", 0))
        usage = {
            "input_tokens": int(usage_metadata.get("input_tokens", 0)),
            "output_tokens": int(usage_metadata.get("output_tokens", 0)),
            "total_tokens": int(usage_metadata.get("total_tokens", 0)),
        }
        return ModelInvocationResult(
            parsed=cast(SchemaT, parsed),
            model=self._specs[role].model,
            usage=usage,
        )


def build_default_model_gateway() -> LangChainOpenAIModelGateway:
    """Build the production gateway from validated application settings."""

    from app.core.config import settings

    return LangChainOpenAIModelGateway(
        api_key=settings.openai_api_key_value,
        specs={
            ModelRole.ROUTER: ModelSpec(
                model=settings.ai_router_model,
                use_responses_api=False,
                temperature=0.0,
                max_tokens=400,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            ),
            ModelRole.ALFRED: ModelSpec(
                model=settings.ai_alfred_model,
                use_responses_api=False,
                temperature=0.3,
                max_tokens=1_300,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            ),
            ModelRole.FEEDBACKER: ModelSpec(
                model=settings.ai_feedbacker_model,
                use_responses_api=True,
                temperature=None,
                max_tokens=3_600,
                top_p=None,
                frequency_penalty=None,
                presence_penalty=None,
                reasoning_effort="medium",
                verbosity="medium",
            ),
            ModelRole.CRITIC: ModelSpec(
                model=settings.ai_critic_model,
                use_responses_api=False,
                temperature=0.0,
                max_tokens=800,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            ),
        },
        timeout_seconds=settings.ai_model_timeout_seconds,
        max_retries=settings.ai_model_max_retries,
    )
