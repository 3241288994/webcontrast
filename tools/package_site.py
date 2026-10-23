#!/usr/bin/env python3
"""Package only the allowlisted website sources. Never packages private/ or output/."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from check_site import ROOT, audit, public_files

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    failures = audit()
    if failures:
        raise SystemExit('\n'.join(failures))
    paths = public_files()
    manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in paths: archive.write(path, 'webcontrast/' + str(path.relative_to(ROOT)))
        archive.writestr('webcontrast/FILE_MANIFEST.json', json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(dict(status='ok', files=len(paths)+1, bytes=args.out.stat().st_size,
                         sha256=hashlib.sha256(args.out.read_bytes()).hexdigest())))

if __name__ == '__main__':
    main()
