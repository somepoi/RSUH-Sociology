# -*- coding: utf-8 -*-
# считаем статистику, рисуем графики
# сначала пробуем через библиотеку rpy2, если не вышло, то через команду Rscript

import os
import shutil
import subprocess

# путь к нашему R-скрипту
R_SCRIPT = os.path.join(os.path.dirname(__file__), "r", "stats_viz.R")


def _try_rpy2(output_dir):
    # без этого блока rpy2 на винде не находит R и падает
    if not os.environ.get("R_HOME"):
        rscript = shutil.which("Rscript")
        if rscript:
            # из ...\R-4.5.2\bin\Rscript.exe получаем папку ...\R-4.5.2
            r_home = os.path.dirname(os.path.dirname(rscript))
            os.environ["R_HOME"] = r_home
            os.environ["PATH"] = (os.path.join(r_home, "bin") + os.pathsep +
                                  os.path.join(r_home, "bin", "x64") + os.pathsep +
                                  os.environ.get("PATH", ""))

    # это тоже, иначе русские буквы из R ломают питон с ошибкой
    from rpy2.rinterface_lib import callbacks
    callbacks._CCHAR_ENCODING = "latin-1"
    callbacks.consolewrite_print = lambda s: None
    callbacks.consolewrite_warnerror = lambda s: None

    import rpy2.robjects as ro
    # encoding="UTF-8" обязательно, иначе R не понимает русские буквы в скрипте
    ro.r["source"](R_SCRIPT.replace("\\", "/"), encoding="UTF-8")
    run = ro.globalenv["run_analysis"]
    run(str(output_dir).replace("\\", "/"))


def _try_rscript(output_dir):
    rscript = shutil.which("Rscript")
    if rscript is None:
        rscript = "Rscript"
    result = subprocess.run([rscript, R_SCRIPT, str(output_dir)],
                            capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=180)
    if result.returncode != 0:
        raise Exception(result.stderr)


def run_r_analysis(output_dir):
    # создаём папки на всякий случай
    if not os.path.exists(os.path.join(output_dir, "plots")):
        os.makedirs(os.path.join(output_dir, "plots"))
    if not os.path.exists(os.path.join(output_dir, "tables")):
        os.makedirs(os.path.join(output_dir, "tables"))

    # rpy2
    try:
        _try_rpy2(output_dir)
        return True, "Анализ в R сделан (через rpy2)"
    except Exception as e1:
        error1 = str(e1)

    # попытка 2, через Rscript
    try:
        _try_rscript(output_dir)
        return True, "Анализ в R сделан (через Rscript)"
    except Exception as e2:
        return False, ("Не получилось запустить R.\n  rpy2: " + error1 +
                       "\n  Rscript: " + str(e2))
