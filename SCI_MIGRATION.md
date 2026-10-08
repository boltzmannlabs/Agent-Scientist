# SCI namespace migration

The public launcher is `agent-sci` (`agent-scientist` is retained locally as an
alias). Internal commands use `sci`; ACP uses `sci-acp`. Application modules,
classes, environment prefixes, toolset identifiers, owned plugin paths, slash
commands and default state directories now use SCI. The title artwork and theme
are unchanged.

## Existing installations

This is an offline migration, not a live conversation reload. Stop writers,
verify a source backup, rehearse the code, and migrate into a **new** home. The
one-time scripts refuse existing destinations and source edits made since
rehearsal. Do not run them again against an already migrated home.

- `scripts/sci_namespace_migration.py`: source rehearsal and path/hash inventory.
- `scripts/sci_home_migration.py`: separate home copy; preserves credentials and
  conversation payloads; rebases operational paths and valid profile approvals.
- `scripts/sci_apply_stage.py`: apply a reviewed stage with an existing source backup.

Use PM to rebuild dependency generations and publish launchers after relocation.
Do not transplant an old managed dependency generation as the active runtime.
Old homes and source archives are recovery material; they are deliberately not
deleted by these scripts. A rollback restores the original source, home path,
launchers and service together, with all writers stopped.

Unmatched science-profile review hashes remain unmatched: migration must not
silently grant permissions. Review those projects before isolated execution.
Boltzmann grants are transferred only when the old receipt matches the same
profile's saved key. A key without a valid receipt stays locked.

## External contracts

Legal notices, original authorship, real third-party URLs/repository identities,
published model identifiers and registered OAuth client IDs are not renamed.
Published dependency names such as `hermes-parser` and `hermes-estree` also
retain their real registry names; they are not application-owned modules.
Renaming them would falsify attribution or address a nonexistent service. The
external plugin version-requirement field is still understood, without relaxing
its gate. New plugin manifests use `requires_sci`. Plugins importing private old
Python module paths must be ported; no old-module import shims are installed.
Historical conversation contents and recovery backups can contain old wording.

New wake-word defaults use “Hey Sci”, with “Hey Agent Scientist” and
“Hey Agent-Sci” as aliases for the same profile, and select the existing sherpa
open-vocabulary engine, which tokenizes that phrase for detection. This needs
the optional PM dependencies and a one-time English model download on enabling.
Listening remains opt-in. Explicit engine/phrase settings are preserved. The
renamed bundled `.tflite` still detects its original phrase, not “Hey Sci”; an
attempt to pair it with a different phrase fails with a configuration remedy.

## Publishing

`sci-unpublished-distribution` blocks self-update admission and source release
resolution. Keep it until SCI-compatible releases and endpoints have been
configured and tested. Do not point the fork at upstream release installers.
The Git push destination must be the project's own repository, not upstream.

Linux source/launcher/profile/plugin paths are covered by targeted tests using
`scripts/run_tests.sh`, including temporary A→B→A homes and controlled startup.
This does not establish Windows/macOS packaging, live provider calls, or the
scientific correctness of tools.

## Verification receipt — 2026-10-07

This audit did not modify old `.hermes` profiles or conversation histories,
publish a release, or change the Git remote. Targeted checks are not a claim
that the entire test suite or every external integration has been verified.

- Python: 564 distinct tests passed across 40 files using `scripts/run_tests.sh`;
  7 native-platform tests skipped on Linux. Includes fresh profile creation and
  actual child-worker requests against a loopback model fixture, A→B→A isolation,
  byte-stable prompts, shared-auth fallback tests, plugin admission, and real
  MCP handshake/discovery without business-tool execution.
- TUI: 1,610 tests passed across 175 files; production bundle built.
- Web: 359 tests passed across 50 files; typecheck and production build passed.
- Namespace/package-lock contracts: 2 JavaScript tests passed. Corrected an
  installed Ink workspace symlink and restored genuine third-party npm identities.
- Application-owned, non-ignored filenames: no remaining `hermes` matches.
  Recovery archives, historical content, legal notices and external identities
  are intentionally outside that claim.
