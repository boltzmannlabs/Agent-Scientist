"""Desktop's bundled catalog must stay on the local source through the RPC."""
from unittest.mock import Mock


def test_bundled_browse_uses_real_local_catalog_without_network(monkeypatch):
    import socket
    from tui_gateway import server
    from tui_gateway.contracts.tools_mcp_plugins import SkillsManageParams
    from tools.skills_hub_official import OptionalSkillSource

    blocked = Mock(side_effect=AssertionError("offline browse attempted network"))
    monkeypatch.setattr(socket, "create_connection", blocked)
    params = SkillsManageParams(action="browse", source="official", page=1, page_size=20)
    result = server._methods["skills.manage"](1, params.model_dump(exclude_none=True))
    local = {entry.identifier for entry in OptionalSkillSource().list_local()}
    assert local
    assert "error" not in result
    assert result["result"]["items"]
    assert all(item["identifier"] in local for item in result["result"]["items"])
    blocked.assert_not_called()
