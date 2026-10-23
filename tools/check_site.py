#!/usr/bin/env python3
"""Check static links, result consistency, and the public package boundary."""
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
PUBLIC_TOP_FILES = {'.gitignore', 'README.md', 'NOTICE.md', 'DATA_RELEASE_CHECKLIST.md', 'package.json'}
PUBLIC_DIRS = {'docs', 'tools', 'tests'}

def public_files():
    result = []
    for path in ROOT.rglob('*'):
        rel = path.relative_to(ROOT)
        if path.is_symlink():
            if rel.parts[0] in PUBLIC_DIRS:
                raise ValueError('No symlinks in the public package: ' + str(rel))
            continue
        if not path.is_file() or '__pycache__' in rel.parts:
            continue
        if (len(rel.parts) == 1 and rel.name in PUBLIC_TOP_FILES) or rel.parts[0] in PUBLIC_DIRS:
            result.append(path)
    return sorted(result)

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.errors = []
        self.csp = False
        self.lang = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.lang = bool(a.get('lang'))
        if 'id' in a:
            if a['id'] in self.ids: self.errors.append('Duplicate id: ' + a['id'])
            self.ids.add(a['id'])
        if tag == 'meta' and a.get('http-equiv', '').lower() == 'content-security-policy': self.csp = True
        if any(k.startswith('on') for k in a): self.errors.append('Inline event handler')
        if tag == 'script' and 'src' not in a: self.errors.append('Inline script')
        if tag == 'img' and 'alt' not in a: self.errors.append('Image without alt text')
        if tag == 'a' and a.get('target') == '_blank' and 'noopener' not in a.get('rel',''):
            self.errors.append('External target without noopener')
        for key in ('href', 'src'):
            if key in a: self.links.append(a[key])

def audit():
    errors = []
    pages = {}
    for path in DOCS.glob('*.html'):
        page = Page(); page.feed(path.read_text(encoding='utf-8')); pages[path.resolve()] = page
        errors.extend(str(path.name) + ': ' + e for e in page.errors)
        if not page.lang or not page.csp: errors.append(path.name + ': missing language or CSP')
    for path, page in pages.items():
        for link in page.links:
            parsed = urlparse(link)
            if parsed.scheme in ('https','http','mailto','data'): continue
            if parsed.scheme: errors.append(path.name + ': unexpected URI scheme'); continue
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not str(target).startswith(str(DOCS.resolve()) + '/'):
                errors.append(path.name + ': link escapes docs directory: ' + link); continue
            if not target.is_file(): errors.append(path.name + ': missing local target: ' + link)
            if parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
                errors.append(path.name + ': missing fragment: ' + link)
    config = json.loads((DOCS/'config.json').read_text(encoding='utf-8'))
    for key in ('github_url','paper_url','dataset_url','contact_url'):
        value = config.get(key, '')
        if value and (urlparse(value).scheme != 'https' or urlparse(value).username):
            errors.append('Unsafe config URL: ' + key)
    results = json.loads((DOCS/'data/results.json').read_text(encoding='utf-8'))
    if len(results['external']) != 14 or len(results['repair']) != 4: errors.append('Unexpected model count')
    if (results['pages'],results['websites']) != (500,130): errors.append('Stale benchmark size')
    for row in results['external'] + results['repair']:
        m = row['metrics']
        if abs(m['with']['mean'] - m['without']['mean'] - m['effect']['mean']) > 1e-8:
            errors.append('Incorrect rationale-effect arithmetic: ' + row['id'])
    secret = re.compile(r'(?:sk-[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{24,}|hf_[A-Za-z0-9]{24,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)')
    private_path = re.compile(r'/(?:mnt|home|Users)/[A-Za-z0-9]')
    for path in public_files():
        rel = str(path.relative_to(ROOT))
        if path.suffix.lower() in ('.pdf','.zip','.gz','.pem','.key','.jsonl'):
            errors.append('Unexpected asset type: ' + rel)
        text = path.read_text(encoding='utf-8')
        if secret.search(text): errors.append('Potential credential in ' + rel)
        if private_path.search(text): errors.append('Local machine path in ' + rel)
    return errors

if __name__ == '__main__':
    failures = audit()
    print(json.dumps(dict(status='PASS' if not failures else 'FAIL', public_files=len(public_files()), errors=failures), indent=2))
    sys.exit(bool(failures))