- Wake aliases: configuration tests passed; a real sherpa detector triggered on
  locally generated neural speech for “Hey sigh”, “Hey Agent Scientist” and
  “Hey Agent Sci”. Two unrelated phrases did not trigger. Earlier robotic eSpeak
  samples did not trigger; spelling “Sci” in a speech synthesizer is not a reliable
  pronunciation specification. These small fixture checks do not establish
  microphone/accent accuracy or a false-positive rate. Listening stays disabled
  by default; optional dependencies are admitted only when enabling it.

### Still unverified or intentionally deferred

- Desktop tests could not collect with this checkout's partial installed JS
  dependencies (`@rolldown/plugin-babel` missing in the desktop workspace).
  Full locked dependency preparation and Electron packaging remain to be run.
  Only about 3.6 GiB was free during this audit; no shared dependency tree was
  replaced or user data removed to make room.
- Native Windows/macOS launchers, installers, services and packaging need their
  own operating-system runs. Linux tests cannot establish those results.
- Live provider calls, real microphone recognition and production research
  services were not exercised. MCP checks used a local fixture server.
- Third-party plugins importing old private Python modules need SCI-compatible
  releases. The loader now gives an actionable error instead of suggesting that
  installing the old agent would fix them. No compatibility shims are added.
- GitHub repository selection, release/install endpoints, publication and updater
  enablement are deferred as requested. The unpublished-distribution guard remains.

## Local SCI help correction — 2026-10-07

The earlier namespace pass preserved real upstream URLs, but that was insufficient
for application self-help: the system prompt and operating-manual skill still
treated upstream documentation as authoritative for SCI. This caused a capability
greeting to load a skill and fetch an unrelated product's documentation.

The runtime help guidance now gives greetings and broad capability introductions
an explicit no-tools exception. Detailed SCI help uses local instructions and
implementation, without an upstream documentation fallback. Both help variants
(with and without skill tools), default persona seeds, the repository SOUL files,
and CLI attribution now identify Boltzmann Labs. The installed main home's
operating manual was updated too, preserving unrelated local reference changes.
Existing profile SOUL files and active conversations were not rewritten.

`README.md` is now the SCI setup and user guide. The dashboard renders its bundled
copy instead of a remote iframe. CLI setup/recovery documentation hints now direct
users to the local checkout. Default Python-side model/plugin/skills catalog
lookups no longer contact the upstream docs service; shipped catalogs and
independent registries remain available, and cached plugin security removals are
retained. Optional skills no longer silently fall back to the upstream source repo.

This is a prompt/operating-manual correction, not a network firewall or a claim
that every model response is deterministic. Restart the CLI without resuming an
old conversation to test the changed system instructions. No live model request
was used for verification; fresh worker tests used a controlled loopback provider.

The release pass below supersedes the earlier desktop dependency and self-help
limitations. It does not supersede the native-platform verification boundary.

## Release cleanup receipt — 2026-10-07

Status: **not approved for public release yet**. No push, publication, Git remote
change, or rewrite of old profiles/sessions was performed.

### Completed

- Desktop help now uses the bundled SCI README. Desktop catalogs and the bot
  skills picker use the selected backend/profile instead of upstream website
  downloads. Catalog caches and idle prefetches preserve connection/profile
  ownership, including A→B→A changes.
- Desktop/installer application identities use Boltzmann Labs. Inherited mascot
  SVGs were removed and replaced with intentionally empty SCI marks as requested;
  native icon frames keep valid platform geometry but have no mascot. Original
  artwork remains recoverable from Git. The CLI title, theme and status bar were
  not redesigned. No user data was deleted.
- Desktop and native bootstrap source URLs no longer default to upstream.
  Source installers require an explicit reviewed source. Unpublished release,
  updater, Store packaging and publishing paths fail closed. CI publication
  requires explicit SCI release admission. No SCI repository, certificate or
  security contact was invented.
- Diagnostic support uploads require a configured destination rather than
  silently using an upstream endpoint. CLI and RPC wording now use `support`.
  Local reports remain available; redaction is not described as infallible.
- The canonical README, translated entry READMEs, contribution/security guidance,
  desktop recovery/help, dashboard attribution and legacy-site navigation were
  corrected. The legacy site warns that its reference pages are under review;
  it is not the published SCI manual. Required legal notices and actual
  third-party package/provider identities are preserved.
