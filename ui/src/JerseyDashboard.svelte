<script lang="ts">
  import { onMount } from 'svelte'
  import { connectionStatus, nodes, nodeInactiveTimer, packets, type NodeInfo } from 'api/src/vars'
  type Sample = { at: number; rssi: number | null; snr: number | null }
  let history: Record<string, Sample[]> = {}
  let watched: Record<string, boolean> = {}
  let previousActive: Record<string, boolean> = {}
  let alerts: string[] = []
  let selected = ''
  let showHistory = false
  let notifications = false
  let compact = false
  let search = ''
  let onlyWatched = false
  let showAlerts = true
  let signalWarning = -110
  let weakSignals: Record<string, boolean> = {}
  let now = Date.now()
  const maxSamples = 90
  const threshold = () => ($nodeInactiveTimer ?? 60) * 60 * 1000
  const active = (n: NodeInfo) => n.lastHeard > 0 && now - n.lastHeard * 1000 < threshold()
  $: activeNodes = $nodes.filter(active)
  $: inactiveNodes = $nodes.filter((n) => !active(n))
  $: directNodes = activeNodes.filter((n) => n.hopsAway === 0)
  $: positioned = activeNodes.filter((n) => n.position?.latitudeI && n.position?.longitudeI)
  $: sampleCount = $packets.length
  $: quality = $nodes.length ? Math.round((activeNodes.length / $nodes.length * 70) + (directNodes.length / $nodes.length * 20) + (positioned.length / $nodes.length * 10)) : null
  $: chosen = $nodes.find((n) => String(n.num) === selected)
  $: visibleNodes = $nodes.filter((n) => (!onlyWatched || watched[String(n.num)]) && ((n.user?.longName || String(n.num)).toLowerCase().includes(search.trim().toLowerCase())))
  $: watchedCount = Object.values(watched).filter(Boolean).length
  $: series = history[selected] ?? []
  function record() {
    now = Date.now()
    for (const node of $nodes) {
      const id = String(node.num)
      const heard = node.lastHeard || 0
      const isActive = active(node)
      if (watched[id] && previousActive[id] === true && !isActive) {
        const message = `${node.user?.longName || id} went quiet — where'd everybody go?`
        alerts = [message, ...alerts].slice(0, 15)
        if (notifications && typeof Notification !== 'undefined' && Notification.permission === 'granted') new Notification('We Got a Problem!', { body: message })
      }
      previousActive[id] = isActive
      const weak = isActive && typeof node.rssi === 'number' && node.rssi <= signalWarning
      if (watched[id] && weak && weakSignals[id] === false) {
        const message = `${node.user?.longName || id} has weak signal (${node.rssi} dBm)`
        alerts = [message, ...alerts].slice(0, 15)
        if (notifications && typeof Notification !== 'undefined' && Notification.permission === 'granted') new Notification('Weak Mesh Signal', { body: message })
      }
      weakSignals[id] = weak
      const old = history[id] ?? []
      const latest = old[old.length - 1]
      if (heard && (!latest || latest.at !== heard)) {
        history[id] = [...old, { at: heard, rssi: node.rssi ?? null, snr: node.snr ?? null }].slice(-maxSamples)
      }
    }
    history = history
  }
  function clearAlerts() { alerts = [] }
  function toggleCompact() { compact = !compact; try { localStorage.setItem('jerseyCompact', String(compact)) } catch {} }
  function toggleWatch(id: string) {
    watched = { ...watched, [id]: !watched[id] }
    try { localStorage.setItem('jerseyWatch', JSON.stringify(watched)) } catch {}
  }
  async function enableNotifications() {
    if (typeof Notification === 'undefined') return
    notifications = await Notification.requestPermission() === 'granted'
  }
  onMount(() => {
    try { watched = JSON.parse(localStorage.getItem('jerseyWatch') || '{}') } catch {}
    try { compact = localStorage.getItem('jerseyCompact') === 'true' } catch {}
    try { const stored = Number(localStorage.getItem('jerseySignalWarning')); if (stored >= -130 && stored <= -40) signalWarning = stored } catch {}
    notifications = typeof Notification !== 'undefined' && Notification.permission === 'granted'
    record()
    const timer = window.setInterval(record, 15000)
    return () => clearInterval(timer)
  })
</script>

