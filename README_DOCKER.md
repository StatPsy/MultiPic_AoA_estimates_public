# Use the MultiPic AoA Docker environment

## 1. Docker installation

Install Docker Desktop ([Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
or [Mac](https://docs.docker.com/desktop/setup/install/mac-install/)) and start it.
On Windows, use Linux containers. Linux users can use
[Docker Engine](https://docs.docker.com/engine/install/).

Download this project using **Code > Download ZIP** and extract it. Open a terminal
in the project folder containing **`Dockerfile`**. On Windows, right-click inside
the folder, choose **Open in Terminal**, and use **PowerShell**.

## 2. Build the environment (only once)

```text
docker build --platform linux/amd64 --tag multipic-aoa-env:1.0.0 .
```

Include the final **`.`**. This installs the fixed R and Python packages and may
take several minutes. Internet access is required.

## 3. Open the environment

Run the command for your computer from the same project folder:

**Windows / PowerShell**

```powershell
docker run --rm -it --init --pull never --platform linux/amd64 --mount "type=bind,source=$($PWD.Path),target=/project" multipic-aoa-env:1.0.0
```

**Mac or Linux**

```bash
docker run --rm -it --init --pull never --platform linux/amd64 --user "$(id -u):$(id -g)" --mount "type=bind,source=$(pwd),target=/project" multipic-aoa-env:1.0.0
```

You are now inside Docker, with the `aoa` environment active. Your local project
is available at **`/project`**. Scripts run only when you launch them.

## 4. Run the scripts manually

To regenerate the estimates using the archived study lists, run these commands
**inside Docker**, one at a time and in order. Stop if a command reports an error.

```bash
# Download missing reference data (requires internet).
cd /project/external_resources
python download_corpora.py

# Add database information to the raw ratings.
cd /project/estimates/src
Rscript --vanilla -e "rmarkdown::render('merge_database_infos.Rmd', output_format = 'html_document', envir = new.env())"

# Generate participant metadata.
Rscript --vanilla -e "rmarkdown::render('generate_participants_metadata.Rmd', output_format = 'html_document', envir = new.env())"

# Calculate and analyse estimates for the unique items.
Rscript --vanilla -e "rmarkdown::render('AoA_estimates_for_MultiPic.Rmd', output_format = 'html_document', envir = new.env())"

# Add duplicate items to produce the complete estimates.
python fill_in_info_for_duplicates.py
```

CSV outputs are saved in your local **`estimates/data`** folder; HTML reports are
saved in **`estimates/src`**. The R Markdown files load `helper_functions.R`
automatically.

Edit scripts with your usual editor on your computer, then run them again in the
Docker terminal. Your edits are available immediately. Type **`exit`** to leave
Docker; changes and outputs in the project folder stay on your computer.

Further script details: [estimates](estimates/src/README.md),
[external resources](external_resources/README.md), and
[study setup](study_setup/src/README.md).
