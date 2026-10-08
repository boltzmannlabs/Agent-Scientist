#!/usr/bin/env bash
# Install Agent Scientist from this source checkout using its managed runtime.
set -Eeuo pipefail

setup=true
stage="checking prerequisites"
trap 'status=$?; printf "\nInstallation stopped during %s (exit %s). See the error above.\n" "$stage" "$status" >&2; exit "$status"' ERR
trap 'printf "\nInstallation cancelled during %s. Existing SCI data remains available.\n" "$stage" >&2; exit 130' INT TERM

usage() {
    printf '%s\n' \
        'Usage: bash install-sci.sh [--non-interactive] [--help]' \
        '' \
        'Installs the managed Python/Node/tools, application dependencies, SCI launchers' \
        'and bundled skills. Interactive mode then opens model/provider setup.' \
        '--non-interactive installs the software without asking for credentials.'
}
for option in "$@"; do
    case "$option" in
        --non-interactive|--no-setup) setup=false ;;
        --help|-h) usage; exit 0 ;;
        *) printf 'Unknown option: %s\n' "$option" >&2; usage >&2; exit 2 ;;
    esac
done

source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
case "$(uname -s)" in
    Linux|Darwin) ;;
    *) printf 'Use setup-sci.ps1 for native Windows. This installer supports Linux and macOS.\n' >&2; exit 1 ;;
esac
for tool in curl tar awk; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        printf 'Missing prerequisite: %s. Install it using your operating system package manager, then retry.\n' "$tool" >&2
        exit 1
    fi
done
if ! command -v sha256sum >/dev/null 2>&1 && ! command -v shasum >/dev/null 2>&1; then
    printf 'Missing SHA256 verifier: install sha256sum or shasum, then retry.\n' >&2
    exit 1
fi
for file in setup-sci.sh pyproject.toml uv.lock pm/lock.json; do
    if [ ! -f "$source_dir/$file" ]; then
        printf 'Incomplete SCI checkout: %s is missing. Obtain the complete repository and retry.\n' "$file" >&2
        exit 1
    fi
done
if [ "$setup" = true ] && { [ ! -t 0 ] || [ ! -t 1 ]; }; then
    printf 'No interactive terminal detected; installing software without credential setup.\n'
    setup=false
fi

printf 'Agent Scientist installation\nSource: %s\n' "$source_dir"
stage="installing runtime and dependencies"
bash "$source_dir/setup-sci.sh" --user-install

stage="checking the installed CLI"
installed_cli="$source_dir/.sci/bin/sci"
"$installed_cli" --help >/dev/null

if [ "$setup" = true ]; then
    stage="configuring your model provider"
    "$installed_cli" setup
else
    printf '\nSoftware installed. Configure your model before chatting: sci setup\n'
fi

printf '\nAgent Scientist is installed.\n'
printf 'Start: agent-sci\n'
printf 'If the command is not found, open a new terminal or run:\n  export PATH="$HOME/.local/bin:$PATH"\n'
printf 'Keep this source checkout at: %s\n' "$source_dir"
printf 'Optional service credentials are configured separately inside SCI.\n'
