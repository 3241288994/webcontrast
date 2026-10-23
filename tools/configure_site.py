#!/usr/bin/env python3
"""Set verified public links. This command does not upload or publish anything."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--github-repo', help='Actual owner/repository, e.g. your-account/webcontrast')
    parser.add_argument('--dataset-url')
    parser.add_argument('--paper-url')
    parser.add_argument('--release-status')
    args = parser.parse_args()
    path = ROOT / 'docs/config.json'
    config = json.loads(path.read_text(encoding='utf-8'))
    if args.github_repo:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+', args.github_repo):
            parser.error('Use an actual owner/repository, without a URL or placeholder brackets.')
        config['github_url'] = 'https://github.com/' + args.github_repo
    for key in ('dataset_url', 'paper_url'):
        value = getattr(args, key)
        if value is not None:
            parsed = urlparse(value)
            if parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password:
                parser.error(key + ' must be an HTTPS public URL without credentials')
            config[key] = value
    if args.release_status:
        config['release_status'] = args.release_status
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Public links updated locally; nothing has been uploaded.')

if __name__ == '__main__':
    main()
