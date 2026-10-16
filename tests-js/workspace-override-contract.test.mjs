/** Direct workspace pins must match exact overrides when Nix drops override metadata. */
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

import { test } from 'vitest'

test('workspace exact dependency pins agree with resolved root overrides', () => {
  const root = JSON.parse(readFileSync(new URL('../package.json', import.meta.url), 'utf8'))
  const lock = JSON.parse(readFileSync(new URL('../package-lock.json', import.meta.url), 'utf8'))
  for (const path of Object.keys(lock.packages)) {
    if (path.includes('node_modules')) continue
    const manifest = JSON.parse(readFileSync(new URL(`../${path ? path + '/' : ''}package.json`, import.meta.url), 'utf8'))
    for (const kind of ['dependencies', 'devDependencies', 'optionalDependencies']) {
      for (const [name, declared] of Object.entries(manifest[kind] || {})) {
        const override = root.overrides?.[name]
        if (typeof override === 'string' && /^\d+\./.test(override) && /^\d+\./.test(declared)) {
          assert.equal(declared, override, `${path || 'root'}: ${name} must agree with its resolved override`)
        }
      }
    }
  }
})
