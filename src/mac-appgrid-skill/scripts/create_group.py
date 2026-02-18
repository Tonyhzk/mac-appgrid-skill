"""在 AppGrid 页面中创建分组"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import (
    connect, insert_item, shift_ordering, get_next_ordering,
    check_capacity, TYPE_GROUP, TYPE_CONTAINER,
)


def main():
    parser = argparse.ArgumentParser(description="创建 AppGrid 分组")
    parser.add_argument("--db", required=True, help=".agrid 数据库路径")
    parser.add_argument("--page", required=True, type=int, help="目标页面 ID")
    parser.add_argument("--name", required=True, help="分组名称")
    parser.add_argument("--position", type=int, default=None, help="插入位置（省略则追加到末尾）")
    args = parser.parse_args()

    conn = connect(args.db)

    # 验证页面存在且为容器类型
    page = conn.execute(
        "SELECT type FROM items WHERE rowid=?", (args.page,)
    ).fetchone()
    if not page or page["type"] != TYPE_CONTAINER:
        print(f"错误: 页面 {args.page} 不存在或不是容器类型", file=sys.stderr)
        sys.exit(1)

    pos = args.position if args.position is not None else get_next_ordering(conn, args.page)

    # 检查页面容量
    try:
        check_capacity(conn, args.page)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    # 如果指定位置，先腾出空间
    if args.position is not None:
        shift_ordering(conn, args.page, pos)

    # 1. 创建分组 item (type=2)
    group_id = insert_item(conn, TYPE_GROUP, args.page, pos)

    # 2. 创建 groups 记录
    conn.execute(
        "INSERT INTO groups (item_id, category_id, title) VALUES (?, 0, ?)",
        (group_id, args.name),
    )

    # 3. 创建分组内部容器 (type=3)
    container_id = insert_item(conn, TYPE_CONTAINER, group_id, 0)

    conn.commit()
    conn.close()

    print(f"✓ 分组已创建: '{args.name}' (ID={group_id}, 容器ID={container_id})")


if __name__ == "__main__":
    main()
