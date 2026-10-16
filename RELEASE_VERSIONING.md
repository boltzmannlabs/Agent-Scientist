# Agent Scientist release versions

Public releases use **`v1.M.m.p`**: Major.Milestone.Minor.Patch.

- `1`: fixed major for this product cycle.
- `M`: significant new modules or milestone features.
- `m`: enhancements and improvements within a milestone.
- `p`: fixes and small tweaks.

The initial source release is **`v1.0.0.0`**. Incrementing a component resets
every component to its right. For example, `v1.2.1.3` advances to `v1.2.1.4`
for a fix, `v1.2.2.0` for an enhancement, or `v1.3.0.0` for a milestone.
Keep major at 1 unless explicitly starting a new product cycle.

The CLI, source-install identity, Git tags, Debian packages and provenance
retain the full four-part version. Existing three-part releases remain readable.
Source `pyproject.toml` and npm versions are build placeholders; do not change
dependency locks merely to tag a release. Runtime identity comes from Git or
the verified install stamp.

## Native-package compatibility

Four-part versions are not Semantic Versioning. Electron, Cargo and Tauri use
the ordered internal mapping `1.M.m.p` → `1.(M*1000+m).p`. Thus `1.2.1.3`
packages as `1.2001.3`, while SCI displays `1.2.1.3`. The initial package version
is `1.0.0`. This mapping supports minor values 0–999; advance the milestone
before exceeding that range. Invalid or unsafe numeric fields fail explicitly.
Windows release packages retain their existing timestamp-based native version
sequence, independent of the public version. Update feeds carry the compatible
package version; source tags and artifact provenance retain the SCI identity.

## Cutting a source release

1. Review and test the exact changes to ship, including credential-pattern checks.
2. Commit them on main; a Git tag cannot include uncommitted files.
3. Create an annotated tag on that exact commit:

   ```bash
   git tag -a v1.0.0.0 -m "Agent Scientist v1.0.0.0 — initial source release"
   git push --atomic origin main refs/tags/v1.0.0.0
   ```

Never move or overwrite an already published release tag. Use the next patch
version for corrections. A source tag is not proof of signed native-installer
qualification and does not itself publish a GitHub Release, native update feed,
or binaries. Those remain separately gated by [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).

Install or update source deployments using [INSTALLATION.md](INSTALLATION.md).
