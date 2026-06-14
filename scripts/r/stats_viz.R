# считаем статистику и рисуем графики
# питон сам вызывает этот файл и передаёт папку output
# читаем готовые таблицы из output/tables и сохраняем картинки в output/plots

run_analysis <- function(output_dir) {
  tables_dir <- file.path(output_dir, "tables")
  plots_dir  <- file.path(output_dir, "plots")

  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    stop("Не установлен пакет ggplot2. Поставьте: install.packages('ggplot2')")
  }
  library(ggplot2)

  # UTF-8-BOM, потому что питон пишет файлы с BOM (чтобы Excel их нормально открывал)
  docs <- read.csv(file.path(tables_dir, "documents.csv"), fileEncoding = "UTF-8-BOM")

  # график 1: распределение настроения (гистограмма)
  g1 <- ggplot(docs, aes(x = score)) +
    geom_histogram(bins = 20, fill = "#4C72B0", color = "white") +
    labs(title = "Распределение тональности текстов",
         x = "Оценка тональности (от -1 до 1)", y = "Сколько текстов") +
    theme_minimal()
  ggsave(file.path(plots_dir, "sentiment_hist.png"), g1, width = 8, height = 5)

  # график 2: настроение по источникам (если источников больше одного)
  if (length(unique(docs$source)) > 1) {
    g2 <- ggplot(docs, aes(x = source, y = score, fill = source)) +
      geom_boxplot(show.legend = FALSE) +
      labs(title = "Тональность по источникам", x = "Источник", y = "Оценка") +
      theme_minimal()
    ggsave(file.path(plots_dir, "sentiment_by_source.png"), g2, width = 8, height = 5)
  }

  # график 3: как менялось среднее настроение по дням
  docs$day <- as.Date(docs$date)
  if (sum(!is.na(docs$day)) > 1) {
    by_day <- aggregate(score ~ day, data = docs, FUN = mean)
    g3 <- ggplot(by_day, aes(x = day, y = score, group = 1)) +
      geom_line(color = "#55A868") +
      geom_point(color = "#55A868") +
      labs(title = "Средняя тональность по дням", x = "Дата", y = "Среднее") +
      theme_minimal()
    ggsave(file.path(plots_dir, "dynamics.png"), g3, width = 8, height = 5)
  }

  # график 4: топ слов (читаем вторую таблицу)
  freq_file <- file.path(tables_dir, "word_freq.csv")
  if (file.exists(freq_file)) {
    freq <- read.csv(freq_file, fileEncoding = "UTF-8-BOM")
    freq <- head(freq, 15)
    freq$word <- factor(freq$word, levels = rev(freq$word))
    g4 <- ggplot(freq, aes(x = word, y = count)) +
      geom_col(fill = "#C44E52") +
      coord_flip() +
      labs(title = "Топ-15 частых слов", x = "", y = "Сколько раз") +
      theme_minimal()
    ggsave(file.path(plots_dir, "top_words.png"), g4, width = 8, height = 6)
  }

  # сохраняем сводную таблицу с цифрами
  summary <- data.frame(
    Показатель = c("Текстов", "Среднее настроение", "Стд отклонение",
                   "Доля позитивных", "Доля негативных"),
    Значение = c(nrow(docs), round(mean(docs$score), 4), round(sd(docs$score), 4),
                 round(mean(docs$label == "позитив"), 4),
                 round(mean(docs$label == "негатив"), 4))
  )
  # пишем с BOM, иначе Excel показывает кракозябры
  con <- file(file.path(tables_dir, "stats_summary.csv"), open = "w", encoding = "UTF-8")
  writeLines("﻿", con, sep = "")
  write.csv(summary, con, row.names = FALSE)
  close(con)

  lines <- c("Статистические тесты (R)", "")
  # Шапиро-Уилка, проверяет нормальное ли распределение
  sh <- shapiro.test(docs$score)
  lines <- c(lines, paste0("Шапиро-Уилк: W = ", round(sh$statistic, 4),
                           ", p = ", format(sh$p.value, digits = 4)))
  # ANOVA, есть ли разница в настроении между источниками
  if (length(unique(docs$source)) > 1) {
    model <- aov(score ~ source, data = docs)
    p <- summary(model)[[1]][["Pr(>F)"]][1]
    lines <- c(lines, paste0("ANOVA (настроение ~ источник): p = ", format(p, digits = 4)))
  }
  # UTF-8, иначе кракозябры :(
  con <- file(file.path(tables_dir, "stat_tests.txt"), open = "w", encoding = "UTF-8")
  writeLines(lines, con)
  close(con)
}

# если файл запустили через Rscript, берём папку из аргументов и считаем
args <- commandArgs(trailingOnly = TRUE)
if (length(args) >= 1) {
  run_analysis(args[1])
  cat("R: готово\n")
}
