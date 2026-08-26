"""
Thuật toán Prim – Cây khung nhỏ nhất (Minimum Spanning Tree)

Ý tưởng:
- Bắt đầu từ một đỉnh root bất kỳ.
- Dùng min-heap (priority queue) để luôn chọn cạnh nhẹ nhất
  kết nối từ tập đỉnh đã chọn ra tập đỉnh chưa chọn.
- Lặp cho đến khi tất cả đỉnh đã vào MST.

Độ phức tạp: O(E log V) với heap nhị phân.
"""

import heapq
from typing import Dict, List, Tuple, Optional


# ─── Kiểu dữ liệu ─────────────────────────────────────────────────────────────
# graph: dict[node] = list[(neighbor, weight)]
Graph = Dict[str, List[Tuple[str, float]]]

# Một bước trong trace (để UI vẽ từng bước)
Step = Dict  # {"added_edge": (u, v, w), "visited": set, "mst_edges": list}


# ─── Hàm chính ────────────────────────────────────────────────────────────────
def prim(graph: Graph, root: str) -> Tuple[List[Tuple[str, str, float]], float, List[Step]]:
    """
    Chạy thuật toán Prim từ đỉnh root.

    Trả về:
        mst_edges : danh sách cạnh trong MST, dạng [(u, v, w), ...]
        total_cost: tổng trọng số MST
        steps     : danh sách các bước cho visualization

    Raises:
        ValueError: nếu root không tồn tại trong graph, hoặc graph rỗng.
    """
    if not graph:
        raise ValueError("Đồ thị rỗng.")
    if root not in graph:
        raise ValueError(f"Đỉnh '{root}' không tồn tại trong đồ thị.")

    visited: set = set()
    mst_edges: List[Tuple[str, str, float]] = []
    steps: List[Step] = []
    total_cost: float = 0.0

    # heap: (weight, from_node, to_node)
    heap: List[Tuple[float, str, str]] = []

    def _push_edges(node: str):
        for neighbor, w in graph[node]:
            if neighbor not in visited:
                heapq.heappush(heap, (w, node, neighbor))

    visited.add(root)
    _push_edges(root)

    # Bước khởi đầu
    steps.append({
        "added_edge": None,
        "visited": set(visited),
        "mst_edges": list(mst_edges),
        "description": f"Bắt đầu từ đỉnh '{root}'.",
    })

    while heap and len(visited) < len(graph):
        w, u, v = heapq.heappop(heap)

        if v in visited:
            continue  # bỏ qua cạnh ngược

        # Thêm cạnh (u → v) vào MST
        visited.add(v)
        mst_edges.append((u, v, w))
        total_cost += w
        _push_edges(v)

        steps.append({
            "added_edge": (u, v, w),
            "visited": set(visited),
            "mst_edges": list(mst_edges),
            "description": f"Thêm cạnh ({u} — {v}), trọng số = {w}.",
        })

    # Kiểm tra đồ thị có liên thông không
    if len(visited) < len(graph):
        missing = set(graph) - visited
        steps.append({
            "added_edge": None,
            "visited": set(visited),
            "mst_edges": list(mst_edges),
            "description": (
                f"Đồ thị không liên thông. "
                f"Không thể tới: {', '.join(sorted(missing))}."
            ),
        })

    return mst_edges, total_cost, steps
