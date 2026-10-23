#!/usr/bin/env python3
"""Join annotations to exact locally prepared observations, checking every hash.

This is the final assembly step, NOT a Mind2Web raw-HTML preprocessing pipeline.
The observations file must contain id and observation fields for the exact frozen
representations. Never replace these with a different HTML representation.
"""
import argparse
import json
from pathlib import Path
from annotation_io import assemble, read_rows, write_rows

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--annotations', type=Path, required=True)
    parser.add_argument('--observations', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    rows = assemble(read_rows(args.annotations), read_rows(args.observations))
    write_rows(args.out, rows)
    print(json.dumps(dict(status='hashes_verified', pages=len(rows))))

if __name__ == '__main__':
    main()
