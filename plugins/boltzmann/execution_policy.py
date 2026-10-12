"""Expose the authorized provider before the model chooses a scientific skill.

Plugin skills deliberately live outside the ordinary available-skills index.
The existing prompt-section API freezes this discovery guidance per session;
the execution gate still revalidates credentials independently on every call.
"""

from .auth import available


AUTHORIZED_EXECUTION_POLICY = """Boltzmann scientific execution routing

This profile had /Add_boltz authorization when this session's policy was built.
That is not a live service check or permission to bypass session tool restrictions.
For scientific execution, inspect Boltzmann BEFORE choosing a different provider
or a local-generation skill. Load skill_view(name='boltzmann:tools'), then its
module registry and the matching complete contract. Plugin skills are not in
the ordinary available-skills index; absence from that index is not absence of
the Boltzmann workflow. If tools are deferred, use tool_search for Boltzmann,
tool_describe for schemas, and tool_call for the discovered plugin operations.

For 'generate 20 random antibodies' or similar random-antibody requests, start
with references/modules/protein-antibody-generation.md in boltzmann:tools.
Preserve the requested count; ask for missing format and experiment-name
confirmation. Do not invent pairing guarantees or promise the requested count
before inspecting the actual heavy/light outputs and the contract's limitations.

When a verified contract matches the requested inputs and outputs, execute with
the Boltzmann plugin tools, not ToolUniverse alternatives, p-IgGen, Hugging Face,
or locally generated scripts. Supporting skills may guide input preparation and
output validation; they must not change the chosen execution provider. Do not
inspect GPUs or install/download a local generator before this provider decision.

If the session cannot discover the required plugin tools or boltzmann:tools,
stop and explain the missing setup/session access; request a restart of agent-sci
after /Add_boltz. Do not treat deferred activation as 'no suitable tool exists'.
If authentication fails, a contract is blocked, or scientific inputs are missing,
stop and explain/ask; do not silently switch providers. For a nonmatching task,
explain the limitation and obtain explicit approval before alternative scientific
execution. An explicit request for local/other-provider execution is an override,
not permission to copy credentials or bypass execution permissions. Literature,
general coding, and non-execution questions do not have to use Boltzmann.

Submit once; retain and poll the same job ID. Never duplicate a pending or
ambiguously submitted job. Verify actual artifacts and counts, report partial
results honestly, and never automatically submit a top-up job.
"""


def render_execution_policy(_session_info):
    """Use the owning profile's local receipt, with no network or secret output."""
    return AUTHORIZED_EXECUTION_POLICY if available() else ""
