"""Fresh Git history must ship runtime inputs without committing private state."""

from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def _stage_fixture(tmp_path, relative_paths):
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    subprocess.run(["git", "init", "-q", str(checkout)], check=True)
    shutil.copyfile(ROOT / ".gitignore", checkout / ".gitignore")
    website = checkout / "website"
    website.mkdir()
    shutil.copyfile(ROOT / "website" / ".gitignore", website / ".gitignore")
    for relative in relative_paths:
        path = checkout / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("reviewed fixture\n")
    subprocess.run(["git", "-C", str(checkout), "add", "."], check=True)
    result = subprocess.run(
        ["git", "-C", str(checkout), "ls-files", "-z"],
        check=True, capture_output=True, text=True,
    )
    return set(result.stdout.split("\0")) - {""}


def test_fresh_history_includes_authored_runtime_and_skill_inputs(tmp_path):
    required = {
        "examples/mcp/client-metadata.json.example",
        "skills/science/example/examples/invocation.md",
        "optional-skills/creative/example/examples/workflow.md",
        "skills/science/example/references/data.md",
        "apps/desktop/electron/get-windows.d.ts",
        "website/src/data/userStories.json",
        "apps/ui/lib/ui/components/button.js",
        "apps/ui/lib/fonts/Mondwest-Regular.woff2",
        "third_party/misaki/misaki/data/us_gold.json",
    }
    assert required <= _stage_fixture(tmp_path, required)


def test_fresh_history_excludes_secrets_research_and_generated_outputs(tmp_path):
    private = {
        ".env", ".env.backup", ".sci/config.yaml", ".hermes/auth.json",
        "credentials/api_key",
        "profiles/project/auth.json", "state.db", "state.db-wal",
        "science-library/private.fasta", "artifacts/analysis.csv",
        "outputs/project/candidate.pdb",
        "examples/private-request.txt", "examples/mcp/private-token.json",
        "node_modules/package/index.js", "apps/ui/node_modules/private/index.js",
        "apps/desktop/dist/index.html", "sci_cli/web_dist/index.html",
        "web/public/fonts/generated.woff2", "website/src/data/skills.json",
        "key.pem", "ref_imgs/image.png",
    }
    staged = _stage_fixture(tmp_path, private | {".env.example", "install-sci.sh"})
    assert not (private & staged)
    assert {".env.example", "install-sci.sh"} <= staged
