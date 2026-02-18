"""移动 AppGrid 应用到指定页面或分组"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import (
    connect, resolve_target, shift_ordering, get_next_ordering,
    reorder_children, check_capacity, TYPE_APP,
)


def main():
    parser = argparse.ArgumentParser(description="移动 AppGrid 应用")
    parser.add_argument("--db", required=True, help=".agrid 数据库路径")
    parser.add_argument("--app", required=True, type=int, help="应用 ID")
    parser.add_argument("--to", required=True, type=int, help="目标页面或分组 ID")
    parser.add_argument("--position", type=int, default=None, help="目标位置（省略则追加到末尾）")
    args = parser.parse_args()

    conn = connect(args.db)

    # 验证应用存在
    app = conn.execute(
        "SELECT i.rowid, i.parent_id, a.title FROM items i JOIN apps a ON i.rowid = a.item_id WHERE i.rowid=? AND i.type=?",
        (args.app, TYPE_APP),
    ).fetchone()
    if not app:
        print(f"错误: 应用 {args.app} 不存在", file=sys.stderr)
        sys.exit(1)

    old_parent = app["parent_id"]
    target_id = resolve_target(conn, args.to)

    # 检查目标容器容量（同容器内移动不需要检查）
    if target_id != old_parent:
        try:
            check_capacity(conn, target_id)
        except ValueError as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)

    pos = args.position if args.position is not None else get_next_ordering(conn, target_id)

    # 如果指定位置，先腾出空间
    if args.position is not None:
        shift_ordering(conn, target_id, pos)

    # 移动应用
    conn.execute(
        "UPDATE items SET parent_id=?, ordering=? WHERE rowid=?",
        (target_id, pos, args.app),
    )

    # 重新整理原父节点排序
    reorder_children(conn, old_parent)

    conn.commit()
    conn.close()

    print(f"✓ 应用 '{app['title']}' 已移动到目标 {args.to} (位置 {pos})")


if __name__ == "__main__":
    main()
