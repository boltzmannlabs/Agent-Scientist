"""A local source-built sandbox must never become an invented registry pull."""

import subprocess

import pytest

from sci_cli.config_defaults import DEFAULT_SANDBOX_IMAGE
from tools.environments.base import EnvironmentConnectionError


def test_source_image_rejected_before_remote_probes():
    from tools.environments.daytona import DaytonaEnvironment
    from tools.environments.modal import ModalEnvironment
    from tools.environments.singularity import SingularityEnvironment

    for environment, image in (
        (ModalEnvironment, DEFAULT_SANDBOX_IMAGE),
        (DaytonaEnvironment, DEFAULT_SANDBOX_IMAGE),
        (SingularityEnvironment, f"docker://{DEFAULT_SANDBOX_IMAGE}"),
    ):
        with pytest.raises(EnvironmentConnectionError, match="No image was pulled"):
            environment(image)
    from tools.environments.remote_common import require_published_sandbox_image
    require_published_sandbox_image("registry.example.org/team/sandbox@sha256:fixture", "modal")


def test_docker_missing_source_image_never_pulls_or_runs(monkeypatch):
    from tools.environments import docker

    calls = []
    monkeypatch.setattr(docker, "_ensure_docker_available", lambda: None)
    monkeypatch.setattr(docker, "find_docker", lambda: "docker")

    def inspect(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 1, "", "not found")

    monkeypatch.setattr(docker, "run_capture", inspect)
    with pytest.raises(EnvironmentConnectionError, match="docker build"):
        docker.DockerEnvironment(DEFAULT_SANDBOX_IMAGE)
    assert len(calls) == 1 and calls[0][1:3] == ["image", "inspect"]
    environment = object.__new__(docker.DockerEnvironment)
    environment._docker_exe = "docker"
    environment._image = DEFAULT_SANDBOX_IMAGE
    assert not environment._image_available_locally()
    assert all(command[1:3] == ["image", "inspect"] for command in calls)
