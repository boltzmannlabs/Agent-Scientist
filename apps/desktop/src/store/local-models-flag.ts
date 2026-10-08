import { atom } from 'nanostores'

/**
 * Feature-flag gate for every local-models surface in the GUI.
 *
 * Local models ship on main when the app was launched with `--local` (either
 * `sci desktop --local` or the flag on Sci.exe itself), OR when this
 * is a canary build, which previews gated features by default. Without the
 * flag the Desktop App shows no local-models surface at all, even on a machine
 * where local models are configured and running.
 */
export const $localModelsEnabled = atom<boolean>(
  typeof window !== 'undefined' && window.sciDesktop?.localModelsEnabled === true
)
