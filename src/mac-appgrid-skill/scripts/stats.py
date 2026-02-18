"""统计 AppGrid 数据库概览"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import connect, get_pages, get_group_container, TYPE_GROUP, TYPE_CONTAINER, TYPE_APP


def main():
    parser = argparse.ArgumentParser(description="AppGrid 数据库统计概览")
    parser.add_argument("--db", required=True, help=".agrid 数据库路径")
    parser.add_argument("--format", choices=["table", "json"], default="table")
    args = parser.parse_args()

    conn = connect(args.db)

    # 页面信息
    pages = get_pages(conn)

    # 分组信息
    groups = conn.execute(
        """SELECT i.rowid, i.parent_id, g.title FROM items i
           JOIN groups g ON i.rowid = g.item_id WHERE i.type = ?""",
        (TYPE_GROUP,),
    ).fetchall()

    # 总应用数
    total_apps = conn.execute("SELECT COUNT(*) FROM apps").fetchone()[0]

    # 分组容器 ID 集合
    group_containers = conn.execute(
        """SELECT i.rowid FROM items i
           WHERE i.type = ? AND i.parent_id IN (SELECT rowid FROM items WHERE type = ?)""",
        (TYPE_CONTAINER, TYPE_GROUP),
    ).fetchall()
    container_ids = {r["rowid"] for r in group_containers}

    # 未归组数
    ungrouped = conn.execute(
        "SELECT COUNT(*) FROM items WHERE type = ?", (TYPE_APP,)
    ).fetchone()[0]
    grouped_count = sum(
        1 for r in conn.execute("SELECT parent_id FROM items WHERE type = ?", (TYPE_APP,)).fetchall()
        if r["parent_id"] in container_ids
    )
    ungrouped_count = ungrouped - grouped_count

    result = {
        "total_apps": total_apps,
        "grouped": grouped_count,
        "ungrouped": ungrouped_count,
        "pages": len(pages),
        "groups": [],
    }

    for g in groups:
        container = get_group_container(conn, g["rowid"])
        app_count = 0
        if container:
            app_count = conn.execute(
                "SELECT COUNT(*) FROM items WHERE parent_id=? AND type=?", (container, TYPE_APP)
            ).fetchone()[0]
        result["groups"].append({
            "id": g["rowid"],
            "title": g["title"],
            "app_count": app_count,
        })

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"总应用: {total_apps} | 已归组: {grouped_count} | 未归组: {ungrouped_count} | 页面: {len(pages)} | 分组: {len(groups)}")
        print()
        for g in result["groups"]:
            print(f"  📁 [{g['id']}] {g['title']}: {g['app_count']} 个应用")

    conn.close()


if __name__ == "__main__":
    main()