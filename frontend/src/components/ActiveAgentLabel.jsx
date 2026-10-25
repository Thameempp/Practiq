import { useSyncExternalStore } from 'react'


export function ActiveAgentLabel({ store }) {
  const { agents } = useSyncExternalStore(store.subscribe, store.getSnapshot)
  const active = agents.at(-1)
  if (!active) return null
  return <span className="active-agent-label" role="status" aria-atomic="true"
    title={agents.map(({ name }) => name).join(' · ')}>
    {active.name}
  </span>
}
