# запускаем один раз, чтобы поставить пакет ggplot2 (графики)
# запуск:  Rscript scripts/r/install_packages.R

if (!requireNamespace("ggplot2", quietly = TRUE)) {
  cat("Ставим ggplot2...\n")
  install.packages("ggplot2", repos = "https://cloud.r-project.org")
} else {
  cat("ggplot2 уже есть\n")
}
cat("Готово\n")
