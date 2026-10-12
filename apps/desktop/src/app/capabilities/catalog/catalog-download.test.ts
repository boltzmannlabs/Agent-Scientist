// @vitest-environment node
import { afterEach, expect, it, vi } from 'vitest'

import { setApiRequestConnection, setApiRequestProfile } from '@/api/client'

import { fetchCatalog, prefetchCatalogWhenIdle } from './catalog-data'

afterEach(() => {
  setApiRequestConnection(null)
  setApiRequestProfile(null)
  vi.unstubAllGlobals()
})

it('uses the selected backend A → B → A without contacting public catalogs', async () => {
  const api = vi.fn(async (request: { profile?: string }) => ({ skills: [{ name: request.profile }] }))
  const fetch = vi.fn(() => {
    throw new Error('unexpected website request')
  })
  vi.stubGlobal('window', { sciDesktop: { api } })
  vi.stubGlobal('fetch', fetch)

  for (const name of ['antibody', 'molecule', 'antibody']) {
    setApiRequestConnection(name + '-connection')
    setApiRequestProfile(name)
    expect(await fetchCatalog('skills')).toMatchObject([{ name, source: 'official' }])
    expect(api).toHaveBeenLastCalledWith(
      expect.objectContaining({
        connectionId: name + '-connection',
        profile: name,
        timeoutMs: 60_000
      })
    )
  }

  expect(fetch).not.toHaveBeenCalled()
})

it('captures idle-prefetch ownership and surfaces malformed/backend errors without fallback', async () => {
  const api = vi.fn().mockResolvedValue({ entries: [] })
  vi.stubGlobal('window', { sciDesktop: { api } })

  let idle: () => void = () => {}
  vi.stubGlobal('requestIdleCallback', (callback: () => void) => {
    idle = callback

    return 1
  })
  vi.stubGlobal('cancelIdleCallback', vi.fn())
  setApiRequestConnection('original-connection')
  setApiRequestProfile('original-profile')
  prefetchCatalogWhenIdle('plugins')
  setApiRequestConnection('other-connection')
  setApiRequestProfile('other-profile')
  idle()
  await vi.waitFor(() =>
    expect(api).toHaveBeenCalledExactlyOnceWith(
      expect.objectContaining({
        connectionId: 'original-connection',
        profile: 'original-profile'
      })
    )
  )
  api.mockResolvedValueOnce({ entries: 'not a catalog' })
  await expect(fetchCatalog('plugins')).rejects.toThrow('Invalid catalog response')
  api.mockRejectedValueOnce(new Error('backend timeout'))
  await expect(fetchCatalog('skills')).rejects.toThrow('backend timeout')
  expect(api).toHaveBeenCalledTimes(3)
})
