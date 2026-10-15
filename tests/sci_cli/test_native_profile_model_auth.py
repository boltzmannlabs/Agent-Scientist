"""Science profiles reuse shared model credentials without copying secrets."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock


def test_inline_model_rejected_before_wizard_selections(tmp_path, monkeypatch):
    from sci_cli.config import atomic_config_replace
    from sci_cli.native_profile_wizard import create_wizard

    monkeypatch.setattr(Path, 'home', lambda: tmp_path)
    home = tmp_path / '.sci'
    home.mkdir()
    monkeypatch.setenv('SCI_HOME', str(home))
    atomic_config_replace(home / 'config.yaml', {'model': {
        'provider': 'custom', 'api_key': 'fixture-secret', 'default': 'fixture'}})
    ui = SimpleNamespace(show=Mock(), ask=Mock(), choose=Mock())
    create_wizard(SimpleNamespace(), '/create_profile example', ui=ui, source_home=home)
    ui.ask.assert_not_called()
    ui.choose.assert_not_called()
    assert 'inline API key' in str(ui.show.call_args_list)
    assert 'fixture-secret' not in str(ui.show.call_args_list)


def test_created_profile_resolves_shared_model_without_secret_copy(tmp_path, monkeypatch):
    from sci_cli.config import atomic_config_replace, read_user_config_raw
    from sci_cli.native_profile_creation import create_native, profile_scope
    from sci_cli.auth import write_credential_pool
    from sci_cli.runtime_provider import resolve_runtime_provider
    from agent.credential_pool import PooledCredential

    monkeypatch.setattr(Path, 'home', lambda: tmp_path)
    main = tmp_path / 'science-root'
    main.mkdir()
    monkeypatch.setenv('SCI_HOME', str(main))
    monkeypatch.setattr('sci_constants.get_default_sci_root', lambda **_: main)
    monkeypatch.setattr('sci_cli.profiles._get_profiles_root', lambda: main / 'profiles')
    monkeypatch.setattr('sci_cli.profiles._get_default_sci_home', lambda: main)
    monkeypatch.setattr('sci_cli.profiles._notify_multiplexer', lambda *_: None)
    monkeypatch.setattr('sci_cli.profiles._maybe_register_gateway_service', lambda *_: None)
    provider = 'fixture-gateway'
    url = 'http://127.0.0.1:54321/v1'
    atomic_config_replace(main / 'config.yaml', {
        'model': {'provider': provider, 'default': 'fixture'},
        'providers': {provider: {'base_url': url}}})
    with profile_scope(main):
        entry = PooledCredential(provider=provider, id='fixture', label='Fixture',
            auth_type='api_key', priority=0, source='manual',
            access_token='fixture-secret', base_url=url)
        write_credential_pool(provider, [entry.to_dict()])
        create_native('study', main, [], [], [], {'backend': 'local'}, 'Scientist')
    child = main / 'profiles' / 'study'
    assert child.is_dir()
    assert 'fixture-secret' not in str(read_user_config_raw(child / 'config.yaml'))
    for home in (main, child, main):
        with profile_scope(home):
            runtime = resolve_runtime_provider(requested=provider, target_model='fixture')
            assert runtime['api_key'] == 'fixture-secret'
            assert runtime['base_url'].rstrip('/') == url
    if (child / 'auth.json').exists():
        assert 'fixture-secret' not in (child / 'auth.json').read_text()
