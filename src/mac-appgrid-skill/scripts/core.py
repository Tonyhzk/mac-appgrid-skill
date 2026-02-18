"""AppGrid 数据库核心操作模块"""
import sqlite3
import uuid
from pathlib import Path


# 类型常量
TYPE_CONTAINER = 3  # 容器/页面
TYPE_GROUP = 2      # 分组
TYPE_APP = 4        # 应用


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
    """获取分组内部容器的 rowid"""
    row = conn.execute(
        "SELECT rowid FROM items WHERE type=? AND parent_id=?",
        (TYPE_CONTAINER, group_id),
    ).fetchone()
    return row["rowid"] if row else None


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
    """解析移动目标：如果是分组则返回其内部容器 ID，否则原样返回"""
    row = conn.execute("SELECT type FROM items WHERE rowid=?", (target_id,)).fetchone()
    if not row:
        raise ValueError(f"目标 ID {target_id} 不存在")
    if row["type"] == TYPE_GROUP:
        container = get_group_container(conn, target_id)
        if not container:
            raise ValueError(f"分组 {target_id} 缺少内部容器")
        return container
    return target_id
