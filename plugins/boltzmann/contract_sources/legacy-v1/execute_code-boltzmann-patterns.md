---
name: boltzmann-api-key-transport
---

# Boltzmann API-key transport

This installation uses the Sci `boltzmann` plugin for all platform
execution. Do not call Boltzmann endpoints from `execute_code`, terminal,
`curl`, or an improvised script.

## Authentication

- Credential: `BOLTZMANN_API_KEY` in the active profile's `.env`.
- Authenticated API header: `Authorization: Bearer <API_KEY>`.
- Bearer is the transport format; the credential remains `BOLTZMANN_API_KEY`.
- Startup validation: authenticated `GET /api/get-projects` must succeed.
- Submission endpoint:
  `https://nodeapis.boltzmann.co/api/submit-job`.
- Submission body:

```json
{
  "job_name": "<exact job_name>",
  "experimentData": {"<documented field>": "<validated value>"},
  "experimentName": "<user-confirmed name>"
}
```

The plugin owns credentials and transport. The agent supplies only
`job_name`, `experiment_data`, and `experiment_name` to `boltzmann_submit`.
It must retain the returned `doc_id` and poll that same job with
`boltzmann_status`.

## Failure handling

- Missing key: Boltzmann tools are unavailable.
- Invalid key or failed startup authentication: tools are unavailable.
- HTTP 401/403: report the authentication error; never expose the key.
- Connection timeout before the request is sent: one retry is allowed.
- Read timeout after submission: the job may exist; do not resubmit.
- Poll/status failure: never create a replacement job.

Signed output URLs are short-lived and must be passed only to
`boltzmann_download`. Never print or persist them in user-visible text.
