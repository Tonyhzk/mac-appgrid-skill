"""移动 AppGrid 分组到另一个页面"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import (
    connect, shift_ordering, get_next_ordering, reorder_children,
    check_capacity, TYPE_GROUP, TYPE_CONTAINER,
)


def main():
    parser = argparse.ArgumentParser(description="移动 AppGrid 分组")
    parser.add_argument("--db", required=True, help=".agrid 数据库路径")
    parser.add_argument("--group", required=True, type=int, help="分组 ID")
    parser.add_argument("--to-page", required=True, type=int, help="目标页面 ID")
    parser.add_argument("--position", type=int, default=None, help="目标位置（省略则追加到末尾）")
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

    # 验证目标页面
    page = conn.execute(
        "SELECT type FROM items WHERE rowid=?", (args.to_page,)
    ).fetchone()
    if not page or page["type"] != TYPE_CONTAINER:
        print(f"错误: 页面 {args.to_page} 不存在或不是容器类型", file=sys.stderr)
        sys.exit(1)

    old_parent = group["parent_id"]

    # 检查目标页面容量（同页面内移动不需要检查）
    if args.to_page != old_parent:
        try:
            check_capacity(conn, args.to_page)
        except ValueError as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)

    pos = args.position if args.position is not None else get_next_ordering(conn, args.to_page)

    if args.position is not None:
        shift_ordering(conn, args.to_page, pos)

    conn.execute(
        "UPDATE items SET parent_id=?, ordering=? WHERE rowid=?",
        (args.to_page, pos, args.group),
    )

    reorder_children(conn, old_parent)

    conn.commit()
    conn.close()

    print(f"✓ 分组 '{group['title']}' 已移动到页面 {args.to_page} (位置 {pos})")


if __name__ == "__main__":
    main()
