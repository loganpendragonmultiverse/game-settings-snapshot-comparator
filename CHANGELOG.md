# Changelog

## 1.1.2 - 2026-10-19

- Keep supplied text inside Markdown report cells, headings and items; preserve JSON values.

- Protect source files and existing reports; require distinct new destinations and report I/O failures clearly.
- Reject ambiguous flattened JSON paths and duplicate keys; preserve empty-container presence and types, including value-redacted reports.

## 1.1.1 - 2026-10-16

- Correct the completed 1.1.0 release wording and dates; feature behavior is unchanged.

## 1.1.0 - 2026-10-15

- Added opt-in typed value redaction to terminal, Markdown, and JSON reports, with content-free errors for malformed redacted input.

## 1.0.0 - 2026-07-22

- Added JSON, INI/CFG, and key-value parsing.
- Added added, removed, changed, and unchanged classifications.
- Added exact-key exclusions and Markdown and JSON reports.
