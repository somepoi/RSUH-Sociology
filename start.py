# -*- coding: utf-8 -*-
# это главный файл, его и запускаем: python start.py
# тут немного настроек и переход в меню

import os
import sys


def main():
    # чтобы русские буквы в консоли винды не превращались в кракозябры
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

    # создаём папки, если их ещё нет
    for folder in ["output/plots", "output/tables", "data", "notes"]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # запускаем меню
    from scripts.menu import main as menu_main
    try:
        menu_main()
    except KeyboardInterrupt:
        print("\nВыход")


if __name__ == "__main__":
    main()
