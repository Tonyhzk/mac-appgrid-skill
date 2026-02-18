# Changelog

All notable changes to this project will be documented in this file.

**English** | [中文](CHANGELOG_CN.md)

---

## [1.0.1] - 2026-02-18

### Added
- Container capacity limit check: max 35 items per container (page or group, 7×5 grid)
- `core.py`: added `MAX_ITEMS_PER_CONTAINER` constant, `count_children()` and `check_capacity()` functions
- `move_app.py`, `move_group.py`, `create_group.py` now validate target capacity before execution
- `SKILL.md`: added capacity limit documentation section

---

## [1.0.0] - 2025-02-18

### Added
- Initial release
- List tree structure of pages, groups, and apps
- Search apps by name or bundle ID
- Create, rename, delete, and move groups
- Move apps between pages and groups
- Export app list to CSV or JSON
- Statistics overview
- Check ungrouped apps
- Database integrity check