# add9.com

Bilingual (English / Simplified Chinese) static SEO site, playable genre chord guides, and privacy policy for **add9**, published via GitHub Pages (`https://github.com/jarvisrr/add9.com`).

## Build & Data Source

- Run `python3 scripts/build_site.py` (or `--base-url https://add9.com` when switching to a custom domain) to regenerate all 28 HTML pages, `sitemap.xml`, and `robots.txt` from `../alternative-chord/Packages/ChordKit/Sources/ChordKit/Resources/chord-atlas.json` and `../alternative-chord/AlternativeChord/Resources/Localizable.xcstrings`.
- Do **not** modify `README.md` or `privacy-zh.md` unless explicitly requested; they back existing App Store privacy URLs.

## Web & Design Skills

- **fe-modern-web-guidance** — Check before modifying HTML, CSS, accessibility, performance, or client-side JS: `/Users/jarvisren/Master/Skills/plugins/indie-eng/collected/fe-modern-web-guidance/SKILL.md` (linked via `.agents/skills/fe-modern-web-guidance` and `.claude/skills/fe-modern-web-guidance`).
- Keep zero external blocking fonts/CDNs and pure static pre-rendered HTML for fast mainland China access and Baidu/Google/Bing crawlability.
- Localization: Shoegaze 一律译为「盯鞋」；Bossa nova 一律保留英文原名。

## Team workflow

Team workflow (multi-agent tasks in T3 Code): read and follow /Users/jarvisren/Master/TEAM.md
