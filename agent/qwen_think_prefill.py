"""Restore Qwen's template-prefilled think opener before the shared scrubber.

Some OpenAI-compatible servers return ``thoughts</think>answer`` in content:
the opening tag was part of the server's prompt, not its generated tokens.
Buffer that ambiguous prefix so it cannot leak to a streaming answer consumer.
Native reasoning fields and other models keep their existing delivery path.
"""

import re


class QwenThinkPrefill:
    def __init__(self, model: str, effort: str | None = None):
        bare = (model or "").lower().rsplit("/", 1)[-1]
        self.pending = effort != "none" and bool(re.match(r"^qwen3\.8-27b(?:$|[-:])", bare))
        self.parts: list[str] = []
        self.tail = ""

    def feed(self, text: str, *, native_reasoning: bool = False) -> str:
        if not self.pending:
            return text
        self.parts.append(text)
        scan = self.tail + text
        self.tail = scan[-8:]
        if native_reasoning or "<think>" in scan:
            return self._release()
        if "</think>" in scan:
            return "<think>" + self._release()
        return ""

    def _release(self) -> str:
        text = "".join(self.parts)
        self.parts.clear()
        self.pending = False
        return text

    def finish(self, finish_reason: str | None) -> str:
        if not self.pending:
            return ""
        text = self._release()
        # A completed plain answer is valid. An interrupted/length-limited
        # ambiguous prefix is not evidence of an answer; keep it in reasoning.
        return "<think>" + text if text and finish_reason in (None, "length") else text


def restore_qwen_think_prefill(response, model: str, effort: str | None = None):
    """Repair a newly received response, never previously cached conversation."""
    for choice in getattr(response, "choices", ()):
        message = getattr(choice, "message", None)
        content = getattr(message, "content", None)
        if not isinstance(content, str):
            continue
        native = getattr(message, "reasoning_content", None) or getattr(message, "reasoning", None)
        parser = QwenThinkPrefill(model, effort)
        message.content = parser.feed(content, native_reasoning=bool(native)) + parser.finish(
            getattr(choice, "finish_reason", None))
    return response
