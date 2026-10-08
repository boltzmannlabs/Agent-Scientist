# SCI branding review

This is a classification and cleanup record, not public-release approval.
`BRANDING_INVENTORY.json` lists every matched working-tree text file and line,
with categories produced by `scripts/audit_branding.py`. Categories containing
`review` are outstanding review queues, **not approved exceptions**. A file may
belong to several categories. Do not delete a file just because it matches.

## Policy

- SCI product identity: Agent Scientist / SCI, built by Boltzmann Labs.
  Launcher: `agent-sci`; administration: `sci`; state: `.sci`.
- Preserve real third-party package/model/plugin identifiers, author credits,
  licenses, provenance, historical issue references and attack signatures.
- Preserve migration recognition of old names: deleting those strings can stop
  an old auto-generated persona from upgrading correctly.
- No fabricated SCI repository, download service, OAuth identity or installer.
  Missing publication destinations stay unset and publication stays blocked.
- No live user-state changes or prompt/toolset reloads for this cleanup.

## Completed in this pass

- Disabled the inherited backup binary mirror in `pm/artifact-mirror.json`.
  PM and generated shell/PowerShell bootstrap pins now support an absent mirror.
  Primary pinned downloads and SHA256 checks remain; a primary outage fails
  without silently contacting another publisher. Explicit mirror fixtures still
  pass the existing recovery tests. A future mirror requires approved hosting.
- Disabled website prebuild's inherited skill-index fetch and default remote
  plugin-star cache. Bundled catalogs/offline data remain available. Explicit
  GitHub star probes remain an opt-in developer operation.
- Corrected the LLM documentation generator, model-catalog documentation URL,
  skill-reference generator and bundled-skill install metadata. Generated
  documentation no longer invents an upstream install target for SCI's local
  skills. Optional skills keep their working `official/...` identifier.
- Regenerated the 243 bundled/optional skill documentation pages and catalogs.
  This legitimately propagates contributor credits into generated pages; raw
  match counts can increase even as incorrect destinations are removed.
- Rewrote or retired 24 inherited installation, update and hosted-service setup
  pages; repaired source-checkout links in 83 documents. Updated dashboard
  guidance to direct SCI deployments to their own configured authentication.
  Updated Chinese pages that were retired carry an explicit localized-review
  notice; this is not a claim of complete translation/localization acceptance.
- Removed inherited subscription recommendations from the primary provider,
  browser, web-search, TTS and tools guides. Corrected remaining FAQ/developer
  installation examples and the optional-model-catalog instructions. Retired
  the expired free-model promotion and misleading renamed hosted-cloud guide.
- Unconfigured managed Telegram pairing now stops before network access, with
  manual BotFather guidance. Explicitly configured service endpoints and ordinary
  Telegram bot-token setup are preserved. No new credentials were requested.
- Corrected the desktop-inspection skill's stale environment-variable name and
  the Skills Hub's bundled-catalog label.
- Removed 326 inherited testimonials from SCI's website dataset, rather than
  attributing other products' users to SCI. The case-study page now shows an
  honest empty state. A recoverable copy is outside the repo at
  `/home/boltzmann20/sci-removed-branding-1V35xY/website-userStories.json`.
- Added the source installer `install-sci.sh` and `INSTALLATION.md`; ordinary
  users no longer need the developer/test setup path. The real installer
  walkthrough covers quoted paths, dependency/hash failures, reruns, and
  supporting skill files. Fixed launcher ownership so a reinstall recognizes
  its own `agent-sci` wrapper.
- Replaced the publisher UI dependency with the local `@sci/ui` workspace.
  Retained its original MIT license; production web, desktop and bootstrap
  builds passed. Replaced the speech fork with official Misaki 0.9.4 source,
  recorded its source hash/license, and staged local dependencies through PM.
- The sandbox default is now the local `agent-scientist-sandbox:desktop`
  recipe. Missing builds fail with instructions instead of pulling an invented
  SCI image; remote backends require an approved registry image/local SIF.
  Fixed Docker build-context omissions and the renamed SQLite qualification
  probe. A real minimal Docker context build passed; full images remain untested.
- Removed inherited installer/CDN recommendations from primary and localized
  entry pages, retired hosted-subscription recipes, and corrected CLI/plugin
  help destinations. The inherited reference corpus remains under review.
- Removed the inherited MCP hosted OAuth identity default. DCR and existing
  registered clients remain; CIMD requires an explicit approved document URL.
  Its unpublished template lives in `examples/mcp/`, not a public static URL.
  Real MCP OAuth regressions and A→B→A multiplexed identity checks passed.
- Archived 22 unused UI screenshots/experiments outside the repository at
  `/home/boltzmann20/sci-release-extras-5mj8M9/`. Scientific research files,
  live credentials, sessions and profiles were not removed.
- Updated the remaining vulnerable production JavaScript dependencies through
  the lockfile. `npm audit --omit=dev` reports zero known findings.

## Intentional retained identities

| Identity | Why it must not be blindly renamed |
| --- | --- |
| LICENSE, contributor records, skill authors, plugin provenance | Credit and origin are not SCI product branding. |
| `hermes-parser`, `hermes-estree`, external plugin repositories and model IDs | These are real packages/products; changing the name does not create a replacement. |
| UI/speech source notices | Local replacements retain original licenses and source provenance; they are not newly authored implementations. |
| `hermes-0day` and published security advisories | Detection and incident references must retain the observed identifiers. |
| Old namespace/persona strings in migration code | Recognition inputs, not the new product identity. |
| Tests and historical issue/commit references | Keep evidence; adjust fixtures when a contract intentionally changes. |
| Nous provider/auth/billing compatibility code | A real optional vendor integration, not Boltzmann's service. Do not rename vendor charges, tokens or OAuth identifiers to SCI. First-run removal does not imply this code was removed. |

## Outstanding decisions and verification

1. **Sandbox images:** local source/configuration guards are verified, but a full
   SCI application/sandbox image build and real supported-backend qualification
   remain. No public registry URL or successfully built full image was invented.
2. **Speech:** official source and PM staging are verified; full voice/G2P
   acceptance on every supported Python/platform combination remains.
3. **Documentation:** the inventory still flags legacy service instructions and
   other untranslated references for review. Do not publish the full legacy
   website as an approved SCI manual yet. `README.md` and `INSTALLATION.md`
   are authoritative for source setup.
4. **Optional vendor removal:** deleting retained authentication/provider modules
   requires a separate dependency/call-path removal, not renaming them to SCI.
   Review the inventory's runtime/service queues before claiming independence.
5. **Release:** the Git repository is now approved; security contact,
   hosting/signing and native-platform acceptance remain missing. The production npm findings have
   been resolved; broader Python/Rust dependency and licensing/security reviews
   are not established by this cleanup or a narrow credential-pattern scan.
6. **Private old history:** the owner approved fresh public history with the old
   metadata retained in a protected backup outside the repo. Two historical
   non-test credential-shaped literals still require review in that backup.
   Values were not exposed or authenticated, and the old objects are not included
   in the new repository. See `SECURITY_SCAN_REVIEW.md`.

To inspect current references without changing files:

```bash
python scripts/audit_branding.py
```

The inventory excludes itself, ignored local research/state and binary contents.
It does not certify Git history, scan images or prove the scientific correctness
of tools. See `SCI_MIGRATION.md` for verification receipts and earlier asset removal.
