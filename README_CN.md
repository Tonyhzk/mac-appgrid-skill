# mac-appgrid-skill

![mac-appgrid-skill banner](./assets/banner_cn.svg)

用于管理 macOS AppGrid 网格布局数据库的 Claude Code 技能。

[English](README.md) | **中文** | [更新日志](CHANGELOG_CN.md)

---

## 功能特性

![核心功能](./assets/features_cn.svg)

### 核心功能
- **列出结构** - 显示页面、分组、应用的树形结构
- **搜索应用** - 按名称或 Bundle ID 查找应用
- **分组管理** - 创建、重命名、删除、移动分组
- **移动应用** - 在页面和分组间移动应用
- **导出数据** - 将应用列表导出为 CSV 或 JSON

### 诊断工具
- **统计概览** - 显示应用总数、分组数及各分组应用数量
- **检查未归组** - 列出所有不在任何分组内的散落应用
- **一致性检查** - 检测孤立记录、空分组、缺失 bookmark 等问题

---

## 系统要求

| 平台 | 最低版本 |
|------|---------|
| macOS | 10.15+ |
| Python | 3.8+ |
| Claude Code | 最新版 |

---

## 安装

### 从 Releases 下载

从 [Releases](https://github.com/Tonyhzk/mac-appgrid-skill/releases) 下载最新版本。

### 手动安装

```bash
cd ~/.claude/skills/
git clone https://github.com/Tonyhzk/mac-appgrid-skill.git program-appgrid
```

---

## 快速开始

```bash
# 列出所有应用的树形结构
python3 ~/.claude/skills/program-appgrid/scripts/list_tree.py --db ~/path/to/MyGrid.agrid

# 检查未归组的应用
python3 ~/.claude/skills/program-appgrid/scripts/check_ungrouped.py --db ~/path/to/MyGrid.agrid

# 创建新分组
python3 ~/.claude/skills/program-appgrid/scripts/create_group.py --db ~/path/to/MyGrid.agrid --page 2 --name "视频编辑"
```

---

## 配置说明

无需配置文件。使用 `--db` 参数指定 `.agrid` 数据库路径即可。

---

## 项目结构

```
program-appgrid/
├── SKILL.md              # 技能定义文件
├── scripts/              # Python 脚本
│   ├── core.py           # 共享数据库操作
│   ├── list_tree.py      # 列出树形结构
│   ├── search.py         # 搜索应用
│   ├── create_group.py   # 创建分组
│   ├── delete_group.py   # 删除分组
│   ├── rename_group.py   # 重命名分组
│   ├── move_app.py       # 移动应用
│   ├── move_group.py     # 移动分组
│   ├── export.py         # 导出数据
│   ├── stats.py          # 统计概览
│   ├── check_ungrouped.py # 检查未归组应用
│   └── check_integrity.py # 一致性检查
└── references/
    └── db-schema.md      # 数据库结构参考
```

---

## 致谢

为 [AppGrid](https://zekalogic.com/appgrid/) 用户提供可编程管理其应用网格的工具。

---

## 许可证

[Apache License 2.0](LICENSE)

---

## 作者

[Tonyhzk](https://github.com/Tonyhzk)