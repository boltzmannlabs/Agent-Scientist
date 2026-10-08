import { contextBridge, ipcRenderer, webFrame, webUtils } from 'electron'

import type { DesktopProfileRoute } from './desktop-profile'
import type { HudModifierApi, HudModifierStatus } from './hud-modifier-types'
import { customWindowControlsEnabled } from './window-controls'

// Which translucency the OS can back. Asked synchronously because the renderer
// needs it before its first paint, and answered by main because deciding it
// needs `os.release()` — a sandboxed preload may only require electron, events,
// timers and url, so importing node:os here throws before contextBridge runs
// and takes the ENTIRE bridge down with it (window.sciDesktop undefined =>
// "Desktop IPC bridge is unavailable"). No reply means no glass, which degrades
// to an ordinary opaque window rather than a page thinned over nothing.
const translucencySupport = ipcRenderer.sendSync('sci:translucency:support')
const hudWindowing = ipcRenderer.sendSync('sci:hud:windowing')
const hudNativeDrag = hudWindowing?.nativeDrag === true

const launchFlags: { localModels?: boolean; guestOnboarding?: boolean } | undefined =
  ipcRenderer.sendSync('sci:feature-flags')

// Local, sanitized skin payload for the first renderer theme paint. This does
// not wait on `gateway.ready`, so an unreachable remote primary cannot force
// the built-in palette over the skin configured on this machine.
const localSkin = ipcRenderer.sendSync('sci:skin:local')