- Updated pinned vulnerable JavaScript dependencies and regenerated the lockfile.
  The simple-git v4 API import was corrected and real local Git regressions passed.
  Narrow, documented security exceptions retain the npm age quarantine elsewhere.
  Bundled README edits now invalidate web/desktop build receipts.

### Verification

The release checks used `scripts/run_tests.sh` for Python. JavaScript dependency
preparation used the canonical locked builder in an isolated source copy; the
checkout's partial installed dependency tree was not replaced. No production
research service or live model request was needed.

- Python release groups: 647 passing targeted tests covering installers,
  additions/profiles, configuration/packaging, providers and release scripts;
  subsequent diagnostics (69), identity/plugin-extension (198), and
  plugin/doctor/release checks (301) also passed. Groups can overlap and are not
  an aggregate full-suite count. Native-only tests were skipped on Linux.
- Icon-generator error/empty-mark tests: 22 passed. Generated PNG/ICO/ICNS/SVG
  format, dimensions and frame checks passed. The separate fresh-environment
  icon-flavor acceptance file timed out during PM preparation and remains
  unverified. An initial parallel test invocation incorrectly shared a pytest
  basetemp; the isolated icon-generator rerun passed without that collision.
- TUI: 1,610 tests across 175 files passed in the earlier verification.
- Web: 360 tests across 51 files, typechecked production build and bundled
  manual rendering passed against the updated lockfile. Installer frontend
  typecheck and production build passed; desktop typechecks passed too.
- Desktop production compilation and final emitted-chunk validation passed with
  the updated dependencies and blank artwork. The build-freshness receipt is
  current. This is an unsigned Linux validation build, not a native installer
  or a signed release artifact.
- Desktop cleanup: 166 tests across 21 files passed; the post-dependency-change
  Git/sanitization/math/manual/catalog/diagnostics subset passed 92 tests across
  11 files. These are targeted checks, not the full desktop suite.
- Build freshness, namespace lock and publication admission: 13 JavaScript tests
  passed. The manual freshness test exercises actual web builds.
