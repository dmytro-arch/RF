#!/usr/bin/env node
/**
 * Функциональный QA-аудит сайта royalfoam.art (Playwright).
 *
 * Что проверяет:
 *  1. Краулинг всех внутренних страниц (BFS от главной).
 *  2. Ошибки JS в консоли + необработанные исключения + упавшие запросы.
 *  3. Все ссылки: статус ответа, редиректы, битые (404/5xx), ссылки «в никуда» (на ту же страницу).
 *  4. Вёрстка: горизонтальный скролл на 1440 / 1024 / 768 / 390 px («ничего не искажалось»).
 *  5. Формы: состав полей, заполнение тестовыми данными и (опционально) реальная отправка.
 *  6. Время загрузки страниц («не подвисало»).
 *
 * Запуск:
 *   cd qa && npm install
 *   node audit.mjs                       # быстрый прогон: 25 страниц
 *   node audit.mjs --max-pages 200       # полный обход
 *   node audit.mjs --submit-form         # реально отправить форму на /contact/
 *   node audit.mjs --out out/report.json # свои пути для отчётов
 */
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';
import {
  normalizeUrl,
  isInternal,
  canonicalPath,
  looksLikeAsset,
  extractForms,
  classifyLink,
  isSelfLink,
  renderMarkdown,
} from './lib.mjs';

const SITE = arg('site', 'https://royalfoam.art/');
const MAX_PAGES = Number(arg('max-pages', '25'));
const OUT = arg('out', 'out/report.json');
const SUBMIT_FORM = process.argv.includes('--submit-form');
const CONCURRENCY = Number(arg('concurrency', '4'));
const VIEWPORTS = [1440, 1024, 768, 390];

function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 && process.argv[i + 1] ? process.argv[i + 1] : def;
}

const origin = new URL(SITE).origin;
const startedAt = new Date().toISOString();

/** @type {{url:string,level:string,code:string,from:string,detail?:string}[]} */
const linkRows = [];
/** @type {{page:string,type:string,text:string}[]} */
const consoleErrors = [];
/** @type {{page:string,width:number,scrollWidth:number,clientWidth:number}[]} */
const overflow = [];
const timings = [];
const formsFound = [];
const pagesVisited = [];

const browser = await chromium.launch();
const context = await browser.newContext({
  userAgent:
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
  viewport: { width: 1440, height: 900 },
});

const queue = [SITE];
const seen = new Set([canonicalPath(SITE)]);

while (queue.length && pagesVisited.length < MAX_PAGES) {
  const batch = queue.splice(0, CONCURRENCY);
  await Promise.all(batch.map((url) => visit(url)));
}

async function visit(url) {
  if (pagesVisited.length >= MAX_PAGES) return;
  const page = await context.newPage();
  const record = { url, status: 0, finalUrl: url, ms: 0, title: '' };
  page.on('console', (msg) => {
    if (msg.type() === 'error' || msg.type() === 'warning') {
      consoleErrors.push({ page: url, type: msg.type(), text: msg.text().slice(0, 400) });
    }
  });
  page.on('pageerror', (err) => consoleErrors.push({ page: url, type: 'pageerror', text: String(err).slice(0, 400) }));
  page.on('requestfailed', (req) =>
    consoleErrors.push({ page: url, type: 'requestfailed', text: `${req.method()} ${req.url()} — ${req.failure()?.errorText}` }),
  );

  const t0 = Date.now();
  try {
    const resp = await page.goto(url, { waitUntil: 'load', timeout: 45000 });
    record.status = resp?.status() ?? 0;
    record.finalUrl = page.url();
    record.title = await page.title();
    await page.waitForTimeout(1500); // даём доработать lazy-скриптам/слайдерам
    record.ms = Date.now() - t0;
  } catch (e) {
    record.ms = Date.now() - t0;
    consoleErrors.push({ page: url, type: 'navigation', text: String(e).slice(0, 300) });
  }
  timings.push({ page: url, ms: record.ms });
  pagesVisited.push(url);

  // --- вёрстка: горизонтальный скролл на разных ширинах
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

  // --- формы
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
    // Поле без подписи и без placeholder — кандидат в «непонятные поля».
    for (const fl of f.fields) {
      if (!fl.label && !fl.placeholder && ['text', 'textarea', 'email', 'tel'].includes(fl.type)) {
        linkRows.push({ url: `${url}#form:${fl.name || fl.type}`, level: 'info', code: 'FIELD_WITHOUT_LABEL', from: url });
      }
    }
  }

  // --- ссылки
  const anchors = await page.evaluate(() =>
    Array.from(document.querySelectorAll('a[href]')).map((a) => ({
      href: a.getAttribute('href'),
      text: (a.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80),
      title: a.getAttribute('title') || '',
    })),
  );
  const internalTargets = new Set();
  for (const a of anchors) {
    const abs = normalizeUrl(a.href, url);
    if (!abs) continue;
    if (looksLikeAsset(abs)) continue;
    if (!isInternal(abs, origin)) {
      linkRows.push({ url: abs, level: 'info', code: 'EXTERNAL', from: url, text: a.text });
      continue;
    }
    if (isSelfLink(url, abs) && !abs.includes('#')) {
      linkRows.push({ url: abs, level: 'warn', code: 'SELF_LINK', from: url, text: a.text });
    }
    linkRows.push({ url: abs, level: 'ok', code: 'FOUND', from: url, text: a.text });
    internalTargets.add(abs);
    const key = canonicalPath(abs);
    if (!seen.has(key)) {
      seen.add(key);
      queue.push(abs);
    }
  }

  // --- статусы внутренних ссылок (без редиректов, чтобы увидеть 301)
  const targets = [...internalTargets].slice(0, 60);
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
      if (cls.level !== 'ok') {
        linkRows.push({ url: target, level: cls.level, code: cls.code, from: url, detail: cls.detail });
      }
    }),
  );

  await page.close();
}

