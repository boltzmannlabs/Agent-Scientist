import { describe, expect, it } from 'vitest'

import {
  normalizeSciOpenString,
  pathFromOpenDeepLink,
  pathFromSciDeepLink,
  resolveSciOpenPath
} from './sci-open-target'

describe('normalizeSciOpenString', () => {
  it('accepts hash-router paths and strips a leading hash', () => {
    expect(normalizeSciOpenString('/index-network/intent/1')).toBe('/index-network/intent/1')
    expect(normalizeSciOpenString('#/index-network/intent/1')).toBe('/index-network/intent/1')
  })

  it('maps plugin-scoped sci:// deep links to the same path', () => {
    expect(normalizeSciOpenString('sci://index-network/intent/1')).toBe('/index-network/intent/1')
    expect(normalizeSciOpenString('sci://index-network/intent/1?focus=true')).toBe('/index-network/intent/1?focus=true')
  })

  it('maps sci://open/… deep links by stripping the open host', () => {
    expect(normalizeSciOpenString('sci://open/index-network/intent/1')).toBe('/index-network/intent/1')
    expect(normalizeSciOpenString('sci://open/settings/plugins')).toBe('/settings/plugins')
  })

  it('rejects reserved sci kinds and unsafe paths', () => {
    expect(normalizeSciOpenString('sci://blueprint/morning-brief')).toBeNull()
    expect(normalizeSciOpenString('sci://plugin/install')).toBeNull()
    expect(normalizeSciOpenString('https://example.com/x')).toBeNull()
    expect(normalizeSciOpenString('/../etc/passwd')).toBeNull()
    expect(normalizeSciOpenString('index-network')).toBeNull()
  })
})

describe('resolveSciOpenPath', () => {
  it('merges structured path + params', () => {
    expect(resolveSciOpenPath({ path: '/index-network/intent/1', params: { focus: 'true' } })).toBe(
      '/index-network/intent/1?focus=true'
    )
  })

  it('resolves href the same as a bare string', () => {
    expect(resolveSciOpenPath({ href: 'sci://index-network/intent/1' })).toBe('/index-network/intent/1')
  })
})

describe('pathFromSciDeepLink', () => {
  it('builds the navigate path from a plugin-scoped deep-link payload', () => {
    expect(pathFromSciDeepLink('index-network', 'intent/1')).toBe('/index-network/intent/1')
  })

  it('builds the navigate path from sci://open/… payloads', () => {
    expect(pathFromOpenDeepLink('index-network/intent/1')).toBe('/index-network/intent/1')
    expect(pathFromSciDeepLink('open', 'agent/42')).toBe('/agent/42')
  })

  it('ignores reserved kinds', () => {
    expect(pathFromSciDeepLink('blueprint', 'morning-brief')).toBeNull()
    expect(pathFromSciDeepLink('plugin', 'install')).toBeNull()
    expect(pathFromSciDeepLink('skill', 'install')).toBeNull()
  })
})
