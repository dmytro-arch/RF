# Аудит перелинковки: статьи блога и кейсов ↔ страницы услуг

**Сайт:** https://decorativearchitecturalproducts.com/
**Раздел услуг:** https://decorativearchitecturalproducts.com/services/
**Дата проверки:** 21 сентября 2026
**Источник перечня страниц:** вкладка «Decorative Architectural Products» контент-таблицы + sitemap сайта (`sitemap_index.xml`, `post-sitemap.xml`, `cases-sitemap.xml`, `service-sitemap.xml`)

## Краткий вывод

**Тематическая перелинковка «статья → своя услуга» отсутствует полностью: 0 из 23 пар связаны.**

| Направление | Проверено | Тематическая ссылка есть | Статус |
|---|---|---|---|
| Статья блога → своя услуга | 11 статей | 0 | ❌ |
| Кейс → своя услуга | 12 кейсов | 0 | ❌ |
| Услуга → тематическая статья/кейс | 2 услуги полностью + шаблон | 0 | ❌ |
| Услуга → статьи (блок «Blog posts», 3 последние, нетематические) | 2 услуги полностью | есть, но не по теме | ⚠️ |
| Статья блога → услуги (шаблонный блок «What we do», 10 услуг, нетематический) | 10 статей | есть, но «своей» услуги там нет | ⚠️ |
| Кейс → услуги (любой вид ссылок) | 12 кейсов полностью | 0 ссылок вообще | ❌ |

## Методология

- Прямой доступ к сайту из песочницы закрыт, поэтому страницы проверялись через построчное чтение (весь видимый текст + все ссылки каждой страницы).
- **Кейсы: 12/12 проверены целиком** (все блоки страницы: тело, «See other solutions», FAQ, каталог, контакты).
- **Блог: 2 статьи проверены целиком** — *Faux Wood Trusses* (8/8 блоков), *Custom Column Capitals & Bases* (5/5 блоков): в теле ноль ссылок на `/services/`.
- **Блог: остальные 8 статей** — первый блок (тело, ссылок на услуги нет) + блок с шаблоном «What we do» (зафиксирован состав ссылок).
- **Услуги: 2 страницы проверены целиком** — `/services/faux-wood-trusses/` (7/7), `/services/carved-corbels/` (7/7): шаблон полностью идентичен.
- Соответствие «статья → услуга» установлено по смыслу (в таблице нет явной колонки-связки): названия статей прямо повторяют названия услуг; спорные пары помечены ниже.

## 1. Блог → услуги (11 статей из таблицы)

| # | Статья | Ожидаемая услуга | Ссылка в теле статьи | «Своя» услуга в блоке «What we do» | Итог |
|---|---|---|---|---|---|
| 1 | Faux Wood Trusses: The Complete Expert Guide… | `/services/faux-wood-trusses/` | ❌ нет (проверена целиком) | ❌ | ❌ отсутствует |
| 2 | Front Door Surround Kits: The Complete Expert Guide… | `/services/front-door-surrounds-kits/` | ❌ нет | ❌ | ❌ отсутствует |
| 3 | Faux Wood Beams Made of Polyurethane… | `/services/custom-faux-wood-beams/` | ❌ нет | ❌ | ❌ отсутствует |
| 4 | Architectural Column Kits: The Complete Expert Guide… | `/services/architectural-columns-kits/` | ❌ нет | ❌ | ❌ отсутствует |
| 5 | Exterior Polyurethane Trim and Molding… | — (услуги «Trim/Molding» на сайте нет) | ❌ нет | ❌ (нечему соответствовать) | ❌ некуда вести |
| 6 | Decorative Columns for Porch and Exterior Design… | `/services/architectural-columns-kits/` | — | — | ⛔ страница 404 (см. находку №1) |
| 7 | Ceiling Faux Wood Planks… | `/services/ceiling-faux-wood-planks/` | ❌ нет | ❌ | ❌ отсутствует |
| 8 | Ceiling Dome Design Systems… | `/services/ceiling-dome-design-systems/` | ❌ нет | ❌ | ❌ отсутствует |
| 9 | Carved Foam Ceilings… | `/services/carved-foam-ceilings/` | ❌ нет | ❌ | ❌ отсутствует |
| 10 | Coffered Ceilings… | `/services/custom-coffered-ceilings/` | ❌ нет | ❌ | ❌ отсутствует |
| 11 | Custom Column Capitals & Bases… | `/services/custom-column-capitals-and-bases/` | ❌ нет (проверена целиком) | ❌ | ❌ отсутствует |

