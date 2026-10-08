import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

import { afterEach, describe, expect, it } from 'vitest'

import { COMPOSER_PASTES_DIRNAME, writeComposerPaste } from './composer-paste'

const scratch: string[] = []

afterEach(() => {
  for (const dir of scratch.splice(0)) {
    fs.rmSync(dir, { force: true, recursive: true })
  }
})

describe('writeComposerPaste', () => {
  it('lands the paste directly under <SCI_HOME>/composer-pastes so the backend admits it', async () => {
    const sciHome = fs.mkdtempSync(path.join(os.tmpdir(), 'sci-home-'))
    scratch.push(sciHome)

    const filePath = await writeComposerPaste(sciHome, 'pasted body')

    expect(path.dirname(filePath)).toBe(path.join(sciHome, COMPOSER_PASTES_DIRNAME))
    expect(fs.readFileSync(filePath, 'utf8')).toBe('pasted body')
  })
})
