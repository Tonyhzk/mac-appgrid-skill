"""重命名 AppGrid 分组"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import connect, TYPE_GROUP


def main():
    parser = argparse.ArgumentParser(description="重命名 AppGrid 分组")
    parser.add_argument("--db", required=True, help=".agrid 数据库路径")
    parser.add_argument("--group", required=True, type=int, help="分组 ID")
    parser.add_argument("--name", required=True, help="新名称")
    args = parser.parse_args()

    conn = connect(args.db)

    row = conn.execute(
        "SELECT g.title FROM groups g JOIN items i ON g.item_id = i.rowid WHERE g.item_id=? AND i.type=?",
        (args.group, TYPE_GROUP),
    ).fetchone()
    if not row:
        print(f"错误: 分组 {args.group} 不存在", file=sys.stderr)
        sys.exit(1)

    old_name = row["title"]
    conn.execute("UPDATE groups SET title=? WHERE item_id=?", (args.name, args.group))
    conn.commit()
    conn.close()

    print(f"✓ 分组已重命名: '{old_name}' → '{args.name}'")


if __name__ == "__main__":
    main()
