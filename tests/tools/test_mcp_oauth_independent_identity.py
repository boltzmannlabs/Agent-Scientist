"""SCI must not borrow another application's hosted OAuth identity."""

from unittest.mock import MagicMock

import pytest


def test_unconfigured_identity_preserves_dcr_and_requires_explicit_cimd(tmp_path, monkeypatch):
    from tools import mcp_oauth
    from tools.mcp_oauth_manager import MCPOAuthManager, reset_manager_for_tests

    monkeypatch.setenv("SCI_HOME", str(tmp_path))
    stdin = MagicMock()
    stdin.isatty.return_value = True
    monkeypatch.setattr(mcp_oauth.sys, "stdin", stdin)
    reset_manager_for_tests()
    manager = MCPOAuthManager()
    try:
        provider = manager.get_or_build_provider("fixture", "https://mcp.example.org/mcp", {})
        assert provider.context.client_metadata_url is None
        with pytest.raises(ValueError, match="oauth.client_metadata_url"):
            mcp_oauth._maybe_use_cimd({"cimd": True})
        # Constructing a provider does not authenticate or invoke business tools.
        assert not (tmp_path / "mcp-tokens").exists()
    finally:
        for port, sock in list(mcp_oauth._reserved_sockets.items()):
            sock.close()
            mcp_oauth._reserved_sockets.pop(port)
        reset_manager_for_tests()


def test_explicit_identity_is_profile_scoped_across_a_b_a(tmp_path, monkeypatch):
    from tools import mcp_oauth
    from tools.mcp_oauth_manager import MCPOAuthManager, reset_manager_for_tests
    from agent.secret_scope import reset_multiplex_context, set_multiplex_context
    from tui_gateway.server import (
        _profile_runtime_scope_tokens,
        _release_profile_runtime_scope_tokens,
    )

    stdin = MagicMock()
    stdin.isatty.return_value = True
    monkeypatch.setattr(mcp_oauth.sys, "stdin", stdin)
    reset_manager_for_tests()
    manager = MCPOAuthManager()
    homes = [tmp_path / "a", tmp_path / "b"]
    providers = []
    multiplex = set_multiplex_context(True)
    try:
        for home in (homes[0], homes[1], homes[0]):
            home.mkdir(exist_ok=True)
            url = f"https://{home.name}.example.org/oauth/client.json"
            scopes = _profile_runtime_scope_tokens(str(home))
            try:
                providers.append(manager.get_or_build_provider(
                    "fixture", "https://mcp.example.org/mcp", {"client_metadata_url": url}
                ))
            finally:
                _release_profile_runtime_scope_tokens(scopes)
            assert providers[-1].context.client_metadata_url == url
        assert providers[0] is providers[2]
        assert providers[0] is not providers[1]
    finally:
        # Close only sockets these fixtures reserved.
        for provider in providers:
            port = provider.context.client_metadata.redirect_uris[0].port
            sock = mcp_oauth._reserved_sockets.pop(port, None)
            if sock:
                sock.close()
        mcp_oauth._assigned_cimd_ports.clear()
        reset_manager_for_tests()
        reset_multiplex_context(multiplex)
