# Restore Linux packages from the supplied R lockfile; no Windows libraries are copied.
lock <- renv::lockfile_read("/opt/aoa/renv.lock")
if (as.character(getRversion()) != lock$R$Version) {
  stop("The R runtime does not match renv.lock.")
}
library_path <- Sys.getenv("R_LIBS_USER")
dir.create(library_path, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(library_path, .libPaths()))
renv::restore(lockfile = "/opt/aoa/renv.lock", library = library_path,
              prompt = FALSE)
