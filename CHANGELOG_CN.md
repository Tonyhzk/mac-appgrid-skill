# 更新日志

本项目的所有重要更改都将记录在此文件中。

[English](CHANGELOG.md) | **中文**

---

## [1.1.0] - 2026-02-21

### 新增
- 分组内分页支持：分组可包含多个分页（type=3 容器），每页最多容纳 35 个应用
- `core.py` 新增 `get_group_containers()` 和 `find_available_container()` 函数
- `resolve_target()` 自动选择有空位的分页，所有分页满时自动创建新分页
- `list_tree.py` 多分页分组显示子分页结构
- `stats.py` 多分页分组显示页数
- `check_integrity.py` 检测分组内的空分页

### 变更
- `delete_group.py` 删除分组时处理所有分页内的应用
- `export.py` 导出时收集分组所有分页的应用

---

## [1.0.1] - 2026-02-18

### 新增
- 容器容量限制检查：单个容器（页面或分组）最多容纳35个子项（7×5网格）
- `core.py` 新增 `MAX_ITEMS_PER_CONTAINER` 常量、`count_children()` 和 `check_capacity()` 函数
- `move_app.py`、`move_group.py`、`create_group.py` 在执行前自动检查目标容量
- `SKILL.md` 新增容量限制说明章节

---

## [1.0.0] - 2025-02-18

### 新增
- 初始版本发布
- 列出页面、分组、应用的树形结构
- 按名称或 Bundle ID 搜索应用
- 创建、重命名、删除、移动分组
- 在页面和分组间移动应用
- 导出应用列表为 CSV 或 JSON
- 统计概览
- 检查未归组应用
- 数据库一致性检查