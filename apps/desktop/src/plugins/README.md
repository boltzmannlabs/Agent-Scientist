# Bundled plugins

Drop a `<name>/plugin.{ts,tsx}` here that default-exports a `SciPlugin` and
it registers automatically at boot (vite glob in `../contrib/plugins.ts`), with
the same inventory + live enable/disable contract as runtime plugins.

Keep this tree for real shipped plugins (and the small authoring fixtures that
dogfood the SDK). One-off demos that rebuild a core chrome piece 1:1 do not
belong here — they double the UI and confuse Capabilities ▸ Plugins. Keep those
in a separate, explicitly selected plugin repository. Use the local SDK and
bundled plugins as authoring examples.

User- and agent-authored plugins load at runtime from
`$SCI_HOME/desktop-plugins/<name>/plugin.js` (the disk door) — see the
`sci-desktop-plugins` skill.
