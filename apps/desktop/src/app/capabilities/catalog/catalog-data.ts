import { skillCatalogInstallIdentifier } from '@sci/shared'
import { useStore } from '@nanostores/react'
import { queryOptions, useQuery } from '@tanstack/react-query'

import { $apiRequestScope, capabilityScoped, type ProfileScope, sciApi } from '@/api/client'
import { queryClient } from '@/lib/query-client'

export type CatalogKind = 'skills' | 'plugins'

export interface CatalogEntry {
  id: string
  name: string
  description: string
  overview: string
  category: string
  categoryLabel: string
  source: string
  author: string
  identifier: string
  installIdentifier?: string | null
  repo: string
  sha: string
  subdir: string
  version: string
  requiresSci: string
  tags: string[]
  platforms: string[]
  requirements: string[]
  tools: string[]
  hooks: string[]
  middleware?: string[]
  commands?: string[]
  license?: string
  sourceUrl: string | null
  docsUrl: string | null
  /** Catalog-provided media, restricted to the same GitHub hosts as the website. */
  imageUrl: string | null
  screenshots?: string[]
  addedAt?: string
  updatedAt?: string
  stars: number | null
  search: string
}

const text = (value: unknown): string => (typeof value === 'string' ? value : '')
const strings = (value: unknown): string[] => (Array.isArray(value) ? value.filter(v => typeof v === 'string') : [])

const IMAGE_HOSTS = new Set(['raw.githubusercontent.com', 'github.com'])

// URL.parse, not `new URL` in try/catch: most skill rows carry no repo or docs
// URL, and 200k thrown TypeErrors cost ~0.7s of main thread per catalog load.
const parseUrl = (value: unknown) => URL.parse(text(value))

/** Mirrors scripts/validate_plugin_catalog.py: https on a GitHub host, else no image. */
export function catalogImageUrl(value: unknown): string | null {
  const url = parseUrl(value)
  const host = url?.hostname.toLowerCase() ?? ''

  return url?.protocol === 'https:' && (IMAGE_HOSTS.has(host) || host.endsWith('.githubusercontent.com'))
    ? url.href
    : null
}

function webUrl(value: unknown): string | null {
  const url = parseUrl(value)

  return url?.protocol === 'https:' || url?.protocol === 'http:' ? url.href : null
}

/** Display form of a source or category id: domains stay verbatim (`browse.sh`),
 *  slugs read as words (`software-development` → `Software Development`). */
export const catalogLabel = (value: string) =>
  value.includes('.') ? value : value.replace(/[-_]+/g, ' ').replace(/\b\w/g, c => c.toUpperCase())

