# Release validation — v1.0.0

Checked locally on 2026-10-18, macOS, against the public package.

| Check | Observed result |
| --- | --- |
| Python regression suite | 184 tests passed |
| Fresh installation and existing-directory protection | Covered by three installation tests |
| Skill frontmatter | Checked with the local skill validator |
| Relative Markdown file links | Checked against repository files |
| Public package text and DOCX XML | Scanned for local paths, client names and credential-like content |
| GitHub Actions | Linux / Python 3.10 and 3.12 both passed: [run 39135292064](https://github.com/ccygod/lecture/actions/runs/39135292064) |

## Lecture-specific evidence

The existing 181 tests pass, plus 3 installation tests. The arithmetic example reports ratio 1.5 and relative change 50%. The before/after is an original editorial illustration, not a controlled generation benchmark. No live audience study, real rehearsal or full generated presentation is claimed.
