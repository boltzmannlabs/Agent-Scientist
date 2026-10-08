"""Schemas for the tools-only Boltzmann integration."""

SCHEMAS = [
    {
        "name": "boltzmann_submit",
        "description": (
            "Submit one validated platform-tools job. Use the exact job name and payload "
            "from the selected Boltzmann skill module. First load skill_view(name='boltzmann:tools'). "
            "Never resubmit after an ambiguous timeout."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "job_name": {
                    "type": "string",
                    "description": "Exact job_name from the selected Boltzmann contract.",
                },
                "experiment_data": {
                    "type": "object",
                    "description": "Complete payload matching that job's documented schema.",
                },
                "experiment_name": {
                    "type": "string",
                    "description": "User-supplied or explicitly confirmed experiment name.",
                },
            },
            "required": ["job_name", "experiment_data", "experiment_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "boltzmann_status",
        "description": (
            "Poll an existing Boltzmann platform-tools job. Use the exact job_name and doc_id "
            "returned by boltzmann_submit; polling never creates another job."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "job_name": {"type": "string"},
                "doc_id": {"type": "string"},
                "output_folder": {
                    "type": "string",
                    "description": "Optional local results directory used by the active session.",
                },
            },
            "required": ["job_name", "doc_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "boltzmann_download",
        "description": "Download one output artifact from a completed Boltzmann job.",
        "input_schema": {
            "type": "object",
            "properties": {
                "download_url": {
                    "type": "string",
                    "description": "Signed HTTPS URL returned by boltzmann_status.",
                },
                "output_folder": {
                    "type": "string",
                    "description": "Local directory in which to save the artifact.",
                },
            },
            "required": ["download_url", "output_folder"],
            "additionalProperties": False,
        },
    },
    {
        "name": "boltzmann_upload",
        "description": "Upload one validated local input file to Boltzmann platform storage.",
        "input_schema": {
            "type": "object",
            "properties": {
                "local_path": {
                    "type": "string",
                    "description": "Absolute path to the already validated input file.",
                }
            },
            "required": ["local_path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "boltzmann_fetch_tool_log",
        "description": (
            "Read the durable platform-tools record for a known collection and experiment ID. "
            "This is diagnostic and never submits or mutates a job."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "collection": {
                    "type": "string",
                    "description": "Verified durable collection name from the skill contract.",
                },
                "experiment_id": {
                    "type": "string",
                    "description": "Exact document ID returned by the current workflow.",
                },
            },
            "required": ["collection", "experiment_id"],
            "additionalProperties": False,
        },
    },
]
