import type * as SciSdk from '@sci/plugin-sdk'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { translateBots } from './i18n-test-helper'

const mocks = vi.hoisted(() => ({
  notify: vi.fn(),
  notifyError: vi.fn(),
  request: vi.fn(async (_method: string, _params: Record<string, unknown>): Promise<unknown> => ({})),
  requestProfile: vi.fn(
    async (_route: unknown, _method: string, _params: Record<string, unknown>): Promise<unknown> => ({})
  )
}))

vi.mock('@sci/plugin-sdk', async importOriginal => {
  const original = await importOriginal<typeof SciSdk>()

  return {
    ...original,
    usePluginI18n: () => translateBots,
    host: {
      ...original.host,
      notify: mocks.notify,
      notifyError: mocks.notifyError,
      request: mocks.request,
      requestProfile: mocks.requestProfile
    }
  }
})

const { HubSkillsSection } = await import('./skills-hub')

beforeEach(() => {
  vi.clearAllMocks()
})
afterEach(cleanup)

const fixture = {
  items: [{ name: 'Evidence review', identifier: 'official/science/evidence', description: 'Review evidence' }],
  page: 1,
  total_pages: 1
}

describe('backend skill browser', () => {
  it('browses without an external iframe and requires a button click to install', async () => {
    mocks.request.mockResolvedValue(fixture)
    const { container } = render(<HubSkillsSection />)
    fireEvent.click(screen.getByRole('button', { name: /browse the full hub/i }))
    await screen.findByText('Evidence review')
    expect(container.querySelector('iframe')).toBeNull()
    expect(mocks.request).toHaveBeenCalledExactlyOnceWith('skills.manage', {
      action: 'browse',
      source: 'official',
      page: 1,
      page_size: 20
    })
    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'sci-skill-pick', identifier: 'untrusted/tool' },
        origin: 'https://example.org',
        source: window
      })
    )
    expect(mocks.request).toHaveBeenCalledTimes(1)
    fireEvent.click(screen.getByRole('button', { name: /install.*Evidence review/i }))
    await waitFor(() =>
      expect(mocks.request).toHaveBeenLastCalledWith('skills.manage', {
        action: 'install',
        query: 'official/science/evidence'
      })
    )
  })

  it('browses and installs on the existing bot owner, not the active connection', async () => {
    mocks.requestProfile.mockResolvedValue(fixture)
    render(
      <HubSkillsSection
        bot={{
          name: 'worker',
          remoteSource: true,
          sourceScoped: true,
          route: { connectionId: 'remote-a', mode: 'remote', profile: 'worker', targetProfile: 'backend-worker' }
        }}
      />
    )
    fireEvent.click(screen.getByRole('button', { name: /browse the full hub/i }))
    await screen.findByText('Evidence review')
    fireEvent.click(screen.getByRole('button', { name: /install.*Evidence review/i }))
    await waitFor(() =>
      expect(mocks.requestProfile).toHaveBeenLastCalledWith(
        expect.objectContaining({ connectionId: 'remote-a', targetProfile: 'backend-worker' }),
        'skills.manage',
        { action: 'install', profile: 'backend-worker', query: 'official/science/evidence' }
      )
    )
    expect(mocks.request).not.toHaveBeenCalled()
  })
})
