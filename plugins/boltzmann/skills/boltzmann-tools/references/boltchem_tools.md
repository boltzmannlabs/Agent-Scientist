# Property Prediction
Tool display name:
Property Prediction

Frontend route/screen:
Small Molecule Design → QSPR Modelling

Exact form fields:
- Molecule input / smiles
- Uncertainty
- Explainability
- Global Property Models
- Experiment name (optional)
- Custom property model (optional and backend-dependent)

Required fields:
- One uploaded CSV path in experimentData.smiles
- CSV header exactly: SMILES
- At least one global_models selection
- uncertainty: 0 or 1
- explainability: 0 or 1

Optional fields:
- experimentName
- custom_models with a real supported model ID

Allowed choices and exact spelling:
- uncertainty: 0, 1
- explainability: 0, 1
- global_models: exact backend model-name strings, including:
  CaCo2 permeability, Half Life, Solubility, VDss, GIA, Clearance,
  Hydration Free Energy, LD50, Lipophilicity, PPBR, rPPB, hPPB,
  BBB, Bioavailability, HIA, PAMPA, PGP_inh, AMES, Carcinogenicity,
  DILI, hERG, Cyp1a2 inh, Cyp2c9 inh, Cyp2c9 sub, Cyp2c19 inh,
  Cyp2d6 inh, Cyp2d6 sub, Cyp3a4 inh, Cyp3a4 sub, and documented
  NR-* / SR-* endpoints.
- `Cyp2d9` entries in the older document should not be trusted; the
  verified backend spelling is `Cyp2d6`.

Sample input file:
One CSV containing:

SMILES
CCO
CC(=O)O

The live Property Prediction backend requires the `SMILES` column but accepts
additional columns in the same CSV and ignores them. Preserve those columns;
do not reject the file or silently create a projected one-column copy.
c1ccccc1
CC(C)O
C1CCCCC1

Required file format:
Exactly one readable `.csv` molecule-library file.

Required column names:
Exactly `SMILES` in uppercase.

Sample output file:
bpp_6a8ffd076534fa00c1b79871.csv

Observed output columns:
SMILES, ACTIVITY, CaCo2_permeability, QED, SA, TPSA,
NUM_HDONORS, NUM_HACCEPTORS, Molecular Weight

These are observed output columns, not universal input requirements.

Actual backend/network payload:
{
  "experimentData": {
    "smiles": "<cloud path returned by file_upload>",
    "uncertainty": 1,
    "explainability": 1,
    "global_models": ["CaCo2 permeability"]
  },
  "job_name": "Property_Prediction",
  "experimentName": "property_prediction_sample"
}

Exact backend job name:
Property_Prediction

Known validation or failure messages:
- Bare SMILES or a local path is rejected; smiles must be an uploaded CSV path.
- Wrong or missing header is rejected because it must be exactly SMILES.
- Empty global_models is invalid.
- uncertainty and explainability must be explicitly 0 or 1.
- Object-form global_models is invalid; use a list of strings.
- Sending an unsupported models field can produce HTTP 500.
- Missing model artifacts can produce signed-URL download errors such as HTTP 404.
- “Failed to generate output” is a terminal backend failure, not a valid result.
# IC50
Tool display name:Global IC50
Frontend route/screen:Small Molecule Design → QSPR Modelling
Exact form fields:
- `filepath` — uploaded CSV path for multiple molecule/sequence pairs.
- `smiles` — one ligand SMILES for the single-pair mode.
- `sequence` — one target protein sequence for the single-pair mode.
Required fields:
- Exactly one input mode is required:
  - Batch mode: `filepath` containing multiple paired rows.
  - Single-pair mode: both `smiles` and `sequence`.
- `experimentData` must contain the selected mode and must not mix an uploaded
  `filepath` with scalar values unless the backend contract explicitly requires
  both.
Optional fields:
- `experimentName` — optional experiment label.
Allowed choices and exact spelling:
- No enumerated model or flag choices are defined.
- `smiles` values must be non-empty, valid ligand SMILES strings.
- `sequence` values must be non-empty protein sequences in one-letter amino-acid
  notation.
- For batch mode, preserve the exact CSV headers `SMILES,SEQUENCES`.
- The backend wire key is singular `sequence`; the sample CSV header is plural
  `SEQUENCES` and must not be silently renamed without evidence.
Sample input file:/path/to/approved-input-or-output
Required file format:csv
Required column names:SMILES,SEQUENCES
Sample output file:/path/to/approved-input-or-output
output file column names: smiles,sequence,pIC50,IC50_nM
Actual backend/network payload:
data = {
        "experimentData": {
            "filepath": "CURRENT_USER_UPLOAD_PATH"
        },
        "job_name": "global_ic50",
        "experimentName": "prime"
    }

data = {
        "experimentData": {
            "smiles": "O=C1CCCC2=C1C1(CCS(=O)(=O)C1)NC(Nc1nc3ccccc3o1)=N2",
            "sequence": "USER_SUPPLIED_PROTEIN_SEQUENCE"
        },
        "job_name": "global_ic50",
        "experimentName": "global_ic50_test"
    }
Exact backend job name, if visible:global_ic50
Known validation or failure messages:
- A missing `filepath` in batch mode, or a missing `smiles`/`sequence` value in
  single-pair mode, is incomplete and must be clarified before submission.
- An unreadable, empty, malformed, or incorrectly headed CSV must be rejected
  before upload.
- Do not submit raw CSV text, a local filesystem path, or an HTTP URL as
  `experimentData.filepath`; use the cloud path returned by `file_upload()`.
- Do not treat a pending or queued result as a failure and do not duplicate the
  job while polling.
- A terminal result without `smiles`, `sequence`, `pIC50`, and `IC50_nM` is
  unverified and must not be reported as a successful prediction.

Submission instructions:
1. If the user supplies multiple pairs, validate one CSV with exact headers
   `SMILES,SEQUENCES`, upload it, and pass the returned cloud path as
   `experimentData.filepath`.
2. If the user supplies one pair, pass both scalar `smiles` and `sequence` in
   `experimentData` as shown in the verified payload.
3. Submit once using the exact job name `global_ic50` and keep
   `experimentName` top-level when supplied.
4. Poll the returned document ID with the same exact job name and verify the
   downloaded output before reporting values.

Polling and timeout behavior:
- Continue polling while the job is queued, pending, or running.
- A client-side polling timeout does not prove that the job failed; do not
  resubmit until the original job's absence or terminal failure is established.
- Retry only transient status/download failures through the existing helper
  behavior, never by creating a duplicate experiment.

Output verification:
- The verified output columns are exactly `smiles,sequence,pIC50,IC50_nM`.
- Verify that returned molecule/sequence pairs correspond to the submitted
  input and that both numeric result columns are populated before claiming
  success.
- `pIC50` is logarithmic; `IC50_nM` is the corresponding nanomolar estimate.

# Structure-Based Generator
Tool display name: Structure-Based Generator
Frontend route/screen: Small Molecule Design → Structure-Based Generation
Purpose: Generate small molecules for an uploaded protein binding-pocket
structure, optionally filtering the generated molecules with selected property
models.
Exact form fields:
- `protein_Path`
- `no_of_shapes`
- `no_of_decodings`
- `model_category` (optional)
- `global_models` (optional/conditional)
- `custom_models` (optional)
Required fields:
- `protein_Path`: uploaded `.pdb` platform path.
- `no_of_shapes`: integer, minimum `1`.
- `no_of_decodings`: integer, minimum `1`.
Optional fields:
- `model_category`; the verified sample used exact value `ML`.
- `global_models`; omit it or send `[]` when no property filter is selected.
- `custom_models`; omit it or send `[]` when no custom model is selected.
Allowed choices and exact spelling:
- `model_category`: verified sample value `ML`.
- Each selected global model must be an object containing exactly the relevant
  model name and numeric threshold bounds:
  `{ "name": "LD50", "min_threshold": "1", "max_threshold": "5" }`.
- If any global model is selected, both thresholds are mandatory and must be
  explicitly supplied by the user. Never invent, infer, default, or choose
  `min_threshold` or `max_threshold`.
- Threshold values may use the API's verified string representation, but must
  be numeric and `max_threshold >= min_threshold`.
- A selected global model must never be sent as a bare string such as
  `"global_models": ["QED"]`.
Sample input file: uploaded protein binding-pocket `.pdb` file (local sample
path not supplied in this packet).
Required file format: `.pdb`.
Required column names: not applicable to the PDB input.
Sample output file: verified `rawdata.csv` artifact.
Output file column names:
`SMILES,QED,SA,TPSA,NUM_HDONORS,NUM_HACCEPTORS,Molecular Weight`
Actual backend/network payload:
```python
uploaded_pocket_path = file_upload(local_pocket_pdb)

experiment_data = {
    "protein_Path": uploaded_pocket_path,
    "no_of_shapes": 3,
    "no_of_decodings": 4,
    "model_category": "ML",
    "global_models": [
        {"name": "LD50", "min_threshold": "1", "max_threshold": "5"}
    ],
    "custom_models": [],
}
job_name = "Structure_Based_Generator"
experiment_name = "Structure-based generation with LD50 filtering"
```
Exact backend job name, if visible: `Structure_Based_Generator`
Backend task: `structurebasedgen`
Validation status: verified working for a thresholded global-model submission;
terminal status was `Success`.
Known validation or failure messages:
- Raw sequence, PDB text, local paths, and HTTP URLs are invalid for
  `protein_Path`; upload an existing `.pdb` and use the returned platform path.
- `no_of_shapes` and `no_of_decodings` must be integers greater than or equal
  to `1`.
- With no property filtering, omitting both model arrays or sending both as
  empty arrays was observed valid (HTTP 200).
- Bare-string global models such as `global_models: ["QED"]` were observed
  invalid (HTTP 500); do not retry that identical payload.
- A non-empty custom-model item schema is not live-verified; do not invent it.
- A terminal output without a readable, non-empty CSV is unverified.

Submission instructions:
1. Confirm that the user has an existing valid binding-pocket/protein `.pdb`.
2. Upload it with `file_upload()` and use the returned path as
   `experimentData.protein_Path`.
3. Require integer `no_of_shapes >= 1` and `no_of_decodings >= 1`.
4. If global models are selected, require threshold objects with `name`,
   `min_threshold`, and `max_threshold` for every selected model. Ask the
   user for both threshold values when either is missing; never supply them
   on the user's behalf.
