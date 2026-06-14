# -*- coding: utf-8 -*-
# берём тексты для анализа из RSS-лент новостей

import os
import csv

# готовые ленты (название: адрес).
FEEDS = {
    "Лента.ру": "https://lenta.ru/rss/news",
    "РИА Новости": "https://ria.ru/export/rss2/archive/index.xml",
    "Ведомости": "https://www.vedomosti.ru/rss/news",
    "РБК": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
    "ТАСС": "https://tass.ru/rss/v2.xml",
}

DUMP_PATH = "data/sample_texts.csv"


def _parse_date(s):
    # из ленты дата приходит в разном виде, приводим к 2025-06-16
    s = s.strip()
    if s == "":
        return ""
    # формат типа 2025-06-16T09:30:00
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10]
    # формат типа "Mon, 16 Jun 2025 09:30:00 +0300" (обычный rss)
    try:
        from email.utils import parsedate_to_datetime
        d = parsedate_to_datetime(s)
        return d.strftime("%Y-%m-%d")
    except Exception:
        return ""


def fetch_rss(url, source_name=None):
    # скачиваем одну ленту, берём заголовок + описание + дату
    if source_name is None:
        source_name = url

    try:
        import requests
        from bs4 import BeautifulSoup
    except Exception:
        raise Exception("Не установлены requests и beautifulsoup4 (pip install -r requirements.txt)")

    try:
        page = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        page.raise_for_status()
    except Exception:
        raise Exception("Не получилось загрузить ленту. Проверьте интернет и адрес: " + url)

    rows = []
    try:
        soup = BeautifulSoup(page.content, "xml")
        items = soup.find_all(["item", "entry"])
        i = 0
        for item in items:
            title = item.find("title")
            desc = item.find(["description", "summary", "content"])
            date = item.find(["pubDate", "published", "updated"])

            text = ""
            if title is not None:
                text = title.get_text().strip()
            if desc is not None:
                text = text + ". " + desc.get_text().strip()
            text = text.strip(". ").strip()
            if text == "":
                continue

            i = i + 1
            day = ""
            if date is not None:
                day = _parse_date(date.get_text())
            rows.append({"id": str(i), "date": day, "source": source_name, "text": text})
    except Exception:
        raise Exception("Не получилось разобрать ленту")

    if len(rows) == 0:
        raise Exception("Лента загрузилась, но текстов в ней не найдено")
    return rows


def fetch_many(feeds=None):
    # собираем сразу несколько лент. каждый текст помечаем его источником
    if feeds is None:
        feeds = FEEDS

    all_rows = []
    broken = []
    for name in feeds:
        url = feeds[name]
        try:
            rows = fetch_rss(url, name)
            all_rows = all_rows + rows
        except Exception:
            broken.append(name)   # одна сломанная лента не должна ломать всё

    if len(all_rows) == 0:
        raise Exception("Не получилось собрать ни одной ленты. Проверьте интернет.")

    # перенумеровываем id, потому что в каждой ленте они начинались с 1
    for j in range(len(all_rows)):
        all_rows[j]["id"] = str(j + 1)

    if broken:
        print("  (не открылись ленты:", ", ".join(broken), ")")
    return all_rows


def save_dump(rows, path=DUMP_PATH):
    # сохраняем выгрузку в csv, чтобы потом можно было не качать заново
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    # utf-8-sig добавляет BOM, чтобы Excel открывал без кракозябр
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "source", "text"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def load_csv(path):
    # читаем сохранённую раньше выгрузку (csv). нужна колонка с текстом
    if not os.path.exists(path):
        raise Exception("Файл не найден: " + path)

    rows = []
    try:
        f = open(path, "r", encoding="utf-8-sig", newline="")
    except Exception:
        raise Exception("Не получилось открыть файл: " + path)

    with f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise Exception("Файл пустой или это не csv")

        text_col = None
        date_col = None
        source_col = None
        for name in reader.fieldnames:
            low = name.lower().strip()
            if low in ("text", "текст", "comment", "message"):
                text_col = name
            if low in ("date", "дата"):
                date_col = name
            if low in ("source", "источник"):
                source_col = name

        if text_col is None:
            raise Exception("В файле нет колонки с текстом (нужна колонка 'text' или 'текст')")

        i = 0
        for line in reader:
            text = line.get(text_col, "")
            if text is None:
                text = ""
            text = text.strip()
            if text == "":
                continue
            i = i + 1
            date = ""
            if date_col is not None and line.get(date_col):
                date = line[date_col].strip()
            source = "CSV"
            if source_col is not None and line.get(source_col):
                source = line[source_col].strip()
            rows.append({"id": str(i), "date": date, "source": source, "text": text})

    if len(rows) == 0:
        raise Exception("В файле нет ни одной строки с текстом")
    return rows
