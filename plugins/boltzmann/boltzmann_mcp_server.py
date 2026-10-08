"""Stdio MCP adapter for Boltzmann platform-tools mode only."""

import sys
from pathlib import Path
from typing import Any

PLUGIN_DIR = Path(__file__).resolve().parent
# Import this plugin as a package; its tools.py must not shadow Sci tools/.
sys.path = [entry for entry in sys.path if Path(entry).resolve() != PLUGIN_DIR]
sys.path.insert(0, str(PLUGIN_DIR.parent))

from mcp.server import MCPServer

from boltzmann.tools import (
    handle_boltzmann_download,
    handle_boltzmann_fetch_tool_log,
    handle_boltzmann_status,
    handle_boltzmann_submit,
    handle_boltzmann_upload,
)
from boltzmann.auth import require_authorized

mcp = MCPServer(
    "boltzmann",
    description="Authenticated Boltzmann scientific platform tools",
)


@mcp.tool()
def boltzmann_submit(
    job_name: str,
    experiment_data: dict[str, Any],
    experiment_name: str,
) -> str:
    """Submit one fully specified Boltzmann platform-tools job."""
    return handle_boltzmann_submit(
        job_name=job_name,
        experiment_data=experiment_data,
        experiment_name=experiment_name,
    )


@mcp.tool()
def boltzmann_status(
    job_name: str,
    doc_id: str,
    output_folder: str | None = None,
) -> str:
    """Poll the existing Boltzmann job identified by job_name and doc_id."""
    return handle_boltzmann_status(
        job_name=job_name,
        doc_id=doc_id,
        output_folder=output_folder,
    )


@mcp.tool()
def boltzmann_download(download_url: str, output_folder: str) -> str:
    """Download one signed output artifact from a completed Boltzmann job."""
    return handle_boltzmann_download(
        download_url=download_url,
        output_folder=output_folder,
    )


@mcp.tool()
def boltzmann_upload(local_path: str) -> str:
    """Upload one validated local input file to Boltzmann platform storage."""
    return handle_boltzmann_upload(local_path=local_path)


@mcp.tool()
def boltzmann_fetch_tool_log(collection: str, experiment_id: str) -> str:
    """Read one durable platform-tools record without mutating it."""
    return handle_boltzmann_fetch_tool_log(
        collection=collection,
        experiment_id=experiment_id,
    )


def main() -> None:
    try:
        require_authorized()
    except PermissionError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
