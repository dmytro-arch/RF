#!/usr/bin/env node
/**
 * Функциональный QA-аудит сайта royalfoam.art.
 *
 * Два режима:
 *   node audit.mjs                — браузерный (Playwright): консоль, вёрстка, формы, ссылки
 *   node audit.mjs --no-browser   — только HTTP: ссылки, редиректы, статусы, alt у картинок
 *                                   (браузер не нужен, ставится одним npm install)
 *
 * Что проверяет браузерный режим:
 *  1. Краулинг всех внутренних страниц (BFS от главной).
 *  2. Ошибки JS в консоли + необработанные исключения + упавшие запросы.
 *  3. Все ссылки: статус ответа, редиректы, битые (404/5xx), кнопки «в никуда» (ссылка на ту же страницу).
 *  4. Вёрстка: горизонтальный скролл на 1440 / 1024 / 768 / 390 px.
 *  5. Формы: состав полей, поля без подписи, заполнение и (опционально) отправка.
 *  6. Время загрузки страниц.
 *
 * Запуск:
 *   cd qa && npm install && npx playwright install chromium
 *   node audit.mjs                       # быстрый прогон: 25 страниц
 *   node audit.mjs --max-pages 200       # полный обход
 *   node audit.mjs --submit-form         # реально отправить форму на /contact/
 *   node audit.mjs --no-browser          # без Chromium
 */
import fs from 'node:fs';
import path from 'node:path';
import {
  normalizeUrl,
  isInternal,
  canonicalPath,
  looksLikeAsset,
  extractLinks,
  extractImages,
  extractForms,
  classifyLink,
  isSelfLink,
  renderMarkdown,
  groupLinks,
  groupConsole,
  groupForms,
  findForbidden,
  stripTags,
} from './lib.mjs';

const SITE = arg('site', 'https://royalfoam.art/');
const MAX_PAGES = Number(arg('max-pages', '25'));
const OUT = arg('out', 'out/report.json');
const SUBMIT_FORM = process.argv.includes('--submit-form');
const HTTP_ONLY = process.argv.includes('--no-browser');
const CONCURRENCY = Number(arg('concurrency', '4'));
const VIEWPORTS = [1440, 1024, 768, 390];
const UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36';

function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 && process.argv[i + 1] ? process.argv[i + 1] : def;
}

const origin = new URL(SITE).origin;

// Правила контентной проверки (чужой бренд, leftover-текст, обязательные слова).
const RULES_PATH = path.join(path.dirname(new URL(import.meta.url).pathname), 'content-checks.json');
const RULES = fs.existsSync(RULES_PATH) ? JSON.parse(fs.readFileSync(RULES_PATH, 'utf8')) : { forbidden: [], required: [] };

function checkContent(pageUrl, text) {
  for (const r of findForbidden(text, RULES.forbidden)) {
    linkRows.push({ url: r.text, level: 'error', code: 'FORBIDDEN_TEXT', from: pageUrl, detail: r.why });
  }
  for (const r of RULES.required || []) {
    if (!String(text || '').toLowerCase().includes(String(r.text).toLowerCase())) {
      linkRows.push({ url: `нет «${r.text}»`, level: 'warn', code: 'MISSING_REQUIRED_TEXT', from: pageUrl, detail: r.why });
    }
  }
}
const startedAt = new Date().toISOString();

const linkRows = [];
const consoleErrors = [];
const overflow = [];
const timings = [];
const formsFound = [];
const pagesVisited = [];

HTTP_ONLY ? await crawlHttp() : await crawlBrowser();

