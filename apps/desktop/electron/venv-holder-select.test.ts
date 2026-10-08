import assert from 'node:assert/strict'

import { test } from 'vitest'

import { hasWindowsPathPrefix, isExternalVenvHolder, isSciOwnedVenvDaemon } from './venv-holder-select'

const SCRIPTS = 'C:\\Sci\\venv\\Scripts'

test('matches the hindsight daemon shim (exe under venv Scripts + hindsight cmdline)', () => {
  assert.equal(
    isSciOwnedVenvDaemon(
      'C:\\Sci\\venv\\Scripts\\pythonw.exe',
      'C:\\Sci\\venv\\Scripts\\pythonw.exe -m hindsight_api.main --daemon --idle-timeout 300 --port 9177',
      SCRIPTS
    ),
    true
  )
})

test('Windows path prefix match is ordinal case-insensitive', () => {
  assert.equal(
    isSciOwnedVenvDaemon(
      'c:\\sci\\venv\\scripts\\python.exe',
      'python.exe -m hindsight_api.main --daemon',
      'C:\\Sci\\venv\\Scripts'
    ),
    true
  )
})

test('excludes external venv holders that are not the hindsight daemon', () => {
  // a user terminal running the sci CLI from the venv — must NOT be killed
  assert.equal(isSciOwnedVenvDaemon('C:\\Sci\\venv\\Scripts\\sci.exe', 'sci chat -q "hi"', SCRIPTS), false)
  // an unrelated python script using the venv interpreter
  assert.equal(
    isSciOwnedVenvDaemon('C:\\Sci\\venv\\Scripts\\python.exe', 'python C:\\tools\\import.py', SCRIPTS),
    false
  )
})

test('excludes exes outside the venv even when the cmdline mentions hindsight', () => {
  assert.equal(
    isSciOwnedVenvDaemon('C:\\Other\\pythonw.exe', 'pythonw -m hindsight_api.main --daemon', SCRIPTS),
    false
  )
})

test('prefix boundary: sibling dirs (ScriptsX) do not match', () => {
  assert.equal(hasWindowsPathPrefix('C:\\Sci\\venv\\ScriptsX\\python.exe', SCRIPTS), false)
  assert.equal(hasWindowsPathPrefix('C:\\Sci\\venv\\Scripts\\python.exe', SCRIPTS), true)
})

test('null/undefined fields never match', () => {
  assert.equal(isSciOwnedVenvDaemon(null, 'x', SCRIPTS), false)
  assert.equal(isSciOwnedVenvDaemon('C:\\Sci\\venv\\Scripts\\pythonw.exe', null, SCRIPTS), false)
  assert.equal(isSciOwnedVenvDaemon(undefined, undefined, SCRIPTS), false)
})

// --- isExternalVenvHolder (#62311) ------------------------------------------

test('matches the autostart gateway shim (sci.exe under venv Scripts)', () => {
  assert.equal(
    isExternalVenvHolder(
      'C:\\Sci\\venv\\Scripts\\sci.exe',
      '"C:\\Sci\\venv\\Scripts\\sci.exe" gateway run --external-supervisor',
      SCRIPTS
    ),
    true
  )
})

test('matches the dashboard scheduled task (python -m sci_cli / -m sci)', () => {
  assert.equal(
    isExternalVenvHolder(
      'C:\\Sci\\venv\\Scripts\\python.exe',
      '"C:\\Sci\\venv\\Scripts\\python.exe" -m sci_cli.main dashboard',
      SCRIPTS
    ),
    true
  )
  assert.equal(
    isExternalVenvHolder('C:\\Sci\\venv\\Scripts\\pythonw.exe', 'pythonw.exe -m sci serve', SCRIPTS),
    true
  )
})

test('never matches an unrelated process that merely borrows the venv interpreter', () => {
  // a user's own script running on the venv python — NOT Sci, must NOT be killed
  assert.equal(
    isExternalVenvHolder('C:\\Sci\\venv\\Scripts\\python.exe', 'python C:\\tools\\import.py', SCRIPTS),
    false
  )
  // hindsight daemon is selected by isSciOwnedVenvDaemon, not here
  assert.equal(
    isExternalVenvHolder('C:\\Sci\\venv\\Scripts\\pythonw.exe', 'pythonw -m hindsight_api.main --daemon', SCRIPTS),
    false
  )
})

test('never matches a process outside the venv, even with sci in the cmdline', () => {
  // an editor / shell whose command line mentions the install root (#62445 regression guard)
  assert.equal(
    isExternalVenvHolder('C:\\Windows\\System32\\cmd.exe', 'cmd /c cd C:\\Sci\\venv\\Scripts && dir', SCRIPTS),
    false
  )
  assert.equal(isExternalVenvHolder('C:\\Other\\sci.exe', 'sci gateway run', SCRIPTS), false)
})

test('sibling-dir and boundary safety for the external selector', () => {
  assert.equal(isExternalVenvHolder('C:\\Sci\\venv\\ScriptsX\\sci.exe', 'sci gateway run', SCRIPTS), false)
  assert.equal(isExternalVenvHolder(null, 'sci gateway run', SCRIPTS), false)
  assert.equal(isExternalVenvHolder('C:\\Sci\\venv\\Scripts\\sci.exe', null, SCRIPTS), false)
})
