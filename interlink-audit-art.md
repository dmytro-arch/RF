# Аудит перелинковки: статьи блога и кейсы ↔ страницы услуг

**Сайт:** https://royalfoam.art/
**Раздел услуг:** https://royalfoam.art/services/
**Дата проверки:** 21 сентября 2026
**Источник перечня страниц:** живой sitemap сайта (`sitemap_index.xml`, `post-sitemap.xml`, `case-sitemap.xml`, `service-sitemap.xml`), сверен 21.09.2026. Вкладки контент-таблицы по Royal Foam Art пока не получены — источник только sitemap; после получения таблицы отчёт будет сведён со статусами и дополнен.

## Краткий вывод

**Тематическая перелинковка «статья → своя услуга» отсутствует: 0 из 29 пар связаны.** Единственная контекстная ссылка из контентных страниц на услуги — нетематическая.

| Направление | Проверено | Тематическая ссылка есть | Статус |
|---|---|---|---|
| Статья блога → своя услуга | 5 статей | 0 (1 ссылка есть, но не по теме) | ❌ |
| Кейс → своя услуга | 24 кейса | 0 | ❌ |
| Услуга → тематическая статья/кейс | 2 услуги полностью + точечная проверка 3-й | 0 | ❌ |
| Услуга → статьи (статичный блок из 3 самых старых постов) | 3 услуги | есть, тематической привязки нет | ⚠️ |
| Блог → блог / блог → хаб портфолио | 5 статей | есть (только эти ссылки) | ℹ️ |
| Кейс → услуги (любой вид ссылок) | 24 кейса полностью | 0 ссылок вообще | ❌ |

## Методология

- Прямой доступ к сайту из песочницы закрыт, поэтому страницы проверялись через построчное чтение (весь видимый текст + все ссылки каждой страницы).
- **Блог: 5/5 статей проверены целиком** (все блоки страницы).
- **Кейсы: 24/24 проверены целиком** (тело, похожие проекты, FAQ, каталог, форма).
- **Услуги: 2 страницы проверены целиком** (шаблон полностью идентичен) + точечная проверка `/services/foam-monument-signs/` (3 блока: шапка, середина SEO-текста, подвал с блоком статей).
- Соответствие «статья → услуга» установлено по смыслу (таблицы пока нет): названия статей и кейсов прямо указывают на услуги; спорные пары помечены ниже.
- Все 5 статей и 24 кейса из sitemap живы (404 среди контентных URL из sitemap нет) — удаления согласованы с картой сайта.

## 1. Блог → услуги (5 статей из sitemap)

| # | Статья | Ожидаемая услуга | Ссылка в теле статьи | Итог |
|---|---|---|---|---|
| 1 | In the beginning was the idea: how we turn sketches into custom monument signs | `/services/foam-monument-signs/` | ❌ нет | ❌ отсутствует |
| 2 | Custom 3D props that turn events into shareable moments | `/services/brand-activation-props/` | ❌ нет | ❌ отсутствует |
| 3 | Commercial monument signs on a deadline: how we deliver orders | `/services/foam-monument-signs/` | ❌ нет | ❌ отсутствует |
| 4 | Custom architectural foam elements: design process, manufacturing, materials and applications | `/services/architectural-shapes/` | ⚠️ 1 ссылка, но на `foam-monument-signs` (не по теме) | ❌ тематической нет |
| 5 | Custom prop fabrication: how foam props are made for film, theater and events | `/services/foam-stage-movie-props/` | ❌ нет | ❌ отсутствует |

Шаблон статей блога **не содержит сервисного блока вообще**: статьи ссылаются только друг на друга и на хаб `/portfolio/`. Кейсы живут в разделе `/case/` с хабом `/cases/` — из статей на них ссылок нет.

## 2. Кейсы → услуги (24 кейса из sitemap)

Все 24 страницы проверены целиком. **Ни на одной нет ни одной ссылки на `/services/`** — ни контекстной, ни шаблонной.

