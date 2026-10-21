---
name: wp-performance-review
description: WordPress performance code review for Codex. Use when reviewing themes, plugins, or custom WordPress code for query bloat, cache misses, slow hooks, cron issues, asset-loading waste, polling, or pre-launch scalability risks.
---

# Codex WordPress Performance Review

## Purpose

Use this skill when Codex needs to review WordPress code for performance problems and produce actionable findings with file references, severity, and specific remediation guidance.

## Focus Areas

- Unbounded or inefficient `WP_Query` usage
- Expensive hooks, page-load writes, and cache bypass
- AJAX polling, blocking HTTP calls, and asset overloading
- Transients, object cache, and cron misuse
- Template-level N+1 patterns and repeated expensive lookups

## Workflow

1. Identify the WordPress context: plugin, theme, WooCommerce extension, or mixed codebase.
2. Scan for critical issues first: unbounded queries, `query_posts()`, `session_start()`, frontend polling, and repeated writes on page load.
3. Review likely hotspots in PHP, templates, JavaScript, and asset registration.
4. Use the reference docs below for deeper guidance only where needed.
5. Report findings grouped by severity with file paths, line references, impact, and the recommended fix.

## Reference Files

Load only the references you need from:

- `../../claude-skills/wp-performance-review/references/anti-patterns.md`
- `../../claude-skills/wp-performance-review/references/wp-query-guide.md`
- `../../claude-skills/wp-performance-review/references/caching-guide.md`
- `../../claude-skills/wp-performance-review/references/measurement-guide.md`

## Output

- Group findings by `CRITICAL`, `WARNING`, and `INFO`
- Include concrete file references
- Explain why the pattern is a problem in WordPress terms
- Suggest the smallest practical fix