export function parseCatalog(kind: CatalogKind, data: unknown): CatalogEntry[] {
  if (!Array.isArray(data)) {
    throw new Error('Invalid catalog response')
  }

  const entries = new Map<string, CatalogEntry>()

  for (const row of data) {
    if (!row || typeof row !== 'object' || !text(row.name)) {
      continue
    }

    const name = text(row.name)
    const source = text(kind === 'plugins' ? row.tier : row.source)
    const identifier = text(row.identifier) || name
    const id = `${source}:${identifier}`
    const caps = row.capabilities ?? {}
    const category = text(row.category) || 'uncategorized'
    const categoryLabel = text(row.categoryLabel) || category
    const tags = strings(row.tags)
    const tools = strings(caps.providesTools ?? caps.provides_tools)
    const hooks = strings(caps.providesHooks ?? caps.provides_hooks)
    const middleware = strings(caps.providesMiddleware ?? caps.provides_middleware)
    const commands = strings(row.commands)
    const platforms = strings(row.platforms)
    const requirements = strings(kind === 'plugins' ? caps.requiresEnv ?? caps.requires_env : row.envVars)
    const author = text(row.maintainer ?? row.author)
    const description = text(row.description)

    entries.set(id, {
      id,
      name,
      description,
      overview: text(row.overview),
      category,
      categoryLabel,
      source,
      author,
      identifier,
      installIdentifier:
        kind === 'skills'
          ? skillCatalogInstallIdentifier({
              name,
              source,
              identifier: text(row.identifier),
              installIdentifier: text(row.installIdentifier)
            })
          : null,
      repo: text(row.repo),
      sha: text(row.sha),
      subdir: text(row.subdir),
      version: text(row.version),
      requiresSci: text(row.requiresSci ?? row.requires_sci),
      tags,
      tools,
      hooks,
      middleware,
      commands,
      license: text(row.license) || undefined,
      platforms,
      requirements,
      sourceUrl: webUrl(row.repo || row.sourceUrl),
      docsUrl: webUrl(row.docsUrl ?? row.docs_url),
      imageUrl: kind === 'plugins' ? catalogImageUrl(row.image) : null,
      screenshots:
        kind === 'plugins'
          ? strings(row.screenshots)
              .map(catalogImageUrl)
              .filter((url): url is string => url !== null)
          : [],
      addedAt: Number.isFinite(Date.parse(text(row.addedAt))) ? text(row.addedAt) : undefined,
      updatedAt: Number.isFinite(Date.parse(text(row.updatedAt))) ? text(row.updatedAt) : undefined,
      stars: typeof row.stars === 'number' && Number.isFinite(row.stars) ? row.stars : null,
      search: [
        name,
        description,
        text(row.overview),
        author,
        category,
        categoryLabel,
        source,
        ...tags,
        ...tools,
        ...hooks,
        ...platforms,
        ...requirements,
        ...commands,
        ...middleware
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
    })
  }

  return [...entries.values()]
}

type CatalogScope = ReturnType<typeof capabilityScoped>

async function fetchScopedCatalog(kind: CatalogKind, scope: CatalogScope): Promise<CatalogEntry[]> {
  // Use the authenticated backend's shipped catalogs, never an unrelated site's
  // public snapshot. Explicit undefined prevents a delayed query inheriting a
  // newly selected connection from sciApi's ambient wrapper.
  const response = await sciApi<{ skills?: unknown; entries?: unknown }>({
    ...scope,
    connectionId: scope.connectionId,
    profile: scope.profile,
    path: kind === 'skills' ? '/api/skills/hub/official' : '/api/dashboard/plugins/catalog',
    timeoutMs: 60_000
  })
  const rows = kind === 'skills' ? response.skills : response.entries
  if (!Array.isArray(rows)) throw new Error('Invalid catalog response')
  return parseCatalog(kind, kind === 'skills' ? rows.map(row => ({ ...row, source: 'official' })) : rows)
}

export function fetchCatalog(kind: CatalogKind, scope?: ProfileScope): Promise<CatalogEntry[]> {
  return fetchScopedCatalog(kind, capabilityScoped(scope))
}

export const catalogQuery = (kind: CatalogKind, scope?: ProfileScope) => {
  const request = capabilityScoped(scope)
  return queryOptions({
    queryKey: ['backend-catalog', kind, request.connectionId ?? '', request.profile ?? ''],
    queryFn: () => fetchScopedCatalog(kind, request),
    staleTime: 30 * 60_000,
    gcTime: 30 * 60_000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    refetchOnMount: false,
    retryOnMount: false,
    retry: false
  })
}

export function useCatalog(kind: CatalogKind, scope?: ProfileScope) {
  useStore($apiRequestScope)
  return useQuery({
    ...catalogQuery(kind, scope),
    enabled: query => query.state.status !== 'error'
  })
}

/** Capture the owner now, so changing profiles before idle cannot retarget it. */
export function prefetchCatalogWhenIdle(kind: CatalogKind, scope?: ProfileScope) {
  const query = catalogQuery(kind, scope)
  const id = requestIdleCallback(() => void queryClient.prefetchQuery(query), { timeout: 5_000 })
  return () => cancelIdleCallback(id)
}
