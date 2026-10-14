"""Profile-local conversation picker and safe session handoff."""

from sci_cli.skill_add import WizardUI, Cancelled


def flush_before_switch(cli):
    """A failed flush must leave the user in their current conversation."""
    if getattr(cli, "_agent_running", False) or getattr(cli, "_science_running_worker", None):
        raise ValueError("Finish or explicitly cancel the running work before switching.")
    agent = getattr(cli, "agent", None)
    if agent and getattr(cli, "conversation_history", None):
        agent._flush_messages_to_session_db(cli.conversation_history,
                                            conversation_history=cli.conversation_history)


def pick_session(cli, ui=None):
    from sci_cli.session_listing import query_session_listing
    from sci_cli.timefmt import relative_time
    from sci_cli.native_profile_session import profile_label
    from sci_state_sessions import INTERNAL_LISTING_SOURCES
    ui = ui or WizardUI(cli)
    if not getattr(cli, "_session_db", None):
        ui.show("Saved conversation store unavailable; current session unchanged.")
        return None
    query, page = "", 0
    try:
        while True:
            rows = query_session_listing(cli._session_db, source="cli", include_all_sources=False,
                current_session_id=cli.session_id, include_current_session=True, include_unnamed=True,
                search_query=query, limit=(page + 1) * 8 + 1, exclude_sources=list(INTERNAL_LISTING_SOURCES))
            visible = rows[page * 8:(page + 1) * 8]
            labels = {}
            for row in visible:
                name = row.get("title") or "Untitled"
                label = (f"{name[:55]} | {relative_time(row.get('last_active'), session_id=row['id'])} | "
                         f"{row.get('message_count', 0)} messages | {row['id']}" +
                         (" [active]" if row.get("is_current_session") else ""))
                labels[label] = row["id"]
            controls = [*labels, "Search", "Cancel"]
            if len(rows) > (page + 1) * 8:
                controls.insert(-1, "Next page")
            if page:
                controls.insert(-1, "Previous page")
            choice = ui.choose(f"Conversations [{profile_label()}] — page {page + 1}; search title or ID", controls)
            if choice in labels:
                return labels[choice]
            if choice == "Search":
                query, page = ui.ask("Search conversation title or ID:"), 0
            else:
                page += 1 if choice == "Next page" else -1
    except (Cancelled, KeyboardInterrupt, EOFError):
        ui.show("Conversation selection cancelled; current session unchanged.")
        return None
