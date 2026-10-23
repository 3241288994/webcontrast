# WebContrast project website

A lightweight static website for **WebContrast**, a 500-page diagnostic benchmark
for goal-directed action judgment and explanation robustness.

- Website: https://3241288994.github.io/webcontrast/
- Website repository: https://github.com/3241288994/webcontrast

GitHub Pages publishes the `main` branch's `docs/` directory.

## What is available here

- A project homepage with an interactive, original illustration.
- An explorer for three fictional design examples or a user-selected local dataset.
- Frozen result tables: 14 external configurations and four reconstruction-training
  conditions, grouped by scoring interface.
- Data access, metric definitions, provenance, and release-status documentation.
- Small, portable tools for annotation-layer export and hash-checked local assembly.

**This is the website release, not the complete research-code or dataset release.**
It contains no manuscript PDF, raw upstream pages, original screenshots, model
weights, credentials, or full benchmark annotation file. The paper will be linked
after it is posted to arXiv. The original experimental code package is unchanged.

## Preview

From this directory, using Python 3.8 or later:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Open `http://localhost:8000`. On Windows, `python` may replace `python3`.
Use a local HTTP server rather than double-clicking HTML files: the viewer loads
its bundled JSON through relative URLs. No frontend build or npm install is needed.

## Checks

```bash
python3 tools/check_site.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/data.test.js
```

Node 22 or later is used only for the JavaScript tests, not for serving the site.
These checks do not replace browser verification on desktop and mobile.

## GitHub Pages

1. Create a clean repository such as `your-account/webcontrast`.
2. Set the actual repository link:

   ```bash
   python3 tools/configure_site.py --github-repo your-account/webcontrast
   ```

3. Commit this package, not the surrounding research workspace.
4. In **Settings → Pages**, choose **Deploy from a branch**, branch **main**, folder
   **/docs**, and save.
5. Verify the resulting project URL and all four pages.

All internal asset and navigation URLs are relative, so the site works at both
the root and a project subpath. No custom domain, backend, billing account, secret,
or GitHub Actions workflow is required. Never put local benchmark records inside
`docs/`: everything in that folder is intended to be publicly served.

Official setup guide:
https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

## Update public links later

Only set verified URLs, never invented paper IDs or guessed author names.

```bash
python3 tools/configure_site.py --paper-url https://arxiv.org/abs/ACTUAL_ID
python3 tools/configure_site.py --dataset-url https://huggingface.co/datasets/ACTUAL_OWNER/ACTUAL_DATASET
```

The strings above are examples to replace, not existing release links. After a data
or code release, also revise the availability list and relevant text in
`docs/guide.html`; changing a button alone is not enough.

## Results provenance

`docs/data/results.json` is exported from the audited frozen 500-page CSVs. Its
metadata records the input hashes, data freeze, denominators, and interface notes.
Do not edit numerical cells by hand. To regenerate it from those original exports:

```bash
python3 tools/export_results.py --external external_panel_audited.csv --repair paper_main_selftrained500.csv --out docs/data/results.json
```

The external panel does not isolate a causal effect of one training dataset.
Interfaces differ across groups. The two Llama/AgentRM reference rows are not a
matched-interface base/release comparison.

## Local data tools

`export_annotations.py` removes page observations and internal metadata through an
explicit field allowlist. It creates a **release candidate**, not a legal clearance.
`assemble_local.py` combines those annotations with exact local observation text
and refuses every hash mismatch. It is a final join step, **not a complete
Mind2Web-to-WebContrast preprocessing pipeline**. The public raw-source pipeline
must still be ported and checked for all 500 records before the data release.

The browser displays all supplied page HTML as plain text. It never renders it as
live HTML. Files are read in browser memory, not submitted to an upload endpoint.
No analytics, third-party scripts, external fonts, or inference APIs are included.
The hosting provider can still keep ordinary website request logs.

## Package

```bash
python3 tools/package_site.py --out output/webcontrast-website.zip
```

The packager uses an allowlist. `private/`, `output/`, full JSONL data, and manuscript
PDFs are never included. Review `NOTICE.md` and `DATA_RELEASE_CHECKLIST.md` before
publishing additional research resources.