| # | Кейс | Ожидаемая услуга | Ссылка на услугу | Итог |
|---|---|---|---|---|
| 1 | Living Stream Church: creating atmosphere with architectural foam solutions | `/services/designs-for-places-of-worship/` | ❌ нет | ❌ отсутствует |
| 2 | The Big Red Hat mobile activation | `/services/brand-activation-props/` | ❌ нет | ❌ отсутствует |
| 3 | Giant foam props: large-scale 3D boombox installation for casino event | `/services/event-props-decor/` | ❌ нет | ❌ отсутствует |
| 4 | Dynamics of color and light: 3D decor for Living Stream kids | `/services/designs-for-places-of-worship/` | ❌ нет | ❌ отсутствует |
| 5 | Custom striped M letters + accent pillars | `/services/oversize-foam-letters-logos/` | ❌ нет | ❌ отсутствует |
| 6 | 8-foot freestanding branded N letter for N-able event | `/services/oversize-foam-letters-logos/` | ❌ нет | ❌ отсутствует |
| 7 | OSET 2025 update | `/services/oversize-foam-letters-logos/` | ❌ нет | ❌ отсутствует |
| 8 | 5-foot interactive YOU letters with writable surface | `/services/oversize-foam-letters-logos/` | ❌ нет | ❌ отсутствует |
| 9 | XXL 3D castle installations for casino summer campaign | `/services/event-props-decor/` | ❌ нет | ❌ отсутствует |
| 10 | Freestanding 3D Amazon logo signage installation | `/services/3d-logo-branding-installations/` | ❌ нет | ❌ отсутствует |
| 11 | Floating Camp Poosh pool letters | `/services/floating-pool-letters/` | ❌ нет | ❌ отсутствует |
| 12 | Hunter conference sign | `/services/foam-monument-signs/` | ❌ нет | ❌ отсутствует |
| 13 | Custom 3D swirl logo element for Xumo expo booth | `/services/3d-logo-branding-installations/` | ❌ нет | ❌ отсутствует |
| 14 | 1 Billion & Beyond letters | `/services/oversize-foam-letters-logos/` | ❌ нет | ❌ отсутствует |
| 15 | Interactive phone booth installation | `/services/brand-activation-props/` | ❌ нет | ❌ отсутствует |
| 16 | Custom outdoor DWC letters: 5' branded letter installation | `/services/oversize-foam-letters-logos/` | ❌ нет | ❌ отсутствует |
| 17 | Engineering Giant mobile 3D signs | `/services/oversize-foam-letters-logos/` | ❌ нет | ❌ отсутствует |
| 18 | Large-scale 3D logo installation for ABC convention | `/services/3d-logo-branding-installations/` | ❌ нет | ❌ отсутствует |
| 19 | Custom experiential installation for Pandora | `/services/custom-foam-sculptures/` (+ вторичная `event-props-decor`) | ❌ нет | ❌ отсутствует |
| 20 | Oversized 3D PCMA letters + logo | `/services/oversize-foam-letters-logos/` (+ вторичная `3d-logo-branding-installations`) | ❌ нет | ❌ отсутствует |
| 21 | Oversized perfume bottle display for brand activation | `/services/foam-product-replicas/` | ❌ нет | ❌ отсутствует |
| 22 | The Modern Versailles project | `/services/architectural-shapes/` | ❌ нет | ❌ отсутствует |
| 23 | Large-scale 3D logo installation at College of Education | `/services/3d-logo-branding-installations/` | ❌ нет | ❌ отсутствует |
| 24 | Freestanding LOVE letter installation for wedding events | `/services/oversize-foam-letters-logos/` | ❌ нет | ❌ отсутствует |

## 3. Услуги → статьи и кейсы (обратное направление)

Проверены целиком 2 услуги + точечно `foam-monument-signs`, шаблон идентичен:

