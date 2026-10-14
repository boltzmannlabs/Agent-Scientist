"""Defer reviewed MCP edits in this CLI only, without changing watcher settings."""

from contextlib import contextmanager
from copy import deepcopy


@contextmanager
def deferred_save(cli, home, before, after):
    from sci_constants import get_sci_home
    from sci_cli.config import _expand_env_vars
    if cli is None or home.resolve() != get_sci_home().resolve():
        yield
        return
    previous = deepcopy(getattr(cli, "_science_deferred_mcp", {}))
    pending = deepcopy(previous)
    old, new = before.get("mcp_servers", {}), after.get("mcp_servers", {})
    for name in old.keys() | new.keys():
        if old.get(name) != new.get(name):
            pending[name] = _expand_env_vars(new.get(name))
    cli._science_deferred_mcp = pending
    try:
        yield
    except Exception:
        cli._science_deferred_mcp = previous
        raise


def defer_watcher_reload(cli, new_mcp):
    pending = getattr(cli, "_science_deferred_mcp", {})
    if not pending:
        return False
    old = cli._config_mcp_servers
    changes = {name for name in old.keys() | new_mcp.keys() if old.get(name) != new_mcp.get(name)}
    unrelated = {name for name in changes if name not in pending or new_mcp.get(name) != pending[name]}
    cli._config_mcp_servers = new_mcp
    if unrelated:
        # The existing reloader reconnects ALL servers. Running it here would also
        # activate the deferred additions and replace the conversation's tool prefix.
        print("MCP edits detected: " + ", ".join(sorted(unrelated)) +
              ". This CLI has next-session changes pending. Restart to apply them, or explicitly "
              "approve /reload-mcp (applies all changes and rebuilds the tool prefix).")
    return True
