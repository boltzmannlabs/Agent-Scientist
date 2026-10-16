import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { expect, it } from 'vitest'
import feedContract from '../apps/desktop/update-feed.cjs'

const root = fileURLToPath(new URL('../', import.meta.url))

function configFor({ variant = 'bundled', tag = 'v1.0.0.0', url = 'https://updates.example', published = true } = {}) {
  // Simulate only the marker's absence in a staged, approved distribution.
  // Never delete the real publication guard or turn on publishing in this checkout.
  const marker = `const fs=require('node:fs'), path=require('node:path');
    const exists=fs.existsSync, marker=path.resolve('sci-unpublished-distribution');
    fs.existsSync=file=>path.resolve(file)===marker ? ${!published} : exists(file);`
  const script = `${marker}
    const c=require('./apps/desktop/electron-builder.config.cjs');
    console.log(JSON.stringify({publish:c.publish,mac:c.mac}));`
  return JSON.parse(execFileSync(process.execPath, ['-e', script], {
    cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env, SCI_DESKTOP_VARIANT: variant, SCI_PAYLOAD_TAG: tag, CLOUDFLARE_R2_PUBLIC_URL: url }
  }))
}

it.each([
  ['bundled', 'v0.28.0', 'stable', false],
  ['bundled', 'v0.29.0+canary.20260906T000000Z', 'canary', false],
  ['light', 'v0.28.0', 'stable', true],
  ['light', 'v0.29.0+canary.20260906T000000Z', 'canary', true]
])('packaging and runtime agree for %s %s', (variant, tag, channel, light) => {
  const config = configFor({ variant, tag }).mac
  const feed = feedContract.darwinFeed(channel, light)
  expect(config.publish).toEqual([{ provider: 'generic', url: `https://updates.example/${feed.directory}/`, channel: feed.channel }])
  expect(config.target).toContain('zip')
  expect(config.notarize).toBe(false)
})

it('bakes only a canonical https feed base into the updater config', () => {
  expect(feedContract.feedBaseUrl(undefined)).toBeUndefined()
  expect(feedContract.feedBaseUrl('https://updates.example/releases/')).toBe('https://updates.example/releases')
  for (const raw of ['http://updates.example', 'https://user:pw@updates.example', 'https://updates.example/?x=1',
    'https://updates.example/#frag', 'https://Updates.Example', 'updates.example', 'https://updates.example/a b']) {
    expect(() => feedContract.feedBaseUrl(raw)).toThrow(TypeError)
  }
  const build = (url) => configFor({ url }).publish
  expect(build('https://updates.example/')).toEqual([{ provider: 'generic', url: 'https://updates.example', channel: 'latest' }])
  expect(() => build('http://updates.example')).toThrow(/canonical https/)
})

it('unpublished builds cannot enable any feed merely by supplying an update URL', () => {
  for (const variant of ['bundled', 'light']) {
    const config = configFor({ variant, published: false })
    expect(config.publish).toBeNull()
    expect(config.mac.publish).toBeNull()
  }
})
