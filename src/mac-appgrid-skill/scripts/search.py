"""搜索 AppGrid 应用"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import connect


def main():
    parser = argparse.ArgumentParser(description="搜索 AppGrid 应用")
    parser.add_argument("--db", required=True, help=".agrid 数据库路径")
    parser.add_argument("--query", required=True, help="搜索关键词")
    parser.add_argument("--field", choices=["name", "bundleid", "all"], default="all")
    parser.add_argument("--format", choices=["table", "json"], default="table")
    args = parser.parse_args()

    conn = connect(args.db)

    conditions = []
    params = []
    keyword = f"%{args.query}%"

    if args.field in ("name", "all"):
        conditions.append("a.title LIKE ?")
        params.append(keyword)
    if args.field in ("bundleid", "all"):
        conditions.append("a.bundleid LIKE ?")
        params.append(keyword)

    where = " OR ".join(conditions)
    rows = conn.execute(
        f"""SELECT i.rowid, i.parent_id, i.ordering, a.title, a.bundleid, a.custom_path,
                   g.title AS group_name
            FROM items i
            JOIN apps a ON i.rowid = a.item_id
            LEFT JOIN items pi ON i.parent_id = pi.rowid
            LEFT JOIN items gi ON pi.parent_id = gi.rowid AND gi.type = 2
            LEFT JOIN groups g ON gi.rowid = g.item_id
            WHERE {where}
            ORDER BY a.title""",
        params,
    ).fetchall()

    results = [dict(r) for r in rows]

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print("未找到匹配的应用")
        else:
            print(f"找到 {len(results)} 个应用：")
            print(f"{'ID':<6} {'名称':<30} {'Bundle ID':<45} {'所在分组'}")
            print("-" * 100)
            for r in results:
                group = r["group_name"] or "-"
                print(f"{r['rowid']:<6} {(r['title'] or ''):<30} {(r['bundleid'] or ''):<45} {group}")

    conn.close()


if __name__ == "__main__":
    main()