/* ------------------------------------------------------------------ */
/* Режим 1: только HTTP (без браузера)                                 */
/* ------------------------------------------------------------------ */
async function crawlHttp() {
  const queue = [SITE];
  const seen = new Set([canonicalPath(SITE)]);

  while (queue.length && pagesVisited.length < MAX_PAGES) {
    const url = queue.shift();
    const t0 = Date.now();
    let res, html;
    try {
      res = await fetch(url, { redirect: 'follow', headers: { 'user-agent': UA } });
      html = await res.text();
    } catch (e) {
      consoleErrors.push({ page: url, type: 'navigation', text: String(e.message || e).slice(0, 300) });
      continue;
    }
    const ms = Date.now() - t0;
    timings.push({ page: url, ms });
    pagesVisited.push(url);

    if (res.status >= 400) {
      linkRows.push({ url, level: 'error', code: `HTTP_${res.status}`, from: 'crawl' });
    }
    if (canonicalPath(res.url) !== canonicalPath(url)) {
      linkRows.push({ url, level: 'warn', code: 'SOFT_REDIRECT', from: 'crawl', detail: res.url });
    }

    // картинки без alt
    for (const img of extractImages(html, url)) {
      if (!img.hasAlt || img.alt === '') {
        linkRows.push({ url: img.url || img.src || '(без src)', level: 'info', code: 'IMAGE_NO_ALT', from: url });
      }
    }

    // формы
    for (const f of extractForms(html)) {
      formsFound.push({ page: url, ...f });
      for (const fl of f.fields) {
        if (!fl.placeholder && ['text', 'textarea', 'email', 'tel'].includes(fl.type) && !fl.name) {
          linkRows.push({ url: `${url}#form-field`, level: 'info', code: 'FIELD_WITHOUT_LABEL', from: url });
        }
      }
    }

    checkContent(url, stripTags(html));

    // ссылки
    const internal = new Set();
    for (const a of extractLinks(html, url)) {
      if (!a.url) continue;
      if (looksLikeAsset(a.url)) continue;
      if (!isInternal(a.url, origin)) {
        linkRows.push({ url: a.url, level: 'info', code: 'EXTERNAL', from: url, text: a.text });
        continue;
      }
      if (isSelfLink(url, a.url)) {
        // Без DOM не отличить «кнопку в никуда» от пункта меню — поэтому только info.
        linkRows.push({ url: a.url, level: 'info', code: 'SELF_LINK', from: url, text: a.text });
      }
      internal.add(a.url);
      const key = canonicalPath(a.url);
      if (!seen.has(key)) {
        seen.add(key);
        queue.push(a.url);
      }
    }

    // статусы внутренних ссылок
    const targets = [...internal].slice(0, 60);
    await Promise.all(
      targets.map(async (target) => {
        try {
          const r = await fetch(target, { redirect: 'follow', headers: { 'user-agent': UA } });
          const cls = classifyLink({ url: target, status: r.status, finalUrl: r.url, known: null });
          if (cls.level !== 'ok') linkRows.push({ url: target, level: cls.level, code: cls.code, from: url, detail: cls.detail });
        } catch {
          linkRows.push({ url: target, level: 'error', code: 'UNREACHABLE', from: url });
        }
      }),
    );
    console.log(`  ${pagesVisited.length}. ${url} — ${res.status}, ${ms} мс, ссылок ${internal.size}`);
  }
}

