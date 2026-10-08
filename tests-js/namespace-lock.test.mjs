import { expect, test } from 'vitest'
import fs from 'node:fs'

test('published third-party package identities survive application rebranding', () => {
  const lock = JSON.parse(fs.readFileSync(new URL('../package-lock.json', import.meta.url), 'utf8'))
  const external = Object.entries(lock.packages).filter(([, value]) =>
    value.resolved?.startsWith('https://registry.npmjs.org/hermes-'))
  expect(external.length).toBeGreaterThan(0)
  for (const [location, value] of external) {
    const name = new URL(value.resolved).pathname.split('/')[1]
    expect(location.split('node_modules/').at(-1)).toBe(name)
    expect(value.integrity).toBeTruthy()
    for (const dependency of Object.keys(value.dependencies ?? {})) {
      expect(lock.packages[`node_modules/${dependency}`]).toBeDefined()
    }
  }
})

test('owned workspace links resolve to packages carrying their declared identity', () => {
  const lock = JSON.parse(fs.readFileSync(new URL('../package-lock.json', import.meta.url), 'utf8'))
  for (const [location, value] of Object.entries(lock.packages)) {
    if (!value.link || !location.startsWith('node_modules/@sci/')) continue
    const manifest = JSON.parse(fs.readFileSync(new URL(`../${value.resolved}/package.json`, import.meta.url), 'utf8'))
    expect(location.slice('node_modules/'.length)).toBe(manifest.name)
  }
})
