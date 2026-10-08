# Sci Desktop ☤

<p align="center">




</p>

**The native desktop app for [Agent Scientist](../../README.md), customized by Boltzmann Labs.** The CLI, gateway and desktop share the agent runtime. Native installer publication is pending SCI release configuration and native-platform verification.

> **Intel Macs:** the `Sci-Setup.dmg` bootstrap installer is built for
> Apple Silicon (arm64) only, so on an Intel Mac it reports "not supported on
> this Mac". The desktop release pipeline also builds a native `darwin-x64`
> bundle (signed, notarized, with its own update feed); use that build, or
> install the [CLI](../../README.md) and run `sci desktop`. See
> [Platform Support](../../website/docs/getting-started/platform-support.md#build-targets-and-support-priority).

<table>
<tr><td><b>Chat with the full agent</b></td><td>Streaming responses, live tool activity, structured tool summaries, and the same conversation history as every other Sci surface.</td></tr>
<tr><td><b>Side-by-side previews</b></td><td>Render web pages, files, and tool outputs in a right-hand pane while you keep chatting.</td></tr>
<tr><td><b>File browser</b></td><td>Explore and preview the working directory without leaving the app.</td></tr>
<tr><td><b>Voice</b></td><td>Talk to Sci and hear it back.</td></tr>
<tr><td><b>Settings & onboarding</b></td><td>Manage providers, models, tools, and credentials from a real UI. First-run setup gets you to your first message in seconds.</td></tr>
<tr><td><b>Stays current</b></td><td>Built-in updates pull the latest agent and rebuild the app in place.</td></tr>
</table>

---

## Install

### Install with Sci (recommended)

Already have the Sci CLI? Just run:

```bash
sci desktop
```

It builds and launches the GUI against your existing install — same config, keys, sessions, and skills. If Desktop cannot find a usable runtime or saved remote connection, first launch lets you connect to an existing Sci gateway or install Sci locally. Local onboarding then walks you through choosing a provider and model.

### Prebuilt installers

Prebuilt SCI installers are not published yet. Use the source-development instructions below; see [release readiness](../../SCI_MIGRATION.md) for verification limits.

---

## Updating

Update through the owner of the installed artifact: Windows App Installer for
sideload MSIX, Microsoft Store for Store packages, and `electron-updater` for
macOS bundles. Source-built apps use the checkout update handoff.

`sci update` updates managed source checkouts; it does not rewrite a bundled
payload. See [BUILDING.md](BUILDING.md) for package and release contracts.

---

## Screenshot shortcut (macOS)

Enable **Settings → Keyboard Shortcuts → Screenshot shortcut**, then press the
left and right Command keys together in any app. Sci captures that app's
frontmost window and attaches the image to the last-active Sci composer,
including split-pane chats. It does not send the draft or capture the whole
screen. Release both keys before taking another screenshot.

The shortcut is off by default and saved only on this Mac. macOS requires
**Input Monitoring** and **Screen & System Audio Recording** permission; the
settings row links to the relevant system pane and offers Retry. If macOS asks
to restart the app after granting access, do so before retrying. Review the
attachment before sending, especially when the captured window is sensitive.

## Requirements

Bundled packages provide Python 3.14 and their supported dependencies.
Source/bootstrap builds have a separate preparation path. Platform-native
requirements, including system Git on POSIX, are described in [BUILDING.md](BUILDING.md).
macOS source builds also require Xcode Command Line Tools to compile the native
shortcut helper. Prebuilt installers include it; no compiler is needed at runtime.

---

## Development

Want to hack on the app itself? Install workspace deps from the repo root once, then run the dev server from this directory:

```bash
npm install          # from repo root — links apps/desktop, web, apps/shared
cd apps/desktop
npm run dev          # Vite renderer + Electron, which boots the Python backend
```

Point the app at a specific source checkout, or sandbox it away from your real config:

```bash
# throwaway SCI_HOME, separate Electron userData, distinct app name to avoid the single-instance lock
../../scripts/dev-sandbox.sh npm run dev
SCI_DESKTOP_SCI_ROOT=/path/to/clone npm run dev
SCI_HOME=$HOME/.sci/cache/scratch/throwaway npm run dev
npm run dev:fake-boot   # exercise the startup overlay with deterministic delays
```

### Building installers

```bash
npm run dist:mac     # DMG + zip
npm run dist:win     # MSIX
npm run dist:linux   # AppImage + deb + rpm
npm run pack         # unpacked app under release/ (no installer)
```

These are ordinary packaging commands, not complete tagged payload builds.
Use [BUILDING.md](BUILDING.md) for the native bundled builder, Azure/Apple
signing, R2 artifact publication, and release gates. The current release matrix
publishes Windows and macOS packages; Linux desktop legs are disabled.

### How it works

The bundled app carries the Electron shell, native React chat surface, and
local agent payload. It runs the payload directly from resources. User data
lives in `SCI_HOME` outside the app. Bootstrap builds instead provision a
source installation; Light is a remote-only variant without a local runtime.

The app has three boundaries:

- **Electron** resolves and validates a runnable backend, owns native
  filesystem/git/window capabilities, and exposes a narrow preload bridge.
- **React** owns the Desktop routes, panes, interaction state, and
  `@assistant-ui/react` transcript.
- **Sci Agent** runs as a headless `sci serve` process and exposes the
  `tui_gateway` JSON-RPC/WebSocket API. The renderer connects through
  [`apps/shared`](../shared/), which is also used by the browser dashboard.

A bundled artifact uses its payload. If that payload is unusable, the app
reports damage rather than installing a second checkout. It does not adopt
an arbitrary `sci` command on PATH or a system Python installation.

Non-bundled builds can use the explicit source-root override, development
checkout, completed managed install, or `SCI_DESKTOP_SCI` deployment
override before offering bootstrap. Candidates are probed before use.
A runtime that predates `serve` falls back to headless
`dashboard --no-open`. This is compatibility for the backend command only and
does not launch or embed the dashboard UI.

The Electron orchestration entry point is `electron/main.ts`; pure resolution,
probe, hardening, and platform policies live in focused modules beside it. The
renderer is under `src/`, with shared atoms in `src/store` and transport/native
adapters in `src/lib`.

Before changing the app, read:

- [`AGENTS.md`](./AGENTS.md): architecture, state ownership, resolver/fallback,
  transport, performance, and testing rules.
- [`DESIGN.md`](./DESIGN.md): visual system, information architecture, motion,
  direct manipulation, and keyboard behavior.

### Connections, projects, and switching

Desktop supports a managed local backend, explicit remote gateways, and Sci
Cloud connections. Remote and cloud modes use the same remote-capability path;
authentication and discovery differ, not the renderer feature model.

When no usable local runtime or saved remote connection exists, the first-run
screen offers **Connect to existing Sci** before starting the local installer.
Desktop probes the gateway to discover token or OAuth authentication, requires a
successful HTTP and WebSocket connection test, and saves the connection using
the same encrypted Desktop configuration used by Settings. A saved remote
connection bypasses this choice on later launches. The regular Desktop build
still includes the local-install option; this is a remote operating mode, not a
separate client-only application.

In remote mode the gateway host is the execution boundary: agent tools,
terminal commands, and file operations run against the remote Sci host, not
the computer displaying the Desktop UI.

Remote gateways that sit behind an access proxy may require extra headers on
every HTTP and WebSocket request. Configure them per connection in Settings →
Connections (Extra gateway headers), or add a `headers` object to Desktop's
Electron `userData/connection.json` remote block:

```json
{
  "mode": "remote",
  "remote": {
    "url": "https://hermes.example.com",
    "authMode": "token",
    "token": { "encoding": "safeStorage", "value": "..." },
    "headers": {
      "CF-Access-Client-Id": { "encoding": "safeStorage", "value": "..." },
      "CF-Access-Client-Secret": { "encoding": "safeStorage", "value": "..." }
    }
  }
}
```

Per-profile remote entries under `profiles[name].headers` use the same shape.
Desktop applies these headers only to matching remote gateway requests, treats
`https` and `wss` as the same gateway origin for WebSocket upgrades, and drops
transport- or Sci-managed header names such as `Authorization`, `Cookie`,
`Host`, `Origin`, `Referer`, and `X-Sci-Session-Token`.

Projects are the workspace abstraction. A project may own multiple folders,
repositories, worktrees, and sessions; a bare new chat remains detached unless
the user enters a project or configures a default project directory. Use the
Projects UI rather than adding a second per-session folder-picker workflow.

Changing profiles or connection modes is a soft workspace switch, not another
cold boot. The shell and current management overlay remain mounted while
gateway-bound nanostores are wiped, query-backed data is invalidated, and the
new connection repopulates skeletons. This prevents rows or transcripts from
the previous gateway bleeding into the next one. Switching changes only the
foreground view and request route: it does not cancel turns or stop a backend,
and retained background sockets continue receiving events from running jobs.

### Verification

Run before opening a PR (lint may surface pre-existing warnings but must exit cleanly):

```bash
npm run fix
npm run typecheck
npm run lint
npm run test:ui
npm run test:desktop:platforms
```

Run `npm run test:desktop:all` for install, boot, update, packaging, or other
release-path changes.

### Troubleshooting

Boot logs land in `SCI_HOME/logs/desktop.log` (includes backend output and recent Python tracebacks) — check it first if the app reports a boot failure.

**macOS / Linux:**

```bash
# Force a clean first-launch setup
rm "$HOME/.sci/sci-agent/.sci-bootstrap-complete"
# Rebuild a broken Python venv
rm -rf "$HOME/.sci/sci-agent/venv"
# Reset a stuck macOS microphone prompt (macOS only)
tccutil reset Microphone com.boltzmannlabs.sci
```

**Windows (PowerShell):**

```powershell
# Force a clean first-launch setup
Remove-Item "$env:LOCALAPPDATA\sci\sci-agent\.sci-bootstrap-complete"
# Rebuild a broken Python venv
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\sci\sci-agent\venv"
```

> The default Sci home on Windows is `%LOCALAPPDATA%\sci`. Set the `SCI_HOME` env var if you've relocated it.

---

## Community

- Support: contact your Boltzmann Labs maintainer; public contact pending.
- [SCI manual](../../README.md)
- Report bugs through the SCI team; repository URL pending.

---

## License

MIT — see [LICENSE](../../LICENSE).

Customized by Boltzmann Labs. Original contributor notices remain in [LICENSE](../../LICENSE).
