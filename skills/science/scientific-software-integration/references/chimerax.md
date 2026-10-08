# ChimeraX Deployment and Scripting

Use this reference for UCSF ChimeraX installation, embedded scripting, and native Sci integration. The Debian extraction, launch interface, headless structure analysis, PDB export, and registered-tool dispatch were exercised successfully. No end-to-end image-rendering recipe is claimed here.

## 1. Select the Correct UCSF Product

Start from the official entry points:

- https://www.rbvi.ucsf.edu/chimerax/
- https://www.rbvi.ucsf.edu/chimerax/download.html
- https://www.rbvi.ucsf.edu/chimerax/docs/

Inspect a Python distribution's publisher and description rather than assuming it is unrelated because its release numbering differs from the desktop application. The UCSF `chimerax` Python distribution describes molecular analysis and manipulation functionality without the application's GUI components. Choose by required capability, and recheck the current distribution description and Python support.

## 2. Discover the Actual Installer

The official download page uses release metadata and JavaScript-generated links. Retrieve the following with permitted web tools or `terminal`, and inspect their contents with `read_file` when saved locally:

- `data/release-info/enabled.json`, relative to the ChimeraX site directory, lists enabled release channels.
- `data/release-info/<channel>.json` provides platform entries, artifact links, sizes, and checksums.
- The download page's referenced `js/relutil-*.js` defines the installer link base. Resolve the filename from the page instead of pinning a historical JavaScript version.

Choose the platform entry matching the live OS and architecture. Build the URL from the actual installer base and the selected artifact's `link`; do not invent a generic tarball endpoint.

The exercised noncommercial installer flow used `/chimerax/cgi-bin/secure/chimerax-get.py?file=<artifact-link>`:

1. The initial GET returned a license page, not the package.
2. Its form supplied `file` and submitted `choice=Accept` by POST.
3. After authorized acceptance, the response contained an actual download link in an HTML anchor and a meta-refresh target, with a generated identifier.
4. Following that returned link produced the installer. A redirect-following HTTP client alone does not process HTML meta-refresh.

Reinspect the live form before submitting it. Never persist a generated identifier or treat acceptance of noncommercial terms as authorization for commercial use. Validate the resulting file against the selected release metadata; HTTP success and an installer filename do not establish that the body is a binary package.

## 3. User-Local Debian Extraction

This is a Linux recipe for the publisher's Debian package, not a cross-platform installation command. Choose fresh installer and destination variables before invoking it through `terminal`:

    dpkg-deb -I "$INSTALLER"
    dpkg-deb -x "$INSTALLER" "$DEST"
    file "$DEST/usr/bin/chimerax"
    file "$DEST/usr/lib/ucsf-chimerax/bin/ChimeraX"
    ldd "$DEST/usr/lib/ucsf-chimerax/bin/ChimeraX"

The inspected package layout placed the application in `usr/lib/ucsf-chimerax/`, with a `usr/bin/chimerax` symlink to its `bin/ChimeraX` launcher and an internally bundled Python runtime. Resolve the current package layout rather than assuming it is immutable.

For this layout, linking the actual launcher into an existing user PATH directory worked:

    ln -s "$DEST/usr/lib/ucsf-chimerax/bin/ChimeraX" "$HOME/.local/bin/chimerax"

Check for an existing destination before creating the link; do not overwrite another installation blindly. Through `terminal`, run `chimerax --version` to establish launch success. Extraction bypasses package-manager dependency installation, so proceed to independent functional probes even if the launcher has no unresolved `ldd` entries.

## 4. Embedded Command Dispatch

Use `terminal(command="chimerax --help", timeout=120)` to verify flags against the installed version. The exercised interface used lowercase `--nogui` for headless operation, `--cmd` for ChimeraX command-language input, and `--script` for Python files.

Inside a Python file run by ChimeraX, use the module function:

    from chimerax.core.commands import run
    run(session, "open <PDB_ID_OR_PATH>")

The application injected the active `session` into the script namespace. Installed source documented model access as `session.models.list()`. Use that explicit access pattern rather than assuming a standalone `models` global. Execute Python through the application's scripting entry point; a Python expression passed to `--cmd` is interpreted as a ChimeraX command.

