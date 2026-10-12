import { Button } from '@sci/ui/ui/components/button'
import { stripWpStyles } from '@sci/ui/utils'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { expect, test } from 'vitest'

test('local button preserves its content and native disabled state', () => {
  const enabled = renderToStaticMarkup(createElement(Button, { children: 'Run analysis' }))
  const disabled = renderToStaticMarkup(createElement(Button, { disabled: true, children: 'Run analysis' }))
  expect(enabled).toContain('Run analysis')
  expect(disabled).toContain('Run analysis')
  expect(enabled).not.toContain('disabled=""')
  expect(disabled).toContain('disabled=""')
})

test('local content sanitizer preserves scientific text but blocks executable URLs', () => {
  const text = '<p>Antibody evidence</p><video poster="javascript:alert(1)"></video>' +
    '<a href="javascript:alert(2)">unsafe</a><script>alert(3)</script>'

  const result = stripWpStyles(text)
  expect(result).toContain('Antibody evidence')
  expect(result).not.toContain('javascript:')
  expect(result).not.toContain('<script')
})
