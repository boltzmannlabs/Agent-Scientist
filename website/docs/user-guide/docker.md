---
title: "SCI containers"
description: "Build SCI containers from the reviewed local checkout; no inherited published image."
---

# SCI containers

Container images must contain this customized source. Pulling another product's
image does not install Agent Scientist. Docker is optional for the normal CLI.

## Application container

From the complete SCI checkout:

```bash
docker build -t sci-agent:local .
docker run --rm -it --pull=never \
  -v "$HOME/.sci:/opt/data" sci-agent:local setup
docker run --rm -it --pull=never \
  -v "$HOME/.sci:/opt/data" sci-agent:local
```

The Dockerfile assembles a managed runtime, application dependencies, TUI,
dashboard, and bundled skills. A build needs substantial free disk space and
network access to checksum-verified dependencies. No public SCI image is
configured yet. Keep credentials/state out of the build context and mount only
the intended SCI home; container file ownership must match your deployment.

The checkout's `docker-compose.yml` is a Linux host-network recipe for gateway
and dashboard operation. Review its bind mounts, `SCI_UID`/`SCI_GID`, network
configuration, and service credentials before starting it. The dashboard must
stay on localhost unless you configure authentication and a secure proxy.

## Scientific terminal sandbox

The application container and the terminal sandbox are different images. For
Docker-based terminal execution, build the sandbox recipe explicitly:

```bash
docker build -f docker/sandbox-desktop.Dockerfile \
  -t agent-scientist-sandbox:desktop .
```

Then select it in your active profile's configuration:

```yaml
terminal:
  backend: docker
  docker_image: agent-scientist-sandbox:desktop
```

SCI will not silently pull an invented public image when this local tag is
missing. A recipe supplies base utilities, not every scientific model, dataset,
or experimental software requirement. Verify those separately.

Modal and Daytona require your own compatible published registry image.
Singularity/Apptainer may use an approved registry image or a prepared local
SIF. The local Docker tag is not a remote registry destination. Existing
explicit image choices are preserved; do not change a running research
environment without reviewing its mounts, persistence, and dependencies.

## Release verification

A successful source or build-context check is not a full image qualification.
Run the actual Docker integration suite against the newly built SCI image before
shipping it. Native desktop installers are separate build products. See the
checkout's `INSTALLATION.md`, `CONTRIBUTING.md`, and `SCI_MIGRATION.md` for current
instructions and verification limits.
