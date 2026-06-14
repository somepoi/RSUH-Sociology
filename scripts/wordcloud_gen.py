# -*- coding: utf-8 -*-
# тут делаем облако слов (картинку, где частые слова крупнее)
# если библиотек нет, просто пропускаем

import os


def build_wordcloud(counts, output_path):
    # {слово: сколько раз}
    if not counts:
        return "Облако слов: нет данных"

    try:
        from wordcloud import WordCloud
        import matplotlib
        matplotlib.use("Agg")   # чтобы рисовать без открытия окна
        import matplotlib.pyplot as plt
    except Exception:
        return "Облако слов пропущено (не установлены wordcloud/matplotlib)"

    folder = os.path.dirname(output_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    try:
        wc = WordCloud(width=1000, height=600, background_color="white")
        wc = wc.generate_from_frequencies(counts)
        plt.figure(figsize=(10, 6))
        plt.imshow(wc)
        plt.axis("off")
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()
    except Exception as e:
        return "Не получилось сделать облако слов: " + str(e)

    return "Облако слов сохранено: " + output_path
