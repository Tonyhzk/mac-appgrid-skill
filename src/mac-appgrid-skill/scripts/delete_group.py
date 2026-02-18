"""删除 AppGrid 分组，将组内应用移回父页面"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import (
    connect, get_group_container, get_next_ordering, reorder_children,
    TYPE_GROUP, TYPE_APP,
)


def main():
    parser = argparse.ArgumentParser(description="删除 AppGrid 分组")
    parser.add_argument("--db", required=True, help=".agrid 数据库路径")
    parser.add_argument("--group", required=True, type=int, help="分组 ID")
    args = parser.parse_args()

    conn = connect(args.db)

    # 验证分组存在
    group = conn.execute(
        "SELECT i.rowid, i.parent_id, g.title FROM items i JOIN groups g ON i.rowid = g.item_id WHERE i.rowid=? AND i.type=?",
        (args.group, TYPE_GROUP),
    ).fetchone()
    if not group:
        print(f"错误: 分组 {args.group} 不存在", file=sys.stderr)
        sys.exit(1)

    page_id = group["parent_id"]
    container_id = get_group_container(conn, args.group)

    # 将组内应用移回父页面
    moved = 0
    if container_id:
        apps = conn.execute(
            "SELECT rowid FROM items WHERE parent_id=? AND type=? ORDER BY ordering",
            (container_id, TYPE_APP),
        ).fetchall()
        next_ord = get_next_ordering(conn, page_id)
        for app in apps:
            conn.execute(
                "UPDATE items SET parent_id=?, ordering=? WHERE rowid=?",
                (page_id, next_ord, app["rowid"]),
            )
            next_ord += 1
            moved += 1

        # 删除容器
        conn.execute("DELETE FROM items WHERE rowid=?", (container_id,))

    # 删除分组记录
    conn.execute("DELETE FROM groups WHERE item_id=?", (args.group,))
    conn.execute("DELETE FROM items WHERE rowid=?", (args.group,))

    # 重新整理父页面排序
    reorder_children(conn, page_id)

    conn.commit()
    conn.close()

    print(f"✓ 分组 '{group['title']}' 已删除，{moved} 个应用已移回页面")


if __name__ == "__main__":
    main()
