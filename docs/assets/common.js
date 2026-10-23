function validExternal(value) {
  if (!value) return false;
  try { return new URL(value).protocol === 'https:'; } catch { return false; }
}
export const configReady = fetch(new URL('../config.json', import.meta.url))
  .then(response => { if (!response.ok) throw new Error('Configuration unavailable'); return response.json(); })
  .then(config => {
    document.querySelectorAll('[data-config-link]').forEach(link => {
      const value = config[link.dataset.configLink];
      if (validExternal(value)) { link.href = value; link.target = '_blank'; link.rel = 'noopener noreferrer'; }
    });
    document.querySelectorAll('[data-release-status]').forEach(node => { node.textContent = config.release_status; });
    if (validExternal(config.paper_url)) {
      document.querySelectorAll('[data-paper-status]').forEach(node => {
        const link = document.createElement('a'); link.href = config.paper_url;
        link.textContent = 'Read the paper on arXiv ↗'; link.rel = 'noopener noreferrer'; link.target = '_blank';
        node.replaceChildren(link);
      });
    }
    return config;
  }).catch(error => { console.warn(error.message); return {}; });

export function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
export function fixed(value, signed = false) {
  if (!Number.isFinite(value)) return '—';
  return `${signed && value > 0 ? '+' : ''}${value.toFixed(2)}`.replace('-', '−');
}
