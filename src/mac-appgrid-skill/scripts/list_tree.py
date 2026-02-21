"""列出 AppGrid 树形结构"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import connect, get_pages, get_children, get_group_containers, TYPE_GROUP, TYPE_APP, TYPE_CONTAINER


def build_tree(conn, parent_id, depth=0):
    """递归构建树形结构"""
    result = []
    children = get_children(conn, parent_id)
    for child in children:
        node = {
            "id": child["rowid"],
            "type": child["type"],
            "ordering": child["ordering"],
        }
        if child["type"] == TYPE_APP:
            node["title"] = child["app_title"] or ""
            node["bundleid"] = child["bundleid"] or ""
        elif child["type"] == TYPE_GROUP:
            node["title"] = child["group_title"] or ""
            containers = get_group_containers(conn, child["rowid"])
            all_children = []
            for ci, cid in enumerate(containers):
                page_children = build_tree(conn, cid, depth + 1)
                if len(containers) > 1:
                    # 多分页时包装为分页节点
                    all_children.append({
                        "id": cid,
                        "type": TYPE_CONTAINER,
                        "ordering": ci,
                        "title": f"分页 {ci + 1}",
                        "children": page_children,
                    })
                else:
                    all_children.extend(page_children)
            node["children"] = all_children
        elif child["type"] == TYPE_CONTAINER:
            node["children"] = build_tree(conn, child["rowid"], depth + 1)
        result.append(node)
    return result


def print_tree(nodes, indent=0):
    """打印树形结构"""
    for node in nodes:
        prefix = "  " * indent
        t = {TYPE_APP: "📱", TYPE_GROUP: "📁", TYPE_CONTAINER: "📄"}.get(node["type"], "?")
        title = node.get("title", f"Page")
        extra = f" ({node.get('bundleid', '')})" if node.get("bundleid") else ""
        print(f"{prefix}{t} [{node['id']}] {title}{extra}")
        if "children" in node:
            print_tree(node["children"], indent + 1)


def main():
    parser = argparse.ArgumentParser(description="列出 AppGrid 树形结构")
    parser.add_argument("--db", required=True, help=".agrid 数据库路径")
    parser.add_argument("--page", type=int, help="只显示指定页面 ID")
    parser.add_argument("--format", choices=["tree", "json"], default="tree")
    args = parser.parse_args()

    conn = connect(args.db)
    pages = get_pages(conn)

    if args.page:
        pages = [p for p in pages if p["rowid"] == args.page]
        if not pages:
            print(f"页面 {args.page} 不存在", file=sys.stderr)
            sys.exit(1)

    tree = []
    for i, page in enumerate(pages):
        page_node = {
            "id": page["rowid"],
            "type": TYPE_CONTAINER,
            "ordering": page["ordering"],
            "title": f"页面 {i + 1}",
            "children": build_tree(conn, page["rowid"]),
        }
        tree.append(page_node)

    if args.format == "json":
        print(json.dumps(tree, ensure_ascii=False, indent=2))
    else:
        print_tree(tree)

    conn.close()


if __name__ == "__main__":
    main()
