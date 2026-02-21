# Changelog

All notable changes to this project will be documented in this file.

**English** | [中文](CHANGELOG_CN.md)

---

## [1.1.0] - 2026-02-21

### Added
- Group pagination support: groups can now contain multiple pages (type=3 containers), each holding up to 35 apps
- `core.py`: added `get_group_containers()` and `find_available_container()` functions
- `resolve_target()` now auto-selects an available page or creates a new one when all pages are full
- `list_tree.py`: displays sub-pages within groups when multiple pages exist
- `stats.py`: shows page count for multi-page groups
- `check_integrity.py`: detects empty sub-pages within groups

### Changed
- `delete_group.py`: handles all sub-pages when deleting a group
- `export.py`: collects apps from all sub-pages within a group

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