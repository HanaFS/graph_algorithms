"""
Thuật toán Kruskal – Cây khung nhỏ nhất (Minimum Spanning Tree)

Ý tưởng:
- Sắp xếp tất cả cạnh theo trọng số tăng dần.
- Dùng cấu trúc Union-Find (Disjoint Set Union) để kiểm tra chu trình.
- Lần lượt thêm cạnh nhẹ nhất nếu không tạo chu trình.

Độ phức tạp: O(E log E).
"""

from typing import Dict, List, Tuple


# ─── Kiểu dữ liệu ─────────────────────────────────────────────────────────────
Graph = Dict[str, List[Tuple[str, float]]]
Step  = Dict  # {"edge": (u,v,w), "accepted": bool, "mst_edges": list, ...}


# ─── Union-Find ────────────────────────────────────────────────────────────────
class UnionFind:
    def __init__(self, nodes):
        self.parent = {n: n for n in nodes}
        self.rank   = {n: 0  for n in nodes}

    def find(self, x: str) -> str:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x: str, y: str) -> bool:
        """Hợp nhất 2 tập. Trả về True nếu hợp nhất thành công (không tạo chu trình)."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False  # đã cùng tập → tạo chu trình
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


# ─── Hàm chính ────────────────────────────────────────────────────────────────
def kruskal(graph: Graph) -> Tuple[List[Tuple[str, str, float]], float, List[Step]]:
    """
    Chạy thuật toán Kruskal trên đồ thị vô hướng.

    Trả về:
        mst_edges : danh sách cạnh trong MST, dạng [(u, v, w), ...]
        total_cost: tổng trọng số MST
        steps     : danh sách các bước cho visualization

    Raises:
        ValueError: nếu graph rỗng.
    """
    if not graph:
        raise ValueError("Đồ thị rỗng.")

    nodes = list(graph.keys())

    # Thu thập tất cả cạnh (loại trùng cho đồ thị vô hướng)
    seen_edges: set = set()
    all_edges: List[Tuple[float, str, str]] = []
    for u in graph:
        for v, w in graph[u]:
            key = tuple(sorted([u, v]))
            if key not in seen_edges:
                seen_edges.add(key)
                all_edges.append((w, u, v))

    # Sắp xếp theo trọng số tăng dần
    all_edges.sort(key=lambda e: e[0])

    uf = UnionFind(nodes)
    mst_edges: List[Tuple[str, str, float]] = []
    steps: List[Step] = []
    total_cost: float = 0.0

    # Bước khởi đầu: hiển thị danh sách cạnh đã sắp xếp
    steps.append({
        "edge": None,
        "accepted": None,
        "mst_edges": [],
        "description": (
            f"Sắp xếp {len(all_edges)} cạnh theo trọng số tăng dần.\n"
            + "  ".join(f"({u}-{v}, w={w})" for w, u, v in all_edges[:6])
            + ("  ..." if len(all_edges) > 6 else "")
        ),
    })

    for w, u, v in all_edges:
        accepted = uf.union(u, v)
        if accepted:
            mst_edges.append((u, v, w))
            total_cost += w

        steps.append({
            "edge": (u, v, w),
            "accepted": accepted,
            "mst_edges": list(mst_edges),
            "description": (
                f"Xét cạnh ({u} — {v}), w={w}. "
                + ("✔ Thêm vào MST." if accepted else "✘ Bỏ qua (tạo chu trình).")
            ),
        })

        if len(mst_edges) == len(nodes) - 1:
            break  # MST hoàn chỉnh

    steps.append({
        "edge": None,
        "accepted": None,
        "mst_edges": list(mst_edges),
        "description": f"Hoàn thành! MST có {len(mst_edges)} cạnh, tổng trọng số = {total_cost}.",
    })

    return mst_edges, total_cost, steps
