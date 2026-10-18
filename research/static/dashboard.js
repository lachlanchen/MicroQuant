const byId = (id) => document.getElementById(id);
const words = (value) => String(value || 'pending').replaceAll('_', ' ');
const date = (stamp) => stamp ? new Date(stamp * 1000).toLocaleString() : 'unknown';
const money = (amount) => new Intl.NumberFormat('en-US', {style: 'currency', currency: 'USD', minimumFractionDigits: 2}).format(amount);
async function read(path) {
  const response = await fetch(path, {cache: 'no-store'});
  if (!response.ok) throw new Error('Service unavailable');
  return response.json();
}
async function refresh() {
  try {
    const [status, news, analysis, events] = await Promise.all([
      read('/api/status'), read('/api/news'), read('/api/analysis'), read('/api/events'),
    ]);
    byId('connection').textContent = status.broker.status === 'ok' && !status.broker_stale ? 'Collecting demo observations · virtual trading only' : 'Service online · demo data is not ready';
    byId('equity').textContent = money(status.paper.equity);
    byId('pnl').textContent = money(status.paper.net_pnl);
    byId('trades').textContent = `${status.paper.closed_trades} closed paper trades · unvalidated`;
    byId('broker').textContent = words(status.broker.status);
    byId('brokerDetail').textContent = `${status.broker.demo_verified ? 'Demo verified' : 'Demo not verified'} · ${date(status.broker.observed_at)}`;
    byId('paperStatus').textContent = words(status.paper.status);
    const feeds = Object.values(status.feeds);
    byId('feedStatus').textContent = `${feeds.filter((feed) => feed.ok).length} / ${feeds.length} feeds responding`;
    byId('analysisHeading').textContent = `${status.model} · ${words(status.analysis.status)}`;
    if (analysis) {
      byId('summary').textContent = analysis.payload.summary;
      byId('risks').replaceChildren(...analysis.payload.risks.map((risk) => { const li = document.createElement('li'); li.textContent = risk; return li; }));
      byId('nextExperiment').textContent = analysis.payload.next_experiment;
      byId('analysisTime').textContent = `Last completed note: ${date(analysis.observed)} · Research only`;
    }
    byId('news').replaceChildren(...news.slice(0, 12).map((item) => {
      const article = document.createElement('article');
      const link = document.createElement('a');
      link.textContent = item.title; link.href = item.url; link.target = '_blank'; link.rel = 'noopener noreferrer';
      const meta = document.createElement('p');
      meta.textContent = `${item.source} · Published ${date(item.published)} · Collected ${date(item.first_seen)}`;
      article.append(link, meta); return article;
    }));
    byId('events').replaceChildren(...events.map((item) => {
      const li = document.createElement('li');
      li.textContent = `${date(item.observed)} · ${words(item.kind)} · ${words(item.payload.status || item.payload.type)}`;
      return li;
    }));
    byId('updated').textContent = `Last refresh: ${date(status.now)}`;
  } catch {
    byId('connection').textContent = 'Connection interrupted. Displayed observations may be stale.';
  }
}
refresh();
setInterval(refresh, 30000);