<section class="rounded-lg border border-[#F2B134]/40 bg-[#15191D]/85 p-3 text-green-50" aria-label="The Family Business network dashboard">
  <div class="flex items-center justify-between gap-3 flex-wrap">
    <div><h2 class="!bg-none !p-0 text-lg">🤌 The Family Business</h2><p class="text-xs text-white/60">Network overview · {watchedCount} watched · {sampleCount} packets</p></div>
    <div class="flex gap-2 text-xs items-center">
      <span class={$connectionStatus === 'connected' ? 'text-green-300' : 'text-amber-300'} aria-live="polite">● {$connectionStatus}</span>
      <button class="btn" on:click={toggleCompact} aria-pressed={compact}>{compact ? 'Expand' : 'Compact'} view</button>
      <button class="btn" on:click={() => showHistory = !showHistory}>{showHistory ? 'Hide' : 'Show'} signal history</button>
      <button class="btn" on:click={enableNotifications}>Alerts {notifications ? 'enabled' : 'opt in'}</button>
    </div>
  </div>
  <div class="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-6 gap-2 mt-2 text-sm">
    <div class="card"><div class="text-[#F2B134]">Da Neighborhood</div><strong>{$nodes.length} nodes</strong></div>
    <div class="card"><div class="text-[#F2B134]">You Still Alive?</div><strong>{activeNodes.length} active</strong></div>
    <div class="card"><div class="text-[#F2B134]">Where'd Everybody Go?</div><strong>{inactiveNodes.length} inactive</strong></div>
    <div class="card"><div class="text-[#F2B134]">Direct Neighbors</div><strong>{directNodes.length} one hop</strong></div>
    <div class="card"><div class="text-[#F2B134]">What Exit?</div><strong>{positioned.length} mapped</strong></div>
    <div class="card"><div class="text-[#F2B134]">The Boss's Report</div><strong>{quality === null ? 'No data' : quality + '/100'}</strong></div>
  </div>
  {#if !compact}
  <p class="text-xs text-white/60 mt-1">Health score is a local heuristic based on recently heard, direct, and positioned nodes—not a measurement of delivery reliability. {sampleCount} packets in the current log.</p>
  <div class="mt-3 flex items-center gap-2 flex-wrap text-sm">
    <input class="input max-w-52" aria-label="Search nodes" placeholder="Search the neighborhood…" bind:value={search} />
    <label class="flex items-center gap-1 text-xs"><input type="checkbox" bind:checked={onlyWatched} /> Watched only</label>
    <label for="jersey-signal-threshold">Weak signal alert:</label>
    <select id="jersey-signal-threshold" class="input" bind:value={signalWarning} on:change={() => { try { localStorage.setItem('jerseySignalWarning', String(signalWarning)) } catch {} }}>
      <option value={-120}>−120 dBm</option><option value={-110}>−110 dBm</option><option value={-100}>−100 dBm</option><option value={-90}>−90 dBm</option>
    </select>
    <label for="jersey-node">How Ya Doin'? Signal:</label>
    <select id="jersey-node" class="input max-w-52" bind:value={selected}>
      <option value="">Choose a node</option>
      {#each visibleNodes as node (node.num)}
        <option value={String(node.num)}>{node.user?.longName || node.num}</option>
      {/each}
    </select>
    {#if chosen}
      <span>RSSI: {chosen.rssi ?? 'unknown'} dBm · SNR: {chosen.snr ?? 'unknown'} dB · {active(chosen) ? 'You Good!' : 'Fuggedaboutit!'}</span>
      <button class="btn text-xs" on:click={() => toggleWatch(selected)}>{watched[selected] ? 'Unwatch' : 'Watch'} offline</button>
    {/if}
  </div>
  {#if showHistory && chosen}
    <div class="mt-2 rounded bg-black/30 p-2 text-xs">
      <div class="text-[#F2B134] mb-1">How Ya Doin'? — observed signal samples ({series.length}/{maxSamples})</div>
      {#if series.length}
        <div class="flex items-end gap-px h-16" role="img" aria-label="Historical RSSI samples from weakest to strongest">
          {#each series as sample}
            <div class="grow min-w-[2px] bg-[#F2B134]" title={new Date(sample.at * 1000).toLocaleString() + ': RSSI ' + (sample.rssi ?? 'unknown')} style:height={sample.rssi === null ? '3px' : Math.max(3, Math.min(64, (sample.rssi + 130) / 90 * 64)) + 'px'}></div>
          {/each}
        </div>
        <div class="text-white/60 mt-1">Oldest → newest · approximate RSSI scale −130 to −40 dBm</div>
      {:else}
        <div>No signal samples observed yet. Stay tuned, capisce?</div>
      {/if}
    </div>
  {/if}
  {#if alerts.length}
    <div class="mt-3 flex items-center justify-between gap-2 text-xs" role="status"><strong class="text-[#F2B134]">We Got a Problem! · {alerts.length} alerts</strong><div class="flex gap-2"><button class="btn" on:click={() => showAlerts = !showAlerts}>{showAlerts ? 'Hide' : 'Show'}</button><button class="btn" on:click={clearAlerts}>Clear</button></div></div>
    {#if showAlerts}<ul class="mt-1 max-h-28 overflow-y-auto text-xs text-white/80">{#each alerts as alert, i (i)}<li class="border-t border-white/10 py-1">{alert}</li>{/each}</ul>{/if}
  {/if}
  {/if}
</section>