- **Блок статей есть, но это статичный виджет «3 самых старых поста»**, одинаковый на всех проверенных услугах (картинка + заголовок + анонс + «Discover more»):
  1. *Commercial monument signs on a deadline…* → `/commercial-monument-signs/` (пост №3)
  2. *Custom 3D props that turn events into shareable moments* → `/custom-3d-props-that-turn-events-into-shareable-moments/` (пост №2)
  3. *In the beginning was the idea…* → `/in-the-beginning-was-the-idea-how-we-turn-sketches-into-custom-monument-signs/` (пост №1)
  
  плюс ссылка «More blog posts» → `/blog/`. Тематической привязки нет: совпадение постов №1/№3 с услугой Monument Signs — случайность статичного блока, а не осознанная связка. **2 самых свежих поста (№4 architectural foam elements, №5 prop fabrication) с услуг не связаны вообще.**
- **Ссылок на кейсы (`/case/`) нет вообще.** При этом в SEO-тексте услуг есть мини-истории «Case Study: Maple Creek… / Heritage Dental… / Redwood Logistics… / Meadowbrook…» — обычным текстом, без ссылок на страницы кейсов.
- В шапке каждой услуги — блок «More services» (10 ссылок на смежные услуги) + бегущая строка услуг; также есть ссылки на `/portfolio/`, `/faq/`, технический центр. Состав топ-10 на `foam-monument-signs`: `outdoor-led-signs`, `molds-for-cast-stone-signs`, `sandblasted-signs`, `industrial-3d-printing`, `designs-for-places-of-worship`, `wedding-arch-colonnades`, `architectural-shapes`, `foam-routed-signs`, `small-metal-letters`, `illuminated-letters`.
- **Контекстных ссылок в SEO-тексте услуг на статьи/кейсы нет.**
- Следствие: кейсы (24/24) не получают с услуг ничего; из 5 статей 2 не получают ничего, 3 — только шаблонный блок.

## 4. Попутные находки (вне перелинковки, но важно)

1. **🐞 FAQ кейса «1 Billion & Beyond letters» называет чужой бренд.** Вопрос «Can Decorative Architectural Shapes handle…» — остаток копипаста с соседнего сайта группы. Критично для доверия.
2. **Единственная контентная ссылка ведёт не туда.** Пост №4 про architectural foam elements ссылается на `foam-monument-signs` вместо `architectural-shapes` — похоже на ошибку при простановке.
3. **Статичный блок «3 oldest» вместо «3 latest».** В отличие от сестринских сайтов (там виджет «3 последние статьи»), здесь блок застыл на трёх самых старых постах — свежие материалы не связаны с услугами.
4. **Мини-кейсы в тексте услуг не кликабельны.** 4 истории Maple Creek / Heritage Dental / Redwood / Meadowbrook на странице Monument Signs — готовые анкоры под ссылки на `/case/`, сейчас plain text.
5. ✅ **Позитивная проверка:** все URL из `post-sitemap.xml` и `case-sitemap.xml` живы, битых ссылок из sitemap нет.

## 5. Рекомендации (по приоритету)

1. **Исправить чужой бренд в FAQ кейса 1 Billion & Beyond** (одна правка, репутационный риск).
2. **Добавить контекстные ссылки «статья → своя услуга»** — по 1–2 ссылки в теле каждого из 5 постов (интро + CTA в конце); в посте №4 заменить ссылку на `architectural-shapes` (или добавить второй).
3. **Добавить CTA-ссылку на услугу в каждый кейс** (24 страницы): блок «Discuss the project» / «Related service» со ссылкой на услугу из таблицы выше.
4. **Сделать блок статей на услугах тематическим** (связь услуга → свой гайд + свои кейсы) вместо статичных «3 oldest»; минимум — переключить на «3 latest», чтобы не терять свежие посты.
5. **Добавить на услуги блок «Related cases»** и связать мини-истории в SEO-тексте с реальными страницами `/case/` (сейчас 0/24 кейсов получают ссылки с услуг).
6. **Сверить отчёт с контент-таблицей**, когда будут получены вкладки Royal Foam Art (статусы, URL только из таблицы, возможные переименования).

---
*Детальная построчная таблица — в файле `interlink-audit-art.csv` (разделитель `;`).*