/* ------------------------------------------------------------------ */
/* Режим 2: браузер (Playwright)                                       */
/* ------------------------------------------------------------------ */
async function crawlBrowser() {
  const { chromium } = await import('playwright');
  const browser = await chromium.launch();
  const context = await browser.newContext({ userAgent: UA, viewport: { width: 1440, height: 900 } });

  const queue = [SITE];
  const seen = new Set([canonicalPath(SITE)]);

  while (queue.length && pagesVisited.length < MAX_PAGES) {
    const batch = queue.splice(0, CONCURRENCY);
    await Promise.all(batch.map((url) => visit(url)));
  }

  async function visit(url) {
    if (pagesVisited.length >= MAX_PAGES) return;
    const page = await context.newPage();
    page.on('console', (msg) => {
      if (msg.type() === 'error' || msg.type() === 'warning') {
        consoleErrors.push({ page: url, type: msg.type(), text: msg.text().slice(0, 400) });
      }
    });
    page.on('pageerror', (err) => consoleErrors.push({ page: url, type: 'pageerror', text: String(err).slice(0, 400) }));
    page.on('requestfailed', (req) =>
      consoleErrors.push({
        page: url,
        type: 'requestfailed',
        text: `${req.method()} ${req.url()} — ${req.failure()?.errorText}`,
      }),
    );

    const t0 = Date.now();
    try {
      await page.goto(url, { waitUntil: 'load', timeout: 45000 });
      await page.waitForTimeout(1500); // даём доработать lazy-скриптам и слайдерам
    } catch (e) {
      consoleErrors.push({ page: url, type: 'navigation', text: String(e).slice(0, 300) });
    }
    timings.push({ page: url, ms: Date.now() - t0 });
    pagesVisited.push(url);

    // вёрстка: горизонтальный скролл
    for (const width of VIEWPORTS) {
      await page.setViewportSize({ width, height: 900 });
      await page.waitForTimeout(300);
      const m = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));
      if (m.scrollWidth - m.clientWidth > 2) overflow.push({ page: url, width, ...m });
    }
    await page.setViewportSize({ width: 1440, height: 900 });

    // формы
    const forms = await page.evaluate(() =>
      Array.from(document.querySelectorAll('form')).map((f) => ({
        action: f.getAttribute('action') || '',
        method: (f.getAttribute('method') || 'GET').toUpperCase(),
        id: f.id || '',
        fields: Array.from(f.querySelectorAll('input,textarea,select'))
          .filter((el) => el.type !== 'hidden')
          .map((el) => ({
            name: el.name || el.id || '',
            type: (el.type || el.tagName).toLowerCase(),
            required: el.required,
            placeholder: el.placeholder || '',
            label: (document.querySelector(`label[for="${el.id}"]`)?.textContent || '').trim(),
          })),
      })),
    );
    for (const f of forms) {
      formsFound.push({ page: url, ...f });
      for (const fl of f.fields) {
        if (!fl.label && !fl.placeholder && ['text', 'textarea', 'email', 'tel'].includes(fl.type)) {
          linkRows.push({ url: `${url}#form:${fl.name || fl.type}`, level: 'info', code: 'FIELD_WITHOUT_LABEL', from: url });
        }
      }
    }

    checkContent(url, await page.evaluate(() => document.body.innerText));

    // картинки без alt
    const imgs = await page.evaluate(() =>
      Array.from(document.querySelectorAll('img')).map((i) => ({
        src: i.currentSrc || i.src || '',
        alt: i.getAttribute('alt'),
      })),
    );
    for (const i of imgs) {
      if (i.alt === null || i.alt === '') linkRows.push({ url: i.src, level: 'info', code: 'IMAGE_NO_ALT', from: url });
    }

    // ссылки
    const anchors = await page.evaluate(() =>
      Array.from(document.querySelectorAll('a[href]')).map((a) => ({
        href: a.getAttribute('href'),
        text: (a.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80),
        inNav: !!a.closest('nav, header, [aria-current="page"], .active'),
      })),
    );
    const internal = new Set();
    for (const a of anchors) {
      const abs = normalizeUrl(a.href, url);
      if (!abs || looksLikeAsset(abs)) continue;
      if (!isInternal(abs, origin)) {
        linkRows.push({ url: abs, level: 'info', code: 'EXTERNAL', from: url, text: a.text });
        continue;
      }
      // Ссылка на текущую страницу в контенте = кнопка «в никуда»; в меню это норма.
      if (isSelfLink(url, abs) && !a.inNav) {
        linkRows.push({ url: abs, level: 'warn', code: 'SELF_LINK', from: url, text: a.text });
      }
      internal.add(abs);
      const key = canonicalPath(abs);
      if (!seen.has(key)) {
        seen.add(key);
        queue.push(abs);
      }
    }

    // статусы внутренних ссылок (без редиректов, чтобы увидеть 301)
    const targets = [...internal].slice(0, 60);
    await Promise.all(
      targets.map(async (target) => {
        let res;
        try {
          res = await context.request.get(target, { maxRedirects: 0, timeout: 30000 });
        } catch {
          linkRows.push({ url: target, level: 'error', code: 'UNREACHABLE', from: url });
          return;
        }
        const cls = classifyLink({ url: target, status: res.status(), finalUrl: res.url(), known: null });
        if (cls.level !== 'ok') linkRows.push({ url: target, level: cls.level, code: cls.code, from: url, detail: cls.detail });
      }),
    );

    console.log(`  ${pagesVisited.length}. ${url} — ссылок ${internal.size}`);
    await page.close();
  }

  if (SUBMIT_FORM) await submitContactForm(context);
  await browser.close();
}