Состав шаблонного блока «What we do» — **одинаковый на всех 10 живых статьях** (только ссылки-картинки, без текстовых анкоров):

1. `/services/acoustic-panels-systems/`
2. `/services/green-wall-vertical-garden-panel-systems/`
3. `/services/suspended-ceiling-systems/`
4. `/services/acoustic-ceiling-systems/`
5. `/services/stucco-mailboxes-and-lamp-posts-kits/`
6. `/services/stucco-architectural-fencing-systems/`
7. `/services/faux-stone-column-wraps/`
8. `/services/faux-wood-mantels/`
9. `/services/fireplace-surround-kits/`
10. `/services/juliet-balcony-decorative-kits/`

Пересечение этого списка с 10 «своими» услугами статей блога — **нулевое**. То есть даже сквозной шаблонный блок не связывает ни одну статью с её услугой.

## 2. Кейсы → услуги (12 кейсов: 11 из таблицы + 1 из sitemap)

Все 12 страниц проверены целиком. **Ни на одной нет ни одной ссылки на `/services/`** — ни контекстной, ни шаблонной. Блок «See other solutions» ведёт только на другие кейсы.

| # | Кейс | Ожидаемая услуга | Ссылка на услугу | Итог |
|---|---|---|---|---|
| 1 | Chatelaine Fence Project | `/services/stucco-architectural-fencing-systems/` | ❌ нет | ❌ отсутствует |
| 2 | Custom Lightweight Fence Panel System with Integrated Lighting | `/services/stucco-architectural-fencing-systems/` | ❌ нет | ❌ отсутствует |
| 3 | Custom 3D Monument Sign with Realistic Pine Trees | — (услуги «Signage» нет) | ❌ нет | ❌ некуда вести |
| 4 | Decorative Custom Shutters for Commercial Project | — (услуги «Shutters» нет) | ❌ нет | ❌ некуда вести |
| 5 | Custom Decorative Balusters for Residential Project | — (услуга «Balustrades and Railings» в таблице без URL, страницы нет) | ❌ нет | ❌ некуда вести |
| 6 | Custom Decorative Wall Panels for Outdoor Zoning | — (подходящей услуги нет) | ❌ нет | ❌ некуда вести |
| 7 | Custom Fireplace Surround for a Luxury Residence | `/services/fireplace-surround-kits/` (+ вторичная `/services/faux-wood-mantels/`) | ❌ нет | ❌ отсутствует |
| 8 | Custom Faux Brick Mailbox for Residential Project | `/services/stucco-mailboxes-and-lamp-posts-kits/` | ❌ нет | ❌ отсутствует |
| 9 | Custom Columns and Trellis for Residential Project | `/services/architectural-columns-kits/` | ❌ нет | ❌ отсутствует |
| 10 | Custom Lightweight Balustrade System | — (услуги «Balustrades» нет, см. №5) | ❌ нет | ❌ некуда вести |
| 11 | Custom Decorative Corbels for Residential Project | `/services/carved-corbels/` | ❌ нет | ❌ отсутствует |
| 12 | XXL Corinthian Column Capitals for 20’ Architectural Columns ⚠️ (есть на сайте и в sitemap, **нет в таблице**) | `/services/custom-column-capitals-and-bases/` (+ вторичная `/services/architectural-columns-kits/`) | ❌ нет | ❌ отсутствует |

