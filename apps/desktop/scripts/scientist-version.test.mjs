import { expect, test } from 'vitest'
import semver from 'semver'
import { nativeQuad, packageVersion } from '../../../scripts/msix-shared.mjs'

test('SCI release order survives native SemVer mapping without changing the original identity', () => {
  const versions = ['1.0.0.0', '1.0.0.1', '1.0.1.0', '1.0.999.999', '1.1.0.0', '1.2.1.3']
  const packages = versions.map(packageVersion)
  expect(packages.every(value => semver.valid(value))).toBe(true)
  for (let i = 1; i < packages.length; i++) expect(semver.gt(packages[i], packages[i - 1])).toBe(true)
  expect(packageVersion('1.2.1.3')).toBe('1.2001.3')
  expect(packageVersion('1.2.1.3+canary.20261016T120000Z')).toBe('1.2001.3+canary.20261016T120000Z')
  expect(packageVersion('0.21.5')).toBe('0.21.5')
  expect(() => packageVersion('1.0.1000.0')).toThrow('minor < 1000')
  expect(() => packageVersion('1.0.0.0.1')).toThrow('Invalid')
})

test('SCI stable and canary refs retain the native timestamp sequence', () => {
  const epoch = Date.parse('2026-10-16T12:00:00Z') / 1000
  expect(nativeQuad('v1.2.1.3', epoch)).toBe(nativeQuad('v1.2001.3', epoch))
  expect(nativeQuad('v1.2.1.3+canary.20261016T120000Z', epoch))
    .toBe(nativeQuad('v1.2001.3+canary.20261016T120000Z', epoch))
})
