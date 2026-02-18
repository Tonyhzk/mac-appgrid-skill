"""检查未归组的应用"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import connect, TYPE_GROUP, TYPE_CONTAINER, TYPE_APP


def main():
    parser = argparse.ArgumentParser(description="检查未归组的 AppGrid 应用")
    parser.add_argument("--db", required=True, help=".agrid 数据库路径")
    parser.add_argument("--format", choices=["table", "json"], default="table")
    args = parser.parse_args()

    conn = connect(args.db)

    # 获取所有分组容器 ID
    group_containers = conn.execute(
        """SELECT i.rowid FROM items i
           WHERE i.type = ? AND i.parent_id IN (SELECT rowid FROM items WHERE type = ?)""",
        (TYPE_CONTAINER, TYPE_GROUP),
    ).fetchall()
    container_ids = {r["rowid"] for r in group_containers}

    # 获取所有应用
    apps = conn.execute(
        """SELECT i.rowid, i.parent_id, a.title, a.bundleid
           FROM items i JOIN apps a ON i.rowid = a.item_id
           WHERE i.type = ? ORDER BY a.title""",
        (TYPE_APP,),
    ).fetchall()

    ungrouped = [dict(a) for a in apps if a["parent_id"] not in container_ids]
    grouped = len(apps) - len(ungrouped)

    if args.format == "json":
        print(json.dumps({"total": len(apps), "grouped": grouped, "ungrouped": ungrouped}, ensure_ascii=False, indent=2))
    else:
        print(f"总应用: {len(apps)}, 已归组: {grouped}, 未归组: {len(ungrouped)}")
        if ungrouped:
            print(f"\n{'ID':<8} {'名称':<30} {'Bundle ID':<45} {'父节点'}")
            print("-" * 95)
            for a in ungrouped:
                print(f"{a['rowid']:<8} {(a['title'] or ''):<30} {(a['bundleid'] or ''):<45} {a['parent_id']}")

    conn.close()


if __name__ == "__main__":
    main()