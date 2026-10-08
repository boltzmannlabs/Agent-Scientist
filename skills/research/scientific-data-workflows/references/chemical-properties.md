# Compound identity and 3D property retrieval

## Name → PubChem CID → requested descriptors

1. Discover and inspect current ToolUniverse schemas. Resolve the supplied name with `Metabolite_get_info({"compound_name": name})`; inspect `status`, `data.pubchem_cid`, formula, name, and returned source URL. Establish whether the record represents a parent compound, salt, or charged species before reporting mass.
2. Pass the returned CID to `PubChem_get_compound_properties_by_CID` with an explicit property list. Request `MolecularFormula`, `MolecularWeight`, and `ConnectivitySMILES` for core properties. PubChem's legacy `CanonicalSMILES` request can return the current `ConnectivitySMILES` key; inspect actual response keys rather than assuming the requested spelling.
3. For 3D conformation properties, request `Volume3D`, `XStericQuadrupole3D`, `YStericQuadrupole3D`, `ZStericQuadrupole3D`, `ConformerCount3D`, and `EffectiveRotorCount3D`. If pharmacophore features are useful, add `FeatureCount3D`, `FeatureAcceptorCount3D`, `FeatureDonorCount3D`, `FeatureAnionCount3D`, `FeatureCationCount3D`, `FeatureRingCount3D`, and `FeatureHydrophobeCount3D`.
4. Inspect `data.PropertyTable.Properties` and match the returned CID. Preserve numeric precision and distinguish missing fields from zero. A successful request need not provide every requested descriptor.
5. Report core properties first, then 3D descriptors and optional feature counts. Distinguish descriptor retrieval from retrieval of actual conformer coordinates; do not imply that a descriptor response supplies a 3D structure file.
6. Use source-documented units when verified; otherwise disclose that descriptor units were not included in the response. Do not reinterpret 3D donor/acceptor feature counts as conventional 2D hydrogen-bond counts, or cationic feature counts as the compound's formal charge.
7. Finish with the source identifier and actual tools used. Separate successful ToolUniverse retrieval from any independently executed web verification; do not invent a browser attempt or error to explain the source.
