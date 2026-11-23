#!/usr/bin/env python3
"""Download the latest Glottolog languoid CSV linked by its official download page.

The script records the exact download URL, release label, timestamps and SHA-256
hashes. It extracts only the expected CSV from the ZIP and rejects unsafe paths.
"""
import argparse
import csv
import hashlib
import json
import re
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

PAGE = "https://glottolog.org/download"
MAX_ZIP_BYTES = 25 * 1024 * 1024

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.href = None
        self.text = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self.href = dict(attrs).get("href")
            self.text = []
    def handle_data(self, data):
        if self.href is not None:
            self.text.append(data)
    def handle_endtag(self, tag):
        if tag.lower() == "a" and self.href is not None:
            self.links.append((self.href, " ".join(self.text)))
            self.href = None
            self.text = []

def get(url, limit):
    request = urllib.request.Request(url, headers={"User-Agent": "AWEFonts-Open-Data-Importer/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        final_url = response.geturl()
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("download exceeded configured size limit")
    return data, final_url

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="upstream/glottolog")
    parser.add_argument("--page-url", default=PAGE)
    parser.add_argument("--max-zip-mb", type=int, default=25)
    args = parser.parse_args()
    if not args.page_url.startswith("https://glottolog.org/"):
        parser.error("--page-url must be on https://glottolog.org/")
    page, page_final = get(args.page_url, 5 * 1024 * 1024)
    html = page.decode("utf-8", errors="replace")
    links = Links()
    links.feed(html)
    match = next(((href, label) for href, label in links.links
                  if "glottolog_languoid.csv.zip" in (href or "") + " " + label), None)
    if not match:
        raise SystemExit("Official page did not expose a glottolog_languoid.csv.zip link")
    href, label = match
    download_url = urllib.parse.urljoin(page_final, href)
    if not download_url.startswith("https://"):
        raise SystemExit("Refusing a non-HTTPS Glottolog download URL")
    zip_data, final_url = get(download_url, args.max_zip_mb * 1024 * 1024)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    zip_path = out / "glottolog_languoid.csv.zip"
    zip_path.write_bytes(zip_data)
    with zipfile.ZipFile(zip_path) as archive:
        candidates = [i for i in archive.infolist()
                      if i.filename.lower().endswith(".csv")
                      and "languoid" in Path(i.filename).name.lower()]
        if len(candidates) != 1:
            raise SystemExit("Expected exactly one languoid CSV in archive")
        info = candidates[0]
        member = Path(info.filename)
        if member.is_absolute() or ".." in member.parts or info.file_size > 20 * 1024 * 1024:
            raise SystemExit("Unsafe or unexpectedly large CSV member")
        csv_data = archive.read(info)
    text = csv_data.decode("utf-8-sig")
    reader = csv.DictReader(text.splitlines())
    headers = {h.lower() for h in (reader.fieldnames or [])}
    if not {"id", "name", "level"}.issubset(headers):
        raise SystemExit("CSV does not contain required id, name and level columns")
    csv_path = out / "glottolog_languoid.csv"
    csv_path.write_bytes(csv_data)
    version_match = re.search(r"\bVersion\s+([0-9.]+)", html, re.I)
    manifest = {
        "source": "Glottolog official downloads",
        "sourcePage": page_final,
        "release": version_match.group(1) if version_match else None,
        "linkLabel": label,
        "downloadUrl": final_url,
        "downloadedAt": datetime.now(timezone.utc).isoformat(),
        "zip": {"path": zip_path.name, "bytes": len(zip_data), "sha256": sha(zip_data)},
        "csv": {"path": csv_path.name, "bytes": len(csv_data), "sha256": sha(csv_data), "archiveMember": info.filename},
        "note": "The Glottolog CSV contains languoids; use level=language for language-only counts. Dialects and families are distinct record levels."
    }
    (out / "glottolog-download-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
