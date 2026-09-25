#!/usr/bin/env node
/**
 * Разбор готового отчёта audit.mjs: схлопывает дубли и показывает, что реально чинить.
 * Заново сайт не обходит — работает с уже сохранённым JSON.
 *
 *   node summarize.mjs                    # читает out/full.json
 *   node summarize.mjs out/report.json    # свой файл
 *   node summarize.mjs out/full.json --top 30
 */
import fs from 'node:fs';
import path from 'node:path';
import { groupLinks, groupConsole, groupForms, slowestPages } from './lib.mjs';

const file = process.argv.find((a) => a.endsWith('.json')) || 'out/full.json';
const TOP = Number((process.argv.find((a, i) => process.argv[i - 1] === '--top') || '15'));

if (!fs.existsSync(file)) {
  console.error(`Файл не найден: ${file}\nСначала прогоните: node audit.mjs --max-pages 200 --out out/full.json`);
  process.exit(2);
}
const report = JSON.parse(fs.readFileSync(file, 'utf8'));
const lines = [];
const say = (s = '') => {
  lines.push(s);
  console.log(s);
};
const only = (code) => report.links.filter((l) => l.code === code);

say(`# Разбор отчёта ${path.basename(file)}`);
say(`Сайт: ${report.site} · режим: ${report.mode || 'browser'} · старт: ${report.startedAt}`);
say(`Страниц: ${report.pages.length} · записей о ссылках: ${report.links.length} · ошибок консоли: ${report.consoleErrors.length} · форм: ${report.forms.length}`);
say('');

/* ---------- 1. Битые ссылки ---------- */
const broken = groupLinks(report.links.filter((l) => l.level === 'error'));
say(`## 1. Битые ссылки — ${broken.length} уникальных`);
if (!broken.length) say('Нет.');
for (const b of broken) {
  say(`- ${b.code} ${b.url} — найдено ${b.count} раз, например со страниц: ${b.from.slice(0, 3).join(', ')}`);
}
say('');

/* ---------- 2. Редиректы ---------- */
const redirects = report.links.filter((l) => l.code === 'REDIRECT' || l.code === 'SOFT_REDIRECT');
const byPattern = groupLinks(redirects, { byPattern: true });
const uniqRedirects = groupLinks(redirects);
say(`## 2. Редиректы — ${redirects.length} записей, ${uniqRedirects.length} уникальных адресов`);
say('По шаблонам:');
for (const p of byPattern.slice(0, TOP)) {
  const example = uniqRedirects.find((u) => u.url.startsWith(p.url.replace('/*', '/')));
  say(`- ${p.url} — ${p.count} раз${example?.detail ? ` (пример: ${example.url} → ${example.detail})` : ''}`);
}
say('');
say(`Топ уникальных адресов (${Math.min(TOP, uniqRedirects.length)} из ${uniqRedirects.length}):`);
for (const u of uniqRedirects.slice(0, TOP)) say(`- ${u.url} → ${u.detail || '?'} · ${u.count} раз`);
say('');

/* ---------- 3. Ссылки «в никуда» ---------- */
const self = groupLinks(only('SELF_LINK'));
say(`## 3. Ссылки на ту же страницу (кнопки «в никуда») — ${self.length} уникальных`);
for (const s of self.slice(0, TOP)) say(`- ${s.url} — ${s.count} раз, например: ${s.from.slice(0, 3).join(', ')}`);
say('');

/* ---------- 4. Ошибки консоли ---------- */
const cons = groupConsole(report.consoleErrors);
say(`## 4. Ошибки в консоли — ${report.consoleErrors.length} записей, ${cons.length} уникальных`);
for (const c of cons.slice(0, TOP)) {
  say(`- ×${c.count} [${c.type}] ${c.text}`);
  say(`    страницы: ${c.pages.slice(0, 3).join(', ')}`);
}
say('');

/* ---------- 5. Вёрстка ---------- */
say(`## 5. Горизонтальный скролл — ${report.overflow.length}`);
if (!report.overflow.length) say('Нет.');
for (const o of report.overflow) {
  say(`- ${o.page} @${o.width}px: ${o.scrollWidth} > ${o.clientWidth} (+${o.scrollWidth - o.clientWidth}px)`);
}
say('');

/* ---------- 6. Формы ---------- */
const forms = groupForms(report.forms);
say(`## 6. Формы — ${report.forms.length} экземпляров на страницах, ${forms.length} уникальных конфигураций`);
say(`Среднее на страницу: ${(report.forms.length / Math.max(1, report.pages.length)).toFixed(1)}`);
for (const f of forms.slice(0, TOP)) {
  const fields = f.fields.map((x) => x.name || x.type).join(', ') || '(нет полей)';
  say(`- ×${f.count} ${f.signature.split('|')[0]} ${f.signature.split('|')[1] || '(без action)'}`);
  say(`    поля: ${fields}`);
  say(`    страницы: ${f.pages.slice(0, 3).join(', ')}`);
}
say('');

/* ---------- 7. Прочее ---------- */
const info = groupLinks(report.links.filter((l) => l.level === 'info'));
say('## 7. Прочее (info)');
for (const i of info.slice(0, TOP)) say(`- ${i.code}: ${i.count} раз${i.code === 'EXTERNAL' ? '' : ` — ${i.url}`}`);
say('');

/* ---------- 8. Скорость ---------- */
say('## 8. Самые медленные страницы');
for (const t of slowestPages(report.timings, 10)) say(`- ${t.ms} мс — ${t.page}`);
say('');

/* ---------- 9. Итог ---------- */
const fatal = broken.length;
say('## 9. Что делать в первую очередь');
say(`1. Битые ссылки: ${fatal ? 'починить ' + broken.map((b) => b.url).join(', ') : 'нет'}.`);
say(`2. Редиректы: заменить ${byPattern[0] ? byPattern[0].url : '—'} на конечные адреса (${redirects.length} срабатываний на ${report.pages.length} страницах).`);
say(`3. Консоль: ${cons.length} уникальных ошибок — начать с самых частых (см. раздел 4).`);
say(`4. Вёрстка: ${report.overflow.length} случаев горизонтального скролла.`);
say(`5. Формы: ${forms.length} уникальных при ${report.forms.length} экземплярах — проверить, не дублируется ли глобальная форма.`);

const mdPath = file.replace(/\.json$/, '') + '.summary.md';
fs.writeFileSync(mdPath, lines.join('\n'));
console.log(`\nСохранено: ${mdPath}`);
