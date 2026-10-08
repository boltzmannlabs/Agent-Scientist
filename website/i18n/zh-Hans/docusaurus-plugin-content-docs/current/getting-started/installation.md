---
sidebar_position: 2
---

<!-- Updated SCI source instructions; localized review pending. -->

# Install Agent Scientist

SCI is built by Boltzmann Labs. Obtain the approved source checkout from your team;
a public repository, signed installers and update channels are not published yet.
Do not install another product's release expecting SCI customizations.

## Linux source installation

From the approved checkout, using your normal user account:

```bash
bash ./setup-sci.sh
export PATH="$HOME/.local/bin:$PATH"
sci setup
sci doctor
agent-sci
```

Setup downloads pinned dependencies and verifies their hashes. No external backup
artifact mirror is configured; an unavailable primary download fails visibly.
Keep this checkout in place. Do not copy another person's state directory or keys.

## Model and service credentials

Use `sci setup` or `sci model` for your selected model provider. No hosted-product
login is required by SCI. Tools may require their own credentials. Authorize
Boltzmann using `/Add_boltz` and its masked key prompt; never paste keys in chat.

## State and verification

The launcher is `agent-sci`; the administration command is `sci`.
State defaults to `~/.sci`; an explicit `SCI_HOME` selects a different home.
Confirm `sci --help`, `sci doctor`, then a short conversation. Scientific workflows
need separate tool/environment checks; installed instructions do not install software.

## Other platforms and updates

Windows source setup uses the checkout's `setup-sci.ps1` and local instructions.
Native Windows/macOS packages, Nix and Termux distribution are not release-certified.
No public download, signing identity, package repository or update feed is promised.
Automatic publication and self-update remain blocked until SCI endpoints are verified.
Use the supplied `README.md`, `SECURITY.md` and `SCI_MIGRATION.md` for current status.
