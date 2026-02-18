---
name: program-appgrid
version: 1.0.0
description: macOS AppGrid 网格布局管理。当用户需要查看、编辑、整理 AppGrid 应用布局、管理分组、移动应用、导出应用列表时使用。关键词：AppGrid、应用网格、分组管理、应用布局、agrid。
---

# AppGrid 网格布局管理

管理 macOS AppGrid 的 `.agrid` 数据库文件（SQLite），提供基础 CRUD 操作。

## 数据库路径

用户需提供 `.agrid` 文件路径。默认参考路径：
`~/Documents/GitHub/HZK-Script/程序-Mac-Appgrid数据库编辑/grid/MyGrid.agrid`

## 数据库结构概要

详细 schema 见 `%当前SKILL文件父目录%/references/db-schema.md`

核心树形层级：根(0) → 网格(1) → 页面(type=3) → 应用(type=4) / 分组(type=2) → 分组容器(type=3) → 应用(type=4)

- `type=3`：容器/页面
- `type=2`：分组（文件夹）
- `type=4`：应用

## 可用操作

所有脚本通过 `--db <path>` 指定数据库路径。

### 1. 列出树形结构

```bash
python3 %当前SKILL文件父目录%/scripts/list_tree.py --db <path> [--page <page_id>] [--format tree|json]
```

### 2. 搜索应用

```bash
python3 %当前SKILL文件父目录%/scripts/search.py --db <path> --query <text> [--field name|bundleid|all]
```

### 3. 创建分组

```bash
python3 %当前SKILL文件父目录%/scripts/create_group.py --db <path> --page <page_id> --name <name> [--position <int>]
```

### 4. 删除分组

删除分组，将组内应用移回父页面。

```bash
python3 %当前SKILL文件父目录%/scripts/delete_group.py --db <path> --group <group_id>
```

### 5. 重命名分组

```bash
python3 %当前SKILL文件父目录%/scripts/rename_group.py --db <path> --group <group_id> --name <new_name>
```

### 6. 移动应用

将应用移动到指定页面或分组。`--to` 接受页面 ID 或分组 ID。

```bash
python3 %当前SKILL文件父目录%/scripts/move_app.py --db <path> --app <app_id> --to <target_id> [--position <int>]
```

### 7. 移动分组

将分组移动到另一个页面。

```bash
python3 %当前SKILL文件父目录%/scripts/move_group.py --db <path> --group <group_id> --to-page <page_id> [--position <int>]
```

### 8. 导出应用列表

```bash
python3 %当前SKILL文件父目录%/scripts/export.py --db <path> [--format csv|json] [--output <path>]
```

### 9. 数据库统计概览

显示总应用数、分组数、各分组应用数量等。

```bash
python3 %当前SKILL文件父目录%/scripts/stats.py --db <path> [--format table|json]
```

### 10. 检查未归组应用

列出所有不在任何分组内的散落应用。

```bash
python3 %当前SKILL文件父目录%/scripts/check_ungrouped.py --db <path> [--format table|json]
```

### 11. 数据库一致性检查

检测孤立记录、空分组、空页面、bookmark 缺失等问题。

```bash
python3 %当前SKILL文件父目录%/scripts/check_integrity.py --db <path>
```

## 操作注意事项

- 修改数据库前建议备份 `.agrid` 文件
- 分组的 `--to` 参数：传入分组 ID 时自动定位到其内部容器
- `--position` 省略时追加到末尾