Treat these as interface primitives, not a complete analysis test. Select the application's documented termination behavior and run the whole probe with a bounded timeout and a captured return code. Confirm the loaded input and inspect the output before declaring the requested operation successful.

## 5. Rendering Is a Separate Capability

Consult the installed version's image-save documentation and headless-rendering prerequisites before preparing a rendering test. Loading, coloring, or adjusting a view does not prove that an image was saved. Claim rendering only after the command exits successfully and the produced image has been inspected. Do not infer removal of a feature or an API redesign from an unknown command or an attribute error in a hand-written probe.

## 6. Native Sci Plugin Integration

Use an existing installation rather than downloading or accepting another license when the executable already resolves and functional probes pass. Implement the supported local-plugin surface under `$SCI_HOME/plugins/chimerax/`, not Sci core. A manifest with `manifest_version: 2`, `api_version: 1`, and `provides_tools` accompanies `register(ctx)` in `__init__.py`. Register separate version/introspection and execution tools through `ctx.register_tool`, with an executable-availability `check_fn`.

Use an embedded runner launched by the application's own interpreter:

    chimerax --nogui --silent --nostatus --exit --script <runner.py>

The inspected application's help advertised `--usedefaults`, but launch emitted an unsupported-option warning; omit this flag unless the installed version genuinely supports it. The runtime can execute scripts without GUI rendering.

Pass a JSON payload through a unique run directory and a child-only environment variable. Resolve persistent data with `plugins.plugin_storage.plugin_data_dir("chimerax")`, keeping payloads, logs, result reports, and default outputs outside the plugin installation directory. Use argument-list subprocess execution with a dedicated working directory, not `shell=True`. Validate local input paths, argument types, and a bounded timeout before launching. Terminate the owned process group on timeout; retain complete log files and bounded log excerpts.

In the embedded runner, quote local paths with `StringArg.unparse` before `run(session, "open " + quoted_path)`. Dispatch command-language strings with `chimerax.core.commands.run`. To support a trusted user Python script while preserving exceptions, use `runpy.run_path(script_path, init_globals={"session": session}, run_name="__main__")` inside a try/except. The application's `open_python_script` logs ordinary exceptions internally; merely running a `runscript` command can therefore hide script failure from a parent process. Write an explicit completion report and require both its success flag and the subprocess exit code. Treat a missing completion report as failure, even with exit code zero. Scripts and commands have host filesystem/network access; this integration is not a security sandbox.

Report model inventory from `session.models.list()`: `id_string`, `name`, model type, and (when present) `num_atoms`, `num_residues`, and chain IDs. Inventory only new or modified files in a dedicated output directory; identify saves outside that directory as outside the artifact inventory. Persist the final enriched report for successful and failed runs.

Validate and enable with the supported CLI:

    sci plugins doctor "$SCI_HOME/plugins/chimerax" --ci
    sci plugins enable chimerax --no-allow-tool-override

Verify enablement by reading the exact plugin back. Then use a fresh Sci process to resolve the actual CLI selection via `sci_cli.tools_config._get_platform_tools`, inspect raw definitions through `model_tools.get_tool_definitions(..., skip_tool_search_assembly=True)`, and call both tools with `tools.registry.registry.dispatch`. If the CLI selection excludes the toolset, use `sci tools enable chimerax --platform cli`, preserving unrelated settings. Tool enablement takes effect in new sessions; do not mutate the live conversation's tool schemas.

For dependency-free tests inside the Sci runtime, use `sci --run-module unittest discover -s <test-directory> -v`. To execute a verification file with that runtime, invoke `runpy.run_path` from a unittest case. Do not use `sci --run-module runpy /absolute/script.py`: the runpy command-line entry treats that argument as a module name, not a file path.

Use RCSB entry 1CRN as a small crambin fixture, not as an antibody fixture. Headless loading, atom/residue inventory, PDB export, and a Python-script distance measurement can be checked independently against the PDB coordinate fields. The exercised command `distance #1/A:1,2@CA monitor false` returns a numeric distance through `run(session, ...)`. Include malformed inputs, nonexistent paths, command errors, user-script exceptions, filesystem failures, and timeout tests. These capabilities do not establish image rendering; keep rendering explicitly unverified until an actual image passes inspection.