5. Submit once with `Structure_Based_Generator`.
6. Poll the returned document ID with the same job name and verify the
   downloaded artifact before reporting generated molecules.

Polling and timeout behavior:
- Continue polling while the job is queued, pending, or running.
- A client-side timeout does not prove failure; do not create a duplicate job
  until the original job's terminal state or absence is established.
- Retry transient status/download errors only through the existing helper
  behavior.

Output verification:
- Read the path from `OutputData.rawdata_path.path` and the download link from
  `OutputData.rawdata_path.download_link`.
- Handle `download_link` as either a list or a string.
- Verify the downloaded CSV is non-empty and parse every returned `SMILES`.
- Report the actual row count; do not assume it equals
  `no_of_shapes * no_of_decodings`.
- When property filters are selected, verify returned columns and values from
  the artifact instead of assuming every filter creates a named column.


# Random based generator-inference
Tool display name:Random based generation-inference
Frontend route/screen:
Exact form fields:num_samples,model_name,prop_model_category,global_models
Required fields:num_samples,model_name,prop_model_category,global_models
fields details and options: num-samplesintegrer(Total number of molecules to be generated that satisfy the given property profile.),
model_name:string[CharRNN,vae]
prop_model_category:string[ML]
globals_models:list of threshold objects; at least one global model is required
                ["CaCo2 permeability",
                "Half Life",
                "Solubility",
                "VDss",
                "GIA",
                "Biodegradability",
                "Cyp2d9 inh",
                "Cyp2d9 sub",
                "PGP sub",
                "Endocrine disrupting",
                "Eye corrosive",
                "Genotoxicity",
                "Clearance",
                "Hydration Free Energy",
                "LD50",
                "Lipophilicity",
                "PPBR",
                "rPPB",
                "hPPB",
                "Nephrotox_v3",
                "BBB",
                "Bioavailability",
                "HIA",
                "PAMPA",
                "PGP_inh",
                "Cyp1a2 inh",
                "Cyp2c9 inh",
                "Cyp2c9 sub",
                "Cyp2c19 inh",
                "Cyp2d6 inh",
                "Cyp2d6 sub",
                "Cyp3a4 inh",
                "Cyp3a4 sub",
                "AMES",
                "Carcinogenicity",
                "DILI",
                "hERG",
                "Skin reaction",
                "ClinTox",
                "NR-AR",
                "NR-AR-LBD",
                "NR-AhR",
                "NR-Aromatase",
                "NR-ER",
                "NR-ER-LBD",
                "NR-PPAR-gamma",
                "SR-ARE",
                "SR-ATAD5",
                "SR-HSE",
                "SR-MMP",
                "SR-p53"
            ]
Optional fields:
  `model_filePath`: optional fine-tuned generator checkpoint path. Use only the
  exact `.ckpt` path returned by a verified Random Generation Training result,
  together with that result's exact `model_name`.
  "custom_models": [
                {
                    "id": "",
                    "min_threshold": "",
                    "max_threshold": ""
                }]
Allowed choices and exact spelling:
- `model_name` must be the exact backend token `vae` or `CharRNN`; do not send
  UI labels such as `VAE`, `charRNN`, or `TransVAE` to this non-TransVAE job.
- `prop_model_category` must be the verified value `ML`.
- `global_models` is compulsory and must contain at least one object. Every
  selected model object must include `name`, `min_threshold`, and
  `max_threshold`.
- Whenever a global model is selected, both threshold values are mandatory and
  must be explicitly supplied by the user. The agent must never invent,
  infer, default, or choose either threshold.
- Thresholds must be numeric and `max_threshold >= min_threshold`; do not mix
  a numeric threshold with an empty string.
- Use no more than three total reward/property models when the backend applies
  the documented cardinality limit.
Sample input file:null
Required file format:null
Required column names:null
Sample output file:
Actual backend/network payload:
data = {
        "experimentData": {
            "num_samples": 3,
            "model_name": "CharRNN",
            "prop_model_category": "ML",
            "global_models": [
                {
                    "name": "Clearance",
                    "min_threshold": "3",
                    "max_threshold": "11"
                }
            ]
        },
        "job_name": "Random_based_generation_nontrans",
        "experimentName": "prime"
    }
Exact backend job name, if visible:Random_based_generation_nontrans
Known validation or failure messages:
- Missing `num_samples`, `model_name`, `prop_model_category`, or
  `global_models` is incomplete and must be clarified before submission.
- A global model without user-supplied `min_threshold` and `max_threshold`
  must be rejected before submission; never fill either value automatically.
- A bare-string global model such as `{"global_models": ["QED"]}` is invalid;
  use threshold objects instead.
- A missing, failed, or non-`.ckpt` `model_filePath` from a prior training
  result cannot be reused; report it and do not silently fall back to a global
  generator.
- A terminal `Success` with `save_gen_mols_path` equal to
  `"No molecules obtained"` means zero molecules passed the constraints, not
  a populated successful result.

Submission instructions:
1. Collect `num_samples`, exact `model_name`, and `prop_model_category="ML"`.
2. Require at least one selected global model and ask the user for both
   thresholds for every selected model.
3. Submit threshold objects, not bare model-name strings, using the exact job
   name `Random_based_generation_nontrans`.
4. For a custom generator, use only the verified prior training `.ckpt` path
   and matching model token.
5. Poll the returned document ID and verify `OutputData.save_gen_mols_path`.

Polling and output verification:
- Pending, queued, and running are not failures; continue polling the same
  document with the same job name and never duplicate the request.
- The successful output is an object containing `path` and `download_link`;
  handle the signed link through the existing download helper.
- The generated CSV should be non-empty, contain valid `SMILES`, and be
  checked for the selected property columns and actual row count.

# Pharmacophore based generator
Tool display name:Pharmacophore based generator
Frontend route/screen:
Exact form fields:experimentName, posp_path
Required fields:experimentName, posp_path
Optional fields:null
Allowed choices and exact spelling:
Sample input file:CURRENT_USER_UPLOAD_PATH
Required file format:posp
Required column names:
Sample output file:/path/to/approved-input-or-output
output file format:csv
columns of output file: SMILES,QED,SA,TPSA,NUM_HDONORS,NUM_HACCEPTORS,Molecular Weight
Observed successful output envelope: `OutputData.pgmg_upload_path` containing a
generated CSV `path` and one or more signed `download_link` values. A verified
live response returned HTTP 200 with `status: Success`.
Observed artifact path pattern:
`.../Pharmacophore_Based_Generator/pharmacophore-generator/<run_id>.csv`.

Actual backend/network payload:
data = {
        "experimentData": {
            "posp_path": "CURRENT_USER_UPLOAD_PATH"
        },
        "job_name": "Pharmacophore_Based_Generator",
        "experimentName": "prime"
    }
Exact backend job name, if visible:Pharmacophore_Based_Generator
Known validation or failure messages:
- Treat HTTP 200 with `status: Success` and a non-empty
  `OutputData.pgmg_upload_path` artifact as terminal success.
- Verify the signed download, non-empty CSV, documented columns, and actual row
  count before reporting generated molecules.

# Receptor based Pharmacophore hypothesis
Tool display name:Receptor based Pharmacophore hypothesis
Frontend route/screen:
Exact form fields:pdb_path, features, ligand
Required fields:pdb_path, features, ligand
Optional fields:
fields details and options:
pdb_path: String,
"features": [
                "hb acceptor",
                "hb donor",
                "aromatic ring",
                "hydrophobicity",
                "positive charge",
                "negative charge"
            ],
ligand:String
Allowed choices and exact spelling:
Sample input file:/path/to/approved-input-or-output
Required file format:pdb
Required column names:
Sample output file:
Observed successful output envelope: `OutputData.zip_files` (generated ZIP),
`OutputData.outputFilePath` (generated CSV), and
`OutputData.default_hypothesis` (generated `.posp` hypothesis). A verified live
response returned HTTP 200 with `status: Success`.
Observed artifact path patterns:
- `.../Pharmacophore_Hypothesis/pharmacophore-hypothesis/<run_id>.zip`
- `.../Pharmacophore_Hypothesis/pharmacophore-hypothesis/<run_id>.csv`
- `.../Pharmacophore_Hypothesis/pharmacophore-hypothesis/<run_id>_default.posp`
The exact CSV columns from the live artifact still require inspection; do not
invent them from the HTTP envelope. The `.posp` file is reusable by downstream
pharmacophore generation or screening.
Actual backend/network payload:
data = {
        "experimentData": {
            "pdb_path": "CURRENT_USER_UPLOAD_PATH",
            "features": [
                "hb acceptor",
                "hb donor",
                "aromatic ring",
                "hydrophobicity",
                "positive charge",
                "negative charge"
            ],
            "ligand": "DUE"
        },
        "job_name": "Pharmacophore_Hypothesis",
        "experimentName": "prime"
    }
Exact backend job name, if visible:Pharmacophore_Hypothesis
Known validation or failure messages:
- Treat HTTP 200 with `status: Success` and all expected output keys
  (`zip_files`, `outputFilePath`, and `default_hypothesis`) as terminal success
  only after each signed download is verified.
- A missing or unreadable ZIP, CSV, or `.posp` artifact is unverified; do not
  claim hypothesis generation succeeded.