- Production dependency audit for desktop/shared/bootstrap workspaces: zero
  critical, high or moderate entries; eight low entries remain in the KaTeX
  dependency chain. This is not a Python/Rust audit or proof of exploitability.
  See [KaTeX advisory](https://github.com/advisories/GHSA-238p-pmpm-9mq7).
  Resolving it requires a separately verified rendering-dependency upgrade;
  no blanket forced audit fix was applied.
- Working-tree high-confidence secret scan: no findings in 20,222 scanned
  files and no flagged sensitive filenames. Git history was not audited.

### Remaining release gates

1. Supply the approved SCI repository and private security-reporting contact;
   configure SCI-owned release/install/update endpoints and signing identities.
   Keep `sci-unpublished-distribution` and CI publication guards until verified.
2. Run real Windows/macOS native installer, signing and upgrade tests. Rust/Tauri
   compilation was not verified here. Linux's optional HUD helper also needs
   X11/Xi development headers before its native build can be verified.
3. Finish review/remediation of the KaTeX audit finding and re-run the independent
   icon-flavor acceptance file with a successfully prepared environment.
4. Port or explicitly retire the full legacy website/reference corpus before
   publishing it as SCI documentation. The local SCI README is the current guide;
   a corrected navbar is not a certification of every legacy page.
5. Complete Git-history secret/licensing review and fresh-install acceptance on
   the actual release checkout. Validation copies use a placeholder commit stamp,
   so their bundles are not distributable release artifacts. Live provider/service
   acceptance and scientific correctness still need the science team's trials.

## Skill distribution receipt — 2026-10-08

- Added the 33 previously local-only skill bundles to `skills/`: 362 files,
  including 92 Python helper files. The bundled catalog now contains 91 skills.
  Supporting references, templates, examples, source revisions and upstream
  notices are included; personal installation/history metadata is not.
- Replaced personal scientific-interpreter paths with prerequisite checks and
  portable placeholders. Recorded package versions describe prior validation,
  not software installed by cloning this repository. Preserved Linux gating.
- Standardized the local entrypoints, removed a dangling image-reference link,
  and replaced the bioinformatics gateway's bulk package-install shortcut with
  explicit environment review and approval. The external gateway index is not
  a claim that its hundreds of referenced skills are already installed.
- Packaged the 19 disabled selections in `cli-config.yaml.example` and the
  template-free first-save policy (`sci_cli/config_skill_defaults.py`). They
  are not runtime merge defaults. Existing configuration choices, including
  explicit empty lists and per-platform choices, remain authoritative.
- Exempted shipped export helpers/references from the broad `export*` Git ignore
  rule so a fresh archive does not silently omit them.
- Verification: 1,783 passing targeted tests across nine files, using
  `scripts/run_tests.sh`: authoring standards; real archive-to-home resource
  preservation; actual enabled-skill discovery; template/fallback/first-save
  seeding; existing config preservation; A→B→A homes under multiplex scope;
  existing sync, filtering, config loading and save-integrity regressions.
  Ruff and the atomic-config-writer check passed.
- The community-pattern scanner returned 32 safe and one caution verdict for
  the new bundles, with no dangerous verdict. The remaining caution is the
  resource inspector's intentional Linux `/proc/self/cgroup` read. This scan
  does not establish scientific validity or replace a licensing review.
- The live user's configuration was unchanged (checksum verified). No credentials,
  sessions, private profiles, scientific environments or service authorization
  were copied. No scientific jobs, network services, or imported scripts were
  executed for this verification. No commit or push was performed.

These checks validate packaging and selection, not every scientific workflow or
native installer. The earlier release gates remain in force. Fresh users receive
these defaults only from a release containing these changes; existing installs
keep their own selections. The policy remains a disabled list, not an allowlist.

## Git upstream disconnection — 2026-10-08

At the user's explicit choice, local Git history was kept. Removed the inherited
`origin`, its tracking configuration/references, the stale VS Code merge-base
setting, and cached `FETCH_HEAD`. HEAD remains `f42f579cf8`; working files,
local commits, tags and pre-existing edits were not reset. `git remote -v` is empty.

Removed inherited destinations from GitHub workflows, issue/PR templates and the
plugin-validation action. Release CI now requires explicit SCI publisher settings;
plugin validation needs an explicit SCI repository, and installer acceptance needs
SCI installer URLs. Runtime Git/ZIP release lookup, banner release links and release
notes no longer default to the inherited publisher. Unconfigured lookups fail
without contacting that publisher or adding a remote. The unpublished-distribution
marker remains; no new remote, commit, tag, push or publication was created.

Verification: 59 targeted Python tests passed through `scripts/run_tests.sh`,
including real temporary Git repositories and controlled release-resolution HTTP
fixtures; two JavaScript publication/CI checks passed. All 52 workflow YAML files
parsed. Targeted Ruff and diff whitespace checks passed. No inherited project
destination remains in `.github/` or this checkout's local Git configuration.

This is not a claim that every upstream reference across the tree was erased.
Historical commit messages and required attribution/license notices remain by
design. Legacy documentation still needs its previously recorded porting review.
Dependency sources such as the pinned speech-package fork and
`pm/artifact-mirror.json` (also reflected in generated installer pins) remain;
these are dependency supply-chain references, not a Git remote, and replacing
them requires validating compatible package sources rather than deleting URLs.
The approved SCI GitHub URL, release endpoints and security contact are still
needed before publishing or enabling update channels.

## Final-pass branding and release audit — 2026-10-08

**Verdict: not approved for a public push or release.** The cleanup below is
verified, but this checkout is not free of inherited references and the release
gates above remain open. No commit, push, publication, or history rewrite was made.

### Artwork and immediate corrections

- Visually inspected 91 non-research raster/icon assets using contact sheets,
  including the TIFF installer background. Renamed files were not assumed to
  contain new branding: both banner PNGs still said HERMES-AGENT, and the
  `sci.png`/sprite/frame files still contained the inherited mascot.
- Removed 41 files from the working tree: two banners, the old DMG background,
  ten mascot sprite/frame images, 25 dashboard/model/kanban screenshots, two
  achievements screenshots, and one desktop PR screenshot.
- These were moved, not destroyed. Recoverable originals and a path manifest
  are outside the repo at `/home/boltzmann20/sci-removed-branding-1V35xY/`.
  No live user profiles or conversations were touched. Old commits still contain
  historical assets because history retention was explicitly requested.
- The DMG now uses a plain white background. Removed the website social-preview
  banner configuration and documentation references to retired screenshots.
  Existing blank app-icon tiles and transparent wordmarks remain. Corrected the
  icon generator's stale artwork description without changing its rendering.
- Corrected achievements share-card/footer branding and removed its hardcoded
  upstream social promotion, preserving the author's MIT attribution.
- Matched the Spanish security policy to the English pending-SCI-contact policy.
  Repair/error guidance now refers to the local SCI documentation instead of the
  inherited website. Updated incidental example URLs and speech vocabulary.
- Added Git exclusions for untracked local `artifacts/`, `science-library/`
  staging, and four root reference PNGs (including watermarked stock imagery).
  Nothing in those locations was deleted. Approved bundled skills remain under
  `skills/`; Git ignore rules do not remove already tracked files or old commits.

### Remaining references are not all equivalent

The final candidate-tree scan covered **17,272 existing tracked/untracked,
non-ignored regular files**. **1,399 text files** matched the case-insensitive
pattern `hermes|nous[ -]?research`. This is a discovery count, not a count of bugs
or a claim that each match was individually adjudicated.

Examples requiring further review before claiming independence:

| Area | Current evidence / required decision |
| --- | --- |
| User documentation | 272 website files match; legacy provider/setup guidance remains. Port or explicitly retire that corpus. The remaining TUI demo MP4 was not frame-audited. |
| Dependency distribution | `pm/artifact-mirror.json` still uses the upstream artifact host; sandbox image defaults still use `nousresearch/hermes-sandbox:desktop`. Replace only with tested SCI-owned equivalents. |
| UI/runtime dependencies | `@nous-research/ui` and the pinned speech-package fork retain their real external identities. Do not rename package IDs or invent replacement URLs. |
| Provider integrations | Nous auth/provider modules and catalog entries remain, even though the first-run/picker policy is restricted. Removing all of that code is a separate compatibility change, not a text substitution. |
| Skills/catalogs | External repository URLs and skill provenance still reference their actual publishers; some legacy instructions also need review. |
| Attribution and history | LICENSE, authorship, contributor records, migration fixtures and Git history retain original names intentionally. Product branding cleanup must not falsify provenance. |

The broad result also includes tests, model IDs, attack signatures and third-party
projects unrelated to this application's brand. Blind replacement would break
those identities and can weaken security checks.

### Verification and safety limits

- **135 Python tests passed**, seven macOS-only tests skipped, across 12 files
  through `scripts/run_tests.sh`. Covered icon generation, publication refusal,
  detached origin handling, namespace launchers, fresh-home skill distribution,
  disabled-skill defaults, Nous policy surfaces/filtering, import-repair guidance
  and storage-generation guards.
- **Eight JavaScript tests passed** across four files: documentation image
  reference resolution, installer background configuration, publication gates,
  namespace locks and real isolated icon generation. All **36 icon targets**
  passed generator structural checks. This does not validate a signed native DMG.
- Targeted Ruff, achievements JavaScript syntax, and whole-tree
  `git diff --check` passed (Git emitted only existing PowerShell line-ending
  conversion warnings).
- The candidate-tree credential heuristic found no flagged non-test token
  strings or sensitive credential/database filenames. Sixteen test files matched
  token/private-key patterns. This limited check does not certify secrets absent;
  Git history and binary/media metadata were not comprehensively secret-scanned.
- Fresh root-workspace `npm audit --omit=dev` reports **one high and eight low
  vulnerable package entries** (not nine independent advisories). The high entry
  is TUI `undici@6.28.0`; the audit proposes 6.29.0. The low entries include the
  previously recorded KaTeX dependency chain. This broader result supersedes any
  interpretation that the earlier desktop/shared/bootstrap-only audit certified
  the entire repository. No automatic dependency changes were made.
  Maintainer advisories:
  [WebSocket decompression](https://github.com/nodejs/undici/security/advisories/GHSA-3wwx-pv8p-q78v),
  [retry response framing](https://github.com/nodejs/undici/security/advisories/GHSA-r53p-7pc4-xj5r),
  [WebSocket subprotocol](https://github.com/nodejs/undici/security/advisories/GHSA-rfgv-xxqx-mfg5).
  Applicability/exploitability in SCI needs review alongside the upgrade tests.
- This was not the full test suite, a fresh-server install, a native build, or a
  scientific workflow acceptance run. Only about 2.7 GiB is free on this host.
  Python/Rust dependency review and native OS validation remain outstanding.

Before a public push: review the final staged diff and retained Git history for
secrets/licensing, finish the intended branding/dependency decisions, and supply
the approved repository. Before release: remediate/triage dependency findings,
validate fresh installs and native packages on their actual platforms, and supply
SCI release/update endpoints, signing identities and the private security contact.
Keep publication/update guards enabled until these gates are satisfied.

## Follow-up: classified reference cleanup

This receipt supersedes the earlier mirror/default-documentation findings where
noted; it does not supersede the remaining dependency or release blockers.

- Added `scripts/audit_branding.py`, `BRANDING_INVENTORY.json` and
  `BRANDING_REVIEW.md`. The read-only inventory records matching file/line
  locations and separates attribution, migration/security identities, external
  dependencies and unresolved documentation/runtime review. Classification is
  heuristic triage, not a claim that every match has been manually approved.
- Disabled the inherited binary backup mirror while retaining verified primary
  downloads and support for explicitly configured mirrors. Regenerated Bash and
  PowerShell bootstrap fragments. A primary download failure now fails honestly
  instead of silently reaching a different publisher.
- Removed default inherited catalog/star-cache network fetches during website
  generation. Unconfigured Telegram managed pairing stops before network access
  and directs users to manual BotFather setup; explicitly configured endpoints
  and ordinary token-based connections remain supported.
- Rewrote or retired 24 installation/update/hosted-service pages, corrected
  provider and tool-service recommendations, and repaired local documentation
  references. Regenerated 243 skill pages/catalogs with truthful bundled-skill
  metadata and contributor credits. The full legacy/localized corpus still
  requires review; it is not approved wholesale for publication.
- Removed 326 inherited testimonials from SCI's website and replaced the empty
  dataset's presentation with an honest pending-case-studies message. Originals
  are recoverable at
  `/home/boltzmann20/sci-removed-branding-1V35xY/website-userStories.json`.
- No live profile, credential, conversation or prompt-cache changes. Git has no
  configured remote; no commit, push or publication was performed.

### Follow-up verification

- Final focused reruns: **93 Python tests passed**, seven Windows-only tests
  skipped, across 18 files using `scripts/run_tests.sh`. This includes 76 tests
  for mirrors/bootstrap, document generators, skill metadata, pairing and setup;
  13 for inventory/namespace/publication/fresh-home skill distribution; and four
  selected dashboard-update tests. The rest of that dashboard test file is not
  included in this final count.
- **Seven JavaScript tests passed** across four files, including executing the
  real website prebuild in a temporary empty checkout with network interception,
  publication gates, media references and namespace lock consistency.
- Targeted Ruff, documentation link-style checks and generated-bootstrap
  consistency checks passed. TypeScript syntax-only checks passed for the
  changed case-study component, sidebars and site configuration. These are not
  full typechecks or a Docusaurus production build.
- Whole-tree `git diff --check` passed with only existing PowerShell line-ending
  warnings. No successful fresh-server installation receipt is claimed from
  this pass. Full installation/native-platform acceptance remains outstanding.

The latest inventory has 1,394 matched text files across 17,309 scanned regular
files. Counts include real package names, contributor credits, fixtures and newly
generated skill pages. They are not a deletion target. See `BRANDING_REVIEW.md`
for outstanding sandbox/UI/speech dependencies, optional provider compatibility,
documentation review, publication inputs and security/native acceptance gates.

## Source-installation handoff: 2026-10-08

This receipt supersedes earlier findings about the missing ordinary-user
installer, inherited UI/speech dependencies, sandbox default and production npm
vulnerabilities. Earlier receipts above remain historical evidence, not the
current installation guide.

### Changes and installation

- Added `install-sci.sh` and `INSTALLATION.md`. Run
  `bash ./install-sci.sh` from the complete checkout, or add `--non-interactive`
  for software-only server installation. The installer uses the managed runtime,
  locked core dependencies and bundled skills; it does not install developer
  groups, arbitrary scientific datasets/software, or signed native packages.
- Fixed reinstall recognition of the generated `agent-sci` launcher. Real fresh
  installation, rerun, quoted paths, skill/reference preservation and controlled
  missing-dependency/hash failures were exercised in disposable homes.
- Replaced the external publisher UI package with local `@sci/ui`, preserving
  original source/license notices. Replaced the speech fork with official Misaki
  0.9.4 source and recorded its hash/license. PM now snapshots declared local
  source dependencies into isolated environments.
- Repaired the Docker SQLite qualification SQL and build-context omissions.
  The sandbox default is a locally built SCI image; missing images give build
  instructions rather than pulling an invented registry image. Remote backends
  require an explicit compatible image.
- Removed the inherited default MCP hosted OAuth identity. Registered clients
  and dynamic registration remain supported. CIMD requires an approved explicit
  metadata URL; its unfilled template is under `examples/mcp/`, not served as a
  false public identity. Added real SDK/profile-scope regressions.
- Updated entry documentation, local help destinations and generated skill
  references. `README.md` and `INSTALLATION.md` are the source-setup authority;
  the full legacy/localized reference corpus is not approved wholesale.
- Archived 22 unused UI screenshots and experiments outside the repository at
  `/home/boltzmann20/sci-release-extras-5mj8M9/`. They remain recoverable.
  Research files, live credentials, sessions and profiles were not removed.
- Updated production JavaScript dependency pins; the final production npm audit
  reported zero known findings. Real external provider/package identifiers,
  security signatures and attribution are intentionally retained.

### Verification receipts

All Python checks used `scripts/run_tests.sh`. These are targeted groups, with
overlap between runs; do not add them into a claimed full-suite count.

- Fresh source installer: three controlled walkthrough tests passed.
- PM snapshot/build/activation: 34 tests passed across four files.
- MCP OAuth/security/SDK regressions: 146 tests passed across six files; two
  additional independent-identity/multiplexed A→B→A tests passed.
- Sandbox/desktop hints/launchers/model documentation: 60 passed, nine
  Windows-only cases skipped on this Linux host.
- Plugin/Discord/branding: 37 plugin tests, one Discord regression and two
  inventory tests passed.
- Documentation generation/CI mapping: 94 tests passed across four files.
- Final distribution/onboarding/skill defaults/profile process checks: 71
  passed across six files, one Windows-only case skipped.
- Real SQLite build qualification probe passed. A minimal Docker build using
  the actual filtered source context verified required local UI/speech/docs
  assets; this was not a full application/sandbox image build.
- Web: 360 tests across 51 files, typecheck and production build passed.
  Desktop: typecheck, production build and bundle-freshness assertion passed.
  Bootstrap frontend: typecheck and production build passed. The final focused
  root JavaScript run passed 21 tests across five files.
- Changed Python Ruff checks, shell syntax, documentation link-style lint and
  `git diff --check` passed. Existing PowerShell line-ending warnings remain.

### Git and release boundaries

No staging, commit, repository initialization, remote addition or push was
performed. The existing local history is retained and remotes remain absent.
The working-tree credential-pattern scan found reviewed synthetic fixtures,
not non-test credentials; binary contents are outside that scan.

A read-only scan of stored history found two unresolved non-test credential-like
literals in reachable blobs. They were not sent to services, authenticated or
printed. **Do not publicly push retained history until its owner approves the
history treatment.** See `SECURITY_SCAN_REVIEW.md` for redacted locations and
limits. History was not silently rewritten to hide this finding.

The source is prepared for local installation and Git review, not certified for
public release. The approved repository/security contact, history treatment,
SCI-owned publication destinations, full Docker/backend qualification, speech
acceptance, native Windows/macOS installers/signing and authorized scientific
workflow trials remain pending. No full test-suite, full Docusaurus production
build, live model/research-service or signed-native acceptance is claimed.

## Approved Git preparation: fresh SCI history

The owner supplied `https://github.com/boltzmannlabs/Agent-Scientist.git` and
approved a new public history while retaining the inherited history privately.
The old `.git` was copied and byte-compared to a permission-restricted backup
outside this checkout, on the separate storage drive, before removing the
original metadata. New Git metadata was initialized on `main`; old branches,
tags, reflogs and historical objects were not imported. Only the approved
repository was added as `origin`. Original licenses and contributor credit
remain; the root license adds a separate SCI-modifications notice.

The local author is `Dileepkumar-486`, with the corresponding GitHub ID-based
noreply email. No global Git identity was changed. This preparation does not
authorize or perform a push, publish native installers, or enable automatic
updates. The publication marker remains until SCI delivery is configured and
qualified; the source-updater check still has ten outstanding regressions,
including fixtures that assume the old publisher.

The `.gitignore` review corrected exclusions that would have lost the MCP
template, skill examples, authored desktop types, the empty website case-study
dataset and local speech dictionaries in a fresh clone. It keeps environment
secrets, legacy/current user state, research outputs, dependency trees and
generated bundles outside source. Docker's context likewise preserves the local
speech dictionaries while excluding research outputs. Twelve targeted tests
passed for fresh-history inclusion/exclusion, flat-install state safety,
installer behavior, the SQLite build probe and unpublished-update boundaries;
one Windows-only test was skipped on Linux. These tests do not imply
the full repository or a signed release is qualified.

The staged source review covered 17,451 files (approximately 187 MiB), with no
private state/dependency/output paths, symlinks, case-colliding paths or files
over GitHub's 100 MiB limit. A limited text credential-pattern scan found 33
matches across 31 test-fixture files and no non-fixture matches. The two flagged
historical blobs and inherited HEAD are absent from the new object database.
The initial whole-tree whitespace check reports inherited formatting and test
strings containing deliberate conflict markers; it is not a green full-tree
whitespace receipt. Those fixture strings were inspected, not deleted.
Installer shell syntax and the new ignore-policy test's Ruff check passed.

## CLI source updates enabled for the approved SCI repository

The owner requested enabling update recommendations and installation. Verified
Git source checkouts whose origin is `boltzmannlabs/Agent-Scientist` can now use
the existing `main` source-branch channel without a promoted release service.
The publication marker is retained: it still refuses unrelated source origins
and keeps native/promoted publication paths guarded. Official SCI checkouts
fetch from origin rather than an inherited upstream remote. The ZIP fallback
also receives the explicitly selected source repository for branch overrides.

Startup recommendations are read-only, normally cached for 24 hours and respect
`updates.check: false`. They never install software automatically. An immediate
check uses `sci update --check`; deliberate installation uses `sci update` or
`/update` in the CLI. Uncounted updates still show the correct update command.
Each tested commit subsequently pushed to `main` may be recommended; this does
not claim a signed stable release channel. Docker installations receive their
own approved-image rebuild guidance, not another publisher's registry command.

All targeted Python checks used `scripts/run_tests.sh`, with file retries
disabled: 291 distinct tests passed across 21 files; five native-platform tests
were skipped on this Linux host. The groups cover passive checks, release
channel validation, source admission, explicit checks, shallow/fork handling,
ZIP/Git completion, process routing, snapshots and publication boundaries.
The real local Git walkthrough advances a fixture origin, checks notifications
under temporary profiles A→B→A, then checks and pulls the selected revision
without contacting GitHub. Profile config, credentials, sessions and skill bytes
remain unchanged. Dependency/build/service completion is exercised separately
by the existing controlled completion tests, not installed into the live home.
The ten passive-check regressions noted above are resolved. Initial broader
fixture runs hit temporary root-disk limits; after fixing the ZIP repository
handoff, those tests passed serially on the larger storage drive. No full-suite,
signed-native or production research-service qualification is claimed.

A read-only `git ls-remote --heads origin` succeeded with no branch refs: the
approved GitHub repository still needs its initial push before source delivery
can operate for users. No production pull, live profile mutation, service restart,
push or release publishing was performed. Desktop/native signing, promoted feeds
and publication configuration remain separate release work.
