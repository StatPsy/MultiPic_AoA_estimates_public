# Check every R package version and load the packages used by the R Markdown files.
lock <- renv::lockfile_read("/opt/aoa/renv.lock")
expected <- jsonlite::fromJSON("/opt/aoa/expected-python.json")
stopifnot(as.character(getRversion()) == lock$R$Version)
stopifnot(as.character(packageVersion("renv")) == expected$renv)
problems <- character()
for (name in names(lock$Packages)) {
  actual <- tryCatch(as.character(packageVersion(name)),
                     error = function(error) "missing")
  if (actual == "missing" || utils::compareVersion(actual, lock$Packages[[name]]$Version) != 0L) {
    problems <- c(problems, paste(name, "expected", lock$Packages[[name]]$Version,
                                  "but found", actual))
  }
}
if (length(problems) > 0) {
  stop(paste(problems, collapse = "\n"))
}
packages <- c("tibble", "readr", "readxl", "readODS", "dplyr", "magrittr",
              "ggplot2", "RColorBrewer", "cowplot", "stringr", "knitr", "rmarkdown")
for (name in packages) {
  library(name, character.only = TRUE)
}
stopifnot(rmarkdown::pandoc_available())
stopifnot(as.character(rmarkdown::pandoc_version()) == expected$pandoc)
cat("R", as.character(getRversion()), "and", length(lock$Packages),
    "locked R package versions verified.\n")
