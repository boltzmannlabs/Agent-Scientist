/** Backend-owned skill browsing and explicit installation; no remote picker iframe. */

import { Button, Codicon, host, Input, useI18n } from '@sci/plugin-sdk'
import { useEffect, useRef, useState } from 'react'

import { useBots } from './i18n'
import { botWorkspaceOwnerKey, requestForBot } from './routing'
import type { RosterRow } from './types'

/** One `skills.manage action=search` hit. */
interface HubSkillResult {
  description?: string
  identifier?: string
  name: string
}
interface HubSkillsSectionProps {
  /** Existing bot to route through; omitted for the launch profile at create time. */
  bot?: RosterRow
  onInstalled?: (name: string) => void
}

export function HubSkillsSection({ bot, onInstalled }: HubSkillsSectionProps) {
  const b = useBots()
  const { t } = useI18n()
  const h = t.skills.hub
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<HubSkillResult[] | null>(null)
  const [searching, setSearching] = useState(false)
  const [installing, setInstalling] = useState<null | string>(null)
  const [installed, setInstalled] = useState<Record<string, boolean>>({})
  const [browseHub, setBrowseHub] = useState(false)
  const [page, setPage] = useState(1)
  const [pages, setPages] = useState(1)
  const generation = useRef(0)
  const ownerGeneration = useRef(0)
  const owner = bot ? botWorkspaceOwnerKey(bot) : 'ambient'
  useEffect(() => {
    ownerGeneration.current++
    generation.current++
    setResults(null)
    setInstalled({})
    setSearching(false)
    setInstalling(null)
    setBrowseHub(false)

    return () => {
      generation.current++
      ownerGeneration.current++
    }
  }, [owner])

  const lookup = async (browsePage?: number) => {
    const q = query.trim()

    if (searching || (browsePage === undefined && !q)) {
      return
    }
    const attempt = ++generation.current
    setSearching(true)
    setResults(null)
    setBrowseHub(browsePage !== undefined)

    try {
      const params =
        browsePage === undefined
          ? { action: 'search', query: q }
          : { action: 'browse', source: 'official', page: browsePage, page_size: 20 }

      const scoped = { ...params, ...(bot ? { profile: bot.name } : {}) }

      const res: { items?: HubSkillResult[]; results?: HubSkillResult[]; page?: number; total_pages?: number } =
        await (bot ? requestForBot(bot, 'skills.manage', scoped) : host.request('skills.manage', scoped))

      if (attempt !== generation.current) {
        return
      }
      setResults(res.items ?? res.results ?? [])
      setPage(res.page ?? 1)
      setPages(res.total_pages ?? 1)
    } catch (error) {
      if (attempt === generation.current) {
        setResults(null)
        host.notifyError(error, h.actionFailed)
      }
    } finally {
      if (attempt === generation.current) {
        setSearching(false)
      }
    }
  }

  const install = async (name: string, displayName?: string) => {
    const label = displayName || name

    if (installing) {
      return
    }

    setInstalling(label)
    const installOwner = ownerGeneration.current

    try {
      // Existing bots must use their owner route; the active gateway is not
      // necessarily the gateway that owns the bot. Create-time installs stay
      // ambient because there is no bot row to route yet.
      const params = {
        action: 'install',
        query: name,
        ...(bot ? { profile: bot.name } : {})
      }

      await (bot ? requestForBot(bot, 'skills.manage', params) : host.request('skills.manage', params))

      if (installOwner !== ownerGeneration.current) {
        return
      }
      setInstalled(prev => ({
        ...prev,
        [label]: true
      }))
      host.notify({
        kind: 'success',
        message: b.tools.installed(label)
      })

      if (typeof onInstalled === 'function') {
        onInstalled(label)
      }
    } catch (err) {
      if (installOwner === ownerGeneration.current) {
        host.notifyError(err, b.tools.installFailed(label))
      }
    } finally {
      if (installOwner === ownerGeneration.current) {
        setInstalling(null)
      }
    }
  }

  return (
    <div className="grid gap-1.5 border-t border-(--ui-stroke-secondary) pt-2">
      <div className="flex items-baseline justify-between gap-2">
        <div className="text-[0.7rem] font-medium text-(--ui-text-secondary)">{b.tools.skillsHub}</div>
        <Button
          className="text-[0.65rem] text-(--ui-text-quaternary) hover:text-(--ui-text-secondary)"
          disabled={searching}
          onClick={() => {
            if (browseHub) {
              generation.current++
              setBrowseHub(false)
              setResults(null)
            } else {
              void lookup(1)
            }
          }}
          size="inline"
          variant="text"
        >
          {browseHub ? h.pickerHide : h.pickerBrowse}
        </Button>
      </div>
      {browseHub && pages > 1 ? (
        <div className="flex gap-1.5">
          <Button disabled={searching || page <= 1} onClick={() => void lookup(page - 1)} size="sm" variant="ghost">
            {t.ui.pagination.previous}
          </Button>
          <span>
            {page} / {pages}
          </span>
          <Button disabled={searching || page >= pages} onClick={() => void lookup(page + 1)} size="sm" variant="ghost">
            {t.ui.pagination.next}
          </Button>
        </div>
      ) : null}
      <div className="flex gap-1.5">
        <Input
          className="h-7 flex-1 text-xs"
          onChange={event => setQuery(event.target.value)}
          onKeyDown={event => {
            // IME guard: Enter confirming a composed word must not search.
            if (event.nativeEvent?.isComposing || event.keyCode === 229) {
              return
            }

            if (event.key === 'Enter') {
              event.preventDefault()
              void lookup()
            }
          }}
          placeholder={b.tools.searchHub}
          value={query}
        />
        <Button disabled={searching || !query.trim()} onClick={() => void lookup()} size="sm" variant="secondary">
          {searching ? h.searching : h.search}
        </Button>
      </div>
      {searching ? <div className="px-1 text-[0.65rem] text-(--ui-text-quaternary)">{b.tools.searchHint}</div> : null}
      {results === null ? null : results.length === 0 ? (
        <div className="px-1 py-1.5 text-[0.7rem] text-(--ui-text-quaternary)">{h.noResults}</div>
      ) : (
        <div
          className="overflow-y-auto overscroll-contain"
          style={{
            maxHeight: 150
          }}
        >
          <div className="grid gap-1">
            {results.map(r => (
              <div className="flex items-center gap-2 text-xs" key={r.name}>
                <div className="min-w-0 flex-1">
                  <div className="truncate font-medium">{r.name}</div>
                  {r.description ? (
                    <div className="truncate text-[0.65rem] text-(--ui-text-quaternary)">{r.description}</div>
                  ) : null}
                </div>
                {installed[r.name] ? (
                  <span className="flex shrink-0 items-center gap-0.5 text-[0.65rem] text-(--ui-text-tertiary)">
                    <Codicon name="check" size="0.65rem" />
                    {h.installed}
                  </span>
                ) : (
                  <Button
                    aria-label={b.tools.installHint(r.name)}
                    className="shrink-0 px-2 font-semibold"
                    disabled={installing !== null}
                    onClick={() => void install(r.identifier || r.name, r.name)}
                    size="sm"
                    variant="ghost"
                  >
                    {installing === r.name ? '…' : '+'}
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
