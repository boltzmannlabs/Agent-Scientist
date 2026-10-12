import fs from 'node:fs'
import https from 'node:https'
import os from 'node:os'
import path from 'node:path'

import { expect, test, vi } from 'vitest'

import { resolveInstallScript } from '../apps/desktop/electron/bootstrap-runner'

test('unpublished packaged bootstrap refuses before writing an installer', async () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'sci-distribution-'))
  const network = vi.spyOn(https, 'get').mockImplementation(() => { throw new Error('unexpected network') })

  try {
    await expect(resolveInstallScript({
      installStamp: { commit: 'a'.repeat(40), branch: 'main' },
      sourceRepoRoot: null,
      sciHome: home,
      emit: () => {}
    })).rejects.toThrow('SCI packaged installer is not published')
    expect(fs.readdirSync(home)).toEqual([])
    expect(network).not.toHaveBeenCalled()
  } finally {
    network.mockRestore()
    fs.rmSync(home, { recursive: true, force: true })
  }
})

test('source checkout uses its own installer without a download', async () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'sci-distribution-'))
  const download = vi.fn(() => { throw new Error('unexpected network') })
  const script = path.join(home, 'scripts', process.platform === 'win32' ? 'install.ps1' : 'install.sh')

  try {
    fs.mkdirSync(path.dirname(script))
    fs.writeFileSync(script, '# fixture, never executed\n')

    const resolved = await resolveInstallScript({
      installStamp: null, sourceRepoRoot: home, sciHome: home,
      emit: () => {}, _download: download
    })

    expect(resolved.path).toBe(script)
    expect(resolved.source).toBe('local')
    expect(download).not.toHaveBeenCalled()
  } finally {
    fs.rmSync(home, { recursive: true, force: true })
  }
})