contextBridge.exposeInMainWorld('sciDesktop', {
  glassSupported: translucencySupport?.glass === true,
  translucencySupported: translucencySupport?.translucency === true,
  // Launch-flag fact: the app was started with --local, so the renderer may
  // show the local-models surfaces. Static for the window's lifetime.
  localModelsEnabled: launchFlags?.localModels === true,
  // Launch-flag fact: the Nous free tier is on for this launch
  // (SCI_GUEST_ONBOARDING=1 or --guest-onboarding). Read-only; the same
  // decision is stamped onto every backend the app spawns.
  guestOnboardingEnabled: launchFlags?.guestOnboarding === true,
  localSkin: localSkin && typeof localSkin === 'object' ? localSkin : null,
  getConnection: (profile, opts) => ipcRenderer.invoke('sci:connection', profile, opts),
  // Registry-scoped backend resolution: { connectionId, profile } → descriptor.
  getConnectionFor: payload => ipcRenderer.invoke('sci:connection:for', payload),
  getProfileRoutes: profiles => ipcRenderer.invoke('sci:plugin-profile-routes', profiles),
  revalidateConnection: () => ipcRenderer.invoke('sci:connection:revalidate'),
  touchBackend: (profile, options) => ipcRenderer.invoke('sci:backend:touch', profile, options),
  getPoolLimits: () => ipcRenderer.invoke('sci:pool-limits:get'),
  setPoolLimits: limits => ipcRenderer.invoke('sci:pool-limits:set', limits),
  getGatewayWsUrl: profile => ipcRenderer.invoke('sci:gateway:ws-url', profile),
  // Registry-scoped fresh WS URL: { connectionId, profile } → result shape of
  // getGatewayWsUrl, minted against that connection's backend.
  getGatewayWsUrlFor: payload => ipcRenderer.invoke('sci:gateway:ws-url-for', payload),
  // Union agent roster across every registered connection.
  getAgentRoster: () => ipcRenderer.invoke('sci:agents:roster'),
  openSessionWindow: (sessionId, opts) => ipcRenderer.invoke('sci:window:openSession', sessionId, opts),
  openSessionInTerminal: (sessionId, opts) => ipcRenderer.invoke('sci:window:openInTerminal', sessionId, opts),
  openWindow: (options?: DesktopProfileRoute) => ipcRenderer.invoke('sci:window:openInstance', options),
  openBrowserWindow: tabId => ipcRenderer.invoke('sci:window:openBrowser', tabId),
  onBrowserPopoutClosed: callback => {
    const listener = (_event, tabId) => callback(tabId)
    ipcRenderer.on('sci:browser-popout:closed', listener)

    return () => ipcRenderer.removeListener('sci:browser-popout:closed', listener)
  },
  claimAmbientCue: key => ipcRenderer.invoke('sci:ambient:claim', key),
  windowControls: {
    custom: customWindowControlsEnabled(),
    minimize: () => ipcRenderer.send('sci:window-control', 'minimize'),
    toggleMaximize: () => ipcRenderer.send('sci:window-control', 'toggle-maximize'),
    close: () => ipcRenderer.send('sci:window-control', 'close')
  },
  wakeIndicator: {
    getState: () => ipcRenderer.invoke('sci:wake-indicator:get'),
    setState: state => ipcRenderer.send('sci:wake-indicator:set', state),
    onState: callback => {
      const listener = (_event, state) => callback(state)
      ipcRenderer.on('sci:wake-indicator:state', listener)

      return () => ipcRenderer.removeListener('sci:wake-indicator:state', listener)
    }
  },
  chatOnboarding: {
    grow: request => ipcRenderer.send('sci:chat-onboarding:grow', request),
    soloBoot: () => ipcRenderer.send('sci:chat-onboarding:solo-boot')
  },
  petOverlay: {
    // Main renderer → main process: window lifecycle + drag. `request` is
    // `{ bounds, screen }`; resolves with the screen bounds it actually used.
    open: request => ipcRenderer.invoke('sci:pet-overlay:open', request),
    close: () => ipcRenderer.invoke('sci:pet-overlay:close'),
    setBounds: bounds => ipcRenderer.send('sci:pet-overlay:set-bounds', bounds),
    setIgnoreMouse: ignore => ipcRenderer.send('sci:pet-overlay:ignore-mouse', ignore),
    // Flip the overlay focusable (and focus it) while the composer needs keys.
    setFocusable: focusable => ipcRenderer.send('sci:pet-overlay:set-focusable', focusable),
    // Main renderer → overlay (forwarded by main): push the latest pet state.
    pushState: payload => ipcRenderer.send('sci:pet-overlay:state', payload),
    // Overlay → main renderer (forwarded by main): pop back in / composer submit.
    control: payload => ipcRenderer.send('sci:pet-overlay:control', payload),
    // Overlay subscribes to state pushes.
    onState: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('sci:pet-overlay:state', listener)

      return () => ipcRenderer.removeListener('sci:pet-overlay:state', listener)
    },
    // Main renderer subscribes to overlay control messages.
    onControl: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('sci:pet-overlay:control', listener)

      return () => ipcRenderer.removeListener('sci:pet-overlay:control', listener)
    }
  },
  // HUD mode: the chrome-free floating chat. A full app renderer (own gateway)
  // sized as a floating bar, so it mounts the real composer. Main owns the
  // window; `onChanged` keeps every window's toggle truthful.
  hud: {
    nativeDrag: hudNativeDrag,
    windowing: {
      clientPlacement: hudWindowing?.clientPlacement !== false,
      controlDrag: hudWindowing?.controlDrag === true,
      nativeDrag: hudNativeDrag,
      solid: hudWindowing?.solid === true,
      workspaceTransfer: hudWindowing?.workspaceTransfer === true
    },
    open: request => ipcRenderer.invoke('sci:hud:open', request),
    close: () => ipcRenderer.invoke('sci:hud:close'),
    setIgnoreMouse: ignore => ipcRenderer.send('sci:hud:ignore-mouse', ignore),
    beginMove: () => ipcRenderer.send('sci:hud:begin-move'),
    endMove: () => ipcRenderer.send('sci:hud:end-move'),
    moveBy: delta => ipcRenderer.send('sci:hud:move-by', delta),
    setWorkspaceTransfer: transferring => ipcRenderer.send('sci:hud:workspace-transfer', transferring),
    setBounds: bounds => ipcRenderer.send('sci:hud:set-bounds', bounds),
    resetLayout: () => ipcRenderer.invoke('sci:hud:reset-layout'),
    // Whether the band covers the window below the bar. Main pairs it with the
    // user's translucency setting to decide the native frost (macOS vibrancy /
    // Windows 11 DWM backdrop) — see hudFrostFor.
    setFrost: showing => ipcRenderer.invoke('sci:hud:frost', showing),
    // The HUD tells main which session it is on; main hands that back to the
    // app window when the HUD closes, so the app can re-home onto it.
    setSession: sessionId => ipcRenderer.send('sci:hud:session', sessionId),
    onGoto: callback => {
      const listener = (_event, sessionId) => callback(sessionId)
      ipcRenderer.on('sci:hud:goto', listener)

      return () => ipcRenderer.removeListener('sci:hud:goto', listener)
    },
    onChanged: callback => {
      const listener = (_event, state) => callback(state)
      ipcRenderer.on('sci:hud:changed', listener)

      return () => ipcRenderer.removeListener('sci:hud:changed', listener)
    },
    // Linux only, and silent elsewhere: where the cursor is, in page
    // coordinates, or null when it has left the window. Stands in for the
    // mousemove that `setIgnoreMouseEvents(true, { forward: true })` delivers on
    // macOS and Windows but not here.
    onCursor: callback => {
      const listener = (_event, point) => callback(point)
      ipcRenderer.on('sci:hud:cursor', listener)

      return () => ipcRenderer.removeListener('sci:hud:cursor', listener)
    },
    // Main's game-overlay watch: whether a fullscreen app (a game) is under
    // the HUD, so the renderer can step back to the low-opacity overlay
    // treatment while one owns the screen.
    onGameOverlay: callback => {
      const listener = (_event, state) => callback(state)
      ipcRenderer.on('sci:hud:game-overlay', listener)

      return () => ipcRenderer.removeListener('sci:hud:game-overlay', listener)
    }
  },
  hudModifier: {
    getSettings: () => ipcRenderer.invoke('sci:hud-modifier:settings:get'),
    setEnabled: enabled => ipcRenderer.invoke('sci:hud-modifier:settings:set', enabled),
    openPermissionSettings: () => ipcRenderer.invoke('sci:hud-modifier:permission'),
    onStatus: callback => {
      const listener = (_event: Electron.IpcRendererEvent, status: HudModifierStatus) => callback(status)
      ipcRenderer.on('sci:hud-modifier:status', listener)

      return () => ipcRenderer.removeListener('sci:hud-modifier:status', listener)
    }
  } satisfies HudModifierApi,
  // macOS native screenshot gesture; captures require a main-issued request.
  screenshot:
    process.platform === 'darwin'
      ? {
          getSettings: () => ipcRenderer.invoke('sci:screenshot:settings:get'),
          setEnabled: enabled => ipcRenderer.invoke('sci:screenshot:settings:set', enabled),
          openPermissionSettings: kind => ipcRenderer.invoke('sci:screenshot:permission', kind),
          capture: requestId => ipcRenderer.invoke('sci:screenshot:capture', requestId),
          onStatus: callback => {
            const listener = (_event, status) => callback(status)
            ipcRenderer.on('sci:screenshot:status', listener)

            return () => ipcRenderer.removeListener('sci:screenshot:status', listener)
          },
          onRequest: callback => {
            const channel = 'sci:screenshot:request'
            const listener = (_event, requestId) => callback(requestId)

            if (ipcRenderer.listenerCount(channel) === 0) {
              ipcRenderer.send('sci:screenshot:subscribe', true)
            }

            ipcRenderer.on(channel, listener)

            return () => {
              ipcRenderer.removeListener(channel, listener)

              if (ipcRenderer.listenerCount(channel) === 0) {
                ipcRenderer.send('sci:screenshot:subscribe', false)
              }
            }
          }
        }
      : undefined,
  // Quick Entry: the global-hotkey mini composer window. Main owns the OS
  // shortcut + the persisted preference; the quick window only captures text
  // and hands it back, and the primary renderer submits it through the normal
  // prompt path.
  quickEntry: {
    getSettings: () => ipcRenderer.invoke('sci:quick-entry:settings:get'),
    setSettings: patch => ipcRenderer.invoke('sci:quick-entry:settings:set', patch),
    submit: payload => ipcRenderer.send('sci:quick-entry:submit', payload),
    dismiss: () => ipcRenderer.send('sci:quick-entry:dismiss'),
    // Primary renderer → main → quick window: gateway connection state + the
    // recent-session options the target picker offers. Main caches the latest
    // payload so a freshly spawned quick window starts from truth.
    pushState: payload => ipcRenderer.send('sci:quick-entry:state', payload),
    // Quick window subscribes to those pushes.
    onState: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('sci:quick-entry:state', listener)

      return () => ipcRenderer.removeListener('sci:quick-entry:state', listener)
    },
    // Main → primary renderer: a submit captured by the quick window.
    onSubmit: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('sci:quick-entry:submit', listener)

      return () => ipcRenderer.removeListener('sci:quick-entry:submit', listener)
    },
    // Main → quick window: you were just summoned (reset draft + refocus).
    onShown: callback => {
      const listener = () => callback()
      ipcRenderer.on('sci:quick-entry:shown', listener)

      return () => ipcRenderer.removeListener('sci:quick-entry:shown', listener)
    }
  },
  getBootProgress: () => ipcRenderer.invoke('sci:boot-progress:get'),
  getConnectionConfig: profile => ipcRenderer.invoke('sci:connection-config:get', profile),
  saveConnectionConfig: payload => ipcRenderer.invoke('sci:connection-config:save', payload),
  applyConnectionConfig: payload => ipcRenderer.invoke('sci:connection-config:apply', payload),
  testConnectionConfig: payload => ipcRenderer.invoke('sci:connection-config:test', payload),
  // Opt-in OS-keychain encryption for stored gateway secrets (default off —
  // see secret-storage-policy.ts). get never touches the OS keychain.
  getSecretStorageEncryption: () => ipcRenderer.invoke('sci:secret-storage:get'),
  setSecretStorageEncryption: (on: boolean) => ipcRenderer.invoke('sci:secret-storage:set', on),
  // v2 multi-connection registry: named agent sources (local / remote / cloud / ssh).
  connections: {
    list: () => ipcRenderer.invoke('sci:connections:list'),
    save: payload => ipcRenderer.invoke('sci:connections:save', payload),
    remove: id => ipcRenderer.invoke('sci:connections:remove', id),
    setPrimary: id => ipcRenderer.invoke('sci:connections:set-primary', id),
    setLaunchMode: mode => ipcRenderer.invoke('sci:connections:set-launch-mode', mode),
    setLastUsed: id => ipcRenderer.invoke('sci:connections:set-last-used', id),
    test: id => ipcRenderer.invoke('sci:connections:test', id),
    updateManaged: id => ipcRenderer.invoke('sci:connections:update-managed', id),
    // Fan out `sci update` to every eligible registered connection.
    // Optional excludeIds skips rows the caller updates through another path.
    updateAll: options => ipcRenderer.invoke('sci:connections:update-all', options),
    // Registry lifecycle push (main → renderer): a connection was removed or
    // materially edited, so secondaries scoped to it must be disposed (and,
    // for edits, re-dialed at the new target).
    onChanged: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('sci:connections:changed', listener)

      return () => ipcRenderer.removeListener('sci:connections:changed', listener)
    }
  },
  sshConfigHosts: () => ipcRenderer.invoke('sci:ssh-config:hosts'),
  sshResolveHost: host => ipcRenderer.invoke('sci:ssh-config:resolve', host),
  probeConnectionConfig: remoteUrl => ipcRenderer.invoke('sci:connection-config:probe', remoteUrl),
  // `options` lets a registry-editor draft sign in BEFORE it is saved: the
  // main process settles the draft's connection id up front so the login
  // window writes into the per-connection cookie jar the saved entry will
  // read (not the legacy shared jar an unsaved URL would fall back to).
  oauthLoginConnectionConfig: (remoteUrl, options) =>
    ipcRenderer.invoke('sci:connection-config:oauth-login', remoteUrl, options),
  oauthLogoutConnectionConfig: remoteUrl => ipcRenderer.invoke('sci:connection-config:oauth-logout', remoteUrl),
  // Sci Cloud: one portal login powers discovery + silent per-agent sign-in
  // (cloud-auto-discovery Phase 3).
  cloud: {
    status: () => ipcRenderer.invoke('sci:cloud:status'),
    login: () => ipcRenderer.invoke('sci:cloud:login'),
    logout: () => ipcRenderer.invoke('sci:cloud:logout'),
    discover: org => ipcRenderer.invoke('sci:cloud:discover', org),
    agentSignIn: dashboardUrl => ipcRenderer.invoke('sci:cloud:agent-sign-in', dashboardUrl)
  },
  profile: {
    getDefault: () => ipcRenderer.invoke('sci:profile:default:get'),
    setDefault: (route: DesktopProfileRoute) => ipcRenderer.invoke('sci:profile:default:set', route),
    onDefaultChanged: (callback: (route: DesktopProfileRoute | null) => void) => {
      const listener = (_event: Electron.IpcRendererEvent, route: DesktopProfileRoute | null) => callback(route)
      ipcRenderer.on('sci:profile:default:changed', listener)

      return () => ipcRenderer.removeListener('sci:profile:default:changed', listener)
    },
    get: () => ipcRenderer.invoke('sci:profile:get'),
    remember: name => ipcRenderer.invoke('sci:profile:remember', name),
    set: name => ipcRenderer.invoke('sci:profile:set', name)
  },
  api: request => ipcRenderer.invoke('sci:api', request),
  notify: payload => ipcRenderer.invoke('sci:notify', payload),
  claimStartupLatency: () => ipcRenderer.invoke('sci:startup-latency:claim'),
  requestMicrophoneAccess: () => ipcRenderer.invoke('sci:requestMicrophoneAccess'),
  readWindowBelow: () => ipcRenderer.invoke('sci:window:readBelow'),
  readFileDataUrl: filePath => ipcRenderer.invoke('sci:readFileDataUrl', filePath),
  readFileDataUrlForAttach: filePath => ipcRenderer.invoke('sci:readFileDataUrlForAttach', filePath),
  dataUrlReadMax: {
    get: () => ipcRenderer.invoke('sci:data-url-read-max:get'),
    set: maxMb => ipcRenderer.invoke('sci:data-url-read-max:set', maxMb)
  },
  readFileText: filePath => ipcRenderer.invoke('sci:readFileText', filePath),
  readPluginSource: (filePath: string) => ipcRenderer.invoke('sci:readPluginSource', filePath),
  selectPaths: options => ipcRenderer.invoke('sci:selectPaths', options),
  selectSavePath: options => ipcRenderer.invoke('sci:selectSavePath', options),
  writeClipboard: text => ipcRenderer.invoke('sci:writeClipboard', text),
  readClipboard: () => ipcRenderer.invoke('sci:readClipboard'),
  saveGatewayFile: payload => ipcRenderer.invoke('sci:saveGatewayFile', payload),
  saveImageFromUrl: url => ipcRenderer.invoke('sci:saveImageFromUrl', url),
  contextMenuEdit: command => ipcRenderer.invoke('sci:context-menu:edit', command),
  contextMenuCopyImage: () => ipcRenderer.invoke('sci:context-menu:copy-image'),
  contextMenuSpellcheck: action => ipcRenderer.invoke('sci:context-menu:spellcheck', action),
  contextMenuGuestAddWord: payload => ipcRenderer.invoke('sci:context-menu:guest-add-word', payload),
  onContextMenuSpellcheck: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('sci:context-menu-spellcheck', listener)

    return () => ipcRenderer.removeListener('sci:context-menu-spellcheck', listener)
  },
  saveImageBuffer: (data, ext, name) => ipcRenderer.invoke('sci:saveImageBuffer', { data, ext, name }),
  capturePreview: payload => ipcRenderer.invoke('sci:capturePreview', payload),
  savePastedText: text => ipcRenderer.invoke('sci:savePastedText', { text }),
  saveClipboardImage: () => ipcRenderer.invoke('sci:saveClipboardImage'),
  getPathForFile: file => {
    try {
      return webUtils.getPathForFile(file) || ''
    } catch {
      return ''
    }
  },
  normalizePreviewTarget: (target, baseDir) => ipcRenderer.invoke('sci:normalizePreviewTarget', target, baseDir),
  watchPreviewFile: url => ipcRenderer.invoke('sci:watchPreviewFile', url),
  watchDirectory: dir => ipcRenderer.invoke('sci:watchDirectory', dir),
  stopPreviewFileWatch: id => ipcRenderer.invoke('sci:stopPreviewFileWatch', id),
  setActiveWork: payload => ipcRenderer.send('sci:active-work', payload),
  setTitleBarTheme: payload => ipcRenderer.send('sci:titlebar-theme', payload),
  setNativeTheme: mode => ipcRenderer.send('sci:native-theme', mode),
  setTranslucency: payload => ipcRenderer.send('sci:translucency', payload),
  setKeepAwake: on => ipcRenderer.send('sci:keep-awake', on),
  minimizeToTray: {
    get: () => ipcRenderer.invoke('sci:minimize-to-tray:get'),
    set: on => ipcRenderer.invoke('sci:minimize-to-tray:set', on),
    onChanged: callback => {
      const listener = (_event, status) => callback(status)
      ipcRenderer.on('sci:minimize-to-tray:changed', listener)

      return () => ipcRenderer.removeListener('sci:minimize-to-tray:changed', listener)
    }
  },
  setDisableF12: blocked => ipcRenderer.send('sci:devtools:disable-f12', blocked),
  setF12ShortcutActive: active => ipcRenderer.send('sci:f12ShortcutActive', Boolean(active)),
  onF12Shortcut: callback => {
    const listener = (_event, input) => callback(input)
    ipcRenderer.on('sci:f12-shortcut', listener)

    return () => ipcRenderer.removeListener('sci:f12-shortcut', listener)
  },
  setPreviewShortcutActive: active => ipcRenderer.send('sci:previewShortcutActive', Boolean(active)),
  openExternal: url => ipcRenderer.invoke('sci:openExternal', url),
  mcpOauth: {
    // One-shot loopback listener for MCP OAuth against remote backends: bind
    // on this machine, hand redirectUri to mcp.servers.oauth.start, then wait
    // for the provider redirect and relay code/state via oauth.callback.
    listen: () => ipcRenderer.invoke('sci:mcp-oauth:listen'),
    wait: (id, timeoutMs) => ipcRenderer.invoke('sci:mcp-oauth:wait', id, timeoutMs),
    cancel: id => ipcRenderer.invoke('sci:mcp-oauth:cancel', id)
  },
  openPreviewInBrowser: url => ipcRenderer.invoke('sci:openPreviewInBrowser', url),
  reachPreviewUrl: url => ipcRenderer.invoke('sci:preview:reach', url),
  setActiveConnectionRoute: route => ipcRenderer.send('sci:connection:active-route', route),
  fetchLinkTitle: url => ipcRenderer.invoke('sci:fetchLinkTitle', url),
  resolveFavicon: url => ipcRenderer.invoke('sci:resolveFavicon', url),
  sanitizeWorkspaceCwd: cwd => ipcRenderer.invoke('sci:workspace:sanitize', cwd),
  settings: {
    getDefaultProjectDir: () => ipcRenderer.invoke('sci:setting:defaultProjectDir:get'),
    setDefaultProjectDir: dir => ipcRenderer.invoke('sci:setting:defaultProjectDir:set', dir),
    pickDefaultProjectDir: () => ipcRenderer.invoke('sci:setting:defaultProjectDir:pick')
  },
  zoom: {
    // Current zoom of this window, as { level, percent }.
    get: () => ipcRenderer.invoke('sci:zoom:get'),
    // Synchronous zoom factor (1 = 100%). Coordinate math needs it in the
    // same tick as the event it converts, so no IPC round-trip here.
    factor: () => webFrame.getZoomFactor(),
    setPercent: percent => ipcRenderer.send('sci:zoom:set-percent', percent),
    // Fires on every zoom change, including the Ctrl/Cmd +/-/0 shortcuts,
    // so the settings UI can stay in sync with the keyboard.
    onChanged: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('sci:zoom:changed', listener)

      return () => ipcRenderer.removeListener('sci:zoom:changed', listener)
    }
  },
  revealLogs: () => ipcRenderer.invoke('sci:logs:reveal'),
  getRecentLogs: () => ipcRenderer.invoke('sci:logs:recent'),
  // Fire-and-forget: persists a renderer error-boundary catch (with component
  // stack) to desktop.log so crashes survive the window (#79428).
  reportRendererError: report => ipcRenderer.send('sci:logs:renderer-error', report),
  logLine: (line: string): void => ipcRenderer.send('sci:logs:renderer-line', line),
  readDir: dirPath => ipcRenderer.invoke('sci:fs:readDir', dirPath),
  gitRoot: startPath => ipcRenderer.invoke('sci:fs:gitRoot', startPath),
  revealPath: targetPath => ipcRenderer.invoke('sci:fs:reveal', targetPath),
  openDir: dirPath => ipcRenderer.invoke('sci:fs:openDir', dirPath),
  desktopPluginsRoot: () => ipcRenderer.invoke('sci:fs:desktopPluginsRoot'),
  reconcileDesktopPlugins: () => ipcRenderer.invoke('sci:fs:reconcileDesktopPlugins'),
  logsRoot: (profile?: string) => ipcRenderer.invoke('sci:fs:logsRoot', profile),
  renamePath: (targetPath, newName) => ipcRenderer.invoke('sci:fs:rename', targetPath, newName),
  writeTextFile: (filePath, content) => ipcRenderer.invoke('sci:fs:writeText', filePath, content),
  trashPath: targetPath => ipcRenderer.invoke('sci:fs:trash', targetPath),
  git: {
    worktreeList: repoPath => ipcRenderer.invoke('sci:git:worktreeList', repoPath),
    worktreeAdd: (repoPath, options) => ipcRenderer.invoke('sci:git:worktreeAdd', repoPath, options),
    worktreeRemove: (repoPath, worktreePath, options) =>
      ipcRenderer.invoke('sci:git:worktreeRemove', repoPath, worktreePath, options),
    branchSwitch: (repoPath, branch) => ipcRenderer.invoke('sci:git:branchSwitch', repoPath, branch),
    branchList: repoPath => ipcRenderer.invoke('sci:git:branchList', repoPath),
    baseBranchList: repoPath => ipcRenderer.invoke('sci:git:baseBranchList', repoPath),
    repoStatus: repoPath => ipcRenderer.invoke('sci:git:repoStatus', repoPath),
    fileDiff: (repoPath, filePath) => ipcRenderer.invoke('sci:git:fileDiff', repoPath, filePath),
    scanRepos: (roots, options) => ipcRenderer.invoke('sci:git:scanRepos', roots, options),
    review: {
      list: (repoPath, scope, baseRef) => ipcRenderer.invoke('sci:git:review:list', repoPath, scope, baseRef),
      diff: (repoPath, filePath, scope, baseRef, staged) =>
        ipcRenderer.invoke('sci:git:review:diff', repoPath, filePath, scope, baseRef, staged),
      stage: (repoPath, filePath) => ipcRenderer.invoke('sci:git:review:stage', repoPath, filePath),
      unstage: (repoPath, filePath) => ipcRenderer.invoke('sci:git:review:unstage', repoPath, filePath),
      revert: (repoPath, filePath) => ipcRenderer.invoke('sci:git:review:revert', repoPath, filePath),
      revParse: (repoPath, ref) => ipcRenderer.invoke('sci:git:review:revParse', repoPath, ref),
      commit: (repoPath, message, push) => ipcRenderer.invoke('sci:git:review:commit', repoPath, message, push),
      commitContext: repoPath => ipcRenderer.invoke('sci:git:review:commitContext', repoPath),
      push: repoPath => ipcRenderer.invoke('sci:git:review:push', repoPath),
      shipInfo: repoPath => ipcRenderer.invoke('sci:git:review:shipInfo', repoPath),
      prList: (repoPath, branches, numbers) =>
        ipcRenderer.invoke('sci:git:review:prList', repoPath, branches, numbers),
      createPr: repoPath => ipcRenderer.invoke('sci:git:review:createPr', repoPath)
    }
  },
  terminal: {
    attach: id => ipcRenderer.invoke('sci:terminal:attach', id),
    cwd: id => ipcRenderer.invoke('sci:terminal:cwd', id),
    dispose: id => ipcRenderer.invoke('sci:terminal:dispose', id),
    resize: (id, size) => ipcRenderer.invoke('sci:terminal:resize', id, size),
    start: options => ipcRenderer.invoke('sci:terminal:start', options),
    write: (id, data) => ipcRenderer.invoke('sci:terminal:write', id, data),
    onData: (id, callback) => {
      const channel = `sci:terminal:${id}:data`
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on(channel, listener)

      return () => ipcRenderer.removeListener(channel, listener)
    },
    onExit: (id, callback) => {
      const channel = `sci:terminal:${id}:exit`
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on(channel, listener)

      return () => ipcRenderer.removeListener(channel, listener)
    }
  },
  onClosePreviewRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('sci:close-preview-requested', listener)

    return () => ipcRenderer.removeListener('sci:close-preview-requested', listener)
  },
  onPreviewNav: callback => {
    const listener = (_event, command) => callback(command)
    ipcRenderer.on('sci:preview-nav', listener)

    return () => ipcRenderer.removeListener('sci:preview-nav', listener)
  },
  onOpenFolderRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('sci:open-folder-requested', listener)

    return () => ipcRenderer.removeListener('sci:open-folder-requested', listener)
  },
  onOpenUpdatesRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('sci:open-updates', listener)

    return () => ipcRenderer.removeListener('sci:open-updates', listener)
  },
  onDeepLink: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('sci:deep-link', listener)

    return () => ipcRenderer.removeListener('sci:deep-link', listener)
  },
  signalDeepLinkReady: () => ipcRenderer.invoke('sci:deep-link-ready'),
  probePluginRepo: payload => ipcRenderer.invoke('sci:plugin:probe', payload),
  installDesktopPlugin: payload => ipcRenderer.invoke('sci:plugin:installDesktop', payload),
  removeDesktopPlugin: payload => ipcRenderer.invoke('sci:plugin:removeDesktop', payload),
  onWindowStateChanged: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('sci:window-state-changed', listener)

    return () => ipcRenderer.removeListener('sci:window-state-changed', listener)
  },
  onFocusSession: callback => {
    const listener = (_event, sessionId) => callback(sessionId)
    ipcRenderer.on('sci:focus-session', listener)

    return () => ipcRenderer.removeListener('sci:focus-session', listener)
  },
  onNotificationAction: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('sci:notification-action', listener)

    return () => ipcRenderer.removeListener('sci:notification-action', listener)
  },
  onNotificationActivate: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('sci:notification-activate', listener)

    return () => ipcRenderer.removeListener('sci:notification-activate', listener)
  },
  onExternalOpenFailed: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('sci:external-open-failed', listener)

    return () => ipcRenderer.removeListener('sci:external-open-failed', listener)
  },
  onPreviewFileChanged: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('sci:preview-file-changed', listener)

    return () => ipcRenderer.removeListener('sci:preview-file-changed', listener)
  },
  onBackendExit: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('sci:backend-exit', listener)

    return () => ipcRenderer.removeListener('sci:backend-exit', listener)
  },
  // Cooperative pool retirement (main → renderer): the pooled backend under
  // `poolKey` is being stopped for a foreground open. Park that scope; do not
  // redial into the slot it vacated.
  onPoolBackendRetiring: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('sci:pool:retiring', listener)

    return () => ipcRenderer.removeListener('sci:pool:retiring', listener)
  },
  // Soft gateway-mode apply finished tearing down the primary backend. Renderer
  // should wipe session lists + re-dial without a window reload.
  onConnectionApplied: callback => {
    const listener = () => callback()
    ipcRenderer.on('sci:connection:applied', listener)

    return () => ipcRenderer.removeListener('sci:connection:applied', listener)
  },
  onPowerResume: callback => {
    const listener = () => callback()
    ipcRenderer.on('sci:power-resume', listener)

    return () => ipcRenderer.removeListener('sci:power-resume', listener)
  },
  // AC ↔ battery transitions; renderers slow their backstop polls on battery.
  getOnBattery: () => ipcRenderer.invoke('sci:power-battery:get'),
  onBatteryChanged: callback => {
    const listener = (_event, onBattery) => callback(Boolean(onBattery))
    ipcRenderer.on('sci:power-battery', listener)

    return () => ipcRenderer.removeListener('sci:power-battery', listener)
  },
  onBootProgress: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('sci:boot-progress', listener)

    return () => ipcRenderer.removeListener('sci:boot-progress', listener)
  },
  // First-launch bootstrap progress -- emitted by the install.ps1 stage
  // runner in main.ts (apps/desktop/electron/bootstrap-runner.ts).
  // Renderer's install overlay subscribes to live events and queries the
  // current snapshot via getBootstrapState() to recover after a devtools
  // reload mid-bootstrap.
  getBootstrapState: () => ipcRenderer.invoke('sci:bootstrap:get'),
  probeLocalBackend: () => ipcRenderer.invoke('sci:local-backend:probe'),
  continueBootstrapLocal: () => ipcRenderer.invoke('sci:bootstrap:continue-local'),
  recycleBackend: profile => ipcRenderer.invoke('sci:backend:recycle', profile),
  resetBootstrap: () => ipcRenderer.invoke('sci:bootstrap:reset'),
  repairBootstrap: () => ipcRenderer.invoke('sci:bootstrap:repair'),
  cancelBootstrap: () => ipcRenderer.invoke('sci:bootstrap:cancel'),
  onBootstrapEvent: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('sci:bootstrap:event', listener)

    return () => ipcRenderer.removeListener('sci:bootstrap:event', listener)
  },
  getVersion: () => ipcRenderer.invoke('sci:version'),
  relaunchApp: () => ipcRenderer.invoke('sci:app:relaunch'),
  getMachineProfile: () => ipcRenderer.invoke('sci:machine:profile'),
  getRemoteDisplayReason: () => ipcRenderer.invoke('sci:get-remote-display-reason'),
  uninstall: {
    summary: () => ipcRenderer.invoke('sci:uninstall:summary'),
    run: mode => ipcRenderer.invoke('sci:uninstall:run', { mode })
  },
  updates: {
    check: opts => ipcRenderer.invoke('sci:updates:check', opts),
    apply: opts => ipcRenderer.invoke('sci:updates:apply', opts),
    getBranch: () => ipcRenderer.invoke('sci:updates:branch:get'),
    setBranch: name => ipcRenderer.invoke('sci:updates:branch:set', name),
    onProgress: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('sci:updates:progress', listener)

      return () => ipcRenderer.removeListener('sci:updates:progress', listener)
    },
    takePendingRun: () => ipcRenderer.invoke('sci:updates:metric:take'),
    ackPendingRun: sent => ipcRenderer.invoke('sci:updates:metric:ack', sent),
    onPendingRun: callback => {
      const listener = () => callback()
      ipcRenderer.on('sci:updates:metric:pending', listener)

      return () => ipcRenderer.removeListener('sci:updates:metric:pending', listener)
    }
  },
  desktopMetrics: {
    setEnabled: (on, profile) => ipcRenderer.invoke('sci:desktop-metrics:set-enabled', on, profile),
    takeRendererCrashes: () => ipcRenderer.invoke('sci:desktop-metrics:crash:take'),
    ackRendererCrashes: sent => ipcRenderer.invoke('sci:desktop-metrics:crash:ack', sent)
  },
  themes: {
    fetchMarketplace: id => ipcRenderer.invoke('sci:vscode-theme:fetch', id),
    searchMarketplace: query => ipcRenderer.invoke('sci:vscode-theme:search', query)
  },
  // Find-in-page (Ctrl/Cmd+F): delegates to Electron's
  // webContents.findInPage on the IPC sender's window so a Cmd+F pressed
  // in a secondary session window searches THAT window, not the primary.
  // `onFoundInPage` returns the unsubscribe fn; the renderer wires it via
  // `initFindInPageListener` in store/find-in-page.ts and tears it down
  // when the FindBar unmounts.
  findInPage: (query, options) => ipcRenderer.invoke('sci:find-in-page', query, options),
  stopFindInPage: () => ipcRenderer.invoke('sci:stop-find-in-page'),
  onFoundInPage: callback => {
    const listener = (_event, result) => callback(result)
    ipcRenderer.on('sci:found-in-page', listener)

    return () => ipcRenderer.removeListener('sci:found-in-page', listener)
  },
  // Main-process `before-input-event` forwards Ctrl/Cmd+F here so renderer
  // can open the FindBar even when the GTK compositor has already grabbed
  // the chord at the windowing layer (#81727).
  onOpenFindBarRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('sci:open-find-bar', listener)

    return () => ipcRenderer.removeListener('sci:open-find-bar', listener)
  }
})
