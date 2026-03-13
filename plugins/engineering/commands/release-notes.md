---
description: "Generate release notes from git log or PR list"
argument-hint: "[--from <tag>] [--to <tag>] [--format markdown|slack|email]"
---

# Release Notes

Generate professional release notes from git history or PR list. Categorizes changes, writes human-readable summaries, and formats for the target audience.

## Pre-flight Checks
1. Determine range: if `--from` and `--to` provided, use git log between tags; otherwise use last tag to HEAD
2. Determine output format from `--format` flag (default: markdown)
3. Check for CHANGELOG.md to understand existing format conventions

## Phase 1: Collect Changes
```bash
git log --oneline <from>..<to>
# or if no tags:
git log --oneline $(git describe --tags --abbrev=0)..HEAD
```

Pull PR titles if GitHub MCP is available:
- Group by labels: `feature`, `bug`, `security`, `breaking-change`, `chore`

## Phase 2: Categorize
Sort commits/PRs into categories:
- 🚀 **New Features** — user-facing functionality additions
- 🐛 **Bug Fixes** — resolved issues
- 🔒 **Security** — vulnerability patches, auth changes
- ⚠️ **Breaking Changes** — API changes, removed features, migration required
- ⚡ **Performance** — speed/memory improvements
- 🔧 **Internal** — refactors, dependency updates, CI changes (often omitted from user-facing notes)

Discard: merge commits, trivial chore commits, typo fixes

## Phase 3: Write Release Notes
For each change:
- Rewrite git commit messages into human-readable sentences
- Lead with the benefit, not the implementation: "Users can now export reports as PDF" not "Added PDF export handler"
- For breaking changes: include migration steps

## Phase 4: Format Output

### Markdown (default)
```markdown
# v2.4.0 — 2026-03-13

## 🚀 New Features
- Export reports as PDF and CSV from the dashboard (#234)
- Added dark mode support across all pages (#198)

## 🐛 Bug Fixes
- Fixed session timeout not refreshing on activity (#241)

## ⚠️ Breaking Changes
- `getUserById()` now returns `null` instead of throwing on missing user.
  Migration: replace `try/catch` with null check.

## 🔒 Security
- Updated dependencies to patch CVE-2026-1234 in `axios`
```

### Slack format
```
*v2.4.0 released* 🎉
• Export reports as PDF/CSV
• Dark mode support
• Fixed session timeout bug
Full notes: <link>
```

## Output Format
- Print to console in requested format
- Optionally save to `CHANGELOG.md` (append at top)

## Error Handling
- No tags found: use first commit to HEAD
- Ambiguous commit messages: group under "Other Changes" and flag for manual review
- No commits in range: output "No changes since last release"
