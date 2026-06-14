# -*- coding: utf-8 -*-
# меню

import os
import sys
import subprocess

from . import parser
from . import pipeline

# путь до папки проекта (на одну выше чем scripts)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANUAL = os.path.join(ROOT, "notes", "user_manual.pdf")
OUTPUT = os.path.join(ROOT, "output")


def ask_choice(question, options):
    # спрашиваем пока пользователь не введёт один из вариантов
    while True:
        answer = input(question).strip()
        if answer in options:
            return answer
        print("  ! Ошибка ввода. Введите:", ", ".join(options))


def ask_int(question, default, low, high):
    # спрашиваем число. если буква или пусто, то просим заново
    while True:
        answer = input(question + " (от " + str(low) + " до " + str(high) +
                       ", по умолчанию " + str(default) + "): ").strip()
        if answer == "":
            return default
        if not answer.lstrip("-").isdigit():
            print("  ! Нужно число")
            continue
        number = int(answer)
        if number < low or number > high:
            print("  ! Число должно быть от", low, "до", high)
            continue
        return number


def open_manual():
    # открываем инструкцию
    if not os.path.exists(MANUAL):
        print("  ! Инструкция не найдена:", MANUAL)
        return
    try:
        if sys.platform == "win32":
            os.startfile(MANUAL)
        elif sys.platform == "darwin":
            subprocess.run(["open", MANUAL])
        else:
            subprocess.run(["xdg-open", MANUAL])
        print("  Открыли инструкцию")
    except Exception as e:
        print("  ! Не вышло открыть. Откройте вручную:", MANUAL)


def open_folder():
    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)
    try:
        if sys.platform == "win32":
            os.startfile(OUTPUT)
        elif sys.platform == "darwin":
            subprocess.run(["open", OUTPUT])
        else:
            subprocess.run(["xdg-open", OUTPUT])
    except Exception:
        print("  ! Не вышло открыть папку:", OUTPUT)


def load_data(data):
    print()
    print("--- Загрузка новостей (RSS) ---")
    print("  1. Собрать со всех лент сразу")
    print("  2. Выбрать одну ленту из списка")
    print("  3. Ввести свой адрес RSS")
    print("  4. Загрузить сохранённую выгрузку (csv)")
    print("  0. Назад")
    choice = ask_choice("  Выберите: ", ["0", "1", "2", "3", "4"])

    if choice == "0":
        return

    # на каждый вариант ловим ошибку, чтобы программа не падала
    try:
        if choice == "1":
            data["rows"] = parser.fetch_many()
            parser.save_dump(data["rows"])
        elif choice == "2":
            names = list(parser.FEEDS.keys())
            for i in range(len(names)):
                print("   ", i + 1, names[i])
            num = ask_int("  Номер ленты", 1, 1, len(names))
            name = names[num - 1]
            data["rows"] = parser.fetch_rss(parser.FEEDS[name], name)
            parser.save_dump(data["rows"])
        elif choice == "3":
            url = input("  Введите адрес RSS: ").strip()
            if url == "":
                print("  ! Адрес не ввели")
                return
            data["rows"] = parser.fetch_rss(url)
            parser.save_dump(data["rows"])
        elif choice == "4":
            path = input("  Введите путь к csv: ").strip().strip('"')
            data["rows"] = parser.load_csv(path)
        data["desc"] = str(len(data["rows"])) + " текстов"
        print("  + Загрузили", len(data["rows"]), "текстов")
    except Exception as e:
        print("  ! Ошибка:", e)


def set_params(data):
    print()
    print("--- Параметры ---")
    data["top_n"] = ask_int("  Сколько топ-слов показывать", data["top_n"], 5, 100)
    print("  + Готово, top_n =", data["top_n"])


def run_analysis(data):
    if not data["rows"]:
        print("  ! Сначала загрузите данные (пункт 1)")
        return
    print()
    print("Считаем... (чистка, частоты, настроение, графики R)")
    try:
        report = pipeline.run_pipeline(data["rows"], OUTPUT, data["top_n"], data["threshold"])
    except Exception as e:
        print("  ! Не получилось:", e)
        return
    show_report(report)


def show_report(report):
    print()
    print("========== РЕЗУЛЬТАТЫ ==========")
    print("Текстов обработано:", report["n_docs"])
    s = report["sentiment"]
    print("Настроение: позитив =", s["позитив"],
          ", нейтрал =", s["нейтрал"], ", негатив =", s["негатив"])
    print()
    print("Топ слов:")
    place = 1
    for word, count in report["top"][:10]:
        print("  ", place, word, "-", count)
        place = place + 1
    print()
    print(report["wc_msg"])
    if report["r_ok"]:
        print("Графики и статистика R: ОК")
    else:
        print("Графики R: НЕ СДЕЛАНЫ")
        print(report["r_msg"])
    print()
    print("Таблицы лежат в:", report["tables_dir"])
    print("Графики лежат в:", report["plots_dir"])
    print("================================")


def main():
    data = {"rows": None, "desc": "не загружены", "top_n": 20, "threshold": 0.05}

    print("=" * 50)
    print(" Анализ тональности и частот текстов")
    print(" Python + R")
    print("=" * 50)

    while True:
        print()
        print("Данные:", data["desc"], "| top-слов:", data["top_n"])
        print("  1. Загрузить данные")
        print("  2. Настроить параметры")
        print("  3. Запустить анализ")
        print("  4. Инструкция (открыть pdf)")
        print("  5. Открыть папку с результатами")
        print("  0. Выход")

        choice = ask_choice("  > ", ["0", "1", "2", "3", "4", "5"])
        if choice == "1":
            load_data(data)
        elif choice == "2":
            set_params(data)
        elif choice == "3":
            run_analysis(data)
        elif choice == "4":
            open_manual()
        elif choice == "5":
            open_folder()
        elif choice == "0":
            print("Пока!")
            break
