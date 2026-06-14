# -*- coding: utf-8 -*-
# чистим тексты, считаем частоты и настроение,
# сохраняем таблицы, делаем облако слов и делаеим графикы

import os
import csv

from . import preprocess
from . import analysis
from . import wordcloud_gen
from . import r_bridge


def run_pipeline(rows, output_dir="output", top_n=20, threshold=0.05):
    # rows - список текстов
    if not rows:
        raise Exception("Нет данных. Сначала загрузите данные (пункт 1)")

    tables_dir = os.path.join(output_dir, "tables")
    plots_dir = os.path.join(output_dir, "plots")
    if not os.path.exists(tables_dir):
        os.makedirs(tables_dir)
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)

    # чистим тексты и считаем
    texts = []
    for r in rows:
        texts.append(r.get("text", ""))
    corpus = preprocess.preprocess_corpus(texts)

    sentiments = analysis.analyze_documents(corpus, threshold)
    top = analysis.top_words(corpus, top_n)
    all_counts = analysis.count_words(corpus)
    summary = analysis.sentiment_summary(sentiments)

    # сохраняем таблицу по каждому тексту (её потом читает R)
    # encoding utf-8-sig добавляет BOM, иначе Excel показывает кракозябры
    with open(os.path.join(tables_dir, "documents.csv"), "w",
              encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "source", "score", "label"])
        for i in range(len(rows)):
            r = rows[i]
            s = sentiments[i]
            writer.writerow([r.get("id", ""), r.get("date", ""),
                             r.get("source", ""), s["score"], s["label"]])

    # сохраняем таблицу частот слов
    # берём топ 50 слов
    all_pairs = list(all_counts.items())
    all_pairs.sort(key=lambda x: x[1], reverse=True)
    with open(os.path.join(tables_dir, "word_freq.csv"), "w",
              encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "count"])
        for word, count in all_pairs[:50]:
            writer.writerow([word, count])

    # облако слов (по первым 100 словам)
    top100 = {}
    for word, count in all_pairs[:100]:
        top100[word] = count
    wc_msg = wordcloud_gen.build_wordcloud(top100, os.path.join(plots_dir, "wordcloud.png"))

    # считаем статистику, рисуем графики
    r_ok, r_msg = r_bridge.run_r_analysis(output_dir)

    # отдаём в менюшку
    report = {
        "n_docs": len(rows),
        "top": top,
        "sentiment": summary,
        "wc_msg": wc_msg,
        "r_ok": r_ok,
        "r_msg": r_msg,
        "tables_dir": tables_dir,
        "plots_dir": plots_dir,
    }
    return report
