"""Extracted APIRouter modules for the dashboard web server.

Each exposes ``router`` (profiles also ``sessions_router``), mounted by ``web_server`` at the
point the routes were originally registered so match order is unchanged. Shared helpers/state
come through the late-binding seam in ``sci_cli.web_deps``.
"""
