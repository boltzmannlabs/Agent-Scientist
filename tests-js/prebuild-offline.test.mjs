import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { spawnSync } from 'node:child_process'
import { expect, test } from 'vitest'

test('unconfigured website prebuild stays offline even with no cached catalog', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'sci-prebuild-'))
  try {
    const scripts = path.join(root, 'website', 'scripts')
    fs.mkdirSync(scripts, { recursive: true })
    const entry = path.join(scripts, 'prebuild.mjs')
    fs.copyFileSync(new URL('../website/scripts/prebuild.mjs', import.meta.url), entry)
    const code = `
      let requests = 0;
      globalThis.fetch = async () => { requests++; throw new Error('Network forbidden'); };
      await import(${JSON.stringify(pathToFileURL(entry).href)});
      if (requests !== 0) process.exitCode = 1;
    `
    const result = spawnSync(process.execPath, ['--input-type=module', '-e', code], {
      encoding: 'utf8', timeout: 10000,
    })
    expect(result.error).toBeUndefined()
    expect(result.status, result.stderr).toBe(0)
    expect(JSON.parse(fs.readFileSync(path.join(root, 'website/static/api/skills.json'), 'utf8'))).toEqual([])
  } finally {
    fs.rmSync(root, { recursive: true, force: true })
  }
})
