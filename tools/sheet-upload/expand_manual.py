#!/usr/bin/env python3
"""Разворачивает компактные ручные выгрузки (manual/part*.tsv) в полноценные CSV для merge.py."""
import csv, glob, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
MANUAL = os.path.join(BASE, "manual")
OUTDIR = os.path.join(BASE, "received")
COLS = ["Сайт","Страница","URL","Документ","Ссылка на документ","Слов в тексте","Ключевая фраза","Статус","Вхождений"]

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    total = 0
    for part in sorted(glob.glob(os.path.join(MANUAL, "part*.tsv"))):
        meta, rows = None, []
        with open(part, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                if line.startswith("@"):
                    meta = line[1:].split("|")
                    continue
                if meta is None:
                    continue
                cells = line.split("\t")
                phrase = cells[0].strip()
                status = cells[1].strip() if len(cells) > 1 and cells[1].strip() else "Не использован"
                count = cells[2].strip() if len(cells) > 2 and cells[2].strip() else "0"
                rows.append([meta[0], meta[1], meta[2], meta[3], meta[4], meta[5], phrase, status, count])
        name = os.path.splitext(os.path.basename(part))[0] + ".csv"
        with open(os.path.join(OUTDIR, name), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(COLS)
            w.writerows(rows)
        print(f"{os.path.basename(part)}: страниц/блоков — строк {len(rows)} -> {name}")
        total += len(rows)
    print("всего строк:", total)

if __name__ == "__main__":
    main()
