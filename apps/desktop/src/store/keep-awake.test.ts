import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { storedBoolean } from '@/lib/storage'

import { $keepAwake, setKeepAwake } from './keep-awake'

const KEY = 'sci.desktop.keepAwake.v1'
const desktopWindow = window as unknown as { sciDesktop?: Window['sciDesktop'] }
const initialSciDesktop = desktopWindow.sciDesktop
const setKeepAwakeBridge = vi.fn()

beforeEach(() => {
  desktopWindow.sciDesktop = { setKeepAwake: setKeepAwakeBridge } as unknown as Window['sciDesktop']
  setKeepAwake(false)
  setKeepAwakeBridge.mockClear()
})

afterEach(() => {
  desktopWindow.sciDesktop = initialSciDesktop
})

describe('keep-awake store', () => {
  it('persists the pref and mirrors it to the main process', () => {
    setKeepAwake(true)
    expect($keepAwake.get()).toBe(true)
    expect(storedBoolean(KEY, false)).toBe(true)
    expect(setKeepAwakeBridge).toHaveBeenLastCalledWith(true)

    setKeepAwake(false)
    expect(storedBoolean(KEY, true)).toBe(false)
    expect(setKeepAwakeBridge).toHaveBeenLastCalledWith(false)
  })
})
