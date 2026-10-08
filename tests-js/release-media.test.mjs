import fs from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'
import { expect, test } from 'vitest'

const root = fileURLToPath(new URL('../', import.meta.url))
const require = createRequire(import.meta.url)

test('installer artwork references resolve, or use the plain-background mode', () => {
  const { dmg } = require('../apps/desktop/electron-builder.config.cjs')
  if (dmg.background) {
    expect(fs.statSync(path.join(root, 'apps/desktop', dmg.background)).isFile()).toBe(true)
  } else {
    expect(dmg.backgroundColor).toMatch(/^#[0-9a-f]{6}$/i)
  }
})

test('documentation image references point to distributable media', () => {
  const folders = [
    'website/docs',
    'website/i18n/zh-Hans/docusaurus-plugin-content-docs/current',
  ]
  const missing = []
  for (const folder of folders) {
    for (const name of fs.readdirSync(path.join(root, folder), { recursive: true })) {
      if (!/\.mdx?$/.test(name)) continue
      const doc = path.join(folder, name)
      const raw = fs.readFileSync(path.join(root, doc), 'utf8')
      for (const match of raw.matchAll(/!\[[^\]]*\]\((\/img\/[^)\s]+)\)/g)) {
        if (!fs.existsSync(path.join(root, 'website/static', match[1]))) {
          missing.push(`${doc}: ${match[1]}`)
        }
      }
    }
  }
  expect(missing).toEqual([])
})
