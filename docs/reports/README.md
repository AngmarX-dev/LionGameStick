# Development Reports

| Report | Branch | Objective |
|---|---|---|
| [001-binary-recovery-audit.md](001-binary-recovery-audit.md) | `recovery/01-git-history-archive` | Recover the exact original 7-Zip archive from Git history and audit historical binary coverage |
| [002-verified-extraction.md](002-verified-extraction.md) | `recovery/02-verified-extraction` | Add a non-destructive, integrity-checked extraction path for the recovered archive |

## History

- 2026-11-09: Audited the current `main` tree and the historical archive/extraction commits. Confirmed that all 1,330 files under the historical `extracted/GameStickLite/` tree already exist at the repository root with identical Git blob SHA values. The missing historical artifact is the original 7-Zip archive, not the extracted binary filesystem.