# Molecule Enumeration
Tool display name:Molecule Enumeration
Frontend route/screen:
Exact form fields:building_blocks_file,input_scaffolds_file,global_models
Required fields:building_blocks_file,input_scaffolds_file,global_models
building_blocks_file:CSV input fragements generated via boltzmann's fragment extraction.
Fragments,Num_Atoms,Parent_Molecule_count,Parent_Molecules,Mol_wt,numHacceptors,numHdonors,clogp,rotatable_bonds
input_scaffolds_file:Input scaffold with R's at its position where the enumeration can be done.[THIS NEED NOT BE A PATH EVERY TIME IT WE CAN EVEN TYPE SMILES DIRECTLY, CHECK THE WORKING PAYLOAD ONCE]
globals_models:string"options are:
                ["CaCo2 permeability",
                "Half Life",
                "Solubility",
                "VDss",
                "GIA",
                "Biodegradability",
                "Cyp2d9 inh",
                "Cyp2d9 sub",
                "PGP sub",
                "Endocrine disrupting",
                "Eye corrosive",
                "Genotoxicity",
                "Clearance",
                "Hydration Free Energy",
                "LD50",
                "Lipophilicity",
                "PPBR",
                "rPPB",
                "hPPB",
                "Nephrotox_v3",
                "BBB",
                "Bioavailability",
                "HIA",
                "PAMPA",
                "PGP_inh",
                "Cyp1a2 inh",
                "Cyp2c9 inh",
                "Cyp2c9 sub",
                "Cyp2c19 inh",
                "Cyp2d6 inh",
                "Cyp2d6 sub",
                "Cyp3a4 inh",
                "Cyp3a4 sub",
                "AMES",
                "Carcinogenicity",
                "DILI",
                "hERG",
                "Skin reaction",
                "ClinTox",
                "NR-AR",
                "NR-AR-LBD",
                "NR-AhR",
                "NR-Aromatase",
                "NR-ER",
                "NR-ER-LBD",
                "NR-PPAR-gamma",
                "SR-ARE",
                "SR-ATAD5",
                "SR-HSE",
                "SR-MMP",
                "SR-p53"
            ]
Optional fields:null
Allowed choices and exact spelling:
Sample input file:/path/to/approved-input-or-output
Required file format:csv
Required column names:Fragments,Num_Atoms,Parent_Molecule_count,Parent_Molecules,Mol_wt,numHacceptors,numHdonors,clogp,rotatable_bonds
Sample output file:/path/to/approved-input-or-output
Actual backend/network payload:
data = {
        "experimentData": {
            "building_blocks_file": "CURRENT_USER_UPLOAD_PATH",
            "input_scaffolds_file": "CC(CNC(C1:C2CC(CCN:2:N:C:1)([R1]))=O)(C)C",
            "global_models": [
                "CaCo2 permeability"
            ]
        },
        "job_name": "Molecule_Enumeration",
        "experimentName": "Molecule_Enumeration_test"
    }
Exact backend job name, if visible:Molecule_Enumeration
Known validation or failure messages:

# Butina clustering
Tool display name: Butina
Frontend route/screen:
Exact form fields: "Path","model","DimReduce","sampling_type","cutoff","sampling"
Required fields:"Path","model","DimReduce","sampling_type","cutoff","sampling"
fields details and options:
[Path:CSV file path of ligands for clustering.With column name as SMILES,
model:[Butina,Murcko-Butina] ,
DimReduce: [PCa, tSNE],
sampling_type:[Random,Min-Max],
cutoff:float,Similarity threshold for molecules within each cluster.(0 to 1)
sampling:[yes,no]
]
Optional fields:null
Allowed choices and exact spelling:
Sample input file:/path/to/approved-input-or-output
Required file format:csv
Required column names:SMILES
Sample output file:/path/to/approved-input-or-output
output file column names: ID,ClusterID,SMILES
Actual backend/network payload:
data = {
        "experimentData": {
            "Path": "CURRENT_USER_UPLOAD_PATH",
            "model": "Butina",
            "DimReduce": "PCA",
            "sampling_type": "Random",
            "cutoff": 0.4,
            "sampling": "yes"
        },
        "job_name": "Butina_Clustering",
        "experimentName": "Butina_Clustering_test"
    }
Exact backend job name, if visible:Butina_Clustering
Known validation or failure messages:

# Kmean clustering
Tool display name:Kmean clustering
Frontend route/screen:
Exact form fields:Path, Features, DimReduce, no_of_cluster
Required fields:Path, Features, DimReduce, no_of_cluster
field details and options:
Path:CSV file path of ligands for clustering.With column name as SMILES
Features:[descriptors,fingerprints],
DimReduce:[PCA,tSNE]
no_of_cluster:integer(Number of clusters to be created.)
Optional fields:null
Allowed choices and exact spelling:
Sample input file:/path/to/approved-input-or-output
Required file format:csv
Required column names:SMILES
Sample output file:/path/to/approved-input-or-output
output column names: ID,ClusterID,SMILES
Actual backend/network payload:
data = {
        "experimentData": {
            "Path": "CURRENT_USER_UPLOAD_PATH",
            "Features": "descriptors",
            "DimReduce": "PCA",
            "no_of_cluster": "4"
        },
        "job_name": "K_Means_Clustering",
        "experimentName": "K_Means_Clustering_test"
    }
Exact backend job name, if visible:K_Means_Clustering
Known validation or failure messages:

# Pharmacophore screening
Tool display name:Pharmacophore Screening
Frontend route/screen:
Exact form fields:hypothesis_path, library, min_features
Required fields:hypothesis_path, library, min_features
Optional fields:null
Allowed choices and exact spelling:
No of file inputs required:2(hypothesis_path, library)
Sample input file:CURRENT_USER_UPLOAD_PATH,
CURRENT_USER_UPLOAD_PATH
Required file format:hypothesis_path:posp, library:csv
Required column names:csv file:SMILES,QED,SA,TPSA,NUM_HDONORS,NUM_HACCEPTORS,Molecular Weight
Sample output file:CURRENT_USER_UPLOAD_PATH
Actual backend/network payload:data = {
        "experimentData": {
            "hypothesis_path": "CURRENT_USER_UPLOAD_PATH",
            "library": "CURRENT_USER_UPLOAD_PATH",
            "min_features": "2"
        },
        "job_name": "Pharmacophore_Screening",
        "experimentName": "Pharmacophore_Screening_test"
    }
