# SCI source handoff and release checklist

## Source installation

From a complete checkout, as your normal user:

```bash
bash ./install-sci.sh
```

For an unattended server, use `--non-interactive`, then run `sci setup`
interactively and start `agent-sci`. See [INSTALLATION.md](INSTALLATION.md)
for prerequisites, Windows, optional web/desktop builds, credentials and recovery.
The installer prepares the core CLI; it does not supply model/service credits,
scientific datasets, arbitrary software, or signed native packages.

## Completed source checks

- Source installer walkthrough: real PM/dependency assembly, rerun, quoted paths,
  skill/reference preservation, hash and missing-dependency failures.
- Existing launcher ownership, missing sandbox behavior, local dependency staging.
- MCP OAuth: no inherited hosted identity, explicit CIMD, registered-client/DCR
  preservation, real SDK/loopback regressions, A→B→A multiplexed profile isolation.
- Web: 360 tests and production build; desktop production build/typecheck;
  bootstrap frontend production build/typecheck; local UI/security contracts.
- Documentation generators, CI classification and hand-authored link-style lint.
- Production JavaScript dependency audit: zero known findings.
- Docker build-context availability and the actual SQLite qualification SQL.
  Full application/sandbox image builds were not performed on this low-disk host.
- Working-tree credential-pattern and case-collision checks. These do not certify
  absence of secrets or scientific correctness; test fixtures intentionally
  contain synthetic credentials.
- Fresh-home/profile distribution checks: 71 tests passed across six files,
  including enabled/disabled skill defaults and isolated-profile execution.

Detailed receipts and limitations: [SCI_MIGRATION.md](SCI_MIGRATION.md).
Branding classifications: [BRANDING_REVIEW.md](BRANDING_REVIEW.md).
Remaining third-party names include real providers/packages, licenses,
contributors, security signatures and history. Do not falsify them.

## Git handoff

Approved repository: `https://github.com/boltzmannlabs/Agent-Scientist.git`.
With the owner's approval, the old Git metadata was copied and byte-compared
into a permission-restricted private backup on the separate storage drive.
The checkout was then initialized with fresh history on `main`, with only the
approved repository configured as `origin`. The initial source commit does not
include inherited branches, tags or historical objects. Push remains a separate
explicit action; initializing and committing locally does not publish source.
Ignored runtime state, dependencies, builds and research folders are not release
source. Review the actual proposed staged diff before publishing.

The two historical API-key-shaped literals remain only in the private old-history
backup, not in the new public commit ancestry. Never import or push that backup.
Staged source received a limited credential-pattern, private-path, file-size
and case-collision review; recheck after any later changes. See the redacted
findings and scan limits in
[SECURITY_SCAN_REVIEW.md](SECURITY_SCAN_REVIEW.md).

## Before public release

- Supply the private security-reporting contact; the SCI repository is approved.
- Configure and verify SCI-owned release/update/install/support destinations.
  Keep native/publication guards until then. CLI Git updates now use the
  approved SCI origin and `main`, without a promoted release service.
- Push the reviewed source-update implementation before recommending it to
  users. The former passive-check failures included unset repository identity
  and tests assuming the old publisher; see the latest migration receipt for
  the rerun. Source delivery is not signed native release qualification.
- If needed, publish and validate an approved MCP CIMD identity document.
- Run full Docker image/backends and optional speech acceptance.
- Run real Windows/macOS native installers, signing, upgrade and recovery tests.
  A Linux Electron build is not native-platform or signing certification.
- Complete scientific workflow trials with approved fixtures and authorized
  services. Live model/research-service execution was not part of this cleanup.
- Review licensing and dependency security beyond the production npm audit.
  Credential-pattern scans are only one input to a public-source security review.

The source is prepared for installation and Git review. This checklist does not
declare a signed/public release ready or claim the entire test suite passed.
