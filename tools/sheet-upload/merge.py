#!/usr/bin/env python3
"""
Сведение листов Google-таблицы kw_results_rev2 в одну таблицу.

Вход:  файлы в tools/sheet-upload/received/ — книга .xlsx (все листы) и/или отдельные .csv по листам.
Выход: kw_results_merged.csv  — одна таблица, строки всех листов подряд,
       добавлена колонка «Лист» (откуда строка) и убраны полные дубликаты.

Запуск:  python3 tools/sheet-upload/merge.py [out.csv]
"""
import csv
import os
import re
import sys
import glob
import html as html_mod

BASE = os.path.dirname(os.path.abspath(__file__))
RECEIVED = os.path.join(BASE, "received")

# Порядок листов в итоговом файле и подписи для колонки «Лист»
SHEET_ORDER = ["shapes", "royalfoam", "products"]

# Ключевые слова, по которым узнаём строку заголовков
HEADER_HINTS = ["сайт", "страница", "url", "документ", " ключевая фраза", "ключевая фраза", "статус", "вхождений"]

# Колонки, которые хотим видеть первыми (остальные — в порядке появления)
PREFERRED = ["Лист", "Сайт", "Страница", "URL", "Документ", "Ссылка на документ",
             "Слов в тексте", "Ключевая фраза", "Статус", "Вхождений"]


def norm(v):
    return ("" if v is None else str(v)).replace("\xa0", " ").strip()


SITE_TO_SHEET = {
    "decorativearchitecturalshapes": "shapes",
    "decorativearchitecturalproducts": "products",
    "royalfoam": "royalfoam",
}


def label_by_site(value):
    low = norm(value).lower()
    for key, label in SITE_TO_SHEET.items():
        if key in low:
            return label
    return ""


def guess_sheet_label(name):
    """Человеческая подпись листа по имени файла/листа."""
    n = os.path.basename(name).lower()
    for key in SHEET_ORDER:
        if key in n:
            return key
    return os.path.splitext(os.path.basename(name))[0]


def looks_like_header(row):
    low = [norm(c).lower() for c in row]
    if not any(low):
        return False
    hits = 0
    for cell in low:
        if any(h.strip() in cell for h in HEADER_HINTS):
            hits += 1
    # заголовок «Сайт | Страница | ...» узнаём по 3+ совпадениям
    return hits >= 3


def rows_from_xlsx(path):
    """Все листы книги: [(label, rows)] — rows вместе с заголовком."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = []
    for ws in wb.worksheets:
        rows = [[norm(c) for c in r] for r in ws.iter_rows(values_only=True)]
        rows = [r for r in rows if any(r)]
        if rows:
            out.append((guess_sheet_label(ws.title), rows))
    wb.close()
    return out


def rows_from_html(path):
    """Листы из HTML-рендера gviz (там сразу все листы одной таблицей)."""
    import re
    with open(path, encoding="utf-8", errors="replace") as f:
        doc = f.read()
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", doc, re.S | re.I):
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S | re.I)
        cells = [re.sub(r"<[^>]+>", "", c) for c in cells]
        cells = [html_mod.unescape(c).replace("\xa0", " ").strip() for c in cells]
        if any(cells):
            rows.append(cells)
    return [("all", rows)] if rows else []


def rows_from_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(8192)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except Exception:
            dialect = csv.excel
        rows = [[norm(c) for c in r] for r in csv.reader(f, dialect)]
    rows = [r for r in rows if any(r)]
    return [(guess_sheet_label(path), rows)] if rows else []


def split_blocks(rows):
    """Файл может содержать несколько таблиц подряд (каждая со своей шапкой)."""
    blocks, cur = [], []
    for r in rows:
        if looks_like_header(r):
            if cur:
                blocks.append(cur)
            cur = [r]
        else:
            cur.append(r)
    if cur:
        blocks.append(cur)
    return blocks


def collect():
    """Все источники: [(label, header, data_rows)]."""
    sources = []

    for path in sorted(glob.glob(os.path.join(RECEIVED, "*.xlsx")) + glob.glob(os.path.join(RECEIVED, "*.xls"))):
        try:
            for label, rows in rows_from_xlsx(path):
                for block in split_blocks(rows):
                    header = block[0] if looks_like_header(block[0]) else None
                    data = block[1:] if header else block
                    sources.append((label, header, data))
        except Exception as e:
            print(f"  ! {os.path.basename(path)}: не удалось прочитать ({e})")

    for path in sorted(glob.glob(os.path.join(RECEIVED, "*.html"))):
        try:
            for label, rows in rows_from_html(path):
                for block in split_blocks(rows):
                    header = block[0] if looks_like_header(block[0]) else None
                    data = block[1:] if header else block
                    sources.append((label, header, data))
        except Exception as e:
            print(f"  ! {os.path.basename(path)}: не удалось прочитать ({e})")

    for path in sorted(glob.glob(os.path.join(RECEIVED, "*.csv")) + glob.glob(os.path.join(RECEIVED, "*.tsv"))):
        try:
            for label, rows in rows_from_csv(path):
                for block in split_blocks(rows):
                    header = block[0] if looks_like_header(block[0]) else None
                    data = block[1:] if header else block
                    sources.append((label, header, data))
        except Exception as e:
            print(f"  ! {os.path.basename(path)}: не удалось прочитать ({e})")

    return sources


def header_columns(sources):
    """Единый набор колонок: сначала известные, потом новые."""
    seen = []
    for _, header, _ in sources:
        for c in (header or []):
            if c and c not in seen:
                seen.append(c)
    cols = [c for c in PREFERRED if c in seen]
    cols += [c for c in seen if c not in cols]
    return cols


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(BASE.rstrip("/")), "kw_results_merged.csv")

    sources = collect()
    if not sources:
        print(f"Нет данных: положите .xlsx или .csv в {RECEIVED}")
        return 1

    cols = header_columns(sources)
    print("Колонки итога:", ", ".join(["Лист"] + [c for c in cols if c != "Лист"]))

    # порядок листов: shapes → royalfoam → products → прочие
    def sort_key(item):
        label = item[0].lower()
        for i, key in enumerate(SHEET_ORDER):
            if key in label:
                return (i, label)
        return (len(SHEET_ORDER), label)

    merged = []
    seen_rows = set()
    stats = []
    for label, header, data in sorted(sources, key=sort_key):
        idx = {c: (header.index(c) if header and c in header else None) for c in cols}
        n, dup = 0, 0
        for r in data:
            row = {}
            for c in cols:
                i = idx.get(c)
                row[c] = r[i] if (i is not None and i < len(r)) else ""
            row["Лист"] = label_by_site(row.get("Сайт", "")) or label
            key = tuple(row.get(c, "") for c in cols)
            if key in seen_rows:
                dup += 1
                continue
            seen_rows.add(key)
            merged.append(row)
            n += 1
        stats.append((label, n, dup))

    out_cols = ["Лист"] + [c for c in cols if c != "Лист"]

    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=out_cols, delimiter=";")
        w.writeheader()
        for row in merged:
            w.writerow(row)

    print()
    for label, n, dup in stats:
        extra = f", дубликатов отброшено: {dup}" if dup else ""
        print(f"  {label:<28} строк: {n}{extra}")
    print(f"\nИтого строк: {len(merged)}")
    print(f"Файл: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
