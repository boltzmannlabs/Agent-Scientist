"""Release skill choices, applied at first config creation, never at runtime merge."""

from copy import deepcopy


INITIAL_DISABLED_SKILLS = (
    "api-integration-review",
    "architecture-diagram",
    "ascii-video",
    "baoyu-infographic",
    "blocked-page-recovery",
    "claude-design",
    "design-md",
    "email-inbox-triage",
    "gif-search",
    "himalaya",
    "humanizer",
    "manim-video",
    "obsidian",
    "p5js",
    "popular-web-designs",
    "songsee",
    "songwriting-and-ai-music",
    "xurl",
    "youtube-content",
)


def with_initial_skill_defaults(config: dict) -> dict:
    """Seed a missing selection without overriding explicit lists, nulls or platform choices.

    Call only when creating a configuration. Putting this policy in DEFAULT_CONFIG
    would silently change existing installations that omitted skills.disabled.
    """
    result = deepcopy(config)
    skills = result.setdefault("skills", {})
    if isinstance(skills, dict):
        skills.setdefault("disabled", list(INITIAL_DISABLED_SKILLS))
    return result
