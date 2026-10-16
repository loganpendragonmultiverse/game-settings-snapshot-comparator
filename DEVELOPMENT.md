# Development record

Version 1.0.0 implements the complete initial scope: deterministic comparison of common text settings formats with typed JSON values, explicit differences, and no mutation. Proprietary binary decoding and advice about ideal settings are excluded.

## 1.1.0 - 2026-10-15

Use `game-settings-compare before.json after.json --redact-values --json changes.json --markdown changes.md` to retain setting keys, value types, added/removed/changed classifications, and counts while omitting values. JSON primitive types appear as `[redacted:string]`, `[redacted:number]`, `[redacted:boolean]`, or `[redacted:null]`; INI/CFG and key-value entries are strings. Comparison happens before redaction, so two different secrets still count as changed. Invalid or unreadable redacted inputs produce a generic error without input contents.

Redaction is opt-in; default output continues to include values. **Setting names and input/output paths remain visible** and can themselves contain sensitive information. Redaction does not anonymize names or paths. No files are uploaded or modified.

Changes require independent review before merge or release.
