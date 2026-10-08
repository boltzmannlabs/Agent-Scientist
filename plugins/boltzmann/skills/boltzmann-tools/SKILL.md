---
name: boltzmann-tools
description: Use authenticated Boltzmann platform operations for explicitly specified scientific workflows.
---

# Boltzmann workflows

Requires this profile's user to authorize access with `/Add_boltz` and start a new session.
Never ask for an API key in conversation, write one into a tool argument, or bypass the authorization gate.

All five platform operations are prerequisites, not separate scientific capabilities:

- `boltzmann_submit`: submit a fully specified job, with its documented job name, experiment name and input object.
- `boltzmann_status`: poll the job name and document ID returned by submission; polling must not resubmit it.
- `boltzmann_download`: retrieve a signed output URL returned by a completed job.
- `boltzmann_upload`: upload an explicitly approved local input file.
- `boltzmann_fetch_tool_log`: retrieve a specified experiment's durable record.

Use the service's documented workflow schema or an installed scientific skill for the job's parameters.
Do not invent schemas, sequences, scientific assumptions, or missing requirements. Ask the user when uncertain.
Confirm paid submissions and sensitive uploads before executing them. Authorization alone is not approval
to upload research data or spend credits. Report timeouts and failures honestly; check job status before
retrying a submission to avoid duplicate charges. Successful execution does not establish scientific validity.

Source: the existing Agent Scientist Boltzmann connector, whose service endpoint is
`https://nodeapis.boltzmann.co`. This skill supplies operational guidance, not scientific validation.
