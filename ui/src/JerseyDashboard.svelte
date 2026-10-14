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
      const old = history[id] ?? []
      const latest = old[old.length - 1]
      if (heard && (!latest || latest.at !== heard)) {
        history[id] = [...old, { at: heard, rssi: node.rssi ?? null, snr: node.snr ?? null }].slice(-maxSamples)
      }
    }
    history = history
  }
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
    notifications = typeof Notification !== 'undefined' && Notification.permission === 'granted'
    record()
    const timer = window.setInterval(record, 15000)
    return () => clearInterval(timer)
  })
</script>

<section class="rounded-lg border border-[#F2B134]/40 bg-[#15191D]/85 p-3 text-green-50" aria-label="The Family Business network dashboard">
  <div class="flex items-center justify-between gap-2 flex-wrap">
    <h2 class="!bg-none !p-0 text-lg">🤌 The Family Business <span class="text-xs font-normal text-[#F2B134]">Live network intelligence</span></h2>
    <div class="flex gap-2 text-xs items-center">
      <span class:!text-green-300={$connectionStatus === 'connected'} class="text-amber-300">{$connectionStatus}</span>
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
  <p class="text-xs text-white/60 mt-1">Health score is a local heuristic based on recently heard, direct, and positioned nodes—not a measurement of delivery reliability. {sampleCount} packets in the current log.</p>
  <div class="mt-2 flex items-center gap-2 flex-wrap text-sm">
    <label for="jersey-node">How Ya Doin'? Signal:</label>
    <select id="jersey-node" class="input max-w-52" bind:value={selected}>
      <option value="">Choose a node</option>
      {#each $nodes as node (node.num)}
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
    <div class="mt-2 text-xs" role="status"><strong class="text-[#F2B134]">We Got a Problem!</strong> {alerts[0]}</div>
  {/if}
</section>
