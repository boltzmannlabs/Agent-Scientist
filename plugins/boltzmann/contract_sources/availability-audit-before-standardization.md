# Boltzmann submission-readiness audit

Reviewed 2026-10-14 against the repository contracts and retained source records.
No production experiment or live endpoint verification was performed. This is
an inventory of known gaps, not certification that every other request is correct.

## Catalogued requests

All 122 entries in `tool-contracts.v1.json` have an exact job name, a request
schema, a file-handling record and an input-limits record. None now has a
tool-level `execution_blocked` flag set to true. Authorization, profile access,
known-input validation and scientific safety checks still apply.

`Vina_basic_docking` has documented historical worker failures. These now cause
a warning requiring informed approval, not a permanent local ban. Recovery has
not been verified. Submit once and report the real service outcome; do not retry
an ambiguous submission or silently substitute another service.

The following request details still need attention:

| Job | Remaining information gap | Effect |
|---|---|---|
| `Multimer_Structure_Prediction` | `input_path` has no declared wire type; the source description mentions both CSV and colon-delimited text. | Confirm the intended mode and accepted payload from authoritative documentation; do not guess the file/text mapping. |
| `Property_Prediction` | `uncertainty` and `explainability` have no single declared type, but the schema explicitly permits numeric `0`/`1` and string `"0"`/`"1"`. | These are documented choices, not missing values to invent; review warnings do not prohibit a valid request. |
| `Property_Prediction` | The shape of `custom_models` elements is not established; the field description explicitly warns against unverified custom models. | Standard documented model requests are distinct from this unresolved optional mode. |
| `epitope_abgen` | Optional `epitope_residues` has no declared type or description. | Do not invent the value/shape. Its absence does not by itself block other documented modes. |

## File-security restrictions retained

- `Thermal_MPNN.model_path`: custom serialized model input lacks an approved
  safe validation path. The optional field is distinct from platform-default
  model use; do not fabricate a default storage path.
- `epitope_abgen.input_path`: prepared serialized-feature files/archives lack
  an approved safe validation path. Other input modes are separate.
- Serialized executable/model formats, unsafe archives, symlinks, excessive
  file sizes and known malformed inputs remain restricted. User approval for
  partial scientific checks does not disable security checks.

There are 52 file-field records marked partial and 48 with documented rules.
Even documented rules do not mean every scientific semantic check is implemented.
Incomplete specialized validation is disclosed and can proceed with explicit
approval when the request is otherwise valid; it is not a blanket submission ban.

## Previously excluded entries

These are now visible as `needs_contract_review`, not automatically enabled.
Documented names were restored from source records, never constructed from labels.
Historical status is retained in `previous_status` for traceability.

| Entry | Sourced job name | Gap |
|---|---|---|
| Toxicophore Screening | `toxic_screening` | Source is name-only; no request fields or output contract established. |
| Create Library | `create_library` | No reconciled executable request contract. |
| Fragments | `fragments` | Historical source exists; no reconciled executable request contract. |
| Deepcodon | `Deepcodon` | Historical source exists; no reconciled executable request contract. |
| Formulation Search | `Formulation_Search` | Historical source exists; no reconciled executable request contract. |
| QM-MM Single-Point Energy | `QM_MM_SPE` | Historical source exists; no reconciled executable request contract. |
| Interactive Builder | Not established | Both exact job name and executable request contract unresolved. |

Existing source fields are evidence to review, not proof of current entitlement
or a complete working request. In particular, do not claim that a historical
name is unknown when it is recorded above, or that an old exclusion proves the
platform service has been discontinued.

## Additional historical identifiers requiring reconciliation

The archived public-evidence record contains these identifiers outside the
current executable catalog. They have not been silently added or mapped to
similar names. A platform owner should confirm current support, exact submission
name, request schema and whether the entry is a separate mode or replacement:

```text
ligand_pharmacophore
fragment_based_training
Vina_Equidock
randomgen
chemprop
molscreening
DiffLinker
aa_rescoring
atom_openmm
deep-literature-search
data_transformation
QM_MM_Optimize
QM_MM_ReactionPath
QM_MM_SuggestRegion
QM_MM_ValidatePartition
QM_MM_CompareEmbeddings
QM_MM_Restore
QM_MM_BasisSensitivity
QM_MM_TS_Search
Formulation_Alternatives
Formulation_Dissolution
Formulation_Dose_Population
Formulation_PK
BE_Off_Target_Prediction
BE_Off_Target_Property_Prediction
Binding_Site_Prediction_batch
```

`PPI_Flow` and `Custom_Property_Model` are already represented as mode families;
their family labels must not be mistaken for missing individual catalog entries.
The old submission guard for `Fragment_based_generation_Inference`,
`Merge_Substructure`, `Substructures` and `Synergy_Prediction` remains: these
are outside the current executable catalog and have not been reconciled here.

## Evidence and scope

- Current: the three JSON files under `skills/boltzmann-tools/references/`.
- Historical: `contract_sources/legacy-v1/additional-tools.md`,
  `clarification-public-evidence.v1.json`, and `module-registry.v1.json`.
- All submission/output verification markers remain `not_retested`; this audit
  does not establish live scientific correctness, current availability or cost.
- Nothing in this audit grants account access, changes profile selection,
  authorizes a research-data upload, or spends service credits.
