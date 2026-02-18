"""导出 AppGrid 应用列表"""
import argparse
import csv
import json
import sys
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import connect, get_pages, get_group_container, TYPE_GROUP, TYPE_APP


def collect_apps(conn, parent_id, page_name, group_name=""):
    """递归收集应用列表"""
    results = []
    rows = conn.execute(
        """SELECT i.rowid, i.type, a.title, a.bundleid, a.custom_path, g.title AS group_title
           FROM items i
           LEFT JOIN apps a ON i.rowid = a.item_id
           LEFT JOIN groups g ON i.rowid = g.item_id
           WHERE i.parent_id=? ORDER BY i.ordering""",
        (parent_id,),
    ).fetchall()

    for row in rows:
        if row["type"] == TYPE_APP:
            results.append({
                "id": row["rowid"],
                "title": row["title"] or "",
                "bundleid": row["bundleid"] or "",
                "custom_path": row["custom_path"] or "",
                "page": page_name,
                "group": group_name,
            })
        elif row["type"] == TYPE_GROUP:
            container = get_group_container(conn, row["rowid"])
            if container:
                results.extend(
                    collect_apps(conn, container, page_name, row["group_title"] or "")
                )
    return results


def main():
    parser = argparse.ArgumentParser(description="导出 AppGrid 应用列表")
    parser.add_argument("--db", required=True, help=".agrid 数据库路径")
    parser.add_argument("--format", choices=["csv", "json"], default="csv")
    parser.add_argument("--output", help="输出文件路径（省略则输出到终端）")
    args = parser.parse_args()

    conn = connect(args.db)
    pages = get_pages(conn)

    all_apps = []
    for i, page in enumerate(pages):
        all_apps.extend(collect_apps(conn, page["rowid"], f"页面{i + 1}"))

    conn.close()

    if args.format == "json":
        content = json.dumps(all_apps, ensure_ascii=False, indent=2)
    else:
        buf = StringIO()
        writer = csv.DictWriter(buf, fieldnames=["id", "title", "bundleid", "custom_path", "page", "group"])
        writer.writeheader()
        writer.writerows(all_apps)
        content = buf.getvalue()

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"✓ 已导出 {len(all_apps)} 个应用到 {args.output}")
    else:
        print(content)


if __name__ == "__main__":
    main()
