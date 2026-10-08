# Sci CLI Reference

Live sources when anything looks stale: `sci --help`, `sci <command> --help`,
website/docs/reference/cli-commands.md

### Global Flags

```
sci [flags] [command]        (no subcommand = interactive chat)

  --version, -V             Show version
  -z, --oneshot PROMPT      One-shot: print ONLY the final response (for scripts/pipes)
  -m MODEL  --provider P    Model/provider override for this invocation
  -t, --toolsets LIST       Comma-separated toolsets for this invocation
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --tui / --cli             Force the Ink TUI / classic REPL
  --ignore-rules            Skip AGENTS.md/SOUL.md/memory/skill injection
  --safe-mode               Disable ALL customizations (troubleshooting)
  --pass-session-id         Include session ID in system prompt
```

### Chat

```
sci chat [flags]
  -q, --query TEXT          Single query, non-interactive
  --image PATH              Attach a local image to a single query
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --max-turns N             Cap tool-calling iterations
  --source TAG              Session source tag (default: cli)
```
(plus the global flags above)

### Configuration

```
sci setup [section]      Wizard (model|tts|terminal|gateway|tools|agent)
sci model                Interactive model/provider picker
sci fallback [add|remove|list]  Fallback provider chain
sci config [show|edit|get|set|unset|path|env-path|check|migrate]
sci login / logout       OAuth sign-in / clear stored auth
sci doctor [--fix]       Check dependencies and config
sci status [--all]       Component status
```

### Tools & Skills

```
sci tools [list|enable NAME|disable NAME]   Per-platform toolsets (curses UI with no args)

sci skills list|browse|search QUERY|inspect ID
sci skills install ID    Hub identifier OR a direct https://…/SKILL.md URL
sci skills config        Enable/disable skills per platform
sci skills check|update|uninstall|publish PATH
sci skills tap add REPO  Add a GitHub repo as a skill source
sci bundles              Skill bundles (one /<name> alias loads several skills)
```

### MCP Servers

```
sci mcp add NAME (--url or --command) | remove | list | test NAME
sci mcp catalog | install NAME     Curated catalog install
sci mcp configure NAME             Toggle tool selection
sci mcp serve                      Run Sci as an MCP server
```
Details (transport, tool discovery, catalog): `references/native-mcp.md`.

### Gateway (Messaging Platforms)

```
sci gateway run|install|start|stop|restart|status|setup
```

20+ platforms: Telegram, Discord, Slack, WhatsApp (Baileys + Business Cloud API), iMessage (Photon — `sci photon setup`), Signal, Email, SMS, Matrix, Mattermost, Teams, LINE, SimpleX, ntfy, Google Chat, Home Assistant, DingTalk, Feishu, WeCom, Weixin, API Server, Webhooks. Open WebUI connects via the API Server adapter. Most adapters ship under `plugins/platforms/`.
Docs: README.md

### Sessions

```
sci sessions list|browse|rename ID TITLE|delete ID|export OUT|prune|stats
```

### Cron / Webhooks

```
sci cron list|create SCHED|edit ID|pause|resume|run ID|remove|status
    Schedules: '30m', 'every 2h', '0 9 * * *', ISO timestamp
sci webhook subscribe NAME|list|remove NAME|test NAME
```
Webhook payloads/routes: `references/webhooks.md`.

### Profiles

```
sci profile list|create NAME (--clone|--clone-all|--clone-from)|use|show|delete
sci profile rename A B | alias NAME | export NAME | import FILE
sci profile migrate-identity A B   Retry a completed rename's session/routing identity migration
```

### Credentials & Pools

```
sci auth                 Interactive credential manager
sci auth add [PROVIDER]  Add OAuth or API-key credential (nous, openai-codex, qwen-oauth, …)
sci auth list|remove P IDX|reset PROVIDER|status
```
Multiple credentials per provider form a pool that rotates automatically and skips exhausted keys.

### Other

```
sci desktop / gui        Native desktop app
sci dashboard            Web admin panel + embedded chat (--stop / --status)
sci proxy                OpenAI-compatible local proxy backed by an OAuth provider
# Provider login: sci model
sci kanban <verb>        Multi-agent work-queue board
sci project              Named multi-folder workspaces
sci skin list|use|set    Switch/tweak skins (see references/themes.md)
sci pets <verb>          Pet mascots (see references/petdex.md)
sci memory setup|status|off|reset   Memory provider
sci secrets bitwarden|onepassword   External secret stores
sci moa                  Mixture-of-Agents slots
sci hooks / security / backup / import / checkpoints / console
sci logs [-f] [errors]   View agent/error logs
sci send                 One-off message through a gateway platform
sci pairing / plugins / insights / journey / computer-use
sci acp                  ACP server (IDE integration)
sci completion bash|zsh|fish
sci update / uninstall / claw migrate
```

Plugin- and provider-supplied subcommands (e.g. `sci photon setup`) only appear once their plugin is installed/active.

### Where to Find Things

| Looking for... | Location |
|---|---|
| Config options | `sci config edit` · [Configuration docs](website/docs/user-guide/configuration.md) |
| Tools / toolsets | `sci tools list` · [Tools reference](website/docs/reference/tools-reference.md) |
| Skills catalog | `sci skills browse` · [Skills catalog](website/docs/reference/skills-catalog.md) |
| Provider setup | `sci model` · [Providers guide](website/docs/integrations/providers.md) |
| Env variables | `sci config env-path` · [Env vars reference](website/docs/reference/environment-variables.md) |
| Gateway logs | `~/.sci/logs/gateway.log` (or `sci logs`) |
| Sessions | `sci sessions browse` (reads state.db) |
