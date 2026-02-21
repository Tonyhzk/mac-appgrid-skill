# AppGrid 数据库 Schema

## 表结构

### items（核心树形结构）
| 字段 | 类型 | 说明 |
|------|------|------|
| rowid | INTEGER PRIMARY KEY | 项目 ID |
| uuid | VARCHAR | 唯一标识符 |
| flags | INTEGER | 标志位 |
| type | INTEGER | 类型：2=分组, 3=容器/页面, 4=应用 |
| parent_id | INTEGER NOT NULL | 父项 ID |
| ordering | INTEGER | 排序序号 |

### apps（应用详情）
| 字段 | 类型 | 说明 |
|------|------|------|
| item_id | INTEGER PRIMARY KEY | 关联 items.rowid |
| title | VARCHAR | 应用名称 |
| bundleid | VARCHAR | Bundle ID |
| storeid | VARCHAR | App Store ID |
| category_id | INTEGER | 分类 ID |
| moddate | REAL | 修改日期 |
| bookmark | BLOB | 书签数据 |
| custom_path | VARCHAR | 自定义路径 |

### groups（分组详情）
| 字段 | 类型 | 说明 |
|------|------|------|
| item_id | INTEGER PRIMARY KEY | 关联 items.rowid |
| category_id | INTEGER | 分类 ID |
| title | VARCHAR | 分组名称 |

### 其他表
- **categories**: rowid, uti
- **image_cache**: item_id, uuid, size_big, size_mini, image_data, image_data_mini
- **custom_icons**: app_path (PK), icon_data, icon_data_mini
- **app_sources**: rowid, uuid, flags, bookmark, last_fsevent_id, fsevent_uuid
- **dbinfo**: key, value
- **downloading_apps**: item_id, title, bundleid, storeid, category_id, install_path

## 树形层级

```
根 (virtual, id=0)
└── 网格 (id=1, type=3, parent_id=0)
    ├── 页面1 (type=3, parent_id=1, ordering=0)
    │   ├── 应用A (type=4, parent_id=页面1)
    │   ├── 分组X (type=2, parent_id=页面1)
    │   │   ├── 分页1 (type=3, parent_id=分组X, ordering=0)
    │   │   │   ├── 应用B (type=4)
    │   │   │   └── 应用C (type=4)  ← 最多35个
    │   │   └── 分页2 (type=3, parent_id=分组X, ordering=1)
    │   │       └── 应用D (type=4)  ← 溢出到第二页
    │   └── 应用E (type=4, parent_id=页面1)
    └── 页面2 (type=3, parent_id=1, ordering=1)
        └── ...
```

**分组内分页机制**：一个分组(type=2)下可以有多个容器(type=3)作为分页，每页最多35个子项。当第一页满时，自动创建新分页容纳更多应用。

## 索引
- `items_uuid_index` ON items(uuid)
- `items_ordering_index` ON items(parent_id, ordering)
- `items_type` ON items(type)
- `image_cache_index` ON image_cache(item_id)

## 创建分组的数据操作

1. 在 items 插入分组记录 (type=2, parent_id=页面ID)
2. 在 groups 插入分组名称
3. 在 items 插入分组内部容器 (type=3, parent_id=分组ID, ordering=0)
