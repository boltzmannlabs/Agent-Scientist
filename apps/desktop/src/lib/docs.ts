import manual from '../../../../README.md?raw'

import { downloadTextFile } from './download-text'

/** Handled inside the renderer, never delegated to a browser or protocol handler. */
export const DESKTOP_DOCS_URL = 'sci:manual'

/** Available even when the backend cannot start. No website or model request. */
export function openLocalManual(): void {
  downloadTextFile('Agent-Scientist-Manual.md', manual, 'text/markdown')
}
