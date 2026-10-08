"""Custom Qwen requests must stay within the model template's effort vocabulary."""

from agent.reasoning_effort import effort_display_label
from agent.transports.chat_completions import ChatCompletionsTransport
from sci_constants import parse_reasoning_effort
from providers import get_provider_profile


def test_custom_qwen_efforts_match_request_and_status():
    transport = ChatCompletionsTransport()
    expected = {
        "none": "none", "minimal": "low", "low": "low", "medium": "medium",
        "high": "medium", "xhigh": "xhigh", "max": "xhigh", "ultra": "xhigh",
    }
    for provider in ("custom", "custom:qwen_custom", "vllm"):
        profile = get_provider_profile(provider)
        for model in ("qwen3.8-27b", "Qwen/Qwen3.8-27B", "Qwen3.8-27B-FP8"):
            for requested, sent in expected.items():
                kwargs = transport.build_kwargs(
                    model, [{"role": "user", "content": "Hello"}],
                    provider_profile=profile, base_url="http://127.0.0.1:8000/v1",
                    reasoning_config=parse_reasoning_effort(requested),
                )
                assert kwargs["reasoning_effort"] == sent
                label = effort_display_label(requested, provider, model)
                assert label == (requested if requested == sent else f"{requested} (sends {sent} on this route)")
            assert "reasoning_effort" not in transport.build_kwargs(
                model, [{"role": "user", "content": "Hello"}],
                provider_profile=profile, reasoning_config=None,
            )
    # A model-family match must not restrict unrelated Qwen or arbitrary custom models.
    for model in ("qwen3.8-max", "qwen3.5-27b", "qwen3.8-27bother", "my-model"):
        kwargs = transport.build_kwargs(
            model, [{"role": "user", "content": "Hello"}],
            provider_profile=get_provider_profile("custom"),
            reasoning_config=parse_reasoning_effort("high"),
        )
        assert kwargs["reasoning_effort"] == "high"
