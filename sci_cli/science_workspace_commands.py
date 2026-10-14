"""Thin CLI edges for science inventory, profile editing, and saved transcript browsing."""


class ScienceWorkspaceCommandsMixin:
    def _handle_capabilities_command(self, cmd):
        from sci_cli.capability_overview import run
        run(self, cmd)

    def _handle_boltzmann_tools_command(self, cmd):
        from sci_cli.science_catalog_view import run_catalog
        run_catalog(self, cmd)

    def _handle_update_profile_command(self, cmd):
        from sci_cli.native_profile_update import update_wizard
        update_wizard(self, cmd)