Характерно: на каждом кейсе есть «пустой» продуктовый подвал — картинка услуги + заголовок (напр. «Carved Corbels», «Custom Fireplace Surround») + буллеты + текст «Discuss the project» — **без единой ссылки**. Это готовое место под CTA-ссылку на услугу.

## 3. Услуги → статьи и кейсы (обратное направление)

Проверены целиком 2 услуги (`faux-wood-trusses`, `carved-corbels`), шаблон идентичен:

- **Блок «Blog posts» есть**, но это виджет **«3 последние статьи»**, одинаковый на всех услугах: *Capitals & Bases (30.06) → Coffered Ceilings (29.06) → Carved Foam Ceilings (26.06)*. Тематической привязки нет: услуга Trusses не ссылается на гайд по фермам, услуга Corbels — ни на статью, ни на кейс про карнизы.
- **Ссылок на кейсы (`/case-collection/`) нет вообще** — только ссылка «All our gallery» → `/portfolio-collection`.
- **Контекстных ссылок в SEO-тексте внизу услуг нет.**
- Следствие: 7 из 10 статей (все, кроме 3 самых свежих) не получают с услуг вообще ничего; кейсы не получают ничего.

## 4. Попутные находки (вне перелинковки, но критично)

1. **⛔ 404: статья из таблицы не существует.** `https://decorativearchitecturalproducts.com/decorative-columns-for-porch-and-exterior-design/` отдаёт страницу 404, хотя в таблице статус «Готово». URL также отсутствует в `post-sitemap.xml`.
2. **🐞 Кнопка «See all services» ведёт на `/blog`.** В блоке «What we do» на всех 10 статьях ссылка с текстом «See all services» указывает на `https://decorativearchitecturalproducts.com/blog` вместо `/services/`.
3. **📋 Ошибка URL в таблице.** Строка «Faux Wood Mantels» содержит URL `…/services/faux-stone-column-wraps/` (дубль соседней строки). Правильный URL существует: `…/services/faux-wood-mantels/`.
4. **📋 Кейс XXL Corinthian Column Capitals есть на сайте, но отсутствует в таблице** (раздел Cases).
5. **Статьям/кейсам не на что ссылаться:** нет услуг «Trim and Molding», «Shutters», «Monument Signs», «Wall Panels», «Balustrades and Railings» (последняя в таблице есть, но без URL и статуса «Готово»). Это 1 статья + 5 кейсов без целевой страницы.

## 5. Рекомендации (по приоритету)

1. **Починить 404 статьи про porch columns** (восстановить страницу или снять статус «Готово» + настроить редирект) — иначе это битая страница в индексе/карте контента.
2. **Починить «See all services» → вести на `/services/`** (одна правка в шаблоне, влияет на 10 статей).
3. **Добавить контекстные ссылки «статья → своя услуга»** — минимум по 1 ссылке в теле каждой из 9 статей с существующей услугой (интро + CTA-блок в конце). Анкоры — по названию услуги.
4. **Добавить CTA-ссылку на услугу в продуктовый подвал каждого кейса** (заголовок + кнопка «Discuss the project» → ссылка на услугу) — 7 кейсов с существующей услугой.
5. **Сделать блок «Blog posts» на услугах тематическим** (связь услуга → свой гайд + свои кейсы) вместо «3 последних»; добавить на услуги блок «Related cases».
6. **Решить судьбу 6 страниц без целевой услуги** (trim-статья + 5 кейсов): создать услуги (Balustrades — уже в планах) либо задать ближайшие соответствия (напр., Monument Sign → Services hub) временными ссылками.
7. **Исправить таблицу:** URL Mantels, добавить XXL-кейс, актуализировать статус porch-columns.

---
*Детальная построчная таблица — в файле `interlink-audit-products.csv` (разделитель `;`).*
