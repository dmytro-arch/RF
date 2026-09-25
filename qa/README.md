# QA royalfoam.art — автоматическая проверка

Функциональный аудит сайта: битые ссылки, редиректы, ошибки в консоли, «поехавшая» вёрстка,
состав и отправка форм, время загрузки.

## Быстрый старт

```bash
cd qa
npm install
npx playwright install chromium

npm test            # юнит-проверки парсеров (без сети и браузера)
npm run audit       # 25 страниц, отчёт в out/report.json и out/report.md
npm run audit:full  # до 200 страниц
npm run audit:form  # заполнить и отправить форму на /contact/
```

Параметры: `--site https://royalfoam.art/`, `--max-pages 50`, `--out out/report.json`,
`--concurrency 4`, `--submit-form`.

## Что проверяется

| Проверка | Как |
| --- | --- |
| Статус каждой внутренней ссылки | `request.get(..., maxRedirects: 0)` → 404/5xx = ошибка, 3xx = редирект |
| Кнопки «в никуда» | ссылка ведёт на ту же страницу (`SELF_LINK`) |
| Ошибки JS | `console.error`, `pageerror`, `requestfailed` |
| Вёрстка | `scrollWidth > clientWidth` на 1440 / 1024 / 768 / 390 px |
| Формы | поля без подписи и placeholder (`FIELD_WITHOUT_LABEL`), опциональная отправка |
| Скорость | время до `load` по каждой странице |

Скрипт выходит с кодом `1`, если нашлась битая ссылка, ошибка консоли или горизонтальный скролл —
удобно вешать в CI.

## Файлы

- `audit.mjs` — краулер на Playwright.
- `lib.mjs` — чистые функции (разбор ссылок/форм, классификация статусов, генерация отчёта).
- `selftest.mjs` + `fixtures/sample.html` — проверки `lib.mjs` без сети.
- `out/` — результаты (в git не коммитим).
