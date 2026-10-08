# biotoolsSchema integration

## Product identity and scope

biotoolsSchema is a formal metadata description model, not a sequence-analysis application or runnable upstream CLI. Expose local schema inspection and validation through a native Sci plugin rather than pretending that cloning the repository installs an executable. Keep metadata conformance distinct from registry API acceptance or biological/scientific validation.

## Source selection and provenance

Use the publisher's `stable/biotools.xsd` for stable XML validation, not `biotools_dev.xsd` or the historical reverse-engineering XSD in jsonschema/assets. The repository's `jsonschema/biotoolsj.json` declares JSON Schema Draft-04 and a top-level array of tool objects. Record the source commit and SHA-256 of both schema files; fail if checked bytes change unexpectedly. Do not assume the JSON snapshot and stable XML constraints are identical.

The verified snapshot c31233af4e136f985e83a58f3ca11b02628348f9 has a duplicate EPL-2.0 entry in definitions/tool/properties/license/enum. Draft-04 meta-schema checking rejects the duplicate. Preserve the original source and deduplicate only that identical enum member in memory, then meta-validate the effective schema. Disclose the correction and distinguish original schema validity from effective schema validity. Do not generalize this into silently repairing future schema defects. The same snapshot constrains homepage only to string in JSON; do not invent a URL regex that the schema lacks.

## Plugin and isolation

Use a profile-local directory plugin with a standard-library adapter and an isolated validator interpreter containing jsonschema and lxml. Do not inject third-party packages into the Sci-managed runtime. Check native `ctx.register_tool`, manifest parsing and registration with `sci plugins doctor PATH --ci`; enable through `sci plugins enable NAME --no-allow-tool-override`.

Tools exposed by the verified local integration are biotools_schema_info, biotools_schema_validate and biotools_schema_fields. Validate accepts exactly one of a local JSON/XML file or inline JSON object/array. Report a single-object wrapper explicitly instead of modifying fields or silently flattening API response envelopes. Success indicates that validation ran; valid indicates conformance. Include exact detected error totals, capped error lists and truncation flags. Dotted field inspection should descend through array items and local references while retaining human-readable annotations. Draft-04 ignores validation siblings of $ref; do not treat descriptive annotations as added validation constraints.

Reject JSON duplicate keys and nonfinite numeric values. For automatic file-format sniffing, recognize UTF-8 BOMs and UTF-16 signatures even when the filename has no XML extension; decoding a sniffing copy with json.detect_encoding and errors=replace works in the pinned Python 3.12 interpreter, while the parser receives unchanged original bytes. Test Unicode-encoded JSON too so BOM detection does not misclassify every BOM-bearing file as XML. Disable XML network access, DTD loading and entity expansion; reject any document with a doctype after parsing so UTF-16 declarations are also detected. Bound file/request bytes, record counts, returned errors and subprocess duration. No credential fields, registry uploads or implicit remote schema fetches belong in this interface.

## Fresh-runtime verification

Sci may use a PM-selected runtime that is different from shell python or an old venv. Invoke tests through the installed launcher. `sci --run-module unittest discover -s ABSOLUTE_TEST_DIRECTORY -p verify_registration.py -v` is a working pattern: unittest adds the test directory and uses Sci's bootstrapped interpreter. `sci --run-module runpy ABSOLUTE_SCRIPT.py` is not a script runner; runpy interprets the path as a module name and fails.

Resolve configured CLI toolsets through `_get_platform_tools`, retrieve model_tools.get_tool_definitions, assert expected native names, and exercise actual registry.dispatch handlers. Verify conforming JSON/XML fixtures, nonconforming metadata and nested field lookup. Store the machine-readable proof under plugin_data_dir, not a hardcoded profile path. New tool schemas are deferred to the next conversation; enabling a plugin does not mutate the current session's prompt cache.
