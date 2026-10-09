# Durable Boltzmann tool-log lookup

This protocol is for `platform_tools` only. It does not alter Omics routing,
Omics checkpoints, conversation memory, or the existing workflow logger.

## Two status sources

1. `boltzmann_status` (the `fetch_status` helper) polls the live Boltzmann
   result endpoint. Its `(job_name, doc_id)` pair and returned terminal status
   are authoritative for the current state of the submitted job.
2. `boltzmann_fetch_tool_log` reads one durable MongoDB document to explain a
   terminal result. It is useful for the platform's recorded error/message,
   output metadata, timing, billing, and other persisted details. It is not a
   replacement for live polling and it never submits, updates, searches, or
   retries a job.

When `boltzmann_status` receives a terminal `failed` or `error` response, the
plugin automatically performs this exact lookup and adds the result under
`durable_log`. The model must summarize the recorded cause from that object;
it must not stop at a generic message such as “Failed to generate output”.

## Endpoint contract

The documented operation is `POST /v5/tools/mongodb_fetcher`. The API's
OpenAPI contract (operation `read_mongodb_v5_tools_mongodb_fetcher_post`)
requires exactly these JSON fields:

```json
{
  "collection": "<exact collection name>",
  "experiment_id": "<exact document/experiment id>"
}
```

`/v4/tools/mongodb_fetcher` is retained as a compatibility route. The adapter
uses v5 by default and allows an operator-provided
`BOLTZMANN_MONGODB_FETCHER_URL` override without changing skill instructions.

## Safe invocation

Use the registered `boltzmann_fetch_tool_log` tool only after the current
conversation contains a successful submit/workflow record with the exact
collection and document ID. Resolve the collection from
`references/tool-collection-inventory.csv` only when its mapping is non-empty
and unambiguous. Resolve the ID from the immediate submit response or the
current conversation's workflow record. Do not infer either value from
arbitrary user text.

If the selected module gives a durable collection that differs from the
submission job name, use that exact collection (for example, `equidock` for
Vina score-only) in the lookup. The submission job name must still be used
for live `boltzmann_status` polling.

The runtime may pass the current conversation ID, request ID, and bearer
credential as hidden tool context. Never put credentials, raw Mongo documents,
or signed download URLs in user-facing text; the adapter redacts credentials
and bounds large documents before returning them to the model.

## Reconciliation and failure semantics

- Live `fetch_status` wins when its state disagrees with a durable document.
- A durable document enriches the explanation; it does not turn a missing
  document into a scientific failure.
- `not_found` means no document was returned for that exact pair.
- `unreachable` or `unauthorized` means the lookup could not be checked;
  report that limitation and preserve the live status.
- `malformed`, `error`, or `invalid_request` must be summarized as a lookup
  problem and must not be presented as a fabricated tool result.

The lookup is intentionally read-only and bounded to one exact pair per call.
