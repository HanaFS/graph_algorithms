"""
Thuật toán duyệt đồ thị theo chiều rộng (Breadth-First Search – BFS).

Hỗ trợ cả hai dạng đầu vào:
  - Graph object (dùng với module graph.py) có thuộc tính adj_list / adjacency_list
  - dict adjacency list (dùng nội bộ trong graph_ui.py):
      { node: [(neighbor, weight), ...], ... }
"""

from collections import deque
from typing import Any, List


def bfs(graph, start: Any) -> List[Any]:
    """
    Duyệt BFS từ đỉnh `start`.

    Parameters
    ----------
    graph : Graph object hoặc dict
        - Nếu là Graph object: phải có thuộc tính `adj` là dict
          mapping node → list[(neighbor, weight)]  hoặc list[neighbor].
        - Nếu là dict: dạng { node: [(neighbor, weight), ...] }.
    start : Any
        Đỉnh bắt đầu duyệt.

    Returns
    -------
    List[Any]
        Danh sách các đỉnh theo thứ tự BFS.
    """
    adj = _get_adj(graph)

    visited = {start}
    queue = deque([start])
    order: List[Any] = []

    while queue:
        u = queue.popleft()
        order.append(u)
        for neighbor in _neighbors(adj, u):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order


# ── Internal helpers ──────────────────────────────────────────────────────────

def _get_adj(graph) -> dict:
    """Trích xuất adjacency dict từ Graph object hoặc dict thuần."""
    if isinstance(graph, dict):
        return graph
    # Graph object: thử các tên thuộc tính phổ biến
    for attr in ("adj", "adj_list", "adjacency_list", "adjacency"):
        if hasattr(graph, attr):
            return getattr(graph, attr)
    raise TypeError(
        "graph phải là dict hoặc object có thuộc tính 'adj'/'adj_list'."
    )


def _neighbors(adj: dict, u: Any) -> List[Any]:
    """
    Trả về danh sách đỉnh kề của u (đã sắp xếp để kết quả ổn định).
    Hỗ trợ danh sách kề dạng [(neighbor, weight), ...] hoặc [neighbor, ...].
    """
    raw = adj.get(u, [])
    result = []
    for item in raw:
        if isinstance(item, (list, tuple)):
            result.append(item[0])   # (neighbor, weight)
        else:
            result.append(item)      # neighbor thuần
    # Sắp xếp để thứ tự duyệt ổn định
    try:
        return sorted(result, key=str)
    except TypeError:
        return result
