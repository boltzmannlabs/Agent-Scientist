import { expect, it, vi } from 'vitest'

import { DESKTOP_DOCS_URL } from './docs'
import { downloadTextFile } from './download-text'
import { openExternalLink } from './external-link'

vi.mock('./download-text', () => ({ downloadTextFile: vi.fn() }))

it('opens the bundled manual without an external website', () => {
  const external = vi.fn()
  const original = window.sciDesktop
  window.sciDesktop = { ...original, openExternal: external }

  try {
    openExternalLink(DESKTOP_DOCS_URL)
    expect(downloadTextFile).toHaveBeenCalledWith(
      'Agent-Scientist-Manual.md',
      expect.stringContaining('Boltzmann'),
      'text/markdown'
    )
    expect(external).not.toHaveBeenCalled()
  } finally {
    window.sciDesktop = original
  }
})
