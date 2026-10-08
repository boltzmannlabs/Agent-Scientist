"""Profile-local authorization granted only by the reviewed /Add_boltz flow."""

import hashlib
import hmac

from agent.secret_scope import build_profile_secret_scope
from sci_constants import get_sci_home, sci_home_key
from sci_cli.plugins_state import PluginState

from .nodeapi_helpers import validate_api_key

KEY_NAME = "BOLTZMANN_API_KEY"
AUTH_MESSAGE = "Boltzmann is locked. Run /Add_boltz in this profile and enter a valid API key."


def current_key():
    # Read the owning profile, never a different profile's inherited process env.
    # Re-reading also notices local key removal/rotation between calls.
    return (build_profile_secret_scope(get_sci_home()).get(KEY_NAME) or "").strip()


def fingerprint(key):
    return hashlib.sha256(f"{sci_home_key()}\0{key}".encode()).hexdigest()


def available():
    """Cheap discovery gate; execution independently revalidates with the service."""
    key = current_key()
    if not key:
        return False
    try:
        receipt = PluginState("boltzmann").get("authorization", "")
    except RuntimeError:
        return False
    return isinstance(receipt, str) and hmac.compare_digest(receipt, fingerprint(key))


def authorize_saved_key():
    """Called only after the secure prompt validated and persisted the supplied key."""
    key = current_key()
    if not key:
        raise ValueError("No saved Boltzmann credential")
    PluginState("boltzmann").set("authorization", fingerprint(key))


def require_authorized():
    if not available():
        raise PermissionError(AUTH_MESSAGE)
    key = current_key()
    if not validate_api_key(key):
        raise PermissionError(
            "Boltzmann authorization failed or the service is unreachable. "
            "No operation ran. Check connectivity or replace the key with /Add_boltz."
        )
    return key