// --- опциональная отправка формы
let formSubmit = null;
if (SUBMIT_FORM) {
  formSubmit = await submitContactForm();
}

async function submitContactForm() {
  const page = await context.newPage();
  const target = `${origin}/contact/`;
  await page.goto(target, { waitUntil: 'load', timeout: 45000 });
  await page.waitForTimeout(3000); // ждём Cloudflare Turnstile
  const test = {
    text: 'QA automation test',
    email: 'qa+test@example.com',
    tel: '+15551234567',
    textarea: 'Automated QA submission — please ignore.',
  };
  const filled = [];
  for (const el of await page.$$('form input[type=text], form input[type=email], form input[type=tel], form textarea')) {
    const type = await el.getAttribute('type');
    const name = (await el.getAttribute('name')) || '';
    const key = type === 'email' ? 'email' : type === 'tel' ? 'tel' : (await el.evaluate((n) => n.tagName, el)) === 'TEXTAREA' ? 'textarea' : 'text';
    await el.fill(test[key] || test.text);
    filled.push(`${name || type || key}`);
  }
  const radios = await page.$$('form input[type=radio]');
  if (radios.length) await radios[0].check().catch(() => {});
  const submit = await page.$('form button[type=submit], form input[type=submit]');
  let result = 'no-submit-button';
  if (submit) {
    await submit.click();
    await page.waitForTimeout(5000);
    const body = (await page.locator('body').innerText()).toLowerCase();
    result = /thank|success|успеш|спасибо|sent/.test(body) ? 'looks-submitted' : 'no-visible-confirmation';
  }
  await page.close();
  return { target, filled, result };
}

await browser.close();

// --- отчёты
const links = linkRows.filter((r) => r.code !== 'FOUND');
const report = {
  site: SITE,
  startedAt,
  pages: pagesVisited,
  links,
  consoleErrors,
  overflow,
  forms: formsFound,
  timings,
  formSubmit,
};
const outPath = path.resolve(OUT);
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, JSON.stringify(report, null, 2));
fs.writeFileSync(outPath.replace(/\.json$/, '.md'), renderMarkdown(report));

const errors = links.filter((l) => l.level === 'error').length;
console.log(`Страниц проверено: ${pagesVisited.length}`);
console.log(`Ошибок в консоли: ${consoleErrors.length}`);
console.log(`Битых ссылок: ${errors}`);
console.log(`Проблем с вёрсткой (горизонтальный скролл): ${overflow.length}`);
console.log(`Форм найдено: ${formsFound.length}`);
console.log(`Отчёт: ${outPath}`);
process.exit(errors || consoleErrors.length || overflow.length ? 1 : 0);
