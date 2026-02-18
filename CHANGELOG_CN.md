# 更新日志

本项目的所有重要更改都将记录在此文件中。

[English](CHANGELOG.md) | **中文**

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