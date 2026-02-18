"""检查数据库一致性"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import connect, TYPE_GROUP, TYPE_CONTAINER, TYPE_APP


def main():
    parser = argparse.ArgumentParser(description="检查 AppGrid 数据库一致性")
    parser.add_argument("--db", required=True, help=".agrid 数据库路径")
    args = parser.parse_args()

    conn = connect(args.db)
    issues = []

    # 1. type=4 但无 apps 记录
    orphan_items = conn.execute(
        """SELECT i.rowid FROM items i LEFT JOIN apps a ON i.rowid = a.item_id
           WHERE i.type=? AND a.item_id IS NULL""", (TYPE_APP,)
    ).fetchall()
    if orphan_items:
        issues.append(f"type=4 但无 apps 记录: {len(orphan_items)} 条")

    # 2. apps 记录但无 items
    orphan_apps = conn.execute(
        """SELECT a.item_id, a.title FROM apps a LEFT JOIN items i ON a.item_id = i.rowid
           WHERE i.rowid IS NULL"""
    ).fetchall()
    if orphan_apps:
        issues.append(f"apps 记录但无 items: {len(orphan_apps)} 条")
        for r in orphan_apps:
            issues.append(f"  [{r['item_id']}] {r['title']}")

    # 3. 分组无容器
    groups = conn.execute(
        "SELECT i.rowid, g.title FROM items i JOIN groups g ON i.rowid=g.item_id WHERE i.type=?",
        (TYPE_GROUP,),
    ).fetchall()
    for g in groups:
        container = conn.execute(
            "SELECT rowid FROM items WHERE type=? AND parent_id=?", (TYPE_CONTAINER, g["rowid"])
        ).fetchone()
        if not container:
            issues.append(f"分组 [{g['rowid']}] {g['title']} 缺少内部容器")

    # 4. 空分组（容器内无应用）
    empty_groups = []
    for g in groups:
        container = conn.execute(
            "SELECT rowid FROM items WHERE type=? AND parent_id=?", (TYPE_CONTAINER, g["rowid"])
        ).fetchone()
        if container:
            count = conn.execute(
                "SELECT COUNT(*) FROM items WHERE parent_id=?", (container["rowid"],)
            ).fetchone()[0]
            if count == 0:
                empty_groups.append(f"  📁 [{g['rowid']}] {g['title']}")
    if empty_groups:
        issues.append(f"空分组: {len(empty_groups)} 个")
        issues.extend(empty_groups)

    # 5. 孤立页面（无子项的页面）
    pages = conn.execute(
        """SELECT i.rowid FROM items i WHERE i.type=? AND i.parent_id IN
           (SELECT rowid FROM items WHERE type=? AND parent_id=0)""",
        (TYPE_CONTAINER, TYPE_CONTAINER),
    ).fetchall()
    empty_pages = []
    for p in pages:
        count = conn.execute("SELECT COUNT(*) FROM items WHERE parent_id=?", (p["rowid"],)).fetchone()[0]
        if count == 0:
            empty_pages.append(p["rowid"])
    if empty_pages:
        issues.append(f"空页面: {len(empty_pages)} 个 (IDs: {empty_pages})")

    # 6. bookmark 缺失统计
    no_bookmark = conn.execute(
        "SELECT COUNT(*) FROM apps WHERE bookmark IS NULL OR LENGTH(bookmark) = 0"
    ).fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM apps").fetchone()[0]
    if no_bookmark > 0:
        issues.append(f"bookmark 为空: {no_bookmark}/{total} 个应用")

    conn.close()

    if issues:
        print(f"发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("✓ 数据库一致性检查通过，无问题")


if __name__ == "__main__":
    main()