output payload:Status: 200
{'status': 'Success', 'OutputData': {'outputFilePath': [{'path': 'CURRENT_USER_UPLOAD_PATH, 'download_link': ['https://example.invalid/current-job-artifact {'path': 'CURRENT_USER_UPLOAD_PATH, 'download_link': ['https://example.invalid/current-job-artifact 'billing': [{'job_name': 'task-ph-screening-v4-tntdn', 'tool_name': 'ph_screening', 'node': 'boltzmann2', 'duration_seconds': 124, 'total_tool_runtime': 121, 'tool_lifetime_seconds': 124, 'rounded_minutes': 3, 'rate_per_hour': 20, 'amount': 1}]}
Exact backend job name, if visible:Pharmacophore_Screening
Known validation or failure messages:

# Similarity Screening
Tool display name:Similarity Screening
Frontend route/screen:
Exact form fields:ref_smile,ref_mols_path,lib_mols_path,screen_threshold
Required fields:ref_smile,lib_mols_path,screen_threshold
fields and details:
Reference SMILES*string
(A single SMILES of the reference molecule to compute similarity against.)
Reference Molecules CSV Path*string
(CSV file containing multiple reference molecules with a SMILES header.)

Library Molecules CSV Path*string
(Path to the input CSV file containing molecules to compute similarity with respect to the reference SMILES.)

Screening Threshold*integer
(Threshold for screening molecules in the library based on similarity with the reference SMILES.(0 to 1))
Optional fields:ref_mols_path
Allowed choices and exact spelling:
Sample input file:CURRENT_USER_UPLOAD_PATH
Required file format:csv
Required column names:SMILES
Sample output file:CURRENT_USER_UPLOAD_PATH
Actual backend/network payload:data = {
        "experimentData": {
            "ref_smile": "CCOC1=CC=C(C=C1)C(=O)N2CCC(CC2)NC(=O)C3=CC=CC=C3",
            "lib_mols_path": "CURRENT_USER_UPLOAD_PATH",
            "screen_threshold": "0.05"
        },
        "job_name": "Similarity_Screening",
        "experimentName": "prime"
    }
output_schema:Status: 200
{'status': 'Success', 'OutputData': {'sim_screen_data_path': {'path': 'CURRENT_USER_UPLOAD_PATH, 'download_link': ['https://example.invalid/current-job-artifact 'billing': [{'job_name': 'task-sim-screen-dll28', 'tool_name': 'sim_screen', 'node': 'boltzmann2', 'duration_seconds': 39, 'total_tool_runtime': 37, 'tool_lifetime_seconds': 39, 'rounded_minutes': 1, 'rate_per_hour': 20, 'amount': 1}]}
Exact backend job name, if visible:Similarity_Screening
Known validation or failure messages:
The fields ref_mols_path, ref_smile are interelated, when the user have only one reference smile then we use the field ref_smile and if the user have multiple then we make a csv of those smiles with column name as "SMILES" and we use the field ref_mols_path for that

# Substructure Screening
Tool display name:Substructure Screening
Frontend route/screen:
Exact form fields:library_path,substructures_path,method,task,screening_type
Required fields:library_path,substructures_path,method,task,screening_type
Fields and options:
library_path:CSV file path of the molecules to screen with respect to the substructure.
substructures_path:Substructures to use for screening: either a CSV file or a list of SMILES.
method:[graph_matcher,rdkit],
task:[toxic,substructure],
screening_type:[in,out]
Optional fields:null
Allowed choices and exact spelling:
Sample input file:CURRENT_USER_UPLOAD_PATH
Required file format:csv
Required column names:action_type,activity_comment,activity_id,activity_properties,assay_chembl_id,assay_description,assay_type,assay_variant_accession,assay_variant_mutation,bao_endpoint,bao_format,bao_label,canonical_smiles,data_validity_comment,data_validity_description,document_chembl_id,document_journal,document_year,ligand_efficiency,molecule_chembl_id,molecule_pref_name,parent_molecule_chembl_id,pchembl_value,potential_duplicate,qudt_units,record_id,relation,src_id,standard_flag,standard_relation,standard_text_value,standard_type,standard_units,standard_upper_value,standard_value,target_chembl_id,target_organism,target_pref_name,target_tax_id,text_value,toid,type,units,uo_units,upper_value,value,SMILES,Molecular Weight,ACTIVITY

Sample output file:
Actual backend/network payload:
data = {
        "experimentData": {
            "library_path": "CURRENT_USER_UPLOAD_PATH",
            "substructures_path": "C1C=CC=C(N)C=1",
            "method": "rdkit",
            "task": "substructure",
            "screening_type": "out"
        },
        "job_name": "Substructure_Screening",
        "experimentName": "Substructure_Screening_test"
    }
backend schema:
Exact backend job name, if visible:Substructure_Screening
Known validation or failure messages:

# QSPR Screening
Tool display name:QSPR Screening
Frontend route/screen:
Exact form fields:path,filters,global_models,custom_models
Required fields:path,filters
Optional fields:global_models,custom_models
`global_models` uses the fixed BoltChem property-model choices. `custom_models`
uses threshold objects such as `[{"id":"ss","min_threshold":"11","max_threshold":"11"}]`.
fields and options:
path:Path to the CSV file or library containing ligands with a 'SMILES' column for screening.
 "filters": [
                {
                    "value": "BBB",
                    "type": "Permeable"
                },
                {
                    "value": "Bioavailability",
                    "type": "Bioavailable"
                },
                {
                    "value": "BBB",
                    "type": "Impermeable"
                },
                {
                    "value": "HIA",
                    "type": "Absorbed"
                },
                {
                    "value": "HIA",
                    "type": "Not absorbed"
                },
                {
                    "value": "Bioavailability",
                    "type": "Non Bioavailable"
                },
                {
                    "value": "PGP_inh",
                    "type": "inhibitor"
                },
                {
                    "value": "PGP_inh",
                    "type": "non-Inhibitor"
                },
                {
                    "value": "Cyp2c9_inh",
                    "type": "inhibitor"
                },
                {
                    "value": "Cyp2c9_inh",
                    "type": "non-Inhibitor"
                },
                {
                    "value": "Cyp2c19_inh",
                    "type": "inhibitor"
                },
                {
                    "value": "Cyp2c19_inh",
                    "type": "non-Inhibitor"
                },
                {
                    "value": "Cyp1a2_inh",
                    "type": "inhibitor"
                },
                {
                    "value": "Cyp1a2_inh",
                    "type": "non-Inhibitor"
                },
                {
                    "value": "Cyp3a4_inh",
                    "type": "inhibitor"
                },
                {
                    "value": "Cyp3a4_inh",
                    "type": "non-Inhibitor"
                },
                {
                    "value": "Cyp3a4_sub",
                    "type": "substrate"
                },
                {
                    "value": "Cyp3a4_sub",
                    "type": "non-substrate"
                },
                {
                    "value": "Cyp2d6_inh",
                    "type": "non-Inhibitor"
                },
                {
                    "value": "Cyp2d6_inh",
                    "type": "inhibitor"
                },
                {
                    "value": "Cyp2c9_sub",
                    "type": "substrate"
                },
                {
                    "value": "Cyp2c9_sub",
                    "type": "non-substrate"
                },
                {
                    "value": "Cyp2d6_sub",
                    "type": "substrate"
                },
                {
                    "value": "Cyp2d6_sub",
                    "type": "non-substrate"
                },
                {
                    "value": "Hydration_Free_Energy",
                    "type": "None"
                },
                {
                    "value": "CaCo2_permeability",
                    "type": "High"
                },
                {
                    "value": "CaCo2_permeability",
                    "type": "Low"
                },
                {
                    "value": "Clearance",
                    "type": "High"
                },
                {
                    "value": "Clearance",
                    "type": "Low"
                },
                {
                    "value": "Half_Life",
                    "type": "Long"
                },
                {
                    "value": "Half_Life",
                    "type": "Short"
                },
                {
                    "value": "Lipophilicity",
                    "type": "High"
                },
                {
                    "value": "Lipophilicity",
                    "type": "Low"
                },
                {
                    "value": "PAMPA",
                    "type": "High"
                },
                {
                    "value": "PAMPA",
                    "type": "Low"
                },
                {
                    "value": "hPPB",
                    "type": "High"
                },
                {
                    "value": "hPPB",
                    "type": "Low"
                },
                {
                    "value": "PPBR",
                    "type": "High"
                },
                {
                    "value": "PPBR",
                    "type": "Low"
                },
                {
                    "value": "Solubility",
                    "type": "Soluble"
                },
                {
                    "value": "Solubility",
                    "type": "Insoluble"
                },
                {
                    "value": "VDss",
                    "type": "None"
                },
                {
                    "value": "AMES",
                    "type": "Toxic"
                },
                {
                    "value": "AMES",
                    "type": "Non toxic"
                },
                {
                    "value": "Carcinogenicity",
                    "type": "Carcinogenic"
                },
                {
                    "value": "Carcinogenicity",
                    "type": "Non Carcinogenic"
                },
                {
                    "value": "DILI",
                    "type": "Toxic"
                },
                {
                    "value": "DILI",
                    "type": "Non toxic"
                },
                {
                    "value": "hERG",
                    "type": "Toxic"
                },
                {
                    "value": "hERG",
                    "type": "Non toxic"
                },
                {
                    "value": "LD50",
                    "type": "None"
                },
                {
                    "value": "Skin_Reaction",
                    "type": "No skin reaction"
                },
                {
                    "value": "Skin_Reaction",
                    "type": "Skin reaction"
                },
                {
                    "value": "GIA",
                    "type": "High"
                },
                {
                    "value": "GIA",
                    "type": "Low"
                },
                {
                    "value": "Biodegradability",
                    "type": "Biodegradable"
                },
                {
                    "value": "Biodegradability",
                    "type": "Non biodegradable"
                },
                {
                    "value": "Cyp2d9_inh",
                    "type": "inhibitor"
                },
                {
                    "value": "Cyp2d9_inh",
                    "type": "non-Inhibitor"
                },
                {
                    "value": "Cyp2d9_sub",
                    "type": "substrate"
                },
                {
                    "value": "Cyp2d9_sub",
                    "type": "non-substrate"
                },
                {
                    "value": "PGP_sub",
                    "type": "substrate"
                },
                {
                    "value": "PGP_sub",
                    "type": "non-substrate"
                },
                {
                    "value": "Endocrine_disrupting",
                    "type": "Endocrine disrupting"
                },
                {
                    "value": "Endocrine_disrupting",
                    "type": "Non endocrine disrupting"
                },
                {
                    "value": "Eye_corrosive",
                    "type": "Corrosive"
                },
                {
                    "value": "Eye_corrosive",
                    "type": "Non corrosive"
                },
                {
                    "value": "Genotoxicity",
                    "type": "Genotoxic"
                },
                {
                    "value": "Genotoxicity",
                    "type": "Non genotoxic"
                },
                {
                    "value": "ClinTox",
                    "type": "Toxic"
                },
                {
                    "value": "ClinTox",
                    "type": "Non toxic"
                },
                {
                    "value": "rPPB",
                    "type": "High"
                },
                {
                    "value": "rPPB",
                    "type": "Low"
                },
                {
                    "value": "Nephrotox_v3",
                    "type": "None"
                },
                {
                    "value": "NR-AR",
                    "type": "Active"
                },
                {
                    "value": "NR-AR",
                    "type": "Inactive"
                },
                {
                    "value": "NR-AR-LBD",
                    "type": "Active"
                },
                {
                    "value": "NR-AR-LBD",
                    "type": "Inactive"
                },
                {
                    "value": "NR-AhR",
                    "type": "Active"
                },
                {
                    "value": "NR-AhR",
                    "type": "Inactive"
                },
                {
                    "value": "NR-Aromatase",
                    "type": "Active"
                },
                {
                    "value": "NR-Aromatase",
                    "type": "Inactive"
                },
                {
                    "value": "NR-ER",
                    "type": "Active"
                },
                {
                    "value": "NR-ER",
                    "type": "Inactive"
                },
                {
                    "value": "NR-ER-LBD",
                    "type": "Active"
                },
                {
                    "value": "NR-ER-LBD",
                    "type": "Inactive"
                },
                {
                    "value": "NR-PPAR-gamma",
                    "type": "Active"
                },
                {
                    "value": "SR-ARE",
                    "type": "Active"
                },
                {
                    "value": "NR-PPAR-gamma",
                    "type": "Inactive"
                },
                {
                    "value": "SR-ARE",
                    "type": "Inactive"
                },
                {
                    "value": "SR-ATAD5",
                    "type": "Active"
                },
                {
                    "value": "SR-ATAD5",
                    "type": "Inactive"
                },
                {
                    "value": "SR-HSE",
                    "type": "Active"
                },
                {
                    "value": "SR-HSE",
                    "type": "Inactive"
                },
                {
                    "value": "SR-MMP",
                    "type": "Active"
                },
                {
                    "value": "SR-MMP",
                    "type": "Inactive"
                },
                {
                    "value": "SR-p53",
                    "type": "Active"
                },
                {
                    "value": "SR-p53",
                    "type": "Inactive"
                }
            ]
Optional fields:custom_models
  "custom_models": [
                {
                    "id": "",
                    "min_threshold": "",
                    "max_threshold": ""
                }]
Allowed choices and exact spelling:
Sample input file:CURRENT_USER_UPLOAD_PATH
Required file format:csv
Required column names:SMILES
Sample output file:
Actual backend/network payload:
data = {
        "experimentData": {
            "path": "CURRENT_USER_UPLOAD_PATH",


            "filters": [
                {
                    "value": "BBB",
                    "type": "Permeable"
                },
                {
                    "value": "Bioavailability",
                    "type": "Bioavailable"
                }
            ]
        },
        "job_name": "QSPR_Screening",
        "experimentName": "Sample experiment - QSPR Screening"
    }
Exact backend job name, if visible:QSPR_Screening
Known validation or failure messages:

# Novelty
Tool display name:Novelty
Frontend route/screen:
Exact form fields:path,library,STRUCTURE_SEARCH,threshold
Required fields:path,library,STRUCTURE_SEARCH,threshold
path:CSV file path containing the molecules with header 'SMILES'.
library:[ChEMBL,SureChEMBL,Enamine]
STRUCTURE_SEARCH:[Identical,Similarity]
Similarity Threshold:Similarity threshold to consider as patentable or non-patentable if structure search is Similarity or else it is 1
Optional fields:null
Allowed choices and exact spelling:
Sample input file:CURRENT_USER_UPLOAD_PATH
Required file format:csv
Required column names:SMILES
Sample output file:
Actual backend/network payload:
data = {
        "experimentData": {
            "path": "CURRENT_USER_UPLOAD_PATH",
            "library": "ChEMBL",
            "STRUCTURE_SEARCH": "Identical",
            "threshold": 1
        },
        "job_name": "Novelty",
        "experimentName": "Novelty_test"
    }
Exact backend job name, if visible:Novelty
Known validation or failure messages:


---

# Additional BoltChem tools (scope update 2026-09-08)

These records are appended from the live BoltChem verification ledger. They are not part of the current optimization/lead-generation scope. Toxicity is intentionally not duplicated because the current plan treats it under the Substructure Screening worker family.

## Tool 2 — Custom Property Model - Classification (`Custom_Property_Model_DL`) — VERIFIED

### Identity
- Experiment Name: Custom Property Model - Classification
- Job Name: `Custom_Property_Model_DL` ⚠ (NOT `Custom_Property_Model_DNN_Classification`) — VERIFIED_LIVE
- API route: `/v4/proppred/dl` · internal task: `dlproptrain` · node: `boltzmann15`

### Verification Status
- Input contract verified: VERIFIED_LIVE (after 1 job-name correction)
- Submission verified: VERIFIED_LIVE (docId `CURRENT_JOB_ID`, 4 credits, est 3 min 21 s)
- Result fetch verified: VERIFIED_LIVE (terminal `Success`, 3 min 50 s compute / 636 s lifetime)
- Output download verified: VERIFIED_LIVE (train/test CSVs + **431 MB `.pt` model**)
- Output analysis verified: VERIFIED_LIVE (CSV passthroughs + torch checkpoint inspected)
- Downstream compatibility: VERIFIED_PRODUCT_FEATURES (model path feeds Property Prediction
  `custom_models` — not yet chained live)
- Confidence: HIGH — full lifecycle observed end-to-end

### Input Contract

| Field | Type | Required | Allowed | Default | Source |
|---|---|---|---|---|---|
| `property_name` | string | yes | becomes output filename stem | — | VERIFIED_LIVE |
| `filepath` | string (cloud CSV) | yes | uploaded training CSV | — | VERIFIED_LIVE |
| `modeltype` | string | yes | `"classification"` (this tool) | — | VERIFIED_LIVE |
| `modelName` | string | yes | `"DNN_Classification"` observed; grover is the actual backend | — | VERIFIED_LIVE |
| `transformation` | string | yes | `"no"` (Morgan/other transforms exist) | — | VERIFIED_LIVE |

Training CSV: header `SMILES,ACTIVITY`; ACTIVITY = class 0/1 (also accepts continuous for regression twin).

```python
{
    "experimentData": {
        "property_name": "logp_class",
        "filepath": "users/<userId>/<ts>/train_cls.csv",   # 32 rows
        "modeltype": "classification",
        "modelName": "DNN_Classification",
        "transformation": "no"
    },
    "job_name": "Custom_Property_Model_DL",
    "experimentName": "cpmc_verify"
}
```

### Submission Findings
- First attempt used job_name `Custom_Property_Model_DNN_Classification` → rejected
  (no such collection). Probed with empty payload → **`Custom_Property_Model_DL`** is the
  collection key. Corrected resubmit accepted.

### Result Contract — VERIFIED_LIVE
- Terminal status: `"Success"`
- OutputData keys (three): `TrainFile`, `TestFile` (split CSVs) and `outputFilePath` (**the trained
  model**) — each `{path, download_link:[...]}`
- Naming: `<property_name>_<backend>_<role>.csv` / `<property_name>_<backend>_model.pt`
  → observed `logp_class_grover_*` (backend is **grover** regardless of `modelName=DNN_Classification`)
- Path pattern: `users/<userId>/Custom_Property_Model_DL/property-predictors/<docId>/…`
- billing: `tool_name: "dlproptrain"`, 4 credits, rate 50/hr.

### Output Analysis — VERIFIED_LIVE
- TrainFile: 32 rows `SMILES,ACTIVITY` — exact passthrough of my upload (28× class 0, 4× class 1).
- TestFile: 4 rows — internal validation split.
- Model: **torch zip checkpoint, 431,511,849 bytes, 119 tensor entries.** `model/data.pkl` carries
  the training args: `parser_name: finetune`, `data_path: dl_data/frameworks/grover/logp_class/train.csv`,
  `batch_size: 32`, `gpu: 0` → it is a **GROVER fine-tune** checkpoint, self-contained (loads with
  `torch.load` without the platform).
- Input → output transformation: training CSV + property name → (a) split artifacts, (b) a portable
  pretrained-then-finetuned property model keyed by property name.

### Downstream Compatibility
- The model cloud path is the `path` field of `outputFilePath` → Property Prediction
  `custom_models: [{name: <property_name>, path: <path>, model_type: …, …}]` (contract from product
  features; chaining not yet run live — scheduled follow-up).
- The `.pt` downloads and loads anywhere torch exists — models are NOT platform-locked.

### Sci Execution Instructions
1. User supplies labeled data: `SMILES,ACTIVITY` CSV, classes 0/1. Check class balance locally;
   warn below ~10% minority.
2. Pick a short snake_case `property_name` (it becomes the model's identifier everywhere).
3. Upload CSV; submit payload above with `job_name="Custom_Property_Model_DL"`; budget 4 credits
   and ~4 min compute + queue.
4. Download all three artifacts (the model is ~431 MB — disk-space aware).
5. Store the model cloud path: it is the handle for future predictions via Property Prediction
   custom_models, or load the .pt directly in local torch.
6. Do not resubmit to "improve" — a new run trains from scratch and re-bills.

### Verified Quirks
- Job-name ≠ product name (`Custom_Property_Model_DL`, not `…_DNN_Classification`).
- `modelName: "DNN_Classification"` is a UI label; the backend always runs GROVER fine-tuning
  (visible in checkpoint args and output filenames).
- Model file is huge (431 MB) relative to a 32-row train set — it's the pretrained GROVER backbone;
  download time can exceed training time.
- With a tiny imbalanced set (28/4) training still completes cleanly — no minimum-data guard.

---



## Tool 3 — Custom Property Model - Regression (`Custom_Property_Model_Automl`) — VERIFIED

### Identity
- Experiment Name: Custom Property Model - Regression
- Job Name: `Custom_Property_Model_Automl` — VERIFIED_LIVE
- API route: `/v4/proppred/automl` · internal task: `automl` · node: `boltzmann3-hp-z6-g4-workstation`

### Verification Status
- Input contract verified: VERIFIED_LIVE (after 3 corrections — see Submission Findings)
- Submission verified: VERIFIED_LIVE (docId `CURRENT_JOB_ID`, 1 credit, est 39 s)
- Result fetch verified: VERIFIED_LIVE (terminal `Success`, 57 s compute)
- Output download verified: VERIFIED_LIVE (train/test CSVs)
- Output analysis verified: VERIFIED_LIVE (predictions + applicability-domain columns)
- Downstream compatibility: VERIFIED_PRODUCT_FEATURES only — **no model artifact is exposed**,
  so unlike the DL variant nothing user-portable is returned
- Confidence: HIGH on the observed contract

### Input Contract

| Field | Type | Required | Allowed | Source |
|---|---|---|---|---|
| `property_name` | string | yes | filename stem (`clogp`) | VERIFIED_LIVE |
| `filepath` | string (cloud CSV) | yes | `SMILES,ACTIVITY` (continuous labels) | VERIFIED_LIVE |
| `modeltype` | string | yes | `"regression"` | VERIFIED_LIVE |
| `features` | string | yes | `"descriptors"` observed (fingerprints likely) | VERIFIED_LIVE |
| `splittype` | string | yes | **`"randomsplit"`** (not `"random"`) | VERIFIED_LIVE |
| `modelName` | array | yes | `["automl"]` — array, lowercase | VERIFIED_LIVE |
| `transformation` | string | yes | `"no"` | VERIFIED_LIVE |

```python
{
    "experimentData": {
        "property_name": "clogp",
        "filepath": "users/<userId>/<ts>/train_reg.csv",
        "modeltype": "regression",
        "features": "descriptors",
        "splittype": "randomsplit",
        "modelName": ["automl"],
        "transformation": "no"
    },
    "job_name": "Custom_Property_Model_Automl",
    "experimentName": "cpmr_verify"
}
```

### Submission Findings (3 rejections before accept — richest correction chain of the batch)
1. `splittype: "random"` → rejected; enum is **`randomsplit`**.
2. `modelName: ""` → rejected; must be an **array**.
3. `modelName: ["AutoML"]` → rejected "Invalid ML regression model"; must be **lowercase `["automl"]`**.
Accepted on 4th attempt.

### Result Contract — VERIFIED_LIVE
- Terminal status: `"Success"`
- OutputData keys: only `TestFile` and `TrainFile` — **no model file key** (contrast: DL variant
  returns a 431 MB `.pt`). The trained AutoML model is not downloadable.
- Naming: `<property_name>_<model>_<features>_train/test.csv` → `clogp_rf_descriptors_*.csv`
  (rf = the AutoML-selected random forest).
- billing: `tool_name: "automl"`, 1 credit, 57 s compute, cheap node.

### Output Analysis — VERIFIED_LIVE
- TrainFile: `Label,ACTIVITY` — my input values plus slight perturbation (Label = input truth?
  ACTIVITY = model fit). 42 rows.
- TestFile (8 rows): `Label, ACTIVITY, distances, applicability_domain` —
  **the only custom-model tool that reports applicability domain**: `distances` = distance to
  training manifold, `applicability_domain` = Yes/No flag. One point at distance 1,325 → still
  flagged "Yes" (threshold appears lenient or absolute-scaled).
- Fit quality on the toy set: |Label−ACTIVITY| ≈ 0.01–0.17 across 8 test points — good on
  trivial data (clogp from SMILES is an easy descriptor task).
- Input → output transformation: labeled CSV → trained (server-side) regressor + validation
  split with per-point predictions and AD flags.

### Downstream Compatibility
- Nothing portable leaves the platform (no model file). If the user needs to run predictions
  later, the path is Property Prediction with `custom_models` — whether the AutoML backend
  supports that hook is UNVERIFIED; recommend the DL variant when portability matters.
- TestFile is self-contained (truth + prediction + AD) — directly reportable to users.

### Sci Execution Instructions
1. Build `SMILES,ACTIVITY` CSV with **continuous** labels; upload.
2. Submit with the exact enums above (`randomsplit`, lowercase `["automl"]`); 1 credit; ~1 min.
3. Download both CSVs; report test metrics from Label vs ACTIVITY, flag points where
   `applicability_domain` is No.
4. Warn the user: no downloadable model artifact from this variant.

### Verified Quirks
- Strict enums: `randomsplit` not `random`; `automl` lowercase array.
- No model artifact in OutputData — the DL variant (`Custom_Property_Model_DL`) is the one that
  returns a portable `.pt`.
- AutoML picks the model (rf here); the chosen model surfaces only in the output filename.

---



## Tool 5 — Binding Site Prediction (`Binding_Site_Prediction`) — VERIFIED

### Identity
- Experiment Name: Binding Site Prediction
- Job Name: `Binding_Site_Prediction` — VERIFIED_LIVE
- API route: `/v4/3DModule/fpocket` · internal task: `fpocket` · node: `boltzmann2`

### Verification Status
- Input contract verified: VERIFIED_LIVE (accepted payload below)
- Submission verified: VERIFIED_LIVE (docId `CURRENT_JOB_ID`, credits 2, est 2 min 30 s)
- Result fetch verified: VERIFIED_LIVE (terminal `Success` in ~18 s compute)
- Output download verified: VERIFIED_LIVE (`output_stats.csv` + `protein.pdb` from GCS signed URLs)
- Output analysis verified: VERIFIED_LIVE (4 pockets, CSV + PDB + inline JSON fully inspected)
- Downstream compatibility verified: VERIFIED_LIVE (pocket PDB path fed to Structure_Based_Generator — accepted)
- Confidence: HIGH — full lifecycle observed end-to-end

### Input Contract

| Field | Type | Required | Allowed Values | Default | Source |
|---|---|---|---|---|---|
| `pdb_path` | string | yes | cloud `.pdb` path from `file_upload` **OR bare PDB-ID string** | — | yup schema + VERIFIED_LIVE (bare `1LYZ` accepted!) |

Single-field tool. No other parameters.

### Contract Conflicts Resolved
1. **Bare PDB-ID accepted.** Despite the schema reading like a file path, the live payload
   `"pdb_path": "1LYZ"` was accepted and the backend fetched the structure from RCSB itself
   (node downloaded 1LYZ lysozyme, 129 residues, chain A). Cloud-path upload also works
   (that is how PH-R/6FMC was submitted). Prefer the bare ID when the user names a PDB entry —
   skip upload entirely.
2. No `chain`/`ligand` filtering options exist at this layer — fpocket runs on the whole structure.

### Verified Submission Payload

```python
{
    "experimentData": {"pdb_path": "1LYZ"},   # bare PDB-ID, no upload needed
    "job_name": "Binding_Site_Prediction",
    "experimentName": "bsp_verify"
}
```

### Result Contract — VERIFIED_LIVE
- Terminal status: `"Success"`
- OutputData keys: **three**, of different shapes:
  - `outcsv_path` → object `{path, download_link:[...]}` — pocket statistics CSV
  - `pdb_path` → object `{path, download_link:[...]}` — processed protein PDB
  - `pockets_data` → **inline JSON array** (no download link!) — per-pocket detail dicts keyed `pocket_1..N`
- `pockets_data[i].pocket_N` fields: `x_center/y_center/z_center` (floats), `Max_Radius` (Å),
  `PDB` (cloud path to `pockets/pocketN_atm.pdb` — NOT in OutputData download links; construct
  signed URL only by re-fetching result), `pocket_seq` (list of per-residue
  `{highlight: "False"|"True", protein_seq: <1-letter>}` for UI rendering), `pocket_residues`.
- Billing: `tool_name: "fpocket"`, credits 2, 18 s compute.

### Output Analysis — VERIFIED_LIVE (1LYZ → 4 pockets)
- `output_stats.csv`: columns `Pockets, GCP_Path, Druggability_Score, Pocket_Residues,
  Center_Coordinates, Max_Radius` — one row per pocket, pockets already sorted by druggability.
- 1LYZ (lysozyme, 129 res): Pocket-1 druggability **0.4464** (16 residues, radius 17.53 Å — the
  canonical substrate cleft), Pocket-2 0.1361, Pockets 3–4 ≈ 0 (shallow surface sites). Correct
  behavior: lysozyme is a hard, low-druggability target; the active-site cleft still ranks #1.
- `protein.pdb`: full processed structure (129 residues, chain A) — usable as generic receptor input.
- `GCP_Path` column values are bare cloud paths (`users/.../pockets/pocket1_atm.pdb`) — these are the
  pocket-only PDBs; the platform does NOT hand you signed URLs for them in the result body.
- Input → output transformation: 1 PDB → N pocket rows + pocket PDBs + centers/radii for all pockets.

### Downstream Compatibility — VERIFIED_LIVE
- `pockets_data[0].pocket_1.PDB` (or the CSV `GCP_Path` column) → **`protein_Path` of
  Structure_Based_Generator** (verified accepted — SBG submission used exactly this value).
- `Center_Coordinates`/`Max_Radius` → constraint-box parameters for docking tools (vina/diffdock).
- `protein.pdb` → any tool wanting a clean receptor (`Pharmacophore_Hypothesis`, docking, MDS).

### Sci Execution Instructions
1. Get a structure: user PDB-ID (pass bare string, no upload) or uploaded `.pdb` file path.
2. Submit single-field payload; `job_name="Binding_Site_Prediction"`.
3. Poll to `Success`; read `pockets_data` inline for pocket count, centers, radii.
4. Download `outcsv_path` + `pdb_path` artifacts (links expire in 300 s).
5. Rank pockets by `Druggability_Score`; report top pockets with residue counts and centers.
6. To chain into generation: use pocket-1's `PDB` cloud path as SBG `protein_Path`; for docking,
   use `protein.pdb` + pocket center/radius as the search box.
7. Never fabricate signed URLs for `pockets/pocketN_atm.pdb` — pass the bare cloud path to the
   next tool's payload (tools read each other's cloud paths directly).

### Verified Quirks
- Bare PDB-ID in `pdb_path` works — no upload round-trip needed for public structures.
- `pockets_data` is inline JSON, not a download; the pocket atom-PDBs inside it are cloud paths
  without signed URLs — downstream tools accept the cloud path as-is.
- 2 credits for an 18 s run (rate ~50/hr node-minutes).
- `pocket_seq` is a per-residue UI-highlight structure (verbose); use `pocket_residues` from the CSV
  for a compact residue list.

---



## Tool 7 — Random Generation - Training (`Random_based_generation_training`) — VERIFIED

### Identity
- Experiment Name: Random Generation - Training
- Job Name: `Random_based_generation_training` — VERIFIED_LIVE
- API route: `/v4/generators/customgen` · internal task: `customgen` (billing label `charrnn`)
- Node: `boltzmann3-hp-z6-g4-workstation` (rate 1/hr)

### Verification Status
- Input contract verified: VERIFIED_LIVE (after 2 corrections — see Submission Findings)
- Submission verified: VERIFIED_LIVE (docId `CURRENT_JOB_ID`, 1 credit, est 22 s)
- Result fetch verified: VERIFIED_LIVE (terminal `Success`, 2 min 30 s compute)
- Output download verified: VERIFIED_LIVE (67.9 MB `.ckpt`)
- Output analysis verified: VERIFIED_LIVE (checkpoint internals inspected)
- Downstream compatibility verified: VERIFIED_PRODUCT_FEATURES (ckpt path feeds
  Random Generation-Inference `model_filePath` — same shape as the global ckpt this run consumed;
  chaining not yet run live)
- Confidence: HIGH — full lifecycle observed end-to-end

### Input Contract

| Field | Type | Required | Allowed | Source |
|---|---|---|---|---|
| `num_epochs` | number | yes | 2 observed (fast verify) | VERIFIED_LIVE |
| `num_samples` | number | yes | 100 observed | VERIFIED_LIVE |
| `model_name` | string | yes | **lowercase** `"vae"` (`"VAE"` rejected) | VERIFIED_LIVE |
| `model_filePath` | string | yes | global ckpt e.g. `"globalgenerators/vae_alldata.ckpt"` or your own prior output | VERIFIED_LIVE |
| `dataPath` | string (cloud CSV) | yes | uploaded `SMILES`-header training CSV | VERIFIED_LIVE |
| `model_category` | string | yes | `"ML"` observed | VERIFIED_LIVE |
| `global_models` | array | yes | `[{name, min_threshold, max_threshold}]` threshold objects | VERIFIED_LIVE |

```python
{
    "experimentData": {
        "num_epochs": 2, "num_samples": 100,
        "model_name": "vae",
        "model_filePath": "globalgenerators/vae_alldata.ckpt",
        "dataPath": "users/<userId>/<ts>/train_gen.csv",
        "model_category": "ML",
        "global_models": [{"name": "Solubility", "min_threshold": -4, "max_threshold": 0.4}]
    },
    "job_name": "Random_based_generation_training",
    "experimentName": "rgt_verify"
}
```

### Submission Findings
- Attempt 1: `model_name: "VAE"` → schema rejection (case). Attempt 2: attribute-object array in
  the wrong layer (`attribute` key at top level) → rejected. Correct form: `global_models`
  containing `{name, min_threshold, max_threshold}` objects. Third submit accepted.

### Result Contract — VERIFIED_LIVE
- Terminal status: `"Success"`
- OutputData keys: exactly one — `outputFilePath` → `{path, download_link:[...]}`
- Artifact: `<docId>_finetuned_model.ckpt` (67,863,919 bytes)
- Path pattern: `users/<userId>/Random_based_generation_training/…/<docId>_finetuned_model.ckpt`
- billing: `tool_name: "customgen"`, 1 credit, rate 1/hr, compute 2 min 30 s for 2 epochs.

### Output Analysis — VERIFIED_LIVE
- PyTorch-Lightning **1.4.2** zip checkpoint, 84 tensor entries.
- Metadata: `epoch: 1` (0-indexed → 2 epochs as requested), `global_step: 3`.
- `state_dict` begins `encoder.x_emb.weight` = **39×39 float tensor** → 39-character SMILES
  vocabulary embedding; encoder/decoder char-VAE architecture.
- "finetuned_model" naming confirms the run **fine-tuned the provided global ckpt**
  (`vae_alldata.ckpt`) on the user CSV rather than training from scratch.
- Input → output transformation: SMILES CSV + base model + property thresholds → a portable
  Lightning char-VAE checkpoint specialized to the user's chemical space.

### Downstream Compatibility
- The ckpt cloud path slots directly into Random Generation-Inference `model_filePath`
  (same field that accepted the global ckpt here) — custom-model inference loop is closed.
- Also downloadable and loadable locally (`torch.load(..., weights_only=False)` under
  PL-class definitions) — not platform-locked.

### Sci Execution Instructions
1. Collect the user's reference SMILES library (≥50 recommended) into a `SMILES`-header CSV;
   upload it.
2. Pick base model: `globalgenerators/vae_alldata.ckpt` for general chemistry; a previous
   custom ckpt path to keep specializing.
3. Real trainings want `num_epochs` 20–100 (2 was a verification setting); credits scale with
   node-minutes on the cheap rate-1 node.
4. Property thresholds in `global_models` shape generation toward the desired region.
5. Submit with `job_name="Random_based_generation_training"`; poll to `Success`.
6. Download the ckpt (68 MB) and record its **cloud path** — that path is the handle for
   Random Generation-Inference runs.

### Verified Quirks
- `model_name` must be lowercase (`vae`).
- The `attribute`-vs-`global_models` layering is the #1 rejection cause for all generative tools.
- Billing labels the task `charrnn` while the model is a char-VAE — internal naming drift,
  harmless.
- Checkpoint pins `pytorch-lightning 1.4.2` — loading it in much newer PL may need shim
  (`weights_only=False` / manual state_dict load).

---



## Tool 9 — Pharmacophore Hypothesis - Ligand based (`ligand_pharmacophore`) — BLOCKED (platform artifact bug)

### Identity
- Experiment Name: Pharmacophore Hypothesis - Ligand based
- Job Name: `ligand_pharmacophore` — VERIFIED_LIVE
- API route: `/v4/pharmacophore/lig_phcore` · internal task: `lig_phcore` · node: `boltzmann2`

### Verification Status
- Input contract verified: VERIFIED_LIVE (payload accepted twice)
- Submission verified: VERIFIED_LIVE (v1 docId `CURRENT_JOB_ID`, 25 credits;
  v2 docId `CURRENT_JOB_ID`)
- Result fetch verified: VERIFIED_LIVE (both terminal `Success`)
- Output download verified: **BLOCKED — reproducible platform bug (2/2 runs)**: result body
  advertises `zip_files` + `default_hypothesis` paths but the GCS objects do not exist
  (`NoSuchKey` on fresh signed URLs from re-fetched result). Not expiry, not auth — the worker
  never uploads the artifacts.
- Confidence: HIGH on input/submit/result contract; artifact retrieval BLOCKED by platform bug

### Input Contract

| Field | Type | Required | Allowed | Default | Source |
|---|---|---|---|---|---|
| `smiles_file` | string (cloud CSV) | yes | uploaded path, header `SMILES` | — | VERIFIED_LIVE |
| `validation_file` | string (cloud CSV) | yes | uploaded path | — | VERIFIED_LIVE |
| `min_features` | number | yes | 2–5 observed | — | VERIFIED_LIVE |
| `max_features` | number | yes | ≥ min | — | VERIFIED_LIVE |
| `percentage` | number 0–1 | yes | e.g. 0.5 | — | VERIFIED_LIVE |
| `n_conformers` | number | yes | e.g. 20 | — | VERIFIED_LIVE |
| `features` | array of strings | yes | subset of `["hb acceptor","hb donor","aromatic ring","hydrophobicity","positive charge","negative charge"]` | — | VERIFIED_LIVE |

### Verified Submission Payload (v2 — the retry)

```python
{
    "experimentData": {
        "smiles_file": "users/<userId>/<ts>/ligands.csv",        # 12 ligands
        "validation_file": "users/<userId>/<ts>/validation.csv", # 6 ligands
        "min_features": 2, "max_features": 5,
        "percentage": 0.5, "n_conformers": 20,
        "features": ["hb acceptor", "hb donor", "aromatic ring", "hydrophobicity"]
    },
    "job_name": "ligand_pharmacophore",
    "experimentName": "phl_verify_v2"
}
```

### Result Contract — VERIFIED_LIVE (shape) / BLOCKED (artifacts)
- Terminal status: `"Success"` (v1: 98 s runtime; v2: 26 s)
- OutputData keys: `outputFilePath` (**empty string**), `zip_files` → `{path, download_link:[...]}`,
  `default_hypothesis` → `{path, download_link:[...]}`
- `default_hypothesis.path` pattern: `users/<userId>/ligand_pharmacophore/lig_phcore/<docId>_default.posp`
- **Both v1 and v2: signed URLs return GCS `NoSuchKey` — objects were never created.**
  Fresh-link re-fetch (same docId) gives the same 404 → this is a worker upload bug, not client error.
- 25 credits charged despite missing artifacts.

### Output Analysis — BLOCKED
- Cannot inspect zip/posp contents (objects absent). Expected by symmetry with PH-Receptor:
  hypothesis `.posp` (feature-type + xyz lines), best-hypothesis SDF, CSV summary.

### Downstream Compatibility — VERIFIED_LIVE (payload layer) / BLOCKED (data layer)
- `default_hypothesis.path` was passed as `posp_path` to Pharmacophore_Based_Generator (tool12) —
  payload accepted at submit. Whether the worker can actually READ the nonexistent posp is
  pending tool12's terminal result (that error path is itself documentation).

### Sci Execution Instructions
1. Build two CSVs (`SMILES` header): actives/training set and validation set (keep ≥5 each).
2. Upload both; submit payload above; `job_name="ligand_pharmacophore"`. Budget **25 credits**.
3. Poll to `Success`; attempt both downloads immediately.
4. On 404 `NoSuchKey`: re-fetch the result once for a fresh link; if still 404, record the docId and
   report the platform artifact bug — do NOT resubmit more than one retry (bug is reproducible).
5. Fallback path for users needing a pharmacophore today: use **Pharmacophore Hypothesis - Receptor**
  (its artifacts DO persist) or run ligand-based pharmacophore locally.

### Verified Quirks
- **Reproducible artifact-persistence bug**: `Success` status + advertised paths + zero uploaded
  objects, two independent runs with different parameters. `outputFilePath` empty string in both.
- 25 credits per run (most expensive tool in batch 2) — charged even when artifacts fail to upload.
- v1 vs v2 parameter change (v1 used tighter feature/percentage settings) made no difference →
  not input-dependent.

---



## Tool 12 — Pharmacophore Based Generator - Ligand (`Pharmacophore_Based_Generator`) — BLOCKED (upstream PH-L artifact bug)

### Identity
- Experiment Name: Pharmacophore Based Generator - Ligand
- Job Name: `Pharmacophore_Based_Generator` (same as Receptor variant) — VERIFIED_LIVE
- API route: `/v4/pharmacophore/pharmacophoreMolGen`

### Verification Status — BLOCKED (upstream dependency broken, failure path itself verified)
- Input contract verified: VERIFIED_LIVE (payload accepted; same single-field contract as Receptor variant)
- Submission verified: VERIFIED_LIVE (docId `CURRENT_JOB_ID`)
- Result fetch verified: VERIFIED_LIVE — terminal **`failed`** with
  `message: "Failed to generate output"` after 448 s
- Output download: N/A (no OutputData in failed body)
- Root cause: `posp_path` pointed at Pharmacophore Hypothesis-Ligand's `default_hypothesis.path`
  whose GCS object was never uploaded (see tool 9's artifact bug). The generator worker could not
  read its input → generic failure message.
- Confidence: HIGH — the failure path is conclusively attributed (only variable vs the successful
  Receptor run was the posp source)

### Verified Submission Payload

```python
{
    "experimentData": {"posp_path": "users/<userId>/ligand_pharmacophore/lig_phcore/<phlDocId>_default.posp"},
    "job_name": "Pharmacophore_Based_Generator",
    "experimentName": "pbgl_verify"
}
```

### Findings
- **The complete tool behaves as designed; the blocker is upstream.** Same job_name, same schema,
  same single field as the successful Receptor run.
- Failure surfaces as `status: "failed"`, `message: "Failed to generate output"` — **generic;
  no mention of the missing input object.** Poller must treat `failed` as terminal and Sci must
  correlate failures back to input provenance (here: PH-L's known artifact bug).
- Credits: 1 charged at submit; no billing block in the failed body.

### Sci Execution Instructions
1. Do NOT chain from ligand-based hypotheses until the PH-L artifact bug is fixed — validate the
   posp exists (attempt a result re-fetch + download once) before spending a PBG run.
2. If a PBG-Ligand run fails with "Failed to generate output": check the posp source first.
3. Working alternative today: Pharmacophore Hypothesis-**Receptor** → PBG (verified chain).

### Verified Quirks
- `failed` status carries no structured error — input-provenance debugging is the agent's job.
- A dependent job can outlive its upstream's artifact bug by design: PBG-Ligand queued fine and
  failed only at worker stage.

---



## Tool 17 — Pharmacophore Screening - Ligand (`Pharmacophore_Screening`) — BLOCKED (upstream)

### Identity
- Route: `/v4/pharmacophore/ph_screening` · job_name `Pharmacophore_Screening` (same as Tool 16).

### Reason — VERIFIED_LIVE (inherited)
- The only differentiator vs Tool 16 is `hypothesis_path` = a **ligand-based** `.posp`, which
  only Pharmacophore Hypothesis - Ligand (Tool 9) can produce — and that tool's result artifacts
  404 (`NoSuchKey`) on the platform (2/2 runs). With no ligand posp obtainable, this variant is
  unrunnable end-to-end today.
- Deliberately NOT submitted: schema is identical to the verified Tool 16 run, so a 200-credit
  submission could only re-prove the receptor-path behavior. Revisit after Tool 9's artifact bug
  is fixed.

### Sci Execution Instructions
1. Treat receptor-based pharmacophore screening (Tool 16) as the working path.
2. If a user supplies their own ligand `.posp` cloud path, the Tool 16 payload contract applies
   verbatim (`hypothesis_path`, `library`, `min_features`).

---



## Tool 27 — Molecular Docking - vina (`Vina_basic_docking`) — BLOCKED (worker bug)

### Identity
- Route: `/v4/DModule/basic_docking` · job_name `Vina_basic_docking`

### Input Contract (yup-verified)
```json
{
  "target_name":      "6FMC",
  "processed_pdb":    "<cloud path: protein PDB>",
  "center_x":         "27.436",     // ALL numerics are STRINGS (yup rejects numbers)
  "center_y":         "…", "center_z": "…",
  "max_radius_size":  "25",
  "exhaustivness":    "8",          // platform's spelling of "exhaustiveness"
  "upload_sdf":       "false",      // STRING boolean
  "smiles":           "<cloud path to ligand CSV with columns SMILES,NAMES>"
}
```
- `smiles` takes a **CSV cloud path**, not a SMILES string (proved by attempt 5 below).
- The ligand CSV **must** contain a `NAMES` column (proved by attempt 1's worker error).

### Submission Findings — 5 reasoned attempts across 7 versions
| # | protein | ligand field | numeric fields | outcome |
|---|---------|--------------|---------------|---------|
| 1 | BSP/fpocket processed PDB | SMILES-only CSV | strings | accepted → worker: `Missing required column(s): NAMES` |
| 2 | BSP/fpocket processed PDB | SMILES+NAMES CSV | strings | accepted → worker: `Failed to generate output` |
| 3 | BSP/fpocket processed PDB | SMILES+NAMES CSV | **numbers** | yup 422 — strings required |
| 4 | 6FMC stripped PDB | SMILES+NAMES CSV (`upload_sdf:"true"`) | strings | accepted → worker: `Failed to generate output` |
| 5 | 6FMC stripped PDB | **literal SMILES string** | strings | 500 `File not found or unreadable (404)` → proves CSV-path semantics |
| 6-7 | pristine RCSB 6FMC PDB (1,441 ATOM) | SMILES+NAMES CSV (`upload_sdf:"false"`) | strings | accepted → worker: `Failed to generate output` |

### Root-Cause Assessment — VERIFIED_LIVE
- Schema is fully solved (every field type and file format confirmed via yup + worker errors).
- The worker crashes after input parsing on every protein source (fpocket output, hand-stripped
  6FMC, pristine RCSB 6FMC) and both `upload_sdf` settings — always the same generic
  `Failed to generate output`. This is a worker-side defect, not an input problem.

### Sci Execution Instructions
1. Do not burn credits on this tool until the worker is fixed; use Diffdock (Tool 28) for
   protein–ligand docking in the interim.
2. If a run is required anyway: use the payload contract above with strings everywhere,
   a `SMILES,NAMES` ligand CSV, and a pristine RCSB PDB; expect `failed`.

### Verified Quirks
- Every numeric field is a string at the yup layer (numbers → 422).
- Field name misspelled `exhaustivness`; booleans are strings (`"false"`).
- `smiles` = ligand-CSV cloud path; missing `NAMES` column is a worker-stage error, not yup.

---



## Tool 28 — Molecular Docking - diffdock (`Diffdock`) — VERIFIED

### Identity
- Route: `/v4/3DModule/diffdock` · job_name `Diffdock`
- 1st-choice docking tool on the platform (vina worker is broken — see Tool 27).

### Input Contract — VERIFIED_LIVE (accepted first try)
```json
{
  "processed_pdb": "<cloud path to protein PDB — BSP fpocket output works>",
  "input_csv":     "<cloud path to ligand CSV (SMILES column; bpp output reused fine)>",
  "upload_sdf":    "false"   // string
}
```
- Ligand field is **`input_csv`** here — NOT `smiles` as in vina. No NAMES column required.

### Result Contract — VERIFIED_LIVE
- `status: "Success"`, `OutputData["outputFilePath[0..1]"]`: `diffdock_res.json` (UI payload) +
  `user_download.csv` (the result table). ~16 min for 5 ligands.

### Output Analysis — VERIFIED_LIVE
- `user_download.csv`: one row per pose = **10 poses (Rank 0–9) per ligand** — 5 ligands → 50 rows.
- Columns: full ADMET panel + 6 descriptors (same family as Property Prediction/Toxicity output,
  replicated on every pose row) + `Ligand_no`, `Rank`, `Confidence`, `Interactions`.
- `Confidence` is **negative-scaled** (−0.16 … −6.05 observed): closer to 0 = better;
  Rank 0 is always the top pose per ligand.
- `Interactions`: Python-repr list (single quotes — `ast.literal_eval`, NOT `json.loads`) of
  `[residue.chain, type, distance Å]`, e.g. `[['ASN44.A', 'VdWContact', 2.8]]`.
  Only `VdWContact` observed in this run; 23/50 pose rows had ≥1 interaction, and the
  rank-0 poses were mostly interaction-free (annotator fires on closer/lower-ranked poses).
- **`Ligand_no` is NOT the input row index** (completion order: 0,1,4,2,3 observed).
  Always map ligands by SMILES, never by Ligand_no.
- `diffdock_res.json`: all 50 pose entries keyed "0"–"49" (string keys), each = CSV row plus
  `node`/`edge`/`buttons` — vis.js graph snippets for the platform's interaction diagram.
  Machine consumers should use the CSV; the JSON is UI-render payload.
- No docked pose PDB/SDF is returned when `upload_sdf: "false"` — only scores/interactions.
  Set `"true"` if 3D structures are needed (untested).

### Downstream Compatibility — VERIFIED_LIVE
- ADMET columns identical to Property Prediction/Toxicity/QSPR outputs → ranking pipelines work
  unchanged; add Confidence + interaction-count as docking axes.

### Sci Execution Instructions
1. Provide a processed protein PDB (fpocket output path is proven) + ligand CSV; `"upload_sdf":
   "false"`; ~1 credit-class run, ~15 min for a handful of ligands (scales with ligand count).
2. Parse `Interactions` with `ast.literal_eval`; ignore `Ligand_no` for identity.
3. Report per ligand: best (rank-0) confidence + the residue contacts across poses.
4. Docked-structure files require `upload_sdf: "true"` — request only when the user needs PDBs.

### Verified Quirks
- Field asymmetry vs vina (`input_csv` vs `smiles`); no NAMES requirement.
- Negative confidence scale; rank 0 = best; Ligand_no ≠ input order.
- Interactions are Python-repr, not JSON; only VdWContact type observed in this run.

---



## Tool 30 — MDS - gromacs (`MDS_Gromacs`) — BLOCKED (worker bug)

### Identity
- Route: `/v4/mds/gromacs` · job_name `MDS_Gromacs` · task `gromacs`

### Input Contract — VERIFIED_LIVE (yup layer)
```json
{
  "Protein_PDB_file": "<cloud path, protein PDB>",
  "Ligand_PDB_file":  "<cloud path, ligand PDB>",   // REQUIRED (v1 400 without it)
  "Time": 1, "xtc_file": "YES",                     // trajectory on/off
  "temparature": 298, "pressure": 1,                // NOTE the typo 'temparature'
  "water_type": "TIP3P", "force_field": "amber",    // enums observed: amber | charmm
  "snaptime": 10                                    // snapshot interval
}
```
- Discovery: v1 (no ligand) → 400 `Ligand_PDB_file` required; adding the DUE ligand extract
  (40 HETATM from 6FMC, `line[17:20]=='DUE'`) was accepted.

### Submission Findings — 3 attempts
| v | change | outcome |
|---|--------|---------|
| 1 | no `Ligand_PDB_file` | 400 (yup) — required-field discovery |
| 2 | + DUE ligand, `snaptime: 10`, `Time: 1` | accepted (30 credits) → worker `Failed to generate output` |
| 3 | `snaptime: 1` (zero-frame-trajectory hypothesis) | accepted (30 credits) → same worker failure |

### Root-Cause Assessment — VERIFIED_LIVE
- The snaptime hypothesis was falsified by v3; the failure is independent of snapshot cadence.
- Remaining untested hypothesis (parked at user request): ligand parameterization — DUE is an
  exotic glycan-class 40-atom fragment and amber-family ligand-topology generation is a known
  fragile step; a drug-like ligand (e.g. RDKit-generated aspirin PDB) would isolate it.
- Same generic `Failed to generate output` signature as the Vina and Molecule Enumeration
  worker bugs. 60 credits burned across the two accepted runs.

### Sci Execution Instructions
1. Use MDS-openMM (Tool 29) for platform MD; treat this tool as unavailable until fixed.
2. If probing a fix: drug-like ligand + `force_field:"charmm"` are the untried variables.

### Verified Quirks
- `temparature` typo is the real field name; `force_field` enum `amber|charmm`.
- Ligand PDB mandatory even for apo-style runs (untested whether an empty/dummy file passes yup).

---



## MDS — OpenMM (`MDS_openMM`) — PARKED

### Status
- The live verification matrix records this job as accepted and pending server-side; its document ID is retained for on-demand fetching.
- No terminal output schema was available during the verification campaign.
- Do not submit or claim a result until a complete input contract and terminal output are verified.

### Known identity
- Job name: `MDS_openMM`
- The molecular-dynamics module is currently removed from the active module registry, so this entry is documentation-only until the route is re-enabled.

## Molecular Docking mode matrix (active scope)

Molecular Docking is one user-facing tool with Vina and DiffDock modes. The
Vina feature choices are mutually exclusive: no feature selects basic docking;
Flexible docking and Score only select their corresponding Vina routes.

| User mode | Exact job name | Status | Required contract |
|---|---|---|---|
| Vina basic | `Vina_basic_docking` | Schema verified; worker blocked | `target_name`, `processed_pdb`, `center_x`, `center_y`, `center_z`, `max_radius_size`, `exhaustivness`, `upload_sdf`, and ligand CSV cloud path in `smiles` |
| Vina flexible | Not live-confirmed | Do not guess or submit | Requires the common receptor/search-box fields; `flexible_residues` is optional; exact submit job name remains unverified |
| Vina score-only | `Vina_Score_only_docking` | Submission verified; terminal output unverified | Common receptor/search-box fields plus `sdf_file` and string `upload_sdf` |
| DiffDock | `Diffdock` | Verified end-to-end | `processed_pdb`, `input_csv`, and string `upload_sdf` |

For Vina, all numeric search-box fields are strings, the field spelling is
`exhaustivness`, and the ligand CSV must contain `SMILES,NAMES`. For DiffDock,
the ligand field is `input_csv`, `NAMES` is not required, and the verified
result is `user_download.csv` with pose/ranking fields. Identify ligands by
`SMILES`, not `Ligand_no`.

Do not submit Vina basic or Gromacs while their worker failures remain active.
DiffDock is the currently verified docking path. Do not claim Vina flexible or
score-only terminal output until its artifacts have been fetched and inspected.
