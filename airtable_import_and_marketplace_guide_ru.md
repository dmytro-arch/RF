# Исправленные PIM-таблицы для Airtable и маркетплейсов

## Что подготовлено

| Файл | Назначение |
|---|---|
| `airtable_products_corrected.csv` | Исходная Products-таблица с сохранёнными колонками и добавленными нормализованными полями |
| `airtable_variations_corrected.csv` | Исходная Variations-таблица с исправленными связями и полями для фидов |
| `airtable_products_normalized.csv` | Чистая нормализованная Products-таблица для новой структуры Airtable |
| `airtable_variations_normalized.csv` | Чистая нормализованная Variations-таблица; связь с Products через `Parent SKU` |
| `airtable_marketplace_offers.csv` | Одна строка на вариацию и сайт назначения; основа для Google, Pinterest и Meta views |

## Что исправлено автоматически

- очищены лишние кавычки, пробелы и переносы в SKU и связях;
- каждая однозначно распознаваемая вариация связана с одним родителем;
- список вариаций родителей перестроен по исправленным связям;
- `Regular Price` разделена на числовое значение и валюту USD;
- добавлены `condition=new`, `item_group_id`, вычисляемый `availability` и название вариации;
- Width, Height, Length, Depth, Projection, Diameter и Sides вынесены в отдельные колонки;
- назначен бренд по сайту назначения;
- один товар, размещённый на нескольких сайтах, разделён на отдельные marketplace offers;
- добавлены `PIM Issues` и статусы готовности.

Неизвестные значения не выдумывались: URL, Google category, GTIN/MPN, Material, вес и доставка оставлены пустыми.

## Как импортировать в Airtable

### Вариант 1 — обновить текущую базу

1. Сделать резервную копию базы.
2. Импортировать `airtable_products_corrected.csv` в Products с объединением по `SKU`.
3. Импортировать `airtable_variations_corrected.csv` в Variations с объединением по `Variation Label` или `Variation SKU`.
4. Проверить, что `Parent Product` является Linked record на Products и сопоставляется с `Product Label`.
5. После проверки использовать `Corrected Variations` вместо старого списка `Variations`.

### Вариант 2 — новая нормализованная структура

1. Создать таблицу Products и импортировать `airtable_products_normalized.csv`; primary field — `Product SKU`.
2. Создать таблицу Variations и импортировать `airtable_variations_normalized.csv`; primary field — `Variation Record Key`. Для четырёх строк без SKU ключ сформирован как `UNRESOLVED::<Variation Label>`, поэтому ни одна запись не теряется.
3. Преобразовать `Parent SKU` в Linked record на Products.
4. Создать таблицу Marketplace Offers и импортировать `airtable_marketplace_offers.csv`; primary field — `Offer Key`.
5. При необходимости связать поле `id` Marketplace Offers с `Variation SKU` таблицы Variations.

## Текущая готовность

- 1 845 из 1 862 вариаций структурно готовы к импорту в Airtable;
- 17 вариаций требуют ручного исправления связей/SKU;
- 2 776 site-specific offers сформированы;
- пока ни один offer не готов к публикации на маркетплейсах, потому что отсутствуют Product URL, Google Product Category и подтверждённая схема идентификаторов; также нужны стабильные изображения, остатки и публикационные статусы.

## Что заполнить перед экспортом

1. `Product Link` — URL карточки с выбранной вариацией.
2. `Google Product Category` — категория из таксономии Google.
3. `GTIN` или `MPN`; для уникальных изделий — корректное `Identifier Exists`.
4. `Material`, выбранные `Color` и `Texture / Pattern`.
5. `Stock` и `Availability` для каждой публикуемой вариации.
6. Постоянные `image_link` на домене сайта/CDN вместо Airtable attachment URL.
7. Вес, размеры упаковки и правила freight-доставки.
8. Исправить строки со статусом `NEEDS_REVIEW` и исключить тестовые SKU.

Для экспорта следует создавать Airtable Views отдельно для каждого сайта и площадки с фильтром соответствующего Status = `READY`.
