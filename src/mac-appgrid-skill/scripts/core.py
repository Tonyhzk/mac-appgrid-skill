"""AppGrid 数据库核心操作模块"""
import sqlite3
import uuid
from pathlib import Path


# 类型常量
TYPE_CONTAINER = 3  # 容器/页面
TYPE_GROUP = 2      # 分组
TYPE_APP = 4        # 应用

# 容量限制：AppGrid 单个容器（页面或分组）最多容纳的子项数（7列 × 5行）
MAX_ITEMS_PER_CONTAINER = 35


def connect(db_path: str) -> sqlite3.Connection:
    """连接数据库，返回 Connection"""
    p = Path(db_path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"数据库文件不存在: {p}")
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    return conn


def get_pages(conn: sqlite3.Connection) -> list[dict]:
    """获取所有页面（网格下的 type=3 容器）"""
    # 网格节点: type=3, parent_id=0 的子节点中 type=3
    grid = conn.execute(
        "SELECT rowid FROM items WHERE type=? AND parent_id=0", (TYPE_CONTAINER,)
    ).fetchone()
    if not grid:
        return []
    rows = conn.execute(
        "SELECT rowid, ordering FROM items WHERE type=? AND parent_id=? ORDER BY ordering",
        (TYPE_CONTAINER, grid["rowid"]),
    ).fetchall()
    return [dict(r) for r in rows]


def get_children(conn: sqlite3.Connection, parent_id: int) -> list[dict]:
    """获取指定父节点下的所有子项，附带 app/group 详情"""
    rows = conn.execute(
        """SELECT i.rowid, i.type, i.parent_id, i.ordering,
                  a.title AS app_title, a.bundleid, a.custom_path,
                  g.title AS group_title
           FROM items i
           LEFT JOIN apps a ON i.rowid = a.item_id
           LEFT JOIN groups g ON i.rowid = g.item_id
           WHERE i.parent_id = ?
           ORDER BY i.ordering""",
        (parent_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_group_container(conn: sqlite3.Connection, group_id: int) -> int | None:
    """获取分组第一个内部容器的 rowid（向后兼容）"""
    row = conn.execute(
        "SELECT rowid FROM items WHERE type=? AND parent_id=? ORDER BY ordering",
        (TYPE_CONTAINER, group_id),
    ).fetchone()
    return row["rowid"] if row else None


def get_group_containers(conn: sqlite3.Connection, group_id: int) -> list[int]:
    """获取分组所有内部容器（分页）的 rowid 列表，按 ordering 排序"""
    rows = conn.execute(
        "SELECT rowid FROM items WHERE type=? AND parent_id=? ORDER BY ordering",
        (TYPE_CONTAINER, group_id),
    ).fetchall()
    return [r["rowid"] for r in rows]


def find_available_container(conn: sqlite3.Connection, group_id: int, auto_create: bool = True) -> int:
    """在分组中找到有空位的容器，如果都满了且 auto_create=True 则自动创建新分页"""
    containers = get_group_containers(conn, group_id)
    if not containers:
        raise ValueError(f"分组 {group_id} 缺少内部容器")
    for cid in containers:
        if count_children(conn, cid) < MAX_ITEMS_PER_CONTAINER:
            return cid
    if not auto_create:
        raise ValueError(f"分组 {group_id} 所有分页已满（共 {len(containers)} 页）")
    # 自动创建新分页
    next_ord = get_next_ordering(conn, group_id)
    new_container = insert_item(conn, TYPE_CONTAINER, group_id, next_ord)
    return new_container


def get_next_ordering(conn: sqlite3.Connection, parent_id: int) -> int:
    """获取指定父节点下的下一个排序序号"""
    row = conn.execute(
        "SELECT MAX(ordering) AS max_ord FROM items WHERE parent_id=?", (parent_id,)
    ).fetchone()
    return (row["max_ord"] or -1) + 1


def insert_item(conn: sqlite3.Connection, type_: int, parent_id: int, ordering: int) -> int:
    """插入 items 记录，返回 rowid"""
    uid = str(uuid.uuid4()).upper()
    cur = conn.execute(
        "INSERT INTO items (uuid, flags, type, parent_id, ordering) VALUES (?, 0, ?, ?, ?)",
        (uid, type_, parent_id, ordering),
    )
    return cur.lastrowid


def shift_ordering(conn: sqlite3.Connection, parent_id: int, from_pos: int, delta: int = 1):
    """将 parent_id 下 ordering >= from_pos 的项目序号偏移 delta"""
    conn.execute(
        "UPDATE items SET ordering = ordering + ? WHERE parent_id = ? AND ordering >= ?",
        (delta, parent_id, from_pos),
    )


def reorder_children(conn: sqlite3.Connection, parent_id: int):
    """重新整理子项的 ordering，从 0 开始连续编号"""
    rows = conn.execute(
        "SELECT rowid FROM items WHERE parent_id=? ORDER BY ordering", (parent_id,)
    ).fetchall()
    for i, row in enumerate(rows):
        conn.execute("UPDATE items SET ordering=? WHERE rowid=?", (i, row["rowid"]))


def resolve_target(conn: sqlite3.Connection, target_id: int) -> int:
    """解析移动目标：如果是分组则返回有空位的容器 ID（满了自动新建分页），否则原样返回"""
    row = conn.execute("SELECT type FROM items WHERE rowid=?", (target_id,)).fetchone()
    if not row:
        raise ValueError(f"目标 ID {target_id} 不存在")
    if row["type"] == TYPE_GROUP:
        return find_available_container(conn, target_id)
    return target_id


def count_children(conn: sqlite3.Connection, parent_id: int) -> int:
    """统计指定父节点下的子项数量"""
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM items WHERE parent_id=?", (parent_id,)
    ).fetchone()
    return row["cnt"]


def check_capacity(conn: sqlite3.Connection, parent_id: int, adding: int = 1):
    """检查容器是否有足够空间，超限则抛出 ValueError"""
    current = count_children(conn, parent_id)
    if current + adding > MAX_ITEMS_PER_CONTAINER:
        raise ValueError(
            f"容器 {parent_id} 已有 {current} 个子项，添加 {adding} 个后将超出上限 {MAX_ITEMS_PER_CONTAINER}"
        )
