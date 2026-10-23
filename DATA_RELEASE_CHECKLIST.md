# Separate website launch from dataset release

The website can launch with fictional illustrations and frozen aggregate results.
Do not turn on a full-data download link until the following work is complete.

## Data publication

- [ ] Confirm the publication scope and applicable license for the added annotations.
- [ ] Review short source-derived text in goals and explanations as well as raw HTML.
- [ ] Retain Mind2Web attribution and explicitly discuss its test-contamination request.
- [ ] Port the exact raw-source-to-simplified-observation reconstruction for all 500 pages.
- [ ] Verify each reconstructed observation hash, label, action binding, and rationale slot.
- [ ] Preserve the original version and release change notes rather than silently changing tests.
- [ ] Provide a data card documenting development use, core/hard composition, and review scope.
- [ ] Choose an annotation license, independently from the code/website license.
- [ ] Publish one fixed archive with checksums and mirror the identical version to Hugging Face.

## Research code

- [ ] Port the latest 500-page data schema to the public evaluation entrypoints.
- [ ] Document model-specific scoring interfaces and complete denominator handling.
- [ ] Run the public-code preflight against the frozen prediction/result receipts.
- [ ] Remove local paths, account details, and credentials from code and configs.
- [ ] Select a code license and preserve dependency notices where applicable.

The included `assemble_local.py` only performs the final hash-checked join. It
does not claim to regenerate simplified observations from upstream raw HTML.
The website correctly marks these resources as preparing until verified.
