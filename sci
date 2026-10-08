#!/usr/bin/env python3
"""
Sci Agent CLI launcher.

This wrapper should behave like the installed `sci` command, including
subcommands such as `gateway`, `cron`, and `doctor`.
"""

if __name__ == "__main__":
    from sci_cli.main import main
    main()
