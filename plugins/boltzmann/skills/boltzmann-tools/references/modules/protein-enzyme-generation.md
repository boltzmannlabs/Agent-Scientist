# Enzyme Generation

Domain: Protein Engineering

This module was selected by the server. Use only the exact contracts below.

## 5. Function-Based Enzyme Generation

| Field | Value |
|-------|-------|
| **job_name** | `Function_Based_Enzyme_Generation` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `label` | string | yes | EC number (e.g., `"1.1.1.1"`, `"3.1.1.2"`) |
| `n_samples` | int | yes | Number of sequences |
| `file_format` | string | no | `"csv"` (default) |

**Output key:** `result["OutputData"]["OutputfilePath"]["download_link"]`
**Note:** Output key is `OutputfilePath` — capital O, capital P. Different from most tools.

**CSV columns:** `Sequence_ID, Sequence, Length, Molecular_Weight, PI, Hydrophobic_Count, Acidic_count, Basic_count, Polar_Count, Others_Count, A..Y`

---

## 6. Genzyme Generation

Generate candidate enzyme structures conditioned on substrate and product SMILES.

| Field | Value |
|---|---|
| **job_name** | `Genzyme_Generation` |
| **backend task/collection** | `genzyme` |
| **validation status** | **Submission verified (HTTP 200); terminal result not yet verified** |
| **observed submission cost/time** | 10 credits; 10 minutes for 2 requested structures in the accepted submission response |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `input_substrate` | string | yes | Substrate SMILES |
| `input_product` | string | yes | Product SMILES |
| `num_structures` | integer | yes | Number of enzyme structures to generate; product validation range is 1–100000 |
| `complex_generation` | string | no | Accepted as `"True"` by the verified submission, but absent from the product-sheet schema; omit unless the user explicitly requests it |
| `top_k` | integer | no | Accepted as `2` by the verified submission, but absent from the product-sheet schema; omit unless the user explicitly requests it |

The three core fields are compulsory. Do not rename them to the UI sample keys
`substrate`, `product`, or `structures`.

```python
job_name = "Genzyme_Generation"
experiment_name = "Genzyme generation"
experiment_data = {
    "input_substrate": "CC(=O)Oc1ccc([N+](=O)[O-])cc1",
    "input_product": "Oc1ccc([N+](=O)[O-])cc1",
    "num_structures": 2,
}
```

When the user explicitly requests complex generation and a ranked subset, the
following extended shape is submission-verified:

```python
experiment_data = {
    "input_substrate": substrate_smiles,
    "input_product": product_smiles,
    "num_structures": 2,
    "complex_generation": "True",
    "top_k": 2,
}
```

### Output instructions

The Boltzyme product source describes the terminal data under
`OutputData.datainfo`, including `time_taken`, `outputFilePath`, and
`model_name: "genzyme"`. Pass the submission document ID and the exact
`Genzyme_Generation` job name to `fetch_status`, preserve the complete terminal
payload, and download only a returned signed URL. Verify the generated artifact
count before reporting completion.

The observed HTTP 200 response proves that the payload was accepted and queued;
it does not prove scientific completion or the terminal artifact shape.

### Evidence

- The all-experiments CSV confirms the exact job name, compulsory core fields,
  and the `num_structures` range.
- The Boltzyme product CSV confirms backend task `genzyme`, model purpose,
  output metadata shape, ten-credit cost, and estimated runtime family.
- The accepted submission in `testing_tools.py` confirms the extended payload
  with `complex_generation: "True"` and `top_k: 2` returns HTTP 200.

---
