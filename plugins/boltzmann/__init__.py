"""Agent Scientist's bundled, credential-gated Boltzmann connector."""

import json
from functools import partial

from .auth import available
from .schemas import SCHEMAS
from . import tools


def _call(handler, args, **kwargs):
    try:
        result = handler(**args)
        return json.dumps(result) if isinstance(result, dict) else result
    except Exception:
        # HTTP exception strings may include signed URLs or credential-bearing data.
        return json.dumps({"error": "Boltzmann operation failed. Check service connectivity and supplied parameters; no success is confirmed."})


def register(ctx):
    from .onboarding import add_boltz, register_skills
    ctx.register_command("add_boltz", lambda raw_args: add_boltz(ctx, raw_args),
                         description="Securely authorize Boltzmann with /Add_boltz",
                         args_hint="[--now] [--replace]", argument_mode="options", cli_only=True)
    if available():
        register_skills(ctx)
    for schema in SCHEMAS:
        ctx.register_tool(name=schema["name"], toolset="boltzmann", schema=schema,
                          handler=partial(_call, getattr(tools, "handle_" + schema["name"])),
                          check_fn=available, description=schema.get("description", ""))
