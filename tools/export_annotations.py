#!/usr/bin/env python3
"""Create a local annotation-only release candidate. Does not grant publication rights."""
import argparse
import json
from pathlib import Path
from annotation_io import annotation, read_rows, write_rows

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    rows = read_rows(args.input)
    if len(rows) != 500 or len({r['id'] for r in rows}) != 500 or len({r['website'] for r in rows}) != 130:
        raise ValueError('Expected the frozen 500-page, 130-website dataset')
    result = [annotation(row, index) for index, row in enumerate(rows)]
    write_rows(args.out, result)
    print(json.dumps(dict(status='candidate_only', records=len(result),
                         observations_included=False, raw_html_included=False,
                         message='Review permissions, annotation excerpts, and reconstruction before public data release.')))

if __name__ == '__main__':
    main()
