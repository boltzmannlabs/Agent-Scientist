# Pre-publication credential review

This is a redacted review record, not a security certification. The owner chose
fresh public history while keeping the inherited history in a private backup
outside this repository. Do not import or publish that backup until the findings
below have been resolved. The findings do not occur in the new commit ancestry.

## Retained-history findings requiring owner review

Two non-test credential-like literals were found in reachable local history.
Their validity and ownership were not established. No credential was sent to a
provider, used for authentication, or reproduced in this report.

| Historical path | Blob object | Finding |
| --- | --- | --- |
| `skills/media/gif-search/SKILL.md`, line 24 | `a255b934d858c6c75d0758682146586f22c8a9b6` | Google/Tenor API-key-shaped literal in a request example |
| `evals/terminal-bench-2/evaluate_config.yaml`, line 59 | `1537d63ccc0d7b71d2039e57ecbc7df2f00985be` | Model-provider API-key-shaped literal in evaluation configuration |

Removing a value from current files does not remove it from prior commits.
Disconnecting a remote or running `git init` in an existing Git repository does
not clear its history either. Instead, the original metadata was copied and
byte-compared into a private backup before its removal from this checkout.
A new repository was initialized without copying the old refs or objects.
Original copyright and license notices remain in the source.

The owner approved publishing reviewed source with new public history and
retaining the old repository privately. The historical findings remain
unresolved in that backup, not approved as safe. A credential owner should
rotate/revoke any genuine credential; this cleanup has no authority over
third-party credentials. No push was performed during local preparation.

## Scan scope and limits

- Working-tree text scan: 17,375 existing, non-ignored source files at scan time.
  Twelve credential-pattern matches were reviewed as test fixtures. No sensitive
  state filenames, normalized/case-folded path collisions, or existing
  distributable filenames containing the old product name were found.
- Read-only history scan: 535,475 stored Git objects, including unreachable
  objects; 259,407 text objects examined. Most matches were test fixtures or
  credential-redaction pattern definitions. The two findings above remain
  unresolved, not approved exceptions.
- Binary objects and eight objects larger than 4 MiB were not text-scanned.
  A limited set of credential patterns cannot detect every secret or establish
  that a matching value is real. Filenames and object counts are point-in-time
  observations, not guarantees about future staged changes.
- Production npm dependency audit reported zero known findings. This is not a
  complete Python/Rust/development-dependency, licensing or application audit.

## Fresh-history staged review

The approved destination is `https://github.com/boltzmannlabs/Agent-Scientist.git`.
The staged source review examined 17,451 files, including 17,385 text files.
The broader limited credential-pattern scan matched 33 patterns across 31
test-fixture files, with no non-fixture matches. Private runtime/dependency/
research-output paths, symlinks, case collisions and files over 100 MiB were
absent from the proposed index. These checks have the detection limits above;
they are not a comprehensive security audit.

The two flagged historical blob IDs and the inherited HEAD are not present in
the newly initialized object database. Only the outside private backup retains
them. Recheck staged files and public-history contents if anything changes
before pushing. Never copy `.sci` state, credentials, research samples or local
profiles into the public source.
