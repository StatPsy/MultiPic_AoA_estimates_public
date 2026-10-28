"""
This script downloads all existing corpora necessary for the survey's stimuli creation
as well as the estimate validation:
    - Schröder (2012)
    - Birchenough (2017)
    - MultiPic (2018, 2022)
    - Kuperman (2012)
    - (SUBTLEX-DE; Marc Brysbaert's website currently under construction)

Run with: $ python3 download_corpora.py

If you already have those databases saved locally, feel free to change the paths in the 
specific files to point to your copies instead of downloading them anew.

"""

from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import ZipFile

import pandas as pd


ROOT = Path(__file__).resolve().parent
NORM_URLS = {
    "Schröder_2012.xls": "https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-011-0164-y/MediaObjects/13428_2011_164_MOESM1_ESM.xls",
    "Birchenough_2017.csv": "https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-016-0718-0/MediaObjects/13428_2016_718_MOESM1_ESM.csv",
    "Kuperman_2012.xlsx": "https://static-content.springer.com/esm/art%3A10.3758%2Fs13428-013-0348-8/MediaObjects/13428_2013_348_MOESM1_ESM.xlsx",
}


def fetch(url):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(request, timeout=90) as response:
            return response.read()
    except (HTTPError, URLError) as exc:
        raise SystemExit(f"Download failed: {exc}\nSource: {url}") from exc


def expected_file(name, data):
    if name.endswith(".xls"):
        return data.startswith(bytes.fromhex("d0cf11e0a1b11ae1"))
    if name.endswith(".xlsx"):
        return data.startswith(b"PK\x03\x04")
    return bool(data) and not data[:256].lstrip().lower().startswith(b"<!doctype html")


def download_multipic():
    multipic = ROOT / "multipic"
    version1 = multipic / "German_MultiPic_version1.csv"
    version5 = multipic / "MultiPic_version5.csv"
    if not version1.exists():
        url = "https://www.bcbl.eu/bcbl-corporativa/wp-content/uploads/2016/10/German_MultiPic.zip"
        with ZipFile(BytesIO(fetch(url))) as archive:
            version1.write_bytes(archive.read("German_MultiPic_CSV.csv"))
        print("Saved", version1)
    if not version5.exists():
        url = "https://figshare.com/ndownloader/files/34462247"
        data = fetch(url)
        if not expected_file("MultiPic_version5.csv", data):
            raise SystemExit("The MultiPic version 5 URL did not return a CSV file.")
        source = multipic / "_MultiPic_version5_download.csv"
        source.write_bytes(data)
        try:
            df = pd.read_csv(source, sep=";", decimal=",")
            df.to_csv(version5, sep=";", decimal=",", index=False)
        finally:
            source.unlink(missing_ok=True)
        print("Saved", version5)


def download_norms():
    norms = ROOT / "norms"
    for name, url in NORM_URLS.items():
        output = norms / name
        if output.exists() and output.stat().st_size > 0:
            print("Already present:", output)
            continue
        print("Downloading", name, "...", flush=True)
        data = fetch(url)
        if not expected_file(name, data):
            raise SystemExit(f"The server did not return the expected file: {name}\nSource: {url}")
        output.write_bytes(data)
        print("Saved", output)


def main():
    for directory in ("multipic", "norms", "frequencies"):
        (ROOT / directory).mkdir(exist_ok=True)

    if (ROOT / "MultiPic_with_frequencies.csv").is_file():
        print("Using the archived MultiPic_with_frequencies.csv; skipping the MultiPic source downloads.")
    else:
        print("Merged MultiPic data not found; attempting to download the source corpora.")
        download_multipic()

    # SUBTLEX-DE is included in the project's GitHub archive.
    download_norms()
    print("All available reference files are ready.")


if __name__ == "__main__":
    main()
