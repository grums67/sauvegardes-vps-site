#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
PAGES = (ROOT / "index.html", ROOT / "privacy.html")
FORBIDDEN_NAMES = re.compile(r"(?:\.env|credentials?|secrets?|tokens?|\.db$|\.sqlite|\.log$|\.json$)", re.I)
SECRET_PATTERNS = {
    "GitHub token": re.compile(r"gh[opsu]_[A-Za-z0-9]{20,}"),
    "Google OAuth client secret": re.compile(r"GOCSPX-[A-Za-z0-9_-]{20,}"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "generic secret assignment": re.compile(r"(?:client_secret|access_token|refresh_token)\s*[:=]\s*['\"][^'\"]+", re.I),
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "private/VPS path": re.compile(r"/(?:root|home|srv|var)/(?:[^<\s'\"]+)", re.I),
    "internal endpoint": re.compile(r"https?://(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)", re.I),
}

class Checker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.title = []
        self.in_title = False
        self.links = []
        self.scripts = 0
        self.h1 = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html": self.lang = attrs.get("lang")
        if tag == "title": self.in_title = True
        if tag == "a" and attrs.get("href"): self.links.append(attrs["href"])
        if tag == "script": self.scripts += 1
        if tag == "h1": self.h1 += 1

    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False

    def handle_data(self, data):
        if self.in_title: self.title.append(data)

errors = []
for page in PAGES:
    if not page.is_file():
        errors.append(f"fichier absent: {page.name}")
        continue
    text = page.read_text(encoding="utf-8")
    checker = Checker(); checker.feed(text)
    if checker.lang != "fr": errors.append(f"{page.name}: lang doit être fr")
    if not "".join(checker.title).strip(): errors.append(f"{page.name}: title absent")
    if checker.h1 != 1: errors.append(f"{page.name}: exactement un h1 requis")
    if checker.scripts: errors.append(f"{page.name}: script interdit")
    for href in checker.links:
        if href.startswith(("http://", "https://", "#")): continue
        target = (page.parent / href.split("#", 1)[0]).resolve()
        if not target.is_file(): errors.append(f"{page.name}: lien local cassé: {href}")

for path in ROOT.rglob("*"):
    if ".git" in path.parts or not path.is_file(): continue
    if FORBIDDEN_NAMES.search(path.name): errors.append(f"nom de fichier sensible: {path.relative_to(ROOT)}")
    if path.suffix.lower() not in {".html", ".md", ".py", "", ".gitignore"}: continue
    text = path.read_text(encoding="utf-8", errors="replace")
    for label, pattern in SECRET_PATTERNS.items():
        if pattern.search(text): errors.append(f"{path.relative_to(ROOT)}: motif interdit ({label})")

if errors:
    print("ÉCHEC")
    for error in errors: print(f"- {error}")
    sys.exit(1)
print(f"OK — {len(PAGES)} pages HTML, liens locaux valides, aucun script ni motif sensible détecté.")
