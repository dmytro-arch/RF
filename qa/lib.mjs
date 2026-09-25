/**
 * Чистые (без браузера и сети) helpers для QA-аудита royalfoam.art.
 * Используются и из audit.mjs (Playwright), и из selftest.mjs (юнит-проверки).
 */

/** Приводим href к абсолютному URL. Возвращаем null, если ссылка не проверяемая. */
export function normalizeUrl(href, baseUrl) {
  if (typeof href !== 'string') return null;
  const raw = href.trim();
  if (!raw) return null;
  // Якоря, javascript:, mailto:, tel: — не страницы, их не краулим.
  if (/^(#|javascript:|mailto:|tel:|data:|blob:)/i.test(raw)) return null;
  let abs;
  try {
    abs = new URL(raw, baseUrl);
  } catch {
    return null;
  }
  if (abs.protocol !== 'http:' && abs.protocol !== 'https:') return null;
  // Якорь на той же странице не меняет URL.
  abs.hash = '';
  return abs.toString();
}

export function isInternal(url, origin) {
  try {
    return new URL(url).origin === new URL(origin).origin;
  } catch {
    return false;
  }
}

/** Убираем «хвост», чтобы /page и /page/ считались одной страницей. */
export function canonicalPath(url) {
  try {
    const u = new URL(url);
    let p = u.pathname;
    if (p.length > 1 && p.endsWith('/')) p = p.slice(0, -1);
    return (p || '/') + (u.search || '');
  } catch {
    return url;
  }
}

const SKIP_RE = /\.(png|jpe?g|gif|webp|svg|avif|ico|css|js|mjs|woff2?|ttf|otf|mp4|webm|pdf|zip|xml|json)(\?|$)/i;

export function looksLikeAsset(url) {
  return SKIP_RE.test(url);
}

/**
 * Достаём ссылки и формы из HTML. Парсер намеренно простой (regex),
 * чтобы модуль работал и в node без DOM-зависимостей.
 */
export function extractLinks(html, baseUrl) {
  const out = [];
  const re = /<a\b[^>]*>/gi;
  let m;
  while ((m = re.exec(html))) {
    const tag = m[0];
    const href = attr(tag, 'href');
    if (href === null) continue;
    const url = normalizeUrl(href, baseUrl);
    out.push({ href, url, text: attr(tag, 'title') || '', title: attr(tag, 'title') || '' });
  }
  return out;
}

export function extractImages(html, baseUrl) {
  const out = [];
  const re = /<img\b[^>]*>/gi;
  let m;
  while ((m = re.exec(html))) {
    const tag = m[0];
    const src = attr(tag, 'src');
    out.push({
      src,
      url: src ? normalizeUrl(src, baseUrl) : null,
      alt: attr(tag, 'alt'),
      hasAlt: /\balt\s*=/i.test(tag),
    });
  }
  return out;
}

export function extractForms(html) {
  const out = [];
  const re = /<form\b[^>]*>[\s\S]*?<\/form>/gi;
  let m;
  while ((m = re.exec(html))) {
    const block = m[0];
    const open = block.match(/<form\b[^>]*>/i)[0];
    const fields = [];
    const fieldRe = /<(input|textarea|select)\b[^>]*>/gi;
    let f;
    while ((f = fieldRe.exec(block))) {
      const tag = f[0];
      const type = (attr(tag, 'type') || (f[1].toLowerCase() === 'textarea' ? 'textarea' : 'text')).toLowerCase();
      if (type === 'hidden') continue;
      fields.push({
        name: attr(tag, 'name') || attr(tag, 'id') || '',
        type,
        required: /\brequired\b/i.test(tag),
        placeholder: attr(tag, 'placeholder') || '',
      });
    }
    out.push({
      action: attr(open, 'action') || '',
      method: (attr(open, 'method') || 'GET').toUpperCase(),
      id: attr(open, 'id') || '',
      fields,
    });
  }
  return out;
}

function attr(tag, name) {
  const re = new RegExp(`\\b${name}\\s*=\\s*("([^"]*)"|'([^']*)'|([^\\s>]+))`, 'i');
  const m = tag.match(re);
  if (!m) return null;
  return (m[2] ?? m[3] ?? m[4] ?? '').trim();
}

/**
 * Классифицируем результат проверки ссылки.
 * expected — набор «правильных» URL сайта (из sitemap / REST API).
 */
export function classifyLink({ url, status, finalUrl, known }) {
  if (status === 0) return { level: 'error', code: 'UNREACHABLE' };
  if (status >= 500) return { level: 'error', code: `HTTP_${status}` };
  if (status === 404 || status === 410) return { level: 'error', code: `HTTP_${status}` };
  if (status >= 400) return { level: 'error', code: `HTTP_${status}` };
  if (status >= 300 && status < 400) {
    return { level: 'warn', code: 'REDIRECT', detail: finalUrl };
  }
  if (url && finalUrl && canonicalPath(url) !== canonicalPath(finalUrl)) {
    return { level: 'warn', code: 'SOFT_REDIRECT', detail: finalUrl };
  }
  if (known && known.size && !known.has(canonicalPath(finalUrl || url))) {
    return { level: 'info', code: 'NOT_IN_SITEMAP' };
  }
  return { level: 'ok', code: 'OK' };
}

/** Ссылка-само ссылка: кнопка, которая ведёт на ту же страницу. */
export function isSelfLink(from, to) {
  if (!to) return false;
  return canonicalPath(from) === canonicalPath(to);
}

export function summarize(rows) {
  const by = { ok: 0, warn: 0, error: 0, info: 0 };
  const codes = {};
  for (const r of rows) {
    by[r.level] = (by[r.level] || 0) + 1;
    codes[r.code] = (codes[r.code] || 0) + 1;
  }
  return { total: rows.length, by, codes };
}

export function renderMarkdown({ site, startedAt, pages, links, consoleErrors, overflow, forms, timings }) {
  const l = summarize(links);
  const out = [];
  out.push(`# QA-отчёт ${site}`);
  out.push('');
  out.push(`Проверено страниц: ${pages.length}. Старт: ${startedAt}`);
  out.push('');
  out.push(`## Ссылки: ${l.total} (ошибок ${l.by.error || 0}, редиректов ${l.by.warn || 0})`);
  for (const [code, n] of Object.entries(l.codes)) out.push(`- ${code}: ${n}`);
  out.push('');
  const bad = links.filter((x) => x.level === 'error');
  if (bad.length) {
    out.push('### Битые ссылки');
    for (const b of bad) out.push(`- ${b.code} ${b.url} (со страницы ${b.from})`);
  }
  const redirects = links.filter((x) => x.code === 'REDIRECT' || x.code === 'SOFT_REDIRECT');
  if (redirects.length) {
    out.push('');
    out.push('### Редиректы');
    for (const r of redirects) out.push(`- ${r.url} → ${r.detail}`);
  }
  out.push('');
  out.push(`## Ошибки в консоли: ${consoleErrors.length}`);
  for (const e of consoleErrors) out.push(`- [${e.page}] ${e.type}: ${e.text}`);
  out.push('');
  out.push(`## Горизонтальный скролл (искажение вёрстки): ${overflow.length}`);
  for (const o of overflow) out.push(`- ${o.page} @${o.width}px: scrollWidth ${o.scrollWidth} > clientWidth ${o.clientWidth}`);
  out.push('');
  out.push(`## Формы: ${forms.length}`);
  for (const f of forms) out.push(`- ${f.page}: ${f.fields.length} полей, action=${f.action || '(нет)'}`);
  out.push('');
  out.push('## Время загрузки');
  for (const t of timings) out.push(`- ${t.page}: ${t.ms} мс`);
  return out.join('\n');
}

/* ------------------------------------------------------------------ */
/* Агрегация результатов прогона (для summarize.mjs)                   */
/* ------------------------------------------------------------------ */

/** /services/brand-activation-props/ → /services/* — чтобы схлопнуть однотипные находки. */
export function urlPattern(url) {
  try {
    const u = new URL(url);
    const seg = u.pathname.split('/').filter(Boolean);
    if (seg.length <= 1) return u.origin + u.pathname;
    return u.origin + '/' + seg[0] + '/*';
  } catch {
    return url;
  }
}

/**
 * Схлопывает дубли: одна и та же ссылка на 200 страницах = одна строка со счётчиком.
 * byPattern=true группирует ещё и по первому сегменту пути (/service/*).
 */
export function groupLinks(rows, { byPattern = false } = {}) {
  const map = new Map();
  for (const r of rows) {
    if (!r || r.code === 'FOUND') continue;
    const key = byPattern ? `${r.code}|${urlPattern(r.url)}` : `${r.code}|${r.url}`;
    if (!map.has(key)) {
      map.set(key, { code: r.code, level: r.level, url: byPattern ? urlPattern(r.url) : r.url, count: 0, from: [], detail: r.detail });
    }
    const g = map.get(key);
    g.count += 1;
    if (r.from && g.from.length < 5 && !g.from.includes(r.from)) g.from.push(r.from);
    if (!g.detail && r.detail) g.detail = r.detail;
  }
  return [...map.values()].sort((a, b) => b.count - a.count);
}

/** Нормализуем текст ошибки, чтобы «одна и та же ошибка на 200 страницах» не считалась 200 раз. */
export function normalizeError(text) {
  return String(text || '')
    .replace(/https?:\/\/\S+/g, '<url>')
    .replace(/\d+/g, '<n>')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 160);
}

export function groupConsole(errors) {
  const map = new Map();
  for (const e of errors) {
    const key = `${e.type}|${normalizeError(e.text)}`;
    if (!map.has(key)) map.set(key, { type: e.type, text: normalizeError(e.text), count: 0, pages: [] });
    const g = map.get(key);
    g.count += 1;
    if (g.pages.length < 5 && !g.pages.includes(e.page)) g.pages.push(e.page);
  }
  return [...map.values()].sort((a, b) => b.count - a.count);
}

/** Уникальные формы: одинаковый набор полей на 200 страницах — это одна форма. */
export function groupForms(forms) {
  const map = new Map();
  for (const f of forms) {
    const sig = `${f.method}|${f.action}|${(f.fields || []).map((x) => `${x.name || x.type}:${x.type}`).join(',')}`;
    if (!map.has(key0(sig))) map.set(key0(sig), { signature: sig, count: 0, pages: [], fields: f.fields || [] });
    const g = map.get(key0(sig));
    g.count += 1;
    if (g.pages.length < 5 && !g.pages.includes(f.page)) g.pages.push(f.page);
  }
  return [...map.values()].sort((a, b) => b.count - a.count);
}
function key0(s) {
  return s;
}

export function slowestPages(timings, n = 10) {
  return [...timings].sort((a, b) => b.ms - a.ms).slice(0, n);
}
