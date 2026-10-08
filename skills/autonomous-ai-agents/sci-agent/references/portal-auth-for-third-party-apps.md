# Provider authentication boundaries

SCI uses the model provider selected with `sci model`. Authenticate through
that provider's supported flow. A model login is not authorization to unrelated
scientific services; Boltzmann access requires `/Add_boltz` in the active profile.

Do not copy browser tokens or local credential-store contents into another
application. Do not infer that another application's subscription accepts SCI
requests. Inspect the installed provider adapter and local configuration first.
If independent provider documentation is needed, consult that provider only for
its own API, not as the operating manual for SCI.

For local setup instructions, use the SCI checkout's `README.md` and
`references/providers-and-models.md` in this skill. Do not invent a SCI release
or documentation URL before the project publishes one.
