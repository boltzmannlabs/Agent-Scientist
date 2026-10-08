# Database histology image retrieval

## Human Protein Atlas IHC

1. Resolve the target gene's Ensembl identifier and open the corresponding cancer collection: `https://www.proteinatlas.org/{EnsemblID}-{gene}/cancer/{cancer}`. URL-encode the cancer label; the renal-cancer collection uses `renal%2Bcancer`. Check the actual tissue and diagnosis annotations before selecting images.
2. Parse full-resolution image anchors on `images.proteinatlas.org` and the nested thumbnail's `title` attribute. The title contains patient ID, tissue, diagnosis, antibody staining, intensity, quantity, and location. Strip markup and decode HTML entities without losing the field boundaries. Associate each image with its antibody column; do not treat the numeric image-directory ID alone as a verified antibody accession.
3. Select by requested criteria. If strong positivity is wanted, use the database's High/Strong annotations rather than assuming that high resolution means high expression. Disclose deliberate positive-case selection; it is not representative sampling.
4. Download the anchor's original JPEG, not `_thumb.jpg` or `selected_60x60.jpg`. Preserve the returned URL rather than inventing a higher-resolution suffix. Use bounded parallel downloads for independent images.
5. Verify each downloaded file with Pillow: read `Image.open(path).size` and call `verify()`. Report measured pixel dimensions, not an unsupported magnification, DPI, or whole-slide claim. If describing visible morphology or visual quality, also inspect the image; decoding alone verifies neither.
6. Save a JSON/CSV manifest containing collection URL, original image URL, local path, dimensions, antibody, patient ID, and source annotations. For complete collections, deduplicate and count programmatically and distinguish images from unique patients; paired cores from one patient are not independent cases.
7. Return the absolute output folder, selected filenames, dimensions, and relevant annotations. Preserve the source diagnosis: an annotation such as adenocarcinoma NOS does not establish clear-cell RCC or another renal subtype. Check the database's current reuse terms before promising publication permissions.

Use a positive example plus a clearly labeled lower-staining comparison when helpful, but never describe specimens stained with different antibodies as a controlled expression comparison without additional validation.