/* ------------------------------------------------------------------ */
/* Отправка формы (--submit-form)                                      */
/* ------------------------------------------------------------------ */
async function submitContactForm(context) {
  const page = await context.newPage();
  const target = `${origin}/contact/`;
  await page.goto(target, { waitUntil: 'load', timeout: 45000 });
  await page.waitForTimeout(3000); // ждём Cloudflare Turnstile

  const sample = { email: 'qa+test@example.com', tel: '+15551234567', textarea: 'Automated QA submission — please ignore.', text: 'QA automation test' };
  const filled = [];

  for (const el of await page.$$('form input:not([type]), form input[type=text], form input[type=email], form input[type=tel], form textarea')) {
    const tag = await el.evaluate((n) => n.tagName);
    const type = (await el.getAttribute('type')) || 'text';
    const key = tag === 'TEXTAREA' ? 'textarea' : type === 'email' ? 'email' : type === 'tel' ? 'tel' : 'text';
    await el.fill(sample[key]).catch(() => {});
    filled.push(`${(await el.getAttribute('name')) || key}`);
  }
  const radio = await page.$('form input[type=radio]');
  if (radio) await radio.check().catch(() => {});

  let result = 'no-submit-button';
  const submit = await page.$('form button[type=submit], form input[type=submit]');
  if (submit) {
    await submit.click();
    await page.waitForTimeout(6000);
    const body = (await page.locator('body').innerText()).toLowerCase();
    result = /thank|success|спасибо|успеш|sent|received/.test(body) ? 'looks-submitted' : 'no-visible-confirmation';
  }
  report.formSubmit = { target, filled, result };
  await page.close();
}

/* ------------------------------------------------------------------ */
/* Отчёты                                                              */
/* ------------------------------------------------------------------ */
const report = {
  site: SITE,
  mode: HTTP_ONLY ? 'http-only' : 'browser',
  startedAt,
  pages: pagesVisited,
  links: linkRows.filter((r) => r.code !== 'FOUND'),
  consoleErrors,
  overflow,
  forms: formsFound,
  timings,
  formSubmit: null,
};

const outPath = path.resolve(OUT);
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, JSON.stringify(report, null, 2));
fs.writeFileSync(outPath.replace(/\.json$/, '.md'), renderMarkdown(report));

const errors = report.links.filter((l) => l.level === 'error');
const warnings = report.links.filter((l) => l.level === 'warn');
// Одна и та же ссылка встречается на каждой странице — показываем и записи, и уникальные адреса.
const uniq = (arr) => groupLinks(arr).length;
console.log('');
console.log(`Режим: ${report.mode}`);
console.log(`Страниц проверено: ${pagesVisited.length}`);
console.log(`Битых ссылок: ${errors.length} записей / ${uniq(errors)} уникальных`);
console.log(`Редиректов и ссылок «в никуда»: ${warnings.length} записей / ${uniq(warnings)} уникальных адресов`);
console.log(`Ошибок в консоли: ${consoleErrors.length} записей / ${groupConsole(consoleErrors).length} уникальных${HTTP_ONLY ? ' (в режиме --no-browser не проверяется)' : ''}`);
console.log(`Проблем с вёрсткой: ${overflow.length}`);
console.log(`Форм: ${formsFound.length} экземпляров / ${groupForms(formsFound).length} уникальных конфигураций`);
console.log(`Отчёт: ${outPath}`);
console.log(`Разбор без дублей: node summarize.mjs ${OUT}`);
process.exit(errors.length || consoleErrors.length || overflow.length ? 1 : 0);
