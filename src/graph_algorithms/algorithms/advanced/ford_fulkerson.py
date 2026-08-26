"""
Thuật toán Ford-Fulkerson – Tìm luồng cực đại (Max Flow)
Biến thể: Edmonds-Karp (dùng BFS tìm đường tăng luồng → O(VE²))

Ý tưởng:
- Xây dựng đồ thị phần dư (residual graph).
- Lặp: tìm đường tăng luồng (augmenting path) từ source → sink bằng BFS.
- Cập nhật luồng trên đường tăng luồng.
- Dừng khi không tìm được đường tăng luồng nào.

Yêu cầu: đồ thị có hướng, trọng số = sức chứa (capacity ≥ 0).

Độ phức tạp: O(V · E²) với BFS (Edmonds-Karp).
"""

from collections import deque
from typing import Dict, List, Tuple, Optional


# ─── Kiểu dữ liệu ─────────────────────────────────────────────────────────────
# graph: dict[node] = list[(neighbor, capacity)]  – đồ thị có hướng
Graph = Dict[str, List[Tuple[str, float]]]
Step  = Dict  # {"path": list, "flow": float, "total_flow": float, "residual": dict}


# ─── BFS tìm đường tăng luồng ─────────────────────────────────────────────────
def _bfs(residual: Dict[str, Dict[str, float]],
         source: str, sink: str) -> Optional[List[str]]:
    """
    BFS trên residual graph. Trả về đường đi từ source → sink (list các đỉnh),
    hoặc None nếu không tồn tại.
    """
    visited = {source}
    parent: Dict[str, Optional[str]] = {source: None}
    queue = deque([source])

    while queue:
        u = queue.popleft()
        for v, cap in residual[u].items():
            if v not in visited and cap > 0:
                visited.add(v)
                parent[v] = u
                if v == sink:
                    # Truy vết đường đi
                    path: List[str] = []
                    node: Optional[str] = sink
                    while node is not None:
                        path.append(node)
                        node = parent[node]
                    path.reverse()
                    return path
                queue.append(v)
    return None


# ─── Hàm chính ────────────────────────────────────────────────────────────────
def ford_fulkerson(
    graph: Graph,
    source: str,
    sink: str
) -> Tuple[float, Dict[Tuple[str, str], float], List[Step]]:
    """
    Chạy Ford-Fulkerson (Edmonds-Karp) tìm luồng cực đại.

    Tham số:
        graph : đồ thị có hướng – dict[u] = [(v, capacity), ...]
        source: đỉnh nguồn (S)
        sink  : đỉnh đích   (T)

    Trả về:
        max_flow  : giá trị luồng cực đại
        flow_on_edge: dict[(u,v)] = lượng luồng thực sự trên mỗi cạnh
        steps     : danh sách các bước cho visualization

    Raises:
        ValueError: nếu source/sink không tồn tại.
    """
    if not graph:
        raise ValueError("Đồ thị rỗng.")
    if source not in graph:
        raise ValueError(f"Đỉnh nguồn '{source}' không tồn tại.")
    if sink not in graph:
        raise ValueError(f"Đỉnh đích '{sink}' không tồn tại.")
    if source == sink:
        raise ValueError("Đỉnh nguồn và đỉnh đích không được trùng nhau.")

    # ── Xây dựng residual graph ────────────────────────────────────────────
    # residual[u][v] = capacity còn lại
    nodes = list(graph.keys())
    residual: Dict[str, Dict[str, float]] = {n: {} for n in nodes}

    # Capacity gốc để tính flow_on_edge sau
    capacity: Dict[Tuple[str, str], float] = {}
    for u in graph:
        for v, cap in graph[u]:
            residual[u][v] = residual[u].get(v, 0) + cap
            residual.setdefault(v, {})
            if v not in residual:
                residual[v] = {}
            if u not in residual[v]:
                residual[v][u] = 0
            capacity[(u, v)] = capacity.get((u, v), 0) + cap

    max_flow: float = 0.0
    steps: List[Step] = []

    steps.append({
        "path": [],
        "bottleneck": 0,
        "total_flow": 0,
        "action": "init",
        "description": (
            f"Khởi tạo Ford-Fulkerson. Nguồn = '{source}', Đích = '{sink}'.\n"
            f"Residual graph đã được xây dựng từ đồ thị gốc."
        ),
    })

    iteration = 0
    while True:
        # Tính flow_on_edge hiện tại từ residual
        current_flow: Dict[Tuple[str, str], float] = {}
        for (u, v), cap in capacity.items():
            flow_val = cap - residual[u].get(v, 0)
            if flow_val > 0:
                current_flow[(u, v)] = flow_val
                
        if iteration == 0:
            steps[0]["flow_on_edge"] = current_flow
        path = _bfs(residual, source, sink)
        if path is None:
            break  # Không còn đường tăng luồng

        iteration += 1

        # Tìm bottleneck (capacity nhỏ nhất trên đường)
        bottleneck = float("inf")
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            bottleneck = min(bottleneck, residual[u][v])

        # Cập nhật residual graph
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            residual[u][v] -= bottleneck
            residual[v][u] = residual[v].get(u, 0) + bottleneck

        max_flow += bottleneck

        current_flow_after: Dict[Tuple[str, str], float] = {}
        for (u, v), cap in capacity.items():
            flow_val = cap - residual[u].get(v, 0)
            if flow_val > 0:
                current_flow_after[(u, v)] = flow_val

        steps.append({
            "path": list(path),
            "bottleneck": bottleneck,
            "total_flow": max_flow,
            "action": "augment",
            "flow_on_edge": current_flow_after,
            "description": (
                f"Lần {iteration}: Đường tăng luồng: {' → '.join(path)}.\n"
                f"  Bottleneck = {bottleneck:.4g}. "
                f"Tổng luồng hiện tại = {max_flow:.4g}."
            ),
        })

    # ── Tính flow_on_edge từ residual ─────────────────────────────────────
    # flow(u,v) = capacity(u,v) - residual(u,v)
    flow_on_edge: Dict[Tuple[str, str], float] = {}
    for (u, v), cap in capacity.items():
        flow_val = cap - residual[u].get(v, 0)
        if flow_val > 0:
            flow_on_edge[(u, v)] = flow_val

    steps.append({
        "path": [],
        "bottleneck": 0,
        "total_flow": max_flow,
        "action": "done",
        "flow_on_edge": flow_on_edge,
        "description": (
            f"Hoàn thành! Luồng cực đại = {max_flow:.4g}.\n"
            f"Số lần tìm đường tăng luồng: {iteration}."
        ),
    })

    return max_flow, flow_on_edge, steps
