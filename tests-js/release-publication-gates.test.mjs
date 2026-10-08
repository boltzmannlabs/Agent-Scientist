import fs from 'node:fs'
import yaml from 'js-yaml'
import { expect, test } from 'vitest'

test('unconfigured release entrypoints and always-running follow-ups stay gated', () => {
  const entries = {
    'canary-release': ['tag'],
    'stable-release': ['admit'],
    'desktop-bundled-release': ['validate'],
    'deploy-site': ['deploy-vercel', 'deploy-docs'],
  }
  for (const [workflow, entryJobs] of Object.entries(entries)) {
    const data = yaml.load(fs.readFileSync(new URL(`../.github/workflows/${workflow}.yml`, import.meta.url), 'utf8'))
    for (const job of entryJobs) {
      expect(data.jobs[job].if).toContain("vars.SCI_RELEASES_ENABLED == 'true'")
    }
    if (workflow === 'canary-release') {
      expect(data.on.schedule).toBeUndefined()
      // Prune is also refused when admission was skipped.
      expect(data.jobs.prune.if).toContain("needs.tag.result != 'skipped'")
    } else {
      for (const job of Object.values(data.jobs)) {
        if (job.if?.includes('always()')) {
          expect(job.if).toContain("vars.SCI_RELEASES_ENABLED == 'true'")
        }
      }
    }
  }
})

test('SCI automation has no inherited project destination and requires explicit publisher inputs', () => {
  const root = new URL('../.github/', import.meta.url)
  for (const area of ['workflows', 'ISSUE_TEMPLATE', 'actions/plugin-validate']) {
    const folder = new URL(`${area}/`, root)
    for (const file of fs.readdirSync(folder).filter(name => /\.ya?ml$/.test(name))) {
      const raw = fs.readFileSync(new URL(file, folder), 'utf8')
      expect(raw).not.toMatch(/NousResearch\/hermes|hermes-assets\.nousresearch|hermes-agent\.nousresearch/i)
      expect(yaml.load(raw)).toBeTruthy()
    }
  }
  const read = path => yaml.load(fs.readFileSync(new URL(path, root), 'utf8'))
  const plugin = read('actions/plugin-validate/action.yml')
  expect(plugin.inputs['sci-repository'].required).toBe(true)
  expect(plugin.inputs['sci-repository'].default).toBeUndefined()
  for (const name of ['sandbox-image', 'skills-index', 'skills-index-freshness', 'live-providers']) {
    const workflow = read(`workflows/${name}.yml`)
    const firstJob = Object.values(workflow.jobs)[0]
    expect(firstJob.if).toContain("vars.SCI_RELEASES_ENABLED == 'true'")
    expect(firstJob.if).toContain('github.repository == vars.SCI_REPOSITORY')
  }
})
