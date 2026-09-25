#!/usr/bin/env node
/**
 * Юнит-проверки чистых функций из lib.mjs.
 * Не требуют ни браузера, ни сети:  node selftest.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
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
  summarize,
  renderMarkdown,
} from './lib.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(here, 'fixtures', 'sample.html'), 'utf8');
const BASE = 'https://royalfoam.art/special-deals/';

let passed = 0;
const failures = [];
function check(name, cond, extra = '') {
  if (cond) passed += 1;
  else failures.push(`${name}${extra ? ` — ${extra}` : ''}`);
}
function eq(name, actual, expected) {
  check(name, JSON.stringify(actual) === JSON.stringify(expected), `получено ${JSON.stringify(actual)}, ждали ${JSON.stringify(expected)}`);
}

// --- normalizeUrl
eq('anchor -> null', normalizeUrl('#brx-content', BASE), null);
eq('mailto -> null', normalizeUrl('mailto:info@royalfoam.art', BASE), null);
eq('tel -> null', normalizeUrl('tel:(904) 712-1995', BASE), null);
eq('relative -> absolute', normalizeUrl('/services/', BASE), 'https://royalfoam.art/services/');
eq('hash обрезается', normalizeUrl('/services/#top', BASE), 'https://royalfoam.art/services/');
eq('мусор -> null', normalizeUrl('   ', BASE), null);

// --- isInternal / canonicalPath / looksLikeAsset
check('isInternal true', isInternal('https://royalfoam.art/faq/', 'https://royalfoam.art/'));
check('isInternal false', !isInternal('https://calendar.app.google/x', 'https://royalfoam.art/'));
eq('canonicalPath убирает слэш', canonicalPath('https://royalfoam.art/portfolio/'), '/portfolio');
check('looksLikeAsset png', looksLikeAsset('https://royalfoam.art/wp-content/uploads/x.png'));
check('looksLikeAsset page', !looksLikeAsset('https://royalfoam.art/portfolio/'));

// --- extractLinks
const links = extractLinks(html, BASE);
const hrefs = links.map((l) => l.href);
check('ссылка без href игнорируется', links.length === 9, `нашли ${links.length}`);
check('якорь остался в списке как непроверяемый', links.find((l) => l.href === '#brx-content').url === null);
check('asset распознан', looksLikeAsset(links.find((l) => l.href.includes('.png')).url));

// --- extractImages: пустой alt и отсутствующий alt — разные проблемы
const imgs = extractImages(html, BASE);
eq('картинок найдено', imgs.length, 3);
check('alt="" распознаётся как пустой', imgs[0].hasAlt === true && imgs[0].alt === '');
check('нормальный alt прочитан', imgs[1].alt === 'Brand Activation');
check('alt отсутствует вовсе', imgs[2].hasAlt === false);

// --- extractForms
const forms = extractForms(html);
eq('форм найдено', forms.length, 1);
eq('action формы', forms[0].action, '/wp-admin/admin-ajax.php');
eq('метод формы', forms[0].method, 'POST');
check('hidden-поля исключены', !forms[0].fields.some((f) => f.name === 'action'));
check('required распознан', forms[0].fields.find((f) => f.name === 'name').required === true);
check('радио-кнопки учтены', forms[0].fields.filter((f) => f.type === 'radio').length === 2);

// --- classifyLink
eq('404 = ошибка', classifyLink({ url: 'https://royalfoam.art/x/', status: 404, finalUrl: 'https://royalfoam.art/x/' }).code, 'HTTP_404');
eq('500 = ошибка', classifyLink({ url: 'https://royalfoam.art/x/', status: 500, finalUrl: 'https://royalfoam.art/x/' }).level, 'error');
eq('301 = редирект', classifyLink({ url: 'https://royalfoam.art/service/a/', status: 301, finalUrl: 'https://royalfoam.art/services/a/' }).code, 'REDIRECT');
eq(
  '200, но другой путь = мягкий редирект',
  classifyLink({ url: 'https://royalfoam.art/blog/', status: 200, finalUrl: 'https://royalfoam.art/blog-b2b-custom-foam-fabrication/' }).code,
  'SOFT_REDIRECT',
);
eq('200 на себя = ok', classifyLink({ url: 'https://royalfoam.art/faq/', status: 200, finalUrl: 'https://royalfoam.art/faq/' }).code, 'OK');
eq(
  'URL вне sitemap помечается',
  classifyLink({ url: 'https://royalfoam.art/under-construction/', status: 200, finalUrl: 'https://royalfoam.art/under-construction/', known: new Set(['/faq']) }).code,
  'NOT_IN_SITEMAP',
);

// --- isSelfLink
check('само-ссылка', isSelfLink('https://royalfoam.art/special-deals/', 'https://royalfoam.art/special-deals/'));
check('не само-ссылка', !isSelfLink('https://royalfoam.art/special-deals/', 'https://royalfoam.art/portfolio/'));

// --- summarize / renderMarkdown
const rows = [
  { level: 'ok', code: 'OK' },
  { level: 'error', code: 'HTTP_404' },
  { level: 'warn', code: 'REDIRECT' },
];
const s = summarize(rows);
eq('summarize total', s.total, 3);
eq('summarize errors', s.by.error, 1);
const md = renderMarkdown({
  site: 'https://royalfoam.art/',
  startedAt: '2026-09-25T00:00:00Z',
  pages: ['https://royalfoam.art/'],
  links: [{ level: 'error', code: 'HTTP_404', url: 'https://royalfoam.art/x/', from: 'https://royalfoam.art/' }],
  consoleErrors: [{ page: 'https://royalfoam.art/', type: 'error', text: 'boom' }],
  overflow: [{ page: 'https://royalfoam.art/', width: 390, scrollWidth: 430, clientWidth: 390 }],
  forms: [{ page: 'https://royalfoam.art/contact/', fields: [1, 2, 3], action: '' }],
  timings: [{ page: 'https://royalfoam.art/', ms: 1200 }],
});
check('в отчёте есть раздел про ссылки', md.includes('## Ссылки'));
check('в отчёте есть консольные ошибки', md.includes('boom'));
check('в отчёте есть вёрстка', md.includes('Горизонтальный скролл'));

if (failures.length) {
  console.error(`✗ Провалено ${failures.length} из ${passed + failures.length}:`);
  for (const f of failures) console.error(`  - ${f}`);
  process.exit(1);
}
console.log(`✓ Все проверки пройдены: ${passed}`);
